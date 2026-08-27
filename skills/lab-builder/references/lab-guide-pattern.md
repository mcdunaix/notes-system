# Lab Guide Pattern: The Accessible Shape

This is `lab-builder` Phase 3's one output shape (per the brief's Design
decision 1). It originated in the `lecture-walkthrough` skill, where it was
first discovered while building the Reticulum ladder's L0 guide, and now
lives only here. It repurposes the lecture-walkthrough
structure template (Hook, Core Idea, Toolbox, Architecture, Results, Punchline)
as a skeleton for hands-on lab guides, for audiences who learn by building.

This is not a catalog entry: it is an instructional document that ends with
the reader having built something real.

## Section mapping

| Walkthrough section | Lab guide equivalent | What it does |
|---|---|---|
| **1. The Hook** | **The Hook** | The one question the lab answers. Names the concrete payoff, not the abstract importance. |
| **2. The Core Idea** | **Core Idea** | One analogy, carried all the way. Define what this rung proves. |
| **3. Toolbox** | **Toolbox (glossary table)** | Define every term before any step uses it. Plain meaning first, term in parens, what it does in THIS lab. |
| **4. Architecture** | **What You Will Build** | ASCII or mermaid diagram of the system. One-paragraph summary of the whole flow. |
| **5. Results / Surprising Facts** | **Step by Step** (numbered) | Each step is exactly one action plus command plus "you should see" checkpoint plus "what that means" plain-language debrief. |
| **6. The Punchline** | **What Just Happened** | Numbered facts of what was proved. Table of real-run numbers. |
| (none) | **The Bigger Picture** | Loops back to the hook. Names what was NOT needed. Foreshadows the next rung. |
| **References** | **Troubleshooting** | Symptom / cause / fix table. Seed with the real failures hit while testing. |
| (none) | **Stretch Goal** | One optional extension, no new purchases. |

The eight-block contract (`eight-block-contract.md`) maps onto this shape by
substance: see that file for exactly which two blocks (Learning objectives,
Prerequisites checklist) fold in as collapsed callouts rather than getting
their own narrative section.

## Key design rules for the lab guide version

- **Each step is ONE action.** Install, configure, start, announce, send,
  prove. Not a group of actions. The reader is never more than one step from
  a known-good state.
- **Every checkpoint has a "what that means" block.** Translate the terminal
  output back to the core-idea analogy. This is where learning happens.
- **The Toolbox table goes before the steps.** Not after, not inline.
  Readers need the vocabulary before they encounter it in commands. Three
  columns: term, plain meaning, what it does in this lab.
- **Real run record with the bug.** Include the failure from the first test
  run, prominently, in the troubleshooting table, not a footnote. For a
  young audience this is not just verification, it is the strongest trust
  signal in the document (see `gen-z-science-communication.md`, finding 3).
- **Define everything.** No assumed knowledge about the domain's basics. A
  glossary table is mandatory.
- **One analogy, start to finish.** If the spine analogy is a postal system,
  every concept maps to it consistently. Do not switch analogies mid-guide.
- **Black box the hardest prerequisite.** Every technical concept has one
  piece that requires half a different field to truly understand
  (cryptography, signal processing, kernel internals). Abstract that piece
  into a labeled black box. Tell the reader what the box produces, never
  explain how it works inside. Give the box a single clear name. The reader
  copies the output and trusts the box. This is not dumbing down, it is scope
  control. The box can be opened in a later, more advanced guide.

  **Worked example, from `L0-own-your-network.md`** (this and the other lab
  guides cited in this file are artifacts in the author's private vault, not
  shipped in this repo): the Identity encapsulates
  key generation, hashing, signing, and encryption. The student sees only the
  32-character hash and the label "a black box on your machine that says 'I
  am this machine and I can prove it.'" No reference to specific cryptographic
  algorithms appears anywhere in the guide.

- **Pick a motivational frame the learner lives inside.** The lab's own
  narrative must carry the motivation, not an external video, not a preamble
  paragraph. The opening hook names a felt problem the reader has experienced
  but could not name. Three frames, named in the focus statement's
  `pedagogical_angle`:

  - **Sovereignty / ownership.** The reader's daily tools are rented, not
    owned. Frames the lab as building an alternative. (`L0-own-your-network.md`:
    "Every message you have ever sent... crossed a machine that belongs to
    someone else.")
  - **Broken default.** Something the reader uses every day works wrong and
    they never knew why. Frames the lab as a fix.
  - **Hidden mechanism.** Something familiar, revealed. Frames the lab as a
    discovery.

  The frame named in the hook must echo in the closing section. If the hook
  says "you don't control the servers," the punchline says "nobody gave you
  permission to build this network. Nobody can take it away from you."
  (`L0-own-your-network.md`'s actual closing line.)

## Embedded software walkthroughs

When a lab depends on GUI software, the numbered steps must include a
detailed walkthrough of the software itself, not just "open the program and
configure it."

- **Open the program section.** Before any configuration steps, a "how to
  install and launch" subsection: exact URL, exact filename, any
  compatibility layer needed.
- **Click paths are steps.** Each dialog, each dropdown, each checkbox gets
  its own bullet. Bold the menu path and the named setting.
- **What-this-means for every parameter.** When the student enters a value,
  explain what it represents and why it matters.
- **Verification state after each config block.** Tell the student what
  should appear on screen after a group of settings.
- **Normal ranges for measurements.** List what a healthy value looks like
  and what common failure modes produce.
- **Screenshot substitutes.** Describe dialog layout and visual cues in
  prose, since screenshots cannot be embedded.

## Hardware lab considerations

When the lab involves physical circuits, measurement hardware, or
electronics assembly, the numbered steps must account for:

| Consideration | What the lab needs |
|---|---|
| **Circuit diagram** | ASCII schematic or a clear wiring list. |
| **Parts list (BOM)** | Table: part name, value or quantity, purpose, where to get it, optional vs required. |
| **Verification step** | A way to check the work before powering on (e.g. a multimeter reading). |
| **Safety note** | Max voltage/current, what to protect, what not to touch. |
| **Failure signatures** | What specific wrong readings or behaviors mean. |
| **Assembly order** | Wires first, then passives, then test points, then the device under test. |

## Provenance

This pattern emerged from building `L0-own-your-network.md` (Reticulum
networking lab) and `labs/speaker-design/L0-measure-driver.md` (speaker
design lab), combining the lecture-walkthrough structure template, plain-
language principles, and Gen Z science communication research. The hardware
lab rules were derived from the EE design pipeline characterize, model, mock,
measure, iterate, concretized through the speaker Thiele-Small parameter
measurement lab. Originally written for the `lecture-walkthrough` skill and
moved into this skill per the lab-builder brief's Suggested SKILL.md scaffold; the
collapsible-inline-compliance technique this file's section mapping now
assumes was proven after this pattern's original write, see
`eight-block-contract.md`.
