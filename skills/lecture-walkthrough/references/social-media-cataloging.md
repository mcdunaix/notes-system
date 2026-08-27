# Social Media Short-Form Video Cataloging

Record of the TikTok/Instagram reel cataloging workflow. Used by Option D in the
lecture-walkthrough SKILL.md.

## Pipeline

1. `transcript.py add --topics "..." URL` generates a stub in `uncategorized/` with
   a real NC-XXXX ID and the raw source title. The stub has no transcript (no subs
   on these platforms).

2. yt-dlp downloads the audio for transcription:
   ```bash
   yt-dlp -x --audio-format mp3 -o "/tmp/<slug>" "URL"
   ```

3. mlx_whisper transcribes:
   ```bash
   mlx_whisper /tmp/<slug>.mp3 --output-dir /tmp/
   ```

4. Move the stub to the correct category folder. For TikTok, always check the
   creator's profile page (e.g. tiktok.com/@handle) for the real display name.

5. Audio embed (default preference) vs video embed (requires approval):
   ```bash
   # Audio only (default - user prefers this):
   # Extract from the video download:
   yt-dlp -o "NC-XXXX_<slug>" --merge-output-format mp4 "URL"
   mv "NC-XXXX_<slug>" "NC-XXXX_<slug>.mp4"
   ffmpeg -i "NC-XXXX_<slug>.mp4" -vn -acodec mp3 "NC-XXXX_<slug>.mp3" -y
   rm "NC-XXXX_<slug>.mp4"
   
   # Or download audio directly (no video file at all):
   yt-dlp -x --audio-format mp3 -o "NC-XXXX_<slug>" "URL"
   ```
   Instagram requires `--cookies-from-browser chrome` for auth.

6. Rewrite the stub body with walkthrough + full transcript + audio/video embed.

7. Update domain index. New subcategories (e.g. "Indigenous Ways of Learning")
   need a new `##` heading in the index.

## Embedding Rules

- **Audio-only is the default.** Use `<audio controls>` tags in Obsidian.
- **Video embedding requires explicit approval.** Ask before downloading video.
- Video when approved: `<video controls width="360">` for vertical content.

## Category Assignment

| Content Type | Directory | Domain Index |
|---|---|---|
| Indigenous learning, elder wisdom | culture-society/ | 02-culture-society/Index.md |
| Talks, interviews, ideology | talks-interviews/ | 02-culture-society/Index.md |
| Tech, hardware, DIY builds | tech/ | 01-engineering/00-Index.md (Hardware section) |

## Known Platforms

| Platform | Subs? | yt-dlp auth needed? | Notes |
|---|---|---|---|
| TikTok | No native subs | No | Audio download + whisper |
| Instagram Reels | No native subs | Yes (--cookies-from-browser) | Same pipeline |

## Whisper Artifacts

mlx_whisper (tiny model) on short audio:
- May merge segments across speaker pauses
- Mishears proper names (e.g. "Bayo Akomolafe" -> "bio akomolafe lafe")
- Always verify names and quoted material against web search before writing
  the walkthrough

## Creator Name Checks

Always navigate to the creator's profile page (not just the video page) to get
the display name. Examples from this session:

| Handle | Display Name | Bio |
|---|---|---|
| @thotij | Dr. Thomas Tijerina | Humanities Professor exploring meaning, identity, and healing through culture and decolonization |
| @doss.discourse | Joshua Doss | Speaker at Thirdway Conference |

## Domain Index Structure

### 02-culture-society/Index.md

```
# Culture and Society

## Talks & Interviews

- [[../transcripts/talks-interviews/NC-XXXX_slug|Display Title]] - MM:SS

## Indigenous Ways of Learning

- [[../transcripts/culture-society/NC-XXXX_slug|Display Title]] - MM:SS
```

### 01-engineering/00-Index.md

```
## 🛠️ Hardware (N)

DIY electronics, 3D printing, and build projects.

- [[../transcripts/tech/NC-XXXX_slug|Display Title]] - MM:SS
```
