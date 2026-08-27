# notes-system: catalog tooling repo (agent on-ramp)

Tooling and protocol for a transcript/research catalog with persistent
NC-#### IDs. The database ships EMPTY and FOLDER-LESS (no personal notes, no
content folders). The repo root is the catalog root (`$CATALOG_ROOT`), the
directory containing `scripts/transcript.py`. This file is the on-ramp a
Hermes or Claude Code session reads when working in this directory; keep it
short, running state lives in `SESSION_STATE.md`.

## How to resume

Read `SESSION_STATE.md` "Resume here" (newest entry first).

## Where things live

- `scripts/transcript.py`: ingest + rebuild + list + verify (the pipeline)
- `scripts/next-id.py`: NC-#### allocator, scans `transcripts/` AND `references/`
- `scripts/test_*.py`: protocol test vectors (R-15)
- `scripts/install-skills.sh`: symlink/copy `skills/` into `~/.hermes/skills/productivity/`
- `skills/`: Hermes skills (SKILL.md format), five of them
- `docs/STORAGE_PROTOCOL.md`: invariants I1-I8 + conventions (D-# ids kept as vocabulary)
- `docs/INGESTION_PIPELINE.md`: the cleaned ingest-to-file routine map
- `requirements.txt`: fetch deps for `add`; everything else is stdlib
- `.github/workflows/ci.yml`: vectors + empty-db gate + installer + D-12 sweep
- `transcripts/`, `references/`, `labs/`, `briefs/`: content folders are NOT
  committed. `add` creates `transcripts/<category>/`; `rebuild` creates
  `000-dashboard/Index.md`; domain/category `00-Index.md` files and the
  `references/`, `labs/`, `briefs/` dirs are created by the agent during use.

## Conventions (the rules agents must not break)

- **No em dashes, ever (D-12).** Neither U+2014 nor `--` as punctuation,
  in entries, docs, or skills. A comma, a colon, or two sentences.
- **Files are truth.** `Index.md` is derived, `rebuild` remakes it.
- **Never drop the `id:` frontmatter line.** Allocate ids with
  `scripts/next-id.py`, never by hand.
- **The slug names the topic, not the title (D-13).** Always pass
  `--topics "..."` to `add`.
- **`verify` must exit 0** after any external edit to a transcript or
  reference entry. It scans both `transcripts/` and `references/`; the
  one reference-only exemption is `--` inside fenced code blocks (CLI
  flags quoted in analysis), em dashes stay banned everywhere.
- **Categories are fixed vocabulary.** `categories[0]` must match the
  containing folder. Extending the vocabulary is test-vectors-first (R-15).
- **Domain/category indexes are hand-curated** and are the primary
  Obsidian navigation. `rebuild` only touches the dashboard.
- **Never rename content files day-to-day (D-8).** A rename is a
  deliberate, verify-gated migration (D-9).
- **No personal vault content ships here.** Skills that reference research
  documents NC-0030/NC-0031 say so and note they are the author's private
  vault, not this repo.

## Commands

```bash
export CATALOG_ROOT="$(pwd)"                       # skills use this for every path
python3 -m pip install -r requirements.txt         # fetch deps, needed by `add` only
python3 scripts/transcript.py add <url> --topics "topic phrase"   # YouTube/Instagram/TikTok
python3 scripts/transcript.py add --pdf <path> --topics "..."     # PDF
python3 scripts/transcript.py list                 # list entries
python3 scripts/transcript.py rebuild              # regenerate dashboard
python3 scripts/transcript.py verify               # audit storage invariants
python3 scripts/next-id.py                         # next free NC id
python3 scripts/next-id.py --check                 # collision check (transcripts + references)
./scripts/install-skills.sh                        # install skills into Hermes
for t in scripts/test_*.py; do python3 "$t"; done  # all test vectors
python3 scripts/test_topics_slug.py                # one vector file
```

`add` needs `yt_dlp` / `youtube_transcript_api` / `pymupdf`; the rest are
stdlib-only. Tests are standalone scripts, no pytest: each prints GREEN or
RED and exits 1 on failure, and none touches the catalog.

## Architecture notes

- `scripts/transcript.py` is a single self-contained file. The invariants
  I1-I8 in its module docstring map one-to-one onto its code sections; read
  that docstring before changing the pipeline.
- ID allocation (I2) is loss-proof by union: live frontmatter ids in
  `transcripts/`, ids in `references/`, and ids recorded in the derived
  `000-dashboard/Index.md`. An `id:` line lost to an external edit shrinks
  the live set but not the index set, so numbers stay monotone.
  `scripts/next-id.py` repeats this scan standalone for agents filing into
  `references/` (the blind spot that once caused a live NC-0034 collision).
- The category vocabulary is code, not config: `CATEGORY_RULES`,
  `CATEGORY_DOMAIN`, and `KNOWN_DOMAINS` in `transcript.py`. `verify`
  enforces them, so extending the vocabulary means a test vector first
  (R-15), then those tables, then the folder.
- `verify` also runs the D-12 dash scan on every transcript entry,
  including the fenced `## Full Text` block (D-25), and on every
  reference entry (where fenced code is exempt from the `--` check
  only). YAML fences and table separator lines are always exempt.
- Tests load `transcript.py` via importlib and call its functions directly.
  Four are pure-function vectors; `test_topics_slug.py` repoints
  `TRANSCRIPTS_DIR` at a temp dir before writing. All five run green on a
  fresh, folder-less clone.

## Skills (mandatory)

Before expanding or filing a catalog entry, load the matching skill and
follow it. Skills are the operational instructions for this repo's content
work; this file is only the on-ramp.

| Task | Skill |
|---|---|
| Maintain the catalog, run the CLI, dedupe, categorize | `content-catalog` |
| Expand a lecture/video transcript into a walkthrough | `lecture-walkthrough` |
| Review hardware/model/tool, guided Discussion, topic Probe | `review-discussion-probe` |
| Build hands-on lab guides | `lab-builder` |
| Fact-check a walkthrough's claims | `lecture-vetting` |
