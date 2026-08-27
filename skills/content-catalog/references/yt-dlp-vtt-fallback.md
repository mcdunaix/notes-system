# yt-dlp VTT Fallback for YouTube Transcripts

## When to use

`YouTubeTranscriptApi` (the catalog script's primary method) fails when:
- Transcripts are disabled on the video
- The video is age-restricted (API blocks access)
- The API is rate-limited or returning transient errors
- Only auto-generated captions exist and the API can't serve them

In these cases, `yt-dlp --write-auto-sub` can still download the captions.

## Pipeline

```bash
# 1. Download auto-generated English subtitles as VTT
yt-dlp --write-auto-sub --sub-lang en --skip-download -o "/tmp/%(id)s" "https://www.youtube.com/watch?v=VIDEO_ID"

# 2. VTT file is at /tmp/VIDEO_ID.en.vtt
```

## Cleaning the VTT

VTT format from auto-captions has overlapping word-level timing cues that produce
consecutive duplicate lines and interleaved alignment markers.

### Python cleanup (one-shot)

```python
import re

with open('/tmp/VIDEO_ID.en.vtt', 'r') as f:
    text = f.read()

lines = text.split('\n')

# Skip VTT header (WEBVTT, Kind, Language, blank line)
start = 0
for i, line in enumerate(lines):
    if line.strip() == '':
        start = i + 1
        break

cleaned = []
for line in lines[start:]:
    if '-->' in line:
        continue          # skip timestamp lines
    if not line.strip():
        continue          # skip blanks
    line = re.sub(r'<00:\d+:\d+\.\d+><c>[^<]*</c>', '', line)
    line = re.sub(r'<c>[^<]*</c>', '', line)
    line = line.strip()
    if line:
        cleaned.append(line)

# Deduplicate consecutive identical lines (common VTT artifact)
deduped = []
for line in cleaned:
    if deduped and line == deduped[-1]:
        continue
    deduped.append(line)

transcript = '\n'.join(deduped)
```

## After cleaning: integrate with catalog

Since `scripts/transcript.py` has no `--text` flag to inject pre-fetched content,
the workflow is:

```bash
# 1. Run the script to create the catalog entry (will use YT API)
cd $CATALOG_ROOT
python3 scripts/transcript.py add "https://www.youtube.com/watch?v=VIDEO_ID"

# 2. If the API failed and the entry wasn't created, create manually:
#    - Find the next NC ID from INDEX.md + 1
#    - Write a markdown file to transcripts/<category>/<date>_<slug>.md
#    - Include full YAML frontmatter (see SKILL.md for format)
#    - Rebuild index: python3 scripts/transcript.py rebuild

# 3. If the entry WAS created but has empty/no text (in case API returned
#    nothing but didn't error), overwrite the full-text section with VTT content
#    by reading the file, splicing in the cleaned text between the ``` markers.
```

## When this doesn't work

- **Members-only / private videos**: yt-dlp can't access the page at all without auth
- **No captions at all**: even auto-generated captions are unavailable (rare for English videos)
- **TikTok / Instagram Reels**: different format - use the Instagram pipelines or Telegram video upload workaround instead
