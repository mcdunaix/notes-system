# Inject Walkthrough via Python Assembly Script

Pattern for replacing the auto-generated intro with a structured walkthrough using a Python helper script. More reliable than patch (avoids fuzzy matching that can destroy the transcript code block).

## The pattern

Write a Python script that:

1. Reads the target transcript file
2. Finds the `## Full Text` boundary
3. Splits into header (frontmatter + metadata through `---` separator) and footer (`## Full Text` + code block + nav)
4. Reads the walkthrough from a separate temp file
5. Stitches everything back
6. Verifies key structural elements survived

## Concrete implementation

### Step 1: Find the boundaries

```bash
python3 -c "
with open('transcripts/ai-ml/FILE.md') as f:
    lines = f.read().split('\n')
for i, line in enumerate(lines):
    if line.strip() == '## Full Text':
        print(f'FullTextIdx:{i}')
        print(f'SepIdx:25')  # line after the --- marker
        break
"
```

Typically:
- Lines 0-26: frontmatter + title + metadata + `---` (the separator)
- Line 27: empty
- Lines 28-N: auto-generated intro
- Line N+1: `## Full Text`
- Lines N+2+: empty + transcript code block + navigation links

### Step 2: Write the assembly script

```python
with open('transcripts/ai-ml/FILE.md') as f:
    content = f.read()
lines = content.split('\n')

# Find ## Full Text boundary
full_text_idx = None
for i, line in enumerate(lines):
    if line.strip() == '## Full Text':
        full_text_idx = i
        break

header = '\n'.join(lines[:full_text_idx])
footer = '\n'.join(lines[full_text_idx:])

walkthrough = open('/tmp/walkthrough.md').read()

new_content = header + '\n\n' + walkthrough + '\n\n' + footer

with open('transcripts/ai-ml/FILE.md', 'w') as f:
    f.write(new_content)

# Verify
bt = new_content.count('```')
ft = new_content.count('## Full Text')
up = new_content.count('Up:')
print(f'Written {len(new_content)} chars')
print(f'## Full Text count: {ft} (should be 1)')
# Note: bt may be 4+ if walkthrough has its own code blocks (ASCII trees, etc.)
# Focus on verifying ## Full Text and nav links, not flat fence count
```

### Step 3: Run it

```bash
python3 /tmp/assemble.py
```

## Why this works

- **No fuzzy matching.** The split is at an exact string boundary (`## Full Text`), not regex/wildcard.
- **The transcript code block is never touched.** The footer includes everything from `## Full Text` onward, the header, empty line, opening fence, full text, closing fence, and nav, all preserved byte-for-byte.
- **The walkthrough is injected cleanly between two `\n\n` separators.** No risk of merging with adjacent sections.

## Pitfalls

- **The auto-generated intro text ends BEFORE the final newline before `## Full Text`.** The split at `full_text_idx` drops the intro cleanly. Verify by checking that the final line of `header` (before the `---` to `## Full Text` gap) is the `---` separator, not random transcript text.
- **Don't use this for patch-level fixes** (e.g., fixing a single metadata field). Use `patch` for targeted changes. This assembly approach is only for the walkthrough injection.
- **After assembly, always run the gate:** `cd $CATALOG_ROOT && python3 scripts/transcript.py rebuild && python3 scripts/transcript.py verify`, `verify` (stdlib-only) confirms the `id:` line and the fenced transcript survived; a non-zero exit names the file and the broken invariant.
