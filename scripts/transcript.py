#!/usr/bin/env python3
"""
Content catalog, video transcripts, PDFs, and social media posts with persistent IDs.

Storage protocol (invariants this file maintains):
  I1  Files are truth. transcripts/<category>/<NC-id>_<slug>.md with YAML
      frontmatter is the only durable store; 000-dashboard/Index.md and
      `list` output are derived views, regenerable any time with `rebuild`.
      The slug names the topic(s) passed via --topics, falling back to the
      source title only when no topics were given (D-13); the verbatim
      title always survives in frontmatter.
  I2  IDs are permanent, unique, monotone. Allocation takes
      max(live frontmatter IDs ∪ IDs recorded in the existing Index.md) + 1,
      so an `id:` line lost to an external edit can never cause reissue.
  I3  One scan per command, frontmatter only. Every command reads the catalog
      once via scan_catalog(), which parses just the frontmatter block,
      never the transcript body.
  I4  Every add is deduplicated by a per-source content key
      (youtube → video_id, pdf → resolved path, social → normalized URL).
  I5  Derived views escape their format: YAML strings on write, `|` in
      Index.md table cells.
  I6  Saves never overwrite: filenames are keyed by the unique entry ID, so
      a collision means an ID was reissued, the add aborts. Existing files
      are never renamed (domain indexes wikilink them by path).
  I7  `verify` audits the invariants (missing/duplicate IDs, unparseable
      frontmatter, category/folder drift, `## Full Text` fence integrity)
      and exits non-zero on violations. references/ is scanned too, for
      the checks that apply there (frontmatter, id integrity, D-12).
  I8  rebuild/list/verify run on stdlib alone; yt_dlp, youtube_transcript_api,
      and fitz import lazily inside the fetch paths that need them.

Commands:
  add <url> [--topics "..."] [--series "..."] - YouTube / Instagram / TikTok
  add --pdf <path> [--topics "..."] [--series "..."] - Extract text from PDF
  rebuild - Rebuild 000-dashboard/Index.md from entries
  list - List all catalog entries
  verify - Audit storage invariants (exit 1 on violation)

Usage:
  python3 scripts/transcript.py add "https://youtube.com/watch?v=..." \
      --topics "reticulum, off-grid mesh networking"
  python3 scripts/transcript.py add --pdf "path/to/document.pdf"
  python3 scripts/transcript.py rebuild
  python3 scripts/transcript.py verify
"""

import re
import sys

if sys.version_info < (3, 10):
    sys.exit("transcript.py needs Python 3.10 or newer "
             f"(you are running {sys.version.split()[0]}). "
             "Install a current Python from https://www.python.org/downloads/")

import argparse
import textwrap
import urllib.parse
from pathlib import Path
from datetime import date
from collections import Counter

NOTES_DIR = Path(__file__).resolve().parent.parent
TRANSCRIPTS_DIR = NOTES_DIR / "transcripts"
REFERENCES_DIR = NOTES_DIR / "references"  # shares the NC numbering (storage protocol)
INDEX_PATH = NOTES_DIR / "000-dashboard" / "Index.md"

CATALOG_PREFIX = "NC"  # Notes Catalog
ID_PATTERN = re.compile(rf"\b{CATALOG_PREFIX}-(\d{{4}})\b")
FRONTMATTER_MAX_BYTES = 8192  # frontmatter must fit in the head of the file

# New entries get "## Full Text"; hand-expanded files legitimately use the
# other names. verify anchors on the LAST such heading in the file.
TRANSCRIPT_HEADING = re.compile(
    r"^## (Full Text|Full Transcript|Raw Transcript|Transcript)\s*$", re.MULTILINE
)

# Category → domain mapping for the folder structure
CATEGORY_DOMAIN = {
    "ai-ml": "engineering",
    "programming": "engineering",
    "web-dev": "engineering",
    "science": "engineering",
    "tutorial": "engineering",
    "networking": "engineering",
    "talks-interviews": "culture-society",
    "tech": "engineering",
    "culture": "culture-society",
}

# The fixed vocabulary (D-17): domains a category may map to. The `it`
# domain was retired by D-14; verify (I7) flags any CATEGORY_DOMAIN value
# that falls outside this set, the same way KNOWN_CATEGORIES guards
# categories, so a stale mapping to a dead domain fails loud instead of
# silently resurrecting it in the next rebuild.
KNOWN_DOMAINS = {"engineering", "culture-society"}

# Category keywords: scored by hit count, ties broken by list order
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("ai-ml", [
        "machine learning", "deep learning", "neural network", "neural net",
        "llm", "transformer",
        "artificial intelligence", "gpt", "diffusion", "embedding", "rag",
        "fine-tuning", "fine tuning", "training a model", "token", "attention mechanism",
        "reinforcement learning", "agent", "autonomous", "langchain", "vector database",
        # The working vocabulary of a deep-learning lecture. Without these,
        # `neuron` counts drag every neural-network video into science
        # (found live with the 3Blue1Brown intro lecture; see
        # test_ai_ml_category.py). Deliberately excluded as too generic:
        # "layer", "network", "training", "pixel".
        "weights", "biases", "activation", "activations", "sigmoid",
        "gradient descent", "backpropagation", "hidden layer", "mnist",
        "convolutional",
    ]),
    ("science", [
        "neuroscience", "neuron", "synapse", "synaptic", "dendrite", "biology",
        "physics", "chemistry", "quantum", "experiment", "laboratory",
        "research paper", "study found", "scientists", "nasa", "space",
        "mathematics", "equation", "theory of", "cellular", "molecular",
    ]),
    ("programming", [
        "python", "javascript", "rust", "golang", "typescript", "code",
        "programming", "software", "api", "git", "debug", "compiler",
        "framework", "library", "function", "algorithm", "data structure",
        "cursor", "copilot", "vscode", "ide", "terminal", "cli",
    ]),
    ("web-dev", [
        "react", "next.js", "vue", "svelte", "css", "html", "frontend",
        "backend", "fullstack", "web app", "web development", "node.js",
        "tailwind", "vercel", "deployment", "docker", "container",
    ]),
    ("networking", [
        "reticulum", "mesh", "meshtastic", "lora", "lorawan", "packet",
        "routing", "networking", "off-grid", "ad hoc", "radio",
        "vpn", "wireguard", "tailscale", "twingate", "zero trust", "zero-trust",
        "homelab", "home lab", "self-host", "self-hosted", "self-hosting",
        "subnet", "firewall",
    ]),
    ("tutorial", [
        "tutorial", "guide", "step by step", "beginner", "how to",
        "learn ", "getting started", "crash course", "walkthrough",
    ]),
    ("talks-interviews", [
        "interview", "podcast", "talk", "conversation", "discussion",
        "fireside chat", "keynote", "panel",
    ]),
    ("tech", [
        "technology", "tech", "computer", "hardware", "gpu", "cpu",
        "server", "cloud", "aws", "apple", "microsoft", "google",
        "startup", "saas", "product",
    ]),
    ("culture", [
        "indigenous", "decolonizing", "decolonization", "elder", "ancestral",
        "ancestors", "tradition", "traditions", "heritage", "ceremony",
        "folklore", "oral history", "ritual", "colonialism",
    ]),
]

# The fixed vocabulary (D-17): guess_category never returns anything outside
# this set, and verify (I7) flags any categories[0] that falls outside it,
# the enforcement mechanism D-18 constrains recategorization to.
KNOWN_CATEGORIES = {cat for cat, _ in CATEGORY_RULES} | {"uncategorized"}

EMOJI_MAP = {
    "ai-ml": "🤖", "programming": "💻", "web-dev": "🌐",
    "science": "🔬", "tutorial": "📚", "talks-interviews": "🎙️",
    "networking": "📡", "tech": "📱", "culture": "🎭", "uncategorized": "📄",
}

TYPE_ICONS = {"youtube": "🎬", "instagram": "📱", "tiktok": "📱", "pdf": "📄"}


class TranscriptUnavailable(RuntimeError):
    """No transcript could be fetched for a video."""


def require(module_name: str, pip_name: str):
    """Import a fetch-path dependency or exit with install instructions (I8).

    Only `add` needs third-party packages; rebuild/list/verify stay
    stdlib-only. A missing package should read as a setup step, not a
    traceback.
    """
    import importlib
    try:
        return importlib.import_module(module_name)
    except ImportError:
        sys.exit(f"ERROR: `add` needs the `{pip_name}` package, which is not "
                 "installed.\n  Install all fetch dependencies with:\n"
                 "    python3 -m pip install -r requirements.txt\n"
                 f"  Or just this one:\n    python3 -m pip install {pip_name}")


def rel(path: Path) -> Path:
    """Path relative to the vault for display; absolute if outside it."""
    try:
        return path.relative_to(NOTES_DIR)
    except ValueError:
        return path


# ── Frontmatter (I3: read heads only) ──────────────────────────────────────

def parse_frontmatter(content: str) -> dict | None:
    """Extract YAML-like frontmatter from markdown text."""
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return None
    data = {}
    for line in m.group(1).strip().split("\n"):
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            data[key] = [v.strip().strip('"') for v in val[1:-1].split(",")]
        elif len(val) >= 2 and val[0] == '"' and val[-1] == '"':
            data[key] = val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        else:
            data[key] = val
    return data


def read_frontmatter(md_file: Path) -> dict | None:
    """Parse frontmatter reading only the head of the file, never the body."""
    try:
        with md_file.open("r", encoding="utf-8") as fh:
            head = fh.read(FRONTMATTER_MAX_BYTES)
    except OSError:
        return None
    return parse_frontmatter(head)


def scan_catalog() -> list[dict]:
    """One pass over transcripts/: [{path, fm}, ...] for every .md file.

    fm is None when frontmatter is missing/unparseable, callers surface
    these loudly (build_index warns, verify fails) instead of skipping
    silently, because an invisible entry is how IDs get reissued.
    """
    if not TRANSCRIPTS_DIR.exists():
        return []
    return [{"path": p, "fm": read_frontmatter(p)}
            for p in sorted(TRANSCRIPTS_DIR.rglob("*.md"))]


# ── ID management (I2: monotone, loss-proof) ───────────────────────────────

def issued_ids(entries: list[dict]) -> set[int]:
    """Every ID number ever issued: live frontmatter ∪ the existing index.

    The index is a derived view, but it is rebuilt on every add, so it also
    serves as the durable record of issued IDs. An `id:` line lost to an
    external edit (this has happened) shrinks the live set but not the
    index set, the union keeps allocation monotone either way.

    references/ shares the NC numbering convention (storage protocol). Its
    ids join the set here so a transcript ingest can never reuse one, the
    blind spot that caused a live NC-0034 collision (see next-id.py).
    """
    nums = set()
    for e in entries:
        fm = e["fm"]
        if fm and "id" in fm:
            m = re.match(rf"^{CATALOG_PREFIX}-(\d+)$", str(fm["id"]))
            if m:
                nums.add(int(m.group(1)))
    if REFERENCES_DIR.exists():
        for p in REFERENCES_DIR.rglob("*.md"):
            fm = read_frontmatter(p)
            if fm and "id" in fm:
                m = re.match(rf"^{CATALOG_PREFIX}-(\d+)$", str(fm["id"]))
                if m:
                    nums.add(int(m.group(1)))
    if INDEX_PATH.exists():
        for m in ID_PATTERN.finditer(INDEX_PATH.read_text(encoding="utf-8")):
            nums.add(int(m.group(1)))
    return nums


def next_catalog_id(entries: list[dict]) -> str:
    nums = issued_ids(entries)
    return f"{CATALOG_PREFIX}-{(max(nums) + 1 if nums else 1):04d}"


# ── Dedup (I4: per-source content keys) ────────────────────────────────────

def normalize_url(url: str) -> str:
    """Host + path, lowercased host, no www/query/trailing slash."""
    p = urllib.parse.urlparse(url)
    netloc = p.netloc.lower().removeprefix("www.")
    return f"{netloc}{p.path.rstrip('/')}"


def content_key(fm: dict) -> tuple | None:
    """The identity of an entry's source, independent of title/category."""
    src = fm.get("source_type", "")
    if src == "youtube" and fm.get("video_id"):
        return ("youtube", fm["video_id"])
    if src == "pdf" and fm.get("file_path"):
        return ("pdf", fm["file_path"])
    if fm.get("url"):
        return ("url", normalize_url(fm["url"]))
    return None


def find_duplicate(entries: list[dict], key: tuple) -> dict | None:
    for e in entries:
        if e["fm"] and content_key(e["fm"]) == key:
            return e
    return None


# ── YouTube ────────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    parsed = urllib.parse.urlparse(url)
    if "youtube.com" in parsed.netloc or "youtu.be" in parsed.netloc:
        if parsed.path == "/watch":
            return urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
        if "youtu.be" in parsed.netloc:
            return parsed.path.lstrip("/").split("?")[0]
        m = re.match(r"/shorts/([a-zA-Z0-9_-]+)", parsed.path)
        if m:
            return m.group(1)
        m = re.match(r"/embed/([a-zA-Z0-9_-]+)", parsed.path)
        if m:
            return m.group(1)
    return None


def fetch_metadata(video_id: str) -> dict:
    """Fetch video title and channel using yt-dlp (no download)."""
    yt_dlp = require("yt_dlp", "yt-dlp")
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )
            return {
                "title": info.get("title", ""),
                "channel": info.get("channel", info.get("uploader", "")),
                "duration": info.get("duration", 0),
            }
    except Exception as e:
        print(f"  Warning: Could not fetch metadata: {e}", file=sys.stderr)
        return {"title": "", "channel": "", "duration": 0}


def fetch_transcript(video_id: str) -> str:
    """Fetch transcript text for a video ID (youtube_transcript_api v1.2.x)."""
    require("youtube_transcript_api", "youtube-transcript-api")
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

    api = YouTubeTranscriptApi()
    try:
        transcript = api.fetch(video_id, languages=["en"])
    except NoTranscriptFound:
        try:
            transcript = api.fetch(video_id)
        except Exception as e:
            raise TranscriptUnavailable(f"no transcript in any language: {e}") from e
    except TranscriptsDisabled as e:
        raise TranscriptUnavailable(f"transcripts disabled: {e}") from e
    return " ".join(snippet.text for snippet in transcript)


# ── PDF ────────────────────────────────────────────────────────────────────

def extract_pdf_text(pdf_path: str) -> dict:
    """Extract text from a PDF using pymupdf."""
    fitz = require("fitz", "pymupdf")
    doc = fitz.open(pdf_path)
    pages_text = []
    for page in doc:
        t = page.get_text()
        if t.strip():
            pages_text.append(t)
    return {
        "text": "\n\n".join(pages_text),
        "pages": len(doc),
    }


# ── Social (Instagram / TikTok) ────────────────────────────────────────────

def detect_source_type(url: str) -> str:
    domain = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    if "instagram.com" in domain:
        return "instagram"
    if "tiktok.com" in domain:
        return "tiktok"
    return "unknown"


def extract_social_metadata(url: str) -> dict:
    """Extract metadata from a social post via yt-dlp (browser cookies, then bare)."""
    try:
        import subprocess
        result = subprocess.run(
            ["yt-dlp", "--cookies-from-browser", "chrome",
             "--quiet", "--no-warnings", "--print",
             "%(title)s||%(uploader)s||%(duration)s||%(description)s",
             url],
            capture_output=True, text=True, timeout=25,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split("||", 3)
            parts += [""] * (4 - len(parts))
            return {
                "title": parts[0] or "",
                "channel": parts[1] or "",
                "duration": int(float(parts[2])) if parts[2] else 0,
                "description": parts[3].strip() if parts[3] else "",
            }
    except Exception:
        pass

    yt_dlp = require("yt_dlp", "yt-dlp")
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            desc = info.get("description") or info.get("alt_title", "")
            return {
                "title": info.get("title", info.get("alt_title", "Untitled")),
                "channel": info.get("uploader", info.get("channel", "")),
                "duration": info.get("duration", 0) or 0,
                "description": desc.strip() if desc else "",
            }
    except Exception as e:
        print(f"  Warning: Could not fetch metadata: {e}", file=sys.stderr)
        return {"title": "", "channel": "", "duration": 0, "description": ""}


# ── Categorization ─────────────────────────────────────────────────────────

def guess_category(text: str, title: str) -> list[str]:
    """Score categories by keyword hits (word-boundary matched).

    Returns the winner plus at most two secondaries that scored at least
    max(2, winner//4), a stray keyword hit no longer tags a 50-minute
    lecture with six categories.
    """
    combined = (title + " " + text).lower()
    scores = {}
    for cat, keywords in CATEGORY_RULES:
        score = 0
        for kw in keywords:
            score += len(re.findall(r"\b" + re.escape(kw.lower()) + r"\b", combined))
        if score > 0:
            scores[cat] = score
    if not scores:
        return ["uncategorized"]
    order = [cat for cat, _ in CATEGORY_RULES]
    ranked = sorted(scores, key=lambda c: (-scores[c], order.index(c)))
    best = ranked[0]
    floor = max(2, scores[best] // 4)
    return [best] + [c for c in ranked[1:] if scores[c] >= floor][:2]


def slugify(text: str, max_len: int = 60) -> str:
    """Turn text into a filesystem-safe slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text.strip())[:max_len]
    return text.rstrip("-")


# ── Series clustering ──────────────────────────────────────────────────────
# A multi-part source (a lecture series, a course) is tagged with --series.
# The series decides the folder: the first entry files wherever the keyword
# guess puts it, every later entry follows the series, never the per-video
# guess. Episode-to-episode vocabulary drift is exactly how earlier versions
# of this system scattered a series across category folders.

def series_category(entries: list[dict], series: str) -> str | None:
    """The primary category the series already lives in, or None if unseen."""
    for e in entries:
        fm = e["fm"]
        if fm and str(fm.get("series", "")) == series:
            cats = fm.get("categories", [])
            if isinstance(cats, list) and cats:
                return cats[0]
    return None


def resolve_categories(guessed: list[str], series_cat: str | None) -> list[str]:
    """Force the series' folder into the primary slot, keep guessed
    secondaries, capped at two like guess_category."""
    if not series_cat or guessed[0] == series_cat:
        return guessed
    return [series_cat] + [c for c in guessed if c != series_cat][:2]


def series_conflicts(entries: list[dict]) -> dict[str, list[str]]:
    """{series: sorted categories} for every series split across folders."""
    cats_by_series: dict[str, set[str]] = {}
    for e in entries:
        fm = e["fm"]
        if fm and fm.get("series"):
            cats = fm.get("categories", [])
            primary = cats[0] if isinstance(cats, list) and cats else str(cats)
            cats_by_series.setdefault(str(fm["series"]), set()).add(primary)
    return {s: sorted(c) for s, c in cats_by_series.items() if len(c) > 1}


# ── Save (I5: escape on write; I6: never overwrite) ────────────────────────

def yaml_str(value) -> str:
    """Double-quoted YAML scalar with backslash and quote escaping."""
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def save_entry(entry_data: dict) -> Path:
    """
    Save a catalog entry as markdown with YAML frontmatter.
    Required keys: id, title, source_type, text, categories
    Optional: topics (names the filename slug, D-13; title is the fallback)
    Optional: series (multi-part sources cluster; verify keeps a series
        in one category folder)
    Optional (video/social): url, video_id, channel, duration
    Optional (pdf): file_path, pdf_pages, author
    """
    today = date.today().isoformat()
    slug = slugify(entry_data.get("topics") or entry_data.get("title") or "")
    if slug and not entry_data.get("topics"):
        print('  note: filename slugged from the source title; '
              'pass --topics "..." to name by topic (D-13)')
    cat_dir = TRANSCRIPTS_DIR / entry_data["categories"][0]
    cat_dir.mkdir(parents=True, exist_ok=True)

    filepath = cat_dir / (f"{entry_data['id']}_{slug}.md" if slug else f"{entry_data['id']}.md")
    if filepath.exists():
        print(f"ERROR: {rel(filepath)} already exists, ID reissued? Run `verify`.",
              file=sys.stderr)
        sys.exit(1)

    src_type = entry_data.get("source_type", "youtube")
    text = entry_data["text"]
    categories = entry_data["categories"]
    title = entry_data["title"] or "Untitled"
    word_count = len(text.split())
    domain = CATEGORY_DOMAIN.get(categories[0], "")

    lines = ["---"]
    lines.append(f"id: {yaml_str(entry_data['id'])}")
    lines.append(f"title: {yaml_str(title)}")
    lines.append(f"source_type: {yaml_str(src_type)}")
    if domain:
        lines.append(f"domain: {yaml_str(domain)}")

    if src_type == "youtube":
        lines.append(f"url: {yaml_str(entry_data['url'])}")
        lines.append(f"video_id: {yaml_str(entry_data.get('video_id', ''))}")
        lines.append(f"channel: {yaml_str(entry_data.get('channel', ''))}")
        lines.append(f"duration_sec: {entry_data.get('duration', 0)}")
    elif src_type == "pdf":
        lines.append(f"file_path: {yaml_str(entry_data.get('file_path', ''))}")
        if entry_data.get("pdf_pages"):
            lines.append(f"pages: {entry_data['pdf_pages']}")
        if entry_data.get("author"):
            lines.append(f"author: {yaml_str(entry_data['author'])}")
    else:  # instagram, tiktok, other url-backed sources
        lines.append(f"url: {yaml_str(entry_data['url'])}")
        lines.append(f"channel: {yaml_str(entry_data.get('channel', ''))}")
        if entry_data.get("duration"):
            lines.append(f"duration_sec: {entry_data['duration']}")

    lines.append(f"date_added: {yaml_str(today)}")
    lines.append(f"categories: [{', '.join(yaml_str(c) for c in categories)}]")
    if entry_data.get("topics"):
        lines.append(f"topics: {yaml_str(entry_data['topics'])}")
    if entry_data.get("series"):
        lines.append(f"series: {yaml_str(entry_data['series'])}")
    lines.append(f"word_count: {word_count}")
    lines.append("---")
    lines.append("")

    lines.append(f"# {title}")
    lines.append("")
    if src_type == "pdf":
        lines.append(f"**File:** `{entry_data.get('file_path', '')}`  ")
        if entry_data.get("pdf_pages"):
            lines.append(f"**Pages:** {entry_data['pdf_pages']}  ")
    else:
        lines.append(f"**Source:** [{entry_data['url']}]({entry_data['url']})  ")
        lines.append(f"**Channel:** {entry_data.get('channel', 'Unknown')}  ")
        dur = entry_data.get("duration", 0)
        if dur or src_type == "youtube":
            lines.append(f"**Duration:** {format_duration(dur)}  ")
    if entry_data.get("series"):
        lines.append(f"**Series:** {entry_data['series']}  ")
    lines.append(f"**Added:** {today}  ")
    lines.append(f"**Categories:** {', '.join(categories)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    paragraphs = text.split("\n\n")
    if paragraphs:
        lines.append(textwrap.fill(paragraphs[0].strip(), width=100))
    lines.append("")
    lines.append("## Full Text")
    lines.append("")
    lines.append("```")
    lines.append(text)
    lines.append("```")
    lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath


# ── INDEX.md builder (I1: derived view) ────────────────────────────────────

def format_duration(sec: int) -> str:
    if not sec:
        return "-"
    m, s = divmod(int(sec), 60)
    return f"{m}:{s:02d}"


def md_cell(value: str) -> str:
    """Escape a value for a markdown table cell."""
    return str(value).replace("|", "\\|")


def domain_for(category: str) -> str:
    """A category's Domain (D-17 tier 1); unmapped categories get their own bucket."""
    return CATEGORY_DOMAIN.get(category, "uncategorized")


def cluster_rows(cat_rows: list[dict]) -> list[dict]:
    """Sort a category's rows so series members sit contiguously.

    Each series block is anchored at its lowest member id; standalone rows
    keep plain id order. Within a block, members stay in id order.
    """
    anchor: dict[str, str] = {}
    for r in cat_rows:
        s = r.get("series", "")
        if s:
            rid = str(r["id"])
            anchor[s] = min(anchor.get(s, rid), rid)
    return sorted(cat_rows,
                  key=lambda r: (anchor.get(r.get("series", ""), str(r["id"])),
                                 str(r["id"])))


def group_by_domain(rows: list[dict]) -> dict[str, dict[str, list]]:
    """Group index rows by Domain, then by Category within Domain (D-18).

    Keeps the dashboard's size tied to Domain/Category count rather than
    entry count as the catalog grows.
    """
    grouped: dict[str, dict[str, list]] = {}
    for r in rows:
        grouped.setdefault(domain_for(r["category"]), {}).setdefault(r["category"], []).append(r)
    return grouped


def build_index(entries: list[dict] | None = None):
    """Regenerate INDEX.md from catalog entries (scans once if not given)."""
    if entries is None:
        entries = scan_catalog()
    if not entries:
        print("No transcripts found.")
        return

    unparseable = [e["path"] for e in entries if e["fm"] is None]
    missing_id = [e["path"] for e in entries
                  if e["fm"] is not None and not str(e["fm"].get("id", "")).startswith(CATALOG_PREFIX)]

    rows = []
    for e in entries:
        fm = e["fm"]
        if not fm:
            continue
        src_type = fm.get("source_type", "youtube")
        cats = fm.get("categories", ["uncategorized"])
        try:
            duration = int(fm.get("duration_sec", 0))
        except (TypeError, ValueError):
            duration = 0
        rows.append({
            "id": str(fm.get("id", "??")),
            "title": fm.get("title", "Untitled"),
            "type": f"{TYPE_ICONS.get(src_type, '📄')} {src_type}",
            "url": fm.get("url", ""),
            "category": cats[0] if isinstance(cats, list) else str(cats),
            "date": fm.get("date_added", ""),
            "duration": duration,
            "channel": fm.get("channel", ""),
            "source_type": src_type,
            "series": str(fm.get("series", "") or ""),
        })

    grouped = group_by_domain(rows)
    total_categories = sum(len(cats) for cats in grouped.values())

    total = len(rows)
    type_counts = Counter(r["source_type"] for r in rows)
    type_summary = ", ".join(f"{n} {t}" for t, n in type_counts.most_common())

    lines = ["# Content Catalog\n"]
    lines.append(f"_Last updated: {date.today().isoformat()}_\n")
    lines.append(f"**{total} entr{'ies' if total != 1 else 'y'}** ({type_summary}) across "
                 f"{len(grouped)} domain{'s' if len(grouped) != 1 else ''}, "
                 f"{total_categories} categor{'ies' if total_categories != 1 else 'y'}.\n")

    for dom in sorted(grouped.keys()):
        cats = grouped[dom]
        lines.append(f"\n## {dom.capitalize()}")
        for cat in sorted(cats.keys()):
            cat_rows = cats[cat]
            emoji = EMOJI_MAP.get(cat, "📄")
            lines.append(f"\n### {emoji} {cat.capitalize()} ({len(cat_rows)})\n")
            has_series = any(r.get("series") for r in cat_rows)
            if has_series:
                lines.append("| ID | Date | Title | Series | Type | Duration | Source |")
                lines.append("|----|------|-------|--------|------|----------|--------|")
            else:
                lines.append("| ID | Date | Title | Type | Duration | Source |")
                lines.append("|----|------|-------|------|----------|--------|")
            for r in cluster_rows(cat_rows):
                title = md_cell(r["title"])
                title_link = f"[{title}]({r['url']})" if r["url"] else title
                series_col = (f"| {md_cell(r.get('series', '')) or '-'} "
                              if has_series else "")
                lines.append(
                    f"| {r['id']} | {r['date']} | {title_link} {series_col}| {r['type']} "
                    f"| {format_duration(r['duration'])} | {md_cell(r['channel']) or '-'} |"
                )

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Index rebuilt at {rel(INDEX_PATH)}")
    print(f"  {total} entries ({type_summary}) in {len(grouped)} domains, {total_categories} categories")

    for p in unparseable:
        print(f"  WARNING: unparseable frontmatter, not indexed: {rel(p)}", file=sys.stderr)
    for p in missing_id:
        print(f"  WARNING: entry has no id (shows as '??'): {rel(p)}", file=sys.stderr)
    if unparseable or missing_id:
        print("  Run `verify` for the full integrity report.", file=sys.stderr)


# ── Verify (I7: invariant audit) ───────────────────────────────────────────

def _find_dash_violations(body: str, rpath: Path,
                          exempt_fenced_hyphens: bool = False) -> list[str]:
    """Check for em dashes and `--` in non-exempt parts of an entry (D-12/D-25).

    Both forms are banned: a real em dash (the primary target, the character
    itself) and the literal `--` a partner model emits in its place. Per D-25,
    this now includes verbatim fenced blocks (## Full Text): the transcript
    itself is no longer exempt from the dash rule, only from wording changes
    (D-8 still applies to substance, not punctuation). Exempts: YAML
    frontmatter (--- fences), markdown table separator lines (|---). archive/
    entries are never passed here because scan_catalog skips them.

    exempt_fenced_hyphens is the references/ mode: reference entries
    legitimately quote CLI flags (`--check`) inside fenced code blocks, so
    `--` is skipped there; em dashes stay banned everywhere.
    """
    problems: list[str] = []
    in_frontmatter = False
    frontmatter_seen = 0  # 0=none, 1=in, 2=exited
    in_fence = False

    for lineno, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()

        # Track YAML frontmatter boundaries (first two --- lines)
        if stripped == "---" and frontmatter_seen < 2:
            frontmatter_seen += 1
            in_frontmatter = (frontmatter_seen == 1)
            continue

        if in_frontmatter:
            continue

        if exempt_fenced_hyphens and stripped.startswith("```"):
            in_fence = not in_fence

        # Skip markdown table separator lines like |---|---|
        if re.match(r"^[\s\|:\-]+$", stripped):
            continue

        if "—" in stripped:
            problems.append(f"  D-12 violation: em dash `—` at {rpath}:{lineno}")
        if "--" in stripped and not (exempt_fenced_hyphens and in_fence):
            problems.append(f"  D-12 violation: double-hyphen `--` at {rpath}:{lineno}")

    return problems


def cmd_verify() -> int:
    """Audit storage invariants (I7) and D-12 em-dash/double-hyphen violations.

    Scans transcripts/ fully, and references/ for the checks that apply to
    reference entries: frontmatter parseability, id integrity (shared with
    the transcript id space, the NC-0034 collision class), and D-12 dashes
    with fenced code exempt from the `--` check only. References carry
    analysis, not transcripts, so no Full Text or folder-drift checks.
    Returns process exit code."""
    entries = scan_catalog()
    problems: list[str] = []
    warnings: list[str] = []
    seen_ids: dict[str, Path] = {}
    seen_keys: dict[tuple, Path] = {}

    for cat, dom in CATEGORY_DOMAIN.items():
        if dom not in KNOWN_DOMAINS:
            problems.append(f"stale domain mapping: CATEGORY_DOMAIN['{cat}'] = '{dom}', "
                            f"not in KNOWN_DOMAINS (D-14/D-17)")

    for e in entries:
        path, fm = e["path"], e["fm"]
        rpath = rel(path)

        if fm is None:
            problems.append(f"unparseable frontmatter: {rpath}")
            continue

        eid = str(fm.get("id", ""))
        if not re.match(rf"^{CATALOG_PREFIX}-\d{{4}}$", eid):
            problems.append(f"missing/malformed id: {rpath}")
        elif eid in seen_ids:
            problems.append(f"duplicate id {eid}: {rpath} and {rel(seen_ids[eid])}")
        else:
            seen_ids[eid] = path

        key = content_key(fm)
        if key:
            if key in seen_keys:
                warnings.append(f"duplicate content {key}: {rpath} and {rel(seen_keys[key])}")
            else:
                seen_keys[key] = path

        cats = fm.get("categories", [])
        primary = cats[0] if isinstance(cats, list) and cats else str(cats)
        if primary and primary != path.parent.name:
            problems.append(f"category/folder drift: {rpath} "
                            f"(frontmatter '{primary}' vs folder '{path.parent.name}')")
        if primary and primary not in KNOWN_CATEGORIES:
            problems.append(f"unknown category '{primary}' not in CATEGORY_RULES (D-17/D-18): {rpath}")

        # Transcript fence integrity: the known external-edit corruption mode
        # is destroying the fenced transcript or merging its heading into a fence.
        body = path.read_text(encoding="utf-8")
        headings = list(TRANSCRIPT_HEADING.finditer(body))
        if not headings:
            problems.append(f"no transcript section (## Full Text or variant): {rpath}")
        else:
            inner = re.search(r"^```[^\n]*\n(.*?)^```", body[headings[-1].end():], re.S | re.M)
            if not inner or not inner.group(1).strip():
                problems.append(f"transcript block broken or empty: {rpath}")

        problems.extend(_find_dash_violations(body, rpath))

    for s, cats in series_conflicts(entries).items():
        problems.append(f"series '{s}' split across category folders: "
                        f"{', '.join(cats)} (a series clusters in one folder)")

    ref_count = 0
    if REFERENCES_DIR.exists():
        for path in sorted(REFERENCES_DIR.rglob("*.md")):
            ref_count += 1
            rpath = rel(path)
            fm = read_frontmatter(path)
            if fm is None:
                problems.append(f"unparseable frontmatter: {rpath}")
                continue
            eid = str(fm.get("id", ""))
            if not re.match(rf"^{CATALOG_PREFIX}-\d{{4}}$", eid):
                problems.append(f"missing/malformed id: {rpath}")
            elif eid in seen_ids:
                problems.append(f"duplicate id {eid}: {rpath} and {rel(seen_ids[eid])}")
            else:
                seen_ids[eid] = path
            body = path.read_text(encoding="utf-8")
            problems.extend(_find_dash_violations(body, rpath,
                                                  exempt_fenced_hyphens=True))

    print(f"Checked {len(entries)} entries, {ref_count} references.")
    for w in warnings:
        print(f"  warning: {w}")
    if problems:
        for p in problems:
            print(f"  PROBLEM: {p}")
        print(f"{len(problems)} invariant violation(s).")
        return 1
    print("OK: all storage invariants hold.")
    return 0


# ── CLI commands ───────────────────────────────────────────────────────────

def apply_series(entries: list[dict], guessed: list[str],
                 series: str | None) -> list[str]:
    """Cluster with the series' existing folder, announcing an override."""
    if not series:
        return guessed
    known = series_category(entries, series)
    resolved = resolve_categories(guessed, known)
    if resolved[0] != guessed[0]:
        print(f"  Series '{series}' already lives in {resolved[0]}, "
              f"filing there (guess was {guessed[0]})")
    return resolved


def cmd_add_youtube(url: str, force: bool = False, topics: str | None = None,
                    series: str | None = None):
    """Fetch a YouTube transcript, categorize, save, update index, one scan."""
    video_id = extract_video_id(url)
    if not video_id:
        print(f"ERROR: Could not extract video ID from URL: {url}")
        sys.exit(1)

    entries = scan_catalog()
    if not force:
        dup = find_duplicate(entries, ("youtube", video_id))
        if dup:
            print(f"Already in catalog: {dup['path'].name} (ID: {dup['fm'].get('id', '?')})")
            print("  Use --force to add again")
            return

    print(f"Fetching transcript for video ID: {video_id}")
    meta = fetch_metadata(video_id)
    title, channel, duration = meta["title"], meta["channel"], meta["duration"]
    print(f"  Title: {title}")
    print(f"  Channel: {channel}")
    if not title:
        print("  (no metadata retrieved, using video ID)")

    try:
        text = fetch_transcript(video_id)
    except TranscriptUnavailable as e:
        print(f"ERROR: Transcript not available: {e}")
        sys.exit(1)

    categories = apply_series(entries, guess_category(text, title), series)
    print(f"  Categories: {', '.join(categories)}")
    cat_id = next_catalog_id(entries)
    print(f"  ID: {cat_id}")

    filepath = save_entry({
        "id": cat_id,
        "title": title,
        "url": url,
        "video_id": video_id,
        "channel": channel,
        "duration": duration,
        "source_type": "youtube",
        "text": text,
        "categories": categories,
        "topics": topics,
        "series": series,
    })
    print(f"  Saved: {rel(filepath)}")
    finish_add(entries, filepath, cat_id)


def cmd_add_social(url: str, source_type: str = "instagram",
                   topics: str | None = None, series: str | None = None):
    """Add a social media post (Instagram/TikTok), metadata + description only."""
    entries = scan_catalog()
    dup = find_duplicate(entries, ("url", normalize_url(url)))
    if dup:
        print(f"Already in catalog: {dup['path'].name} (ID: {dup['fm'].get('id', '?')})")
        return

    print(f"Fetching {source_type} post metadata...")
    meta = extract_social_metadata(url)
    title, channel = meta["title"], meta["channel"]
    duration = int(meta["duration"])
    text = meta.get("description", "")
    print(f"  Title: {title}")
    print(f"  Channel: {channel}")

    if not title and not text:
        print("  Could not extract content from this post.")
        print("  The platform may require browser cookies for access.")
        return

    categories = apply_series(entries, guess_category(text, title), series)
    print(f"  Categories: {', '.join(categories)}")
    cat_id = next_catalog_id(entries)
    print(f"  ID: {cat_id}")

    filepath = save_entry({
        "id": cat_id,
        "title": title,
        "url": url,
        "channel": channel,
        "duration": duration,
        "source_type": source_type,
        "text": text,
        "categories": categories,
        "topics": topics,
        "series": series,
    })
    print(f"  Saved: {rel(filepath)}")
    finish_add(entries, filepath, cat_id)


def cmd_add_pdf(pdf_path: str, topics: str | None = None,
                series: str | None = None):
    """Extract text from a PDF, categorize, save, update index, one scan."""
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    entries = scan_catalog()
    dup = find_duplicate(entries, ("pdf", str(pdf_file.resolve())))
    if dup:
        print(f"Already in catalog: {dup['path'].name} (ID: {dup['fm'].get('id', '?')})")
        return

    print(f"Extracting text from: {pdf_file.name}")
    result = extract_pdf_text(str(pdf_file))
    text, pages = result["text"], result["pages"]
    print(f"  Pages: {pages}")
    print(f"  Words: {len(text.split())}")

    title = pdf_file.stem
    first_line = text.split("\n")[0].strip() if text else ""
    if first_line and len(first_line) < 200:
        title = first_line.strip(".# \t")

    categories = apply_series(entries, guess_category(text, title), series)
    print(f"  Categories: {', '.join(categories)}")
    cat_id = next_catalog_id(entries)
    print(f"  ID: {cat_id}")

    filepath = save_entry({
        "id": cat_id,
        "title": title,
        "url": f"file://{pdf_file.resolve()}",
        "file_path": str(pdf_file.resolve()),
        "source_type": "pdf",
        "pdf_pages": pages,
        "text": text,
        "categories": categories,
        "topics": topics,
        "series": series,
    })
    print(f"  Saved: {rel(filepath)}")
    finish_add(entries, filepath, cat_id)


def finish_add(entries: list[dict], filepath: Path, cat_id: str):
    """Round-trip the new file, append it to the scan, rebuild the index."""
    new_fm = read_frontmatter(filepath)
    if not new_fm or str(new_fm.get("id", "")) != cat_id:
        print(f"ERROR: saved entry failed round-trip parse: {filepath}", file=sys.stderr)
    entries.append({"path": filepath, "fm": new_fm})
    build_index(entries)


def cmd_list():
    """List all catalog entries."""
    entries = scan_catalog()
    rows = [e["fm"] for e in entries if e["fm"]]
    skipped = len(entries) - len(rows)

    if not rows:
        print("No entries found.")
        return

    print(f"{'ID':<10} {'Title':<55} {'Type':<10} {'Category':<20} {'Date':<12}")
    print("-" * 110)
    for fm in sorted(rows, key=lambda f: str(f.get("id", "??"))):
        cats = fm.get("categories", [])
        cat_str = cats[0] if isinstance(cats, list) and cats else str(cats)
        title = (fm.get("title", "Untitled") or "Untitled")[:52]
        print(f"{str(fm.get('id', '??')):<10} {title:<55} {fm.get('source_type', 'youtube'):<10} "
              f"{str(cat_str):<20} {str(fm.get('date_added', '')):<12}")
    if skipped:
        print(f"\n  WARNING: {skipped} file(s) with unparseable frontmatter, run `verify`.",
              file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Content catalog tool")
    parser.add_argument("command", nargs="?", choices=["add", "rebuild", "list", "verify"],
                        help="Command")
    parser.add_argument("--pdf", help="Add a PDF file", metavar="PATH")
    parser.add_argument("--topics", metavar='"PHRASE"',
                        help='Topic(s) for the filename slug (D-13), e.g. '
                             '"reticulum, off-grid mesh networking"; '
                             'defaults to the source title')
    parser.add_argument("--series", metavar='"NAME"',
                        help='Series this entry belongs to, e.g. "3b1b deep '
                             'learning"; later parts file into the same '
                             'category folder and cluster in the dashboard')
    parser.add_argument("--force", action="store_true",
                        help="Add even if the source already exists (YouTube only)")
    parser.add_argument("url", nargs="?", help="YouTube/Instagram/TikTok URL")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "add":
        if args.pdf:
            cmd_add_pdf(args.pdf, topics=args.topics, series=args.series)
        elif args.url:
            src_type = detect_source_type(args.url)
            if src_type == "youtube":
                cmd_add_youtube(args.url, force=args.force, topics=args.topics,
                                series=args.series)
            elif src_type in ("instagram", "tiktok"):
                cmd_add_social(args.url, source_type=src_type,
                               topics=args.topics, series=args.series)
            else:
                print(f"Unknown source type for URL: {args.url}")
                print("  Supported: YouTube, Instagram, TikTok")
                sys.exit(1)
        else:
            print("ERROR: Provide a URL or --pdf <path>")
            print((__doc__ or "").strip())
            sys.exit(1)
    elif args.command == "rebuild":
        build_index()
    elif args.command == "list":
        cmd_list()
    elif args.command == "verify":
        sys.exit(cmd_verify())


if __name__ == "__main__":
    main()
