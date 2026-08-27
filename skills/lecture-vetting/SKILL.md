---
name: lecture-vetting
description: Fact-check an already-cataloged lecture-walkthrough's narrative-load-bearing claims (D-19: claims doing persuasive work for the content's own thesis, not illustrative color) against independent, multi-perspective sources, then annotate disputed or unverified claims in place. Manual/on-demand only (D-20), invoked by the user directly on a whole file ("vet this lecture", "check this lecture's claims", "fact-check the walkthrough") or on one named claim ("check this specific claim", "I'm skeptical about X"). Advisory only, it never blocks or re-runs cataloging, and never triggers itself.
---

# Lecture Vetting: Multi-Perspective Fact-Check of a Cataloged Walkthrough

Take an existing lecture-walkthrough file in the content catalog (`$CATALOG_ROOT/`),
extract its load-bearing factual claims, check each one from several independent
angles, and write the verdicts back into the *same* file, a `## Vetting Report`
section plus inline tags on only the claims that did not come back confident.

`$CATALOG_ROOT` is the catalog root: the directory containing
`scripts/transcript.py` (this repo root when the repo is used as the vault).
Set `export CATALOG_ROOT=/path/to/catalog` before running commands.

This skill is **advisory**. It runs as a follow-up pass on already-cataloged content
(protocol decision D-2, pinned in the author's private vault decision log, not in this repo). It never blocks a video
from being cataloged and never touches `scripts/transcript.py`, the dashboard index,
or the domain indices. Its only write is into the walkthrough file it was pointed at.

It is the sibling of `lecture-walkthrough` and edits the **same fragile region** of
the same files, read the write-back safety protocol below before touching anything.

## Input contract

Takes **an arbitrary path to an existing walkthrough file**, e.g.
`$CATALOG_ROOT/transcripts/ai-ml/NC-0021_1-introduction-and-scope.md` (NC-0021 is
an entry in the author's private vault, not shipped in this repo; substitute any
entry of your own), and
optionally **one named claim** within it, e.g. "check the chimp-DNA percentage in
NC-0021." It does *not* assume you just ran `transcript.py add`. This is deliberate:
backfilling any already-cataloged entry is just "run this skill again on another
path," not a separate feature.

**Deployment is manual only (D-20).** This skill has no automated trigger, no backlog
sweep, and no credibility-based scheduling: the user invokes it directly, in one of
two situations, needing a reliable source for one of their own projects, or being
skeptical about a specific claim. D-19 means the payoff is uneven across the catalog
(a credentialed academic lecture like NC-0021 is mostly illustrative color, low
yield; narrative-pushing shortform content is where this skill earns its keep), but
that is background for the user's own judgment about what to point this at, not a
scheduling rule this skill applies itself.

**A named-claim request can override the D-19 exclusion, but only after confirming.**
If the request names a claim that `claim-extraction.md`'s sixth exclusion category
would otherwise skip as narrative-irrelevant color, do not silently extract it and do
not silently decline: surface the classification and ask before proceeding (see that
file's D-20 note). Whole-file requests are unaffected, the exclusion runs exactly as
written for those.

The file must already have a `## Full Text` section (the fenced transcript). That is
the ground truth the walkthrough was built from and the source you check attributed
quotes against.

## Pipeline

Five stages. Do them in order; do not write anything to disk until stage 5.

| # | Stage | What it produces | Reference doc |
|---|-------|------------------|---------------|
| 1 | **Scan** | Discrete, checkable claims extracted from the walkthrough prose/quotes/tables | `references/claim-extraction.md` |
| 2 | **Interrogate** | Per claim: triage which of the five lenses apply, fire only those independently, collect findings | `references/multi-perspective-verification.md` |
| 3 | **Contradiction map** | Per non-confident claim: the specific conflict, which lens found what, where the disagreement is | `references/multi-perspective-verification.md` (aggregation) |
| 4 | **Synthesis** | Each claim collapsed to one tier (DISPUTED / CONFIDENT / UNVERIFIED / SPECULATIVE) via the aggregation rule; the `## Vetting Report` table drafted | `references/report-and-tags.md` |
| 5 | **Peer review → write-back** | Self-audit the report against its own citations and counts, fix anything it flags, *then* write the file | `references/self-audit.md`, then the protocol below |

Before you build the verification method, read `references/fixtures.md`, the reviewed
example set (R-15). It is the expected-behavior contract for stages 2 to 4: your triage and
aggregation should reproduce those tiers on those claims. If they don't, the logic is
wrong, not the fixtures.

## The five lenses (summary: full method in the reference doc)

Fired **per claim, independently, in parallel**, STORM-style (one thread per lens, no
cross-talk until results merge), but only the lenses that pass triage for that claim:

- **Practitioner**: does this hold up in applied/operational reality, not just theory?
- **Academic**: what do peer-reviewed sources actually say, including explicit
  contradictions of popular belief?
- **Skeptic**: what is the strongest argument *against* this claim?
- **Economist**: who profits from this claim being believed; what incentive shapes it?
  (unusually load-bearing for AI/tech content, where claims ride commercial hype)
- **Historian**: has an equivalent idea played out before, and how did it resolve?

Not every lens applies to every claim (a Big-O bound has no Economist angle). Triage
first, fire narrowly. See `references/multi-perspective-verification.md`.

## Tiers (summary: full aggregation rule in the reference doc)

Adapted from `technical-research-survey` (a skill in the author's private vault, not
shipped in this repo; its "Confidence tiers in research output"
section): keep CONFIDENT / UNVERIFIED / SPECULATIVE, **drop INFERENCE** (that tier is
specific to claims about the user's own custom hardware, irrelevant here), **add
DISPUTED** (sources actively contradict the claim, the exact case a lecturer stating
something wrong produces, which none of the borrowed tiers name).

Priority order when collapsing several lens verdicts into one tier:
**DISPUTED** (any fired lens surfaces a direct contradiction) → **CONFIDENT** (≥2 lenses
independently corroborate) → **UNVERIFIED** (exactly one lens supports, none contradict)
→ **SPECULATIVE** (no fired lens found evidence either way). A single disconfirmation
outweighs several sources that merely don't address the claim.

## Write-back safety protocol (STAGE 5: non-negotiable)

This skill patches the **same danger zone** `lecture-walkthrough` documents as a repeat
source of corruption: the region just above the `## Full Text` fenced code block has
silently swallowed or destroyed the transcript before (see that skill's step 6 patch
pitfall and its NC-0018 incident note; NC-0018 is an entry in the author's private
vault, not shipped in this repo). The Vetting Report inserts *directly adjacent*
to that block. Therefore:

1. **Use `write_file`, never a targeted `patch`.** Read the whole file, build the new
   content in memory (frontmatter + metadata + walkthrough + any `## References` +
   `## Vetting Report` + `## Full Text` + transcript fence), write it in one shot. This
   is Option A from `lecture-walkthrough` step 6, the only safe editor for this region.
   **Copy the frontmatter and the `## Full Text` block verbatim** from what you read,
   never retype either. Retyped frontmatter is how `id:` lines were lost on 2026-07-08.

2. **Placement of `## Vetting Report`:** immediately after `## References` if that
   section exists, otherwise immediately before `## Full Text`. **Note:** the test file
   `NC-0021_1-introduction-and-scope.md` has *no* `## References` section, so there it
   goes right before `## Full Text`. Handle both cases; do not assume References exists.

3. **After writing, run all three gates:**

   ```bash
   cd $CATALOG_ROOT
   # (a) transcript fence intact: MUST print exactly 2
   sed -n '/^## Full Text$/,$ p' transcripts/<cat>/FILE.md | grep -c '^```$'
   # (b) storage invariants intact (id: present, category/folder, no dup): MUST exit 0
   python3 scripts/transcript.py verify
   # (c) no tag leaked past the fence: MUST print exactly 0
   sed -n '/^## Full Text$/,$ p' transcripts/<cat>/FILE.md | grep -c 'see Vetting Report'
   ```

   If (a) is not `2`, (b) is non-zero, or (c) is not `0`, the write damaged the file,
   restore from the copy you read in step 1 and redo. Do not leave a damaged file and
   "flag it." Gate (c) exists because gate (a) alone cannot detect this failure: a tag
   inserted *between* the two fence markers still leaves the fence count at 2, "the
   fence survived" and "nothing between the fences changed" are different claims
   (2026-07-10 NC-0021 live run: 5 tags landed inside `## Full Text` this way, see the
   matching Pitfalls entry).

4. **Blast radius:** the only differences between the before and after file must be the
   new `## Vetting Report` section and the inline tags. Nothing else, not frontmatter,
   not the walkthrough prose beyond the tags, not a byte of `## Full Text`, may change.

## Acceptance gates (from the build brief)

Run these in a live agent session. The Hermes tools `web_search` / `execute_code` /
`delegate_task` / `browser_navigate` are the reference implementation; outside Hermes,
use your agent's equivalents (web search, code execution, sub-agents). The original
gate file is NC-0021 in the author's vault; run the gates against any real transcript
entry of your own.

- **Fixture check**: run the triage + aggregation against all fixtures in
  `references/fixtures.md`; each must land on its expected tier or the mismatch is
  documented and accepted before proceeding.
- **Self-audit check**: the `references/self-audit.md` pass runs and any finding is
  *resolved*, not logged, before the file is written.
- **Live-file check**: pointed at `transcripts/<category>/<a real transcript entry in
  your catalog>.md`,
  produces a `## Vetting Report` positioned per rule (2) with inline tags on only the
  non-confident claims.
- **Corruption check (exact command):**
  `sed -n '/^## Full Text$/,$ p' transcripts/<category>/<a real transcript entry in your catalog>.md | grep -c '^```$'`
  must print `2`.
- **Tag-boundary check (exact command):**
  `sed -n '/^## Full Text$/,$ p' transcripts/<category>/<a real transcript entry in your catalog>.md | grep -c 'see Vetting Report'`
  must print `0`. A claim with no non-confident mention anywhere in the editable
  walkthrough prose gets its tier recorded in the `## Vetting Report` table only; never
  place its inline tag inside `## Full Text` for lack of anywhere else to put it.
- **Blast-radius check**: diff before/after; only the report and the inline tags changed.
- **Scope check**: `scripts/transcript.py`, `000-dashboard/Index.md`, and the domain
  indices are untouched.

## Sub-agent tool caveat (if you fan out the lenses via delegate_task)

Sub-agents spawned by `delegate_task` **do not get `web_search` / `web_extract`**, those
are Hermes host tools only (documented in `technical-research-survey`, its subagent
tool-use pitfalls). A sub-agent firing a lens must use the DuckDuckGo-lite scraping
pattern inside `execute_code` (that skill's Search Fallback Strategy, Layer 1) or
`browser_navigate` for specific URLs. Put this in the `context` field, not `goal`.

## Pitfalls

- **The `## Full Text` fence is sacred.** Everything above is editable; the transcript
  is the primary source and must survive byte-for-byte. Gate (a) above only proves the
  two fence markers survived; it does not prove nothing changed between them, that is
  what gate (c) is for.
- **A claim can live only inside the transcript, with no home in the prose above it.**
  When that happens, do not tag it in `## Full Text`, the whole point of the fence is
  that it never changes. Record its tier in the `## Vetting Report` table and leave it
  untagged inline: the table is the complete record, inline tags are a bonus "flash,"
  not a completeness requirement. (2026-07-10: the NC-0021 live run tagged 5 such
  claims, Lovelace's "first programmer" label, the Turing/Enigma "won the war" line, the
  ~94% chimp-DNA figure, the Genesis "man runs into a woman" example, and the
  population-bottleneck figure, directly inside the transcript because none of them
  recur in the walkthrough prose. Caught by an independent post-run diff review, not by
  this skill's own self-audit stage, which checked tag counts and fence count but never
  tag location. Repaired by restoring `## Full Text` byte-for-byte from git HEAD.)
- **No em dashes, ever (D-12).** The `## Vetting Report`, inline tags, and any prose
  this skill writes never use the em dash character or `--` as punctuation: use a
  comma, a colon, or two sentences (D-12 in `docs/STORAGE_PROTOCOL.md`; the
  whole catalog was scrubbed of them on 2026-07-09).
- **Confident claims stay untagged.** Inline tags go on non-confident claims *only*,
  tagging everything defeats the signal. The `## Vetting Report` lists every checked
  claim; the prose only flashes the ones that need a second look.
- **Don't over-extract.** Rhetorical framing, the Hook, the Punchline, and the raw
  transcript are not claims. See `references/claim-extraction.md` for the exclusions,
  over-extraction floods the report with SPECULATIVE opinion rows and buries the real
  DISPUTED findings.
- **A bare tier label is not a finding.** DISPUTED/UNVERIFIED/SPECULATIVE rows must name
  the specific conflict (which lens, what it found, where the disagreement is), not just
  the label. That is stage 3's whole job.
- **This skill can hallucinate a citation as easily as any other.** The self-audit
  (stage 5) exists because a fabricated source or a miscounted tier would otherwise go
  straight into the file. It is not optional and it fixes rather than flags.
- **Not every load-bearing claim is worth extracting (D-19, 2026-07-11).** D-4's five
  types are the syntactic filter, does this claim have a checkable form. D-19 adds a
  semantic one on top, is this claim doing narrative work for the content's own
  argument, or is it illustrative color in service of a separate point. NC-0021's
  checked claims (chimp-DNA percentage, Lovelace's "first programmer" label, the
  Turing/Enigma "won the war" line, the Genesis example, the population-bottleneck
  figure, Minsky's date, the riddle) are all color under this rule, a credentialed
  academic lecture told for the user's own project use, not a source pushing a
  narrative. `references/fixtures.md`'s F1-F8 (D-15, locked) stay valid for stage 2-4
  tiering, but every one is drawn from NC-0021, so none would reach stage 1 extraction
  under D-19. A stage-1 fixture set built from genuinely narrative-pushing content does
  not exist yet. D-19 is pinned in the author's private vault decision log, not in
  this repo.
- **A named-claim request is not carte blanche to skip D-19's classification silently
  (D-20, 2026-07-11).** Deployment is manual only, there is no automated trigger or
  credibility-based queue (dropped as moot; D-20 is pinned in the author's private
  vault decision log, not in this repo), the user
  invokes this directly on a whole file or on one named claim. When a named-claim
  request targets something the sixth exclusion category would classify as color, do
  not just extract it (silently overriding D-19) and do not just decline it (silently
  overriding the user's direct request): say what the classification is and confirm
  before proceeding. Only whole-file "vet this walkthrough" requests run the D-19
  exclusion untouched.
