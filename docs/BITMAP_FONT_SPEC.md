# BITMAP_FONT_SPEC.md
## Hebrew Bitmap Font Specification — HP Prime

**Task:** Task 3 — Hebrew Bitmap Font Pipeline
**Status:** Milestone A complete (27 Hebrew glyphs)
**Date:** 2026-03-10

---

## 1. Scope

### Included in this phase (Milestone A)
- 22 Hebrew base letters: Alef through Tav
- 5 Hebrew final forms: Kaf sofit, Mem sofit, Nun sofit, Pe sofit, Tsadi sofit
- Total: **27 glyphs** (indices 1–27)
- 1 blank/space placeholder at index 0
- Python generator producing reproducible output from Heebo Bold
- HP Prime PPL asset module (`assets/hebrew_font_bitmap.ppl`)
- Visual validation test (`tests/test_bitmap_glyph_vis.ppl`)

### Deferred (future milestones)
- Digits (0–9)
- Punctuation (`. , : ; ! ? - ( ) " ' / space`)
- Russian/Cyrillic characters (handled via native TEXTOUT_P per architecture decision)
- Latin characters
- Anti-aliased or 2-bit future font variant

---

## 2. Glyph Set

### Index order

| Index | Char | Unicode (decimal) | Unicode (hex) | Name |
|-------|------|-------------------|---------------|------|
| 0 | — | 32 | U+0020 | space/blank placeholder |
| 1 | א | 1488 | U+05D0 | Alef |
| 2 | ב | 1489 | U+05D1 | Bet |
| 3 | ג | 1490 | U+05D2 | Gimel |
| 4 | ד | 1491 | U+05D3 | Dalet |
| 5 | ה | 1492 | U+05D4 | He |
| 6 | ו | 1493 | U+05D5 | Vav |
| 7 | ז | 1494 | U+05D6 | Zayin |
| 8 | ח | 1495 | U+05D7 | Het |
| 9 | ט | 1496 | U+05D8 | Tet |
| 10 | י | 1497 | U+05D9 | Yod |
| 11 | כ | 1499 | U+05DB | Kaf |
| 12 | ל | 1500 | U+05DC | Lamed |
| 13 | מ | 1502 | U+05DE | Mem |
| 14 | נ | 1504 | U+05E0 | Nun |
| 15 | ס | 1505 | U+05E1 | Samekh |
| 16 | ע | 1506 | U+05E2 | Ayin |
| 17 | פ | 1508 | U+05E4 | Pe |
| 18 | צ | 1510 | U+05E6 | Tsadi |
| 19 | ק | 1511 | U+05E7 | Qof |
| 20 | ר | 1512 | U+05E8 | Resh |
| 21 | ש | 1513 | U+05E9 | Shin |
| 22 | ת | 1514 | U+05EA | Tav |
| 23 | ך | 1498 | U+05DA | Kaf sofit (DISTINCT glyph) |
| 24 | ם | 1501 | U+05DD | Mem sofit (DISTINCT glyph) |
| 25 | ן | 1503 | U+05DF | Nun sofit (DISTINCT glyph) |
| 26 | ף | 1507 | U+05E3 | Pe sofit (DISTINCT glyph) |
| 27 | ץ | 1509 | U+05E5 | Tsadi sofit (DISTINCT glyph) |

**Critical rule:** Final forms (23–27) are distinct glyphs, not aliases to base forms.
- כ (idx 11) ≠ ך (idx 23)
- מ (idx 13) ≠ ם (idx 24)
- נ (idx 14) ≠ ן (idx 25)
- פ (idx 17) ≠ ף (idx 26)
- צ (idx 18) ≠ ץ (idx 27)

### Reserved ranges for future milestones
- Indices 28–37: digits 0–9
- Indices 38+: punctuation
- Indices 50+: Latin / other

---

## 3. Cell Geometry

- **Cell size:** 14 × 20 pixels (width × height)
- **Bit depth:** 1-bit (0 = background, 1 = filled pixel)
- **Model:** Strict fixed-width cell; no proportional spacing
- **Baseline:** Glyphs positioned so descenders extend to approximately row 18–19
- **Top margin:** Rows 1–7 are typically empty (ascenders start around row 8)
- **Glyph height:** Effective glyph body occupies approximately rows 8–18 (11 rows)
- **Positioning:** Glyphs centered horizontally; ink starts at approximately column 3

---

## 4. Data Format

### Row-integer encoding

Each glyph is stored as **20 integers**, one per row (top to bottom).

Each integer encodes 14 pixels using **14-bit unsigned value**:

```
Bit 13 (0x2000) = leftmost pixel (column 0)
Bit 12 (0x1000) = column 1
Bit 11 (0x0800) = column 2
...
Bit 0  (0x0001) = rightmost pixel (column 13)
```

To test pixel at column `x` (0 = leftmost):
```
pixel = (row_value >> (13 - x)) & 1
```

### Storage layout

Global list `HFB_DAT` contains **560 integers** (28 glyphs × 20 rows).

Access formula (PPL, 1-based indexing):
```
// Glyph k (0..27), row r (1..20):
HFB_DAT(k * 20 + r)
```

Example: glyph 1 (Alef), row 1 → `HFB_DAT(21)`

`HFB_Init()` must be called once before any rendering function.

---

## 5. Generator Pipeline

### Source font
**Heebo Bold** (Google Fonts, SIL Open Font License)
Path on this system: `C:/Users/Win10_Game_OS/AppData/Local/Microsoft/Windows/Fonts/Heebo-Bold.ttf`

### Dependencies
```
pip install Pillow
```

### Generator: `tools/generate_hebrew_font.py`

**Inputs:**
- Heebo-Bold.ttf (auto-located or `--font PATH`)
- `--threshold N` (default 140): binarization threshold (0–255)
- `--scale N` (default 6): render oversampling factor

**Pipeline steps:**
1. For each glyph codepoint, render character at `(14 × scale) × (20 × scale)` pixels using Pillow
2. Font size ≈ `20 × scale × 0.82` pt to fill ~82% of cell height
3. Center glyph horizontally; align baseline at 88% of cell height
4. Lanczos-downsample to 14×20
5. Threshold: pixel < threshold → filled (1), else background (0)
6. Encode each row as 14-bit integer (bit 13 = leftmost pixel)
7. Emit flat 560-integer list for PPL embedding

**Outputs:**
- `assets/hebrew_font_bitmap.ppl` (complete PPL module)
- Terminal ASCII preview (with `--preview` flag)

**Validation:**
- 20 rows per glyph
- Row values in [0, 16383] (14-bit range)
- No entirely-blank glyphs for indices 1–27

**Reproducibility:**
- All parameters are explicit and documented
- No random state or system-font discovery side effects
- Re-running with same font + parameters produces identical output

### Re-running the generator
```
cd J:\Project_Vibe\HpPrimeEditor
python tools/generate_hebrew_font.py
```

Use `--preview` to inspect ASCII art before committing the PPL update.

---

## 6. Mapping Contract

Function `HFB_CodeToIdx(cp)` accepts a Unicode **decimal codepoint** (as used by HP PPL `CHAR()` function).

Returns:
- Glyph index 1–27 for recognized Hebrew codepoints
- 0 for unknown codepoints

Implementation: linear if-chain (PPL has no dict type). Sorted by codepoint.

### Using the mapping
```ppl
// Render the word שלום (Shin Lamed Vav Mem)
HFB_BlitGlyph(HFB_CodeToIdx(1513), x,    y);  // Shin
HFB_BlitGlyph(HFB_CodeToIdx(1500), x+14, y);  // Lamed
HFB_BlitGlyph(HFB_CodeToIdx(1493), x+28, y);  // Vav
HFB_BlitGlyph(HFB_CodeToIdx(1502), x+42, y);  // Mem
```

Or using `HFB_BlitRow`:
```ppl
HFB_BlitRow({1513,1500,1493,1502}, x, y, 0);
```

Note: Hebrew text is RTL visually. The caller is responsible for reversing display order if needed for RTL layout.

---

## 7. Rendering Contract

### HFB_Init()
Must be called once before any rendering. Loads `HFB_DAT` with glyph integers.

### HFB_BlitGlyph(idx, x, y)
- `idx`: glyph index 0–27 (0 = blank, no-op)
- `x, y`: top-left corner of the 14×20 cell on screen
- Draws filled pixels as `RGB(0,0,0)` using `LINE_P(G0, px,py,px,py,col)`
- Skips background pixels (transparent behavior)
- Writes directly to G0 (screen)

### HFB_GetRow(idx, row)
- Returns the row integer for glyph `idx`, row `1..20`
- Returns 0 for out-of-range inputs
- Useful for custom renderers or GROB-based blitting

### HFB_BlitRow(cp_list, x, y, spacing)
- `cp_list`: PPL list of decimal codepoints
- Renders each codepoint left-to-right starting at `(x, y)`
- `spacing`: extra pixel gap between glyphs (0 = tight)

### Performance note
`HFB_BlitGlyph` uses pixel-by-pixel `LINE_P` calls (up to 280 per glyph).
For dense text rendering, consider batching into a GROB using `DIMGROB_P` / `BLIT_P`.
The current API is designed for correctness and simplicity; performance optimization is deferred.

---

## 8. Quality Criteria

A glyph set is acceptable when:

1. **All 27 glyphs render** without corruption or blank cells
2. **Final forms are visually distinct** from their base forms at 14×20
3. **Confusable pairs are distinguishable**, specifically:
   - ד (Dalet) vs ר (Resh): Dalet has clear horizontal top-right corner; Resh has smooth arch
   - ה (He) vs ח (Het): He has open right leg; Het has closed top with both legs
   - ו (Vav) vs י (Yod): Vav is taller vertical stroke; Yod is short and curved
   - כ (Kaf) vs ב (Bet): Kaf has curved left wall; Bet has horizontal base
   - ס (Samekh) vs ט (Tet) vs ע (Ayin): closed circle vs open top vs bifurcated
   - ש (Shin) vs ת (Tav): Shin has 3 branches; Tav has 2 feet
4. **Alignment is consistent**: glyphs share a common baseline
5. **No row overflow**: no glyph bits exceed 14-bit width
6. **Glyphs fill reasonable coverage**: not too sparse, not bleeding to cell edges

---

## 9. Known Limitations

- **RTL layout not handled in font module**: `HFB_BlitRow` is LTR only; caller must reverse codepoint order for RTL display
- **No kerning**: strict fixed-cell, no inter-glyph adjustments
- **No diacritics**: nikud (vowel marks) not supported
- **Pixel-by-pixel render**: `HFB_BlitGlyph` calls `LINE_P` per filled pixel; may be slow for full-screen text
- **Hebrew only**: no Latin, digits, or punctuation in this milestone
- **Font dependency**: generator requires Heebo-Bold.ttf; if not available, use `--font` parameter
- **Lower rows empty**: Heebo Bold uses moderate descenders; some final-form descenders may appear in rows 17–19

---

## 10. Future Extensions

### Milestone B: Digits and punctuation
- Indices 28–37: digits `0 1 2 3 4 5 6 7 8 9`
- Indices 38+: `. , : ; ! ? - ( ) " ' / space`
- Same generator pipeline; add to GLYPHS list and regenerate

### Milestone C: GROB-based batch renderer
- Pre-render each glyph to a 14×20 GROB at init time
- Use `BLIT_P` instead of pixel-by-pixel for better performance
- Requires ~27 × DIMGROB_P calls at startup

### Milestone D: RTL layout engine
- Reverse codepoint order for RTL display
- Handle mixed RTL+LTR (Hebrew + digits/punctuation)
- Integrate with text engine cursor model

### Milestone E: Russian / Cyrillic
- Continue using native `TEXTOUT_P` for Cyrillic (confirmed to work in Spike02)
- No bitmap font needed for Russian

### Milestone F: 2-bit or 4-gray future
- If HP Prime supports 4-bit color GROBs efficiently
- Could provide anti-aliased appearance
- Currently deferred; 1-bit is sufficient for readability

---

## Migration from Old Glyph System

The old `assets/glyph_hebrew.ppl` (12×18, LINE_P hand-drawn, 22 base letters, no distinct finals) is **deprecated** by this system.

| Property | Old (glyph_hebrew.ppl) | New (hebrew_font_bitmap.ppl) |
|----------|------------------------|------------------------------|
| Cell size | 12×18 | 14×20 |
| Source | Hand-drawn LINE_P | Heebo Bold font rasterization |
| Glyph count | 22 (base only) | 27 (22 base + 5 distinct finals) |
| Final forms | Aliased to base | Distinct glyphs |
| Storage | LINE_P draw calls | 560-integer flat list |
| Reproducible | No | Yes (generator) |
| Renderer | LINE_P atlas blit | Pixel loop via LINE_P |

Old functions `HEB_Init`, `HEB_Blit`, `HEB_CodeToIdx` are replaced by:
`HFB_Init`, `HFB_BlitGlyph`, `HFB_CodeToIdx`

The old file is retained for reference but should not be used for new development.
