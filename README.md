# Notes Catalog System

[![CI](https://github.com/mcdunaix/notes-system/actions/workflows/ci.yml/badge.svg)](https://github.com/mcdunaix/notes-system/actions/workflows/ci.yml)

A personal knowledge catalog with a pipeline, not a vault full of someone
else's notes. This repo ships the **tooling and the protocol** for a
transcript and research catalog with persistent NC-XXXX IDs: an ingestion
script, a storage protocol with an automated integrity audit, hand-curated
Obsidian-native navigation, and the agent skills that expand raw material
into structured notes.

In practice: you paste a YouTube link (or a PDF path, or an Instagram/
TikTok URL), and the tool saves the full text as a Markdown note with a
permanent ID, sorts it into a category, and keeps an index page current.
Agent skills then turn those raw notes into study material: structured
walkthroughs of lectures, reviews of tools and hardware, hands-on lab
guides, and fact-checks. If you learn from videos and want those hours to
leave a searchable, growing library behind, that is the job this does.

**The database ships empty and folder-less.** No personal notes are included
and no content folders are committed. Clone it, open it in Obsidian, and the
catalog starts from zero. The first `add` creates `transcripts/<category>/`;
`rebuild` creates `000-dashboard/Index.md`. This is the point: the value is
in the pipeline, the protocol, and the skills, not in the archive.

This repo was factored out of the author's personal vault
(`~/Documents/notes`), which remains private. The skills and scripts are
kept here in a cleaned, path-parameterized form; the protocol decisions
cited throughout (D-8, D-12, D-13, D-17, ...) are documented in
`docs/STORAGE_PROTOCOL.md`.

## Layout

```
notes-system/
├── scripts/
│   ├── transcript.py       ingest + rebuild + list + verify (the pipeline)
│   ├── next-id.py          NC-XXXX allocator scanning transcripts/ AND references/
│   └── test_*.py           protocol test vectors (R-15)
├── skills/                 agent skills that expand catalog entries
│   ├── content-catalog/         maintain the catalog, run the CLI
│   ├── lecture-walkthrough/     expand a lecture transcript into a structured walkthrough
│   ├── review-discussion-probe/ three modes: Review, Discussion, Probe
│   ├── lab-builder/             build hands-on lab guides from research
│   └── lecture-vetting/         fact-check a walkthrough's claims
├── docs/
│   ├── STORAGE_PROTOCOL.md      the invariants, conventions, and vocabulary
│   └── INGESTION_PIPELINE.md    the ingest-to-file routine map
└── requirements.txt             fetch dependencies (`add` only; the rest is stdlib)
```

No content folders ship. During use the catalog grows:
`add` creates `transcripts/<category>/`, `rebuild` creates
`000-dashboard/Index.md`, and the agent maintains the hand-curated domain
and category `00-Index.md` files (see `docs/STORAGE_PROTOCOL.md`).

## Prerequisites

- **Python 3.10 or newer** (`python3 --version` to check; the scripts
  refuse older versions with a clear message).
- **pip packages for fetching content**, installed in step 3 below. Only
  `add` needs them; everything else runs on the standard library.
- **Optional: [Obsidian](https://obsidian.md)**, a free note-taking app.
  The catalog is plain Markdown, so any editor works, but the wikilink
  navigation is built for Obsidian.
- **Optional: Hermes Agent** (or Claude Code, or any agent that reads a
  directory's `CLAUDE.md`). The pipeline works from a bare terminal; an
  agent is what runs the skills for you.

## Quick start

```bash
# 1. Clone anywhere. The repo root IS the catalog root.
git clone https://github.com/mcdunaix/notes-system.git && cd notes-system

# 2. Set the catalog root for the skills (or export it once in your shell).
export CATALOG_ROOT="$(pwd)"

# 3. Install the fetch dependencies (needed by `add` only).
python3 -m pip install -r requirements.txt

# 4. Sanity-check the empty database (stdlib only).
python3 scripts/transcript.py verify
python3 scripts/transcript.py rebuild
python3 scripts/next-id.py            # prints NC-0001

# 5. Open the folder in Obsidian. Once entries exist and you have run
#    `rebuild`, 000-dashboard/Index.md is the landing page.

# 6. Install the skills into Hermes (or copy them yourself).
./scripts/install-skills.sh           # symlinks skills/ into ~/.hermes/skills/productivity/

# 7. Add your first piece of content.
python3 scripts/transcript.py add "https://youtube.com/watch?v=..." --topics "topic phrase"
```

## Your first entry, what actually happens

```
$ python3 scripts/transcript.py add "https://www.youtube.com/watch?v=aircAruvnKk" \
      --topics "neural network basics"
Fetching transcript for video ID: aircAruvnKk
  Title: But what is a neural network? | Deep learning chapter 1
  Channel: 3Blue1Brown
  Categories: ai-ml, science, programming
  ID: NC-0001
  Saved: transcripts/ai-ml/NC-0001_neural-network-basics.md
Index rebuilt at 000-dashboard/Index.md
  1 entries (1 youtube) in 1 domains, 1 categories
```

One command did the whole mechanical pass: fetched the metadata and the
full transcript, guessed a category from keyword scoring, assigned the
next free ID, saved a Markdown note (frontmatter + summary header + the
raw transcript in a fenced block), and regenerated the dashboard. The
judgment calls (is the category right, what should the note become) are
yours, or your agent's: that is what the skills are for.

## The skills

| Skill | Job |
|---|---|
| `content-catalog` | The day-to-day maintainer: run the CLI, dedupe, categorize, index. |
| `lecture-walkthrough` | Turn a lecture or video into a structured walkthrough with references and full text preserved. |
| `review-discussion-probe` | Three analysis modes: **Review** a piece of hardware, an LLM/model, or a tool (research, breakdown, verdict, logged note); **Discussion** tees up a guided in-depth discussion of a video or artifact; **Probe** researches a topic and presents its cutting edge, future development, and related tech. |
| `lab-builder` | Build hands-on lab guides through four gated phases. |
| `lecture-vetting` | Fact-check the narrative-load-bearing claims of a cataloged walkthrough. |

Skills use `$CATALOG_ROOT` for every path (see each skill's Catalog root
note); nothing hardcodes the author's machine.

## Built for Hermes Agent

Hermes Agent is an agent harness: it runs an AI agent on your machine,
auto-loads per-directory instructions, and executes packaged skills
(`SKILL.md` files) on demand. This repo is shaped for it, and works with
any agent that reads `CLAUDE.md` or `AGENTS.md` in the directory it
operates in (Claude Code included):

- **Session on-ramp.** A Hermes session started in this repo auto-loads
  `CLAUDE.md` (orientation, conventions, commands) and can resume from
  `SESSION_STATE.md` "Resume here", the same convention the author's vault
  uses.
- **Skills.** All five skills are Hermes-format skills (SKILL.md with YAML
  frontmatter), installed with `./scripts/install-skills.sh` into
  `~/.hermes/skills/productivity/` (symlink by default, `--copy` for a
  hermetic install). They load on demand or with `hermes -s <skill>`.
- **Agent-agnostic core.** The pipeline itself (`transcript.py`,
  `next-id.py`) is deliberately plain stdlib Python with no Hermes
  dependency, so any agent or a bare terminal can drive it. Hermes is the
  layer that reads the skills and runs the capture path.
- **Capture path.** The author's setup captures links and video via the
  Hermes gateway (Telegram bot, `catalog-add-from-video.py` with
  mlx-whisper); `content-catalog` documents that pipeline for the same
  setup. It is optional, not required.

## Protocol in one breath

- Files are truth. `Index.md` and `list` are derived views, regenerable with
  `rebuild`.
- Every entry gets a permanent, unique `NC-XXXX` id. Allocate with
  `scripts/next-id.py`, never by hand.
- The filename slug names the topic, never the source title (D-13).
- No em dashes, ever (D-12): a comma, a colon, or two sentences.
- `transcripts/<category>/` holds transcript entries (they carry the raw
  text under `## Full Text`); `references/` holds research and artifact
  notes with the same NC numbering.
- `verify` audits storage invariants across both `transcripts/` and
  `references/` after any external edit. Run it.
- Domain and category indexes are hand-curated and are the primary Obsidian
  navigation; `rebuild` only regenerates the dashboard.

Full detail: `docs/STORAGE_PROTOCOL.md`, including a vocabulary section
that defines the shorthand the skills use (NC id, entry, walkthrough,
D-#, R-15, vault, gateway).

## Troubleshooting

- **`ModuleNotFoundError` or an install prompt when running `add`**: the
  fetch dependencies are missing. `python3 -m pip install -r
  requirements.txt`. Everything except `add` runs without them.
- **"transcript.py needs Python 3.10 or newer"**: your `python3` is too
  old. Install a current version from python.org and retry.
- **"Transcript not available" on a YouTube video**: the video has no
  captions in any language (or captions are disabled). There is nothing
  to fetch; the fallback is downloading the audio and transcribing it
  locally, which the `content-catalog` skill documents.
- **Instagram/TikTok add returns no content**: those platforms usually
  require logged-in browser cookies. The tool tries your Chrome cookies
  first. `skills/content-catalog/references/instagram-cookies.md` covers
  the details and the caveats; treat that whole path as optional.
- **`rebuild` says "No transcripts found."**: normal on an empty catalog.
  The dashboard appears after your first `add`.
- **`verify` fails after you edited an entry by hand**: the output names
  the file and the broken invariant (lost `id:` line, category/folder
  mismatch, broken `## Full Text` fence, or a banned dash). Fix the named
  line and rerun until it exits 0.

## License

MIT. See LICENSE for the full text. The scripts and skills are original work.
