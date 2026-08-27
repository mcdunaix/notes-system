#!/usr/bin/env bash
# Install the repo's skills into ~/.hermes/skills/<category>/.
# Default: symlink (edits in the repo take effect immediately).
# Use --copy to copy instead (for hermetic installs).
#
# Usage:
#   ./scripts/install-skills.sh            # symlink all skills into productivity/
#   ./scripts/install-skills.sh --copy     # copy instead of symlink
#   ./scripts/install-skills.sh content-catalog   # one skill only
#
# Portable to bash 3.2 (macOS default): no mapfile, no declare -A.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$REPO_ROOT/skills"
HERMES_SKILLS="${HERMES_SKILLS:-$HOME/.hermes/skills}"
CATEGORY="productivity"
MODE="symlink"

# A missing ~/.hermes usually means Hermes is not installed yet. Installing
# anyway is harmless (the dir is created), but say so instead of guessing.
if [[ ! -d "$HERMES_SKILLS" ]]; then
    echo "NOTE: $HERMES_SKILLS does not exist yet (Hermes not installed, or a"
    echo "      first-time install). Creating it. The skills also work with any"
    echo "      agent pointed at this repo's skills/ directory."
fi

if [[ "${1:-}" == "--copy" ]]; then
    MODE="copy"
    shift
fi

# List skill directories (one per subdir of skills/).
SKILLS=()
for d in "$SRC_DIR"/*/; do
    [[ -d "$d" ]] && SKILLS+=("$(basename "$d")")
done

# Optional single-skill filter.
TARGETS=("${SKILLS[@]}")
if [[ $# -gt 0 ]]; then
    TARGETS=("$@")
fi

installed=0
for skill in "${TARGETS[@]}"; do
    src="$SRC_DIR/$skill"
    [[ -d "$src" ]] || { echo "SKIP (no such skill dir): $skill"; continue; }
    dest_dir="$HERMES_SKILLS/$CATEGORY"
    dest="$dest_dir/$skill"
    mkdir -p "$dest_dir"
    if [[ -L "$dest" || -e "$dest" ]]; then
        echo "SKIP (already exists): $skill -> $dest"
        continue
    fi
    if [[ "$MODE" == "copy" ]]; then
        cp -R "$src" "$dest"
        echo "COPIED: $skill -> $dest"
    else
        ln -s "$src" "$dest"
        echo "LINKED: $skill -> $dest"
    fi
    installed=$((installed + 1))
done

echo "Done. $installed installed into $HERMES_SKILLS/$CATEGORY/ (mode: $MODE)."
