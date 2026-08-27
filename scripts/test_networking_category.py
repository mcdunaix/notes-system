"""R-15 vectors for the `networking` category (written before the code).

guess_category must send Reticulum/mesh and homelab/zero-trust content to
`networking` as the primary, without stealing ML or plain-programming
content (regression guards). Stdlib-only. Run:
    python3 scripts/test_networking_category.py
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
    ("The Internet, Reinvented.",
     "Reticulum is a cryptography-based networking stack for off-grid mesh "
     "networks. It runs over LoRa radio and packet radio, doing opportunistic "
     "routing with no fixed infrastructure. You can bridge it over TCP, build "
     "a mesh, and route traffic without any central server.",
     "networking"),
    ("Ditching the VPN for Twingate on Raspberry Pis",
     "Ditching the VPN for Twingate: zero trust access to my homelab. "
     "Self-hosted services on Raspberry Pis behind a secure mesh, no more "
     "WireGuard tunnels or firewall port-forwarding.",
     "networking"),
    # Regression: ML content must stay ai-ml, not get pulled to networking.
    ("But what is a neural network?",
     "A neural network learns deep learning by adjusting weights across layers "
     "of neurons; gradient descent trains the model on MNIST digits.",
     "ai-ml"),
    # Regression: plain programming stays programming.
    ("Python Tutorial 2026",
     "Learn Python programming: functions, data structures, the standard "
     "library, and debugging code in an IDE from the terminal.",
     "programming"),
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
