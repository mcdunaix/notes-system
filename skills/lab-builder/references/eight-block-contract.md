# The Eight-Block Contract

Every lab guide `lab-builder` produces must satisfy these eight blocks, by
substance, not by literal section headers. Generalized from the Reticulum lab
ladder's own scaffolding contract (the notes vault's
`labs/reticulum/00-README.md`, "The guide template"), which proved this
structure across a planned five-rung ladder before this skill existed to
automate it.

## The eight blocks

1. **Learning objectives.** "After this lab you can explain X / do Y," 3-5
   bullets, testable.
2. **Concept primer.** Plain language, one analogy carried through the whole
   rung (the ladder's chosen motivational frame, from the focus statement's
   `pedagogical_angle`).
3. **Prerequisites checklist.** Prior rungs, parts with prices, accounts,
   money, a time box.
4. **Numbered steps.** Every step is one action with a copy-paste command (or
   a described physical action) followed by an "expected output" checkpoint.
   The learner is never more than one step from a known-good state. No step
   depends on undefined jargon.
5. **What just happened.** A short debrief connecting the demonstration back
   to the concept primer's thesis and to the specific source claim it
   reproduces.
6. **Troubleshooting table.** Symptom, likely cause, fix, seeded from real
   failures hit during the Phase 4 live run. Never invented in advance.
7. **Safety and legality box** (only when the lab involves RF transmission,
   mains voltage, or another real hazard). ISM-band rules, region settings,
   campus policy checks, whatever the specific hazard requires.
8. **Stretch goal.** One optional extension, no new purchases.

## Substance, not structure

Six of these eight blocks map onto the accessible guide shape's own sections
directly (see `lab-guide-pattern.md`): Concept primer maps to Core Idea,
Numbered steps to Step by Step, What just happened to Results, Troubleshooting
to Troubleshooting, Stretch goal to Stretch, and a Safety box, when the lab
needs one, stays inline. The two blocks without a natural narrative home,
Learning objectives and Prerequisites checklist, get folded in as **collapsed
Obsidian callouts** placed right after the intro, before the narrative starts:

```
> [!abstract]- Learning objectives
> After this lab you can:
> - ...

> [!todo]- Prerequisites checklist
> - **Prior rungs:** ...
> - **Hardware:** ...
> - **Software:** ...
> - **Accounts:** ... **Purchases:** ...
> - **Time box:** ...
```

A Safety and legality box, when the lab needs one, is the one exception: it
stays **uncollapsed** and inline, never behind a fold. Safety content should
never be a click away from being skipped.

Do not build a separate reference-shaped edition to satisfy this contract
literally. One guide, in the accessible shape, with the two orphan blocks
folded in, is a complete implementation of all eight blocks. A second edition
is produced only when `sibling_edition` is explicitly set in the focus
statement, the exception, never the default.

## Author rules

No em dashes anywhere in the guide, matching the catalog protocol's own D-12 even
though this skill lives outside that vault: a comma, a colon, or two
sentences instead, a plain hyphen for structural separators. Jargon gets a
one-line definition at first use, plus a glossary entry if the ladder has
one. The lab answers exactly one question, stated in its title block. Every
external technical claim carries a URL probed live during Phase 1, never
assumed from training knowledge.
