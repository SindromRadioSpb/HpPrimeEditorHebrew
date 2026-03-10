# Spike Results

**Project:** HP Prime Hebrew-Russian Editor
**Last updated:** 2026-03-10

---

## Spike-01: Hebrew Glyph Rendering via TEXTOUT_P

**Status:** COMPLETE
**Result:** FAIL
**Hebrew glyphs visible:** NO
**Decision:** HP Prime system font does NOT contain Hebrew glyphs. TEXTOUT_P cannot render Hebrew.
**Architecture impact:** Custom GROB bitmap glyphs required for all 22 Hebrew letters.

---

## Spike-02: Cyrillic / Russian Glyph Rendering via TEXTOUT_P

**Status:** COMPLETE
**Result:** PASS
**Cyrillic glyphs visible:** YES — Russian letters render correctly via TEXTOUT_P
**Decision:** No custom glyph assets needed for Cyrillic. Native TEXTOUT_P confirmed.

---

## Spike-03: Touch Event Loop Latency / Event Structure

**Status:** COMPLETE
**Result:** PASS (basic event capture works)
**Comment:** Touch events captured and logged on screen. WAIT(-1) successfully receives touch events.
**Event structure raw values:** PENDING — need to read the 0:..8: lines from screen output
**NOTE:** Request user to report exact string values shown in rows 0–8 to determine:
- Which TYPE() value identifies a touch event vs key press
- How to access x, y coordinates (ev(1), ev(2)(1), etc.)

---

## Spike-04: Custom GROB Glyph Pipeline

**Status:** COMPLETE
**Result:** PASS
**GROB rendering correct:** YES
**Comment:** X-like glyphs clearly visible for single and repeated blit.
  - Single glyph (BLIT G1 to screen): visible and correct
  - Row of 4 glyphs (BLIT G1 x4): visible and correct
**Confirmed:** DIMGROB_P, LINE_P(G1,...), BLIT_P pipeline works.
**Note:** SETPIX_P(G1,...) caused "bad argument type" in v1 — use LINE_P(G1,...) for drawing into GROBs.
**Decision:** Custom Hebrew glyph pipeline is viable. Hebrew glyphs will be drawn using LINE_P into GROBs.

---

## Spike-05: Document Size Performance

**Status:** COMPLETE
**Result:** PASS (correctness validated; timing skipped — TICKS does not exist)
**Program:** Spike05e_LocalList_Fix2

**Confirmed operations (200-line LOCAL list of strings):**
| Test | Operation | Result |
|---|---|---|
| T1 | `doc := {"Abc","Def","Ghi"}; line_txt := doc(2)` | PASS — `line_txt = "Def"` |
| T1 | `INSTRING(line_txt, "De")` | PASS — returns 1 |
| T2 | CONCAT loop × 200 | PASS — `SIZE(doc) = 200` |
| T3 | `doc(100) := doc(100) + "X"` | PASS — `line_txt = "line100X"` |
| T4 | `INSTRING(line_txt, "100")` | PASS — returns 5 |
| T5 | Line merge + list rebuild (delete row 101) | PASS — `SIZE(doc) = 199` |

**Root causes of all previous failures (now resolved):**
1. Single-letter globals (A, B, C) used as assignment targets → some are HP Prime reserved constants
2. `POS()` used for string substring search → wrong function; use `INSTRING()` instead
3. `i` not declared LOCAL → shadows imaginary unit only when explicitly declared `LOCAL i`
4. `TICKS` does not exist → removed; correctness-only test

**Confirmed safe patterns:**
- `LOCAL doc, doc2, idx, line_txt, found_pos, i` — all safe when declared LOCAL
- `FOR i FROM 1 TO n DO` — works when `i` is declared LOCAL
- `doc(n)` — list element read works on LOCAL list
- `doc(n) := value` — element assignment works on LOCAL list
- `INSTRING(str, substr)` — substring position (1-based), not `POS()`
- `CONCAT(doc, {item})` — list append works

---

## Architecture Decision — CONFIRMED

**Option C: Hybrid Rendering**

| Component | Method | Confirmed |
|---|---|---|
| Hebrew letters (22 basic) | Custom GROB bitmaps via DIMGROB_P + LINE_P | YES (Spike04 PASS) |
| Cyrillic / Russian | Native TEXTOUT_P | YES (Spike02 PASS) |
| ASCII / digits / punctuation | Native TEXTOUT_P | Assumed (probable) |
| Touch input | WAIT(-1) event loop | YES (Spike03 PASS) |
| GROB → screen blit | BLIT_P(dx1,dy1,dx2,dy2, G1, sx1,sy1,sx2,sy2) | YES (Spike04 PASS) |

## Confirmed Syntax Rules (from spikes)

- `CHAR(n)` — decimal codepoint, NOT `0x` prefix. Use `CHAR(1488)` not `CHAR(0x05D0)`
- `RECT_P(x1,y1,x2,y2,edgecol,fillcol)` — correct; no G0 as first arg
- `LINE_P(G1, x1,y1,x2,y2, color)` — draws into G1 (confirmed)
- `BLIT_P(dx1,dy1,dx2,dy2, G1, sx1,sy1,sx2,sy2)` — blits to G0 (screen); no G0 prefix
- `DIMGROB_P(G1, w, h, color)` — confirmed
- `SETPIX_P(G1, x, y, color)` — BAD ARGUMENT TYPE (do not use with G1)
- `TICKS` — does NOT exist in HP PPL (causes bad argument type)
- `TYPE(ev)` and `ev(2)(1)` — caused syntax errors; event structure not yet confirmed

---

## Spike-03b: Touch Event Structure (Detailed)

**Status:** COMPLETE
**Date run:** 2026-03-10

**Raw output from 1 tap (3 events):**
```
0: {#0:64h,#D0:-16h,#B2:-16h}
1: {#2:64h}
2: {#3:64h,#D0:-16h,#B2:-16h}
```

**Decoded:**
| Event | Type | X | Y | Meaning |
|---|---|---|---|---|
| 0 | 0 | 0xD0=208 | 0xB2=178 | Touch Down |
| 1 | 2 | — | — | Touch Up (no coords) |
| 2 | 3 | 0xD0=208 | 0xB2=178 | Click (tap complete) |

**Critical finding — event structure is FLAT, not nested:**
- `ev(1)` = event type integer
- `ev(2)` = x coordinate (only on types 0 and 3)
- `ev(3)` = y coordinate (only on types 0 and 3)
- **NOT** `ev(2)(1)` for x — element 2 is a direct integer, not a nested list

**Correct touch handler pattern:**
```ppl
ev := WAIT(-1);
IFERR
  t := ev(1);           // touch event (list)
  IF t == 3 THEN        // Click only (ignore Down=0 and Up=2)
    IF SIZE(ev) >= 3 THEN
      x := ev(2);       // x coordinate directly
      y := ev(3);       // y coordinate directly
      DISPATCH_TOUCH(x, y);
    END;
  END;
THEN
  IF ev == 4 THEN BREAK; END;  // ESC key
END;
```

**Note:** Each tap = 3 WAIT(-1) calls. Event loop must process all 3 before it's "free" again.
