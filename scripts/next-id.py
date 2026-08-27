#!/usr/bin/env python3
"""
Print the next free catalog ID (NC-XXXX) and, with --check, report any
collisions across the whole catalog.

Why this exists: `transcript.py` allocates IDs from live frontmatter in
transcripts/ plus the dashboard Index.md, but it has no awareness of
references/ (non-transcript research and artifact notes share the same NC
numbering convention per the storage protocol). That blind spot once caused
a live ID collision in the author's vault: a transcript entry and a
reference entry both claimed NC-0034 and nothing cross-checked them.
This helper scans both trees so the new skill modes (Review, Discussion,
Probe) that file into references/ can never collide with transcripts/.

Stdlib only, by design (same rule as transcript.py's rebuild/list/verify).

Usage:
  python3 scripts/next-id.py          # print next free ID, e.g. NC-0043
  python3 scripts/next-id.py --check  # verify no duplicates, exit 1 on collision
"""

import re
import sys
from pathlib import Path

CATALOG_PREFIX = "NC"
ID_PATTERN = re.compile(rf"\b{CATALOG_PREFIX}-(\d{{4}})\b")
FM_ID_PATTERN = re.compile(rf"^{CATALOG_PREFIX}-(\d+)$")

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = [ROOT / "transcripts", ROOT / "references"]
INDEX_PATH = ROOT / "000-dashboard" / "Index.md"


def collect() -> dict[str, list[str]]:
    """Return {id: [relative paths...]} for every NC id found anywhere."""
    found: dict[str, list[str]] = {}
    for d in SCAN_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            fm_id = _frontmatter_id(p)
            if fm_id:
                found.setdefault(fm_id, []).append(str(p.relative_to(ROOT)))
    if INDEX_PATH.exists():
        for m in ID_PATTERN.finditer(INDEX_PATH.read_text(encoding="utf-8")):
            found.setdefault(f"{CATALOG_PREFIX}-{m.group(1)}", []).append(
                str(INDEX_PATH.relative_to(ROOT)) + " (derived view)"
            )
    return found


def _frontmatter_id(path: Path) -> str | None:
    """Parse just the id: line from a YAML frontmatter block (naive, like transcript.py)."""
    try:
        head = path.read_text(encoding="utf-8")[:8192]
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    end = head.find("\n---", 3)
    if end < 0:
        return None
    for line in head[3:end].splitlines():
        m = re.match(r"\s*id\s*:\s*\"?([^\"]+?)\"?\s*$", line)
        if m and FM_ID_PATTERN.match(m.group(1).strip()):
            return m.group(1).strip()
    return None


def main() -> int:
    found = collect()
    if "--check" in sys.argv:
        collisions = {i: paths for i, paths in found.items() if len(paths) > 1}
        if collisions:
            for i, paths in sorted(collisions.items()):
                print(f"COLLISION {i}: " + " and ".join(paths))
            print(f"{len(collisions)} duplicate id(s).")
            return 1
        print(f"OK: {len(found)} unique ids, no collisions (transcripts/ + references/ + Index.md).")
        return 0

    nums = [int(i.removeprefix(f"{CATALOG_PREFIX}-")) for i in found]
    nxt = (max(nums) + 1 if nums else 1)
    print(f"{CATALOG_PREFIX}-{nxt:04d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
