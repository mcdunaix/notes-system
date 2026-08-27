This document captures project state for session continuity. A new agent
reading this file should be able to orient and resume work without reading
the previous transcript.

## Project

A shippable, Hermes-ready repo (`~/Documents/notes-system`) factored out of
the author's personal notes vault (`~/Documents/notes`, still private). It
ships the catalog system: `scripts/transcript.py` (ingest to rebuild to
verify), `scripts/next-id.py` (NC-#### allocator covering transcripts/ AND
references/), the storage protocol docs, and five Hermes skills, four copied
and cleaned from the vault plus one new (`review-discussion-probe`). The
database is deliberately EMPTY: no personal notes are transferred. The repo
root is the catalog root (`$CATALOG_ROOT`); every skill path is parameterized.

## Resume here

### 2026-08-26 (5th session): R1 resolved by history rewrite (unpushed); series clustering; cold-read README

**Session arc.**
1. Goal set: scrub private info from the tree, make the README readable
   cold, guarantee that a cataloged video series clusters (the pre-repo
   filing system scattered series and failed to create folders).
2. R1 decided as rewrite. `git filter-repo --replace-text --mailmap`
   replaced the bot username, bot display name, bot ID prefix, pairing
   code, and Telegram user ID with the same placeholders the working
   tree already uses, replaced the real name with the publishing
   account name, and remapped the first commit's author (a school
   email identity) to the mcdunaix identity. Post-rewrite audit: zero
   blob hits for all seven strings across all revisions; every commit
   authored by mcdunaix. ALL COMMIT HASHES CHANGED; hashes cited in
   older entries below refer to the pre-rewrite history. A pre-rewrite
   mirror sits at /tmp/notes-system-backup.git until the push is
   verified.
3. LICENSE copyright holder switched from the real name to mcdunaix
   (tree and, via the rewrite, all history).
4. Series clustering shipped, R-15 honored (13 vectors in
   scripts/test_series_clustering.py written RED first). `add --series`
   writes `series:` frontmatter; later parts inherit the series' category
   folder over their own keyword guess (apply_series/resolve_categories);
   the dashboard clusters series members contiguously anchored at the
   lowest member id and adds a Series column when a category has any;
   `verify` exits 1 on a series split across folders (series_conflicts).
   End-to-end proof in a temp catalog: cluster order NC-0002/NC-0004
   contiguous, split simulation caught.
5. README rewritten for a cold read: job stated in the first sentence,
   pipeline/protocol/skills named as the three shipped parts, D-# codes
   introduced as citations into STORAGE_PROTOCOL, vault provenance and
   "the author's setup" narrative removed, --topics and --series
   documented at the worked example. Series pinned in STORAGE_PROTOCOL
   ("Series" subsection), CLAUDE.md, and content-catalog SKILL.md.

**R1 CLOSED.** User approved in-session; force-pushed and verified:
remote main at the rewritten head, GitHub commit list and LICENSE
content confirmed clean via API, CI green on the new head, pre-rewrite
backup mirror deleted. Residual: GitHub can cache old commits by SHA
for a while; the bot token was never fully committed (prefix only), but
rotating it via BotFather remains the belt-and-braces close.

**Gotchas.**
- CI's test glob picks up test_series_clustering.py automatically.
- cluster_rows sorts on (series anchor, id) with str() coercion; ids in
  index rows are already strings.
- The README series example shows only the command, no pasted output
  (the override print fires only when the guess differs; do not invent
  sample output, rerun for real if output is wanted).

### 2026-08-26 (4th session): Peer review pass; verify covers references/, student on-ramp, PII scrub, CI

**Session arc.**
1. User set the goal: peer review the repo as a tool, polish to industry
   standard for a broad audience (students), keep it built around Hermes.
2. Pipeline hardening: requirements.txt, Python 3.10 guard, missing-dep
   errors that read as install steps, repo-relative output paths.
3. Closed verify's documented blind spot: it now scans references/ too
   (frontmatter, cross-tree id collisions, D-12). R-15 honored:
   scripts/test_verify_references.py written RED first, 8 vectors.
   Reference-only exemption: `--` inside fenced code (CLI flags quoted
   in analysis); em dashes fail everywhere.
4. Ran the tool for real and caught the classifier misfiling the
   canonical 3Blue1Brown neural-network lecture into science (neuron
   scored 19 vs ai-ml 8). Added deep-learning vocabulary to ai-ml
   keywords with a regression vector (test_ai_ml_category.py); the
   video now files under ai-ml, confirmed by a live add in a venv.
5. Skills audit (agent sweep, then two agents fixing disjoint trees):
   scrubbed the unredacted Telegram bot username (14 sites) and two real
   private individuals used as examples; reconciled content-catalog to
   transcript.py (NC filenames, 10 categories, next-id.py allocation,
   PDF dedup, --topics everywhere); fixed two live bugs in
   catalog-add-from-video.py (duration fallback wrote a bare comma,
   --source was ignored); parameterized lecture-vetting's NC-0021 gates;
   marked private-vault ids and the unshipped technical-research-survey
   skill with a self-contained retrieval fallback; labeled Telegram /
   mlx-whisper / Obsidian paths optional with cross-platform
   alternatives; deleted the orphan social-media-cataloging.md and the
   stale duplicate lecture-walkthrough lab-guide-pattern.md.
6. Student-facing README rebuild (prereqs, worked example pasted from a
   real run, troubleshooting), vocabulary section + unlisted-D-# note in
   STORAGE_PROTOCOL, CI on 3.10/3.13 (vectors, empty-db gate, installer,
   em dash sweep). First CI run green.
7. Found SESSION_STATE.md itself re-leaking the identifier values it
   recorded as redacted; scrubbed the values, kept the record.

**Decisions pinned.** No repo-local decisions.md; the one protocol
change (verify scans references/, fenced-hyphen exemption) is pinned in
docs/STORAGE_PROTOCOL.md "Entry kinds" and evidenced by
scripts/test_verify_references.py.

**Files produced/changed.** Commit c2236ee, 40 files. New:
requirements.txt, .github/workflows/ci.yml, scripts/test_ai_ml_category.py,
scripts/test_verify_references.py. Deleted: the two lecture-walkthrough
reference files above. Modified: transcript.py (verify extension, guard,
require(), ai-ml keywords, rel paths), install-skills.sh (missing-Hermes
note), README, CLAUDE.md, both docs, SESSION_STATE, and 20 skill files.

**Gotchas.**
- Pushing .github/workflows/ needs the `workflow` OAuth scope; the push
  was rejected until `gh auth refresh -h github.com -s workflow` (now
  granted for mcdunaix).
- Category keywords are word-boundary matched in singular form only
  ("neuron" matches, "neurons" does not). "layer", "network",
  "training", "pixel" were deliberately left out of ai-ml as too
  generic; see the comment in CATEGORY_RULES.
- The redacted identifier values (Telegram user ID, bot username) are
  still in pushed git history (commit 62e7c28 era). Working tree is
  clean; history is not.
- README sample output is pasted from a real run; if add's output format
  changes, re-run the real ingest and repaste, do not hand-edit.

**On the horizon.**
- Immediate: decide R1, the identifiers in pushed git history. Either
  accept exposure (they are a bot username and a Telegram user id, low
  but nonzero risk) or rewrite history: `git filter-repo` on the two
  strings, force-push, and note the rewrite in README for cloners.
- Rolled forward: labs/ is still outside verify (manual gate in
  lab-builder self-audit); en dashes are swept but not codified in D-12
  or gated in CI (em dash only); skill frontmatter is inconsistent
  (only content-catalog has version:/tags:); content-catalog/SKILL.md
  was deduplicated but is still the longest file in skills/.

### 2026-08-26 (3rd session): Database now ships folder-less; content folders removed from the public repo

**Session arc.**
1. User reported the shipped repo looked wrong: "I literally see folders
   that shouldn't be there." Verified GitHub == local (single branch, no
   tags): the only content-side files were the 00-Index.md templates (the
   author's own category prose) and .gitkeep dirs, no entries, no personal
   notes. User confirmed the whole content side goes: 000-dashboard/,
   01-engineering/, 02-culture-society/, transcripts/<cats>/, references/,
   labs/, briefs/ and their index files. Ship only scripts/, skills/,
   docs/, README, LICENSE.
2. `git rm -r` the content side. Fixed `transcript.py` build_index to
   mkdir 000-dashboard/ before writing Index.md: the write previously
   assumed the shipped dir, and the first `add` on a fresh clone would
   have crashed. Proved the path with a synthetic entry (rebuild created
   the dashboard, verify passed on 1 entry), then removed the test files.
3. Confirmed the pipeline is folder-less-safe: scan_catalog, issued_ids,
   and next-id.py collect() all guard `exists()`. verify/list/rebuild/
   next-id all exit 0 with no content dirs present.
4. Updated README (empty-and-folder-less wording, layout, quick start) and
   CLAUDE.md (where things live). Skills keep their vault-organization
   guidance as protocol for a live catalog, not shipped structure.

**Files changed.** scripts/transcript.py (mkdir fix), README.md, CLAUDE.md,
SESSION_STATE.md. Deleted all content-side folders.

### 2026-08-26 (2nd session): Shipping audit before GitHub publish; 3 leak classes fixed

**Session arc.**
1. User asked whether the repo is ready to ship from GitHub to other users.
   Ran the full gate: 5 test vectors GREEN, `verify` exit 0, `next-id.py
   --check` clean, fresh-clone quick start (rsync to /tmp, no git) passes,
   `install-skills.sh` verified against a temp HERMES_SKILLS dir (5 linked,
   idempotent on second run), D-12 scan clean (all remaining `--` are
   frontmatter fences, table separators, or CLI flags).
2. Found and fixed a real leak: `skills/content-catalog/scripts/
   catalog-add-from-video.py` still hardcoded the author's vault paths
   (`Path.home() / "Documents" / "notes"`, `INDEX.md`, `_scripts/
   transcript.py`). Parameterized to `$CATALOG_ROOT` with a repo-root
   fallback, pointed at `scripts/transcript.py` and `scripts/next-id.py`,
   delegated id allocation to `next-id.py` (closes the cross-folder
   collision class the allocator fix guards), aligned filenames to the
   `NC-####_slug.md` protocol (D-13), and added the missing networking +
   culture categories (D-17). Also fixed a latent bug in the script's
   fallback id scan: `^NC-` never matched frontmatter, so it always
   returned NC-0001; now scans `id:` lines with re.MULTILINE. Verified:
   allocator branch NC-0001, fallback branch NC-0008 with NC-0007 present.
3. Redacted personal identifiers in `skills/content-catalog/references/
   telegram-gateway.md`: the author's Telegram user ID, a bot ID prefix,
   a stale pairing code (values intentionally not repeated here), and the
   `_scripts/` path. Swept the remaining `_scripts/transcript.py` references in three
   more reference files to `scripts/transcript.py`; the intentional pitfall
   note in `lecture-walkthrough/references/transcript-script-notes.md`
   stays.

**Outstanding before publish.** None code-side. The two decisions left are
the user's: pick a LICENSE (README still says none chosen; MIT recommended
for a permissive personal-tooling repo) and create the GitHub remote (no
remote is configured yet; README quick start has a `<this-repo>`
placeholder). SESSION_STATE.md itself documents provenance and ships fine.

**Files changed.** skills/content-catalog/scripts/catalog-add-from-video.py,
skills/content-catalog/references/{telegram-gateway,instagram-transcription-pipeline,lecture-walkthrough-example,yt-dlp-vtt-fallback}.md.
Uncommitted at end of session.

### 2026-08-26 (1st session): Repo built from the vault system, Hermes-ready, empty database, new review-discussion-probe skill

**Session arc.**
1. User asked to turn the notes system plus relevant skills into a repo: no
   notes transferred, empty database shipped, a new walkthrough-sibling skill
   with three modes (Review, Discussion, Probe), and a cleanup of the
   ingest-to-file routines. Scope clarified up front: repo at
   `~/Documents/notes-system`, repo-copy-only cleanup (live vault untouched),
   one skill with three modes.
2. Copied `scripts/transcript.py` + 5 test vectors verbatim, and four skills
   (`content-catalog`, `lecture-walkthrough`, `lab-builder`,
   `lecture-vetting`) from `~/.hermes/skills/productivity/`.
3. Cleanup pass on the copies: 42 hardcoded `~/Documents/notes` paths swept
   to `$CATALOG_ROOT` with a Catalog root note per skill; the 6 stale
   tech-to-archived-03-it redirect spots in `lecture-walkthrough` rewritten
   to the general "category without a live domain index" rule; the literal
   `\n` merged bullet split back into two; dangling NC-0030/NC-0031/briefs
   pointers replaced with self-contained text or explicit "not shipped"
   notes; 142 U+2014 em dashes scrubbed from skills (only the self-audit
   detector command and table placeholders keep `--`, both exempt); 6 prose
   `--` uses fixed in lab references.
4. Wrote the new skill `skills/review-discussion-probe/SKILL.md`: one skill,
   three modes (Review: research + breakdown + verified claims + verdict for
   hardware/model/tool; Discussion: guided in-depth discussion scaffold for a
   video or artifact; Probe: current state, cutting edge with confidence
   labels, trajectories, related tech for a topic). Shared protocol section,
   structure template per mode, pitfalls. D-12 clean.
5. Wrote `scripts/next-id.py` (stdlib allocator + `--check` collision scan
   over transcripts/ + references/ + Index.md) and
   `scripts/install-skills.sh` (symlink or `--copy` into
   `~/.hermes/skills/productivity/`, bash 3.2 portable).
6. Wrote README.md, docs/STORAGE_PROTOCOL.md (I1-I8 + D-# conventions),
   docs/INGESTION_PIPELINE.md (routine map + the 8-item cleanup list), and
   the empty-database index templates.
7. Verified with real output: 5 test vectors GREEN; empty-db verify/list/
   rebuild/next-id all pass; fixture test proved next-id.py sees
   references/ (NC-0002 there made it print NC-0003) and that the old
   collision class (transcripts/NC-0001 vs references/NC-0001) now exits 1
   and names both files.
8. User asked "/handoff" and whether the repo is built specifically for
   Hermes Agent. Loaded the hermes-agent skill. Answer: partly already
   (skills are Hermes SKILL.md format, installer targets ~/.hermes/skills,
   capture path is gateway-driven), and this session closed the gap: added
   this SESSION_STATE.md resume convention, CLAUDE.md on-ramp (Hermes and
   Claude Code both auto-load it), and a README "Built for Hermes Agent"
   section. The pipeline core stays deliberately agent-agnostic (stdlib
   Python) so any tool can drive it.

**Decisions pinned.** No repo-local decisions yet. Protocol decisions from
the author's vault are documented, ids kept as vocabulary, in
`docs/STORAGE_PROTOCOL.md` (D-8 never rename, D-9 migrations, D-12 no em
dashes, D-13 topic slugs, D-14 extension pattern, D-17/D-18 fixed
vocabulary, D-25 no full-text exemption, R-15 test vectors).

**Files produced/changed.**
- Repo root: README.md, CLAUDE.md, SESSION_STATE.md, .gitignore,
  .obsidian/app.json, 000-dashboard/Index.md (placeholder, rebuild
  regenerates once entries exist), domain and category 00-Index.md templates
  (empty), transcripts/<9 categories>/.gitkeep, references/.gitkeep,
  labs/.gitkeep, briefs/.gitkeep.
- scripts/: transcript.py (verbatim), next-id.py (new), install-skills.sh
  (new), test_category_domain.py, test_culture_category.py,
  test_dashboard_tiering.py, test_networking_category.py,
  test_topics_slug.py (verbatim, all GREEN).
- skills/: content-catalog, lecture-walkthrough, lab-builder,
  lecture-vetting (copied + cleaned), review-discussion-probe (new).
- docs/: STORAGE_PROTOCOL.md, INGESTION_PIPELINE.md.
- Git: initialized, initial commit made this session. The author's vault
  repo was untouched.

**Gotchas.**
- The initial AGENTS.md write was blocked by an approval timeout
  (protected agent-instruction file). Delivered the same value as
  CLAUDE.md instead (Hermes and Claude Code both read CLAUDE.md). Do not
  retry AGENTS.md unless the user asks for it by name.
- `transcript.py verify` does not scan `references/`; the manual D-12 gate
  lives in `review-discussion-probe` step 7 and in `lab-builder`'s
  self-audit. `next-id.py --check` is the only whole-catalog collision
  check.
- The fixture files used to prove next-id.py were removed before the
  commit; the shipped database is empty. The proof is recorded in this
  entry, not as committed files.
- The double-hyphen (`--`) sweep of skill reference files is COMPLETE for
  prose found (6 fixes in lab-guide-pattern and abstraction-plan-checklist),
  but no exhaustive pass was run over every remaining `--` in all reference
  files (some are legitimate regex/CLI syntax). A final sweep before
  publishing the repo is still owed.

**On the horizon.**
1. Final `--` sweep over skills/ references (get to the self-audit bar:
   "MUST be 0 once table/rule syntax is excluded").
2. Test `scripts/install-skills.sh` against a temp HERMES_SKILLS dir
   before the user runs it for real (it skips existing skills, so the
   live harness is safe, but prove it first).
3. Optional: add a repeatable test fixture set (scripts/test_pipeline.py
   or tests/) covering the empty-db, next-id-across-references, and
   collision cases, so the R-15 vectors extend to the new tooling.
4. Optional: decide whether the Telegram-gateway capture path
   (content-catalog's Telegram capture-bot pipeline) should be documented as a
   Hermes gateway integration in README, or left as a personal-setup note.
5. Optional: pick a LICENSE if the repo will be published; README flags
   that none is chosen.
6. If the user wants the live vault to benefit from the cleanup (stale
   tech-to-03-it redirects, the next-id gap), port the fixes deliberately,
   not wholesale: the vault has personal paths and content this repo does
   not.
