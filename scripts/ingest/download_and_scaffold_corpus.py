#!/usr/bin/env python3
"""
Populate a Great Books repo with raw source files and scaffolded folders.

This script is intentionally conservative:
- It reads a fixed local manifest (no crawling).
- It creates the expected repo folders.
- It downloads files serially with a browser-like user agent.
- It sleeps between requests, with optional jitter.
- It writes per-source lock files with checksums.

Expected manifest shape: see great-books-download-manifest.json.

Typical usage from the repo root:

  mkdir -p sources/catalog scripts/ingest
  cp /path/to/great-books-download-manifest.json sources/catalog/launch-corpus.json
  cp /path/to/download_and_scaffold_corpus.py scripts/ingest/download_and_scaffold_corpus.py
  python scripts/ingest/download_and_scaffold_corpus.py \
      --repo-root . \
      --manifest sources/catalog/launch-corpus.json \
      --sleep 12 --jitter 3

Scaffold only, without any network requests:

  python scripts/ingest/download_and_scaffold_corpus.py \
      --repo-root . \
      --manifest sources/catalog/launch-corpus.json \
      --scaffold-only

Limit to one slug while testing:

  python scripts/ingest/download_and_scaffold_corpus.py \
      --repo-root . \
      --manifest sources/catalog/launch-corpus.json \
      --slug meditations \
      --sleep 12

Notes:
- Project Gutenberg's robot-access policy is strict. This script avoids crawling and uses
  a fixed manifest + serial downloads + sleeps, but manual download or Gutenberg's official
  robot/harvest endpoints are still the most policy-conservative routes.
- The script populates /sources/raw/... and scaffolds /content/texts/... . It does NOT
  perform the final normalization into section HTML; that should happen in a separate,
  deterministic transform step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import random
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# Browser-like but still identifiable as this project. Edit if you want your own.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36 "
    "GreatBooksCorpusBootstrap/0.1"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


@dataclass(frozen=True)
class DownloadPlanItem:
    field_name: str
    url: str
    dest_name: str


class DownloadError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and scaffold Great Books source files.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repo root where /sources and /content live. Default: current directory.",
    )
    parser.add_argument(
        "--manifest",
        default="sources/catalog/launch-corpus.json",
        help="Path to the launch-corpus manifest JSON. Default: sources/catalog/launch-corpus.json",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=12.0,
        help="Base seconds to sleep between network requests. Default: 12.",
    )
    parser.add_argument(
        "--jitter",
        type=float,
        default=3.0,
        help="Random jitter (+/- seconds) applied around --sleep. Default: 3.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-request timeout in seconds. Default: 60.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Retry count per file. Default: 3.",
    )
    parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Only process this slug. Repeat to process multiple slugs.",
    )
    parser.add_argument(
        "--provider",
        action="append",
        default=[],
        help="Only process this provider, e.g. gutenberg or web. Repeat to include multiple.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N sources after filtering.",
    )
    parser.add_argument(
        "--scaffold-only",
        action="store_true",
        help="Create folders and seed files but do not download anything.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without writing files or downloading.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing downloaded files and seed files.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first error instead of continuing to the next source.",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="Override the default browser-like user agent.",
    )
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "sources" not in data:
        raise ValueError(f"Manifest at {path} does not look like a launch-corpus manifest.")
    return data


def ensure_dir(path: Path, dry_run: bool = False) -> None:
    if dry_run:
        return
    path.mkdir(parents=True, exist_ok=True)


def infer_extension(url: str, preferred_raw_format: str | None = None) -> str:
    parsed = urlparse(url)
    path = parsed.path.lower()

    if path.endswith(".html.images") or path.endswith(".htm") or path.endswith(".html"):
        return ".html"
    if path.endswith(".txt.utf-8") or path.endswith(".txt"):
        return ".txt"
    if path.endswith(".rdf"):
        return ".rdf"
    if path.endswith(".zip"):
        return ".zip"
    if path.endswith(".xml"):
        return ".xml"
    if path.endswith(".json"):
        return ".json"
    if path.endswith(".epub") or path.endswith(".epub.images") or path.endswith(".epub.noimages"):
        return ".epub"
    if path.endswith(".pdf"):
        return ".pdf"

    if preferred_raw_format:
        fmt = preferred_raw_format.lower()
        if fmt in {"html", "html_images"}:
            return ".html"
        if fmt in {"txt", "plain_text"}:
            return ".txt"
        if fmt in {"usfm_zip", "zip"}:
            return ".zip"

    guessed, _ = mimetypes.guess_type(path)
    if guessed == "text/html":
        return ".html"
    if guessed == "text/plain":
        return ".txt"
    if guessed == "application/zip":
        return ".zip"

    return ".bin"


def build_download_plan(source: dict[str, Any]) -> list[DownloadPlanItem]:
    source_ext = infer_extension(source["source_url"], source.get("preferred_raw_format"))
    items: list[DownloadPlanItem] = [
        DownloadPlanItem("source_url", source["source_url"], f"source{source_ext}")
    ]

    fallback_url = source.get("fallback_txt_url")
    if fallback_url:
        fallback_ext = infer_extension(fallback_url)
        if fallback_ext == ".txt" and source_ext != ".txt":
            dest_name = "source.txt"
        else:
            dest_name = f"fallback{fallback_ext}"
        items.append(DownloadPlanItem("fallback_txt_url", fallback_url, dest_name))

    metadata_url = source.get("metadata_url")
    if metadata_url:
        metadata_ext = infer_extension(metadata_url)
        dest_name = "source.rdf" if metadata_ext == ".rdf" else f"metadata{metadata_ext}"
        items.append(DownloadPlanItem("metadata_url", metadata_url, dest_name))

    rights_url = source.get("rights_url")
    if rights_url:
        rights_ext = infer_extension(rights_url)
        items.append(DownloadPlanItem("rights_url", rights_url, f"rights{rights_ext}"))

    return items


def filtered_sources(manifest: dict[str, Any], slugs: set[str], providers: set[str], limit: int | None) -> list[dict[str, Any]]:
    sources = manifest["sources"]
    out: list[dict[str, Any]] = []
    for src in sources:
        if slugs and src["slug"] not in slugs:
            continue
        if providers and src.get("provider") not in providers:
            continue
        out.append(src)
        if limit is not None and len(out) >= limit:
            break
    return out


def create_seed_files(repo_root: Path, source: dict[str, Any], dry_run: bool, force: bool) -> None:
    for work_slug in source.get("normalized_work_slugs", []):
        text_dir = repo_root / "content" / "texts" / work_slug
        sections_dir = text_dir / "sections"
        ensure_dir(sections_dir, dry_run=dry_run)

        manifest_seed = {
            "slug": work_slug,
            "title": source.get("title"),
            "author": source.get("author"),
            "translator": source.get("translator"),
            "provider": source.get("provider"),
            "sourceSlug": source.get("slug"),
            "path": source.get("path"),
            "launchUsage": source.get("launch_usage"),
            "selectionPlan": source.get("selection_plan"),
            "status": "pending-normalization",
            "notes": [
                "This is a seed file created by download_and_scaffold_corpus.py.",
                "Replace with the final normalized manifest.json after you transform the raw source files.",
            ],
        }
        rights_seed = {
            "provider": source.get("provider"),
            "sourcePage": source.get("landing_url"),
            "sourceSlug": source.get("slug"),
            "status": "pending-normalization",
            "notes": [
                "This is a seed file created by download_and_scaffold_corpus.py.",
                "Replace with the final rights.json after you finish the normalization pass.",
            ],
        }

        write_json_if_needed(text_dir / "manifest.seed.json", manifest_seed, dry_run=dry_run, force=force)
        write_json_if_needed(text_dir / "rights.seed.json", rights_seed, dry_run=dry_run, force=force)
        write_text_if_needed(sections_dir / ".gitkeep", "", dry_run=dry_run, force=force)


def write_json_if_needed(path: Path, data: dict[str, Any], dry_run: bool, force: bool) -> None:
    if path.exists() and not force:
        return
    if dry_run:
        return
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text_if_needed(path: Path, text: str, dry_run: bool, force: bool) -> None:
    if path.exists() and not force:
        return
    if dry_run:
        return
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sleep_with_jitter(base_seconds: float, jitter_seconds: float) -> None:
    delay = max(0.0, base_seconds + random.uniform(-jitter_seconds, jitter_seconds))
    if delay > 0:
        time.sleep(delay)


def download_to_path(
    url: str,
    dest_path: Path,
    headers: dict[str, str],
    timeout: float,
    retries: int,
    dry_run: bool,
    force: bool,
) -> dict[str, Any]:
    if dest_path.exists() and not force:
        return {
            "path": str(dest_path),
            "status": "skipped-existing",
            "sha256": sha256_file(dest_path),
            "bytes": dest_path.stat().st_size,
        }

    if dry_run:
        return {
            "path": str(dest_path),
            "status": "dry-run",
            "sha256": None,
            "bytes": None,
        }

    ensure_dir(dest_path.parent)

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as response:
                data = response.read()
            dest_path.write_bytes(data)
            return {
                "path": str(dest_path),
                "status": "downloaded",
                "sha256": sha256_file(dest_path),
                "bytes": dest_path.stat().st_size,
            }
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt == retries:
                break
            # A small exponential backoff between retries.
            time.sleep(min(30.0, 2 ** attempt))

    raise DownloadError(f"Failed to download {url} -> {dest_path}: {last_error}")


def write_source_lock(
    raw_dir: Path,
    source: dict[str, Any],
    file_records: list[dict[str, Any]],
    dry_run: bool,
) -> None:
    payload = {
        "slug": source.get("slug"),
        "title": source.get("title"),
        "provider": source.get("provider"),
        "retrievedAt": utc_now_iso(),
        "sourcePage": source.get("landing_url"),
        "preferredRawFormat": source.get("preferred_raw_format"),
        "launchUsage": source.get("launch_usage"),
        "normalizedWorkSlugs": source.get("normalized_work_slugs", []),
        "selectionPlan": source.get("selection_plan"),
        "files": file_records,
    }
    write_json_if_needed(raw_dir / "source-lock.json", payload, dry_run=dry_run, force=True)


def copy_manifest_into_repo(manifest_path: Path, repo_root: Path, dry_run: bool, force: bool) -> Path:
    target = repo_root / "sources" / "catalog" / "launch-corpus.json"
    if dry_run:
        return target
    ensure_dir(target.parent)
    if target.resolve() == manifest_path.resolve():
        return target
    if target.exists() and not force:
        return target
    shutil.copyfile(manifest_path, target)
    return target


def process_source(
    repo_root: Path,
    source: dict[str, Any],
    headers: dict[str, str],
    sleep_seconds: float,
    jitter_seconds: float,
    timeout: float,
    retries: int,
    dry_run: bool,
    scaffold_only: bool,
    force: bool,
) -> None:
    raw_dir = repo_root / "sources" / "raw" / str(source.get("provider")) / str(source.get("slug"))
    ensure_dir(raw_dir, dry_run=dry_run)
    create_seed_files(repo_root, source, dry_run=dry_run, force=force)

    plan = build_download_plan(source)
    if scaffold_only:
        write_source_lock(raw_dir, source, [], dry_run=dry_run)
        return

    file_records: list[dict[str, Any]] = []
    for index, item in enumerate(plan):
        dest_path = raw_dir / item.dest_name
        result = download_to_path(
            item.url,
            dest_path,
            headers=headers,
            timeout=timeout,
            retries=retries,
            dry_run=dry_run,
            force=force,
        )
        file_records.append(
            {
                "field": item.field_name,
                "url": item.url,
                "destName": item.dest_name,
                "status": result["status"],
                "bytes": result["bytes"],
                "sha256": result["sha256"],
            }
        )
        # Sleep between requests, but not after the last one for this source.
        if index < len(plan) - 1:
            sleep_with_jitter(sleep_seconds, jitter_seconds)

    write_source_lock(raw_dir, source, file_records, dry_run=dry_run)


def print_plan(repo_root: Path, sources: Iterable[dict[str, Any]]) -> None:
    print("Plan:\n")
    for source in sources:
        raw_dir = repo_root / "sources" / "raw" / str(source.get("provider")) / str(source.get("slug"))
        print(f"- {source.get('slug')} -> {raw_dir}")
        for item in build_download_plan(source):
            print(f"    {item.field_name}: {item.url} -> {raw_dir / item.dest_name}")
        for work_slug in source.get("normalized_work_slugs", []):
            print(f"    scaffold: {repo_root / 'content' / 'texts' / work_slug / 'sections'}")
        print()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest).resolve()

    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest = load_manifest(manifest_path)
    selected = filtered_sources(
        manifest,
        slugs=set(args.slug),
        providers=set(args.provider),
        limit=args.limit,
    )

    if not selected:
        print("No sources matched the filters.", file=sys.stderr)
        return 1

    if not args.dry_run:
        copy_manifest_into_repo(manifest_path, repo_root, dry_run=False, force=args.force)

    print(
        "Using a fixed manifest with serial downloads and sleeps. "
        "This is intentionally not a crawler."
    )
    if any(src.get("provider") == "gutenberg" for src in selected) and not args.scaffold_only:
        print(
            "Warning: Project Gutenberg's robot-access policy is strict. "
            "This script is conservative, but manual download or their official robot/harvest "
            "routes remain the most policy-conservative options."
        )
    print_plan(repo_root, selected)

    headers = dict(DEFAULT_HEADERS)
    headers["User-Agent"] = args.user_agent

    errors: list[str] = []
    for idx, source in enumerate(selected):
        print(f"[{idx + 1}/{len(selected)}] Processing {source['slug']}...")
        try:
            process_source(
                repo_root=repo_root,
                source=source,
                headers=headers,
                sleep_seconds=args.sleep,
                jitter_seconds=args.jitter,
                timeout=args.timeout,
                retries=args.retries,
                dry_run=args.dry_run,
                scaffold_only=args.scaffold_only,
                force=args.force,
            )
        except Exception as exc:  # noqa: BLE001
            msg = f"Error processing {source['slug']}: {exc}"
            print(msg, file=sys.stderr)
            errors.append(msg)
            if args.fail_fast:
                break

        # Sleep between sources too, so we do not burst by book.
        if idx < len(selected) - 1 and not args.scaffold_only:
            sleep_with_jitter(args.sleep, args.jitter)

    if errors:
        print("\nCompleted with errors:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
