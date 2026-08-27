# The Ingest-to-File Routine Map

The end-to-end chain from "a link shows up" to "a filed, indexed, verified
note". This document is the cleaned version of routines that grew organically
in the author's vault; the cleanup notes at the bottom say what changed and
why it matters for anyone maintaining this repo.

## The chain, step by step

```
capture          -> ingest          -> file         -> expand      -> verify   -> index
link / PDF /     -> transcript.py   -> correct      -> skill       -> gates    -> wikilink
video file          add               category/kind   walkthrough    D-12, id,   in the
                                        folder         or review/     fences      domain
                                                        discussion/               index
                                                        probe
```

### 1. Capture

A link, a PDF path, or (for short video) a downloaded media file arrives.
`content-catalog` is the skill that owns this step; it knows the CLI and
the fallbacks.

### 2. Ingest (transcript.py add)

One command does the whole mechanical pass: fetch metadata, fetch full text,
auto-categorize by keyword score, assign the next NC id, save the entry,
rebuild the dashboard.

```bash
python3 scripts/transcript.py add "https://youtube.com/watch?v=..." \
    --topics "topic phrase, topic phrase"     # D-13: the slug names the topic
python3 scripts/transcript.py add --pdf "path/to/doc.pdf" --topics "..."
```

Rules: always pass `--topics`; dedup is automatic per source; saves never
overwrite; the printed NC id is load-bearing.

### 3. File (the judgment call the script cannot make)

The script files into `transcripts/<category>/` by its keyword classifier.
Before any expansion, check that the auto-category is right:

- The category is canonical for the series or topic (lectures of one course
  all live together; a talk that landed in `tech` may belong in
  `talks-interviews`).
- The category has a live domain index; if it does not, redirect the entry
  to a category that does. Do NOT create a domain index as a workaround.
- For non-video work (hardware, model, tool, topic), the entry belongs in
  `references/` with a `kind:` field, not `transcripts/`.

Moving a file between categories is a D-9 migration: `git mv` the file and
edit `categories[0]` together, atomically, with every wikilink rewritten in
the same commit, `verify`-gated. Never a frontmatter-only edit, never a
bare file move.

### 4. Expand (the skills)

| Content | Skill | Output |
|---|---|---|
| Lecture / didactic video | `lecture-walkthrough` | Structured walkthrough: hook, core idea, toolbox, architecture, results, punchline; references; `## Full Text` preserved below |
| Hardware / model / tool | `review-discussion-probe` (Review) | Research + breakdown + verified claims + verdict |
| Video or artifact to discuss | `review-discussion-probe` (Discussion) | Guided discussion scaffold, questions and tensions |
| Open topic | `review-discussion-probe` (Probe) | Current state, cutting edge, trajectories, related tech |
| Hands-on lab | `lab-builder` | Four gated phases to a tested guide with a real-run record |
| Existing walkthrough | `lecture-vetting` | Multi-perspective fact-check, advisory, annotates in place |

All expansion happens with `$CATALOG_ROOT` paths, never hardcoded machine
paths. Reference entries allocate their NC id via `scripts/next-id.py`
(which scans `references/`, closing the gap that `transcript.py` has).

### 5. Verify (the gates)

- `python3 scripts/transcript.py verify` must exit 0 after any edit to a
  transcript entry. It checks ids, categories, folder drift, the `## Full
  Text` fence, and D-12 dash violations.
- Reference entries are not covered by that scan. Gate them manually:
  `grep -c $'—' references/NC-XXXX_*.md` must print 0, and a
  `grep -n -- '--' ...` must show no prose uses. `scripts/next-id.py
  --check` confirms the whole catalog has no id collisions.
- `scripts/transcript.py rebuild` regenerates the dashboard after any set
  of changes.

### 6. Index (make it reachable)

`rebuild` only touches `000-dashboard/Index.md`. The domain and category
indexes are hand-curated and are the primary Obsidian navigation. After
filing an entry:

- add its wikilink to the matching category index (`01-engineering/01-ai/00-Index.md`,
  `02-culture-society/01-talks-interviews/00-Index.md`, ...), id order,
  duration, `topics:` phrase indented;
- if the entry belongs to a series, update the series sub-page and the
  lecture chain (Up/Previous/Next) per `lecture-walkthrough`;
- bump entry counts in parent indexes.

An entry without its wikilink is filed but invisible.

## What was cleaned up (2026-08-26 factoring)

The routines above were copied out of the author's vault with these fixes:

1. **Paths parameterized.** Every skill hardcoded `~/Documents/notes`.
   Now each skill defines `$CATALOG_ROOT` (the repo root) and every
   command/prose uses it. Nothing references the author's machine.
2. **Stale `tech` to `03-it` redirect removed (6 spots).** The vault
   archived its `03-it` domain; the skills' short-form pipeline still
   told agents to redirect `tech` entries to it and warned it was
   archived. Rewritten to the general rule: a category without a live
   domain index is invisible, redirect to a category that has one.
3. **Literal newline artifact fixed.** One pitfall line in
   `lecture-walkthrough` had two bullets glued together with a literal
   `\n` and escaped quotes; split back into two bullets.
4. **ID allocation gap closed.** `transcript.py` only sees
   `transcripts/`; the vault suffered a live NC-0034 collision because
   `references/` shares the numbering. `scripts/next-id.py` scans both
   trees and is the allocator for reference entries.
5. **D-12 scrubbed from the shipped docs.** 142 em dashes removed from
   the skill files (only the detector command in `lab-builder`'s
   self-audit and the table placeholders keep `--`, both exempt).
6. **Dangling pointers removed.** Skill copies referenced personal vault
   files (`NC-0030`, `NC-0031`, `briefs/...`, `decisions.md`). These now
   either point to shipped docs (`docs/STORAGE_PROTOCOL.md`) or note
   explicitly that the research document is a personal artifact not
   shipped.
7. **Duplication removed.** `content-catalog` had a verbatim duplicate
   of the file-explorer block and a duplicated startup-page line; the
   retired `it` domain was dropped from structure docs.
8. **New mode skill.** `review-discussion-probe` adds Review / Discussion
   / Probe on top of the same protocol, with the manual reference-entry
   gate built into it.

The author's live vault was intentionally left untouched; these changes
exist in this repo only. If you also maintain the original vault, port
the fixes deliberately, not wholesale (the vault has personal paths and
content that this repo does not).
