# Obsidian Dataview Plugin Setup

**Not the default.** The catalog's default is plain markdown [[wikilinks]],
not Dataview queries. Only set this up if explicitly asked.

Install in the $CATALOG_ROOT/ vault for auto-generated course/lecture tables.

## What it does

Dataview queries frontmatter metadata to generate live tables that update
automatically when new entries are added. Course landing pages can use this
instead of hardcoded markdown lists, but the default is plain wikilinks.

## How to install it

Plugin files live at `.obsidian/plugins/dataview/`:

```
$CATALOG_ROOT/.obsidian/plugins/dataview/
├── manifest.json   ← from GitHub release
├── main.js         ← from GitHub release
├── styles.css      ← from GitHub release
```

Registered in `.obsidian/community-plugins.json`:

```json
["dataview"]
```

## Dataview queries (if used)

To show clean clickable titles (not filenames) in correct lecture order:

```dataview
TABLE WITHOUT ID link(file.path, title) AS " "
FROM "transcripts/<category>"
WHERE series = "Course Name"
SORT lecture ASC
```

Requires `lecture:` or `chapter:` field in frontmatter for proper sorting.

## Preferred alternative: plain wikilinks

The default here is static markdown lists:

```markdown
- [[transcripts/ai-ml/NC-0007_introduction-and-scope|1. Lecture Title]]
- [[transcripts/ai-ml/NC-0008_goal-trees-problem-solving|2. Lecture Title]]
```

Advantages: no plugin dependency, renders instantly, can't break, works in
any markdown renderer, Obsidian backlinks work.

## Activation

On first open after installation, Obsidian prompts to enable the plugin.
Settings → Community plugins → Dataview → toggle on.

## Reinstallation

If the plugin breaks or needs reinstall:
1. Find latest version from GitHub API
2. Download `main.js`, `manifest.json`, `styles.css` from the release assets
3. Write to `.obsidian/plugins/dataview/`
4. Ensure ["dataview"] is in `.obsidian/community-plugins.json`

## Uninstall

If the user decides to stop using Dataview:
1. Remove "dataview" from `.obsidian/community-plugins.json`
2. Delete the `.obsidian/plugins/dataview/` directory
3. Replace any Dataview query blocks with plain [[wikilinks]]
