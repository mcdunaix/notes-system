# D-12 Fix Workflow: Removing Double-Hyphens from Transcripts

The `transcript.py verify` command checks for invariant violations, including **D-12: double-hyphen `--` used as em dash**. This reference documents the fix workflow.

## Running verification

```bash
# Check ALL catalog entries
cd $CATALOG_ROOT
python3 scripts/transcript.py verify

# Output: lists each PROBLEM with file path and line number, or
# "OK: all storage invariants hold."
```

## Fixing D-12 violations, procedure

1. **Read the flag line and its surrounding context** (2–3 lines above and below) to understand the grammatical function of the `--`.
2. **Choose the correct replacement punctuation** based on context:
   - **Colon (`:`)** - definition, explanation, or elaboration (e.g., "three colors: red, white, blue"; "the surprise: everything that had been done")
   - **Comma (`,`)** - parenthetical aside, trailing break, self-correction, or restatement (e.g., "the machine, in order to learn anything"; "what's a salient, what's a salient idea?")
   - **Period (`.`)** - start a new sentence (rare - only when the text after `--` is a standalone independent clause)
3. **Apply with `patch`**:
   ```
   patch(path="transcripts/<category>/<filename>.md",
         old_string="...--...",
         new_string="...,...")
   ```
4. **Re-verify** after each batch of fixes to track progress:
   ```
   python3 scripts/transcript.py verify
   ```

## Pitfalls

### 1. Duplicate text in code blocks

Transcript files contain a **raw transcript within a fenced code block** (`` ``` `` ... `` ``` ``) AND the same text as regular markdown below it. The code block is **exempt** from D-12 checking, but its text is identical to the non-code version. This means `patch`'s `old_string` will match BOTH locations, the patch often hits the code-block occurrence and leaves the non-code violation untouched.

**Workaround:** Always include enough surrounding context lines in `old_string` to uniquely identify the non-code-block occurrence. If the same text exists in both zones, add a unique line from the paragraph above that differs between the two sections.

**Diagnostic hint:** If verify still reports the violation after a patch, the patch likely hit the code block copy. Check by re-reading the lines around the flagged line number.

### 2. Collateral damage from overly-broad patches

When providing extra context to disambiguate a match, it's easy to accidentally replace more text than intended, especially when the context spans across paragraphs. This can silently delete or duplicate words.

**Always re-read the patched area after each batch** to confirm no text was lost. Look for:
- Missing prepositions or transitional phrases
- Sentence fragments where full sentences belonged
- Changed line wrapping that broke the paragraph flow

### 3. Line numbers shift between verify runs

Each patch changes the file length (adding/removing characters), so line numbers reported by verify shift. Don't rely on absolute line numbers across patches, re-read the flagged area fresh each time.

### 4. Code-block text is NOT checked but CAN be broken

The D-12 checker exempts fenced code blocks, but patching code-block text unnecessarily can introduce inconsistencies between the raw transcript and the formatted version. Only fix violations outside the code blocks.

## Reference: violation counts from NC-0017

The full pass on NC-0017 involved 37 individual `--` replacements outside the code block, broken down as:
- **28 commas** - parenthetical breaks and self-corrections (most common in extemporaneous speech)
- **9 colons** - definition/elaboration patterns
- **0 periods** - all were within continuing clauses
