"""R-15 vectors for ai-ml classification of neural-network lectures.

Found live: the canonical intro lecture (3Blue1Brown, "But what is a neural
network?") filed under science, because `neuron` and `mathematics` outscored
the ai-ml list, which lacked the deep-learning working vocabulary
(backpropagation, gradient descent, activation function, layers, MNIST).
Expected: a neural-network lecture classifies ai-ml primary; a genuine
neuroscience text still classifies science. Stdlib-only. Run:
    python3 scripts/test_ai_ml_category.py
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "transcript", Path(__file__).resolve().parent / "transcript.py")
assert spec is not None and spec.loader is not None
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)

# Term frequencies mirror the real lecture: `neuron` dominates raw counts
# (19 hits live), and the working vocabulary is weights / activations /
# sigmoid / biases, not the phrase "machine learning".
NN_LECTURE = (
    "This is a neural network. Each neuron holds a number, and a neuron "
    "passes its value forward. When one neuron activates, the next neuron "
    "reads it: neuron to neuron to neuron, one neuron at a time. Those "
    "activations flow through weights, and the weights plus biases decide "
    "the activations of the next layer. A sigmoid squishes the weighted sum, "
    "so the weights matter twice. Gradient descent with backpropagation "
    "adjusts the weights, the biases, and every hidden layer until the "
    "network reads handwritten digits from the MNIST dataset. The "
    "mathematics is matrix multiplication and a sigmoid."
)

NEURO_TEXT = (
    "In neuroscience, a neuron fires when synaptic input on a dendrite "
    "crosses threshold. Changes in synapse strength underlie the biology of "
    "memory; the study found cellular and molecular changes across the brain."
)

VECTORS = [
    # (name, title, text, expected primary category)
    ("neural-network lecture is ai-ml",
     "But what is a neural network? | Deep learning chapter 1",
     NN_LECTURE, "ai-ml"),
    ("neuroscience text stays science",
     "How real neurons store memories", NEURO_TEXT, "science"),
]

fails = 0
for i, (name, title, text, expected) in enumerate(VECTORS, 1):
    got = t.guess_category(text, title)[0]
    ok = got == expected
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} v{i}: {name} -> {got}"
          + ("" if ok else f"  (expected {expected})"))

print("GREEN" if not fails else "RED", f"({fails} failing)")
sys.exit(1 if fails else 0)
