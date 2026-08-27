---
name: lab-builder
description: Build hands-on lab guides through four gated phases (research, notes, design, verify/build) that turn a technology and a pedagogical angle into a tested, publishable guide in the accessible shape.
---

# Lab Builder: Research-to-Guide Pipeline for Hands-On Labs

Build one hands-on lab guide per invocation, for the catalog's lab
ladders (`$CATALOG_ROOT/labs/<protocol>/`). Distinct from
`lecture-walkthrough`: that skill expands an existing transcript in one
pass, no design phase, no philosophy bridge. This skill designs a lab from a
user-supplied focus statement across four phases, each with a literal file
artifact the next phase consumes.

The design-rationale brief is a personal vault artifact
(`briefs/2026-07-11_hermes-lab-builder-skill.md`) and is not shipped with
this repo. This file is the operational instructions and is self-contained.

## Catalog root

`$CATALOG_ROOT` is the catalog root: the directory containing
`scripts/transcript.py` (the repo root when this repo is used as the vault).
Set `export CATALOG_ROOT=/path/to/catalog` before running commands.

## Pre-check: does the target guide already exist?

Before any phase, check whether a guide already exists at
`labs/<protocol>/L<N>-*.md`. If it does, read it and evaluate against the
quality criteria implicit in this skill's own pipeline:

1. Does it have the eight-block contract covered by substance (not just
   headings)? Walk the list in `references/eight-block-contract.md`.
2. Does it have a populated Real-run record with real terminal output and
   a gate-check sentence (not "Pending: awaiting user execution")?
3. Are source claims verified and cited against primary sources?

If all three pass, **do not rebuild.** Report the finding and stop.
Rebuilding a guide that already meets the bar produces a functionally
identical copy and, worse, destroys the real-run data the old guide
carried.

If only some checks pass, proceed to Phase 1 but scope it to the gaps.
Do not re-research what is already correct.

## Guided mode only

## Input contract

| Field | Required? | What it is |
|---|---|---|
| `protocol` | Required | The technology this lab teaches. |
| `learner_level` | Required | Audience baseline, stated explicitly. |
| `pedagogical_angle` | Required | The hook's frame: Sovereignty/ownership, Broken default, Hidden mechanism, or a stated novel one. Must pass the relevance-gate test (names the payoff before asking for attention). |
| `philosophical_tie_in` | Required | How this lab exemplifies community-owned infrastructure, concretely. |
| `sibling_edition` | Optional, default none | Only set for a genuinely distinct second document. |
| `source_entries` | Optional | Existing NC-#### id(s) to start from. |
| `hardware_budget` | Optional | Dollar ceiling and existing-hardware assumption. |

## Phase 1: Research

**Input:** the focus statement, `source_entries` if given.

Find primary sources first (protocol spec, manual, RFC), official docs
second, third-party tutorials only as corroboration. Identify a source video
or short-form explainer for the video-first on-ramp
(`gen-z-science-communication.md` finding 4). Verify every capability claim
intended for use against a primary source, cite the URL. Where a procedure
can be tested locally at zero hardware cost, test it now rather than defer
to Phase 4. Where testing needs hardware not yet owned, say so explicitly,
never skip silently.

**Output:** `<protocol-slug>-research-summary.md`: `## Primary sources`,
`## Source video`, `## Verified capability claims` (claim, source, tested
yes/no, command and output if tested), `## Open questions / untested
claims`, `## Candidate demo(s)`.

## Phase 2: Notes

**Input:** the research summary, the focus statement's `pedagogical_angle`
and `philosophical_tie_in`.

For each candidate demo, write out explicitly how it exemplifies
community-owned infrastructure, concretely, not a generic "this is cool
tech" gloss. Draft the hook against the relevance-gate test. Extract key
concepts, one plain-language sentence each. Identify prerequisites. Sketch a
learning arc, ordered, one sentence per step.

Then run two gated sub-phases, in order:

**Phase 2b: abstraction plan.** Follow `references/abstraction-plan-checklist.md`
exactly, including its execution constraint (no `delegate_task`). Produces
one row per concept in the Concept Layer Map.

**Phase 2c: narrative delivery plan.** Follow `references/narrative-delivery-checklist.md`
exactly, including its own gate. Produces one row per concept in the
Narrative delivery plan. "Gate: no" is a valid, complete answer for any or
all concepts.

**Output:** `<protocol-slug>-concept-notes.md`: `## Philosophy bridge`,
`## Hook draft`, `## Concept glossary`, `## Prerequisites`,
`## Learning-arc sketch`, `## Abstraction plan`, `## Narrative delivery
plan`.

## Phase 3: Design

**Input:** the concept notes, the research summary, `sibling_edition`.

Write one guide, in full, spine from `references/lab-guide-pattern.md`:
Hook, Core Idea, Toolbox, What You Will Build, Step by Step, What Just
Happened, The Bigger Picture, Troubleshooting, Stretch Goal. Pick one
motivational frame and carry it start to finish, named in the hook, echoed
in the closing section.

Immediately after the intro, before the Hook, insert two collapsed Obsidian
callouts per `references/eight-block-contract.md`: Learning objectives and
Prerequisites checklist. For a radio rung, add a third block, Safety and
legality, uncollapsed.

Surface the Phase 1 source video near the top as a "watch this first"
pointer, not buried in Sources.

Apply Phase 2b: every numbered step exercises its concept at the target
layer recorded in the abstraction plan. A Witness-layer concept gets a
black-box step the learner observes; a Configure-layer concept gets a step
where they make an intentional choice and see its effect. If a step would
land at a lower layer than planned, update the abstraction plan before
publishing, never leave the guide silently short of its own plan.

Apply Phase 2c: where a concept's gate passed, the Hook and Core Idea
sections follow the per-rung narrative structure in
`references/narrative-delivery-checklist.md` (opening beat, explicit
transition, lab execution, return to narrative). Where no concept's gate
passed, proceed in the plain accessible shape, no forced story beat.

If `sibling_edition` is set to something other than none, produce a second
file for that stated purpose; otherwise produce only the one guide.

The guide carries a `## Real run record (R-15 gate)` section:

- **If the guide is new (no prior real-run data exists):** write
  "Pending: awaiting user execution and evidence."
- **If a prior version of this guide already had a real-run record with
  actual terminal output, numbers, and a gate-check sentence:** preserve
  that data. Add a note that it was carried forward from the prior run.
  Do not replace real data with a placeholder.

The Real-run record format is in `references/real-run-record-format.md`.

**Output:** `<protocol-slug>-L<N>-draft.md`, and only if `sibling_edition`
was set, a second file for that purpose.

## Phase 4: Verify and build

**Input:** the Phase 3 draft, the user's actual execution: real terminal
output, real timing, any failures hit. Cannot run without a live human, by
design.

Build the final Real-run record section from the user's pasted output, per
`references/real-run-record-format.md` exactly: expected outputs were
written before execution, run date and environment, an honest failure if
one happened folded into the Troubleshooting table, real terminal output
verbatim, a gate check sentence.

Run the full self-audit in `references/self-audit.md` before write-back.
Fix anything it finds, do not flag and proceed. Run the executable gates
after write-back.

**Output:** the finished guide in `$CATALOG_ROOT/labs/<protocol>/`, Real
run record fully populated, wikilinked into the relevant domain index.

## Pitfalls

> **Eight-block contract:** see `references/eight-block-contract.md` for the
> substance-not-structure reading and the collapsible-callout technique.
> **Accessible shape:** see `references/lab-guide-pattern.md` for the full
> section mapping, motivational frames, and embedded-software/hardware-lab
> rules.
> **Gen Z research:** see `references/gen-z-science-communication.md` for
> why the hook is a relevance gate, why real-run failures are the primary
> trust signal, and why the guide should point to a source video first.
> **Real-run record:** see `references/real-run-record-format.md` for the
> exact section this skill cannot fabricate, it requires live execution.
> **Abstraction plan (Phase 2b):** see `references/abstraction-plan-checklist.md`.
> Do not skip the execution-constraint note at its top.
> **Narrative delivery plan (Phase 2c):** see `references/narrative-delivery-checklist.md`.
> The gate says no far more often than it says yes; that is correct
> behavior, not a shortfall.
> **Self-audit:** see `references/self-audit.md`. Run it before every
> write-back, not just when something feels off.

- **`delegate_task` does not block in this Hermes instance.** Confirmed
  2026-07-13: single-task and batch calls both return immediately regardless
  of what is requested; results, if they ever arrive, land as a later
  conversation message that a one-shot `hermes chat -q` invocation will
  never see, because the process exits at the end of its own turn. Never use
  `delegate_task` for Phase 2b or 2c's per-concept loops. Classify directly,
  in context, following the checklists' discipline against contamination
  between concepts.
- **No em dashes, ever (D-12 in the notes vault, applied here too).** A
  comma, a colon, or two sentences instead. Structural separators use a
  plain hyphen. Check the guide itself, not just this skill's own reference
  files.
- **One edition per rung is the default (D-23 in the notes vault).**
  `sibling_edition` is the deliberate exception, stated with a distinct
  purpose, never routine reference/accessible duplication.
- **Phase 2c's gate can fail for every concept in a rung.** That is a
  correct, expected outcome for a rung whose concepts are all
  self-explanatory. Do not manufacture a metaphor to avoid an all-no result.
- **Do not rebuild a guide that already meets the quality bar.** The
  pre-check step (before Phase 1) exists to catch this. Ignoring it produces
  a functionally identical guide with regressed data (lost real-run record,
  blank placeholder in its place). If the user explicitly asks you to
  rebuild, preserve the prior real-run data on write-back.
- **The research behind the checklists is not mirrored here.** `abstraction-plan-checklist.md`
  and `narrative-delivery-checklist.md` are narrow operational excerpts and
  are self-contained; the canonical research documents (NC-0030, NC-0031 in
  the author's vault) are not shipped with this repo. Do not restate their
  citations from memory.
- **Phase 1 never auto-ingests a new source into the catalog.** Flag a
  candidate source video for cataloging; `transcript.py add` is a separate,
  user-authorized step.
- **Video embedding requires approval**, same rule as `lecture-walkthrough`:
  never embed a video file without asking first.
