#!/usr/bin/env bash
# catalog-transcribe: deterministic transcript acquisition for the notes catalog.
#
# Usage:  catalog-transcribe <URL|audiofile> <output.txt> [duration_seconds]
#
# Order of attempts (first that produces >= MIN_WORDS wins):
#   1. subs           the source's own caption track via yt-dlp (eng-US/en, manual or auto)
#   2. whisper-local  ffmpeg -> 16 kHz mono WAV -> local whisper.cpp
#   3. whisper-mac    stream the WAV over ssh and run mlx_whisper there
#
# Exit codes:
#   0  transcript written, coverage >= 80% of a 150 wpm expectation
#   4  transcript written but coverage 60-80% (usable, MUST be disclosed in the reply)
#   5  transcript written but coverage < 60% (partial, MUST be disclosed)
#   3  no transcript at all (do NOT write a catalog entry as if it succeeded)
#
# Never call Google Web Speech / speech_recognition: it silently drops chunks on
# music-heavy audio, and it produced every partial transcript this catalog has
# had to repair by hand.
#
# Device configuration (kept out of the repo; set in the wrapper that installs
# this on PATH):
#   CATALOG_MAC        user@host to stream audio to for tier 3 (empty = skip)
#   CATALOG_WCLI       whisper.cpp binary (default: whisper-cli on PATH)
#   CATALOG_WMODEL     whisper.cpp model (.bin)
#   CATALOG_MLX        fallback path to mlx_whisper on the remote host
#   CATALOG_MLX_MODEL  model id for the remote mlx_whisper
set -uo pipefail

[ -n "${PREFIX:-}" ] && export PATH="$PREFIX/bin:$PATH"

WCLI=${CATALOG_WCLI:-$(command -v whisper-cli || echo "$HOME/whisper.cpp/build/bin/whisper-cli")}
WMODEL=${CATALOG_WMODEL:-$HOME/models/whisper/ggml-base.en.bin}
MAC=${CATALOG_MAC:-}
MLX_MODEL=${CATALOG_MLX_MODEL:-mlx-community/whisper-large-v3-turbo}
# Non-interactive ssh gets a minimal PATH, and mlx_whisper shells out to ffmpeg.
MAC_PATH=${CATALOG_MAC_PATH:-/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin}
MIN_WORDS=40
WPM=150

src="${1:-}"; out="${2:-}"; dur="${3:-0}"
if [ -z "$src" ] || [ -z "$out" ]; then
  echo "usage: catalog-transcribe <URL|audiofile> <output.txt> [duration_seconds]" >&2
  exit 2
fi

TMP=$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/ct.$$")
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

srt_to_text() {  # $1 = .srt  -> stdout text (dedup, timestamps+indices stripped)
  python3 - "$1" <<'PY'
import re, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
seen, out = set(), []
for block in re.split(r"\n\s*\n", raw):
    lines = [l for l in block.splitlines()
             if l.strip() and not re.match(r"^\d+$", l.strip()) and "-->" not in l]
    t = re.sub(r"\s+", " ", " ".join(l.strip() for l in lines)).strip()
    if t and t not in seen:
        seen.add(t); out.append(t)
print(" ".join(out))
PY
}

SOURCE=""; TEXT=""

# ---------- 1. caption track ----------
if printf '%s' "$src" | grep -qE '^https?://'; then
  timeout 240 yt-dlp --no-warnings --skip-download \
    --write-subs --write-auto-subs --sub-langs "eng-US,en-US,en" --convert-subs srt \
    -o "$TMP/cap" "$src" >/dev/null 2>&1
  cap=$(ls "$TMP"/cap*.srt 2>/dev/null | head -1)
  if [ -n "${cap:-}" ]; then
    TEXT=$(srt_to_text "$cap")
    [ "$(printf '%s' "$TEXT" | wc -w)" -ge $MIN_WORDS ] && SOURCE=subs
  fi
fi

# ---------- 2. local whisper.cpp ----------
if [ -z "$SOURCE" ]; then
  audio=""
  if printf '%s' "$src" | grep -qE '^https?://'; then
    timeout 420 yt-dlp --no-warnings -f "download/bestaudio" -x --audio-format mp3 \
      -o "$TMP/dl.%(ext)s" "$src" >/dev/null 2>&1
    audio=$(ls "$TMP"/dl*.mp3 "$TMP"/dl*.m4a "$TMP"/dl* 2>/dev/null | grep -v '\.part$' | head -1)
  elif [ -f "$src" ]; then
    audio="$src"
  fi
  if [ -n "${audio:-}" ]; then
    # audio prep is independent of which ASR engine runs: both tiers need the WAV
    ffmpeg -hide_banner -loglevel error -y -i "$audio" -ar 16000 -ac 1 -c:a pcm_s16le "$TMP/a16.wav" 2>/dev/null
    if [ "$dur" = "0" ]; then
      dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$audio" 2>/dev/null | cut -d. -f1)
      dur=${dur:-0}
    fi
  fi
  if [ -f "$TMP/a16.wav" ] && [ -x "$WCLI" ] && [ -f "$WMODEL" ]; then
    timeout 900 "$WCLI" -m "$WMODEL" -f "$TMP/a16.wav" -otxt --no-timestamps \
      -of "$TMP/wout" >/dev/null 2>&1
    if [ -f "$TMP/wout.txt" ]; then
      TEXT=$(python3 -c "import re,sys; print(re.sub(r'\s+',' ',open(sys.argv[1]).read()).strip())" "$TMP/wout.txt")
      [ "$(printf '%s' "$TEXT" | wc -w)" -ge $MIN_WORDS ] && SOURCE=whisper-local
    fi
  fi
fi

# ---------- 3. remote mlx_whisper over ssh ----------
if [ -z "$SOURCE" ] && [ -f "${TMP}/a16.wav" ]; then
  if [ -z "$MAC" ]; then
    echo "note: tier 3 skipped, CATALOG_MAC is not set on this device" >&2
  else
    REMOTE="export PATH=$MAC_PATH:\$PATH; d=/tmp/mac_asr_\$\$; rm -rf \$d; mkdir -p \$d; cat > \$d/in.wav; m=\$(command -v mlx_whisper || echo ${CATALOG_MLX:-mlx_whisper}); \"\$m\" \$d/in.wav --model $MLX_MODEL --output-format txt --output-dir \$d --language en >/dev/null 2>&1; cat \$d/in.txt 2>/dev/null; rm -rf \$d"
    TEXT=$(ssh -o BatchMode=yes -o ConnectTimeout=8 "$MAC" "$REMOTE" \
      < "$TMP/a16.wav" 2>/dev/null | tr -s '[:space:]' ' ')
    [ "$(printf '%s' "$TEXT" | wc -w)" -ge $MIN_WORDS ] && SOURCE=whisper-mac
  fi
fi

# ---------- report ----------
if [ -z "$SOURCE" ]; then
  echo "TRANSCRIPT_SOURCE=none WORDS=0 DURATION=${dur} COVERAGE=0%"
  echo "NO TRANSCRIPT: tried the caption track, local whisper.cpp and the remote host. Do not file this entry as complete." >&2
  exit 3
fi

printf '%s\n' "$TEXT" > "$out"
words=$(printf '%s' "$TEXT" | wc -w)
cov=0
if [ "${dur:-0}" -gt 0 ] 2>/dev/null; then
  cov=$(python3 -c "print(round($words/(($dur/60)*$WPM)*100))" 2>/dev/null || echo 0)
else
  cov=100
fi
echo "TRANSCRIPT_SOURCE=$SOURCE WORDS=$words DURATION=${dur} COVERAGE=${cov}%"
if [ "$cov" -lt 60 ]; then
  echo "PARTIAL (<60% of expected): disclose the coverage in the reply and mark the Full Text block accordingly." >&2
  exit 5
fi
if [ "$cov" -lt 80 ]; then
  echo "THIN (60-80% of expected): disclose the coverage in the reply." >&2
  exit 4
fi
exit 0
