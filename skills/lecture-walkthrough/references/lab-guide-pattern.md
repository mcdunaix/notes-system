# Lab Guide Pattern: Repurposing the Walkthrough Structure

The lecture-walkthrough structure template (Hook, Core Idea, Toolbox, Architecture,
Results, Punchline) can be directly repurposed as a skeleton for **hands-on lab
guides**, especially for audiences who learn by building.

This is not a catalog entry, it is an instructional document that ends with the
reader having built something real.

## When to use this pattern

You have a source video or concept (e.g., the Data Slayer Reticulum video, NC-0024)
and want to write a **do-this-yourself lab** that reproduces one or more of its
demos. The lab is not a walkthrough of the video; it is a step-by-step instruction
set that assumes the reader may or may not have seen the video.

## Section mapping

| Walkthrough section | Lab guide equivalent | What it does |
|---|---|---|
| **1. The Hook** | **The Hook** | The one question the lab answers. Names the concrete payoff, not the abstract importance. |
| **2. The Core Idea** | **Core Idea** | One analogy, carried all the way. Define what this rung proves. |
| **3. Toolbox** | **Toolbox (glossary table)** | Define every term before any step uses it. Plain meaning first, term in parens, what it does in THIS lab. |
| **4. Architecture** | **What You Will Build** | ASCII diagram of the system. One-paragraph summary of the whole flow. |
| **5. Results / Surprising Facts** | **Step by Step** (numbered) | Each step is exactly one action + command + "you should see" checkpoint + "what that means" plain-language debrief. |
| **6. The Punchline** | **What Just Happened** | Numbered facts of what was proved. Table of real-run numbers. |
| -- | **The Bigger Picture** | Loops back to the hook. Names what was NOT needed. Foreshadows the next rung. |
| **References** | **Troubleshooting** | Symptom / cause / fix table. Seed with the real failures hit while testing. |
| -- | **Stretch Goal** | One optional extension, no new purchases. |

## Key design rules for the lab guide version

- **Each step is ONE action.** Install, configure, start, announce, send, prove. Not
  a group of actions. The reader is never more than one step from a known-good state.
- **Every checkpoint has a "what that means" block.** Translate the terminal output
  back to the postal analogy / core idea. This is where learning happens.
- **The Toolbox table goes before the steps.** Not after, not inline. Readers need
  the vocabulary before they encounter it in commands. See the postal skill's table
  for the template: three columns (term / plain meaning / what it does in this lab).
- **Real run record with the bug.** Include the failure from the first test run.
  This is not just verification, for Gen Z readers it is the strongest trust signal
  in the document. Put it prominently (the troubleshooting table, not a footnote).
- **Define everything.** No assumed knowledge about TCP, ports, crypto, config files,
  IP addresses, or command-line basics. A glossary table is mandatory.
- **One analogy, start to finish.** If the spine analogy is the postal system, every
  concept maps to it: identity = fingerprint, announce = telling the post office your
  address, interface = road, port = door number. Do not switch analogies.

- **Black box the hardest prerequisite.** Every technical concept has one piece that
  requires half a different field to truly understand (cryptography, signal processing,
  kernel internals). Abstract that piece into a labeled black box. Tell the reader
  what the box produces (a 32-char address, an unforgeable receipt) but never explain
  how it works inside. Give the box a single clear name (Identity, not the algorithm
  chain). The reader copies the output and trusts the box. This is not dumbing down,
  it is scope control. The box can be opened in a later, more advanced guide.

  **Example from L0-guide-postal.md:** the Identity encapsulates key generation,
  hashing, signing, and encryption. The student sees only the 32-character hash and
  the label "Identity: a black box that says 'I am this machine and I can prove it.'"
  No reference to ECDH, SHA-256, or Ed25519 appears anywhere in the guide.

- **Pick a motivational frame the learner lives inside.** The lab's own narrative
  must carry the motivation, not an external video, not a preamble paragraph. The
  opening hook should name a felt problem the reader has experienced but could not
  name. Effective frames for technical labs:

  * **Sovereignty / ownership**: The reader's daily tools are rented, not owned.
    Frames the lab as building an alternative. (Used in L0-guide-postal: "Every
    message you have ever sent crossed a server you don't control.")

  * **Broken default**: Something the reader uses every day works wrong and they
    never knew why. Frames the lab as a fix.

  * **Hidden mechanism**: Something familiar, revealed. Frames the lab as a discovery.

  The frame named in the hook must echo in the punchline. The closing paragraph
  should return to the same felt problem and show how what the reader built addresses
  it. If the hook says "you don't control the servers," the punchline says "nobody
  gave you permission to build this network. Nobody can take it away from you."

## Example

The Reticulum L0 lab guide (`labs/reticulum/L0-guide-postal.md` in the notes
catalog) is a worked example of this pattern applied. It uses the lecture-walkthrough
section skeleton, the plain-language skill's principles, and Gen Z communication
research to produce a guide designed for first-time terminal users.

## Embedded Software Walkthroughs

When a lab depends on GUI software (REW, WINISD, VituixCAD, SigmaStudio), the
numbered steps must include a **detailed walkthrough of the software itself**,
not just "open the program and configure it."

### Software walkthrough rules

- **Open the program section.** Before any configuration steps, include a "how
  to install and launch" subsection. Name the exact URL, the exact filename to
  download, and any compatibility layer needed (e.g. Wine for Windows-only apps
  on macOS: `brew install --cask wine-stable`).

- **Click paths are steps.** Each dialog, each dropdown, each checkbox gets its
  own bullet or sub-step. Write them as: "Go to **File -> Preferences -> Soundcard**
  and set **Output channel** to **Left** and **Input channel** to **Right**."
  Bold the menu path and the named setting.

- **What-this-means for every parameter.** When the student enters a value (e.g.
  "Reference resistor: 10 ohms"), explain what that number represents and why
  it matters: "The 10 ohm resistor is the known reference REW uses to compute
  impedance via the voltage divider formula. If this value is wrong, every
  impedance measurement shifts by a constant factor."

- **Verification state after each config block.** After a group of settings,
  tell the student what should appear on screen: "The graph should show a flat
  line around 4 ohms before the sweep starts. If it shows 0 or a noisy trace,
  check your input channel selection."

- **Normal ranges for measurements.** When the student runs the measurement and
  sees a number (impedance peak height, T-S parameter output), list what a
  healthy value looks like and what common failure modes produce. For example:
  "Fs should be between 60-300 Hz for a small fullrange driver. If REW reports
  Fs below 20 Hz, the driver likely has a torn surround or you are measuring in
  a sealed box by accident."

- **Screenshot substitutes.** Since you cannot embed actual screenshots in
  markdown, describe the dialog layout and important visual cues: "A dialog
  appears with fields: Name, Fs, Qms, Qes, Qts, Re, Le, Vas, Cms, Mms, BL, Sd.
  Qts is auto-calculated from Qms+Qes. If your manually entered Qts differs
  from the calculated value by more than 5%, check your Re measurement."

## Hardware Lab Considerations

When the lab involves physical circuits, measurement hardware, or electronics
assembly, the numbered steps must account for:

| Consideration | What the lab needs |
|--------------|-------------------|
| **Circuit diagram** | ASCII schematic or clear wiring list. Use bullet-point wire connections: "Left channel (tip) -> 1000 ohm resistor -> junction A" |
| **Parts list (BOM)** | Table with part name, value/quantity, purpose, and where to get it. Mark optional vs required. |
| **Verification step** | "Measure resistance with multimeter between X and Y: should read Z ohms." Give the student a way to check their work before powering on. |
| **Safety note** | Max voltage/current, what to protect (audio output, driver), what not to touch. |
| **Failure signatures** | What specific wrong behaviors mean (flat line at 0 ohms = no signal on measurement channel; flat line at 10 ohms = reference resistor measured but no driver). |
| **Assembly order** | Wires first, then resistors, then test points, then the DUT. |

## Source

This pattern emerged from building L0-guide-postal.md (Reticulum networking lab)
on 2026-07-11 and L0-measure-driver.md (speaker design lab) on 2026-07-12,
combining the lecture-walkthrough structure template, plain-language principles,
and Gen Z science communication research (ACM CHI 2023, Gallup/Walton 2024,
McKinsey 2022). The hardware lab rules were derived from the EE design pipeline
characterize -> model -> mock -> measure -> iterate, concretized through the
speaker T-S parameter measurement lab.

For the full communication research synthesis, see the `plain-language` skill's
"Reaching Younger or First-Time Audiences" section.
