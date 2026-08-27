# Multi-Perspective Verification (Stages 2–4)

Check each extracted claim from several independent angles, then collapse the angle
verdicts into one tier. This is the core of the skill and the part the fixture set
(`fixtures.md`) is the contract for. Build it to reproduce the fixtures.

## The mechanism, borrowed and inverted from STORM

Stanford STORM (github.com/stanford-oval/storm) fans out one independent conversation
thread *per persona* and merges the results only at the end, no cross-talk between
threads (`_run_conversation`'s thread-pool pattern). We reuse that **fan-out mechanism**
and invert its **purpose**: STORM asks N personas to *generate* coverage for a new
article; we fire N fixed lenses to *stress-test the truth* of a claim that already exists.

Two consequences of the inversion:
- **No persona-generation step.** STORM generates topic-specific personas via an LLM call
  plus a Wikipedia-TOC scrape, tuned for coverage. We use five *fixed* lenses tuned for
  disconfirmation. There is nothing to generate, skip straight to firing.
- **STORM is not a fact-checker.** Its own authors state it has no fact-checking
  mechanism and emits citations "for human review." Do not adopt it wholesale; the only
  reusable part is the independent-thread fan-out.

Each fired lens is one independent retrieval + reasoning thread. Behind every lens sits
the **same retrieval apparatus** as `technical-research-survey`: its source-priority
table (GitHub → paper-collection repos → conference proceedings → high-impact journals →
arXiv → official sites → survey articles), its DDG-lite-in-`execute_code` fallback, and
its **term-in-source** verification (does the cited source actually contain the term or
quote attributed to it, the check that caught a fabricated term in a past session). The
lens defines *what question to ask*; that apparatus is *how you answer it*.

## The five fixed lenses

| Lens | The question it asks | Most likely to surface |
|------|----------------------|------------------------|
| **Practitioner** | Does this hold up in applied/operational reality, not just theory? | A claim that's true in the lab but false at scale, or vice-versa |
| **Academic** | What do peer-reviewed sources actually say, including explicit contradictions of the popular version? | Wrong dates, misattributions, superseded results |
| **Skeptic** | What is the strongest argument *against* this claim? | Overstated certainty, cherry-picked framing |
| **Economist** | Who profits from this being believed? What incentive shaped the narrative? | Hype-inflated metrics, vendor ROI figures |
| **Historian** | Has an equivalent idea played out before, and how did it resolve? | Recurring cycles (AI winters), origin-date errors |

Economist and Skeptic are the two lenses most likely to trigger DISPUTED, by design,
they are actively looking for the disconfirmation the other three might miss.

## Triage: which lenses fire for this claim

Do not fire all five on every claim. For each extracted claim, decide which lenses could
*plausibly surface new information*, and fire only those. A Big-O bound has no meaningful
Economist angle; a commercial ROI figure has no Historian angle but a decisive Economist
one.

Triage produces one of three routes per claim:

1. **Externally checkable → fire the applicable lenses.** The normal path. Pick the
   lenses whose question is live for this claim (usually 2–3, occasionally all five for a
   hype-laden historical claim). Record *why* each fired or was skipped, stage 5 audits
   the triage, and `fixtures.md` reviews it.
2. **Analytically verifiable → check by inspection, fire zero external lenses.** Pure
   arithmetic or logical necessity (`$2^4 = 16$`, "a 7-crossing solution exists").
   Verify by doing the math/enumeration yourself. This route resolves to **CONFIDENT** if
   it checks out or **DISPUTED** if the arithmetic is actually wrong. It does **not**
   fall through to SPECULATIVE. (Without this route, self-evidently-true claims would
   wrongly tier SPECULATIVE because "no lens found evidence." Fixture F8 exists to lock
   this in.)
3. **Not a factual claim → drop.** If triage reveals the "claim" is pure opinion or
   rhetoric that slipped past extraction, remove it rather than tier it.

## Firing a lens (independent thread)

For each fired lens, run one independent retrieval + reasoning pass:

1. Form the lens's question about *this specific claim* (e.g. Academic on "Minsky *Steps
   Toward AI* 1960": "In what year and venue was Minsky's *Steps Toward Artificial
   Intelligence* actually published?").
2. Retrieve via the `technical-research-survey` apparatus, source-priority order, its
   DDG-lite pattern, browser for rich pages. For attributed quotes, run **term-in-source**:
   confirm the quote/term appears in the cited paper or the `## Full Text`, not just in
   the lecturer's paraphrase.
3. Record a per-lens verdict: **corroborates** / **contradicts** / **no direct evidence**,
   each with its source(s). "Contradicts" requires a source that directly conflicts with
   the claim, not merely one that fails to mention it.

If you fan the lenses out across `delegate_task` sub-agents: they lack `web_search` /
`web_extract` (host-only). Instruct them, in the `context` field, to use the DDG-lite
`execute_code` pattern or `browser_navigate`. See `technical-research-survey`'s subagent
tool-use pitfalls.

## Stage 3: contradiction map

For every claim that is *not* going to come back CONFIDENT, record the specific conflict,
not just the eventual label: which lens found what, from which source, and where exactly
the disagreement sits. Example, for the $500K/day figure:

> Economist: the figure appears only in retellings of Winston's own lecture; expert-
> systems-era ROI numbers are documented as systematically overstated in AI-winter
> retrospectives. Skeptic: no primary/audited source for the specific per-day figure.
> No lens corroborated it independently. → the disagreement is between the claim's
> confident presentation and the absence of any auditable basis, plus one lens actively
> characterizing figures of this class as inflated.

This map is what makes the Vetting Report's non-confident rows worth reading and what the
inline tag points back to. A row that just says "DISPUTED" with no map has skipped stage 3.

## Stage 4: aggregation: lens verdicts → one tier

Collapse the per-lens verdicts into a single tier. Evaluate in this priority order and
stop at the first match:

1. **DISPUTED**, *any* fired lens surfaced a source that **directly contradicts** the
   claim. A single disconfirmation outweighs several lenses that merely didn't address it.
   (Also the tier for the analytic route when the arithmetic is wrong.)
2. **CONFIDENT**, **≥2 fired lenses independently corroborate** and none contradict.
   (One corroborating source is UNVERIFIED, not CONFIDENT, this threshold is inherited
   from `technical-research-survey`'s tier definitions on purpose.) Also the tier for the
   analytic route when the math checks out.
3. **UNVERIFIED**, **exactly one** fired lens found supporting evidence and none found
   contradicting evidence. Single-source support; genuinely might be true, not confirmed.
4. **SPECULATIVE**, **no fired lens found direct evidence either way**: the claim is
   untestable, an opinion asserted as fact, or too vague to check. (Not the same as the
   analytic route, that never lands here.)

### Tier set, and why it differs from the borrowed one

Taken from `technical-research-survey`'s "Confidence tiers in research output," with two
deliberate changes (protocol decision, work item 4 of the build brief):

- **Dropped INFERENCE.** That tier is defined there as "a number extrapolated about the
  user's own hardware/substrate." There is no custom-hardware here, the tier has no
  referent for lecture content.
- **Added DISPUTED.** None of the borrowed four name the case the user actually worries
  about: a lecturer stating something that is *actively wrong*. UNVERIFIED means "nobody
  confirmed it"; DISPUTED means "a source says it's false." That distinction is the whole
  point of the skill.

Keep the tier *names* identical to the source skill where they overlap (CONFIDENT,
UNVERIFIED, SPECULATIVE) so a reader who knows one vocabulary knows both.

## Worked micro-example (fixture F3)

Claim (split from "Minsky's *Steps Toward AI* (1960)"): **the date 1960**.
Triage: externally checkable; fire Academic (publication record) and Historian (AI-history
timeline). Economist/Practitioner/Skeptic not live for a bare publication date.
- Academic: *Steps Toward Artificial Intelligence*, Marvin Minsky, **Proceedings of the
  IRE, vol. 49, Jan. 1961**, contradicts "1960."
- Historian: standard AI-history timelines place it in 1961, contradicts.
Aggregation: a fired lens directly contradicts → **DISPUTED**. Contradiction map: "lecture
says 1960; the paper is 1961 (Proc. IRE 49). Off by one year." Note the *attribution* to
Minsky is CONFIDENT, only the split-off date is DISPUTED (see the splitting rule in
`claim-extraction.md`).
