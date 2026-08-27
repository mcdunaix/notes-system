# Vault Organization Conventions

The golden rules for the notes vault at $CATALOG_ROOT/. Do not deviate.

## File explorer ordering

Number prefixes enforce intentional order regardless of sort algorithm.

```
000-dashboard/        ← entry point
01-engineering/       ← AI, ML, programming, networking
02-culture-society/   ← cultural commentary, social observations
references/
scripts/              ← utility (no prefix → sorts after numbers)
transcripts/          ← raw transcript files
```

## Domain naming

Each broad domain gets a folder at root with a leading `0N-` number.
Current domains (the fixed `CATEGORY_DOMAIN` set; the `it` domain was
retired, protocol D-14):
- `01-engineering/` - AI, ML, NN, programming, networking all fall under engineering
- `02-culture-society/` - cultural commentary, social analysis

New broad domains get next available number at root level.

## Domain-internal file ordering

Each domain folder uses numbered files/sub-folders:
```
01-engineering/
  00-Index.md           ← domain index (first)
  01-ai/                ← sub-domain folder
    00-Index.md
    01-MIT-6.034.md     ← course landing page
    02-3Blue1Brown.md   ← next course
  02-programming/       ← next sub-domain
    00-Index.md
```

Rules:
- The index is always `00-Index.md` to sort first
- Sub-folders get `01-`, `02-`, etc.
- Files within a sub-folder get `01-`, `02-`, etc.
- Course landing pages use clean descriptive names: `MIT-6.034.md` not `NC-0012_search-optimal-branch-and-bound.md`

## Index.md format (every domain)

Every domain and sub-domain has an Index.md. Format:

```markdown
# Domain Name

- [[SubPage|Display Name]] - description
- [[SubPage|Display Name]] - description

[[../../000-dashboard/Index|← Home]]
```

Rules:
- No emojis, no frontmatter tags, no blockquotes, no HTML
- Clean bullet lists with bold section headers for sub-domains
- Description after ` - ` (space, hyphen, space)
- Back link points to `000-dashboard/Index` from appropriate depth

## Root Index.md (000-dashboard/Index.md)

Lists EVERY entry in the vault grouped by broad domain. Clean lists only.

```markdown
# Notes

**Engineering**

- [[../01-engineering/01-ai/01-MIT-6.034|MIT 6.034]] - 5 lectures
- [[../01-engineering/01-ai/02-3Blue1Brown|3Blue1Brown - Neural Networks]] - 2 videos
- [[../transcripts/ai-ml/...|Introduction to Machine Learning]] - PDF
- [[../01-engineering/02-programming/00-Index|Programming]] - 1 tutorial
- [[../transcripts/tech/...|Entry Name]] - description

**Culture and Society**

- [[../transcripts/talks-interviews/...|Entry Name]] - description
```

Links from 000-dashboard/ use `../` prefix (up to root, then into target).

## Back link paths

From any page, link back to the dashboard:
- From `01-engineering/`: `[[../000-dashboard/Index|← Home]]`
- From `01-engineering/01-ai/`: `[[../../000-dashboard/Index|← Back to Home]]`
- From `transcripts/ai-ml/`: `[[../../000-dashboard/Index|← Home]]`
- From `02-culture-society/`: `[[../000-dashboard/Index|← Home]]`

## Course pages

Course landing pages use plain `[[wikilinks]]`, no Dataview:

```markdown
# MIT 6.034

- [[transcripts/ai-ml/NC-0007_introduction-and-scope|1. Introduction and Scope]]
- [[transcripts/ai-ml/NC-0008_goal-trees-problem-solving|2. Reasoning: Goal Trees and Problem Solving]]

---

[[../../000-dashboard/Index|← Back to Home]]
```

The display text (after `|`) is the lecture title. The raw filename is never shown.

## Transcipt navigation links

At the bottom of each transcript, after the closing ```:

```markdown
---

Up: [[../../01-engineering/01-ai/01-MIT-6.034|Course Name Index]]
Previous: [[../ai-ml/previous-file|Lecture N: Title]]
Next: [[../ai-ml/next-file|Lecture N: Title]]
```

- First entry omits Previous; last entry omits Next.
- Use `[[wikilinks]]` (not markdown `[]()`) for Obsidian backlinks.
- From `transcripts/ai-ml/`, path to course page: `../../01-engineering/01-ai/01-MIT-6.034`
