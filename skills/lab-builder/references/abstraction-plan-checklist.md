# Abstraction Plan Checklist (Phase 2b)

Operational excerpt for applying the 6-layer abstraction taxonomy during
Phase 2 (Notes). This file is what to apply per concept, per rung. It is a
narrow derivative, not a mirror: it does not restate the canonical research
document's citations or its Part 1 research, and it is self-contained (the
full research grounding, the confidence tiers, the worked examples, and the
open questions live in the author's vault as NC-0030, not shipped with this
repo).

## Execution constraint (read this before writing any classification)

Do not use `delegate_task` for this loop. In some Hermes installs
`delegate_task` does not block the calling
turn, single-task or batch, regardless of what is requested. A one-shot
`hermes chat -q` invocation exits at the end of its own turn, before any
dispatched subagent can report back, so any classification attempted through
`delegate_task` in this execution mode will be silently lost. Verify
sub-agent completion before reading results, and classify every
concept directly, in this same context, following the loop below.

Because there is no subagent isolation, independence between concepts is a
prompting discipline, not a structural guarantee. Follow this rule
explicitly: **classify one concept fully (all layers, with justification)
before reading the next concept's row.** Do not let an earlier concept's
layer assignment anchor a later one. If two concepts feel similar, re-derive
each one from the guide text and the rule below separately, do not copy
reasoning from one row to the next.

## The 6-layer taxonomy (operational form)

| Layer | Kind | Name | The learner... | The lab gives them... |
|---|---|---|---|---|
| 0 | Depth | Witness | observes the effect without touching the mechanism | a command they run and watch output appear |
| 1 | Depth | Operate | uses the concept through a concrete, tangible interface | a step where they copy-paste, run a tool, click a button |
| 2 | Depth | Configure | makes an intentional choice that changes how the concept behaves | a config file they write, parameters they set |
| 3 | Depth | Name | attaches the canonical term to a pattern they already experienced | a glossary entry or explicit naming step |
| 4 | Web | Connect | relates the concept to other concepts in the stack | a diagram or status check showing how components fit together |
| 5 | Web | Transfer | applies the abstracted concept to a new medium or context | ladder structure: same concept, new road |

Layers 0-3 are monotonic per concept, per path: within one concept across
rungs, never decrease. Layers 4-5 can recur, they are not "higher" than 0-3
in the concreteness-fading sense. A new concept always starts at layer 0 or
1, never introduced at 3 or above on first appearance.

## Triage: the escape route

Before working through the full loop for a concept, check whether it
resolves directly:

- **Analytically clear** (most concepts at layers 0-2): apply the
  disambiguation rule below, record the layer, done. No further deliberation
  needed.
- **Needs the fuller call** (layers 3-5, or a genuinely ambiguous 0-2 case):
  work through the full per-concept procedure below.

This mirrors this vault's own `lecture-vetting` skill's triage design: an
unambiguous case forced through a heavier procedure anyway is exactly how
classification drift creeps in, not how it gets prevented.

## Disambiguation rule (the Witness/Operate/Configure boundary)

Did the learner's own choice change the output (Configure)? Did they perform
the action themselves with no meaningful choice to make (Operate)? Did they
only watch it happen (Witness)? Apply this per concept, not per step, a
single concept can touch multiple layers across different steps in the same
rung.

Watch for the specific trap this vault's own testing caught: an action that
looks like it belongs to one concept (e.g. copying a hash) may actually
operate on a different, related concept (e.g. the destination address the
hash represents, not the identity that generated it). Re-derive which
concept the action actually touches before assigning a layer, do not assume
from the surface wording of the step.

## Per-concept procedure

For each concept in the rung's master concept list:

1. State the concept name.
2. Read (or recall, if already read this rung) the guide draft's passages
   that mention it.
3. Apply the triage above. If analytically clear, record the layer and move
   on.
4. If not, walk the disambiguation rule against the specific text, citing
   the exact passage that supports the call.
5. A concept can sit at more than one layer in the same rung. Record all
   that apply, each with its own one-sentence citation.
6. Move to the next concept only after this one is fully recorded.

## Output: the Concept Layer Map row

**File location.** The ladder-level map lives at
`labs/<protocol>/concept-layer-map.md`. This file is one per ladder, not one
per rung, it accumulates rows across all rungs so each rung's Phase 2b can
read its own prior-rung column from a single authoritative source.

**Bootstrapping (first rung / L0).** The file does not exist yet for a new
ladder. Create it from `templates/concept-layer-map.md` (in the
lab-builder skill's own templates/ directory) as a starting shape, then fill
in this session's rows. The "Prior rung's layer(s)" column is `N/A (first
rung)` for every concept, the "Layer shift" column is `New`, and the shift
story column describes first appearance.

**Appending (L1+).** Read the existing `concept-layer-map.md`, do not
reconstruct its contents from memory or from a summary. Splice in this
rung's new column, preserving every prior row. This is what keeps "prior
layer" honest instead of drifting rung over rung.

**Relationship to Phase 2's concept-notes.md.** The per-rung concept notes
file (`<protocol-slug>-concept-notes.md`) also includes an `## Abstraction
plan` section that documents this rung's rows. That file is the rung-level
record. The ladder-level map is the cumulative cross-rung record. Both get
produced during Phase 2b, the per-rung notes are the primary artifact, the
ladder-level map is a derived reference for future rungs.

One row per concept:

`| Concept | Prior rung's layer(s) | This rung's layer(s) | Layer shift | One-sentence layer-shift story |`

## Worked example (from this vault's own pilot testing, 2026-07-13)

Concept: **Identity**, Reticulum L0.

Layer 0 (Witness): in the guide's Step 6 the learner runs the server
command and the Identity generates itself automatically, producing a
32-character hash they observe without touching the mechanism. The guide
states outright: "You will never configure the cryptography directly."
Layer 3 (Name): the guide explicitly defines and names the black box,
"Reticulum gives every machine a cryptographic Identity: a black box..."
No Layer 1 or 2: the learner never configures the cryptography or types a
key themselves.

Concept: **Destination**, same rung.

Layer 0 (Witness): the destination address hash appears in the server's
own output, the learner observes it appear. Layer 1 (Operate): the learner
copies that hash and pastes it into the client command, using the
destination address as a tangible tool, this is the action that does not
belong to Identity, see the trap noted above. Layer 3 (Name): the guide's
toolbox table explicitly names and defines it.

Note what this pair demonstrates: Identity and Destination are closely
related in the guide's prose (the same hash is described both as the
Identity's outward face and as the destination address), and a careless
pass could attribute the copy-paste action to the wrong one. Rederiving each
concept separately, per the discipline above, is what caught the
distinction.

## Before moving to Phase 2c

Confirm every concept in the rung has at least one layer recorded, and that
no concept was introduced above layer 1 on its first ladder appearance. If
either check fails, the abstraction plan is incomplete, do not proceed to
the narrative delivery plan on an incomplete concept list.
