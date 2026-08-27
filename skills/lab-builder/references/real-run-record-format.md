# Real-Run Record Format (R-15 gate)

Phase 4 (Verify and build) builds this section from the user's actual
execution. Extracted from the pattern proven in the notes vault's
`archive/labs/L0-rns-over-tcp.md` (superseded by `L0-own-your-network.md`,
which carries the same record forward; both are examples from the author's
private vault, not shipped in this repo), the first Reticulum rung built and
run for real.

## What this section states, in order

1. **Provenance of the expected outputs.** State plainly that the checkpoints
   in the numbered steps were written from primary sources (the protocol
   manual, the tool's own source code) before execution, not copied from a
   run. This is R-15 applied one level earlier: test vectors before the code
   runs.
2. **Run metadata.** Date, environment, versions of every tool involved.
3. **Honest failure, if there was one.** If a first attempt failed, say so
   plainly and describe what actually happened. Never silently discard a
   failed run and show only the clean one. Fold the fix into the
   Troubleshooting table (the eight-block contract's block 6), not just
   narrated here.
4. **Real terminal output, verbatim, in fenced code blocks.** Not
   paraphrased, not reconstructed from memory. Paste what the terminal
   actually printed.
5. **A gate-check sentence.** Closes the section by connecting the real
   numbers back to the rung's stated question, the one named in the Hook.

## Worked example (abbreviated, from L0-own-your-network.md)

> The expected outputs above were written from the Reticulum manual and the
> Echo.py source before execution; this section records the real run that
> validated them.
>
> Run: 2026-07-10, macOS... Run 1 failed the step 9 gate honestly: the echo
> appeared to work, but `rnstatus` showed the TCP server interface with
> `Clients : 0`... The vector caught it; the variant box's port lines are the
> fix, now in the troubleshooting table. Run 2, actual outputs: [fenced
> terminal output blocks follow]... Gate check: message delivered over the
> TCP interface, client sent 331 B against server received 326 B,
> `Clients : 1`, round trip proven cryptographically in 1.645 ms.

## Why this section is load-bearing, not decoration

Per `gen-z-science-communication.md` finding 3, institutional authority lands
weakly with this audience. A real, honestly-included failure, the port
collision that broke Run 1, carries more trust than a polished, failure-free
account would. This section is the guide's primary trust signal, not
methodology filed away at the end.

## Gate

Phase 4 never publishes a guide without this section fully populated with
real output. A guide whose Real-run record still reads "Pending: awaiting
user execution and evidence" (Phase 3's placeholder) is not finished, no
matter how complete the rest of the guide is.
