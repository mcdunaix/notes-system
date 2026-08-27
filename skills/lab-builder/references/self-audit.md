# Self-Audit (before write-back)

Nothing checks lab-builder's output before it reaches disk. This pass is the
gate. It runs after Phase 3's draft is complete and before the guide
publishes. Its discipline, inherited from the author's
`technical-research-survey` skill (private vault, not shipped in this repo)
and this repo's `lecture-vetting` skill: when it finds a
problem, fix it before write-back, do not flag and proceed.

## The checks

### 1. No orphaned delegation

Confirm the guide's Phase 2b and Phase 2c fields were filled by direct,
in-context classification, not by a `delegate_task` call whose result never
returned. In some Hermes installs `delegate_task` does not block, so verify
sub-agent completion before reading results: a run that dispatched subagents and then
wrote placeholder or invented values while "waiting" for them produced
silently wrong output. If any Concept Layer Map or Narrative delivery plan
row looks templated, generic, or unsupported by a specific citation to the
guide text, that is exactly this failure mode. Re-derive it directly.

### 2. Internal consistency

- **Concept coverage.** Every concept in the rung's master concept list has
  at least one Phase 2b layer recorded and an explicit Phase 2c gate result
  (yes or no). No concept silently skipped.
- **Monotonicity.** For every concept, layers 0-3 do not decrease relative
  to its own prior-rung value (read from the ladder-level Concept Layer Map,
  not from memory).
- **Gate-to-content match.** Every concept whose Phase 2c gate passed
  actually has its chosen metaphor's name appear somewhere in the guide's
  prose: the Hook, the Core Idea, a Toolbox definition, or the closing
  section that echoes the hook's frame (`lab-guide-pattern.md`'s own
  closing-echo rule covers this last case). A "yes" gate with no trace of
  the metaphor anywhere in the guide's text is a planning artifact that
  never got executed.
- **No orphan narrative.** No metaphor language appears in the guide for a
  concept whose gate recorded "no." If the guide narrates it anyway, either
  the gate was wrong or the guide drifted from the plan, resolve one or the
  other, do not leave both standing.

### 3. Eight-block contract, by substance

Walk the list in `eight-block-contract.md`. For each of the eight blocks,
confirm its content actually exists somewhere in the guide, native section
or, for Learning objectives and Prerequisites checklist, the collapsed
callout, not just that a heading with a similar name exists.

### 4. Seductive-details scan

For every narrative sentence the guide contains (from a Phase 2c "yes"
concept), confirm it passes at least one of the three gate tests
(need-to-know, consequence, motivation). A sentence that is charming but
does not clear one of the three tests gets cut, per the narrative research's
own Part 3.1.

### 5. Real-run record present and honest

Confirm the Real-run record section (`real-run-record-format.md`) is fully
populated with real, pasted terminal output, not the Phase 3 placeholder
("Pending: awaiting user execution and evidence").

**Carry-forward check:** if the guide is a rebuild of one that already
existed, confirm the prior real-run data was preserved, not replaced with a
blank placeholder. If no prior version existed but the record says
"Pending," that is correct for Phase 3, flag it but do not block (Phase 4
fills it). If a prior version existed and the record says "Pending," that is
a regression, block the write-back and restore the prior data.

If a first attempt failed, confirm the failure is described honestly and its
fix appears in the Troubleshooting table, not silently dropped.

### 6. Dash scan

No em dash character and no `--` used as punctuation anywhere in the guide.
This skill's own reference files are held to the same standard; check the
guide, not just the checklists.

## If the audit finds nothing

It still ran correctly. A pass that changes nothing is not a skipped pass,
it is the evidence the output was clean. Record "self-audit: clean" and
proceed to write-back.

## After write-back: the executable gates

The self-audit above is judgment. These are mechanical and non-negotiable:

```bash
grep -c $'—' <guide-file>          # em dash count (the literal U+2014 character, required in this grep), MUST be 0
grep -n -- '--' <guide-file> | grep -vE '\|[-: ]+\||^[0-9]+:---'   # double hyphens outside table separators and rules; review remaining hits: CLI flags and detector lines are exempt, prose uses must be 0
python3 scripts/transcript.py verify    # if any source_entries were touched, MUST exit 0
```

A warning without a gate does not hold. Treat a failed gate as file damage:
restore from the last good state and redo the affected section, never leave
it and flag it for later.
