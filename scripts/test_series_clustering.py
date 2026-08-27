"""R-15 vectors for series clustering (written before the implementation).

A multi-part source (a lecture series, a course, a multi-video review) must
cluster: every entry added with the same --series files into the folder the
series already lives in, the series carries in frontmatter, the dashboard
lists series members contiguously, and verify fails when a series is split
across category folders by an external edit. Pure helpers under test:

  series_category(entries, series) -> the series' primary category, or None
  resolve_categories(guessed, series_cat) -> categories with the series'
      folder forced primary, guessed secondaries kept
  cluster_rows(cat_rows) -> rows sorted so series members are contiguous,
      each block anchored at its lowest member id
  series_conflicts(entries) -> {series: [categories]} for split series only

Plus save_entry: a "series" key round-trips through frontmatter.
Stdlib-only; writes to a temp dir, never touches the vault.
Run: python3 scripts/test_series_clustering.py
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


def entry(id_, series=None, primary="ai-ml"):
    fm = {"id": id_, "categories": [primary, "science"]}
    if series:
        fm["series"] = series
    return {"path": Path(f"{id_}.md"), "fm": fm}


def row(id_, series=""):
    return {"id": id_, "title": "t", "type": "youtube", "url": "",
            "category": "ai-ml", "date": "2026-01-01", "duration": 0,
            "channel": "", "source_type": "youtube", "series": series}


fails = 0


def check(name, got, expected):
    global fails
    ok = got == expected
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {name}: {got!r}"
          + ("" if ok else f"  (expected {expected!r})"))


# V1: an existing series names its folder; an unseen series does not.
catalog = [entry("NC-0001"), entry("NC-0002", series="deep learning")]
check("v1a series_category finds the series folder",
      t.series_category(catalog, "deep learning"), "ai-ml")
check("v1b unseen series has no folder yet",
      t.series_category(catalog, "linear algebra"), None)
check("v1c unparseable entries are skipped",
      t.series_category([{"path": Path("x.md"), "fm": None}], "deep learning"),
      None)

# V2: the series' folder wins the primary slot, guessed secondaries survive.
check("v2a series folder overrides the guess",
      t.resolve_categories(["science", "ai-ml"], "ai-ml"),
      ["ai-ml", "science"])
check("v2b agreement changes nothing",
      t.resolve_categories(["ai-ml", "science"], "ai-ml"),
      ["ai-ml", "science"])
check("v2c no series keeps the guess",
      t.resolve_categories(["science"], None), ["science"])
check("v2d secondaries stay capped at two",
      t.resolve_categories(["science", "programming", "hardware"], "ai-ml"),
      ["ai-ml", "science", "programming"])

# V3: dashboard rows cluster: series members contiguous, block anchored at
# its lowest id, standalone entries keep their id position.
clustered = t.cluster_rows([row("NC-0001"), row("NC-0002", "s"),
                            row("NC-0003"), row("NC-0004", "s")])
check("v3a series block is contiguous at first member",
      [r["id"] for r in clustered],
      ["NC-0001", "NC-0002", "NC-0004", "NC-0003"])
check("v3b no series means pure id order",
      [r["id"] for r in t.cluster_rows([row("NC-0002"), row("NC-0001")])],
      ["NC-0001", "NC-0002"])

# V4: a series split across category folders is a verify problem; a
# consistent series is not.
split = [entry("NC-0001", "s", "ai-ml"), entry("NC-0002", "s", "science")]
check("v4a split series is reported with both folders",
      t.series_conflicts(split), {"s": ["ai-ml", "science"]})
check("v4b consistent series is clean",
      t.series_conflicts([entry("NC-0001", "s"), entry("NC-0002", "s")]), {})

# V5: series round-trips through save_entry frontmatter.
with tempfile.TemporaryDirectory() as td:
    setattr(t, "TRANSCRIPTS_DIR", Path(td))
    saved = t.save_entry({
        "id": "NC-9001", "title": "Chapter 2", "source_type": "youtube",
        "url": "https://youtube.com/watch?v=x", "video_id": "x1",
        "channel": "c", "duration": 60, "text": "hello world",
        "categories": ["ai-ml"], "topics": "gradient descent",
        "series": "deep learning",
    })
    fm = t.read_frontmatter(saved) or {}
    check("v5 series survives the frontmatter round-trip",
          fm.get("series"), "deep learning")

print("GREEN" if not fails else "RED", f"({fails} failing)")
sys.exit(1 if fails else 0)
