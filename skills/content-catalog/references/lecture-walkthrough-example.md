# Lecture Walkthrough Example: Patrick Winston, Goal Trees & Problem Solving

This is a worked example of the **structured walkthrough** pattern for
didactic lecture transcripts. Use it as a template when processing any
lecture with a clear pedagogical arc.

## Original catalog entry

- **URL:** https://www.youtube.com/watch?v=PNKj529yY5c
- **ID:** NC-0008
- **Title:** 2. Reasoning: Goal Trees and Problem Solving
- **Course:** MIT 6.034 Artificial Intelligence, Fall 2010
- **Instructor:** Patrick Winston
- **Channel:** MIT OpenCourseWare

## Metadata enrichment

After `scripts/transcript.py add "<url>"` runs, added to frontmatter:

```yaml
course: "6.034 Artificial Intelligence, Fall 2010"
instructor: "Patrick Winston"
```

Verified with: `yt-dlp --print description "<url>"`

## Walkthrough structure (8 sections replacing the script-generated intro)

### 1. The Warm-Up Problem
State the exact problem on the board. Include the equation in $\LaTeX$.

### 2. The Core Idea
Name the concept (problem reduction). Explain why naming matters. Include the
speaker's framing about skill, naming, and understanding, these philosophical
moments are what make the lecture memorable.

### 3. The Knowledge
Introduce the taxonomies (safe vs. heuristic transformations) as
tables. This is the conceptual vocabulary the lecture builds.

### 4a. Why the Grungy Detail? (Speakers's Philosophy)
If the speaker pauses to explain *why* they're going through details at a
low level, capture that. It's often the most important pedagogical insight
in the lecture, e.g., Winston's "skill → understand → witness" ladder.

### 4b. The Backstory (Speaker/Program Context)
Include historical context about the program or people involved
(e.g., James Slagle writing SAINT on a 32K machine in 1960). This humanizes
the technical content.

### 4c. The Architecture
Show the program loop and data structures (goal trees, and/or nodes).

### 5. Step-by-Step Solution
Number each transformation step. Show the intermediate expressions in $\LaTeX$.
Include a table for subproblems at and nodes. Give the final answer in $\LaTeX$.

### 6. Results & Metrics
Table of empirical results (solve rate, tree depth, knowledge counts).

### 7. The Catechism
The meta-lesson (Winston's 5-question knowledge framework).

### 8. The Punchline
The story that wraps the lecture. Include the quoted punchline.

## Key pitfalls avoided

- Did NOT assume the lecturer based on the video title alone (initially
  guessed SICP/Abelson-Sussman, actually Winston/6.034)
- Did NOT leave the redundant intro paragraph in place
- Captured the board equation from supplementary course slides, not the
  spoken transcript (spoken transcript says "minus sign and that 5" but
  doesn't state the integral explicitly)

## Supplementary material

Equation source: `https://ai6034.mit.edu/wiki/images/SlagleSlides.pdf`
Extracted via: `curl -sL <url> -o /tmp/file.pdf && python3 -c "import fitz; doc=fitz.open('/tmp/file.pdf'); [print(page.get_text()) for page in doc]"`
