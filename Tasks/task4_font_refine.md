# Claude Code Prompt — Bitmap Font Readability / Verifiability Refinement
## Project: Premium Hebrew-Russian Editor for HP Prime
## Repository: `J:\Project_Vibe\HpPrimeEditor`

You are refining an already working Hebrew bitmap font pipeline for HP Prime.

The current state is:
- the bitmap font pipeline exists,
- glyph generation works,
- 27 Hebrew glyphs are rendered,
- Unicode/codepoint mapping works,
- the font is acceptable as a technical MVP,
- but readability and one-to-one visual verifiability against printed Hebrew are still not strong enough for a premium editor.

This task is **not** to redesign the entire pipeline.
This task is to **improve the visual quality, distinctness, and verification reliability** of the existing Hebrew bitmap font.

---

## Goal

Strengthen the font so that glyphs are:

- easier to read quickly,
- less confusable with neighboring Hebrew letters,
- more reliably verifiable against printed Hebrew forms,
- still compatible with HP Prime constraints,
- still visually consistent as a fixed-cell UI bitmap font.

The primary goal remains:

**unambiguous readability**

The secondary goal remains:

**visual inspiration from Heebo Bold**

---

## Current Status Assumption

The current font is already:
- 14x20,
- 1-bit,
- fixed-cell,
- generated from a reproducible pipeline,
- integrated into:
  - `assets/hebrew_font_bitmap.ppl`
  - `tools/generate_hebrew_font.py`
  - `tests/test_bitmap_glyph_vis.ppl`
  - `docs/BITMAP_FONT_SPEC.md`

Do not throw this away.  
Refine it.

---

## Critical Quality Requirement

The font must not merely “look Hebrew-like”.

It must improve toward a state where:
- a human can distinguish each glyph quickly,
- final forms are clearly distinct from base forms,
- common confusable pairs are intentionally disambiguated,
- glyphs remain stable and visually coherent in running text,
- visual verification against standard printed Hebrew is realistic.

---

## Mandatory Quality Focus Areas

You must explicitly improve the font with attention to the following quality dimensions.

### 1. Distinctness of confusable pairs
You must treat these as mandatory review targets:

- ד / ר
- ה / ח
- ו / י
- כ / ב
- כ / ך
- מ / ם
- נ / ן
- פ / ף
- צ / ץ
- ש / ת
- ס / ט / ע

If needed, add additional problematic comparisons discovered during review.

### 2. Shape recognizability
The following glyphs are especially likely to need targeted refinement:
- א
- ט
- מ
- ע
- צ
- ש
- ת

Do not assume these are acceptable just because they render.
Examine them critically.

### 3. Printed-form verifiability
The glyphs should better resemble standard printed Hebrew forms, not just generic pixel abstractions.

### 4. Visual consistency
Improve consistency in:
- baseline,
- top alignment,
- visual stroke mass,
- interior negative space,
- right/left edge behavior,
- final-form silhouette logic.

---

## Required Work

### A. Audit the current generated glyphs
Inspect the currently generated font and identify:
- which glyphs are acceptable,
- which glyphs are weak,
- which glyph pairs are still too confusable,
- whether any final forms are insufficiently distinct.

Provide a concise but explicit glyph-by-glyph or group-by-group quality assessment.

### B. Improve the generator and/or glyph post-processing
You may refine quality by changing one or more of:
- rasterization size before downsampling,
- glyph placement inside the 14x20 cell,
- binarization threshold,
- post-binarization cleanup,
- per-glyph correction rules,
- per-glyph alignment tuning,
- selective boldening / thinning,
- selective pixel cleanup on problematic glyphs.

However:
- changes must remain reproducible,
- changes must be documented,
- do not introduce ad hoc undocumented hand edits.

### C. Add stronger quality validation
Extend visual validation so it becomes easier to verify:
- distinctness in isolation,
- distinctness in comparison pairs,
- appearance in short word-like runs.

---

## New Quality Constraints to Enforce

You must refine the font under the following additional requirements.

### 1. Glyph identity must dominate over style fidelity
If a glyph looks more like Heebo but becomes harder to distinguish, reject that outcome.
Readability and distinctness are more important than stylistic closeness.

### 2. Final forms must be unmistakable
The final forms:
- ך
- ם
- ן
- ף
- ץ

must not feel like near-duplicates of their base forms.
Their terminal structure and silhouette must be visibly distinct.

### 3. Running-text robustness matters
A glyph that looks acceptable in a single box may fail in a horizontal text run.
You must review glyphs both:
- in isolated grid view,
- and in text-strip / word-like sequences.

### 4. Weak glyphs must be fixed intentionally
Do not rely only on automatic generation if specific glyphs remain weak.
Bounded per-glyph refinement rules are allowed and expected.

### 5. Avoid over-fragmented pixel noise
At 14x20 and 1-bit, excessive micro-detail harms readability.
Prefer cleaner silhouettes over noisy fidelity.

---

## Required Deliverables

Update the existing relevant files as needed:

### 1. `tools/generate_hebrew_font.py`
Refine generation and/or post-processing logic.

### 2. `assets/hebrew_font_bitmap.ppl`
Regenerated improved glyph data.

### 3. `tests/test_bitmap_glyph_vis.ppl`
Expand and strengthen the visual validation test.

Add explicit comparison zones for confusable pairs and final forms.

### 4. `docs/BITMAP_FONT_SPEC.md`
Update the spec with:
- refinement rules,
- quality criteria,
- any per-glyph post-processing logic,
- new acceptance criteria.

### 5. Optional new doc
If useful, create:
- `docs/GLYPH_REFINEMENT_NOTES.md`

to explain which glyphs were refined and why.

---

## Required Validation Additions

The visual test must be enhanced to include the following sections or equivalent:

### Section 1 — Full glyph grid
All 27 Hebrew glyphs.

### Section 2 — Alignment strip
Base + finals in sequence.

### Section 3 — Confusable pair review
Explicit side-by-side comparisons for:
- ד / ר
- ה / ח
- ו / י
- כ / ב
- כ / ך
- מ / ם
- נ / ן
- פ / ף
- צ / ץ
- ש / ת
- ס / ט / ע

### Section 4 — Short reading strips
Short grouped sequences that simulate reading flow.
Examples:
- בדר
- וחי
- כמך
- מנם
- פף
- צץ
- שת
- סטע

These do not need to be linguistically meaningful; they exist for visual discrimination testing.

### Section 5 — Final-form verification
A focused view comparing each base letter with its final form.

---

## Acceptance Criteria

The refinement is successful only if all of the following are true:

1. The font still renders correctly on HP Prime.
2. All 27 Hebrew glyphs still map correctly.
3. Final forms are clearly separate and visually distinct.
4. The most confusable pairs are easier to tell apart than before.
5. The weakest glyphs have been intentionally improved.
6. The generator remains reproducible.
7. The visual test provides a materially better verification surface.
8. The result is still appropriate for integration into the editor renderer.

---

## Output Format

Your response must include:

### 1. Glyph quality audit
Concise assessment of current weak spots.

### 2. Refinement strategy
What you changed and why.

### 3. Files updated
Which files were changed and what role each change plays.

### 4. Code
Provide actual updated code for:
- generator,
- bitmap font asset module,
- visual test,
- docs updates.

### 5. Validation plan
How to verify the improved quality on HP Prime.

### 6. Definition of Done
Concrete criteria for accepting the refinement pass.

---

## Important Engineering Behavior

- Do not restart from scratch.
- Do not discard the existing pipeline.
- Do not claim glyph quality is “good enough” without explicit comparison against confusable pairs.
- Prefer bounded, testable refinements over broad aesthetic statements.
- Optimize for real readability on HP Prime, not just nice-looking screenshots on PC.

---

## Final Instruction

Refine the current Hebrew bitmap font so it becomes meaningfully better for:
- readability,
- pairwise distinctness,
- final-form differentiation,
- verification against printed Hebrew,
while keeping the pipeline reproducible and renderer-ready.