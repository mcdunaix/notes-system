#!/usr/bin/env python3
"""
catalog-add-from-video.py, Full pipeline: local video file → catalog entry.

Transcribes any video file (MP4, MOV, etc.) using mlx-whisper, creates a
catalog entry with NC-XXXX ID, and rebuilds INDEX.md.

Usage:
  python3 catalog-add-from-video.py <video.mp4>
  python3 catalog-add-from-video.py <video.mp4> --title "My Title"
  python3 catalog-add-from-video.py <video.mp4> --title "My Title" --category tech --source "TikTok"

The title and source can also be entered interactively if not provided.

Output:
  - Transcribed markdown file at $CATALOG_ROOT/transcripts/<category>/
  - INDEX.md rebuilt
  - Prints the NC-XXXX ID and path
"""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import date
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
# The catalog root is $CATALOG_ROOT (repo convention). Fall back to the
# repo root so the script also works right after a clone without exports.
ROOT = Path(os.environ.get("CATALOG_ROOT") or Path(__file__).resolve().parent.parent.parent)
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPT_PY = ROOT / "scripts" / "transcript.py"
NEXT_ID_PY = ROOT / "scripts" / "next-id.py"
CATALOG_PREFIX = "NC"

# ── Category map ───────────────────────────────────────────────────────
# Hand-synced mirror of scripts/transcript.py EMOJI_MAP; keep in sync with
# that exact dict (D-17 fixed vocabulary).
CATEGORIES = {
    "ai-ml": "🤖",
    "programming": "💻",
    "web-dev": "🌐",
    "science": "🔬",
    "tutorial": "📚",
    "talks-interviews": "🎙️",
    "networking": "📡",
    "tech": "📱",
    "culture": "🎭",
    "uncategorized": "📄",
}


# ── Helpers ────────────────────────────────────────────────────────────

def next_id() -> str:
    """Allocate the next NC-XXXX id via scripts/next-id.py.

    The allocator scans transcripts/, references/, and Index.md, so ids
    never collide across folders. Falls back to a local transcripts-only
    scan only if the allocator is missing.
    """
    if NEXT_ID_PY.exists():
        result = subprocess.run(
            ["python3", str(NEXT_ID_PY)],
            capture_output=True, text=True, timeout=15,
        )
        m = re.search(r"(NC-\d{4})", result.stdout)
        if m:
            return m.group(1)
    max_num = 0
    for md_file in sorted(TRANSCRIPTS_DIR.rglob("*.md")):
        m = re.search(
            rf'^id:\s*["\']?{re.escape(CATALOG_PREFIX)}-(\d+)',
            md_file.read_text(), re.MULTILINE,
        )
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num
    return f"{CATALOG_PREFIX}-{max_num + 1:04d}"


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[- ]+", "-", text.strip())[:max_len]
    return text.rstrip("-")


def get_duration_sec(video_path: str) -> int:
    """Extract video duration with ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", video_path],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        return int(float(data.get("format", {}).get("duration", 0)))
    except Exception:
        return 0


def extract_audio(video_path: str, wav_path: str) -> None:
    """Extract audio as 16kHz mono WAV for Whisper."""
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path,
         "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
         wav_path],
        check=True, capture_output=True, timeout=120,
    )


def transcribe(audio_path: str) -> tuple[str, str]:
    """Run mlx-whisper and return (full_text, language)."""
    import mlx_whisper
    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo="mlx-community/whisper-tiny",
    )
    return result["text"].strip(), result.get("language", "en")


def guess_category(text: str, title: str) -> list[str]:
    """Simple keyword matching, mirrors transcript.py's logic."""
    combined = (title + " " + text).lower()
    rules = {
        "tech": ["home lab", "raspberry pi", "networking", "server",
                 "vpn", "sase", "zero trust", "homelab", "self-host",
                 "cloud", "infrastructure", "devops", "docker",
                 "kubernetes", "linux", "sysadmin"],
        "programming": ["python", "javascript", "code", "programming",
                        "software", "api", "algorithm", "function"],
        "ai-ml": ["machine learning", "neural network", "ai", "llm",
                  "deep learning", "transformer", "gpt"],
        "talks-interviews": ["interview", "talk", "conversation",
                             "podcast", "discussion"],
        "networking": ["network", "networking", "mesh", "subnet", "firewall",
                       "router", "routing", "protocol", "internet",
                       "bandwidth", "latency", "packet", "dns"],
        "tutorial": ["tutorial", "how to", "guide", "beginner",
                     "step by step"],
        "culture": ["indigenous", "decolonizing", "decolonization", "elder",
                    "ancestral", "ancestors", "tradition", "heritage",
                    "ceremony", "folklore", "oral history", "ritual",
                    "colonialism"],
    }
    matched = []
    for cat, keywords in rules.items():
        if any(kw in combined for kw in keywords):
            matched.append(cat)
            break
    return matched if matched else ["uncategorized"]


def create_entry(title: str, text: str, categories: list[str],
                 duration: int, source: str) -> Path:
    """Create markdown entry file and rebuild index."""
    cat_dir = TRANSCRIPTS_DIR / categories[0]
    cat_dir.mkdir(parents=True, exist_ok=True)

    entry_id = next_id()
    today = date.today().isoformat()
    slug = slugify(title)
    filename = f"{entry_id}_{slug}.md" if slug else f"{entry_id}.md"
    filepath = cat_dir / filename

    word_count = len(text.split())
    dur_str = f"{duration // 60}:{duration % 60:02d}" if duration else "-"

    lines = [
        "---",
        f'id: "{entry_id}"',
        f'title: "{title}"',
        f'source_type: "{source.lower()}"',
        f'date_added: "{today}"',
        f'duration_sec: {duration}',
        f'channel: "{source}"',
        f'categories: ["{categories[0]}"]',
        f"word_count: {word_count}",
        "---",
        "",
        f"# {title}",
        "",
        f"**Source:** {source}  ",
        f"**Duration:** {dur_str}  ",
        f"**Added:** {today}  ",
        f"**Categories:** {', '.join(categories)}",
        "",
        "---",
        "",
        textwrap.fill(text.split("\n\n")[0].strip(), width=100) if "\n\n" in text else "",
        "",
        "## Full Text",
        "",
        "```",
        text,
        "```",
        "",
    ]

    filepath.write_text("\n".join(lines))
    print(f"\n  Entry:   {filepath}")
    print(f"  ID:      {entry_id}")
    print(f"  Title:   {title}")
    print(f"  Words:   {word_count}")
    return filepath


def rebuild_index():
    """Rebuild INDEX.md via the catalog CLI tool."""
    if TRANSCRIPT_PY.exists():
        result = subprocess.run(
            ["python3", str(TRANSCRIPT_PY), "rebuild"],
            capture_output=True, text=True, timeout=30,
        )
        for line in result.stdout.strip().split("\n"):
            print(f"  {line}")
        if result.returncode != 0:
            print(f"  Warning: rebuild stderr: {result.stderr}", file=sys.stderr)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Transcribe a video file and add it to the content catalog.")
    parser.add_argument("video", help="Path to the video file (MP4, MOV, etc.)")
    parser.add_argument("--title", "-t", help="Title for the catalog entry")
    parser.add_argument("--category", "-c", choices=list(CATEGORIES.keys()),
                        help="Category (auto-detected if omitted)")
    parser.add_argument("--source", "-s", default="Telegram video",
                        help="Source/channel name (default: 'Telegram video')")
    parser.add_argument("--keep-audio", action="store_true",
                        help="Don't delete the extracted WAV file after transcription")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"ERROR: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    print(f"📹 Processing: {video_path.name}")
    print(f"  Size: {video_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Get duration
    duration = get_duration_sec(str(video_path))
    print(f"  Duration: {duration // 60}:{duration % 60:02d}")

    # Extract audio
    wav_path = video_path.with_suffix(".wav")
    print(f"  Extracting audio → {wav_path.name} ...")
    extract_audio(str(video_path), str(wav_path))

    # Transcribe
    print("  Transcribing with mlx-whisper (tiny)...")
    text, language = transcribe(str(wav_path))
    print(f"  Language: {language}")
    print(f"  Words: {len(text.split())}")
    print(f"\n{'─' * 60}")
    print("TRANSCRIPT:")
    print(f"{'─' * 60}")
    for line in text.split(". "):
        print(f"  {line.strip()}.")
    print(f"{'─' * 60}")

    # Title
    title = args.title
    if not title:
        title = input("\n  Title for catalog entry [auto-detect]: ").strip()
    if not title:
        # Auto-generate from first line of transcript
        first_sent = text.split(".")[0].strip() if text else "Untitled"
        title = first_sent[:60] if len(first_sent) > 60 else first_sent

    # Category
    categories = [args.category] if args.category else guess_category(text, title)

    # Source
    source = args.source

    # Create entry
    print()
    create_entry(title, text, categories, duration, source)

    # Rebuild index
    print("\n  Rebuilding index...")
    rebuild_index()

    # Cleanup
    if not args.keep_audio:
        wav_path.unlink(missing_ok=True)
        print("  Cleaned up WAV file.")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
