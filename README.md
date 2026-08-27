# Notes Catalog System

A personal knowledge catalog with a pipeline, not a vault full of someone
else's notes. This repo ships the **tooling and the protocol** for a
transcript and research catalog with persistent NC-XXXX IDs: an ingestion
script, a storage protocol with an automated integrity audit, hand-curated
Obsidian-native navigation, and the agent skills that expand raw material
into structured notes.

**The database is empty.** No personal notes are included. Clone it, open it
in Obsidian, and the catalog starts from zero. This is the point: the value
is in the pipeline, the protocol, and the skills, not in the archive.

This repo was factored out of the author's personal vault
(`~/Documents/notes`), which remains private. The skills and scripts are
kept here in a cleaned, path-parameterized form; the protocol decisions
cited throughout (D-8, D-12, D-13, D-17, ...) are documented in
`docs/STORAGE_PROTOCOL.md`.

## Layout

```
notes-system/
├── 000-dashboard/          landing page (Index.md is derived, rebuilt by transcript.py)
├── 01-engineering/         domain: AI, programming, networking (hand-curated indexes)
├── 02-culture-society/     domain: talks, interviews, culture (hand-curated indexes)
├── transcripts/            canonical entry storage (files are truth), empty
├── references/             non-transcript notes: reviews, probes, discussions, empty
├── labs/                   hands-on lab ladders, empty
├── briefs/                 delegation briefs, empty
├── scripts/
│   ├── transcript.py       ingest + rebuild + list + verify (the pipeline)
│   ├── next-id.py          NC-XXXX allocator scanning transcripts/ AND references/
│   └── test_*.py           protocol test vectors (R-15)
├── skills/                 agent skills that expand catalog entries
│   ├── content-catalog/         maintain the catalog, run the CLI
│   ├── lecture-walkthrough/     expand a lecture transcript into a structured walkthrough
│   ├── review-discussion-probe/ three modes: Review, Discussion, Probe (new)
│   ├── lab-builder/             build hands-on lab guides from research
│   └── lecture-vetting/         fact-check a walkthrough's claims
└── docs/
    ├── STORAGE_PROTOCOL.md      the invariants and conventions
    └── INGESTION_PIPELINE.md    the ingest-to-file routine map
```

## Quick start

```bash
# 1. Clone anywhere. The repo root IS the catalog root.
git clone <this-repo> && cd notes-system

# 2. Set the catalog root for the skills (or export it once in your shell).
export CATALOG_ROOT="$(pwd)"

# 3. Sanity-check the empty database (stdlib only).
python3 scripts/transcript.py verify
python3 scripts/transcript.py rebuild
python3 scripts/next-id.py            # prints NC-0001

# 4. Open the folder in Obsidian. 000-dashboard/Index.md is the landing page.

# 5. Install the skills into Hermes (or copy them yourself).
./scripts/install-skills.sh           # symlinks skills/ into ~/.hermes/skills/productivity/

# 6. Add your first piece of content.
python3 scripts/transcript.py add "https://youtube.com/watch?v=..." --topics "topic phrase"
```

`add` needs `yt_dlp`, `youtube_transcript_api`, and `pymupdf`;
`rebuild` / `list` / `verify` / `next-id.py` are stdlib-only.

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

This repo is shaped for Hermes Agent (and works with any agent that reads
`CLAUDE.md` or `AGENTS.md` in the directory it operates in):

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
- `verify` audits storage invariants after any external edit. Run it.
- Domain and category indexes are hand-curated and are the primary Obsidian
  navigation; `rebuild` only regenerates the dashboard.

Full detail: `docs/STORAGE_PROTOCOL.md`.

## License

MIT. See LICENSE for the full text. The scripts and skills are original work.
