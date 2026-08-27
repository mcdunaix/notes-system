# Vetting Report + Inline Tags (Stage 4 output, Stage 5 placement)

Two surfaces for the same verdicts (protocol decision D-3, "output surface: both"): a
`## Vetting Report` section that lists every checked claim, and inline tags on only the
non-confident claims in the prose. Confident claims stay visually untouched, the tags
are a signal, and a signal on everything is noise.

## The `## Vetting Report` section

**Placement:** immediately after `## References` if that section exists; otherwise
immediately before `## Full Text`. Follows the same rule `lecture-walkthrough` uses for
its own References block (metadata about the lecture sits between the walkthrough and the
raw transcript). **The test file `NC-0021_1-introduction-and-scope.md` (an entry in the author's
private vault, not shipped in this repo) has no
`## References` section**, there the report goes directly before `## Full Text`. Never
place it after the `## Full Text` code block.

**Structure:** a one-line summary count, then one table.

```markdown
## Vetting Report

_14 claims checked: 9 confident, 3 unverified, 1 speculative, 1 disputed. Lenses fired:
practitioner, academic, skeptic, economist, historian (per claim, triaged). Advisory,
see D-2. Vetted <describe method: e.g. "via DDG-lite + arXiv + primary papers">._

| # | Claim | Tier | Lens Findings | Sources |
|---|-------|------|---------------|---------|
| 1 | Turing's "Computing Machinery and Intelligence" published 1950 | CONFIDENT | Academic + Historian concur | Mind 59(236), 1950 |
| 2 | Minsky's *Steps Toward AI* dated 1960 | DISPUTED | Academic/Historian: paper is 1961 (Proc. IRE 49), off by a year | Proc. IRE 49(1), Jan 1961 |
| 3 | Gate-scheduling saved Delta ~$500K/day in jet fuel | DISPUTED | Economist: figure only in lecture retellings; expert-systems ROI documented as overstated. Skeptic: no audited primary source | (no primary source located) |
| 4 | Gate-scheduling expert systems were deployed at Atlanta | UNVERIFIED | Practitioner: one trade source confirms deployment; none contradict | <single source> |
| 5 | "The MIT Definition of AI: algorithms enabled by constraints…" | SPECULATIVE | Academic: idiosyncratic to Winston, not a consensus definition; no true/false | (none) |
```

### Column rules

- **Claim**: the specific assertion, tightly worded. One claim per row. A compound
  sentence that split into attribution + date (see `claim-extraction.md`) gets two rows.
- **Tier**: DISPUTED / CONFIDENT / UNVERIFIED / SPECULATIVE (bare word, no styling).
- **Lens Findings**: this column carries the contradiction map from stage 3.
  - **CONFIDENT rows may be terse:** just which lenses corroborated ("Academic + Historian
    concur"). No need to spell out agreement.
  - **DISPUTED / UNVERIFIED / SPECULATIVE rows must name the specific conflict**: which
    lens, what it found, where the disagreement is. Not "sources disagree." Write
    "Practitioner: standard in production per X; Academic: Y (2024) found it ineffective
    at scale, contradicts." A bare tier with a vague note means stage 3 was skipped.
- **Sources**: concrete citation(s) the lenses produced; write "(none located)" if none
  was located (itself
  informative for UNVERIFIED/SPECULATIVE). Every citation here is checked by the stage-5
  self-audit (term-in-source) before this table reaches disk.

### Summary count

One line above the table. Must be **arithmetically consistent with the rows**, the
self-audit checks that the four tier counts sum to the "N claims checked" figure and match
the actual rows. A count that disagrees with its own table is the most common self-audit
catch.

Escape `|` inside any claim/finding cell as `\|` (Obsidian renders raw pipes as column
breaks, the same escaping `transcript.py` applies to index rows).

## Inline tags

Tag **only non-confident claims** (DISPUTED, UNVERIFIED, SPECULATIVE). CONFIDENT claims
get nothing. That is the design. Place the tag **immediately after the claim** in the
walkthrough prose, pointing back to the report rather than duplicating the citation:

```markdown
...rule-based gate scheduling saved Delta $500K/day in jet fuel [DISPUTED, see Vetting Report].
...deployed at the Atlanta airport [UNVERIFIED, see Vetting Report].
> "The MIT Definition of AI: algorithms enabled by constraints..." [SPECULATIVE, see Vetting Report]
```

Format: `[<TIER>, see Vetting Report]`. Rules:

- One tag per tagged claim, right after it. Do not restate the source inline, the report
  row holds the citation; the tag is a pointer.
- **Tables and block quotes:** put the tag at the end of the relevant table cell or on the
  line right after the block quote. Inside a table cell, keep it in the same cell as the
  claim so alignment survives. Never break a table row or a `>` quote across the tag.
- **LaTeX:** place the tag outside the math delimiters, `$2^4 = 16$ [DISPUTED, see Vetting
  Report]`, never inside `$...$`.
- **The tag's tier must equal the report row's tier** for the same claim, the self-audit
  cross-checks this. If you retier a claim during stage 5, fix the tag too.

## Why point back instead of inline citations

`technical-research-survey` (a skill in the author's private vault, not shipped in
this repo) uses an inline style (`[single source: <name>]`) built for
research-doc prose. A walkthrough mixes prose, block quotes, tables, and LaTeX, inline
citations would wreck table alignment and clutter quotes. Centralizing every citation in
the report table and leaving only a typed pointer in the prose keeps the walkthrough
readable while still flagging exactly what to distrust.
