# Claim Extraction (Stage 1)

Turn a walkthrough's prose, block quotes, and tables into a list of discrete,
independently checkable claims. Retrieve widely later; **extract narrowly** now,
the failure mode is over-extraction, which floods the Vetting Report with
un-checkable opinion rows and buries the real findings.

## What counts as a load-bearing claim

A claim is load-bearing if it asserts something about the world that could be *wrong*
and that a reader might carry away as fact. Five types (per protocol decision D-4,
"load-bearing claims only"):

| Type | Example from a lecture | Where it hides |
|------|------------------------|----------------|
| **Named result / attribution** | "Deep Blue beat Kasparov"; "MYCIN diagnosed infections" | Results & Surprising Facts; tables; block quotes |
| **Date** | "Turing's paper (1950)"; "shortly before 50,000 years ago" | History/Ages tables; inline in prose |
| **Number / metric** | "saves Delta $500K/day"; "$2^4 = 16$ states" | Results & Surprising Facts; board-content tables |
| **Attributed quote** | Lovelace: "…no pretensions to originate anything"; a Chomsky quote | Block quotes (`>`) throughout |
| **Definition stated as fact** | "The MIT Definition of AI: algorithms enabled by constraints…" | Core Idea; Knowledge/Toolbox |

## Where to look (walk the walkthrough structure)

The walkthrough follows a fixed template (see `lecture-walkthrough` SKILL.md, its
"Structure template" section). Yield per section:

- **Results & Surprising Facts**: highest yield. Metrics, statistics, dated milestones,
  named systems. Nearly every sentence here is a checkable claim.
- **Block quotes (`>`), anywhere**: attributed claims. Two sub-cases: (a) a quote
  *attributed to a third party* (Lovelace, Chomsky, a cited paper), check the wording
  and the attribution against the source; (b) a quote *from the lecturer's own mouth*
  stating a fact, check the fact. A quote that is pure rhetoric ("purge the word trivial
  from your vocabulary") is not a claim, skip it.
- **Tables**: history/"Ages" tables pack dates + named milestones densely. Each cell
  that names a date, a system, or a metric is its own claim. (In NC-0021 the "Ages of AI"
  table alone yields the Lovelace 1842, Turing 1950, Minsky 1960, MYCIN, $500K/day, and
  Deep Blue 1997 claims.)
- **Core Idea / Knowledge-Toolbox**: definitional claims stated as fact, and any
  named principle presented as established (not as the lecturer's coinage).
- **Board Content**: reconstructed diagrams/tables may carry numeric claims (state
  counts, complexity bounds). Check the numbers, not the ASCII art.

## What to exclude (do not extract)

- **The Hook and the Punchline**: rhetorical framing, motivation, course philosophy.
  "The most simple ideas in AI are often the most powerful" is a thesis, not a checkable
  fact. Skip the whole section unless it embeds a specific dated/numeric/attributed claim.
- **The `## Full Text` block**: that is the source material, not itself a set of claims.
  You *read* it to verify attributed quotes (stage 2), but you never extract claims *from*
  it, only from the walkthrough's own prose.
- **The lecturer's own coinages presented as such**: "the Rumpelstiltskin Principle,"
  "the MIT Definition." These are framings. (Nuance: a *definition asserted as the*
  definition, as if canonical, IS a claim, checkable as "is this the consensus
  definition?" See the F7 fixture: it comes back SPECULATIVE, not excluded, because it's
  asserted as fact rather than flagged as personal.)
- **Pedagogical hedges**: anything the lecturer explicitly marks as uncertain,
  opinion, or "we don't understand this yet." Winston flagging correlation≠causation on
  the attendance scatterplot is self-hedged; extract it only if you want to record the
  hedge, and it will tier SPECULATIVE.
- **Narrative-irrelevant color (D-19)**: a claim can fit one of the five types above and
  still not be worth extracting. Test: would the content's own argument survive if this
  specific claim turned out to be wrong? If yes, it is illustrative decoration, an
  example, an anecdote, historical or scientific flavor, used in service of a separate
  point, skip it regardless of its factual form. If no, the content is using this claim
  to convince the viewer of something, extract it regardless of source credibility. In
  NC-0021 this excludes the chimp-DNA percentage, Lovelace's "first programmer" label,
  the Turing/Enigma "won the war" line, the Genesis example, the population-bottleneck
  figure, Minsky's 1960/1961 date, and the farmer-fox-goose-grain riddle's state count,
  all color in service of teaching AI search concepts, none of it MIT 6.034's own thesis.
  A source's credibility (an anonymous engagement-optimized channel versus a named
  academic) was flagged in D-19 as a signal for where narrative-pushing claims are
  likelier to cluster. In practice (D-20) this plays out informally, in the user's own
  decision to invoke the skill at all, not as logic inside this skill: deployment is
  manual only, there is no automated queue or backlog sweep for credibility to
  prioritize within. It is still never the extraction test itself, run this check on
  every claim regardless of where it came from.

  **Named-claim requests (D-20).** The above is the default when scanning a whole file
  unprompted. If the user names a specific claim (they need it for a project, or they
  are skeptical of it) and this exclusion would otherwise skip it as color, do not
  silently extract it and do not silently decline: state the classification ("this
  reads as color under D-19, not narrative payload") and proceed only after they
  confirm. This override only applies to explicitly named claims, not to this
  exclusion's application during an ordinary whole-file scan.

## Output of this stage

A numbered list. For each claim record:

- **Claim text**: the specific assertion, quoted or tightly paraphrased. One assertion
  per entry. Split compound claims ("Minsky's *Steps Toward AI* (1960)" is two: the
  attribution *and* the date, the attribution can be CONFIDENT while the date is
  DISPUTED, as in fixtures F3).
- **Type**: one of the five above.
- **Location**: section + a short anchor string, so stage 5 can place the inline tag
  and so the write-back knows exactly which prose to tag.
- **Source-internal check needed?**: flag attributed quotes that must be verified
  against the `## Full Text` block or the cited external paper (term-in-source, stage 2).

Hand this list to stage 2 (`multi-perspective-verification.md`) for triage and firing.

## Splitting rule (important)

When a single sentence bundles an attribution and a date/number, split it. The tiers can
differ: the *thing* happened (CONFIDENT) but the *date* the lecturer gave is off by a year
(DISPUTED). Merging them would hide the error under the confident half. This is the single
most common extraction mistake, the fixtures F1/F3 exist to catch it.
