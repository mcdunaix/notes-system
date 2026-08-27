# Narrative Delivery Checklist (Phase 2c)

Operational excerpt for applying the narrative/metaphor delivery research
during Phase 2 (Notes), sequenced after the abstraction plan (Phase 2b).
This file is what to apply per concept, per rung, and is self-contained:
the full research grounding, the story-craft findings, and the
metaphor-candidate evaluation live in the author's vault as NC-0031, not
shipped with this repo.

## The gate comes first, and it can say no

This is not a default pass. Most concepts, most rungs, will not need this
treatment. Per the research's own Scope and limits section: narrative and
metaphor framing is a technique reached for when a concept is genuinely hard
to communicate without one, gated per concept, never applied uniformly.
Forcing a story onto a concept that does not need one is not a stronger
guide, per the seductive-details research it cites, it is a weaker one.

## Execution constraint

Same as Phase 2b: do not use `delegate_task` for this loop, confirmed
non-blocking in this Hermes instance regardless of invocation shape. Classify
each concept's gate result directly, in context, one concept at a time.
Where to look first: concepts that reached Name, Connect, or Transfer
(layers 3-5) in Phase 2b are a reasonable place to check before layers 0-2,
since those layers ask for language and relational structure rather than
direct action, exactly the territory metaphor and story are suited to. This
is a heuristic, not a rule, check every concept against the gate below
rather than skipping layers 0-2 on the assumption they never qualify.

## The gate: three tests, any one is enough

For each concept, ask: does it pass at least one of these?

1. **Need-to-know.** Does a metaphor or story beat create a reason the
   learner needs to know this, that a flat statement of fact would not?
2. **Consequence.** Does narrative framing show a consequence of this
   concept that the learner would otherwise miss?
3. **Motivation.** Does it motivate an action the learner would otherwise
   choose not to take?

**If none apply: record "gate: no" and move on.** No further fields needed.
This is a normal, unremarkable outcome, not a shortfall, do not manufacture
a thin justification to force a "yes."

**If at least one applies: record "gate: yes"** and continue to the fields
below.

## If the gate passes: fields to record

1. **Chosen metaphor.** Reuse the ladder's already-established metaphor if
   one exists, do not introduce a second metaphor mid-ladder without a
   stated reason. Otherwise select one against the Part 4 criteria of the
   research (relational overlap, familiarity, ownership frame, fade-ability,
   emotional resonance) and record why.
2. **Story elements carried.** Which of the seven elements (character,
   intentionality, context, action, conflict, stakes, change) does this
   concept's narrative beat supply. Not every concept needs all seven, the
   rung as a whole does.
3. **Transition marker.** Where the diegetic-to-non-diegetic switch happens
   (story prose to command block), using this ladder's one consistent
   marker, not a new one per rung.

## Worked example

Concept: **Path/routing**, Reticulum L0 (Phase 2b layer: 4, Connect).

Gate check: does the learner need a reason to care that Reticulum found a
path automatically? Consequence test passes: without narrative framing, "the
network found the path" reads as a throwaway implementation detail; framed
as "nobody gave you permission to build this network, nobody can take it
away from you" (the guide's own closing line), the same fact becomes the
payoff the whole rung was building toward. Gate: yes.

Metaphor: the ladder's existing Neighborhood/Territory frame, already
established at L0's hook ("own the address yourself"), no new metaphor
introduced. Story elements: stakes (the alternative is a network you do not
own) and change (before: rented infrastructure, after: a network you
generated and verified yourself). Transition marker: this ladder's existing
pattern, a blockquote "what that means" block following each checkpoint.

Concept: **Interface** (TCP), same rung, Phase 2b layer 1,3 (Operate, Name).

Gate check: none of the three tests clearly apply. The guide already states
plainly what an interface is and does; no missing consequence, no motivation
gap a story would close. Gate: no. This does not mean Interface gets no
narrative color anywhere in the guide, the ladder's overall metaphor still
touches it (the "road" analogy), only that Interface itself does not need
its own dedicated narrative beat.

## Output: the Narrative delivery plan row

One row per concept: `| Concept | Gate | Metaphor (if yes) | Story elements (if yes) | Transition marker (if yes) |`

## Before Phase 3

If every concept in the rung gated "no," that is a valid, complete Phase 2c
output, proceed to Phase 3 in the plain accessible shape with no forced
story beat. Do not treat an all-no result as incomplete work requiring a
second pass to find something to narrate.
