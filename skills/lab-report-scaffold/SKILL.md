---
name: lab-report-scaffold
description: "Use when scaffolding or auditing a lab report note."
version: 1.0.0
author: Hermes Agent
platforms: [macos]
metadata:
  hermes:
    tags: [lab-report, markdown, measurements, uncertainty, pdf, vault, ece5331]
---

# Lab Report Scaffold

When a lab asks the student to take measurements and then write a report, do not
write the report. Build a fill-in note plus a compute script, so the numbers and
the plot come out of the measurements mechanically and the prose stays his. First
used on ECE 5331 Lab 1 (geometrical optics, focal length of a phone camera) in
`~/Documents/School/ECE5331/Lab 1 - Geometrical Optics/`.

## Pick the governing handout first

Before scaffolding anything, confirm which handout governs his section. Online,
IVC and RRT sections commonly get their own remote version of the same lab, and it
is a different experiment rather than a trimmed one (a phone-camera measurement
where the bench section uses an optical bench and lens kit). Using the in-person
file silently produces a report against the wrong procedure.

Identify a handout by its body and the report parts it asks for, never by its
filename. Canvas `display_name`, the module title and even page 1 of the PDF carry
over from an earlier year, so a stale label is not evidence that the right file is
missing. Record the file id, byte size and sha256 in the lab folder's `00-Index.md`
so the next session stops re-litigating it.

A logistics page naming a room and session times is the in-person spec; it carries
nothing for the remote section even when it mentions online students exist.

## The note pattern

One markdown note holds three marker-delimited blocks. HTML comments are invisible
in Obsidian and are skipped by the PDF converter.

- `<!-- ENTER:BEGIN -->` ... `<!-- ENTER:END -->`: what HE edits. A code block of
  `key = value` constants, then a GFM table of the raw measurements. Nothing else
  goes inside: prose that happens to read `g = 1.5` would be parsed as a constant.
- `<!-- RESULTS:BEGIN -->` ... `<!-- RESULTS:END -->`: what the SCRIPT writes.
  Computed table, fit, estimate, uncertainty budget, plot embed.
- `<!-- PHOTOS:BEGIN -->` ... `<!-- PHOTOS:END -->`: the script lists every image
  it finds in `photos/` so dropping a file in is the only step needed.

The script only ever replaces its own blocks, so it is idempotent and safe to
re-run after a remeasure. Constants parse with `^\s*([a-z_]+)\s*=\s*(-?[\d.]+)`
and table rows with `^\|\s*([\d.]+)\s*\|\s*([\d.]*)\s*\|`, blank cells skipped.

When a row needs a text label (two pyramids, two materials), widen the row regex to
a leading label cell and skip the header and the `---` divider by testing
`set(label) <= set("-: ")`; without that the header row parses as data.

## The script

One per lab, next to the note, taking `--note` and `--plot` so a test run can work
on a copy instead of the real note. It must fail closed: with a constant missing or
fewer than three filled rows, print what is missing and write nothing. Report two
independent readings of the same fit when the physics offers them, and say which one
to quote.

Uncertainty budget shape that works: statistical from the fit standard errors,
systematic from each input that scales the fitted quantity, combined in quadrature.
State which inputs are spec (trusted to a percent or two) and which are ruler reads.

## Check the note's own formulas against the target

A check formula can sit in a note for weeks because nobody evaluates it. ECE 5331
Lab 3 told him to compute `cos(theta) = ((b - a) / 2) / h` and expect 0.707 for a
45 degree face, where `h` was the vertical rise. Dividing by the rise gives 1.000
at 45 degrees and 0.707 at 60, so the check inverted the answer. Before trusting
any formula a note states, plug in the value it is supposed to produce; then name
the denominator in the prose (here the slant, not the rise).

Read printed dimensions off the artwork, not off the prose table, and measure the
drawn segments rather than trusting which edge a label points at. That same note
specified a 90 mm base edge while the template is labelled 5 cm base, 1 cm top,
2.8 cm slant; and vision reading the artwork guessed the 2.8 cm was the slant when
it dimensions the rise, which turns a "45 degree" template into a 54 degree one.
The page is a single raster at a known dpi, so Hough segments on the PNG convert
drawn lengths straight to millimetres and settle it in one pass. Then check the
numbers against the hardware they have to sit on: 90 mm cannot fit a 58.4 mm
display.

The mirror, frustum and Fresnel relations those checks rest on, with the values
used to verify a script: `references/optics-geometry-checks.md`.

## Estimator conditioning, the trap that bit

On `1/M = u/f - 1` the two readings are not equal in quality. The slope is well
conditioned; the zero crossing is read by extrapolating from the measurement range
back toward u ~ 0, a lever arm of 40 on a 150-250 mm span, so its error bar lands 5
to 10 times wider. Quote the slope, present the crossing as a sanity check, and
propagate the intercept and slope covariance properly when quoting the crossing
(`var(f_zero)` needs the `cov(a,b)` term, not just `var_a` and `var_b`).
A synthetic test that injects 0.1 mm of display-reading noise into clean model
values shows this immediately, which is why the scaffold gets tested with synthetic
values before the user measures anything.

Handle units and axes explicitly in the note: on a 4:3 photo shown full frame on a
16:9 screen, the correct enlargement pairs the photo's long axis with the sensor's
long axis only. Pairing screen width with the sensor's short axis is off by 1.33 and
the report silently wrong.

## Take the instrument's own units

A tape in inches must not be converted by hand: hand conversion adds arithmetic
error to every read and hides which mark was actually read. Parse units in the note
instead, so the value typed is the value on the instrument. Support `150`, `150 mm`,
`150mm`, `5.906 in`, `5 15/16 in`, `5-15/16"`, `15/16 in`, `5 ft 3 in`, `5'3"`,
`3 cm`; unit-less means millimetres. Two traps: insert a space before the unit word
(`re.sub(r"(?<=[\d/])\s*(mm|cm|inch(?:es)?|in|ft|feet)\b", r" \1", low)`) or
`150mm` never splits, and put `inch(?:es)?` before `in` in the alternation or
`\bin\b` refuses to match it. Strip comments first (`s.split("#")[0]`) since values
carry trailing `#` notes.

Keep the raw typed strings in the results table next to the converted millimetres
(`u as read`), so the report shows what the instrument said. And when the instrument
is coarser than the physics, say so in the note: a 1/16 inch mark is 1.59 mm, which
is 5 to 8 percent of a 20 to 30 mm reading, so that granularity, not the component
tolerance, is what the quoted uncertainty is made of. Offer the finer graduation as
the fix rather than silence.

## Rendering the PDF

The converter is
`~/.hermes/skills/productivity/matlab-homework-deliverables/scripts/md_to_pdf.py`.
It handles headings, bold, lists, fenced code, GFM pipe tables, `![[image|size]]` and
`![alt](path)` (inlined as data URIs, downscaled), `[[wikilink|alias]]` to plain text,
skips HTML comments, and typesets `$...$` with MathJax. A note with no `$` skips the
MathJax wait automatically.

Two steps: build the HTML from the terminal, print it from `browser_exec` (Edge CDP
on 9222 is already up on this Mac).

```
python3 <converter> "note.md" /tmp/note.html --html-only
```

```python
# browser_exec
import types
sk = "/Users/ofafonua/.hermes/skills/productivity/matlab-homework-deliverables/scripts/md_to_pdf.py"
mod = types.ModuleType("md_to_pdf")
mod.__dict__.update({"__name__": "md_to_pdf", "goto_url": goto_url, "new_tab": new_tab,
                     "wait_for_load": wait_for_load, "js": js, "cdp": cdp})
exec(compile(open(sk).read(), sk, "exec"), mod.__dict__)
mod.print_html_to_pdf("/tmp/note.html", "/tmp/note.pdf")
```

Do not `exec(open(sk).read())` bare in `browser_exec`: `__name__` is `__main__` there
and the file's own `if __name__` block then eats `sys.argv[1]`. Injecting the helper
namespace into the module dict is what makes `print_html_to_pdf` see `goto_url` and
`cdp`.

## Verify before handing it over

This model cannot see the PDF. Check it with pymupdf in the terminal python3:

- page count sane, and the marker comments, pipes and `[[` are all absent from the
  extracted text (they mean a block did not convert). Checking the HTML instead:
  grep for `![[` or the literal link text, never bare `[[`, because the converter's
  MathJax config emits `inlineMath: [['$','$']]` and a bare-`[[` grep hits it every
  time on a false positive
- every embedded file exists before the export: a missing `![[name.png]]` prints as
  literal text in the PDF instead of disappearing, so a diagram not yet drawn shows
  up as scaffolding in the submission
- every probe string present: each section heading, the fit line, the estimate, the
  spec comparison
- `document.images.length` from the browser and `len(page.get_images())` from
  pymupdf: identical fixture photos dedupe in the PDF, so trust the browser count
- `len(page.get_drawings())` on a table page (tens, not zero) proves the table
  rendered with rules rather than as paragraphs
- a synthetic run with the note's own predicted measurement values, checked against
the known spec (the phone camera's 3.99 mm came back as 4.01 mm from rounded
  predicted values, which is the expected size of the rounding)

## Vault and state

The School vault is Syncthing-synced: write with
`python3 ~/.hermes/scripts/sync_safe_write.py --path "<folder>" -- <command>`, and put
the run command in the note so the user can repeat it. New files can be written to
scratch and copied in by that wrapper in one pass. Update the lab folder's
`00-Index.md` and the class `SESSION_STATE.md`, then commit. Do not add pointer
lines to a note he submits; link from the index instead.

Lab notes carrying an explicit no-AI instruction (some ECE 5331 problem sets have
one) change the framing: the compute script and the scaffold are then check tools,
the prose is his, and the chat report should say so in one line.
