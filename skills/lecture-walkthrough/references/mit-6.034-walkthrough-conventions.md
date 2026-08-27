# MIT 6.034 (Patrick Winston) Walkthrough Conventions

Walkthrough format for Patrick Winston's MIT 6.034 lecture series.
Transcribed from Fall 2010 OCW lectures hosted on the MIT OpenCourseWare YouTube channel.

## Frontmatter Requirements

The script (`transcript.py`) generates bare frontmatter. Add these fields:

```yaml
course: "6.034 Artificial Intelligence, Fall 2010"
instructor: "Patrick Winston"
categories: ["ai-ml", "programming", "science", "tutorial", "talks-interviews", "tech"]
```

The categories list must include ai-ml first. MIT OCW lectures often get miscategorized
as `science` by the auto-classifier (titles lack strong ai-ml keywords like "neural network").
Always verify and fix both the frontmatter categories AND the body-level `**Categories:**` line.

## File Location

Transcripts live in `transcripts/ai-ml/`, NOT `transcripts/science/` or `transcripts/programming/`.
If the script put the file in the wrong directory, `mv` it before writing the walkthrough.
Then delete the now-empty leaf directory.

## Filename Slug

Pass `--topics "N <topic phrase>"` to `add` (D-13). The leading lecture number keeps
`ls` order equal to lecture order; the phrase names the subject:
`--topics "13 learning by near misses"` → `NC-00XX_13-learning-by-near-misses.md`.
Winston's OCW titles are already topical, so the title fallback stays usable for this
series, but passing `--topics` is still the standard.

## Body Metadata Block

After the `---` separator, before the walkthrough, include:

```markdown
# N. Lecture Title

**Source:** [https://youtu.be/VIDEO_ID](https://youtu.be/VIDEO_ID)  
**Channel:** MIT OpenCourseWare  
**Course:** 6.034 Artificial Intelligence, Fall 2010  
**Instructor:** Patrick Winston  
**Duration:** MM:SS  
**Added:** YYYY-MM-DD  
**Categories:** ai-ml, programming, science, tutorial, talks-interviews, tech
```

Note: The body `**Categories:**` line is set independently from the YAML frontmatter by
the script. They can drift. When fixing frontmatter categories, also update the body line.

## Walkthrough Section Pattern

Title format: `## Lecture Walkthrough: <Descriptive Subtitle>`

Sections are numbered with the pattern `### N. <Section Name>` where N is 1-based.
The section name often has a colon-suffix for the hook: `### 1. The Hook: <Specific Thesis>`.

### Standard Section Sequence

1. **The Hook**, The opening problem or framing question. Usually contains Winston's
   provocative claim for the day. Include a blockquoted quote.
2. **Core Concept**, The main idea, theory, or model introduced.
3. **Knowledge / Taxonomy**, Tables of concepts, techniques, or primitives introduced.
   Use pipe tables with clear column headers. Winston frequently introduces enumerated lists.
4. **Demonstration / Worked Example**, Step-by-step of the in-class demo. Use tables
   to show before/during/after or step-by-step progression.
5. **Results / Surprising Facts**, Metrics, statistics, experimental findings mentioned.
6. **Punchline / Concluding Story**, Winston almost always closes with a personal anecdote
   or philosophical coda. Quote it. The Julia Child story, the "packaging ideas" star, etc.

Some lectures have 8+ sections (e.g., Lecture 15 has 8 sections including
Felicity Conditions and Self-Explanation Effect). Number through.

### Table Format

Pipe tables with `|` delimiters. Header row, separator row, data rows.
Align columns left (default). Use `**bold**` for emphasized column entries.
Keep tables compact, no more than 5-6 columns. Use line breaks sparingly.

### Blockquote Density

Blockquote 1-2 of Winston's most memorable quotes per major section.
Not every sentence, the most quotable lines. Winston's style is full of
aphorisms: "All great ideas are simple," "What's computed is computed and
need not be recomputed," "If you can only think about something in one way,
you have no recourse when you get stuck."

### References Section

After the walkthrough, before `## Full Text`:

```markdown
## References

### Primary Sources

N. **Author, A.** (Year). "Title." *Venue*, Volume(Issue), Pages.
   - 1-sentence relevance summary.

### Secondary Sources

N. ... (same format)

### Board Content Source

Board diagrams (<list of specific diagrams reconstructed>) were reconstructed
from the lecture video.
```

Primary = papers/theses/books Winston explicitly cites.
Secondary = textbook chapters, supporting papers, context.
Each reference gets its own numbered item (flat across primary+secondary).

### Full Text

The full transcript goes at the bottom under `## Full Text` in a fenced code block.
Always start the transcript with `PROFESSOR PATRICK WINSTON:` (the opening spoken line).
The transcript preserves the Creative Commons attribution credo at the top when present.

## Catalog Entry

Add to `$CATALOG_ROOT/01-engineering/01-ai/01-MIT-6.034.md`:
`- [[transcripts/ai-ml/NC-00XX_N-slug-title|N. Lecture Title]]`

Entries are listed in lecture-number order. Out-of-sequence additions (e.g., adding
Lecture 18 after 12b) go in their correct numerical position, not appended at the end.
Use `patch` to insert between existing entries.

## References for MIT 6.034

Common reference targets for this series:

| Reference | How to cite |
|-----------|-------------|
| Winston PhD thesis (arch learning) | Winston, P.H. (1970). *Learning Structural Descriptions from Examples.* MIT AI Lab. |
| Minsky frames | Minsky, M. (1975). "A Framework for Representing Knowledge." In *The Psychology of Computer Vision.* |
| Chomsky merge | Chomsky, N. (2005). "Three Factors in Language Design." *Linguistic Inquiry*, 36(1). |
| Chi self-explanation | Chi, M.T.H. et al. (1989). "Self-Explanations: How Students Study..." *Cognitive Science*, 13(2). |
| Michalski soybean diagnosis | Michalski, R.S. and Chilausky, R.L. (1980). *Int'l Journal of Policy Analysis and Information Systems*, 4(2). |
| Fillmore case grammar | Fillmore, C.J. (1968). "The Case for Case." In *Universals in Linguistic Theory.* |
| Rosch basic-level categories | Rosch, E. et al. (1976). "Basic Objects in Natural Categories." *Cognitive Psychology*, 8(3). |
| Tattersall paleoanthropology | Tattersall, I. (2002). *The Monkey in the Mirror.* Harcourt. |
