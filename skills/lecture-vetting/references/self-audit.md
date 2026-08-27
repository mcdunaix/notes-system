# Self-Audit / Peer Review (Stage 5, before write-back)

Nothing checks the vetting output before it reaches the file, a hallucinated citation or
a miscounted tier from lens-firing would go straight into the walkthrough. This pass is
the gate. It runs **after** the report is drafted and **before** `write_file`. Its
discipline, inherited from `technical-research-survey`'s audit-response cycle: when it
finds a problem, **fix it before write-back, do not flag and proceed.**

This is a scoped-down version of `technical-research-survey`'s Quality Audit checklist,
narrowed to this skill's output.

## The checks

### 1. Term-in-source on every citation the lenses produced

For each citation in the report's Sources column, and for every attributed quote in the
walkthrough that a lens verified: confirm the source **actually contains** the claim,
term, or quote, not just that the source exists and is topically related. This is the
exact check that caught a fabricated term ("memristive effect" attributed to a paper that
never used it) in a past `technical-research-survey` session.

- Attributed quotes: the words must appear in the cited paper or in this file's
  `## Full Text` block. A paraphrase attributed as a direct quote is a finding, either
  requote exactly or downgrade it to "paraphrase."
- Named results: the source must state the result, not merely the topic.
- If a citation can't be confirmed, it is a hallucinated or mis-remembered source: remove
  it and re-tier the claim without it (a CONFIDENT claim resting on it may drop to
  UNVERIFIED or SPECULATIVE).

### 2. Internal consistency

- **Count vs. rows:** the summary line's four tier counts sum to "N claims checked" and
  each equals the actual number of rows at that tier. This is the most common catch.
- **Tag vs. row:** every inline tag's tier equals the report row's tier for the same
  claim; every non-confident row has exactly one inline tag; no CONFIDENT claim is tagged;
  no tag lacks a matching row.
- **One claim per row:** no row secretly bundles an attribution and a date at different
  tiers (the split should have happened at extraction, catch stragglers here).

### 3. Conclusion-body contradiction scan

Does any **CONFIDENT** verdict rest on evidence the report itself describes as partial or
conflicting? Scan each CONFIDENT row's Lens Findings for hedge words ("possibly", "one
source", "contested"), a CONFIDENT tier requires ≥2 independent corroborations and *no*
contradiction, so any hedge in its own findings cell is a contradiction with its tier.
Resolve by re-tiering (drop to UNVERIFIED/DISPUTED), not by deleting the hedge. (Mirrors
`technical-research-survey`'s "conclusion-body contradiction scan.")

### 4. Aggregation replay against the fixtures

Spot-replay the stage-4 aggregation on 2–3 `fixtures.md` claims. If the same triage +
rule no longer reproduces the fixtures' expected tiers, the logic drifted mid-run, fix it
before writing. The fixtures are the contract (R-15); the run conforms to them, not the
reverse.

### 5. Blast-radius pre-flight

Before writing, confirm the *only* things that changed versus the file you read are the
new `## Vetting Report` section and the inline tags. Mentally diff: frontmatter identical
(especially `id:`), walkthrough prose identical except for appended tags. For `## Full
Text`, do not rely on a mental diff, run the executable tag-boundary gate below instead.
A claim with no non-confident mention anywhere in the walkthrough prose above the fence
gets no inline tag at all; its tier lives in the `## Vetting Report` table only. If
anything else moved, you rebuilt something you should have copied verbatim, go back to
the read copy.

## If the audit finds nothing

It still ran correctly. A pass that changes nothing is not a skipped pass. It is the
evidence the output was clean. Record "self-audit: clean" and proceed to write-back.

## After write-back: the executable gates

The self-audit is judgment; these three are executable and non-negotiable (from
SKILL.md's write-back protocol):

```bash
cd $CATALOG_ROOT
sed -n '/^## Full Text$/,$ p' transcripts/<cat>/FILE.md | grep -c '^```$'             # MUST be 2
python3 scripts/transcript.py verify                                                  # MUST exit 0
sed -n '/^## Full Text$/,$ p' transcripts/<cat>/FILE.md | grep -c 'see Vetting Report' # MUST be 0
```

A warning without a gate does not hold. This is the lesson behind the whole catalog's
`verify` command (NC-0018 was corrupted *after* the pitfall was already documented in
prose) and behind the third gate above: the 2026-07-10 NC-0021 live run tagged 5 claims
directly inside `## Full Text` while the fence count stayed `2` the entire time. "The
fence survived" and "nothing between the fences changed" are different claims and need
different gates. Treat a failed gate as file damage: restore from the read copy and
redo, never leave it and flag it.
