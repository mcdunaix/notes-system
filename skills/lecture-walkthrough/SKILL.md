---
name: lecture-walkthrough
description: Turn YouTube, TikTok, short-form videos, and research papers into structured catalog entries with formatted walkthroughs, key quotes, references, and full transcripts.
---

# Lecture Walkthrough: Structured Catalog Entry from YouTube Lectures

Create detailed, structured walkthrough entries for lecture videos in the content catalog at `$CATALOG_ROOT/`.

## Catalog root

`$CATALOG_ROOT` is the catalog root: the directory containing `scripts/transcript.py`
(the repo root when this repo is used as the vault). Every path below is
relative to it. Set it in your shell before running commands: `export CATALOG_ROOT=/path/to/catalog`.

**Interpreter rule.** Run the tools as `python3 scripts/...` and install
dependencies with `python3 -m pip`, using the same interpreter the pipeline
already runs on. On a device where an agent framework ships its own virtualenv
(Android/Termux: system python3 3.14, the Hermes venv 3.13) a package installed
into the other interpreter is invisible to the catalog, and the failure reads
as a missing feature rather than a missing dependency.

## Workflow

### 1. Choose your pipeline

**Option A, Script pipeline (recommended when it works):**

```bash
cd $CATALOG_ROOT
python3 scripts/transcript.py add "https://www.youtube.com/watch?v=VIDEO_ID" \
  --topics "topic one, topic two"
```

This fetches metadata, transcript, auto-categorizes, assigns NC-XXXX ID, saves to `transcripts/<category>/`, and rebuilds INDEX.md.

**Always pass `--topics` (D-13):** the phrase names the filename slug by subject
(`"reticulum, off-grid mesh networking"` → `NC-00XX_reticulum-off-grid-mesh-networking.md`)
and is stored as a `topics:` frontmatter field. Omitted, the slug falls back to the
video's title, which optimizes for clicks, not for finding (the script prints a nudge
but proceeds). For series lectures, lead the phrase with the lecture number so
filenames sort in series order: `--topics "13 learning by near misses"` →
`13-learning-by-near-misses`.

**Option B, Manual yt-dlp pipeline (robust when script fails or for lecture series with strong format conventions):**

```bash
# Step 1: Get metadata
yt-dlp --print title,description,duration "https://www.youtube.com/watch?v=VIDEO_ID"
# Note: yt-dlp --print accepts multiple comma-separated fields in a single call.
# duration is in seconds: divide by 60 for minutes.

# Step 2: Download full transcript as SRT
yt-dlp --skip-download --write-subs --sub-langs en --convert-subs srt \
  -o "/tmp/lecture_tmp" "VIDEO_URL"

# Step 3: Read the transcript to understand structure
# Auto-generated SRTs may have inline HTML font tags (from TTML conversion).
# Strip them first (see Step 5a), then read in 500-line chunks
# to identify the lecture's logical sections (hook, concepts, demos, punchline).
read_file(path="/tmp/lecture_tmp.en.srt", offset=1, limit=500)

# Step 4: Count word count for frontmatter
python3 -c "
import re
with open('/tmp/lecture_tmp.en.srt') as f:
    c = f.read()
    c = re.sub(r'<font[^>]*>', '', c)  # auto-subs preserve HTML tags after TTML->SRT
    c = re.sub(r'</font>', '', c)
    c = re.sub(r'\\d+\\n\\d{2}:\\d{2}:\\d{2},\\d{3} --> \\d{2}:\\d{2}:\\d{2},\\d{3}\\n', '', c)
    c = re.sub(r'^\\[\\d+\\]', '', c, flags=re.MULTILINE)
    clean = ' '.join(c.split())  # collapse whitespace
    print(f'Word count: {len(clean.split())}')
"

# Step 5: Create the file with write_file (safest for patching)
# Name the file NC-00XX_<topic-slug>.md: the slug names the topic(s), never
# the video's title (D-13); series lectures lead with the lecture number.
# Record the topic phrase as a `topics:` frontmatter field.
# Build the full content: frontmatter + walkthrough + ## Full Text + code block.
# READ existing transcripts from the same series first to match conventions
# (section headings, table style, blockquote usage, reference format).
```

**When to use which:**

| Situation | Use |
|-----------|-----|
| Script works | Option A (faster, handles IDs/indexing) |
| Script fails / transcript disabled | Option B |
| Lecture has existing series entries with strong format conventions | Option B (match existing entries exactly) |
| Video is age-restricted / no subs | Option B with `--write-auto-subs` (auto-generated captions) |
| Summarizing an academic paper (no video) | Option C, Research paper pipeline |
| TikTok / Instagram Reel / short-form video (no native subs) | Option D, Short-form pipeline |

**Option D, TikTok / short-form video pipeline (audio-only, no subs):**

TikTok, Instagram Reels, and similar short-form platforms do not expose subtitles
like YouTube does. The catalog script (Option A) can register the video with an
NC-XXXX ID but produces a stub with no transcript. The script may auto-categorize
based on description and hashtags (e.g. videos with "tech", "engineering",
"product" keywords land in `tech/`; political or identity content without strong
category keywords lands in `uncategorized/`). Check the output directory from the
`add` command: the file may be in a real category, not `uncategorized/`.
Always read the stub's `categories:` frontmatter to confirm.

**After noting the auto-category, verify the corresponding domain index EXISTS
before proceeding.** A category without a live domain index is invisible in
Obsidian navigation despite existing on the dashboard. The dashboard is
auto-generated by `rebuild`; domain indexes are hand-curated and are the
user's primary navigation. If the auto-category has no live index, redirect
the entry to a category that does: e.g. talk-format content that lands in
`tech` should go to `talks-interviews` under
`02-culture-society/01-talks-interviews/`.

Full workflow:

```bash
# Step 1: Register the stub (generates NC-XXXX, saves to transcripts/uncategorized/)
cd $CATALOG_ROOT
python3 scripts/transcript.py add --topics "topic one, topic two" "TIKTOK_URL"

# Step 2: Note the assigned NC-XXXX and the source title from the output above
#          (keep the NC id, the full title, and the filename)

# Step 3: Download the audio track and the video file
# PITFALL: yt-dlp -x may pick a video-only stream on TikTok (bytevc1_* formats
# have no audio track despite the format table showing aac). The download
# succeeds but ffmpeg postprocessing fails with "Output file does not contain
# any stream". Fix: probe with `ffprobe` after download; if only one stream
# (hevc video), re-download the watermarked "download" format which carries
# h264+aac, then extract the mp3 manually with ffmpeg:
#   yt-dlp -f "download" -o "/tmp/<slug>_dl" "TIKTOK_URL"
#   ffmpeg -y -i "/tmp/<slug>_dl" -vn -acodec libmp3lame -q:a 4 "/tmp/<slug>.mp3"
yt-dlp -x --audio-format mp3 -o "/tmp/<slug>" "TIKTOK_URL"

# Step 4: Acquire the transcript with the acquisition helper, never by hand.
#          Do NOT use speech_recognition / Google Web Speech: it silently drops
#          chunks on music-heavy audio and produced every partial entry this
#          catalog has had to repair. Tiers, first to yield >= 40 words wins:
#            subs (source caption track) -> whisper-local (whisper.cpp)
#            -> whisper-mac (mlx_whisper on another host over ssh)
#          The helper prints TRANSCRIPT_SOURCE / WORDS / DURATION / COVERAGE
#          and exits 0 (>=80% coverage), 4 (60-80%), 5 (<60%), 3 (nothing).
catalog-transcribe "TIKTOK_URL" "/tmp/<slug>.txt" <duration_seconds>
#          It ships in this repo at scripts/catalog-transcribe.sh; a device
#          installs it on PATH with its own CATALOG_MAC / CATALOG_WCLI /
#          CATALOG_WMODEL, so the device config stays out of the repo.
#          Exit 3: do NOT file the entry. Exit 4 or 5: file it, and the reply
#          MUST state the transcript source and the coverage. A silent partial
#          transcript is the defect this step exists to prevent.

# Step 5: Read the transcription to identify the talk's structure
read_file(path="/tmp/<slug>.txt", limit=100)

# Step 6: Move the stub to the correct category folder
mkdir -p transcripts/<category>
cp transcripts/uncategorized/NC-XXXX_<slug>.md transcripts/<category>/

# Step 6b: Download the video alongside the .md for Obsidian embedding
#          Use --merge-output-format mp4 to get a playable container
cd transcripts/<category>/
yt-dlp -o "NC-XXXX_<slug>" --merge-output-format mp4 "TIKTOK_URL"
# This produces NC-XXXX_<slug> (headerless mp4). Rename to .mp4:
mv "NC-XXXX_<slug>" "NC-XXXX_<slug>.mp4"

# Step 7: If the uncategorized directory is now empty, remove it
rmdir ../uncategorized/ 2>/dev/null

# Step 8: Build the full entry with write_file.
#          Copy YAML frontmatter and body metadata from the stub verbatim
#          (preserving the load-bearing `id:` line and every existing field).
#          Update categories list to match the destination folder.
#          Update the creator field: use the DISPLAY NAME, not just the handle.
#          Check the creator's profile page (e.g. tiktok.com/@handle) for
#          the real name/bio. TikTok usernames like "prof.avila" are handles;
#          the display name is "Dr. Maria Avila".
#          Replace the stub body with the walkthrough.
#          Paste the transcription under ## Full Text in a code block.
#          Add an audio embed between the metadata block and walkthrough
#          (user prefers audio-only over video by default):
#          <audio controls>
#            <source src="NC-XXXX_<slug>.mp3">
#          </audio>
#          If video embedding was specifically requested, use:
#          <video controls width="360">
#            <source src="NC-XXXX_<slug>.mp4">
#          </video>

# Step 9: Verify domain index exists, then update or create the subcategory entry.
#          FIRST: check whether the target domain index actually exists on disk.
#          A category with no live index is invisible in Obsidian navigation.
#          If the index is missing, choose a category with a living index
#          (e.g. redirect talk-format content from tech/ to talks-interviews/).
#          Do NOT create a fresh domain index as a workaround: the domain
#          structure is curated, not auto-created.
#
#          Path/name per the catalog hierarchy:
#          02-culture-society/Index.md: Talks & Interviews, Culture
#          01-engineering/01-ai/00-Index.md: AI series, etc.
#
#          If the content creates a NEW subcategory (e.g. "Indigenous Ways of Learning"),
#          add it as a new ## heading in the domain index, with the first entry:
#          ## New Subcategory Name
#
#          - [[../transcripts/<category>/NC-XXXX_<slug>|Display Title]] - MM:SS

# Step 10: Gate, both mandatory before the entry counts as done
python3 scripts/transcript.py verify            # ids, fences, folder drift, D-12
python3 scripts/catalog_gate.py --root . --entry NC-XXXX
#   Content gate: coverage vs duration, placeholder text, word_count drift,
#   decoder loops, index reachability. Scope it with --entry, otherwise the
#   catalog's older fails mask this entry's own result.
```

**Key differences from YouTube pipelines:**

| Aspect | YouTube (Options A/B) | TikTok / Short-form (Option D) |
|--------|----------------------|-------------------------------|
| Subtitles | Native SRT (auto or manual) | None. Must transcribe from audio |
| Transcription tool | yt-dlp SRT processing | catalog-transcribe (subs -> whisper.cpp -> mlx_whisper); never speech_recognition |
| Category metadata | YouTube API tags | Auto-categorized from description/hashtags; may land in `uncategorized/` if no strong keywords |
| Walkthrough length | Lecture scale (20-90 min) | Short-form scale (1-5 min) |
| Reference depth | Usually cites papers/textbooks | Cites quoted authors + conceptual context |
| Domain index | Existing section (AI, Science) | May need to CREATE a new subcategory |

**Option C, Research paper pipeline (no video):**

Use when the source is an academic paper, not a YouTube lecture. The structure template (see below) is the same; only the data-fetching pipeline changes.

```bash
# Step 1: Discover papers via web search
# Search by topic keywords. Limit results to credible venues
# (arXiv, IEEE, ACM, Springer, reputable .edu domains).
# web_search returns titles + URLs.

# Step 2: Download the PDF with curl
curl -sL -o /tmp/paper.pdf "https://example.edu/path/to/paper.pdf"

# Step 3: Extract text with PyMuPDF (pip install PyMuPDF if missing)
python3 -c "
import fitz
doc = fitz.open('/tmp/paper.pdf')
for i, page in enumerate(doc):
    print(f'--- PAGE {i+1} ---')
    print(page.get_text()[:2000])
    if i >= 3:
        break
print('Total pages:', len(doc))
" 2>/dev/null

# Step 4: If PDF is scanned/image-only (no selectable text),
# settle for citation metadata (arXiv abstract page, DOI page).
# Do not attempt OCR for a walkthrough: it's not worth the failure risk.

# Step 5: Build the walkthrough using the same structure template:
# Hook / Core Idea / Architecture / Results & Surprising Facts / Punchline
# (the full template is under "Structure template" below)
```

**Key differences from the YouTube pipeline:**

| Aspect | YouTube (Options A/B) | Paper (Option C) |
|--------|----------------------|------------------|
| Source | Video transcript (SRT) | Author text (PDF) |
| Tooling | yt-dlp + SRT processing | curl + PyMuPDF |
| Metadata source | yt-dlp --print | arXiv / DOI / conference page |
| Raw text section | `## Full Text` (verbatim transcript) | Not needed, the paper IS the source |
| Navigation update | Series lecture chain | No chain; standalone entry |

**When you find multiple promising papers in one session:**

1. Run the above pipeline for each paper in parallel (independent terminal calls)
2. Create walkthrough entries in the user's chosen directory (e.g., `<project>/papers/` or `$CATALOG_ROOT/transcripts/compression/`)
3. Create a `00-Index.md` in that directory with a comparison table and reading order

**PDF extraction pitfalls:**

- `web_extract` with DuckDuckGo backend cannot handle PDFs. Always use `curl` + `PyMuPDF` for PDF content.
- If PyMuPDF returns empty text for all pages, the PDF is scanned/image-based, do not fall back to OCR. Extract title/author/abstract from the publisher page or arXiv HTML source instead.
- arXiv PDF URLs: `https://arxiv.org/pdf/XXXX.XXXXX` (use this, not the abstract page).

### 2. Identify the course and instructor

```bash
yt-dlp --print description "https://www.youtube.com/watch?v=VIDEO_ID"
```

The description contains the official course number and instructor name. The channel name (e.g., "MIT OpenCourseWare") is NOT the instructor. For lectures in an existing series, also verify the lecture number against the series index.

### 3. Read existing series entries to match format conventions

Before writing, read 1-2 existing entries from the same series to understand:

- **Section heading style**: are they numbered (`### 1. The Hook`) or descriptive (`### The Core Idea`)?
- **Table format**: pipe tables or markdown definition lists?
- **Blockquote density**: how many quotes per section?
- **Board content rendering**: ASCII art or just prose description?
- **Reference section format**: primary vs secondary, how are URLs presented?
- **Full Text inclusion**: is the raw transcript a code block, or just appended in a different format?

```bash
# Read the most recent entry in the series
ls -t $CATALOG_ROOT/transcripts/<category>/*.md | head -3
read_file(path="...", limit=80)
```

Match the conventions exactly. Inconsistency within a series is more harmful than picking a slightly suboptimal format.

Series-specific format references (loaded from this skill's `references/` directory):

- `references/mit-6.034-walkthrough-conventions.md`, MIT 6.034 / Patrick Winston: numbered sections, metadata pattern, reference format, catalog entry conventions.

Check `references/` for the target series before starting, if such a file exists, it overrides the generic guidance in the workflow steps below.

`transcript.py` auto-categorizes based on YouTube's API tags (e.g., "programming"). For lecture series, the canonical category may differ, check the existing lecture files to learn the right directory:

```bash
ls $CATALOG_ROOT/transcripts/
ls $CATALOG_ROOT/transcripts/<suspected-category>/
```

If the file landed in the wrong category, move it:

```bash
mv $CATALOG_ROOT/transcripts/<wrong>/FILE.md $CATALOG_ROOT/transcripts/<right>/FILE.md
```

**Example:** MIT 6.034 lectures auto-categorize under `programming/` but live canonically under `ai-ml/` alongside the existing lectures.

### 4. Update frontmatter: additively; never rebuild the block

**The `id:` line is load-bearing and must survive every edit.** NC-XXXX IDs are permanent catalog identifiers (protocol D-8 in `docs/STORAGE_PROTOCOL.md`). A frontmatter rewrite that drops `id:` orphans the entry, it renders as `??` in the dashboard index. This is not hypothetical: on 2026-07-08 five MIT 6.034 walkthrough rewrites dropped their `id:` lines, and four of those IDs were silently reissued to other videos before the loss was noticed.

Rules:

- Edit frontmatter by adding or changing individual lines in place. Never reconstruct the block from memory, copy it verbatim from the file and splice in only the fields below. Every existing field survives, including ones this skill doesn't use (`id`, `video_id`, `word_count`, `date_added`, ...).
- Add `course` and `instructor` fields:

```yaml
course: "6.034 Artificial Intelligence, Fall 2010"
instructor: "Patrick Winston"
```

- If you moved the file between categories (step 3), update the `categories` list in frontmatter (target category **first**, `categories[0]` must match the containing folder or `verify` reports drift) and the `domain` field.

Also add these fields to the body metadata block below the title, and update the body-level `**Categories:**` line to match the frontmatter categories list (the script writes both independently and they can drift).

After any frontmatter edit, gate it (stdlib-only, no yt_dlp needed):

```bash
cd $CATALOG_ROOT && python3 scripts/transcript.py verify
```

Exit 0 means all storage invariants hold; on failure it names the file and the broken invariant.

### 5. Read the full transcript

Read the full transcript to identify the lecture's structure:

- **The core problem/equation**: what's on the board that drives the lecture
- **Key quotes**: philosophical moments, punchlines, memorable one-liners
- **The step-by-step walkthrough**: how the problem is solved
- **Results or surprising facts**: metrics, statistics
- **The concluding story or punchline**

### 5a. Clean the SRT before reading

Auto-generated captions (`--write-auto-subs`) start as TTML (XML), then get converted to SRT. **The conversion preserves inline HTML font tags** inside each subtitle line:

```
2|00:00:03,439 --> 00:00:08,320
3|<font color="white" size=\".72c\">with every single ongoing experience.</font>
```

Strip these before reading or counting words:

```bash
python3 -c "
import re
with open('/tmp/lecture_tmp.en.srt') as f:
    content = f.read()
content = re.sub(r'<font[^>]*>', '', content)
content = re.sub(r'</font>', '', content)
# Then strip SRT timestamps as usual (Step 5b)
"
```

A quick test command that strips HTML + timestamps and counts words:

```bash
python3 -c "
import re
with open('/tmp/lecture_tmp.en.srt') as f:
    c = f.read()
c = re.sub(r'<font[^>]*>', '', c)
c = re.sub(r'</font>', '', c)
c = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', c)
text = ' '.join(c.strip().split())
print(f'Word count: {len(text.split())}')
"
```

### 5b. Note the board content

As you read, identify **specific diagrams, drawings, and tables the lecturer draws on the board**. These are the visual anchors of the lecture. For each piece of board content, note:

- What's drawn (label diagrams, maps, schedules, pseudocode)
- The key steps the lecturer walks through verbally while pointing at it
- Any results or intermediate states they annotate

These will be reconstructed as ASCII art or structured tables in the walkthrough (see Structure Template below).

### 5c. Source academic references

The user wants original sources (papers, theses, textbooks) cited, not just the YouTube page. Strategy when web_extract fails (DuckDuckGo backend limitation):

1. **Search for the exact paper** with `web_search` using author, year, title keywords
2. **Find the direct PDF/HTML** URL from the search results
3. **Download with curl** when the URL is a PDF:
   ```bash
   curl -sL -o /tmp/paper.pdf "https://example.edu/path/to/paper.pdf"
   ```
4. **Extract text** with PyMuPDF (`pip install PyMuPDF`) if text-based, or read metadata from the URL alone
5. **Cross-reference with course software**, MIT OCW courses often have accompanying Scheme/Python code that implements the exact algorithms. The MIT 6.034 Scheme CSP examples file (on web.mit.edu) contains the exact junction catalog, for example.
6. **For each reference**, include: full citation (author, year, title, venue), a 1-sentence summary of its relevance, and a URL

Typical paper types for AI/history lectures:
| Type | How to Find |
|------|-------------|
| Classic AI paper (Huffman 1971, Clowes 1971) | Search by name + year + venue ("Machine Intelligence", "Artificial Intelligence journal") |
| PhD thesis (Guzman 1968) | Search on dspace.mit.edu or the author's institution repository |
| Textbook chapter | The course website often links the official textbook |
| Conference paper (Waltz 1975) | Search edited volume title + "Psychology of Computer Vision" |

### 6. Replace the auto-generated intro paragraph

The `transcript.py` script generates a short first paragraph from the transcript's opening lines. Replace everything between the `---` metadata separator and `## Full Text` with a structured walkthrough.

**IMPORTANT, PATCH PITFALL:** The transcript text appears in TWO places in the file: the auto-generated intro paragraph AND the `## Full Text` code block. If you use `patch` with the transcript text as context, its fuzzy matching may replace the wrong occurrence (the code block), destroying the full transcript. **Safe approaches (pick one):**

**Option A, write_file (safest):** Read the whole file, build the new content in a single write_file call: frontmatter + metadata + walkthrough + `## Full Text` + transcript code block. This avoids fuzzy matching entirely. **Copy the frontmatter and metadata verbatim from the file you just read, never retype them.** Retyped frontmatter is exactly how `id:` lines get dropped (see step 4). The header/footer split in `references/inject-walkthrough-assembly.md` preserves both automatically and is the preferred implementation of this option.

**Option B, terminal + sed with exact line ranges:** Find the exact line numbers of the `---` separator and `## Full Text`, then use sed to delete between them, then inject the walkthrough:

```bash
cd $CATALOG_ROOT/transcripts/<category>/
SEP=$(grep -n '^---$' "FILE.md" | tail -1 | cut -d: -f1)
FT=$(grep -n '^## Full Text$' "FILE.md" | cut -d: -f1)
sed -i '' "$((SEP+1)),${FT}d" "FILE.md"
# Then write the walkthrough before ## Full Text
```

**Option C, Two-stage patch (last resort):** First, remove the redundant intro (match from `---` through `## Full Text` via patch, putting nothing between them). Then insert the walkthrough before `## Full Text` via a second patch. Then verify the code block still exists.

**Recovery (if the code block was lost):**

1. Get the transcript from YouTube's auto-subs:
   ```bash
   yt-dlp --skip-download --write-auto-subs --sub-lang en --convert-subs srt \
     -o /tmp/recovery "VIDEO_URL"
   ```
   The SRT may have inline HTML font tags (preserved from the TTML source).
   Strip them with `re.sub(r'<font[^>]*>', '', c)` before timestamp removal.
   If SRT fails, fall back to TTML (YouTube's native format):
   ```bash
   yt-dlp --write-auto-subs --sub-lang en --sub-format ttml \
     --skip-download -o /tmp/recovery "VIDEO_URL"
   ```
   Parse the TTML: extract `<p>` tags with `re.findall(r'<p[^>]*>(.*?)</p>', content)`,
   clean XML entities, remove inner tags.

2. Strip SRT timestamps and HTML tags, then append as a code block under `## Full Text`:
   ```bash
   python3 -c "
import re
with open('/tmp/recovery.en.srt') as f:
    c = f.read()
    c = re.sub(r'<font[^>]*>', '', c)
    c = re.sub(r'</font>', '', c)
    c = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', c)
    c = re.sub(r'^\[\d+\]', '', c, flags=re.MULTILINE)
with open('RECOVERY_TEXT.txt', 'w') as f:
    f.write(c)
"
   ```
3. Append the result as a code block under `## Full Text`: triple-backtick + extracted text + triple-backtick

### 6b. Verify the entry survived (mandatory gate)

After any edit to a transcript file, run the catalog's integrity audit, it checks `id:` presence/uniqueness, the fenced transcript block, category/folder drift, and duplicate content, and it needs no third-party packages:

```bash
cd $CATALOG_ROOT && python3 scripts/transcript.py verify
```

Exit 0 = all invariants hold; on failure it names the file and the broken invariant.

`verify` is a STORAGE gate: it passes on a placeholder transcript. Run the
CONTENT gate as well, scoped to the entry you touched:

```bash
cd $CATALOG_ROOT && python3 scripts/catalog_gate.py --root . --entry NC-XXXX
```

It reports coverage against the source duration, placeholder Full Text,
`word_count` drift against the text actually stored, decoder repetition loops,
missing co-located media for short-form, and whether the entry is reachable
from a hand-curated index as well as the dashboard. Scope it with `--entry`:
this catalog carries older entries with known content fails, and a catalog-wide
exit code would never be 0 again. To pinpoint fence damage manually:

```bash
cd $CATALOG_ROOT/transcripts/<category>/
# Find the ## Full Text section boundaries
grep -n '^```$' FILE.md
# Walkthrough-intrinsic code blocks (ASCII trees, code examples)
# will show extra fence pairs: that's normal.
# Confirm at least one pair exists AFTER ## Full Text:
sed -n '/^## Full Text$/,$ p' FILE.md | grep -c '^```$'
# Should be 2 (opening + closing of the transcript code block).
# Also verify the ## Full Text header is on its own line, not merged:
grep -n '## Full Text' FILE.md
# Should show one line with just that header.
```

If the count is wrong or the header is merged, restore via write_file (Option A in step 6) or fix the merged header.

**Structure template:**

```
## Lecture Walkthrough: <Descriptive Title>

### 1. The Hook / Opening Problem
What question does the lecturer pose at the start? What's the problem on the board?

> Key quote about the problem

### 2. The Core Idea
What's the central concept? Any "naming gives power" moments? The key philosophical
insight that drives the lecture.

> Block-quote the lecturer's key philosophical statements

### 3. The Knowledge / Toolbox
Tables for techniques, transformations, rules introduced. Step-by-step derivations.

### 3b. Board Content
For each major diagram or blackboard drawing in the lecture, add a **Board Content**
subsection near the relevant concept. Use ASCII box/line drawings, structured tables,
number progressions, or final-state diagrams.
Label as `### Board Content: <Descriptive Title>` so they're visually distinct.

### 4. The Architecture / Algorithm
Pseudocode or diagram of the algorithm. Who built it, key constraints.

### 5. Results & Surprising Facts
Metrics table, experimental results, surprising statistics.

### 6. The Punchline
The concluding story or insight, often the "fatal mistake" or "intelligence vanishes" moment.

> **Abstraction sequence:** This template (Hook -> Toolbox -> Architecture -> Punchline) follows the concreteness-fading model. See `references/abstraction-in-teaching.md` for why this sequence matters and how to write each section for transfer.
> **Metaphor and narrative design:** Reach for a metaphor or story frame only when a concept is genuinely hard to land without one, not by default. When it is, see `references/abstraction-in-teaching.md` for the pedagogy, and follow the gated approach: source-domain selection criteria, story craft, and an explicit gate for deciding whether to use this technique at all (the full research write-up, NC-0031 in the author's vault, is not shipped with this repo).

### References section (at end, before ## Full Text)

Include a `## References` section with:

1. **Primary Sources**, the original papers/theses cited by the lecturer, with full citation and URL
2. **Secondary Sources**, textbook chapters, course software repositories, supplementary reading
3. **Board Content Source**, a note that board diagrams were reconstructed from the lecture video, cross-referenced against course materials where available

Each reference format:
```
**Author, A.** (Year). "Title." *Venue*, Volume(Issue), Pages.
- 1-sentence relevance summary.
- URL: https://...
```
```

### 7. Update the lecture chain navigation

Whether using the automated or manual pipeline, after adding a lecture to an existing series you must connect it into the navigation chain.

**Step 1, Add Previous link to the new lecture:**

Find the end of the new file's code block and append navigation links. The pattern is consistent: ``---``, blank line, ``Up:``, blank line, ``Previous:``, (optional ``Next:`` only if the next lecture exists).

```bash
# Read the last few lines of the new file to find the closing fence
tail -5 transcripts/ai-ml/NC-00XX_NEW-lecture.md

# Patch: add nav after closing ```
patch(path="transcripts/ai-ml/NC-00XX_NEW-lecture.md",
      old_string="```",   # This MUST be the LAST ``` in the file (the code block's closing fence)
      new_string="```\n\n---\n\nUp: [[../../01-engineering/01-ai/01-MIT-6.034|MIT 6.034 Course Index]]\nPrevious: [[../ai-ml/NC-00XX_PREVIOUS-lecture|N. Previous Title]]")
```

For lecture series with sub-numbered entries (12a → 12b), use the display name without a leading number: ``12a: Neural Nets``, not ``12a. Neural Nets``.

After the nav patch, re-run the verify gate (step 6b), a mis-anchored fence match here once swallowed the nav links *inside* the transcript code block and destroyed the `## Full Text` heading (NC-0018, an entry in the author's private vault, not shipped in this repo; repaired 2026-07-08).

**Step 2, Add Next link to the previous lecture:**

This is the trickiest step, the previous lecture's nav block must be replaced, not appended. Read the existing block first:

```bash
# Find the navigation block at the bottom of the previous lecture
sed -n '/^---$/{:a;n;p;ba}' transcripts/ai-ml/PREVIOUS-lecture.md | tail -10
```

Then replace the entire nav block from ``---`` through the last line in one patch:

```bash
patch(path="transcripts/ai-ml/PREVIOUS-lecture.md",
      old_string="---\n\nUp: [[../../01-engineering/01-ai/01-MIT-6.034|MIT 6.034 Course Index]]\nPrevious: [[../ai-ml/...|N. Lecture Title]]",
      new_string="---\n\nUp: [[../../01-engineering/01-ai/01-MIT-6.034|MIT 6.034 Course Index]]\nPrevious: [[../ai-ml/...|N. Lecture Title]]\nNext: [[../ai-ml/NC-00XX_NEW|NEW: New Title]]")
```

**Do NOT just append**: appending creates duplicate ``Up:`` and orphaned ``Previous:`` lines that break the navigation rendering.

**Step 3, Add lecture link to course landing page:**

This example is from a live catalog; the file and anchor strings will differ in yours.

```bash
patch(path="$CATALOG_ROOT/01-engineering/01-ai/01-MIT-6.034.md",
      old_string="- [[transcripts/ai-ml/NC-00XX_N-previous-title|N. Previous Title]]",
      new_string="- [[transcripts/ai-ml/NC-00XX_N-previous-title|N. Previous Title]]\n- [[transcripts/ai-ml/NC-00XX_N+1-new-title|N+1. New Title]]")
```

If the new entry has a non-standard number (``12a``), match the series' display convention (e.g., ``12a: Neural Nets`` not ``12a. Neural Nets``).

### 7b. Rebuild the index and run the gate

```bash
cd $CATALOG_ROOT && python3 scripts/transcript.py rebuild && python3 scripts/transcript.py verify
```

The ``transcript.py rebuild`` script regenerates ``000-dashboard/Index.md`` automatically. It does NOT update domain-level indices (``01-engineering/00-Index.md``, ``01-engineering/01-ai/00-Index.md``, etc.) or course landing pages. Those are maintained manually.

``rebuild`` warns (and prints ``??`` ID cells) for entries whose ``id:`` line went missing; ``verify`` turns any such damage into a non-zero exit so it can't slip through. Both are stdlib-only.

### 7c. Update domain-level index for discoverability

After adding and walkthroughing a new entry, add a wikilink to the appropriate domain-level index so it appears in Obsidian navigation:

**Standalone video (no series):** Add to the top-level domain index (e.g., ``01-engineering/00-Index.md``) under the relevant topic section:

```bash
# Find the existing entry in the destination index, then insert.
# Example from a live catalog: the index paths and anchors will differ in yours.
patch(path="$CATALOG_ROOT/01-engineering/00-Index.md",
      old_string="## Programming\n\n- [[../../transcripts/programming/...]]",
      new_string="## Programming\n\n- [[../../transcripts/programming/...]]\n\n## Science\n\n- [[../../transcripts/ai-ml/NC-00XX_title|Display Title]] - MM:SS")
```

Match the existing format: ``- [[relative/path|Display Title]] - Duration`` (or ``, N pages`` for PDFs).

**Series lecture:** Add to the course landing page (e.g., ``01-MIT-6.034.md``), see Step 3 above.

Check which domain indices exist and which one fits. On a fresh catalog none
of these exist yet; create the domain/category index when its first entry
lands (per `docs/STORAGE_PROTOCOL.md`). Example layout from a live catalog:
- ``01-engineering/00-Index.md``, AI, Programming, Science
- ``01-engineering/01-ai/00-Index.md``, AI-specific (MIT 6.034, 3Blue1Brown)
- ``01-engineering/02-programming/00-Index.md``, Programming
- ``02-culture-society/Index.md``, Talks, interviews, culture
- ``02-culture-society/01-talks-interviews/00-Index.md``, Talks & interviews
- ``02-culture-society/02-culture/00-Index.md``, Culture

**Verify the index renders correctly** by re-reading the file after the patch. Domain indices are the user's primary Obsidian navigation, a broken wikilink or stale count is immediately visible.

### 8. LaTeX formatting rules

| Plain text | LaTeX |
|-----------|-------|
| ∫ f(x) dx | `$\int f(x) \, dx$` |
| ∫ f(x)/g(x) dx | `$\int \frac{f(x)}{g(x)} \, dx$` |
| ∫ from a to b | `$\int_a^b$` |
| sin, cos, tan | `\sin`, `\cos`, `\tan` |
| superscripts | `x^2`, `x^{5/2}` |
| arcsin, arctan | `\arcsin`, `\arctan` |
| Use `\displaystyle` for display-style integrals inline | `$\displaystyle \int$` |

Use block quotes (`> text`) for direct quotes from the lecturer.

## Pitfalls

> **References:** See `references/transcript-script-notes.md` for known bugs in the transcript.py script and fix steps.
> **Walkthrough assembly:** See `references/inject-walkthrough-assembly.md` for the Python script pattern that reliably injects a walkthrough between the metadata and `## Full Text` without risk of destroying the transcript code block.
> **Lab guide pattern:** See the lab-builder skill's `references/lab-guide-pattern.md` for how this skill's structure template (Hook, Core Idea, Toolbox, Architecture, Results, Punchline) can be repurposed as a skeleton for hands-on lab guides. The reference also covers **embedded software walkthroughs** (click-path instructions for GUI tools like REW, WINISD, VituixCAD) and **hardware lab considerations** (circuit diagrams, BOMs, measurement procedures): both added during the speaker-design lab build on 2026-07-12.
> **Abstraction in teaching:** See `references/abstraction-in-teaching.md` for the pedagogical theory behind the Hook/Toolbox/Punchline sequence. Covers Bruner's three modes, concreteness fading, the White-Mitchelmore 4-phase model, and practical strategies for writing walkthroughs that transfer understanding rather than just summarize.
> **Metaphor and narrative design:** This is a gated, per-concept technique, not a default pass over every walkthrough. The full research (Lakoff, Gentner, Schon on source domains; Haven, Storr, Zak on story craft; delivery patterns and seductive-details research) lives in the author's vault as NC-0031 and is not shipped with this repo. The shipped guidance in `references/abstraction-in-teaching.md` covers the sequence; treat narrative as opt-in per concept, with an explicit gate.
> **MIT 6.034 series:** See `references/mit-6.034-walkthrough-conventions.md` for the Winston lecture format conventions (numbered sections, body metadata, reference structure, catalog entry).

- **Never drop the `id:` frontmatter line.** Frontmatter rewrites must carry over every existing field, `id:` above all. It is the permanent catalog identifier. Five walkthrough rewrites dropped `id:` on 2026-07-08 and four IDs were silently reissued; ID allocation is now index-backed so reissue can't recur, but a missing `id:` still orphans the entry (`??` in the dashboard). `python3 scripts/transcript.py verify` catches it, run it after every write-back.
- **Don't remove the raw transcript.** The `## Full Text` section with the full transcript in a code block must be preserved below the walkthrough.
- **Slug names the topic, not the title (D-13).** Script path: always pass `--topics "..."` to `add`. Manual path (Options B/C): choose the topic slug yourself and add a `topics:` frontmatter field. Never rename an already-saved entry to fix its slug: renames are D-9 migrations (every reference rewritten in one commit, gated on `verify`), reserved for deliberate cleanups, not this skill.
- **No em dashes, ever (D-12).** Walkthrough prose, headings, tables, and references never use the em dash character or `--` as punctuation. Use a comma, a colon, or two sentences; structural separators (reference relevance lines, index `]] - Duration` suffixes) use a plain hyphen. The whole catalog was scrubbed of em dashes on 2026-07-09 (D-12 in `docs/STORAGE_PROTOCOL.md`); when matching an existing entry's conventions, do not reintroduce them.
- **Verify the instructor.** The YouTube channel name is not the instructor name. Check the video description with `yt-dlp --print description`.
- **Body metadata categories mismatch**: After fixing frontmatter categories and
  adding course/instructor, also check the body-level **Categories:** line between
  the --- separator and the walkthrough. The script writes this independently of
  the YAML frontmatter, they can drift. A mismatched Categories line is visible
  on the rendered page and looks sloppy.
- **Body metadata patch can create duplicate Categories lines**: When patching the
  body metadata block, if the original file has no ``**Categories:**`` line but you
  add one, the patch works fine. But if the original already has a stale
  ``**Categories:**`` line and you try to add Course/Instructor + new Categories in
  one patch call, the new Categories line appears *alongside* the old one (they're
  different strings after all). The safer pattern: first patch to add
  ``**Course:**`` and ``**Instructor:**`` only, then a separate patch to fix the
  ``**Categories:**`` line. Or use write_file to replace the entire metadata block
  in one shot.
- **Don't assume SICP.** MIT OCW has both 6.001 (SICP, Abelson/Sussman) and 6.034 (AI, Patrick Winston). Verify the course number.
- **Check auto-category before writing the walkthrough.** `transcript.py` uses a scoring-based classifier (keyword hit count per category, highest wins). A neuroscience video that mentions "machine learning" once but "neuron" 20+ times correctly lands in `science`, but a passing mention can still trigger `ai-ml` if the main topic is barely covered. Verify the output directory after `transcript.py add`. If wrong: move the file early, before writing the walkthrough or updating the index. Moving it afterward means rewriting the walkthrough to fix path references.
- **Block-quote sparingly.** Use quotes for the most memorable lines, not every sentence.
- **Equations in tables.** Use `$\\displaystyle \int ...$` inside table cells for readability.
- **Patches on the intro can destroy the code block.** The transcript text appears both in the auto-generated intro AND in the `## Full Text` code block. Patch's fuzzy matching may match the wrong occurrence, silently deleting the full transcript. Prefer `write_file` (Option A in step 6) to avoid this. Always verify the code block survived after any patch that touches the intro.
- **Patch can merge `## Full Text` header with code fence.** When you delete the auto-generated intro and the old `## Full Text` header in the same patch, the surviving `## Full Text` header can end up concatenated with the opening backtick fence of the full transcript code block. After any patch on the intro region, verify `## Full Text` is on its own line followed by a blank line then the code fence. Fix by patching the merged line back to two separate lines.
- **TTML transcript extraction.** YouTube auto-subs come as `.ttml` (XML). The `<p>` tags contain the text, not `<span>`. Use `re.findall(r'<p[^>]*>(.*?)</p>', content)` to extract, then strip inner XML tags with `re.sub(r'<[^>]+>', '', t)`.
- **YouTube auto-caption VTT duplication.** `--write-auto-subs` VTT captions repeat each line in 2-3 consecutive segments (e.g. "line A / line A / line A + line B / line B / ..."), so a naive strip-and-join yields ~3x word counts and repeated text in `## Full Text`. Fix: split each SRT block's text into individual lines, then remove consecutive duplicates before joining (deduped words ≈ real count). Verify the word count roughly matches duration × 150-170 wpm; if it's 2-3x that, dedupe again.
- **`write_file` "modified since you last read" warning.** When writing to a file that `transcript.py rebuild` or another concurrent process may have touched (e.g. the MIT 6.034 index, the dashboard Index.md), read_file first before writing to refresh local state. If the warning fires, re-read and re-verify, silent line-merging can occur (two lines concatenated onto one).
- **PDF citation extraction.** `web_extract` fails on many PDFs when backend is DuckDuckGo-only. Workaround: `curl -sL -o /tmp/paper.pdf "$URL"` then `python3 -c "import fitz; doc = fitz.open('/tmp/paper.pdf'); print(doc[0].get_text()[:5000])"` (requires `pip install PyMuPDF`). If the PDF is scanned/image-based (no selectable text), settle for the URL and citation metadata alone, don't try OCR for a references section.
- **Cross-referencing course software.** MIT OCW lectures (especially 6.034) have accompanying code repositories with the exact data structures and algorithms from the lecture. Search for `site:web.mit.edu 6.034 <topic>` or check the course's problem set files. These files often contain the authoritative junction catalog, map data, or constraint definitions and should be cited as a secondary source.
- **Don't forget to update the lecture count in parent indexes.** After adding a lecture to a series, update both the course landing page (add the link) and the domain Index.md (bump the count from "N lectures" to "N+1 lectures"). Forgetting the count update means the parent index shows a stale total.
- **Adding Next link to an existing lecture: read the nav block, don't append.** When adding a Next link to the *previous* lecture (e.g., Lecture 11 gets Next: pointing to 12a), don't just append to the file. Read the existing nav block (Up, Previous, and any existing content below the code block), then replace the entire block in one patch. Appending creates duplicate Up: lines and dead Previous: lines. Use a single patch that replaces from `---` (above Up:) through the last nav line with the corrected block.
- **`## References` should come between the walkthrough and `## Full Text`** in the file. The reference section is metadata about the lecture; the full transcript is the primary source. Do not put references after the full transcript code block.
- **Domain indices are not auto-updated.** `transcript.py rebuild` only touches `000-dashboard/Index.md`. The domain-level indices (`01-engineering/00-Index.md`, `02-culture-society/Index.md`, etc.) are the user's primary Obsidian navigation. After adding any entry, manually add a wikilink under the correct topic section in the matching domain index. Forgetting this means the entry exists on the dashboard but is invisible in the vault's file tree.
- **Category vocabulary is fixed (D-17/D-18).** `verify` only accepts a specific set: ai-ml, science, programming, web-dev, networking, tutorial, talks-interviews, tech, culture, uncategorized. A category like "engineering" will fail verify. Pick the closest match (e.g. tech for hardware builds). The `categories[0]` must match the containing folder name.
- **Domain field must match the parent index.** The frontmatter `domain:` field ("engineering", "culture-society") must match the parent domain directory (01-engineering, 02-culture-society) or the dashboard index may misgroup the entry. The script generates a stub with the real NC-XXXX `id:` when you run `add`. Copy frontmatter verbatim from the stub file, do not retype it. Retyped frontmatter drops the `id:` line.
- **Whisper transcript may have artifacts.** mlx_whisper on short-form audio sometimes merges segments or mishears names (e.g. "bio akomolafe lafe" for "Bayo Akomolafe"). Clean up proper names and quoted material before writing the walkthrough. Verify quoted author/book titles against web search results.
- **Short-form entries need shorter walkthroughs.** A 90-second TikTok does not need 8 sections. Trim to 4-6 tight sections that follow the talk's actual structure. The reference section still needs real citations for any authors quoted; don't pad with tangential sources.
- **Creator display name, not just the handle.** TikTok, Instagram, and similar platforms show a handle (e.g. @prof.avila) but the creator likely has a display name or real name (e.g. "Dr. Maria Avila", a humanities professor, or "Alex Rivers", a conference speaker posting as @rivers.talks). Navigate to the creator's profile page to get it. Use the display name as the `channel:` field and list both in the body metadata: `**Creator:** Dr. Maria Avila (@prof.avila)`.
- **Page H1 title = topic, not raw source title.** For standalone entries (no series), the page H1 and frontmatter `title:` should reflect the TOPIC (matching the slug from D-13), not the video's raw title which optimizes for clicks. The raw source title can appear in the body metadata or not at all. For series lectures, the H1 follows the series convention (lecture number + title).
- **Video embedding requires approval.** Never embed a video file into a catalog entry without asking first. The user considers storage impact and clutter before giving the go-ahead. The embedding pattern (when approved): `<video controls width="360">` tag in Obsidian-compatible HTML, or `![[file.mp4]]` wikilink. Video files live alongside the .md in the same `transcripts/<category>/` directory.
- **Instagram downloads need browser cookies.** Instagram blocks unauthenticated yt-dlp downloads. Always use `--cookies-from-browser chrome` when downloading from Instagram. TikTok downloads work without cookies.
- **Cross-reference related standalone entries.** When two standalone entries (not a formal lecture series) share a creator and one references the other (e.g. "41 life lessons at 41" → "20 lessons for getting into tech"), add body metadata noting the relationship AND a cross-link in References. Pattern: add a line in the earlier entry's body metadata like `*Predecessor to NC-00XX ([Title]).` and in the later entry's body `*Predecessor: NC-00XX ([Title]).` Also link them in the References section of each so the relationship survives index rebuilds.
- **Entries in a category without a live domain index are invisible in Obsidian navigation.** The dashboard (auto-generated by `rebuild`) still lists the entry, but there is no hand-curated domain index to surface it in the file explorer tree. Pattern: talk-format content that auto-categorizes as `tech` (because the description contains "product", "engineering", "career" keywords) should be redirected to `talks-interviews/` under `02-culture-society/` when `tech` has no live index. The `categories:` frontmatter, body Categories line, and physical file location all need updating as a unit. After moving, add a wikilink to the talks-interviews index and bump the parent count.
