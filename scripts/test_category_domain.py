"""R-15 vectors for CATEGORY_DOMAIN (written alongside the fix that found it stale).

Regression guard for the class of bug that resurrected the D-14-retired `it`
domain: `tech` must resolve to `engineering`, and no CATEGORY_DOMAIN value may
point outside KNOWN_DOMAINS. Stdlib-only. Run:
    python3 scripts/test_category_domain.py
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "transcript", Path(__file__).resolve().parent / "transcript.py")
assert spec is not None and spec.loader is not None
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

fails = 0

# v1: tech must resolve to engineering, not the D-14-retired `it` domain.
got = t.CATEGORY_DOMAIN.get("tech")
ok = got == "engineering"
fails += not ok
print(f"{'PASS' if ok else 'FAIL'} v1: CATEGORY_DOMAIN['tech'] -> {got}"
      + ("" if ok else "  (expected engineering)"))

# v2: every mapped domain is live (D-14/D-17); catches the next stale mapping
# the same way, before it ever reaches a rebuild.
stale = {cat: dom for cat, dom in t.CATEGORY_DOMAIN.items() if dom not in t.KNOWN_DOMAINS}
ok = not stale
fails += not ok
print(f"{'PASS' if ok else 'FAIL'} v2: all CATEGORY_DOMAIN values in KNOWN_DOMAINS"
      + ("" if ok else f"  (stale: {stale})"))

print("GREEN" if not fails else "RED", f"({fails} failing)")
sys.exit(1 if fails else 0)
