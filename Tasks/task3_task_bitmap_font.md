# Claude Code Prompt — Task: Hebrew Bitmap Font Pipeline for HP Prime
## Project: Premium Hebrew-Russian Editor for HP Prime
## Repository: `J:\Project_Vibe\HpPrimeEditor`

You are working as a senior software architect and implementation engineer on a premium-grade Hebrew-Russian editor for HP Prime.

This task is to build a **reproducible 1-bit Hebrew bitmap font pipeline** for HP Prime, replacing the current hand-drawn `LINE_P` glyph approach for Hebrew.

This is not a toy experiment.  
Treat it as a serious production foundation for future renderer integration.

---

## Mission

Build a **14x20, 1-bit, fixed-cell Hebrew bitmap font system** for HP Prime, with:

- a reproducible Python generator,
- a PPL asset module for the generated glyph data,
- a visual validation test,
- a specification document,
- stable Unicode/codepoint-to-glyph mapping,
- support for Hebrew base letters and final forms.

The primary goal is:

**unambiguous readability**

The secondary goal is:

**visual inspiration from Heebo Bold**

This is an **engineering adaptation**, not a direct copy of the font.

---

## Approved Requirements

These are already decided and must be treated as fixed unless a critical technical blocker is discovered.

### Glyph set
Implement at minimum:

#### Hebrew base letters (22)
א ב ג ד ה ו ז ח ט י כ ל מ נ ס ע פ צ ק ר ש ת

#### Hebrew final forms (5)
ך ם ן ף ץ

Total minimum Hebrew glyphs:
**27**

### Additional characters
These are planned but may be staged after the Hebrew-first milestone if necessary:

#### Digits
0 1 2 3 4 5 6 7 8 9

#### Punctuation
`. , : ; ! ? - ( ) " ' / space`

### Russian
Deferred to a later phase.

### Latin
Deferred to a later phase.

---

## Glyph Geometry

### Cell size
**14x20 pixels**

### Bit depth
**1-bit**

Meaning:
- 0 = background
- 1 = filled pixel

### Cell model
**Strict fixed-width cell**

Do not implement variable-width behavior in this task.  
Later tuning may be added in future phases, but this task must keep cell logic deterministic and fixed.

---

## Visual Reference

### Reference font
**Heebo Bold**

### Interpretation rule
Do not attempt a literal clone.

Instead:
- prioritize unambiguous readability,
- preserve visual family resemblance where feasible,
- optimize for low-resolution rendering and HP Prime constraints.

The user also supplied a PNG with the Hebrew alphabet as a visual reference.  
Use it as a validation/control reference for shape direction and overall silhouette expectations.

---

## Critical Engineering Rule

The current `LINE_P` hand-drawn Hebrew glyphs are considered insufficient for reliable one-to-one visual verification against printed Hebrew.

This task must move the project to a more reliable model:
- generated bitmap glyphs,
- stable encoded storage,
- deterministic renderer path.

---

## Mandatory Pre-Implementation Audit

Before coding, inspect the repository at:

`J:\Project_Vibe\HpPrimeEditor`

Confirm:
- current directory structure,
- whether `assets/`, `tools/`, `tests/`, `docs/` already exist,
- whether any existing `glyph_hebrew.*` files should be preserved, replaced, or deprecated,
- whether prior docs from Task 1 / bitmap planning should be updated or referenced,
- how existing tests and rendering modules may later integrate with the new font pipeline.

Also inspect current Hebrew glyph-related files if present, so the migration path is explicit and no blind compatibility assumption is made.

Document what exists and what will be superseded.

---

## Deliverables Required

Create and/or update the following:

### 1. `assets/hebrew_font_bitmap.ppl`
The HP Prime asset module containing:
- bitmap glyph data,
- glyph indexing helpers,
- glyph blit/render helpers,
- codepoint-to-glyph mapping helpers.

### 2. `tools/generate_hebrew_font.py`
A reproducible Python generator that:
- reads the source font and/or visual reference,
- rasterizes glyphs to 14x20,
- binarizes them,
- optionally cleans them up,
- emits PPL-ready row-integer glyph data.

### 3. `tests/test_bitmap_glyph_vis.ppl`
A visual validation test for HP Prime that:
- displays all Hebrew glyphs,
- validates final forms,
- checks alignment and distinctness,
- provides a readable visual review surface.

### 4. `docs/BITMAP_FONT_SPEC.md`
A document describing:
- glyph set,
- data format,
- generation rules,
- mapping rules,
- limitations,
- validation criteria,
- future extension strategy for digits/punctuation/Russian.

---

## Recommended Implementation Scope for This Task

### Phase target
Prioritize **Hebrew-first**.

That means the first successful implementation should at minimum include:
- 22 base Hebrew letters,
- 5 final forms,
- complete mapping for those 27 glyphs,
- working visual test.

Digits and punctuation may be included in this task if bounded and stable, but Hebrew coverage is the non-negotiable core milestone.

If necessary, you may implement:
- **Milestone A:** Hebrew 27 glyphs
- **Milestone B:** digits + punctuation

But do not compromise Hebrew quality to rush the extended set.

---

## Required Data Representation

Use **row-based integer arrays**.

For each glyph:
- 20 rows total,
- each row is encoded as an integer representing 14 bits.

This format should be:
- compact enough for HP Prime,
- deterministic,
- generator-friendly,
- easier to inspect than over-packed binary blobs.

Document row orientation clearly:
- whether bit 13 is leftmost or rightmost,
- how row integers map to pixels,
- what baseline assumptions are used.

Do not leave this ambiguous.

---

## Required Unicode / Mapping Behavior

Implement explicit mapping for:
- 22 base Hebrew codepoints,
- 5 Hebrew final-form codepoints.

### Important
Final forms must be **distinct glyphs**, not aliases to base forms.

Examples:
- כ ≠ ך
- מ ≠ ם
- נ ≠ ן
- פ ≠ ף
- צ ≠ ץ

The codepoint mapping function must therefore return distinct indices for final forms.

You must define and document the exact glyph index order.

Recommended order:

### Indices 1–22
Base Hebrew letters

### Indices 23–27
Final forms

You may then reserve later ranges for:
- digits,
- punctuation.

Document the final order explicitly.

---

## Required Generator Capabilities

`tools/generate_hebrew_font.py` must be designed as a reproducible build tool.

At minimum it must:
1. define the glyph set,
2. load the reference font (Heebo Bold) if available,
3. render each glyph to a controlled canvas,
4. scale/position into a 14x20 cell,
5. convert to 1-bit,
6. optionally apply bounded cleanup rules,
7. export row-integer arrays,
8. write output in a form that can be embedded into PPL code.

### Strong requirement
Do not make the generator a one-off disposable script.  
It must be understandable, deterministic, and maintainable.

If external Python dependencies are required, document them clearly.

---

## Visual Quality Rules

The font must optimize for:

- distinctness between commonly confusable Hebrew letters,
- visual consistency across the 14x20 grid,
- clear baseline behavior,
- reasonable top extenders,
- stable right/left interior spacing,
- readable final forms.

Pay special attention to differentiation of pairs/groups such as:
- ד / ר
- ה / ח
- ו / י
- כ / ב
- ס / ט / ע
- ש / ת
- base vs final forms

The task is successful only if glyphs are not merely “present”, but are visibly distinct enough for reliable reading on HP Prime.

---

## Font Engineering Rules

This is a fixed-cell UI bitmap font, not a print typesetting engine.

Therefore:
- preserve readability over typographic purity,
- avoid decorative details that collapse at 14x20,
- do not overfit to one screenshot,
- enforce consistency in stroke mass and silhouette,
- make glyphs robust to low-resolution rendering.

If any glyph needs local pixel cleanup after font rasterization, that is allowed — but such cleanup must be:
- bounded,
- documented,
- reproducible,
- not hand-wavy.

If you add per-glyph post-processing rules, document them in the spec.

---

## HP Prime Asset Module Requirements

`assets/hebrew_font_bitmap.ppl` must expose a clean interface.

Suggested API shape (adapt if needed, but keep it clean and documented):

- bitmap font initialization if needed
- glyph count retrieval
- codepoint-to-glyph-index lookup
- glyph blit/render function
- optional helper to render one glyph into a GROB or directly to screen
- optional helper to draw a sequence of glyphs in one row

The API should be future-friendly for later renderer integration.

Do not bury all logic into a giant monolithic function.

---

## Required Visual Test

`tests/test_bitmap_glyph_vis.ppl` must provide practical human verification.

At minimum, it must display:

### Section 1
All 27 Hebrew glyphs in a grid:
- base letters,
- final forms,
- indices,
- labels if screen space allows.

### Section 2
An alignment strip showing glyphs in sequence.

### Section 3
A mapping validation section:
- confirm that selected Unicode/codepoints map to correct glyph indices.

### Section 4
A distinctness review section:
Display short comparison groups or runs that help visually inspect problematic pairs.

Examples may include:
- ד ר
- ה ח
- ו י
- כ ב
- ט ס ע
- ש ת
- כ ך
- מ ם
- נ ן
- פ ף
- צ ץ

The test should be practical for visual inspection, not just a smoke test.

---

## Required Documentation Content

`docs/BITMAP_FONT_SPEC.md` must include:

### 1. Scope
What is included in this phase and what is deferred.

### 2. Glyph set
Exact list of supported glyphs.

### 3. Cell geometry
14x20, baseline assumptions, fixed-cell rules.

### 4. Data format
Row integers, bit ordering, storage structure.

### 5. Generator pipeline
Inputs, dependencies, steps, output format.

### 6. Mapping contract
Unicode/codepoint to glyph index.

### 7. Rendering contract
How a glyph is drawn on HP Prime.

### 8. Quality criteria
What counts as acceptable readability.

### 9. Known limitations
What is not yet solved.

### 10. Future extensions
Digits, punctuation, Russian, possible anti-aliased or 2-bit future work.

---

## Mandatory Risk Review

Before implementing, explicitly identify and address risks including:

- font rasterization not matching low-res readability needs,
- glyph collapse during 14x20 binarization,
- final forms becoming too similar to base forms,
- packed data format ambiguity,
- HP Prime rendering cost if blitting is too granular,
- mismatch between generator output and PPL consumption,
- missing reproducibility if script depends on undocumented local fonts,
- visually acceptable on PC but poor on HP Prime display.

For each risk, either:
- mitigate it in design,
- add a bounded validation step,
- or document why it is deferred.

Do not bury these issues.

---

## Strong Implementation Guidance

### Preferred source path
Use the actual **Heebo Bold** font as the primary rasterization source in Python if feasible.

Use the supplied PNG as:
- a control reference,
- a fallback visual reference,
- a validation image.

If loading the font directly is not possible in a reproducible way, document the fallback clearly and do not hide the tradeoff.

### Preferred development strategy
1. Build Hebrew-only first.
2. Generate 27 glyphs.
3. Validate visually on HP Prime.
4. Only then consider digits/punctuation.

This sequence is preferred over prematurely broad coverage.

---

## Testing Requirements

The implementation must be testable both:
- in generator-side sanity checks on PC,
- and in HP Prime visual verification.

### Python/generator-side checks
Include bounded validation such as:
- glyph dimensions are 14x20,
- exactly 20 rows per glyph,
- row values stay within 14-bit range,
- no empty glyph unless intentionally allowed,
- mapping table matches expected glyph count.

### HP Prime-side checks
The visual test must make it easy to verify:
- all glyphs render,
- glyphs are aligned,
- final forms are distinct,
- no glyphs overlap,
- no row corruption occurs.

---

## Output Format for Your Response

Your response must include:

### 1. Repo audit findings
What currently exists and what will be created/updated.

### 2. Design decisions
Glyph set, data format, mapping order, generator behavior, staging choices.

### 3. Implementation plan
Files to create/update and responsibilities per file.

### 4. Code
Provide actual implementation code for:
- `tools/generate_hebrew_font.py`
- `assets/hebrew_font_bitmap.ppl`
- `tests/test_bitmap_glyph_vis.ppl`

and any small helper files only if truly necessary.

### 5. Documentation content
Provide the content for `docs/BITMAP_FONT_SPEC.md`.

### 6. Test plan
How to run generator-side validation and HP Prime-side visual validation.

### 7. Definition of Done
Concrete acceptance criteria for this task.

### 8. Deferred items
Clearly list what remains out of scope.

---

## Coding and Engineering Discipline

- Keep generator code readable and deterministic.
- Keep PPL asset code modular and documented.
- Avoid fragile magic constants without explanation.
- Use explicit naming.
- Do not over-engineer beyond this task.
- Do not regress existing validated text engine work.
- Make migration from current hand-drawn Hebrew assets explicit.

---

## Final Instruction

Start with repo audit and specification alignment.

Then implement the **Hebrew-first bitmap font pipeline** with:
- reproducible generator,
- 27 Hebrew glyphs,
- fixed 14x20 1-bit row-integer storage,
- HP Prime asset module,
- visual validation test,
- specification document.

Prioritize unambiguous readability over decorative similarity.  
Use Heebo Bold as the design reference, but optimize for real readability on HP Prime hardware/emulator.