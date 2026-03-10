# RENDERER_PHASE1.md
## HP Prime Hebrew-Russian Editor — Renderer MVP

**Phase:** Task 5
**Status:** MVP complete
**Date:** 2026-03-10

---

## 1. Scope

### In scope
- Renderer module `src/renderer.ppl`
- Line-level direction model (LTR / RTL per line)
- Hebrew glyph rendering via `hebrew_font_bitmap` module
- Visible cursor rendering
- Deterministic viewport with `R_VIEW_TOP`
- Active line highlight
- Non-Hebrew fallback (placeholder boxes in RTL, TEXTOUT_P in LTR)
- Visual test harness `tests/test_renderer_basic.ppl` (8 scenarios)
- This documentation

### Out of scope (deferred)
- Full Unicode bidi algorithm
- Mixed-run bidi within a line
- Selection rendering
- Touch keyboard UI and event loop
- Search UI, file persistence UI
- Viewport scrolling (R_VIEW_TOP exists but scrolling is driven externally)
- Russian / Cyrillic character rendering finalization
- Production visual polish

---

## 2. Dependencies

| Module | Used functions |
|--------|---------------|
| `hebrew_font_bitmap` | `HFB_Init()`, `HFB_CodeToIdx(cp)`, `HFB_BlitGlyph(idx,x,y)` |
| `text_engine` | `L0` (global document list), `TE_LineCount()`, `TE_GetLine(lnum)` |

Both modules must be loaded on HP Prime before the renderer module.

---

## 3. Layout Model

**Screen:** 320 x 240 pixels

| Region | y range | Height | Purpose |
|--------|---------|--------|---------|
| Header bar | 0..15 | 16px | `REND_DrawStatus(label)` |
| Editor area | 16..213 | 198px | 9 lines x 22px each |
| Reserved | 214..239 | 26px | Future status/info strip |

**Editor geometry constants (set in `REND_Init`):**

| Global | Value | Meaning |
|--------|-------|---------|
| `R_LINE_H` | 22 | Line height in pixels |
| `R_LINES_VIS` | 9 | Visible line count |
| `R_X_LEFT` | 4 | Left margin (LTR start, RTL clip boundary) |
| `R_X_RIGHT` | 316 | Right reference (RTL glyph anchor, LTR clip boundary) |
| `R_Y_TOP` | 16 | Top y of editor area |
| `R_ADV_HEB` | 15 | Pixel advance per Hebrew glyph (14px cell + 1px gap) |
| `R_ADV_LTR` | 7 | Pixel advance per LTR char (TEXTOUT_P font size 1) |

**Viewport state:**

| Global | Default | Meaning |
|--------|---------|---------|
| `R_VIEW_TOP` | 1 | First visible line (1-based document index) |

Visible lines are `R_VIEW_TOP` through `R_VIEW_TOP + R_LINES_VIS - 1`.
Lines beyond document end are simply skipped (no rendering, no error).

---

## 4. Direction Model

**Strategy:** Line-level heuristic.

**Rule:** If any character in the line is in the range `CHAR(1488)..CHAR(1514)` (Hebrew block), the entire line is rendered in RTL mode. Otherwise LTR.

**Implemented by:** `REND_LineDir(txt)` — returns 1 for RTL, 0 for LTR.

**Rationale:** No full bidi algorithm at this phase. Line-level classification is deterministic, easy to test, and sufficient for an editor where each line is typically monodirectional (Hebrew-only or Latin/digit-only).

**Mixed-line behavior (documented limitation):** If a line contains both Hebrew and non-Hebrew characters, it is classified RTL. Non-Hebrew characters are rendered as gray placeholder boxes. This is intentional for MVP — it makes the fallback visible and testable. See Known Limitations.

---

## 5. Cursor Model

The logical cursor position `(cl, cc)` is maintained by the text engine:
- `cl` = 1-based line index
- `cc` = 1-based column, range `1..SIZE(line)+1`
- `cc=1` = before the first character
- `cc=SIZE+1` = after the last character

**LTR cursor x-position:**
```
cur_x = R_X_LEFT + (cc - 1) * R_ADV_LTR
```
- `cc=1` → `x = R_X_LEFT = 4` (left edge of editor, before first char)
- `cc=12` for "Hello World" → `x = 4 + 11*7 = 81`

**RTL cursor x-position:**
```
cur_x = R_X_RIGHT - (cc - 1) * R_ADV_HEB
```
- `cc=1` → `x = R_X_RIGHT = 316` (just right of first/rightmost glyph)
- `cc=5` for a 4-char RTL line → `x = 316 - 4*15 = 256` (left of all glyphs)

**RTL cursor placement rationale:**
In RTL mode, logical char `kk` is rendered at `bx = R_X_RIGHT - 14 - (kk-1)*R_ADV_HEB`.
The gap between char `kk` and char `kk+1` is at `bx_left_of_kk - 1 = R_X_RIGHT - (kk-1)*R_ADV_HEB - 1`.
Setting `cur_x = R_X_RIGHT - (cc-1)*R_ADV_HEB` places the cursor in the correct inter-glyph gap for all values of `cc`.

**Cursor visual:** 2-pixel wide vertical bar, height `R_LINE_H - 2` pixels, color `R_COL_CUR` (blue RGB(0,80,200)).
Drawn after line text so the cursor is on top.

**Empty line cursor:** `REND_DrawCursor` with `slen=0`, `cc=1` → cursor at `R_X_LEFT` (LTR) or `R_X_RIGHT` (RTL). Since an empty line has no Hebrew, it is LTR, so the cursor appears at `x=4`.

**Cursor clamping:** `cc` is clamped to `[1, slen+1]` before computing cursor x. `cur_x` is clamped to `[R_X_LEFT, R_X_RIGHT]`.

---

## 6. Rendering Behavior

### Hebrew glyph rendering
1. Detect Hebrew character: `ch >= R_HEB_FIRST AND ch <= R_HEB_LAST`
2. Resolve codepoint: `REND__CharCP(ch)` loops `CHAR(1488)..CHAR(1514)`
3. Get glyph index: `HFB_CodeToIdx(cp)` — returns 0 for unknown
4. Render: `HFB_BlitGlyph(idx, bx, scr_y)` — 14x20 bitmap glyph

### RTL line rendering
Characters are placed right-to-left:
- Char `kk` (1-based) blit at `bx = R_X_RIGHT - 14 - (kk-1)*R_ADV_HEB`
- Max visible chars per line: `floor((R_X_RIGHT - 14 - R_X_LEFT) / R_ADV_HEB) + 1 = 20`
- Clipped when `bx < R_X_LEFT` (EXIT loop)
- Hebrew chars → `HFB_BlitGlyph`
- Non-Hebrew chars → `REND__PlaceholderBox` (gray 14x20 box)

### LTR line rendering
Characters are placed left-to-right:
- `cur_x` starts at `R_X_LEFT = 4`
- Hebrew chars → `HFB_BlitGlyph(idx, cur_x, scr_y)`, advance `R_ADV_HEB`
- Non-Hebrew chars → `TEXTOUT_P(ch, cur_x, scr_y+6, 1, R_COL_FG)`, advance `R_ADV_LTR`
- The `+6` vertical offset approximates baseline alignment with Hebrew glyphs
- Clipped when `cur_x > R_X_RIGHT` (EXIT loop)

### Non-Hebrew fallback
| Context | Behavior |
|---------|----------|
| RTL line, non-Hebrew char | Gray placeholder box 14x20 |
| LTR line, non-Hebrew char | `TEXTOUT_P` font size 1 |
| LTR line, Hebrew char | `HFB_BlitGlyph` (unusual but handled) |

### Active line highlight
The cursor line gets a light-blue background `R_COL_ACT = RGB(230,240,255)` drawn before text rendering.

### Screen clearing
`REND_ClearArea()` fills the entire editor area with `R_COL_BG = RGB(255,255,255)` before each `REND_DrawDoc` call.

---

## 7. Public API

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `REND_Init()` | — | — | Init globals + `HFB_Init()` |
| `REND_IsHeb(ch)` | char | 0/1 | Is character Hebrew? |
| `REND_LineDir(txt)` | string | 0/1 | Line direction (0=LTR, 1=RTL) |
| `REND_ClearArea()` | — | — | Clear editor area to white |
| `REND_SetViewTop(vt)` | int | — | Set viewport top line |
| `REND_DrawLine(txt,y,rtl)` | string,int,0/1 | — | Render one line |
| `REND_DrawCursor(cc,y,rtl,slen)` | int,int,0/1,int | — | Render cursor bar |
| `REND_DrawDoc(cl,cc)` | int,int | — | Render full viewport |
| `REND_DrawStatus(label)` | string | — | Render header bar |

### Private helpers (EXPORT with double-underscore)
| Function | Description |
|----------|-------------|
| `REND__CharCP(ch)` | Hebrew char to decimal codepoint |
| `REND__PlaceholderBox(bx,by,bw,bh)` | Draw gray placeholder box |

---

## 8. Known Limitations

### 1. Mixed-line rendering
Lines containing both Hebrew and non-Hebrew characters are rendered in RTL mode with gray boxes for non-Hebrew. This is correct MVP behavior but not production bidi rendering. A line like "Hello שלום 123" will appear entirely from the right side with "Hello" and "123" replaced by placeholder boxes.

**Mitigation:** Documented and visible. Deferred to bidi phase.

### 2. LTR advance is uniform
In LTR mode, all non-Hebrew characters advance by `R_ADV_LTR = 7` pixels regardless of actual character width. Proportional spacing is not implemented in this phase.

### 3. RTL cursor offset assumes uniform Hebrew advance
The RTL cursor formula assumes all characters in the line are exactly `R_ADV_HEB` pixels wide. Mixed-content lines (Hebrew + placeholder boxes) have the same advance per slot, so this is consistent at MVP. If future phases render different widths, the cursor formula must be updated.

### 4. No viewport scrolling
`R_VIEW_TOP` is set manually via `REND_SetViewTop()`. The renderer does not scroll automatically when the cursor moves beyond the visible region. Scrolling will be driven by the keyboard/event-loop phase.

### 5. Hebrew-only range
Only codepoints 1488..1514 (22 base letters + 5 final forms) are handled as Hebrew. Vowel marks (niqqud), cantillation marks, and other Hebrew Unicode block codepoints are treated as non-Hebrew and rendered as placeholder boxes in RTL lines.

### 6. Baseline alignment is approximate
TEXTOUT_P characters at `scr_y+6` and HFB bitmap glyphs at `scr_y` are visually close but not precisely baseline-aligned. Exact alignment would require measuring font metrics.

### 7. No ASC() codepoint resolution
`REND__CharCP` uses an explicit loop through `CHAR(1488)..CHAR(1514)` to map characters to codepoints. This avoids `ASC()` which has uncertain behavior for non-ASCII characters on HP Prime. The loop is 27 iterations maximum and executes only for Hebrew characters.

---

## 9. Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| RTL cursor mismatch | Formula verified: `R_X_RIGHT - (cc-1)*R_ADV_HEB` places cursor in inter-glyph gap for all cc values |
| Off-by-one at line end | `cc` clamped to `[1, slen+1]` in `REND_DrawCursor` |
| Off-by-one at empty line | Empty line is LTR, cursor at `R_X_LEFT + 0 = 4` — valid |
| Viewport out of range | `REND_SetViewTop` clamps to `[1, TE_LineCount()]`; `REND_DrawDoc` exits loop when `abs_line > lcount` |
| Long line overflow | `EXIT` in render loops when clipping boundary is reached |
| Text engine coupling | Renderer only reads `TE_LineCount()` and `TE_GetLine()`; never writes to `L0` directly |

---

## 10. Future Integration

### Next phase: Keyboard / event loop
The renderer is designed to be called from an event loop:
```
loop:
  ev := WAIT(-1)
  process keypress -> update (cl, cc) via text engine
  REND_DrawDoc(cl, cc)
```
`REND_DrawDoc` is idempotent and safe to call on every keypress.

### Viewport scrolling
Add scroll logic to the event loop:
- If `cl < R_VIEW_TOP`: `REND_SetViewTop(cl)`
- If `cl >= R_VIEW_TOP + R_LINES_VIS`: `REND_SetViewTop(cl - R_LINES_VIS + 1)`

### Selection rendering
Add a `sel_start, sel_end` parameter to `REND_DrawDoc`.
Active selection renders with a different highlight color before text drawing.

### Full bidi
Replace `REND_LineDir` with a bidi paragraph analyzer.
`REND_DrawLine` would need a visual-order reordering pass before placement.

### Cyrillic / Latin proportional spacing
Replace uniform `R_ADV_LTR` with per-character advance using `TEXTOUT_P` metrics or a fixed-width Cyrillic bitmap font (analogous to the Hebrew font).

---

## 11. Test Harness

`tests/test_renderer_basic.ppl` — entry: `test_renderer_basic()`

| Scenario | What is tested |
|----------|---------------|
| S1 | Empty document, cursor on empty line |
| S2a/b/c | LTR line "Hello World", cursor at start/middle/end |
| S3a/b/c | RTL Hebrew line (shalom), cursor at right/middle/left |
| S4a/b | 6-line mixed doc, cursor on RTL lines |
| S5 | Words ending in all 5 sofit (final) forms |
| S6 | RTL line with embedded digits — placeholder boxes visible |
| S7 | Cursor on empty line between two Hebrew lines |
| S8 | 10-line doc, viewport starting at line 5, cursor at line 7 |

**To run on HP Prime:**
1. Load modules in order: `hebrew_font_bitmap`, `text_engine`, `renderer`, `test_renderer_basic`
2. Run `test_renderer_basic()` from the program catalog
3. Each scenario displays and waits; press any key to advance

---

## 12. Definition of Done

This phase is complete when:

1. `src/renderer.ppl` compiles without errors on HP Prime
2. `test_renderer_basic()` runs all 8 scenarios without crashes
3. Hebrew glyphs are visible on RTL lines using the bitmap font
4. Cursor is visible at correct positions in all scenarios
5. Active line highlight is visible (light blue background)
6. LTR lines render text left-to-right
7. RTL lines render glyphs right-to-left
8. S8 correctly shows lines 5-9 (not lines 1-4)
9. This document accurately describes all implemented behavior
