# Storage Protocol

The rules that keep the catalog consistent. This repo was factored out of
the author's vault, where each rule was pinned as a numbered decision
(D-#). The ids are kept here as vocabulary so the skills can cite them;
the decision history itself is not shipped. Skills occasionally cite a
D-# that is not defined below (D-2, D-3, D-4, D-7, D-15, D-19, D-20,
D-23): those are pinned in the author's private decision log, and every
citing sentence is written to stand on its own without the definition.

## Vocabulary

- **Catalog**: the whole database of notes rooted at `$CATALOG_ROOT`
  (this repo's root, the directory containing `scripts/transcript.py`).
- **Vault**: the same thing seen from Obsidian; the author's original
  private catalog is also called "the vault" in skill prose.
- **NC-XXXX**: a Notes Catalog id, e.g. `NC-0042`. Permanent, unique,
  allocated by the tooling, never reused and never hand-picked.
- **Entry**: one Markdown file with YAML frontmatter and an NC id.
  Transcript entries carry raw source text; reference entries carry
  analysis (reviews, probes, research notes).
- **Walkthrough**: a transcript entry expanded by the
  `lecture-walkthrough` skill into a structured, teachable writeup with
  the raw transcript preserved below.
- **D-#**: a pinned protocol decision (this document). **R-15**: the rule
  that core-logic changes get test vectors written before implementation
  (`scripts/test_*.py`).
- **Skill**: an instruction file (`SKILL.md`) an agent loads to do one
  kind of content work. **Gateway**: Hermes's capture channel (e.g. a
  Telegram bot) that feeds links and media into the pipeline; optional.

## The invariants (I1-I8)

`scripts/transcript.py` maintains these invariants, and `verify` audits
them. Full detail lives in the module docstring; the readable version:

- **I1 Files are truth.** `transcripts/<category>/<NC-id>_<slug>.md` with
  YAML frontmatter is the only durable store. `000-dashboard/Index.md`
  and `list` output are derived views, regenerable any time with
  `rebuild`. The slug names the topic(s) passed via `--topics`, falling
  back to the source title only when no topics were given (D-13); the
  verbatim title always survives in frontmatter.
- **I2 IDs are permanent, unique, monotone.** Allocation takes
  max(live frontmatter ids, Index.md ids) + 1, so an `id:` line lost to
  an external edit can never cause a reissue. `scripts/next-id.py`
  extends the same rule to `references/`.
- **I3 One scan per command, frontmatter only.** Every command reads the
  catalog once and parses only the frontmatter block, never transcript
  bodies.
- **I4 Every add is deduplicated** by a per-source content key
  (youtube -> video_id, pdf -> resolved path, social -> normalized URL).
- **I5 Derived views escape their format:** YAML strings on write, `|` in
  Index.md table cells.
- **I6 Saves never overwrite.** Filenames are keyed by the unique entry
  id, so a collision means an id was reissued and the add aborts.
  Existing files are never renamed (domain indexes wikilink them by path).
- **I7 `verify` audits** missing/duplicate ids, unparseable frontmatter,
  category/folder drift, `## Full Text` fence integrity, and D-12 dash
  violations, across `transcripts/` and `references/` (see "Entry kinds"
  for which checks apply to references). Exits non-zero on violations.
- **I8 rebuild/list/verify run on stdlib alone.** `yt_dlp`,
  `youtube_transcript_api`, and `fitz` import lazily inside the fetch
  paths that need them.

## Entry kinds and where they live

| Kind | Directory | Carries | Gate |
|---|---|---|---|
| Transcript entry (video, social, PDF) | `transcripts/<category>/` | Raw text under `## Full Text` (fenced) | `transcript.py verify` (automated) |
| Reference entry (Review, Probe, artifact Discussion, research notes) | `references/` | Analysis, no raw transcript | `transcript.py verify` (automated) |

Both kinds share the NC-XXXX numbering, and `verify` audits both trees:
references/ entries are checked for parseable frontmatter, id integrity
against the whole id space (the cross-tree collision class), and D-12
dashes. One reference-only exemption: `--` inside a fenced code block is
allowed there, because reference entries legitimately quote CLI flags.
Em dashes stay banned everywhere. References carry analysis rather than
transcripts, so the `## Full Text` and folder-drift checks do not apply
to them. `scripts/next-id.py --check` remains the standalone allocator
cross-check.

## Conventions (the pinned decisions)

- **D-8 Never rename content files day-to-day.** A rename is legal only as
  a deliberate migration (D-9): every reference rewritten in the same
  commit, gated on `verify`.
- **D-9 Migrations rewrite every reference in one commit**, then pass
  `verify`. Applies to renames and recategorizations alike.
- **D-12 No em dashes, ever.** Neither the character (U+2014) nor `--`
  used as punctuation, in any entry body or fenced transcript. A comma, a
  colon, or two sentences. Plain hyphens for structural separators. D-25
  revoked any exemption for full-text blocks.
- **D-13 The slug names the topic(s), not the source title.** Pass
  `--topics "..."` to `add`; the phrase becomes the filename slug and a
  `topics:` frontmatter field. Omitted, the slug falls back to the title
  and the add prints a nudge.
- **D-14 Extending the vocabulary (a new Domain or Category) follows a
  pattern:** R-15 test vectors first (`scripts/test_*.py`, RED before,
  GREEN after), then a deliberate `CATEGORY_RULES` / `CATEGORY_DOMAIN`
  edit. Never free-type a category into frontmatter; `verify` flags any
  `categories[0]` outside the fixed vocabulary (D-18).
- **D-17 The navigation tiers are fixed-but-extensible:** Domain
  (top, `CATEGORY_DOMAIN` value set), Category (middle, `CATEGORY_RULES`),
  Topic-phrase (leaf, free text, cosmetic). Numbering is append-order: a
  `0N-` prefix is assigned once and never renumbered.
- **D-18 Category vocabulary is enforced.** `verify` flags any
  `categories[0]` outside `CATEGORY_RULES`. `categories[0]` must also
  match the containing folder (I7 category/folder drift).
- **D-25 The Full Text fenced transcript is not exempt from D-12.**
- **R-15 Test vectors before implementation for core logic.** The
  `scripts/test_*.py` files are the standing vectors; run them after any
  change to categorization or indexing.

### Series (multi-part sources)

A lecture series, a course, or any multi-part source is tagged at add
time with `--series "..."`. The name round-trips as a `series:`
frontmatter field and three guarantees follow:

- **One folder per series.** The first entry files where the keyword
  guess puts it; every later `add` with the same series name inherits
  that category folder, overriding its own per-video guess.
  Episode-to-episode vocabulary drift is how earlier versions of this
  system scattered a series across folders.
- **The dashboard clusters.** Within a category table, series members
  list contiguously, anchored at the series' lowest NC id, with a Series
  column naming the group. Standalone entries keep plain id order.
- **`verify` enforces it.** A series whose members sit in more than one
  category folder is an invariant violation (exit 1), the same class as
  category/folder drift.

Pinned by the R-15 vectors in `scripts/test_series_clustering.py`.

## Categories and domains

The fixed vocabulary in `CATEGORY_RULES` (primary category determines the
folder):

| Category | Domain | Emoji |
|---|---|---|
| ai-ml | engineering | 🤖 |
| programming | engineering | 💻 |
| web-dev | engineering | 🌐 |
| science | engineering | 🔬 |
| tutorial | engineering | 📚 |
| networking | engineering | 📡 |
| tech | engineering | 📱 |
| talks-interviews | culture-society | 🎙️ |
| culture | culture-society | 🎭 |
| uncategorized | (none) | 📄 |

Domains: `engineering`, `culture-society` (the `it` domain was retired,
D-14). Keyword rules are scored by hit count, ties broken by list order,
first match wins.

## File format

Transcript entry frontmatter (YAML):

```yaml
id: "NC-0001"
title: "But what is a neural network?"
source_type: "youtube"
domain: "engineering"
url: "https://youtube.com/watch?v=..."
video_id: "aircAruvnKk"
channel: "3Blue1Brown"
date_added: "2026-06-24"
duration_sec: 1120
categories: ["ai-ml"]
topics: "neural network structure, MNIST"
series: "3b1b deep learning"
word_count: 3357
```

`topics:` and `series:` are optional; `series` marks a multi-part source
(see Series above).

Reference entry frontmatter adds a `kind:` field (`review`, `discussion`,
`probe`) and a `source_type` naming the artifact type (`hardware`, `model`,
`tool`, `video`, `paper`, `topic`):

```yaml
id: "NC-0043"
title: "Reticulum: protocol architecture review"
kind: "review"
source_type: "model"
date_added: "2026-08-26"
categories: ["networking"]
topics: "reticulum protocol architecture"
word_count: 812
```

## Navigation and indexing

Three tiers: Domain (top), Category (middle), Topic-phrase (leaf). Every
live Category gets a numbered subfolder with its own `00-Index.md` the
moment it has one entry.

- A **Domain index** (`0N-<domain>/00-Index.md`) links only to its
  Categories' index pages: one H2 section per Category with an emoji, a
  live entry count, and a one-line description. Never links directly to
  entries, so its size tracks Category count, not entry count. A Category
  with zero live entries stays listed as "No entries yet" with no link.
- A **Category index** (`0N-<domain>/0M-<category>/00-Index.md`) links
  directly to entries, id order, each with duration and, when present, its
  `topics:` phrase on an indented line. Footer back to Domain and
  dashboard.
- The **dashboard** (`000-dashboard/Index.md`, `rebuild`'s output) groups
  H2 per Domain, H3 per Category, alphabetical (the generated view has no
  folder-rename cost).
- **Labs** attach as a "## Labs" subsection on the owning Category's
  index. **References** get an inline link on the owning entry's line in
  its Category index.

Rules:

- `Index.md` is derived, never hand-edited, `rebuild` remakes it.
- Domain and Category indexes are hand-curated; `rebuild` never touches
  them. After adding an entry, add its wikilink by hand.
- Back links from domain pages: `[[../000-dashboard/Index|...]]` (one
  level up); from category pages: `[[../00-Index|...]]` and
  `[[../../000-dashboard/Index|...]]`.
- No emojis on index pages, no frontmatter tags, no blockquotes, clean
  bullet lists. Display names via `[[path|Name]]`, never raw filenames.
