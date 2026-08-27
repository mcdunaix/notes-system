---
name: content-catalog
description: "Maintain a content catalog at $CATALOG_ROOT/, video transcripts (YouTube, Instagram), PDF text extracts with persistent NC-XXXX IDs, auto-categorization, and auto-generated INDEX.md. Optional extras: local speech-to-text (mlx-whisper, Apple Silicon only) and a Telegram capture bot for mobile link capture."
version: 4.4.0
tags: [catalog, youtube, transcripts, pdf, indexing, instagram, whisper, telegram]
---

# Content Catalog

Catalog lives at `$CATALOG_ROOT/` (the catalog root, i.e. the directory
containing `scripts/transcript.py`; this repo root when the repo is used as
the vault). Set `export CATALOG_ROOT=/path/to/catalog` before running commands.
CLI tool: `scripts/transcript.py`

## Supported source types

| Type | Flag | What gets extracted |
|---|---|---|
| YouTube | (auto-detect) | Full spoken-word transcript via youtube-transcript-api + metadata via yt-dlp |
| Instagram Reel | (auto-detect) | Description text (auto) or full speech-to-text transcript (manual pipeline) |
| TikTok / other short video | (auto-detect) | **Not supported from server** - IP-blocked. Workaround: download the video on your phone and send the MP4 file to your capture bot as an attachment |
| Local video file | (manual pipeline; transcript.py has no local-file flag) | Full speech-to-text via mlx-whisper, Apple Silicon only (see `<skill_dir>/scripts/catalog-add-from-video.py`) |
| PDF | `--pdf <path>` | Full text via pymupdf + page count + file path |

## CLI commands

```bash
cd "$CATALOG_ROOT"

# YouTube video (auto-detected)
python3 scripts/transcript.py add "https://youtube.com/watch?v=..." --topics "topic phrase"

# Instagram Reel (auto-detected)
python3 scripts/transcript.py add "https://instagram.com/reel/..." --topics "topic phrase"

# PDF
python3 scripts/transcript.py add --pdf "path/to/document.pdf" --topics "topic phrase"

# One part of a multi-part source (lecture series, course)
python3 scripts/transcript.py add "https://youtube.com/watch?v=..." \
    --topics "topic phrase" --series "series name"

# List / rebuild
python3 scripts/transcript.py list
python3 scripts/transcript.py rebuild
```

Always pass `--topics "..."`: the filename slug names the topic, not the
title (D-13).

When the source is one part of a series, always pass the same
`--series "..."` name for every part. The series decides the folder
(later parts inherit the first part's category, whatever their own
keyword guess says), the dashboard lists the parts contiguously, and
`verify` fails if a series ever splits across category folders. Without
the flag, per-video keyword drift can scatter a series.

## Telegram video → catalog pipeline

This capture path is OPTIONAL. It requires setting up your own Telegram bot
with the Hermes gateway (see `references/telegram-gateway.md`); everything in
the catalog works without it, paste links or file paths into `add` directly.

When the user sends a video via Telegram:
1. Find cached video: `~/.hermes/cache/videos/video_*.mp4`
2. Extract metadata via `yt-dlp --print` with TikTok/URL if user provides source
3. Extract audio: `ffmpeg -i <video> -vn -acodec pcm_s16le -ar 16000 -ac 1 <audio>.wav`
4. Transcribe with `mlx_whisper.transcribe()` (mlx-community/whisper-tiny model, Apple Silicon only)
5. Save markdown entry with YAML frontmatter to `transcripts/<category>/NC-XXXX_<slug>.md`
6. Rebuild index: `python3 scripts/transcript.py rebuild`
7. Cache WAV can be cleaned up after (video may be kept for reference)

### Prompt user: repackage or transcript?

After extracting a transcript, ASK the user whether they want:
- **"Repackage"** → Generate reference docs (comparison tables, architecture diagram, glossary, key quotes) and append the repackaged section below the raw transcript in the markdown file. Also add the prompt line at the bottom: `**💬 Prompt:** Say **"repackage"** to get reference docs + architecture diagram, or **"transcript"** to see just the raw text.`
- **"Transcript"** → Just show the raw text, no repackaging

Add the prompt line at the end of every transcript markdown file so the user can request repackaging later too.

**Note on folder naming:** Domain folders use short, obvious names with number
prefixes. Utility folders (`scripts/`, `references/`) have no prefix. Transcripts
are organized by content category, not source type, e.g., `culture/` not
`talks-interviews/`, `ai-ml/` not `youtube/`.

## When user drops a link in chat, FIRST TOOL TO REACH FOR

**Do NOT manually download subtitles or write cleanup scripts.** The catalog
already has a CLI tool that handles metadata, transcription, categorization,
ID assignment, and index rebuilding in one call.

1. Run `scripts/transcript.py add "<url>" --topics "..."` or `--pdf <path> --topics "..."` in the catalog root (D-13: the slug names the topic)
2. If YouTube and the script fails (transcript disabled, age-restricted), fall back to
   `references/yt-dlp-vtt-fallback.md`
3. If Instagram and yt-dlp is rate-limited, fall back to description-only entry (see pitfall)
4. Show the resulting ID (NC-XXXX) and category
5. Paste any relevant snippet if asked

**Post-processing for lectures/courses**: The script doesn't set `course` or
`instructor` fields. For university lectures, manually add these to the
frontmatter and body text after the script runs. Use `yt-dlp --print description
"<url>"` to get the course number and instructor name.

**Post-processing: course-series integration**: When the new entry belongs to
an existing course series (e.g., MIT 6.034, identified by checking whether a
course landing page exists at `01-engineering/01-ai/`), a full integration pass
is required:

1. **Fix category**, MIT OCW lectures commonly get miscategorized as `science`
   (the title may lack ai-ml keywords like "neural network"). Check previous
   entries in the series and match their categories and frontmatter fields
   (course, instructor, categories list).
2. **File location**, Verify the file landed in the correct transcripts/
   subdirectory. If wrong, move it with `mv` to the right dir (e.g., from
   `transcripts/science/` to `transcripts/ai-ml/`). Delete any now-empty
   leaf directory.
3. **Add to course landing page**, Insert a wikilink on the course's landing
   page (`01-engineering/01-ai/01-MIT-6.034.md` or similar) in correct
   numerical order between the existing entries.
4. **Add navigation links**, At the bottom of the transcript file (after the
   closing ```), add:
   ```markdown
   ---

   Up: [[../../01-engineering/01-ai/CourseFile|Course Name Index]]
   Previous: [[../category/prev-file|Lecture N: Previous Title]]
   Next: [[../category/next-file|Lecture N: Next Title]]
   ```
   First entry omits Previous; last entry omits Next.
5. **Update adjacent entries**, Add a `Next: ...` link to the previous
   lecture in the series if it doesn't have one. Add a `Previous: ...` link
   to the next lecture.
6. **Rebuild index**, Run `python3 scripts/transcript.py rebuild` after all
   file operations complete.

**Post-processing: structured walkthrough for didactic lectures**: The
script generates an intro paragraph that is a raw excerpt of the transcript
opening. For lecture-style content with a clear pedagogical structure
(problem → concepts → worked example → results → punchline), this is
redundant with the full transcript below `## Full Text`. Replace the
paragraph between the metadata `---` and `## Full Text` with a structured
walkthrough that captures the lecture's logical flow:

- State the specific problem/equation being solved
- Explain the core idea and name it
- List the concepts/taxonomies introduced (e.g., safe vs. heuristic transforms)
- Walk through the step-by-step worked example with intermediate expressions
- Include results/metrics tables
- Capture the punchline/conclusion

**LaTeX format**: All equations must be in inline $\LaTeX$ or
$\displaystyle$ block math. Plain-text Unicode math (∫ x² dx, sin/cos in
plain text, Unicode superscripts) renders poorly on GitHub and other
Markdown renderers. Use proper LaTeX: `\int`, `\sin`, `\cos`, `\frac`,
`\rightarrow`, etc.

**Preserve key lecture moments**: The walkthrough should not be purely
technical. Lectures often contain rich philosophical content, the
speaker's framing of why a concept matters, educational philosophy
asides, historical backstories (e.g., James Slagle's near-blindness and
antique computer), and anecdotal punchlines. These are the parts that
make the lecture memorable. Include them as blockquote sections
interleaved with the technical content.

**Numbering**: When significant conceptual material (educational philosophy,
historical context) fits naturally between the knowledge section and the
architecture section, use subordinate numbering like 4a/4b/4c rather than
renumbering all subsequent sections.

See `references/lecture-walkthrough-example.md` for a worked example
(Patrick Winston's Goal Trees lecture).

## Vault structure

See `references/vault-organization.md` for the full conventions reference with
path examples for every depth level.

This is the layout a live catalog grows into. The repo ships empty: `add`
creates `transcripts/<category>/` and `rebuild` creates `000-dashboard/Index.md`
on first use, and domain folders are created by hand as entries accumulate.

**File explorer ordering:** Use double-zero number prefixes to enforce intentional order:
```
000-dashboard/        ← entry point (Index.md is the landing page)
01-engineering/       ← AI, ML, NN, programming, networking
02-culture-society/   ← talks, interviews, cultural commentary
references/
scripts/              ← utility scripts (no underscore - underscore sorts before numbers)
transcripts/          ← raw transcript files by topic
```
Domains are the fixed set in `CATEGORY_DOMAIN` (engineering, culture-society);
new domains get the next number and are added deliberately (D-14 pattern), never
free-typed. Utility folders (`scripts/`, `references/`) have no prefix and sort
after numbered folders.

**Golden rules for vault root:**
- Each broad domain gets its own folder at root with a leading number (01-, 02-, ...).
- `000-dashboard/Index.md` is the landing page. In Obsidian it can open automatically on startup via `.obsidian/workspace.json`.
- No loose files in root. Only folders with clear, obvious names.
- A newcomer sees the file explorer panel with folders in numbered priority order and instantly knows where to start.

**Domain folder naming:**
- `01-engineering/` - AI, ML, NN, programming, networking (all fall under engineering)
- `02-culture-society/` - talks, interviews, cultural commentary, societal analysis
- New broad domains get their own folder at root level with next available number

**Domain-internal Index.md format:**
Each domain has an Index.md that lists everything in that domain. No emojis,
no frontmatter tags, no blockquotes. Clean bullet lists with bold headings
for sub-domains when needed.

```markdown
# Engineering

## AI

- [[01-ai/01-MIT-6.034|MIT 6.034]] - 5 lectures
- [[01-ai/02-3Blue1Brown|3Blue1Brown - Neural Networks]] - 2 videos
- [[../../transcripts/ai-ml/...|Introduction to Machine Learning]] - PDF

## Programming

- [[../../transcripts/programming/...|Python Tutorial 2026]] - 5:21

[[../000-dashboard/Index|← Home]]
```

Back links from within domain folders always point to `../000-dashboard/Index`.
From two levels deep (e.g., `01-engineering/01-ai/`): `[[../../000-dashboard/Index|← Home]]`.

**Root Index.md (vault entry point):**
Located at `000-dashboard/Index.md`. Lists every entry grouped by broad domain.
Clean bullet lists, no emojis, no frontmatter tags, no blockquotes. Bold
section headers for each domain.

```markdown
# Notes

**Engineering**

- [[../01-engineering/01-ai/01-MIT-6.034|MIT 6.034]] - 5 lectures
- [[../01-engineering/01-ai/02-3Blue1Brown|3Blue1Brown - Neural Networks]] - 2 videos
- [[../transcripts/ai-ml/...|Introduction to Machine Learning]] - PDF
- [[../01-engineering/02-programming/00-Index|Programming]] - 1 tutorial
- [[../transcripts/tech/...|Twingate Home Lab]] - 1:26

**Culture and Society**

- [[../transcripts/talks-interviews/...|Title]] - description
```

(Entry names like "Twingate Home Lab" are illustrative; the repo ships with
an empty database.)

Rules:
- Every entry in the vault is listed, not just courses.
- No emojis, no frontmatter tags, no blockquotes, no HTML cards.
- Each line: `- [[relative/path|Display Name]]` with a description after ` - `.
- Links from `000-dashboard/Index.md` use `../` prefix (one level up to root, then into target folder).

## INDEX.md format (pruned, preferred)

Group entries by series with simple bullet lists. No table, no columns.

```
# All Entries

## Course Name

- NC-XXXX - [[transcripts/...|Lecture Title]]
- NC-XXXX - [[transcripts/...|Lecture Title]]

## Standalone

- NC-XXXX - [[transcripts/...|Title]] (type)
```

Standalone entries (no series) go under a Standalone heading.
The `scripts/transcript.py rebuild` command does NOT generate this format:
INDEX.md is manually curated for readability.

## INDEX.md format (auto-generated, legacy for CLI)

The transcript.py rebuild script generates this table form (kept for
backward compatibility, but the pruned bullet-list form above is preferred
for Obsidian):

This format is generated by `scripts/transcript.py rebuild` for CLI
compatibility. For the preferred Obsidian-native format (pruned bullet
lists), see the section above. Key differences:
- No Date, Duration, or Source columns (implied by entry context)
- No Series column (entries are grouped under series headings)
- Standalone entries under a "Standalone" heading instead of `-`

## Course / Series organization

When the catalog accumulates multiple entries from the same course or video
series (e.g., MIT 6.034 lectures, 3Blue1Brown playlist), organize them with
three layers:

Note: Obsidian itself is optional. The catalog is plain Markdown and readable
in any editor; `[[wikilink]]` navigation and Dataview are Obsidian features.

**Golden rule: Everything must be Obsidian-native markdown.**
Do NOT create .html files, dashboards, or any non-markdown presentation
layer. Navigation must render natively in Obsidian using `[[wikilinks]]`
and plain markdown lists. A separate HTML file is a maintenance burden
that drifts from the source and loses Obsidian formatting.

**Preferred approach: plain wikilinks, no plugins.**
Course landing pages use a static markdown list of `[[wikilinks]]` with
display text, no Dataview queries, no dynamic tables. This avoids plugin
dependencies, renders instantly, and can't break.

### 1. Course landing page at `01-engineering/01-ai/Name.md`

A minimal markdown page with just a heading and a bullet list of wikilinks.
File name uses a clean descriptive name (`MIT-6.034.md`, `3Blue1Brown.md`).

```markdown
# Course Title

- [[transcripts/<category>/<slug>|1. Lecture Title]]
- [[transcripts/<category>/<slug>|2. Lecture Title]]
- [[transcripts/<category>/<slug>|3. Lecture Title]]

---

[[../000-dashboard/Index|← Back to Home]]
```

Rules:
- **No Dataview syntax. Just plain `[[wikilinks]]`.** Static can't break, requires no plugins, renders instantly.
- Each line is `[[path/to/file|Display Name]]` where the display name is the lecture title. The ugly filename is never shown.
- No metadata columns (date, duration, source). Just the lecture names.
- The back link goes to `000-dashboard/Index` from any depth.
  - From `01-engineering/`: `[[../000-dashboard/Index|← Home]]`
  - From `01-engineering/01-ai/`: `[[../../000-dashboard/Index|← Back to Home]]`

### 2. Cross-links at the bottom of each transcript (Obsidian wikilinks)

After the closing ``` of the raw transcript text, add navigation links using
`[[wikilinks]]` (not markdown `[]()` links) so Obsidian's backlinks and graph
view work:

```markdown
---

Up: [[../../01-engineering/01-ai/01-MIT-6.034|MIT 6.034 Course Index]]
Previous: [[../<category>/<slug>|Lecture N: Title]]
Next: [[../<category>/<slug>|Lecture N: Title]]
```

Rules:
- First entry omits Previous; last entry omits Next.
- The `Up` link goes to the course landing page. From `transcripts/<category>/`,
  the relative path depends on the domain folder:
  - AI content: `../../01-engineering/01-ai/FileName`
  - Other domains: `../../0N-domain/Index`
- Lecture names should match what the course uses (e.g., "Lecture 4:
  Search, Depth-First, Hill Climbing, Beam").
- Use `[[../category/filename|Display]]` format - the pipe is the Obsidian
  alias syntax. Filenames omit the `.md` extension.

### 3. Series frontmatter + INDEX

- Each transcript file's YAML frontmatter gets `series: "Course Name"`
  (shorthand label for grouping).
- For numbered courses, also add `lecture: N` (integer) to the frontmatter
  for ordering. For playlists, use `chapter: N`.
- INDEX.md groups entries by series with simple bullet lists (no table).

### When to apply this pattern

After adding the 2nd+ entry from the same course/series, or when the user
explicitly asks for course organization. Don't create a landing page for a
single-entry series.

### 4. Vault entry point: `000-dashboard/Index.md`

The vault needs one obvious front door: `000-dashboard/Index.md`, listing
every entry grouped by broad domain. Format and rules: see "Root Index.md
(vault entry point)" under "## Vault structure" above.

**Set as startup page (Obsidian):** Edit `.obsidian/workspace.json` (created by
Obsidian on first launch of the vault; the repo does not ship it) to open
`000-dashboard/Index.md` by default. Set the main leaf's `state.state.file`
value to `000-dashboard/Index.md`.

### 5. INDEX.md format (pruned)

See "## INDEX.md format (pruned, preferred)" above for the canonical format.

### Dataview plugin (user must opt in, NOT the default)

**The default approach is plain `[[wikilinks]]` - no plugins, no dynamic queries.**
This is the preferred approach because it can't break, requires no setup, and renders instantly.

Dataview is ONLY used when the user explicitly requests auto-updating tables.
If Dataview is opted into, it's installed at `.obsidian/plugins/dataview/`. Use
`TABLE WITHOUT ID link(file.path, title)` with `SORT lecture ASC` to show clean
clickable titles (not filenames).

```dataview
TABLE WITHOUT ID link(file.path, title) AS " "
FROM "transcripts/<category>"
WHERE series = "Course Name"
SORT lecture ASC
```

**Known pain points (reason plain wikilinks are preferred):**
- Tables show too much info (dates, raw seconds, source columns are noise)
- `LIST title` shows ugly `filename: title` format - `TABLE WITHOUT ID link(file.path, title)` is the workaround but creates a single-column table
- Raw filenames (`NC-0008_goal-trees-problem-solving`) are ugly link text
- Sorts alphabetically unless you add dedicated frontmatter fields (`lecture:`, `chapter:`)
- Plugin can break on Obsidian updates; adds load time

### UX design principles (the catalog's opinionated defaults; adjust deliberately, not casually)

1. **Everything renders natively in Obsidian.** No .html files, no external
   dashboards, no non-markdown presentation layers, these drift from source
   and lose Obsidian formatting.
2. **File explorer is primary navigation.** Keep vault root clean, one
   `000-dashboard/` folder plus broad-domain folders with number prefixes
   (`01-engineering/`, `02-culture-society/`, ...).
   Each domain folder has its own Index.md. A newcomer sees numbered folders
   and instantly knows the priority and scope.
3. **Keep it minimal.** Minimize clicks. Remove clutter. Every page
   should have one clear job and one clear action. No redundant labels
   ("Home" on a home page is redundant, use "Start" or just the topic name).
   No emojis on index pages, clean bullet lists only. No frontmatter tags
   that render as visible hashtags. No metadata noise unless it serves a
   direct purpose. Clean lists, not tables.
4. **Wikilinks (`[[...]]`) over markdown links** everywhere, so Obsidian
   backlinks and graph view work automatically. Use `[[path|Display Name]]`
   for custom display text, never show raw filenames.
5. **Static over dynamic.** Plain markdown `[[wikilinks]]` are the default.
   Dataview is only used when the user explicitly requests auto-updating
   tables. Static can't break, requires no plugins, renders instantly.
6. **Surface everything.** The landing page (`000-dashboard/Index.md`) lists
   every entry in the vault grouped by domain, not just courses. Standalone
   entries appear under their own domain headings.
7. **Progressive disclosure.** Landing page shows all categories with brief
   descriptions. Domain pages show their content. Course pages show lecture
   lists. Transcripts show the full content. Each click reveals one more layer.
   Never dump everything at once.
8. **Numbered prefixes for ordering.** Use `000-` for the dashboard, `01-`
   through `0N-` for domain folders in priority order. This enforces
   intentional file explorer ordering regardless of sort algorithm.
   Scripts and utility folders get no prefix, they sort after all numbered
   folders.
9. **No Dataview unless asked.** The default is plain markdown with
   `[[wikilinks]]`. Dataview queries only when the user explicitly requests
   dynamic tables.
10. **Analytical framing for culture/society notes.** When transcribing a
    talk or interview, don't parrot the source's framing or loaded terminology
    (e.g., "manosphere"). Give the note your own title that describes what
    the speaker actually argues. Add an "Observation" section that distills
    the core thesis in analytical language. Preserve the raw transcript below
    the analysis for reference. Use domain-appropriate categories (e.g.,
    `culture` not `talks-interviews`).

## IDs

Persistent `NC-XXXX` IDs, auto-increment, never reused. `transcript.py`
allocates the ID itself on `add`. For anything created by hand (manual
entries, references), allocate with `python3 scripts/next-id.py`, never
hand-pick an ID; `python3 scripts/next-id.py --check` audits for collisions.
Refer to entries by ID in notes and cross-references.

## Dedup

- **YouTube**: Detected by `video_id` frontmatter. Blocked with message; use `--force` to override.
- **PDF**: Deduplicated by resolved file path (I4).
- **Instagram/TikTok/social**: Deduplicated by normalized URL (I4).

## File format

Each entry is a markdown file with YAML frontmatter. Source-type-specific fields:

**YouTube (lecture/course):**
```yaml
id: "NC-0008"
title: "2. Reasoning: Goal Trees and Problem Solving"
source_type: "youtube"
domain: "engineering"
url: "https://youtube.com/watch?v=PNKj529yY5c"
video_id: "PNKj529yY5c"
channel: "MIT OpenCourseWare"
course: "6.034 Artificial Intelligence, Fall 2010"
instructor: "Patrick Winston"
series: "MIT 6.034"
date_added: "2026-06-27"
duration_sec: 2758
categories: ["ai-ml", "programming"]
topics: "goal trees, problem solving"
word_count: 6055
```

**Note on `course` vs `series`:** `course` is the official full course name
(what appears in the OCW description). `series` is the shorthand label used
in the INDEX.md Series column and for grouping entries. For multi-lecture
courses, both fields should be set.

**Instagram/Culture notes (analytical framing):**
```yaml
id: "NC-0006"
title: "Alex Rivers - Ideology as Payment for Community"  # your own title, not source's framing
source_type: "instagram"
domain: "culture-society"
url: "..."
channel: "rivers.talks"
date_added: "2026-06-24"
duration_sec: 96
transcribed: "mlx-whisper (tiny)"
categories: ["culture"]  # not "talks-interviews"
word_count: 276
```

**Telegram video file:**
```yaml
id: "NC-0007"
title: "Home Lab - Twingate, Zero Trust & SASE Networking"
source_type: "telegram"
channel: "Unknown (Telegram video)"
date_added: "2026-06-24"
duration_sec: 90
categories: ["tech"]
word_count: 172
```

**PDF:**
```yaml
id: "NC-0005"
title: "..."
source_type: "pdf"
domain: "engineering"
file_path: "/path/to/doc.pdf"
pages: 1
date_added: "2026-06-24"
categories: ["ai-ml"]
word_count: 35
```

## Telegram integration (for mobile capture)

This capture path is OPTIONAL: it requires creating your own Telegram bot and
running the Hermes gateway (see `references/telegram-gateway.md`). Everything
else in the catalog works without it, paste links or file paths into `add`
directly. Once set up, you send links from your phone to your capture bot
(`@<your_bot_username>`) and Hermes auto-processes them into the catalog.

### Example setup

- **Bot username:** @<your_bot_username> (created via @BotFather)
- **Token:** set in `~/.hermes/.env` as `TELEGRAM_BOT_TOKEN`
- **Gateway:** run as a foreground process (`hermes gateway run`)
- **Auto-auth:** Chrome cookies via `yt-dlp --cookies-from-browser chrome`
  (the operator must be logged into Instagram on Chrome)

### How it works, URL links

1. User sends a link to @<your_bot_username> on Telegram
2. Hermes gateway creates a session, receives the message
3. Agent detects source type and processes it
4. Reply comes back with the NC-XXXX ID and summary

### How it works, video file attachments

The user can also send a video file (MP4, MOV, etc.) directly to the bot
as an attachment. This is the workaround for TikTok (IP-blocked) and any other
short-form video the user wants transcribed.

1. User sends video file to @<your_bot_username>
2. Gateway caches the file at `~/.hermes/cache/videos/video_*.mp4`
3. Gateway message confirmation shows up in logs: `~/.hermes/logs/gateway.log`, search for "Cached user video"
4. Extract audio with ffmpeg: `ffmpeg -y -i <video.mp4> -vn -acodec pcm_s16le -ar 16000 -ac 1 <output.wav>`
5. Transcribe with mlx-whisper (Apple Silicon only) using the helper script (see `<skill_dir>/scripts/catalog-add-from-video.py`)
6. If the user knows the video source or speaker, ask; otherwise use a descriptive title
7. Entry is manually created since `transcript.py` has no `--file` command

**Quick pipeline (after file is cached):**
```bash
# Full pipeline - extract, transcribe, create entry, rebuild index
python3 <skill_dir>/scripts/catalog-add-from-video.py <video.mp4> --title "Video Title"
```
See `<skill_dir>/scripts/catalog-add-from-video.py` for all options.

### Gateway lifecycle

- **Check status:** `hermes gateway status`
- **Restart after config changes:** `hermes gateway restart`
- **Logs:** `~/.hermes/logs/gateway.log`
- **Verify bot is live:** message your capture bot on Telegram

### Authentication for Instagram via gateway

The gateway Hermes session shares the same filesystem and Chrome instance as
the CLI session. `--cookies-from-browser chrome` works automatically IF the
user has an active Instagram session in Chrome. No separate cookie
configuration needed for the gateway.

### Pitfalls

- Gateway must be **restarted** after .env changes (`hermes gateway restart`)
- If the operator's Telegram handle changes or a different account starts
  messaging the bot, the `allowed_users` filter (if set) will block it, leave
  the filter empty for single-user bots
- The gateway agent doesn't automatically load the `content-catalog` skill.
  The user must tell it "add this to the catalog" or the agent must be
  configured with `hermes -s content-catalog`

## Categorization

Keyword matching via `CATEGORY_RULES` in script. Word-boundary regex (`\bkeyword\b`).
10 categories, in rule order: ai-ml, science, programming, web-dev, networking,
tutorial, talks-interviews, tech, culture, with uncategorized as the fallback.

Rules are scored by keyword hit count, ties broken by list order. The primary
category determines which folder the file lands in.

## Audio transcription (any video with no public transcript API)

For Instagram Reels (or any video without a CC/transcript API), the working pipeline.
See `references/instagram-transcription-pipeline.md` for the full end-to-end recipe.

**Warning**: this path is optional, and automating Instagram access with your
logged-in session cookie is against Instagram's terms of service; the account
can be rate-limited or locked. Prefer a throwaway account, and never commit
or share the cookie.

1. **Get session cookies** from Chrome (auto-tried by script) or manually via DevTools
   → See `references/instagram-cookies.md` for extraction workflow
2. **Authenticate via instaloader** (handles Instagram's API better than yt-dlp)
3. **Get video URL** from the post metadata
4. **Download** with `curl` using the direct CDN URL
5. **Extract audio** with `ffmpeg`
6. **Transcribe** with mlx-whisper (Apple Silicon only, ~5s for 90s clip)
7. **File into catalog** by rewriting the entry with the full transcript

**Dependencies**:
- `instaloader` - Instagram API client
- `ffmpeg` (8.1+) - audio extraction
- `mlx-whisper` (0.4.3+) - Whisper speech-to-text, Apple Silicon only (model:
  `mlx-community/whisper-tiny`). On other hardware, use `openai-whisper` or
  `faster-whisper` instead.
- `yt-dlp` - metadata + cookie extraction

**mlx-whisper performance**: ~5-6 seconds for a 90-second clip using the
`mlx-community/whisper-tiny` model on Apple Silicon. The tiny model produces
decently accurate transcripts for clear speech in English.

**Full command sequence:**
```python
import instaloader
loader = instaloader.Instaloader()
loader.context._session.cookies.update({
    'sessionid': '<from_user>',
    'csrftoken': '<from_user>',
    'ds_user_id': '<from_user>',
})
post = instaloader.Post.from_shortcode(loader.context, '<shortcode>')
# post.video_url → download with curl/wget
# ffmpeg -i video.mp4 -vn audio.mp3
# mlx_whisper.transcribe('audio.mp3', path_or_hf_repo='mlx-community/whisper-tiny')
```

**Important**: `instaloader` may print `JSON Query to graphql/query: Expecting value` 
warnings on first call, these are retries and the second attempt succeeds. Not an error.

## Invariant verification

The catalog has a verify command that checks storage invariants on all entries:

```bash
python3 scripts/transcript.py verify
```

This checks for violations including **D-12** (double-hyphen `--` used as em dash), file integrity, and cross-reference consistency. Run this after any manual edits to transcript files. See `references/d-12-fix-workflow.md` for the complete fix workflow with punctuation rules and pitfalls.

## Pitfalls

- **MIT OCW lectures miscategorized as science**: The script's keyword-based
  categorization uses word-boundary regex (\bkeyword\b) and the first match
  wins. MIT OCW lecture titles like "Learning: Identification Trees, Disorder"
  or "Constraints: Interpreting Line Drawings" lack strong ai-ml keywords
  ("neural network", "deep learning", "machine learning") so they fall through
  to science. After adding any MIT OCW lecture, verify the category matches
  other entries in the same series, patch frontmatter and mv the file to
  transcripts/ai-ml/ if needed.
- **Body metadata categories mismatch**: The script writes both YAML frontmatter
  categories and a body-level **Categories:** line between the --- separator and
  the auto-generated intro. When you patch the frontmatter categories, also
  update the body-level **Categories:** line, it is human-visible in the
  rendered page and easily missed. The mismatch happens because the script sets
  the body metadata once at creation time and does not re-read frontmatter on
  rebuild.
- **Verify course/instructor, don't assume**: When processing an MIT OCW or
  university lecture, check `yt-dlp --print description "<url>"` which includes
  the course number and instructor name. I incorrectly assumed "2. Reasoning:
  Goal Trees and Problem Solving" was SICP (Abelson/Sussman), it was actually
  MIT 6.034 AI by Patrick Winston. The channel name is always "MIT OpenCourseWare"
  regardless of the lecturer. Always verify with metadata before filing.
- **Lecture equations: board-only vs. verbally-defined**: Equations that the
  lecturer *defines verbally* ("it's admissible if the estimated distance between
  any node X and the goal is less than or equal to the actual distance") ARE
  captured in the spoken transcript as natural-language text. Purely visual
  equations (drawn on board but not described aloud) are NOT captured.
  See `references/math-extraction-from-screenshots.md` for the technique:
  when OCR fails on a math screenshot, search the transcript catalog with
  topic keywords, the verbally-defined equations are almost certainly there.
- **Math still not found?** For equations that are genuinely board-only (not
  verbally defined), check supplementary materials from the course wiki
  (e.g., `https://ai6034.mit.edu/wiki/images/SlagleSlides.pdf` for the SAINT
  integration example). Use `curl -sL <url> -o /tmp/file.pdf && python3 -c "import
  fitz; doc=fitz.open('/tmp/file.pdf'); [print(page.get_text()) for page in doc]"`
  to extract equation text from these PDFs.
- **TikTok**: Previously IP-blocked from this server but worked as of July 2026. TikTok links are processed like YouTube - `scripts/transcript.py add "<url>"` works directly. If it stops working again, fallback: user downloads on phone and sends the MP4 to the capture bot for Whisper transcription.
- **Transcript.py has no `--file` or local video command**: When the user
  sends a video file via Telegram upload, the catalog entry must be created
  manually or via the helper script at `<skill_dir>/scripts/catalog-add-from-video.py`.
  The script automates: find cached file → extract audio → transcribe →
  create markdown entry → rebuild index.
- **YouTube transcript API v1.2.x**: Changed from static class methods
  (`YouTubeTranscriptApi.list_transcripts(id)`) to instance methods
  (`YouTubeTranscriptApi().fetch(id, languages=['en'])`) in v1.2. The
  catalog script uses the v1.2 API. Older tutorials show the static API.
- **YouTubeTranscriptApi may fail when yt-dlp works**: The transcript API
  sometimes fails on disabled-transcript or age-restricted videos where
  `yt-dlp --write-auto-sub` still works (auto-generated captions). If the
  script errors out, try the yt-dlp VTT fallback pipeline, see
  `references/yt-dlp-vtt-fallback.md` for the full recipe including VTT
  cleanup dedup and catalog integration.
- **Instagram requires session cookies - httpOnly visibility**: The `sessionid`
  cookie is httpOnly, meaning it does NOT appear in `document.cookie` or
  `browser_cookie3`. However, `yt-dlp --cookies-from-browser chrome` CAN extract
  httpOnly cookies (it accesses Chrome's raw cookie store, not the JS API).
  If the script's auto-extraction fails, the user must extract it manually from
  DevTools (Application → Cookies → instagram.com → `sessionid` value).
- **Chrome cookie DB on macOS**: The first access per boot may block briefly
  (~8-10 seconds) while macOS Keychain resolves. `yt-dlp --cookies-from-browser chrome`
  works *after* the user has an active Instagram session in Chrome and the keychain
  has authorized access. If it times out, try from a subprocess with 25s timeout
  or fall back to manual cookie extraction (see `references/instagram-cookies.md`).
  Edge's cookie store is typically faster to access (no keychain prompt).
- **instaloader retry warnings**: The first API call after authentication often
  prints `JSON Query to graphql/query: Expecting value` but auto-retries and
  succeeds on the second attempt. Not an error.
- **Filename collisions abort**: Filenames are keyed by the unique NC-XXXX ID
  (`NC-XXXX_<slug>.md`), so `save_entry()` never overwrites: an existing path
  means an ID was reissued, and the add aborts (I6). Dedup is per source key:
  YouTube by `video_id`, PDF by resolved path, social by normalized URL (I4).
- **Frontmatter parser is naive**: `parse_frontmatter()` uses regex, not a real
  YAML parser. Multi-line values, quoted strings with colons, and edge cases
  will break silently. Keep frontmatter values single-line.
- **Instagram rate-limiting**: Instagram aggressively rate-limits anonymous
  requests from yt-dlp. Even with valid cookies, an `ERROR: rate-limit reached`
  may appear on consecutive requests. Wait or use instaloader instead.

## Keywords

Update `CATEGORY_RULES` list in `scripts/transcript.py` to add/edit category keywords.
Rules are checked in order, first match wins.
