---
name: review-discussion-probe
description: "Use when turning a piece of hardware, an LLM/model, a video, or a topic into a structured, logged catalog note. Three modes: Review (research and breakdown of a specific artifact), Discussion (guided in-depth discussion of a video or artifact), Probe (cutting edge and future development of a topic, with related tech)."
---

# Review / Discussion / Probe: Artifact and Topic Notes

Turn a specific thing (hardware, an LLM or model, a tool, a video) or an open
topic into a structured catalog note that is filed, logged with an NC-XXXX ID,
and linked into the index. This skill is the sibling of `lecture-walkthrough`
(the skill that expands a lecture transcript in place). The catalog protocol
is identical; only the analysis shape differs.

## Catalog root

`$CATALOG_ROOT` is the catalog root: the directory containing
`scripts/transcript.py` (this repo root when the repo is used as the vault).
Set `export CATALOG_ROOT=/path/to/catalog` before running commands.

## Pick a mode

| Mode | Input | Output | Filed in |
|------|-------|--------|----------|
| Review | A specific artifact: hardware device, LLM/model, tool, product | Research + breakdown note, claims verified where possible | `references/` |
| Discussion | A video or artifact | Guided in-depth discussion scaffold (questions, tensions, follow-ups) | `transcripts/<category>/` if video-sourced, else `references/` |
| Probe | A topic | Current state, cutting edge, future trajectories, related tech | `references/` |

The same subject can take all three modes at different times. Review asks
"what is this and is it any good?", Discussion asks "what is worth thinking
hard about here?", Probe asks "where is this going?". Do not mix modes in one
entry; if two modes fit, write two entries and cross-link them.

## Shared protocol (all modes)

1. **Identify the subject precisely.** Model name and version, SKU, commit,
   paper title, video URL. A review of "the M4 MacBook" is not a review of a
   thing, it is a review of a product family; name the exact configuration.
2. **Research primary sources first.** Spec sheets, datasheets, model cards,
   official docs, benchmark leaderboards, the paper or RFC, the source repo.
   Third-party writeups only as corroboration, never as the sole source.
   For open-source tools, vet repo health: stars, commit activity, license,
   maintenance cadence, issue response. Never rely on a vendor's own
   marketing number without a second source or a local test.
3. **Verify what you state.** If you can run it (a local model benchmark, a
   hardware spec cross-check, a command that produces output), run it and
   record the output. Anything you could not verify is labeled unverified in
   the note. A number with no source and no run is a fabrication, not a claim.
4. **Assign the next ID.** `python3 scripts/next-id.py` prints the next
   free NC-XXXX. It scans `transcripts/` and `references/` (plus the
   dashboard Index.md), so a reference entry can never silently collide
   with a transcript entry. Never hand-pick an ID.
5. **Name the file by topic, not by title (D-13).** `NC-XXXX_<slug>.md`
   where `<slug>` comes from the topics phrase you chose. Store the phrase
   in `topics:` frontmatter. The raw source title stays in frontmatter too.
6. **No em dashes, ever (D-12).** The em dash character (U+2014) and `--`
   used as punctuation are both banned. A comma, a colon, or two sentences
   instead. Plain hyphens for structural separators.
7. **Gate.** Transcript entries: `python3 scripts/transcript.py verify`
   must exit 0. Reference entries: `verify` does not scan `references/`
   (documented gap), so run the manual gate:
   `grep -c $'—' references/NC-XXXX_*.md` must print 0 (the literal U+2014
   character is required inside that grep, same as the self-audit command
   in `lab-builder`), and a
   `grep -n -- '--' references/NC-XXXX_*.md` must show no prose uses.
8. **Index.** Add a wikilink to the matching domain/category index
   (`01-engineering/00-Index.md`, `02-culture-society/Index.md`, or the
   category sub-index) so the entry is reachable from Obsidian navigation.
   `transcript.py rebuild` only regenerates the dashboard, never the
   hand-curated indexes.

## Mode 1: Review

**Input:** a specific artifact. **Job:** research it, break it down, give a
verdict, log the note.

Workflow:

1. Name the exact artifact (model, version, configuration, price at time of
   writing if relevant).
2. Gather primary sources: datasheet / spec sheet / model card / official
   docs / benchmark leaderboards / source repo. For a model, record the
   architecture, parameter count, training data note, license, and the
   official evaluation numbers.
3. Run what you can. A local model gets a real inference run with the
   user's own hardware and a recorded output. A hardware claim gets
   cross-checked against the vendor datasheet and at least one independent
   teardown or measurement. Anything not run is labeled unverified.
4. Write the breakdown and verdict, then file it.

Structure template:

```
# <Topic Phrase>

## What it is
One paragraph: what the artifact is, who makes it, where it sits in the
landscape. Not the vendor pitch, your description.

## How it works
The mechanism: architecture, design decisions, key specs in a small table.
Deep enough that a competent reader could explain it to someone else.

## Claims and verification
A table: claim, source, verified yes/no, how (local run output, second
source, or "unverified"). Every number in the note appears here or in a
cited source.

## Strengths
Concrete, evidence-backed. What it is genuinely good at.

## Weaknesses and limits
Concrete. Licensing traps, hardware requirements, benchmark gaps, things
the marketing overstates. For open-source tools: maintenance risk.

## Who it is for
The user profile that should buy/use it, and the one that should not.

## Verdict
A short, direct call: recommended, recommended with conditions, or not
recommended, and the single strongest reason.

## Sources
Primary sources with URLs, each with a one-line relevance note.
```

## Mode 2: Discussion

**Input:** a video or artifact. **Job:** tee up a guided, in-depth
discussion about the topic the source raises. The discussion note is not a
summary (that is `lecture-walkthrough`'s job). It treats the source as a
shared object and structures a real conversation: the questions worth
asking, the tensions worth sitting in, the threads worth pulling.

Workflow:

1. Get the source content. Video: `scripts/transcript.py add <url>
   --topics "..."` if it is a supported platform, else the manual
   yt-dlp pipeline from `lecture-walkthrough`. Artifact: read the primary
   material (paper, spec, documentation) enough to quote it accurately.
2. Identify the topic and the interesting tensions. A discussion with no
   disagreement or puzzle in it is a summary. Find the friction: two claims
   that strain against each other, a convention that is worth questioning,
   an implication the source does not spell out.
3. Build the scaffold below, keeping questions open and non-leading.
4. File it. Video-sourced discussions go in `transcripts/<category>/`
   (frontmatter keeps the source fields, and the raw transcript is
   preserved under `## Full Text` in a fenced block, same rule as
   `lecture-walkthrough`: never drop the fenced transcript). Artifact
   discussions go in `references/` with `kind: discussion`.

Structure template:

```
# <Topic Phrase>: A Guided Discussion

## The source
One paragraph: what the video or artifact is, who made it, and the one
claim or moment that opens the discussion. Cite it.

## Opening frame
The question this discussion is about, stated plainly. One sentence.

## Key questions
Grouped, 2-3 per group. Each question is answerable from the source plus
the reader's own judgment, not a trivia lookup.

## Guided sections
One section per tension. Each section has: the question, the context
(from the source, quoted where possible), and a probe (what to look at or
try to form a view).

## Stretch questions
2-3 questions that go beyond the source: what would have to be true for
the source's strongest claim to hold.

## Related material
Links to catalog entries (NC-XXXX) that touch the same topic.
```

## Mode 3: Probe

**Input:** a topic. **Job:** research the topic and present its cutting
edge, its future development, and the related technology it connects to.

Workflow:

1. Scope the topic tightly. "Mesh networking" is a field; "Reticulum as a
   protocol" is a topic. Write the scope sentence first.
2. Research current state: the foundations, the standards, the dominant
   approaches, who is building them. Primary sources: RFCs, specs, papers,
   official docs, repos with health checks.
3. Map the frontier: what is moving now, preprints, recent releases,
   benchmark results, conference work. Label confidence: shipped, demoed,
   claimed, speculative.
4. Project trajectories: near-term (12-24 months, grounded in concrete
   work), medium-term (2-5 years, reasoned), and speculative (marked as
   such, never presented as forecast).
5. Map related tech: the adjacent ecosystems that interact or compete,
   one line each, linked to catalog entries where they exist.
6. File it in `references/` with `kind: probe`.

Structure template:

```
# <Topic>: State and Trajectory

## Scope
One sentence defining the topic as probed here. What is included, what is
deliberately excluded.

## Current state
The foundations and the dominant approaches, with primary sources. What
is stable and what is still contested.

## Cutting edge
What is at the frontier right now, each item with a source and a
confidence label (shipped / demoed / claimed / speculative).

## Trajectories
- Near term (12-24 months): grounded in concrete work under way.
- Medium term (2-5 years): reasoned from the near term.
- Speculative: explicitly labeled, no false certainty.

## Related tech
Adjacent ecosystems that interact with or compete against this topic, one
or two lines each, linked to catalog entries where they exist.

## Open questions
What a serious student of the topic still does not know, in question form.

## Sources
Primary sources with URLs, each with a one-line relevance note.
```

## Pitfalls

- **Never state an unverified number as fact.** The whole value of a Review
  or Probe is that its claims are checked. If you did not run it and did not
  find a primary source, label it unverified or cut it.
- **Vendor marketing is not a primary source for a claim.** A benchmark
  figure from the vendor's own page needs a second source or a local run
  before it goes in the note as verified.
- **Review one artifact, not a family.** "M4 MacBook" (family) vs "MacBook
  Pro 14-inch M4 Max, 48 GB" (artifact). The breakdown and verdict only
  make sense at artifact granularity.
- **A Discussion with no friction is a summary in disguise.** If every
  section is a restatement, stop and find the tension, or switch to
  `lecture-walkthrough`.
- **Probe scope creep.** A probe of "AI" is a book; a probe of "the
  transformer attention mechanism's efficiency frontier" is a note. Write
  the scope sentence before researching.
- **Do not hand-pick NC IDs.** `scripts/next-id.py` scans both
  `transcripts/` and `references/`. The author's vault once had a live ID
  collision because reference files were invisible to the allocator; the
  helper closes that gap. Use it.
- **No em dashes, no `--` (D-12).** Same rule as every other note in the
  catalog. A comma, a colon, or two sentences.
- **References entries skip the automated gate.** `transcript.py verify`
  only scans `transcripts/`. Run the manual D-12 grep from step 7 of the
  shared protocol on every reference entry you write.
- **Index it or it does not exist.** `rebuild` regenerates only the
  dashboard. The hand-curated domain and category indexes are the primary
  Obsidian navigation; a filed note without a wikilink is invisible.
- **Keep entries self-contained.** This repo ships an empty database. A
  note that says "as discussed in the earlier session" with no reference is
  broken; cite by NC-XXXX or spell it out.
