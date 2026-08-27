"""R-15 vectors for the `culture` category (written before the code, D-17).

guess_category must send indigenous/ancestral/heritage content to `culture`
as the primary, without stealing plain talks-interviews or ai-ml content
(regression guards). Stdlib-only. Run:
    python3 scripts/test_culture_category.py
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "transcript", Path(__file__).resolve().parent / "transcript.py")
assert spec is not None and spec.loader is not None
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

VECTORS = [
    # (title, text, expected primary category)
    ("The Happiest People I Know Stopped Rushing",
     "An indigenous elder explains decolonizing aging: ancestral traditions "
     "of care, oral history passed down through ceremony, and why western "
     "models of aging erase what elders actually teach.",
     "culture"),
    ("Grandmother's Kitchen: Preserving Culinary Heritage",
     "This documentary follows a family's culinary heritage and folklore, "
     "recipes carried through ritual and tradition across generations, "
     "resisting the erasure of colonialism.",
     "culture"),
    # Regression: a generic interview stays talks-interviews, culture
    # keywords must not fire on content that never mentions them.
    ("A Conversation with Joshua Doss",
     "In this podcast interview, Joshua discusses ideology as payment, "
     "a fireside chat about community, economics, and belief systems.",
     "talks-interviews"),
    # Regression: ML content must stay ai-ml, not get pulled to culture.
    ("But what is a neural network?",
     "A neural network learns deep learning by adjusting weights across "
     "layers of neurons; gradient descent trains the model on MNIST digits.",
     "ai-ml"),
]

fails = 0
for i, (title, text, expected) in enumerate(VECTORS, 1):
    got = t.guess_category(text, title)[0]
    ok = got == expected
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} v{i}: {title[:34]!r} -> {got}"
          + ("" if ok else f"  (expected {expected})"))

print("GREEN" if not fails else "RED", f"({fails} failing)")
sys.exit(1 if fails else 0)
