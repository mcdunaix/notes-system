# Storage Protocol

The rules that keep the catalog consistent. This repo was factored out of
the author's vault, where each rule was pinned as a numbered decision
(D-#). The ids are kept here as vocabulary so the skills can cite them;
the decision history itself is not shipped.

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
  violations. Exits non-zero on violations.
- **I8 rebuild/list/verify run on stdlib alone.** `yt_dlp`,
  `youtube_transcript_api`, and `fitz` import lazily inside the fetch
  paths that need them.

## Entry kinds and where they live

| Kind | Directory | Carries | Gate |
|---|---|---|---|
| Transcript entry (video, social, PDF) | `transcripts/<category>/` | Raw text under `## Full Text` (fenced) | `transcript.py verify` (automated) |
| Reference entry (Review, Probe, artifact Discussion, research notes) | `references/` | Analysis, no raw transcript | Manual D-12 grep (verify does not scan references/) |

Both kinds share the NC-XXXX numbering. `verify`'s blind spot on
`references/` is a known, documented gap (I7 scans transcripts only);
`scripts/next-id.py --check` covers the whole catalog.

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
word_count: 3357
```

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
