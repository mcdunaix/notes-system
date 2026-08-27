# Vetting Fixtures: Reviewed Example Set (R-15)

The expected-behavior contract for stages 2–4 (triage → firing → aggregation). This is
not documentation; it is the **test-vector set that must be reviewed before the
verification logic is trusted** (convention R-15, test vectors before implementation).
Every claim below is real, drawn from `transcripts/ai-ml/NC-0021_1-introduction-and-scope.md`
(MIT 6.034 Lecture 1, Patrick Winston).

Each fixture is a quintuple: **claim → which lenses should fire → per-lens expected
finding → ground-truth aggregate tier → one-line why**. A correct run of the skill
reproduces the tier in column 4. A mismatch means the logic is wrong (or a fixture is,
which is what this review decides), not that the run "found something new."

**Status: LOCKED (2026-07-10).** The three judgment calls (F3, F5, and the triage on
F8) are ruled on their encoded defaults; rulings and rationale in the final section.
This set is the binding expected-behavior contract for the stage 2-4 build.

## Summary

| # | Claim (abbrev.) | Lenses fired | Expected tier |
|---|-----------------|--------------|---------------|
| F1 | Turing's paper, 1950 | Academic, Historian | **CONFIDENT** |
| F2 | MYCIN diagnosed blood/bacterial infections | Academic, Practitioner | **CONFIDENT** |
| F3 | Minsky's *Steps Toward AI*, dated 1960 | Academic, Historian | **DISPUTED** |
| F4 | Cognitive "combine concepts" leap ~50,000 yrs ago (Chomsky) | Academic, Skeptic, Historian | **DISPUTED** |
| F5 | Gate scheduling saved Delta ~$500K/day in jet fuel | Economist, Skeptic, Practitioner | **DISPUTED** |
| F6 | Gate-scheduling expert systems were deployed at Atlanta | Practitioner | **UNVERIFIED** |
| F7 | "The MIT Definition of AI: algorithms enabled by constraints…" | Academic | **SPECULATIVE** |
| F8 | Farmer-fox-goose-grain has $2^4 = 16$ states | *(none, analytic)* | **CONFIDENT** |

Tier coverage: CONFIDENT ×3 (two by lens-agreement, one analytic), DISPUTED ×3,
UNVERIFIED ×1, SPECULATIVE ×1.

---

## F1: Turing's paper (1950) → CONFIDENT

- **Claim:** Turing's paper appeared in 1950 (the "Ages of AI" table, Dawn Age row).
- **Lenses fired:** Academic (publication record), Historian (AI-history timeline).
  Practitioner/Economist/Skeptic not live for a bare historical date.
- **Expected findings:** Academic, "Computing Machinery and Intelligence," *Mind* 59(236),
  Oct 1950; corroborates. Historian, every standard AI timeline anchors the Turing test
  to 1950; corroborates.
- **Aggregate:** ≥2 lenses corroborate, none contradict → **CONFIDENT**.
- **Why:** the canonical well-known date; two independent lenses agree cleanly. This is the
  baseline "confident historical date" case (build brief, item 8 example #1).

## F2: MYCIN diagnosed blood/bacterial infections → CONFIDENT

- **Claim:** MYCIN was an expert system for blood/bacterial infection diagnosis
  (Expert Systems Age row).
- **Lenses fired:** Academic (the primary literature), Practitioner (was it a real,
  evaluated system?).
- **Expected findings:** Academic, Shortliffe's MYCIN (Stanford, ~1972–76) diagnosed
  bacteremia and meningitis and recommended antibiotics; corroborates. Practitioner,
  a real rule-based system, formally evaluated against clinicians; corroborates (with the
  honest caveat it was never deployed clinically, note in the map, doesn't change tier).
- **Aggregate:** ≥2 lenses corroborate, none contradict → **CONFIDENT**.
- **Why:** named result, well-documented; the "never actually deployed" nuance belongs in
  the map, not the tier. It doesn't contradict the diagnosis claim.

## F3: Minsky's *Steps Toward AI*, dated 1960 → DISPUTED

- **Claim:** Minsky's *Steps Toward AI* is dated 1960 (Dawn Age row).
- **Lenses fired:** Academic (publication record), Historian (timeline).
- **Expected findings:** Academic, *Steps Toward Artificial Intelligence*, Proceedings of
  the IRE 49(1), **January 1961**; contradicts "1960." Historian, timelines cite 1961; a
  draft/report version did circulate in 1960 (the nuance).
- **Aggregate:** a fired lens directly contradicts the stated date → **DISPUTED**.
- **Why:** the published date is 1961; a reader taking "1960" as the citation year would be
  wrong. The map must carry the nuance ("1961 published; 1960 draft existed"). That is
  exactly what the contradiction map is for. The *attribution* to Minsky is CONFIDENT and
  is a separate row (splitting rule); only the split-off date is DISPUTED.

## F4: Cognitive "combine concepts" leap ~50,000 years ago → DISPUTED

- **Claim:** "shortly before 50,000 years ago, some small group of us acquired the ability
  to take two concepts and combine them to make a third", the sudden cognitive leap,
  attributed to Chomsky.
- **Lenses fired:** Academic (paleoanthropology), Skeptic (strongest counter), Historian
  (how the "Great Leap" debate resolved). Also a term-in-source / attribution check on the
  Chomsky quote.
- **Expected findings:** Academic, McBrearty & Brooks (2000), "The revolution that wasn't"
  (*J. Human Evolution*), directly argues modern behavior accreted gradually over
  ~200–300 ky in Africa, contradicting a sudden ~50 kya event. Skeptic, the "Upper
  Paleolithic Revolution" framing is a contested minority position, not settled fact.
  Historian, the sudden-leap model has been progressively undercut since ~2000.
- **Aggregate:** a fired lens surfaces a direct contradiction → **DISPUTED**.
- **Why:** presented as a factual framework for human cognition; the sudden-50-kya timing
  is genuinely contested science. Doubles as the "attributed quote checked against source"
  case (build brief, item 8 example #2), confirm the wording/attribution to Chomsky *and*
  test the empirical claim; both feed the map.

## F5: Gate scheduling saved Delta ~$500K/day in jet fuel → DISPUTED

- **Claim:** rule-based aircraft/gate scheduling at Atlanta saved Delta ~$500,000/day in
  jet fuel (Expert Systems Age row).
- **Lenses fired:** Economist (who benefits from the figure), Skeptic (is it audited?),
  Practitioner (did such a system operate?).
- **Expected findings:** Economist, the specific per-day figure appears only in retellings
  of Winston's own lectures; expert-systems-era ROI numbers are documented as systematically
  overstated in AI-winter retrospectives (strong incentive to inflate). Skeptic, no
  primary or audited source for the $500K/day figure could be located. Practitioner, a
  gate-scheduling system plausibly existed (see F6), but that does not source *this number*.
- **Aggregate:** Economist/Skeptic surface a disconfirming characterization of the figure,
  and no lens independently corroborates it → **DISPUTED**.
- **Why:** this is the "Economist or Skeptic alone triggers DISPUTED" case (build brief,
  item 8 example #3) and demonstrates item 4's rule that a single disconfirmation outweighs
  non-addressing sources. **See reviewer decision below. This is the DISPUTED/UNVERIFIED
  boundary and the fixture most likely to need your call.**

## F6: Gate-scheduling expert systems deployed at Atlanta → UNVERIFIED

- **Claim:** rule-based gate/aircraft-scheduling expert systems were actually deployed at
  the Atlanta airport (the existence claim, setting the dollar figure aside. That's F5).
- **Lenses fired:** Practitioner (deployment record). Economist/Skeptic not decisive for a
  bare existence claim once the money figure is split off.
- **Expected findings:** Practitioner, one trade/industry source describes gate-assignment
  expert systems in airline operations in that era; nothing contradicts deployment; only a
  single independent source found.
- **Aggregate:** exactly one lens supports, none contradict → **UNVERIFIED**.
- **Why:** genuinely might be true, single-source, uncorroborated. Shows the
  UNVERIFIED/DISPUTED distinction against F5: same underlying anecdote, but the *existence*
  is merely unconfirmed while the *specific figure* is actively doubted.

## F7: "The MIT Definition of AI…" asserted as the definition → SPECULATIVE

- **Claim:** "The MIT Definition of AI: Algorithms enabled by constraints exposed by
  representations that support models targeted at thinking, perception, and action",
  stated as *the* definition (Core Idea).
- **Lenses fired:** Academic (is this a consensus definition?).
- **Expected findings:** Academic. This is Winston's idiosyncratic framing, not a
  consensus definition (contrast Russell & Norvig's agents-that-perceive-and-act, or
  McCarthy's). It is neither corroborated as standard nor contradicted as false. It's a
  framing, not a falsifiable proposition.
- **Aggregate:** no lens finds it true or false → **SPECULATIVE**.
- **Why:** a definition asserted as fact but not externally adjudicable. In scope (it's
  stated as *the* definition, not flagged as personal), but tiers SPECULATIVE rather than
  being excluded, the boundary between "coinage, exclude" and "definition-as-fact, tier"
  from `claim-extraction.md`.

## F8: Farmer-fox-goose-grain has $2^4 = 16$ states → CONFIDENT (analytic)

- **Claim:** the puzzle's state space is $2^4 = 16$ (four entities, each on one of two
  banks) (Core Idea, state-graph passage).
- **Lenses fired:** **none.** Triage route 2, analytically verifiable.
- **Expected findings:** by inspection, 4 entities × 2 banks = $2^4 = 16$; arithmetic holds.
- **Aggregate:** analytic route, math checks out → **CONFIDENT** (not SPECULATIVE).
- **Why:** the edge case that locks triage rule 2. Without the analytic route, a self-
  evidently-true claim would fall through to SPECULATIVE ("no lens found evidence"), wrong.
  A pure arithmetic identity is CONFIDENT by inspection with zero lenses fired. (If the
  lecturer's arithmetic were wrong, the same route yields DISPUTED.)

---

## Reviewer decisions: RULED, set locked (the R-15 gate, 2026-07-10)

All three calls ruled on their encoded defaults in the 2026-07-10 button-up session
(notes D-15). Provenance: ruled by Claude on the defaults with independent concurring
review, not an interactive user confirmation; reopen any item by number if the
precedent proves wrong in practice.

1. **F5 stays DISPUTED (Economist escalation confirmed).** "The figure is unsourced
   *and* its class is documented as systematically overstated" counts as a disconfirming
   characterization, not mere absence of sources. Concurring reasons: D-7's aggregation
   already names Skeptic/Economist as the lenses designed to trigger DISPUTED this way,
   and the build brief (item 8) mandates a fixture where Economist or Skeptic alone
   triggers DISPUTED; F5 is that fixture, so re-tiering it UNVERIFIED would leave the
   mandated case uncovered. Precedent set: unsourced hype figures in a
   documented-overstated class tier DISPUTED corpus-wide.

2. **F3 stays DISPUTED (published year is canonical).** A stated year that is not the
   canonical publication year tiers DISPUTED even when a draft/report supports it; the
   contradiction map carries the nuance ("1961 published; 1960 draft existed"). A
   defensibility loophole for near-miss dates would defeat the layer's purpose: a reader
   citing "Minsky 1960" cites wrongly, and the map preserves the full story anyway.
   Precedent set for every preprint-vs-publication date in the catalog.

3. **F8 analytic route confirmed (zero lenses is legal).** Arithmetic/logical claims
   resolve by inspection: CONFIDENT when the math holds, DISPUTED when it does not,
   never forced through a lens and never falling through to SPECULATIVE. Without this
   route a self-evidently-true claim would tier SPECULATIVE, which is absurd on its
   face. The rule is design-law for triage even though it postdates the original brief.

A fourth, lower-stakes note stays an open offer (default: not taken): the set is drawn
from one lecture (NC-0021) and covers all four tiers and five lenses, but contains no
Practitioner-lens fixture on a *technical/algorithmic* claim (a complexity bound, an
algorithm's behavior). If wanted, add one from a later MIT 6.034 lecture (e.g., the
search/optimization lectures) before trusting Practitioner triage on that claim class.
