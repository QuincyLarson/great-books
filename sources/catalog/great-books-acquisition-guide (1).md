# Great Books launch corpus acquisition guide

This guide is designed for a **one-time editorial ingest** before you hand the repo to Codex.

## The short answer

Yes, you *can* download everything first and then run a local transform. But do **not** dump all files into one folder.

Use this shape instead:

```text
sources/
  raw/
    gutenberg/
      apology/
        source.html
        source.txt
        source.rdf
        source-lock.json
    web/
      bible-web/
        source.zip
        fallback.zip
        rights.html
        source-lock.json
```

## What to download

For **Project Gutenberg** works, download **three files** per title:

1. `source.html` → the direct `...html.images` file
2. `source.txt` → the direct `...txt.utf-8` file as fallback
3. `source.rdf` → the per-eBook metadata sidecar

For **World English Bible**, download:

1. `source.zip` → `engwebp_usfm.zip`
2. `fallback.zip` → `engwebp_readaloud.zip`
3. `rights.html` → the copyright/public-domain page

## Exact steps

1. Create the repo folders: `sources/raw`, `sources/catalog`, `content/texts`.
2. Download each raw source into its own slug folder immediately. Do not put all books into one shared folder.
3. For Gutenberg works, prefer the single-file `html.images` URL. Only use the `.zip` HTML bundle if the single HTML file is malformed or missing content.
4. Also save the Gutenberg `.rdf` file for provenance and reproducibility.
5. For the Bible, use `engwebp_usfm.zip` as the canonical raw source. That preserves book/chapter/verse structure much better than plain text.
6. After download, create `source-lock.json` in each raw folder with retrieval date, landing URL, source URL, checksum, and editorial notes.
7. Run your local normalization script to convert raw sources into house editions under `content/texts/**`.
8. Commit both the raw snapshots and the normalized house editions before giving the repo to Codex.

## What the normalization script should do

For each source:
- Strip Gutenberg nav/footer/boilerplate from the working reading copy.
- Preserve semantic structure: headings, paragraphs, quotations, lists, speech labels, stage directions, verse/line groups, footnotes if retained.
- Assign stable block IDs. Use verse IDs for Bible content and paragraph/speech IDs for other texts.
- Split long works into natural static sections.
- Write normalized files into `content/texts/{slug}/` as `manifest.json`, `rights.json`, and `sections/*.html` plus `sections/*.meta.json`.

### Recommended sectioning rules

- **Dialogues:** one section per dialogue unless very long; preserve speaker labels if present
- **Meditations:** one section per book
- **Political/philosophical prose:** one section per chapter or essay
- **Shakespeare plays:** one section per act/scene
- **Greek plays:** one section per full play for MVP, or split by major scene/strophe boundaries if you want shorter pages
- **Novels:** one section per chapter
- **Bible:** one section per chapter, verse-level anchors inside the section HTML

## Full launch corpus list

| Raw source slug | Normalized work slug(s) | Title | Source page | Recommended download | Fallback | Metadata / rights | Launch usage | Notes |
|---|---|---|---|---|---|---|---|---|
| `apology` | `apology` | Apology | https://www.gutenberg.org/ebooks/1656 | https://www.gutenberg.org/ebooks/1656.html.images | https://www.gutenberg.org/ebooks/1656.txt.utf-8 | https://www.gutenberg.org/cache/epub/1656/pg1656.rdf | full | Full text; one normalized section. |
| `crito` | `crito` | Crito | https://www.gutenberg.org/ebooks/1657 | https://www.gutenberg.org/ebooks/1657.html.images | https://www.gutenberg.org/ebooks/1657.txt.utf-8 | https://www.gutenberg.org/cache/epub/1657/pg1657.rdf | full | Full text; one normalized section. |
| `enchiridion` | `enchiridion` | The Enchiridion | https://www.gutenberg.org/ebooks/45109 | https://www.gutenberg.org/ebooks/45109.html.images | https://www.gutenberg.org/ebooks/45109.txt.utf-8 | https://www.gutenberg.org/cache/epub/45109/pg45109.rdf | full | Full text; preserve numbered aphorisms as block-level IDs. |
| `meditations` | `meditations` | Meditations | https://www.gutenberg.org/ebooks/2680 | https://www.gutenberg.org/ebooks/2680.html.images | https://www.gutenberg.org/ebooks/2680.txt.utf-8 | https://www.gutenberg.org/cache/epub/2680/pg2680.rdf | full | Split by Book I–XII; section slugs book-1 … book-12. |
| `the-prince` | `the-prince` | The Prince | https://www.gutenberg.org/ebooks/1232 | https://www.gutenberg.org/ebooks/1232.html.images | https://www.gutenberg.org/ebooks/1232.txt.utf-8 | https://www.gutenberg.org/cache/epub/1232/pg1232.rdf | full | Extract only The Prince, not the additional appended texts in this edition; split by chapters 1–26. |
| `leviathan` | `leviathan` | Leviathan | https://www.gutenberg.org/ebooks/3207 | https://www.gutenberg.org/ebooks/3207.html.images | https://www.gutenberg.org/ebooks/3207.txt.utf-8 | https://www.gutenberg.org/cache/epub/3207/pg3207.rdf | selected | Launch v1 selections: ch. 13–15, 17–18. |
| `second-treatise-of-government` | `second-treatise-of-government` | Second Treatise of Government | https://www.gutenberg.org/ebooks/7370 | https://www.gutenberg.org/ebooks/7370.html.images | https://www.gutenberg.org/ebooks/7370.txt.utf-8 | https://www.gutenberg.org/cache/epub/7370/pg7370.rdf | selected | Launch v1 selections: ch. 2, 5, 8, 9, 19. |
| `on-liberty` | `on-liberty` | On Liberty | https://www.gutenberg.org/ebooks/34901 | https://www.gutenberg.org/ebooks/34901.html.images | https://www.gutenberg.org/ebooks/34901.txt.utf-8 | https://www.gutenberg.org/cache/epub/34901/pg34901.rdf | full | Split by Introductory + chapters 1–5. |
| `federalist-papers` | `federalist-papers` | The Federalist Papers | https://www.gutenberg.org/ebooks/18 | https://www.gutenberg.org/ebooks/18.html.images | https://www.gutenberg.org/ebooks/18.txt.utf-8 | https://www.gutenberg.org/cache/epub/18/pg18.rdf | selected | Launch v1 selections: Nos. 1, 10, 14, 39, 51, 78, 84. |
| `odyssey` | `odyssey` | The Odyssey | https://www.gutenberg.org/ebooks/1727 | https://www.gutenberg.org/ebooks/1727.html.images | https://www.gutenberg.org/ebooks/1727.txt.utf-8 | https://www.gutenberg.org/cache/epub/1727/pg1727.rdf | selected | Launch v1 selections: Books 1, 5, 9–12, 23. |
| `sophocles-oedipus-antigone` | `oedipus-rex, antigone` | Plays of Sophocles: Oedipus the King; Oedipus at Colonus; Antigone | https://www.gutenberg.org/ebooks/31 | https://www.gutenberg.org/ebooks/31.html.images | https://www.gutenberg.org/ebooks/31.txt.utf-8 | https://www.gutenberg.org/cache/epub/31/pg31.rdf | selected | One raw source feeds two normalized works. Extract Oedipus the King and Antigone as separate works; ignore Oedipus at Colonus for MVP. |
| `hamlet` | `hamlet` | Hamlet | https://www.gutenberg.org/ebooks/1524 | https://www.gutenberg.org/ebooks/1524.html.images | https://www.gutenberg.org/ebooks/1524.txt.utf-8 | https://www.gutenberg.org/cache/epub/1524/pg1524.rdf | full | Split by act/scene. Preserve speech speakers and stage directions semantically. |
| `bible-web` | `bible-web` | World English Bible Protestant Edition | https://ebible.org/engwebp/ | https://ebible.org/Scriptures/engwebp_usfm.zip | https://ebible.org/Scriptures/engwebp_readaloud.zip | https://ebible.org/engwebp/copyright.htm | selected | Use USFM as canonical raw source; normalize to book/chapter sections with verse-level anchors. Launch v1 selections only, not full Bible UI. |
| `confessions` | `confessions` | The Confessions of St. Augustine | https://www.gutenberg.org/ebooks/3296 | https://www.gutenberg.org/ebooks/3296.html.images | https://www.gutenberg.org/ebooks/3296.txt.utf-8 | https://www.gutenberg.org/cache/epub/3296/pg3296.rdf | selected | Launch v1 selections: Books 1, 2, 3, 7, 8, 10, 11. |
| `city-of-god-vol-1` | `city-of-god-book-1` | The City of God, Volume I | https://www.gutenberg.org/ebooks/45304 | https://www.gutenberg.org/ebooks/45304.html.images | https://www.gutenberg.org/ebooks/45304.txt.utf-8 | https://www.gutenberg.org/cache/epub/45304/pg45304.rdf | selected | Launch v1: Book I only. Extract as a standalone normalized work. |
| `romeo-and-juliet` | `romeo-and-juliet` | Romeo and Juliet | https://www.gutenberg.org/ebooks/1513 | https://www.gutenberg.org/ebooks/1513.html.images | https://www.gutenberg.org/ebooks/1513.txt.utf-8 | https://www.gutenberg.org/cache/epub/1513/pg1513.rdf | full | Split by act/scene. |
| `pride-and-prejudice` | `pride-and-prejudice` | Pride and Prejudice | https://www.gutenberg.org/ebooks/42671 | https://www.gutenberg.org/ebooks/42671.html.images | https://www.gutenberg.org/ebooks/42671.txt.utf-8 | https://www.gutenberg.org/cache/epub/42671/pg42671.rdf | selected | Use improved edition #42671. Launch v1 selections: ch. 1–6, 34, 42–43, 58–61. |
| `vindication-rights-of-woman` | `vindication-rights-of-woman` | A Vindication of the Rights of Woman | https://www.gutenberg.org/ebooks/3420 | https://www.gutenberg.org/ebooks/3420.html.images | https://www.gutenberg.org/ebooks/3420.txt.utf-8 | https://www.gutenberg.org/cache/epub/3420/pg3420.rdf | selected | Launch v1 selections: intro + ch. 2–5 + ch. 13. |
| `narrative-life-frederick-douglass` | `narrative-life-frederick-douglass` | Narrative of the Life of Frederick Douglass, an American Slave | https://www.gutenberg.org/ebooks/23 | https://www.gutenberg.org/ebooks/23.html.images | https://www.gutenberg.org/ebooks/23.txt.utf-8 | https://www.gutenberg.org/cache/epub/23/pg23.rdf | full | Split by chapters 1–11 + appendix if retained. |
| `frankenstein` | `frankenstein` | Frankenstein; Or, The Modern Prometheus | https://www.gutenberg.org/ebooks/42324 | https://www.gutenberg.org/ebooks/42324.html.images | https://www.gutenberg.org/ebooks/42324.txt.utf-8 | https://www.gutenberg.org/cache/epub/42324/pg42324.rdf | full | Use improved 1831 edition #42324 for launch. Split by letters/chapters. |
| `dr-jekyll-and-mr-hyde` | `dr-jekyll-and-mr-hyde` | The Strange Case of Dr. Jekyll and Mr. Hyde | https://www.gutenberg.org/ebooks/42 | https://www.gutenberg.org/ebooks/42.html.images | https://www.gutenberg.org/ebooks/42.txt.utf-8 | https://www.gutenberg.org/cache/epub/42/pg42.rdf | full | Split by chapters. |
| `picture-of-dorian-gray` | `picture-of-dorian-gray` | The Picture of Dorian Gray | https://www.gutenberg.org/ebooks/26740 | https://www.gutenberg.org/ebooks/26740.html.images | https://www.gutenberg.org/ebooks/26740.txt.utf-8 | https://www.gutenberg.org/cache/epub/26740/pg26740.rdf | full | Use smaller text edition #26740 for launch. Split by chapters. |
| `novum-organum` | `novum-organum` | Novum Organum | https://www.gutenberg.org/ebooks/45988 | https://www.gutenberg.org/ebooks/45988.html.images | https://www.gutenberg.org/ebooks/45988.txt.utf-8 | https://www.gutenberg.org/cache/epub/45988/pg45988.rdf | selected | Launch v1 selections: preface + Book I aphorisms 1–68 and 91–130. |
| `discourse-on-method` | `discourse-on-method` | Discourse on the Method of Rightly Conducting One's Reason and of Seeking Truth in the Sciences | https://www.gutenberg.org/ebooks/59 | https://www.gutenberg.org/ebooks/59.html.images | https://www.gutenberg.org/ebooks/59.txt.utf-8 | https://www.gutenberg.org/cache/epub/59/pg59.rdf | selected | Launch v1 selections: Parts I–IV; full text is short enough if desired. |
| `origin-of-species` | `origin-of-species` | On the Origin of Species By Means of Natural Selection | https://www.gutenberg.org/ebooks/1228 | https://www.gutenberg.org/ebooks/1228.html.images | https://www.gutenberg.org/ebooks/1228.txt.utf-8 | https://www.gutenberg.org/cache/epub/1228/pg1228.rdf | selected | Use first edition #1228. Launch v1 selections: ch. 3, 4, 6, 9, 14. |

## Recommended `source-lock.json` format

```json
{
  "retrievedAt": "2026-03-24",
  "landingUrl": "https://www.gutenberg.org/ebooks/2680",
  "sourceUrl": "https://www.gutenberg.org/ebooks/2680.html.images",
  "fallbackUrl": "https://www.gutenberg.org/ebooks/2680.txt.utf-8",
  "metadataUrl": "https://www.gutenberg.org/cache/epub/2680/pg2680.rdf",
  "format": "html",
  "sha256": "<fill-after-download>",
  "rightsNotes": [
    "Public domain in the USA",
    "Remove Project Gutenberg boilerplate from the reading copy",
    "Keep upstream source snapshot unchanged in sources/raw"
  ],
  "editorialNotes": [
    "Split by Book I-XII"
  ]
}
```

## Suggested normalization outputs

```text
content/texts/
  meditations/
    manifest.json
    rights.json
    sections/
      book-1.html
      book-1.meta.json
      book-2.html
      book-2.meta.json

  bible-web/
    manifest.json
    rights.json
    sections/
      genesis-1.html
      genesis-1.meta.json
      matthew-5.html
      matthew-5.meta.json
```

## Recommended answer to your own question

### Can I just right-click download them all to the same folder?

You *can*, but you **should not**.

The better workflow is:

1. use the curated direct URLs in this guide,
2. download each title into its own slug folder,
3. generate `source-lock.json`,
4. run the normalization script,
5. commit both raw and normalized content,
6. then hand the repo to Codex.

That minimizes Codex token burn because Codex will only need to build the reader and the curriculum shell against already-present content.