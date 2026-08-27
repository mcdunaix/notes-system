"""R-15 vectors for the domain-then-category dashboard grouping (D-18).

build_index must group entries by Domain first, then Category within
Domain, via a pure group_by_domain(rows) helper, so 000-dashboard/Index.md
stays scannable "at a glance" as the Category count grows. Stdlib-only. Run:
    python3 scripts/test_dashboard_tiering.py
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "transcript", Path(__file__).resolve().parent / "transcript.py")
assert spec is not None and spec.loader is not None
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


def row(category, id_="NC-0001"):
    return {"id": id_, "title": "t", "type": "youtube", "url": "",
            "category": category, "date": "2026-01-01", "duration": 0,
            "channel": "", "source_type": "youtube"}


VECTORS = [
    # (rows, expected {domain: {category: count}})
    (
        [row("ai-ml"), row("networking"), row("programming"), row("talks-interviews")],
        {"engineering": {"ai-ml": 1, "networking": 1, "programming": 1},
         "culture-society": {"talks-interviews": 1}},
    ),
    (
        [row("culture"), row("culture"), row("talks-interviews")],
        {"culture-society": {"culture": 2, "talks-interviews": 1}},
    ),
    # Regression: a category with no CATEGORY_DOMAIN entry still surfaces,
    # under its own "uncategorized" bucket, rather than disappearing.
    (
        [row("uncategorized")],
        {"uncategorized": {"uncategorized": 1}},
    ),
]

fails = 0
for i, (rows, expected) in enumerate(VECTORS, 1):
    grouped = t.group_by_domain(rows)
    got = {dom: {cat: len(cat_rows) for cat, cat_rows in cats.items()}
           for dom, cats in grouped.items()}
    ok = got == expected
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} v{i}: {expected} -> {got}")

print("GREEN" if not fails else "RED", f"({fails} failing)")
sys.exit(1 if fails else 0)
