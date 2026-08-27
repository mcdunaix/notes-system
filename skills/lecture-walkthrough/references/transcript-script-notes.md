# transcript.py: Current Behavior (2026-07-08 protocol rewrite)

`scripts/transcript.py` maintains 8 documented storage invariants (module docstring; pinned as D-8 in `docs/STORAGE_PROTOCOL.md`). What matters when editing transcript files from this skill:

- **IDs are permanent and monotone.** Allocation takes max(live frontmatter IDs ∪ IDs recorded in the existing `000-dashboard/Index.md`) + 1. A dropped `id:` line can no longer cause an ID to be reissued, but it still orphans the entry (`??` in the index). Never drop it.
- **`verify` command**: `python3 scripts/transcript.py verify`, audits: missing/duplicate/malformed `id:`, unparseable frontmatter, category/folder drift (frontmatter `categories[0]` must equal the containing folder name), fenced-transcript integrity under `## Full Text` (legacy headings `## Full Transcript` / `## Transcript` / `## Raw Transcript` accepted), and duplicate content keys. Non-zero exit on violation. **Run it after every write-back.**
- **`rebuild`, `list`, `verify` are stdlib-only**: they run under any `python3`. Only `add` needs `yt_dlp` / `youtube_transcript_api` / `pymupdf`.
- **Dedup on add:** YouTube by `video_id`, PDFs by resolved path, social posts by normalized URL. `--force` bypasses (YouTube only).
- **Writes escape their formats:** YAML strings (quotes/backslashes) and `|` in Index.md table cells. Filenames are ID-keyed, `transcripts/<category>/<NC-id>_<slug>.md` (D-9, 2026-07-08; the old `<date>_<slug>` names are gone), so a filename collision means a reissued ID and the add aborts. The slug comes from `add --topics "..."` (D-13, 2026-07-10; the phrase is also stored as `topics:` frontmatter); omitted, it falls back to the source title with a printed nudge. Always pass `--topics`. New entries always write `## Full Text`.
- **Files are never renamed by the script**, and recategorizing an already-linked entry means editing frontmatter, not moving the file (domain indexes wikilink by path). Moving a *fresh* entry immediately after `add`, before any links exist, is fine (step 3 of the skill), provided frontmatter `categories[0]` and `domain` are updated to match.

## Rebuild command

```bash
cd $CATALOG_ROOT && python3 scripts/transcript.py rebuild && python3 scripts/transcript.py verify
```

Rebuilds `000-dashboard/Index.md` and audits invariants. Does NOT touch domain-level indices (`01-engineering/00-Index.md`, etc.) or course landing pages. Those are maintained manually.

## Scoring-based classifier (July 2026)

`guess_category()` scores each category by keyword hit count (word-boundary matched) in title + transcript; highest score wins, ties broken by `CATEGORY_RULES` order. Returns `[best, ...at most 2 secondaries scoring ≥ max(2, best//4)]`, the first element determines file location (`transcripts/<best>/`).

**Why:** a neuroscience video mentioning "machine learning" once but "neuron" 20+ times lands in `science`, not `ai-ml`. The secondary cap (2026-07-08) stops stray keyword hits from tagging a 50-minute lecture with six categories.

## Fixed bugs (history: do NOT re-apply these patches)

- `NameError: name 'cat' is not defined` in `save_entry()`, fixed in the 2026-07-08 rewrite; the current script has no such line. Seeing this error means a stale copy is running.
- Instagram descriptions were truncated at the literal string "To honor", hack removed.
- `rebuild`/`list` used to crash on machines without `yt_dlp`, now stdlib-only.
- Index summary undercounted (Instagram/TikTok entries invisible) and unescaped `|` in titles broke table rows, both fixed.
