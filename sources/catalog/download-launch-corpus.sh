#!/usr/bin/env bash
set -euo pipefail

# One-time, serial downloader for the curated launch corpus.
# Use sparingly. This is not a crawler and should not be expanded into site-wide automation.
# It downloads fixed direct file URLs only and sleeps between requests.

ROOT="${1:-.}"
mkdir -p "$ROOT/sources/raw/gutenberg" "$ROOT/sources/raw/web"

download() {
  local provider="$1"; shift
  local slug="$1"; shift
  local url="$1"; shift
  local outfile="$1"; shift
  mkdir -p "$ROOT/sources/raw/$provider/$slug"
  echo "Downloading $provider/$slug -> $outfile"
  curl -L --fail --retry 3 --retry-delay 2 "$url" -o "$ROOT/sources/raw/$provider/$slug/$outfile"
  sleep 2
}

metadata() {
  local provider="$1"; shift
  local slug="$1"; shift
  local url="$1"; shift
  local outfile="$1"; shift
  mkdir -p "$ROOT/sources/raw/$provider/$slug"
  echo "Downloading metadata $provider/$slug -> $outfile"
  curl -L --fail --retry 3 --retry-delay 2 "$url" -o "$ROOT/sources/raw/$provider/$slug/$outfile"
  sleep 2
}

download "gutenberg" "apology" "https://www.gutenberg.org/ebooks/1656.html.images" "source.html"
metadata "gutenberg" "apology" "https://www.gutenberg.org/cache/epub/1656/pg1656.rdf" "source.rdf"
download "gutenberg" "apology" "https://www.gutenberg.org/ebooks/1656.txt.utf-8" "source.txt"

download "gutenberg" "crito" "https://www.gutenberg.org/ebooks/1657.html.images" "source.html"
metadata "gutenberg" "crito" "https://www.gutenberg.org/cache/epub/1657/pg1657.rdf" "source.rdf"
download "gutenberg" "crito" "https://www.gutenberg.org/ebooks/1657.txt.utf-8" "source.txt"

download "gutenberg" "enchiridion" "https://www.gutenberg.org/ebooks/45109.html.images" "source.html"
metadata "gutenberg" "enchiridion" "https://www.gutenberg.org/cache/epub/45109/pg45109.rdf" "source.rdf"
download "gutenberg" "enchiridion" "https://www.gutenberg.org/ebooks/45109.txt.utf-8" "source.txt"

download "gutenberg" "meditations" "https://www.gutenberg.org/ebooks/2680.html.images" "source.html"
metadata "gutenberg" "meditations" "https://www.gutenberg.org/cache/epub/2680/pg2680.rdf" "source.rdf"
download "gutenberg" "meditations" "https://www.gutenberg.org/ebooks/2680.txt.utf-8" "source.txt"

download "gutenberg" "the-prince" "https://www.gutenberg.org/ebooks/1232.html.images" "source.html"
metadata "gutenberg" "the-prince" "https://www.gutenberg.org/cache/epub/1232/pg1232.rdf" "source.rdf"
download "gutenberg" "the-prince" "https://www.gutenberg.org/ebooks/1232.txt.utf-8" "source.txt"

download "gutenberg" "leviathan" "https://www.gutenberg.org/ebooks/3207.html.images" "source.html"
metadata "gutenberg" "leviathan" "https://www.gutenberg.org/cache/epub/3207/pg3207.rdf" "source.rdf"
download "gutenberg" "leviathan" "https://www.gutenberg.org/ebooks/3207.txt.utf-8" "source.txt"

download "gutenberg" "second-treatise-of-government" "https://www.gutenberg.org/ebooks/7370.html.images" "source.html"
metadata "gutenberg" "second-treatise-of-government" "https://www.gutenberg.org/cache/epub/7370/pg7370.rdf" "source.rdf"
download "gutenberg" "second-treatise-of-government" "https://www.gutenberg.org/ebooks/7370.txt.utf-8" "source.txt"

download "gutenberg" "on-liberty" "https://www.gutenberg.org/ebooks/34901.html.images" "source.html"
metadata "gutenberg" "on-liberty" "https://www.gutenberg.org/cache/epub/34901/pg34901.rdf" "source.rdf"
download "gutenberg" "on-liberty" "https://www.gutenberg.org/ebooks/34901.txt.utf-8" "source.txt"

download "gutenberg" "federalist-papers" "https://www.gutenberg.org/ebooks/18.html.images" "source.html"
metadata "gutenberg" "federalist-papers" "https://www.gutenberg.org/cache/epub/18/pg18.rdf" "source.rdf"
download "gutenberg" "federalist-papers" "https://www.gutenberg.org/ebooks/18.txt.utf-8" "source.txt"

download "gutenberg" "odyssey" "https://www.gutenberg.org/ebooks/1727.html.images" "source.html"
metadata "gutenberg" "odyssey" "https://www.gutenberg.org/cache/epub/1727/pg1727.rdf" "source.rdf"
download "gutenberg" "odyssey" "https://www.gutenberg.org/ebooks/1727.txt.utf-8" "source.txt"

download "gutenberg" "sophocles-oedipus-antigone" "https://www.gutenberg.org/ebooks/31.html.images" "source.html"
metadata "gutenberg" "sophocles-oedipus-antigone" "https://www.gutenberg.org/cache/epub/31/pg31.rdf" "source.rdf"
download "gutenberg" "sophocles-oedipus-antigone" "https://www.gutenberg.org/ebooks/31.txt.utf-8" "source.txt"

download "gutenberg" "hamlet" "https://www.gutenberg.org/ebooks/1524.html.images" "source.html"
metadata "gutenberg" "hamlet" "https://www.gutenberg.org/cache/epub/1524/pg1524.rdf" "source.rdf"
download "gutenberg" "hamlet" "https://www.gutenberg.org/ebooks/1524.txt.utf-8" "source.txt"

download "web" "bible-web" "https://ebible.org/Scriptures/engwebp_usfm.zip" "source.zip"
download "web" "bible-web" "https://ebible.org/Scriptures/engwebp_readaloud.zip" "fallback.zip"
download "web" "bible-web" "https://ebible.org/engwebp/copyright.htm" "rights.html"

download "gutenberg" "confessions" "https://www.gutenberg.org/ebooks/3296.html.images" "source.html"
metadata "gutenberg" "confessions" "https://www.gutenberg.org/cache/epub/3296/pg3296.rdf" "source.rdf"
download "gutenberg" "confessions" "https://www.gutenberg.org/ebooks/3296.txt.utf-8" "source.txt"

download "gutenberg" "city-of-god-vol-1" "https://www.gutenberg.org/ebooks/45304.html.images" "source.html"
metadata "gutenberg" "city-of-god-vol-1" "https://www.gutenberg.org/cache/epub/45304/pg45304.rdf" "source.rdf"
download "gutenberg" "city-of-god-vol-1" "https://www.gutenberg.org/ebooks/45304.txt.utf-8" "source.txt"

download "gutenberg" "romeo-and-juliet" "https://www.gutenberg.org/ebooks/1513.html.images" "source.html"
metadata "gutenberg" "romeo-and-juliet" "https://www.gutenberg.org/cache/epub/1513/pg1513.rdf" "source.rdf"
download "gutenberg" "romeo-and-juliet" "https://www.gutenberg.org/ebooks/1513.txt.utf-8" "source.txt"

download "gutenberg" "pride-and-prejudice" "https://www.gutenberg.org/ebooks/42671.html.images" "source.html"
metadata "gutenberg" "pride-and-prejudice" "https://www.gutenberg.org/cache/epub/42671/pg42671.rdf" "source.rdf"
download "gutenberg" "pride-and-prejudice" "https://www.gutenberg.org/ebooks/42671.txt.utf-8" "source.txt"

download "gutenberg" "vindication-rights-of-woman" "https://www.gutenberg.org/ebooks/3420.html.images" "source.html"
metadata "gutenberg" "vindication-rights-of-woman" "https://www.gutenberg.org/cache/epub/3420/pg3420.rdf" "source.rdf"
download "gutenberg" "vindication-rights-of-woman" "https://www.gutenberg.org/ebooks/3420.txt.utf-8" "source.txt"

download "gutenberg" "narrative-life-frederick-douglass" "https://www.gutenberg.org/ebooks/23.html.images" "source.html"
metadata "gutenberg" "narrative-life-frederick-douglass" "https://www.gutenberg.org/cache/epub/23/pg23.rdf" "source.rdf"
download "gutenberg" "narrative-life-frederick-douglass" "https://www.gutenberg.org/ebooks/23.txt.utf-8" "source.txt"

download "gutenberg" "frankenstein" "https://www.gutenberg.org/ebooks/42324.html.images" "source.html"
metadata "gutenberg" "frankenstein" "https://www.gutenberg.org/cache/epub/42324/pg42324.rdf" "source.rdf"
download "gutenberg" "frankenstein" "https://www.gutenberg.org/ebooks/42324.txt.utf-8" "source.txt"

download "gutenberg" "dr-jekyll-and-mr-hyde" "https://www.gutenberg.org/ebooks/42.html.images" "source.html"
metadata "gutenberg" "dr-jekyll-and-mr-hyde" "https://www.gutenberg.org/cache/epub/42/pg42.rdf" "source.rdf"
download "gutenberg" "dr-jekyll-and-mr-hyde" "https://www.gutenberg.org/ebooks/42.txt.utf-8" "source.txt"

download "gutenberg" "picture-of-dorian-gray" "https://www.gutenberg.org/ebooks/26740.html.images" "source.html"
metadata "gutenberg" "picture-of-dorian-gray" "https://www.gutenberg.org/cache/epub/26740/pg26740.rdf" "source.rdf"
download "gutenberg" "picture-of-dorian-gray" "https://www.gutenberg.org/ebooks/26740.txt.utf-8" "source.txt"

download "gutenberg" "novum-organum" "https://www.gutenberg.org/ebooks/45988.html.images" "source.html"
metadata "gutenberg" "novum-organum" "https://www.gutenberg.org/cache/epub/45988/pg45988.rdf" "source.rdf"
download "gutenberg" "novum-organum" "https://www.gutenberg.org/ebooks/45988.txt.utf-8" "source.txt"

download "gutenberg" "discourse-on-method" "https://www.gutenberg.org/ebooks/59.html.images" "source.html"
metadata "gutenberg" "discourse-on-method" "https://www.gutenberg.org/cache/epub/59/pg59.rdf" "source.rdf"
download "gutenberg" "discourse-on-method" "https://www.gutenberg.org/ebooks/59.txt.utf-8" "source.txt"

download "gutenberg" "origin-of-species" "https://www.gutenberg.org/ebooks/1228.html.images" "source.html"
metadata "gutenberg" "origin-of-species" "https://www.gutenberg.org/cache/epub/1228/pg1228.rdf" "source.rdf"
download "gutenberg" "origin-of-species" "https://www.gutenberg.org/ebooks/1228.txt.utf-8" "source.txt"
