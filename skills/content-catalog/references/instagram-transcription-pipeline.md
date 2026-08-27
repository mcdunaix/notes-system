# Instagram → Audio → Transcription Pipeline

Complete sequence for transcribing an Instagram Reel that has no public transcript.

## Prerequisites

All installed:
- `instaloader` - Instagram API
- `ffmpeg` (8.1+) - audio extraction
- `mlx-whisper` (0.4.3+) - Apple Silicon Whisper
- `curl` - download video

## Step-by-step

### 1. Get session cookies

See `references/instagram-cookies.md`. The `sessionid` is httpOnly, must be
extracted from DevTools Application tab (not `document.cookie`).

### 2. Get video URL via instaloader

```python
import instaloader
loader = instaloader.Instaloader()
loader.context._session.cookies.update({
    'sessionid': '<value>',
    'csrftoken': '<value>',
    'ds_user_id': '<value>',
})
post = instaloader.Post.from_shortcode(loader.context, '<shortcode>')
video_url = post.video_url  # direct CDN MP4 URL
```

The shortcode is the part after `/reel/` in the URL (e.g. `DVb6rR_D4qf`).

### 3. Download video

```bash
curl -sL "$video_url" -o /tmp/ig-reel.mp4
```

Typical size: 5-8 MB for a 90-second reel.

### 4. Extract audio

```bash
ffmpeg -y -i /tmp/ig-reel.mp4 -vn -acodec libmp3lame -ab 64k /tmp/ig-audio.mp3
```

Output: ~750 KB for 90 seconds at 64kbps.

### 5. Transcribe with mlx-whisper

```python
import mlx_whisper
result = mlx_whisper.transcribe('/tmp/ig-audio.mp3', path_or_hf_repo='mlx-community/whisper-tiny')
# result['text'] contains the transcript
```

The `whisper-tiny` model is downloaded automatically on first use (~75 MB).
On Apple Silicon, a 90-second clip takes ~5-6 seconds to transcribe.

### 6. Save to catalog

Update the existing entry (created by the script's `add` command which saved
the description only) with the full transcript:

```bash
python3 _scripts/transcript.py add "https://www.instagram.com/reel/<shortcode>/"
```

If already in catalog (dedup), use `--force`:
```bash
python3 _scripts/transcript.py add --force "https://www.instagram.com/reel/<shortcode>/"
```

The entry file is at `transcripts/<category>/<date>-<slug>.md`. Edit the
frontmatter to add `transcribed: "mlx-whisper (tiny)"` and replace the
description-only content with the full transcript.

## Known issues

- **instaloader JSON warning**: First call after auth prints
  `JSON Query to graphql/query: Expecting value` then auto-retries and succeeds.
  Not an error.
- **Rate-limiting**: Both yt-dlp and instaloader may hit rate limits on
  repeated calls. Wait 30-60 seconds between downloads.
- **model download for mlx-whisper**: Only `mlx-community/whisper-tiny` works
  without HF token auth. Larger models (`small`, `medium`) return 401 from
  Hugging Face for the MLX format repos.
