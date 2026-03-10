# GLYPH_REFINEMENT_NOTES.md
## Hebrew Bitmap Font — Task 4 Refinement Notes

**Generator version:** v2
**Date:** 2026-03-10

---

## 1. Audit of v1 Font (Task 3 baseline)

### Primary structural defect
All Hebrew glyphs occupied only **rows 9–18** of the 20-row cell (10 rows of content).
The top 8 rows were blank for all letters (except Lamed which uses rows 6–8 for its ascender).
This meant glyphs were rendered at ~10/20 = 50% of available cell height.
Stroke widths were 2px at most, insufficient for reliable reading at small sizes.

### Confusable pairs assessed

| Pair | v1 status | Problem |
|------|-----------|---------|
| He / Het | Borderline | He's left leg delayed by only 2 rows — subtle at small render size |
| Kaf / Bet | Acceptable | Different bottom shapes, both small |
| Samekh bottom | Weak | Closed with 1px at row 18 |
| Tav right foot | **Broken** | Right foot reduced to 1px at row 18, looked like it dropped off |
| Shin prongs | Acceptable | Middle prong 2px (vs outer 3px), minor asymmetry |
| Vav / Yod | Good | Height difference obvious |
| Dalet / Resh | Good | Width of top bar clearly different |

### Shape-specific issues
- **Tav (22)**: Right foot shrank to 1 pixel at the bottom. Looked broken.
- **He (5)**: Left leg appearance was delayed but still subtle at v1 size.
- **Samekh (15)**: Bottom closure was 1px. Acceptable but weak.

---

## 2. Refinement Strategy (v2)

### A. Rendering parameter improvements

| Parameter | v1 | v2 | Effect |
|-----------|----|----|--------|
| `scale` | 6 (render 84×120) | 8 (render 112×160) | Higher-res intermediate |
| `threshold` | 140 | 130 | Preserve more pixels from Bold font |
| `SIZE_FRACTION` | 0.82 | 0.92 | Glyphs 12% larger in cell |
| `BASELINE_FRACTION` | 0.88 | 0.83 | Baseline higher → glyphs fill rows 7–17 |

**Result:** Glyphs now occupy rows **7–17** (11+ rows of content, up from 10).
At 14×11px effective body size with bold strokes, all distinguishing features are clearly visible.

### B. Morphological cleanup

Added `remove_isolated_pixels()` post-processing:
- Removes pixels with fewer than 1 filled 4-connected neighbor
- Eliminates stray noise pixels from Lanczos antialiasing + threshold
- Does NOT remove pixels that are part of strokes

### C. Per-glyph correction framework

Added `GLYPH_CORRECTIONS` dict with operation-based row corrections:
- Supports: `set`, `or`, `and`, `xor` operations on specific rows
- Applied after auto-generation and cleanup
- Fully reproducible and documented

**Active corrections in v2:**

**He (5) — reinforce middle gap:**
- Rows 16–17: clear bits at columns 4–8 (prevent merging of left/right legs)
- In practice redundant with v2 parameters (gap already visible), but serves as documented intent

**Tav (22) — restore right foot:**
- Rows 17–18: add bits at columns 9–10 (right foot)
- Required in v1 to restore the missing foot. In v2, rendering may already provide this.
- Kept as safety net for this critical glyph shape.

**Samekh (15) — correction removed:**
- v1 plan was to add a bottom closure row. Removed because:
  (a) v2 renders a proper `....XXXXXX....` closure at row 16 already
  (b) Adding row 18 pixels created a detached mark below the oval — incorrect shape

---

## 3. Glyph-by-Glyph v2 Quality Assessment

### Hebrew base letters

| # | Letter | Shape | Status | Notes |
|---|--------|-------|--------|-------|
| 1 | Alef א | Diagonal cross with two arms | Good | Arms visible and separated |
| 2 | Bet ב | Open box, flat base | Good | Base clear, opening at top-left |
| 3 | Gimel ג | Foot shape | Acceptable | Auto-render reasonable |
| 4 | Dalet ד | Wide top bar + right descender | Good | Wide top distinguishes from Resh |
| 5 | He ה | Bar + late left leg + right leg | Good | Left leg delay distinguishes from Het |
| 6 | Vav ו | Tall narrow stroke | Good | Height clearly different from Yod |
| 7 | Zayin ז | Horizontal top + descender | Good | Clear shape |
| 8 | Het ח | Bar + both legs immediately | Good | Distinguishable from He |
| 9 | Tet ט | Rounded rect, open top | Good | Distinguishable from Samekh/Ayin |
| 10 | Yod י | Short small form | Good | Short height vs Vav is obvious |
| 11 | Kaf כ | Curved, open left, curved bottom | Good | Bottom curve distinguishes from Bet |
| 12 | Lamed ל | Ascender + body | Good | Only letter with ascender |
| 13 | Mem מ | Open/M shape | Good | Distinguishable from Mem sofit |
| 14 | Nun נ | Short top blob + descender | Good | Shorter than Nun sofit |
| 15 | Samekh ס | Closed oval | Good | Oval closes cleanly at row 16 |
| 16 | Ayin ע | Y-bifurcation merging at base | Good | Fork shape is distinctive |
| 17 | Pe פ | Rounded with interior element | Good | Interior detail visible |
| 18 | Tsadi צ | Two-pronged top | Good | Distinguishable from Tsadi sofit |
| 19 | Qof ק | Wide top arch + descender | Good | Wide bar distinguishes from Dalet |
| 20 | Resh ר | Narrower arch + descender | Good | Narrower than Dalet |
| 21 | Shin ש | Three prongs merging at base | Good | Three prongs clearly visible |
| 22 | Tav ת | Arch + two feet | Good | Two feet visible (Tav correction applied) |

### Hebrew final forms

| # | Letter | vs. Base | Status | Key distinction |
|---|--------|---------|--------|----------------|
| 23 | Kaf sofit ך | Kaf כ | Good | Long straight descender vs curved base |
| 24 | Mem sofit ם | Mem מ | Good | Closed box vs open M shape |
| 25 | Nun sofit ן | Nun נ | Good | Very long descender vs short |
| 26 | Pe sofit ף | Pe פ | Good | Long descender, different body |
| 27 | Tsadi sofit ץ | Tsadi צ | Good | Long descender, different top |

---

## 4. Confusable Pair Post-v2 Assessment

| Pair | Distinction mechanism | Rating |
|------|-----------------------|--------|
| ד (4) / ר (20) | Dalet: wide bar (10px); Resh: narrow arch (6px) | Strong |
| ה (5) / ח (8) | He: only right leg rows 9-10; Het: both legs from row 9 | Strong |
| ו (6) / י (10) | Vav: 11 rows; Yod: 6 rows — very different height | Strong |
| כ (11) / ב (2) | Kaf: curved bottom; Bet: wide flat base | Strong |
| כ (11) / ך (23) | Kaf: short, curved; KafSofit: long straight descender | Strong |
| מ (13) / ם (24) | Mem: open; MemSofit: closed rectangle | Strong |
| נ (14) / ן (25) | Nun: short body; NunSofit: very long descender | Strong |
| פ (17) / ף (26) | Pe: body+interior; PeSofit: long descender | Strong |
| צ (18) / ץ (27) | Tsadi: compact top; TsadiSofit: different top + long descender | Strong |
| ש (21) / ת (22) | Shin: 3 prongs; Tav: arch+2 feet | Strong |
| ס (15) / ט (9) / ע (16) | Samekh: closed oval; Tet: open top bucket; Ayin: Y-fork | Good |

---

## 5. Remaining Limitations

1. **Shin left margin**: The left prong of Shin starts at column 0 (no left margin). At 14px width with 3 prongs of 3px, there is no room for margins. Acceptable for a fixed-cell font.

2. **He left leg start (row 11)**: A single pixel at col 4 marks the initial appearance of He's left leg. This pixel is intentional (it IS the start of the left leg) but could be mistaken for noise. Not corrected — it is a legitimate letterform feature.

3. **Stroke weight variation**: Different letters have slightly different effective stroke widths (1-3px) depending on their shape. A perfectly uniform-weight bitmap font would require hand-crafting all glyphs, which is deferred.

4. **Visual verification on HP Prime hardware** (not emulator) is the final acceptance test. Emulator rendering may differ slightly from actual hardware display.

---

## 6. How to Re-generate

```
cd J:\Project_Vibe\HpPrimeEditor
python tools/generate_hebrew_font.py

# With inspection:
python tools/generate_hebrew_font.py --preview --pairs --no-ppl
```

All refinement rules are encoded in `generate_hebrew_font.py`:
- `SIZE_FRACTION`, `BASELINE_FRACTION`, `DEFAULT_SCALE`, `DEFAULT_THRESHOLD`
- `GLYPH_CORRECTIONS` dict
- `remove_isolated_pixels()` post-processor

No undocumented manual edits exist.
