# Math Expression Extraction from Screenshots

When the user shares a screenshot containing math notation (equations from
lecture slides, textbook excerpts, paper snippets) and asks you to extract or
interpret the math, use this fallback chain.

## Tier 1: Vision (if model supports it)

If the active model has native vision, pass the image directly to
`vision_analyze` with a question like "Extract all equations exactly as
written."

**Known failure modes:**
- Some models reject image_url inputs entirely (error: "unknown variant
  `image_url`, expected `text`"). This is a provider-level limitation, the
  model literally cannot accept image inputs.
- Fallback vision models may produce garbled output for subscripts, Greek
  letters, and Unicode math symbols.

## Tier 2: Apple Vision framework (macOS, preferred over tesseract)

On macOS, Apple's built-in Vision framework (via a short Swift script) is
significantly more accurate than tesseract for math notation. It correctly
reads `≤`, `≥`, parentheses, and variable names that tesseract garbles.

### Setup

Write a Swift script to a temp file and run with `xcrun swift`:

```swift
import Cocoa
import Vision

let url = URL(fileURLWithPath: "/absolute/path/to/image.png")
guard let image = NSImage(contentsOf: url),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("FAILED to load")
    exit(1)
}

let request = VNRecognizeTextRequest { req, error in
    if let error = error { print("ERROR: \(error)"); return }
    guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
    for obs in observations.sorted(by: { $0.boundingBox.origin.y > $1.boundingBox.origin.y }) {
        if let top = obs.topCandidates(1).first {
            print(top.string)
        }
    }
}
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try? handler.perform([request])
```

### Results vs. tesseract (real example from MIT 6.034 slide)

| Engine | Output |
|--------|--------|
| tesseract | `amiss: BLE = HUA) < DA // CONSISTS \| H&,c)- Hao <D (x4)` |
| Vision | `ADMISSIBLE` / `H(x,G) ≤ D(x,G)` / `CONSISTENCY` / `\|H(x,G) - H(y,G)\| ≤ D(x,y)` |

### Performance note

First run compiles the Swift script (~30-45s cold). Subsequent runs are
instant if you reuse the compiled binary or the script is small.

### macOS filename pitfall

Screenshots saved by macOS may contain a **Unicode Narrow No-Break Space
(U+202F)** between the minute digits and "AM"/"PM" in the filename:
```
Screenshot 2026-06-28 at 10.26.56\u202fAM.png
```
The hex bytes are `e2 80 af`. Shell globbing handles this automatically
(`*Screenshot*2026*AM*`), but hardcoding the path in Python requires
the Unicode escape or the glob approach.

### When Vision produces garbled output for math

If Vision still garbles parts of the equation, try:
1. **Upscale the image first** via Python/PIL (4-6x with LANCZOS)
2. **Increase contrast** with `ImageEnhance.Contrast`
3. **Crop to just the equation**, the less surrounding whitespace, the better
4. Try `request.revision = VNRecognizeTextRequestRevision3` for newer recognition engine

## Tier 3: OCR (tesseract)

If Vision is unavailable (Linux, CI, no Swift toolchain), fall back to tesseract:

```bash
tesseract "<image_path>" stdout --psm 6 2>/dev/null
```

**tesseract limitations on math notation:**
- **≤, ≥, ≠** → rendered as `≤`, `<`, `>`, or gibberish
- **Subscripts (h\*, h\*(n))** → rendered as `Hua` or `H&`
- **Greek letters** → not recognized
- **h(n) without space** → rendered as `HOA`, `HaO`, or split across words

Even with preprocessing (grayscale → threshold → 5x upscale → sharpen),
tesseract cannot reliably extract mathematical notation from slides.

## Tier 4: Transcript catalog cross-reference (recommended)

**Uses the user's own transcript catalog.** This is often the fastest and
most accurate method for lecture content.

### How it works

1. Identify the lecture topic from context (keywords, file name hint, user's
   description, e.g., "searching optimal path," "admissible vs. consistency")
2. Search the user's transcript catalog with topic keywords:
   ```bash
   search_files(pattern='admissible|consistency', path='$CATALOG_ROOT/transcripts/', context=3)
   ```
3. The verbally-defined equations are embedded in the transcript as
   natural-language text. Look for lines like:
   > "we could say that it's admissible if the estimated distance between any
   > node X and the goal is less than or equal to the actual distance between
   > X and the goal"

### Why this works

Lecturers who define math verbally produce transcript text that contains the
exact equation content, even though the *visual* notation (≤, subscripts, etc.)
isn't present. The spoken definition is structured enough to reconstruct the
formal math.

### Example (this session)

**Source:** Screenshot of Patrick Winston's 6.034 slide on admissible vs.
consistent heuristics for A* search.

**OCR gave:** `amiss: BLE = HUA) < DA // CONSISTS | H&,c)- Hao <D (x4)`

**Transcript search gave (from `2026-06-28_5-search-optimal-branch-and-bound-a.md`):**
- Admissible: "the estimated distance between any node X and the goal is less
  than or equal to the actual distance between X and the goal"
  → h(X) ≤ actual_distance(X, G)
- Consistency: "the distance between X and the goal minus the distance between
  some other node in the goal, Y. Take the absolute value of that. That has to
  be less than or equal to the actual distance between X and Y"
  → |h(X) - h(Y)| ≤ actual_distance(X, Y)

## When all three fail

For genuinely board-only equations (drawn on a chalkboard but never spoken
aloud), the catalog won't have them either. Try supplementary materials:

1. Course wiki or linked PDFs from lecture pages (e.g., SlagleSlides.pdf
   for MIT 6.034's SAINT integration example)
2. `curl -sL <url> -o /tmp/file.pdf && python3 -c "import fitz; doc=fitz.open('/tmp/file.pdf'); [print(page.get_text()) for page in doc]"`
