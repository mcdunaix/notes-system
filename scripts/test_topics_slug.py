"""R-15 vectors for D-13 topic slugs (written before the implementation).

Expected: the filename slug comes from entry_data["topics"] when present
(slugified), else falls back to the source title, else bare id. When topics
are given they round-trip through frontmatter. Stdlib-only; writes to a
temp dir, never touches the vault. Run: python3 scripts/test_topics_slug.py
"""
import importlib.util
import sys
import tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "transcript", Path(__file__).resolve().parent / "transcript.py")
assert spec is not None and spec.loader is not None
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

VECTORS = [
    # (topics, title, expected filename)
    ("Reticulum off-grid mesh networking", "The Internet, Reinvented.",
     "NC-9001_reticulum-off-grid-mesh-networking.md"),      # topics beat title
    ("dendritic learning, synaptic plasticity",
     "Why Different Neuron Parts Learn Differently?",
     "NC-9002_dendritic-learning-synaptic-plasticity.md"),  # commas collapse
    (None, "The Internet, Reinvented.",
     "NC-9003_the-internet-reinvented.md"),                 # fallback: title
    (None, "", "NC-9004.md"),                               # fallback: bare id
]

fails = 0
with tempfile.TemporaryDirectory() as td:
    setattr(t, "TRANSCRIPTS_DIR", Path(td))
    for i, (topics, title, expected) in enumerate(VECTORS, 1):
        entry = {
            "id": f"NC-{9000 + i:04d}", "title": title, "source_type": "youtube",
            "url": "https://youtube.com/watch?v=x", "video_id": f"x{i}",
            "channel": "c", "duration": 60, "text": "hello world",
            "categories": ["tech"], "topics": topics,
        }
        got = t.save_entry(entry).name
        ok = got == expected
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} v{i}: topics={topics!r} -> {got}"
              + ("" if ok else f"  (expected {expected})"))
        if topics:
            fm = t.read_frontmatter(t.TRANSCRIPTS_DIR / "tech" / got) or {}
            ok2 = fm.get("topics") == topics
            fails += not ok2
            print(f"{'PASS' if ok2 else 'FAIL'} v{i}b: topics round-trip frontmatter")

print("GREEN" if not fails else "RED", f"({fails} failing)")
sys.exit(1 if fails else 0)
