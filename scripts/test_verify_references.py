"""R-15 vectors for verify covering references/ (written before the implementation).

Expected: cmd_verify scans references/*.md in addition to transcripts/:
frontmatter must parse, ids must be well-formed and unique ACROSS both
trees (the NC-0034 collision class), em dashes are flagged anywhere, and
`--` is flagged only outside fenced code blocks (references legitimately
quote CLI flags; transcripts keep the stricter D-25 rule). References
carry analysis, not transcripts, so no `## Full Text` section is required
and no category/folder drift applies. Stdlib-only; writes to a temp dir,
never touches the catalog. Run: python3 scripts/test_verify_references.py
"""
import contextlib
import importlib.util
import io
import sys
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "transcript", Path(__file__).resolve().parent / "transcript.py")
assert spec is not None and spec.loader is not None
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

GOOD_TRANSCRIPT = """---
id: "NC-0001"
title: "A neural network lecture"
source_type: "youtube"
url: "https://youtube.com/watch?v=x"
video_id: "x"
categories: ["ai-ml"]
---

# A neural network lecture

## Full Text

```
plain transcript text with no banned punctuation
```
"""

def reference(eid: str, body: str) -> str:
    return f"""---
id: "{eid}"
title: "A reference note"
kind: "review"
source_type: "tool"
categories: ["networking"]
---

{body}
"""

VECTORS = [
    # (name, reference bodies keyed by filename, expected exit code)
    ("clean reference passes",
     {"NC-0002_clean.md": reference("NC-0002", "Plain analysis text.")}, 0),
    ("em dash in reference prose fails",
     {"NC-0002_dash.md": reference("NC-0002", "An em dash — right here.")}, 1),
    ("double hyphen in reference prose fails",
     {"NC-0002_hyphen.md": reference("NC-0002", "A pause -- like this.")}, 1),
    ("CLI flag inside fenced code is exempt",
     {"NC-0002_fence.md": reference(
         "NC-0002", "Run the check:\n\n```bash\npython3 scripts/next-id.py --check\n```")}, 0),
    ("em dash inside fenced code still fails",
     {"NC-0002_fdash.md": reference(
         "NC-0002", "```\nquoted — output\n```")}, 1),
    ("cross-tree id collision fails",
     {"NC-0001_steal.md": reference("NC-0001", "Claims the transcript's id.")}, 1),
    ("unparseable frontmatter fails",
     {"NC-0003_broken.md": "no frontmatter at all\n"}, 1),
    ("missing Full Text is fine for references",
     {"NC-0004_nofulltext.md": reference("NC-0004", "Analysis only, no transcript.")}, 0),
]

fails = 0
for i, (name, refs, expected) in enumerate(VECTORS, 1):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        setattr(t, "TRANSCRIPTS_DIR", root / "transcripts")
        setattr(t, "REFERENCES_DIR", root / "references")
        setattr(t, "INDEX_PATH", root / "000-dashboard" / "Index.md")
        (root / "transcripts" / "ai-ml").mkdir(parents=True)
        (root / "transcripts" / "ai-ml" / "NC-0001_lecture.md").write_text(
            GOOD_TRANSCRIPT, encoding="utf-8")
        (root / "references").mkdir()
        for fname, content in refs.items():
            (root / "references" / fname).write_text(content, encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            got = t.cmd_verify()
        ok = got == expected
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} v{i}: {name} -> exit {got}"
              + ("" if ok else f"  (expected {expected})"))
        if not ok:
            print("      " + out.getvalue().replace("\n", "\n      ").rstrip())

print("GREEN" if not fails else "RED", f"({fails} failing)")
sys.exit(1 if fails else 0)
