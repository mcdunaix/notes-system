# Notes Catalog System

[![CI](https://github.com/mcdunaix/notes-system/actions/workflows/ci.yml/badge.svg)](https://github.com/mcdunaix/notes-system/actions/workflows/ci.yml)

Turn links into a library. You paste a YouTube link (or a PDF path, or an
Instagram/TikTok URL) and one command fetches the full transcript or text,
saves it as a Markdown note with a permanent ID, files it into a category
folder, and updates an index page. Over time that leaves you a searchable,
organized library of everything you have watched and read, instead of a
browser history.

Three parts ship in this repo:

1. **A pipeline** (`scripts/transcript.py`): fetch, categorize, file,
   index, and audit notes from the command line. Plain Python, no
   framework.
2. **A storage protocol** (`docs/STORAGE_PROTOCOL.md`): the rules that
   keep the library consistent as it grows, enforced by an automated
   `verify` command.
3. **Agent skills** (`skills/`): instruction files an AI agent (Hermes
   Agent, Claude Code, or similar) follows to turn raw transcripts into
   study material: structured lecture walkthroughs, hardware and tool
   reviews, hands-on lab guides, and fact-checks.

**The library ships empty.** No notes and no content folders are
committed. Clone it and the catalog starts from zero: your first `add`
creates the first category folder, `rebuild` creates the index. The value
is the tooling, not an archive of someone else's notes.

You do not need an AI agent to use the pipeline. The pipeline and the
`verify` audit run from a bare terminal. The skills are what an agent
uses on top, and any note-taking app that reads Markdown works;
[Obsidian](https://obsidian.md) is the best fit because the navigation
uses wikilinks.

## Layout

```
notes-system/
├── scripts/
│   ├── transcript.py       ingest + rebuild + list + verify (the pipeline)
│   ├── next-id.py          NC-XXXX id allocator (scans transcripts/ AND references/)
│   ├── catalog-transcribe.sh  transcript acquisition: captions, then whisper.cpp,
│   │                          then a remote mlx_whisper over ssh
│   ├── test_*.py           test vectors for the protocol rules
│   └── install-skills.sh   install skills/ into Hermes Agent
├── skills/                 agent skills that expand catalog entries
│   ├── content-catalog/         maintain the catalog, run the CLI
│   ├── lecture-walkthrough/     expand a lecture transcript into a structured walkthrough
│   ├── review-discussion-probe/ three modes: Review, Discussion, Probe
│   ├── lab-builder/             build hands-on lab guides
│   └── lecture-vetting/         fact-check a walkthrough's claims
├── docs/
│   ├── STORAGE_PROTOCOL.md      the storage rules and vocabulary
│   └── INGESTION_PIPELINE.md    how a link becomes a filed note
└── requirements.txt             fetch dependencies (`add` only; the rest is stdlib)
```

Content folders appear during use: `add` creates
`transcripts/<category>/`, `rebuild` creates `000-dashboard/Index.md`,
and reference notes, labs, and hand-curated index pages grow alongside
them (all defined in `docs/STORAGE_PROTOCOL.md`).

## Prerequisites

- **Python 3.10 or newer** (`python3 --version` to check; the scripts
  refuse older versions with a clear message).
- **pip packages for fetching content**, installed in step 3 below. Only
  `add` needs them; everything else runs on the standard library.
- **Optional: [Obsidian](https://obsidian.md)**, a free note-taking app.
  The catalog is plain Markdown, so any editor works, but the wikilink
  navigation is built for Obsidian.
- **Optional: an AI agent** (Hermes Agent, Claude Code, or any agent that
  reads a directory's `CLAUDE.md`). The pipeline works from a bare
  terminal; an agent is what runs the skills for you.

## Quick start

```bash
# 1. Clone anywhere. The repo root IS the catalog root.
git clone https://github.com/mcdunaix/notes-system.git && cd notes-system

# 2. Set the catalog root for the skills (or export it once in your shell).
export CATALOG_ROOT="$(pwd)"

# 3. Install the fetch dependencies (needed by `add` only).
python3 -m pip install -r requirements.txt

# 4. Sanity-check the empty catalog (stdlib only).
python3 scripts/transcript.py verify
python3 scripts/transcript.py rebuild
python3 scripts/next-id.py            # prints NC-0001

# 5. Add your first piece of content.
python3 scripts/transcript.py add "https://youtube.com/watch?v=..." --topics "topic phrase"

# 6. Open the folder in Obsidian. 000-dashboard/Index.md is the landing page.

# 7. Optional: install the skills into Hermes Agent.
./scripts/install-skills.sh           # symlinks skills/ into ~/.hermes/skills/productivity/
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

Two flags matter on every `add`:

- `--topics "..."` names the file. The filename slug comes from your
  topic phrase, not the video's title, so
  `NC-0001_neural-network-basics.md` stays findable even when the source
  title is clickbait.
- `--series "..."` clusters multi-part sources. Give every part of a
  lecture series or course the same series name and three things are
  guaranteed: all parts file into the same category folder (later parts
  inherit the first part's category instead of trusting their own
  keyword guess), the dashboard lists the parts together as one block,
  and `verify` fails loudly if a series ever ends up split across
  folders. Without it, part 3 of a series can keyword-drift into a
  different folder than parts 1 and 2.

```bash
python3 scripts/transcript.py add "https://youtube.com/watch?v=<chapter-2>" \
    --topics "gradient descent" --series "3b1b deep learning"
```

## How the library organizes itself

Every note is a Markdown file with YAML frontmatter, filed as
`transcripts/<category>/NC-XXXX_<topic-slug>.md`:

- **IDs are permanent.** `NC-0042` never changes and is never reused,
  so any other note can cite it forever. `scripts/next-id.py` allocates
  the next free number.
- **Categories are a fixed list** (ai-ml, programming, networking,
  science, culture, and so on), grouped into domains (engineering,
  culture-society). `add` guesses by keyword scoring; you or your agent
  correct it when the guess is wrong.
- **Series cluster.** Multi-part sources tagged with `--series` stay in
  one folder and list together on the dashboard.
- **Files are the truth.** The dashboard index is generated FROM the
  files by `rebuild`, never the other way around. Edit or delete notes
  freely, then rebuild.
- **`verify` audits everything**: missing or duplicate IDs, notes filed
  in the wrong folder, broken transcript blocks, split series, and
  banned punctuation. It exits non-zero on any violation, so it works
  as a git hook or CI gate too.

The full rule set, including the file format and the navigation
structure, is `docs/STORAGE_PROTOCOL.md`. Rules there carry stable codes
(D-12, D-13, R-15, ...) so notes, skills, and commit messages can cite a
rule by ID instead of restating it; the codes are defined in that
document.

## The skills

Skills are Markdown instruction files (`SKILL.md`) that tell an AI agent
exactly how to do a job with this catalog. Point any capable agent at
one, or install them into Hermes Agent so they load on demand.

| Skill | Job |
|---|---|
| `content-catalog` | The day-to-day maintainer: run the CLI, dedupe, categorize, index. |
| `lecture-walkthrough` | Turn a lecture or video into a structured walkthrough with references and full text preserved. |
| `review-discussion-probe` | Three analysis modes: **Review** a piece of hardware, an LLM/model, or a tool (research, breakdown, verdict, logged note); **Discussion** tees up a guided in-depth discussion of a video or artifact; **Probe** researches a topic and presents its cutting edge, future development, and related tech. |
| `lab-builder` | Build hands-on lab guides through four gated phases. |
| `lecture-vetting` | Fact-check the narrative-load-bearing claims of a cataloged walkthrough. |

Skills use `$CATALOG_ROOT` for every path (see each skill's Catalog root
note); nothing hardcodes any particular machine.

## Using it with an agent

Hermes Agent is an agent harness: it runs an AI agent on your machine,
auto-loads per-directory instructions, and executes packaged skills
(`SKILL.md` files) on demand. This repo is shaped for it, and
works the same with Claude Code or any agent that reads a `CLAUDE.md` or
`AGENTS.md` file in its working directory:

- **Orientation is automatic.** An agent session started in this repo
  loads `CLAUDE.md` (conventions and commands) and resumes from
  `SESSION_STATE.md`.
- **Skills install once.** `./scripts/install-skills.sh` symlinks all
  five skills into `~/.hermes/skills/productivity/` (`--copy` for a
  hermetic install).
- **The core stays agent-agnostic.** `transcript.py` and `next-id.py`
  are plain stdlib Python with no agent dependency, so a bare terminal
  drives them fine.
- **Mobile capture is possible but optional.** The `content-catalog`
  skill documents a capture path where a personal Telegram bot feeds
  links and videos from your phone into the pipeline via the Hermes
  gateway, with local speech-to-text for videos without captions. It
  requires creating your own bot; nothing else depends on it.

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
  the file and the broken rule (lost `id:` line, category/folder
  mismatch, broken `## Full Text` fence, a split series, or a banned
  dash). Fix the named line and rerun until it exits 0.

## License

MIT. See LICENSE for the full text.
