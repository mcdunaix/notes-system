# Course Series Post-Processing: Worked Example

This reference documents the exact sequence for integrating a new transcript
into an existing MIT 6.034 course series after `transcript.py add`.

## Context

- **New entry**: NC-0013 - "11. Learning: Identification Trees, Disorder"
- **Course**: MIT 6.034 AI, Fall 2010 (Patrick Winston)
- **Existing files**: 10 prior lectures at `transcripts/ai-ml/`
- **Course page**: `01-engineering/01-ai/01-MIT-6.034.md`

## What the script got wrong

| Issue | Script output | Needed |
|---|---|---|
| Category | `science` | `ai-ml` |
| File location | `transcripts/science/` | `transcripts/ai-ml/` |
| Frontmatter | no `course`, no `instructor` | both required |
| Navigation | none | Up + Previous links |
| Course page | not updated | add Lecture 11 entry |
| Prev lecture nav | Lecture 10 had no Next link | add `Next: ...` |

## Fix sequence

```bash
# 1. Patch the frontmatter (add course/instructor, fix categories)
# Use patch() tool with old_string matching the categories line

# 2. Move to correct directory
mv transcripts/science/2026-06-29_11-...md transcripts/ai-ml/

# 3. Remove empty source directory
rmdir transcripts/science/

# 4. Add navigation links at bottom of new transcript file
# (after closing ``` of raw text)
#
# ---
#
# Up: [[../../01-engineering/01-ai/01-MIT-6.034|MIT 6.034 Course Index]]
# Previous: [[../ai-ml/prev-file|Lecture N: Previous Title]]

# 5. Add Next link to the previous lecture in the series
# Use patch() to find the closing ``` and append the nav block

# 6. Add entry to course landing page
# Insert wikilink in correct numerical order on 01-MIT-6.034.md

# 7. Rebuild index
cd $CATALOG_ROOT && python3 scripts/transcript.py rebuild
```

## Key observations

- The script's keyword rules check in priority order: `ai-ml`, `programming`,
  `web-dev`, `science`, `tutorial`, `talks-interviews`, `tech`, `uncategorized`.
  MIT OCW lecture titles that don't contain `\bai\b`, `\bmachine learning\b`,
  `\bneural\b`, `\bdeep learning\b`, or `\bml\b` will fall through to `science`
  because the first matching keyword there is `\bscience\b` (from the channel
  "MIT OpenCourseWare", "Course" is an ai-ml keyword? No, "science" appears
  as a category name. Actually the issue is that "Science" appears in "MIT
  OpenCourseWare" metadata, wait, no. The video title "Identification Trees"
   doesn't match any ai-ml keyword, so it goes further down the priority list.
   The channel name "MIT OpenCourseWare" might contain a "science" keyword
   match. Regardless of the exact regex trigger, the fix is the same: verify
   category for every MIT OCW lecture and patch to `ai-ml`.)
