# HP Prime Hebrew-Russian Editor — Deep Planning Package

**Version:** 1.0
**Date:** 2026-03-10
**Status:** Pre-implementation planning (research-backed)
**Repository:** `J:\Project_Vibe\HpPrimeEditor`

---

## Table of Contents

1. [Repo Audit Findings](#1-repo-audit-findings)
2. [Problem Framing](#2-problem-framing)
3. [Product Requirements](#3-product-requirements)
4. [Technical Feasibility Assessment](#4-technical-feasibility-assessment)
5. [Rendering Architecture Options](#5-rendering-architecture-options)
6. [Recommended Architecture](#6-recommended-architecture)
7. [Text Engine Design](#7-text-engine-design)
8. [UI/UX Architecture](#8-uiux-architecture)
9. [Risk Register](#9-risk-register)
10. [Proof-of-Concept / Spike Plan](#10-proof-of-concept--spike-plan)
11. [Phased Implementation Plan](#11-phased-implementation-plan)
12. [Repository Bootstrap Plan](#12-repository-bootstrap-plan)
13. [Test Strategy](#13-test-strategy)
14. [Definition of Done](#14-definition-of-done)
15. [Blind Spots / Ambiguities / Shallowly-Specified Areas](#15-blind-spots--ambiguities--shallowly-specified-areas)
16. [Open Questions](#16-open-questions)
17. [Final Recommendation](#17-final-recommendation)

---

## 1. Repo Audit Findings

### 1.1 Current Repository State

The repository at `J:\Project_Vibe\HpPrimeEditor` was created from scratch. At audit time:

```
J:\Project_Vibe\HpPrimeEditor\
└── Tasks\
    └── task1.md
```

- No source code exists.
- No documentation exists (beyond task definition).
- No build conventions established.
- No test infrastructure exists.
- No scaffolding, no naming conventions.

**Conclusion:** This is a greenfield project. All structure must be established before implementation begins.

---

### 1.2 Platform: HP Prime — Confirmed Capabilities

Sources: HP official documentation, HP Museum forums, hpcalc.org community, manufacturer datasheets.

| Capability | Detail | Confidence |
|---|---|---|
| Screen resolution | 320 × 240 pixels | CONFIRMED |
| Usable area | 320 × 220 px (bottom 20 px = system menu bar) | CONFIRMED |
| Color format | 16-bit A1R5G5B5 (packed integer) | CONFIRMED |
| G1 CPU | ARM ~400 MHz | CONFIRMED |
| G2 CPU | ARM Cortex-A7 @ 528 MHz | CONFIRMED |
| G1 RAM | 32 MB total, ~16 MB usable | CONFIRMED |
| G2 RAM | 256 MB total, ~128 MB usable | CONFIRMED (estimate) |
| Internal encoding | UTF-16 Little Endian | CONFIRMED |
| String max length | 65,535 characters | CONFIRMED |
| GROB objects | G0 (display) + G1–G9 (off-screen buffers) | CONFIRMED |
| TEXTOUT_P font sizes | 7 sizes: 10pt–22pt | CONFIRMED |
| Touch input model | Polling via WAIT(-1) or MOUSE() | CONFIRMED |
| Events per single tap | 3 (Down → Up → Click) | CONFIRMED |
| Persistence options | EXPORT variables; App Note (.hpappnote) | CONFIRMED |
| File I/O API | None — no fopen/fwrite | CONFIRMED ABSENT |
| RTL text support | None — TEXTOUT always LTR | CONFIRMED ABSENT |
| BiDi algorithm | None | CONFIRMED ABSENT |
| Emulator | HP Prime Virtual Calculator (Windows, v2.4.15515) | CONFIRMED |
| Mouse = touch in emulator | Yes | CONFIRMED |

---

### 1.3 Critical Unconfirmed Platform Facts (Blockers)

| Topic | Risk Level | Notes |
|---|---|---|
| Hebrew glyphs in system font | **CRITICAL** | No confirmed test found. Character browser has 23,000+ chars but font rendering ≠ character entry |
| Cyrillic (Russian) glyphs in TEXTOUT | **HIGH** | Likely present but unconfirmed; "ASCII > 128 garbled" report from older firmware |
| Hebrew combining diacritics (nikud) | **CRITICAL** | Combining chars behavior in TEXTOUT unknown; likely broken |
| Recursion depth limit | MEDIUM | No documented number; affects parser design |
| GROB size limit beyond RAM | LOW | Implicitly RAM-limited |
| Multitouch in Virtual Calculator | LOW | May need real device for two-finger tests |

---

### 1.4 Sources Reviewed

- HP Prime User Guide (official, HP Inc.)
- HP Prime Programming Tutorial — Edward Shore (literature.hpcalc.org)
- TI-Planet HP Prime Wiki (wiki.tiplanet.org)
- HP Museum Forum thread archive (hpmuseum.org)
- Cemetech HP Prime programming forum
- codewalr.us HP Prime community
- holyjoe.net HP Prime reserved variables reference
- HP Prime G2 official datasheet
- hpcalc.org software archive

---

### 1.5 Critical Feasibility Conclusions from Audit

1. **No Hebrew RTL system font rendering can be assumed.** A custom glyph-rendering approach must be planned from the start.
2. **TEXTOUT is LTR only.** Hebrew visual layout requires string reversal before rendering, and cursor logic must work in logical order.
3. **Persistence is viable** via EXPORT globals or App Note, but no general file I/O exists.
4. **Performance for a text editor** (not video) is tractable on G2; G1 is a concern for complex redraw.
5. **Touch input is polling-based**, requiring a tight event loop — manageable but architecturally important.
6. **The project has no precedent** on HP Prime: no prior Hebrew/RTL editor exists in any community archive.

---

## 2. Problem Framing

### 2.1 What "Full-Featured Hebrew-Russian Editor on HP Prime" Actually Means

On a desktop, "full-featured Hebrew text editor" implies:
- Unicode font system with complete Hebrew glyph table and diacritics
- OS-level BiDi algorithm (Unicode Standard Annex #9)
- System clipboard, IME integration, font selection
- File system I/O, undo history, multiple documents

**None of these exist on HP Prime.**

On HP Prime, "full-featured" must be re-scoped to mean:
- Custom glyph rendering for Hebrew and Cyrillic characters (bitmaps embedded in app)
- Logical-order storage with visual reversal for Hebrew
- Simplified BiDi: "pure Hebrew runs" and "pure Russian runs" interleaved, no full UAX#9
- Virtual on-screen keyboard for Hebrew and Russian character input
- Single document editing with persistence via EXPORT/Note
- Text navigation, insert, delete, search
- Viewport scrolling for documents longer than screen

### 2.2 In Scope

- Hebrew character input (22 basic letters; optional: final forms)
- Russian/Cyrillic input (33 letters + Ё)
- ASCII digits and common punctuation
- Mixed Hebrew-Russian text in a single document
- Insert-mode editing (no overwrite)
- Backspace/delete
- Cursor navigation (left, right, line start, line end, next/prev line)
- Viewport scrolling (line by line, page by page)
- Substring search (forward)
- Virtual on-screen keyboard with Hebrew and Russian layouts
- Document persistence (single document per app instance)
- Status bar (current mode, cursor position, language indicator)

### 2.3 Out of Scope (Explicitly Deferred or Rejected)

| Feature | Reason |
|---|---|
| Full UAX#9 BiDi algorithm | Too complex for HP Prime constraints; simplified model sufficient |
| Hebrew diacritics / nikud | Glyph complexity and combining-char rendering; deferred post-MVP |
| Undo/redo history | Memory cost; deferred to Phase 2 |
| Multiple open documents | Single-document per run is simpler and safer |
| Copy/paste via system clipboard | No HP Prime clipboard API |
| Rich text / formatting | Out of scope entirely |
| Regex search | Too complex; simple substring only |
| Font selection / size adjustment | Single fixed rendering font |
| RTL paragraph embedding per UAX#9 | Simplified: paragraph-level direction flag only |
| Hebrew final letter forms (ך ם ן ף ץ) | Optional Phase 2 if glyph set is extended |

### 2.4 Desktop Expectations That Are Impossible

- Smooth sub-pixel text rendering
- System-level IME for Hebrew/Russian
- Auto-correct / spell check
- Variable-width proportional fonts (PPL rendering is fixed metrics)
- Clipboard paste from PC
- "Instant" (<1ms) response — expect 10-50ms per frame redraw

---

## 3. Product Requirements

### 3.1 Functional Requirements

#### FR-01: Text Buffer Model
- Store document as a list of logical lines: `LIST_OF_STRINGS`
- Each line is a UTF-16 string in **logical insertion order** (not visual display order)
- Hebrew characters stored left-to-right in logical order; visual reversal is the renderer's job
- Maximum document size: 200 lines × 80 characters = 16,000 characters (soft limit; configurable)

#### FR-02: Hebrew Input
- Virtual keyboard with 22 Hebrew letters (+ 5 final forms in Phase 2)
- Pressing a Hebrew letter inserts it at cursor position in logical order
- Hebrew text runs have `direction = RTL` at the logical level
- Characters appear visually right-to-left in the editor area

#### FR-03: Russian Input
- Virtual keyboard with 33 Cyrillic letters (upper + lower case layouts)
- Insert at cursor position in logical order
- Russian text runs are LTR

#### FR-04: Mixed Text Input
- A single line can contain Hebrew, Russian, digits, and punctuation
- Direction switching is explicit (user switches via mode key)
- Simplified model: each character carries no BiDi property internally; the mode flag at insertion time determines visual placement order

#### FR-05: Virtual Keyboard
- On-screen keyboard occupies lower 100 px of screen (320 × 100 area)
- 3 layouts: Hebrew (RTL layout), Russian (LTR layout), Numeric/Symbol
- Layout switch buttons visible at all times within keyboard
- Minimum key touch target: 26 × 26 pixels
- Delete and Enter keys on all layouts

#### FR-06: Navigation
- Arrow keys on physical keyboard or virtual arrow buttons
- Left/Right: move cursor one logical character position
- Up/Down: move to same approximate visual column in adjacent line
- Home/End: jump to line start/end
- PgUp/PgDn: scroll viewport by one screenful of lines

#### FR-07: Editing Operations
- Insert character at cursor
- Backspace: delete character to left of cursor (in logical order)
- Delete: delete character to right of cursor (in logical order)
- Enter: split current line at cursor

#### FR-08: Search
- Enter a search string via a search popup
- Forward search from current cursor position
- Highlight (visually) the first match found
- "Next match" navigation
- Case-insensitive search option

#### FR-09: Selection (Deferred to Phase 2)
- Tap-and-hold to begin selection
- Drag to extend
- Selection highlighting

#### FR-10: Persistence
- Document auto-saves to EXPORT variable on any edit (debounced: every 5 seconds or on app exit)
- On app start: load from EXPORT variable if non-empty
- "New document" action: clears buffer with confirmation

#### FR-11: Document Open/Save Model
- Single document per app instance
- Document saved to: exported global variable `HPEDITOR_DOC` (list of strings)
- Future: export to App Note for readability outside the editor

#### FR-12: Viewport Scrolling
- Editor area shows N visible lines (N depends on font size and editor area height)
- Scroll offset tracked as `first_visible_line` index
- Redraw triggered on cursor movement that would move off-screen

#### FR-13: Line Wrapping
- Phase 1: **no soft wrap** — lines wider than viewport are scrolled horizontally via cursor position clamping
- Phase 2: optional soft wrap at word boundary

#### FR-14: Status Bar
- Fixed 20 px strip at top of editor area (not bottom, to avoid system menu bar overlap)
- Shows: current language mode (HE/RU/EN), cursor position (line:col), document dirty indicator

#### FR-15: Error States
- Document full: notify user, block further input
- Glyph not found: render placeholder rectangle
- Search no match: display "Not found" notification for 2 seconds

---

### 3.2 Non-Functional Requirements

| NFR | Target |
|---|---|
| Frame redraw latency | < 100 ms per full screen redraw (G2); < 200 ms (G1) |
| Key-to-screen response | < 200 ms from touch event to updated display |
| Max document size | 16,000 characters (bounded to fit in RAM with headroom) |
| Memory footprint | Glyph bitmaps + document + buffers < 4 MB total |
| Crash / corruption | No data loss on unexpected power-off (EXPORT auto-save) |
| UX consistency | All touch targets ≥ 26 × 26 px; no accidental target overlap |
| Redraw flicker | Double-buffer all redraws (G1 → G0 BLIT_P only) |
| Code maintainability | All PPL modules < 300 lines; explicit comment blocks for RTL logic |

---

## 4. Technical Feasibility Assessment

### 4.1 Definitely Feasible

| Feature | Evidence |
|---|---|
| Full-screen double-buffered UI | Confirmed community demos (video playback via BLIT_P) |
| Virtual keyboard with touch hit-testing | MOUSE()/WAIT(-1) confirmed; tap coordinates returned |
| Logical text storage as list-of-strings | UTF-16 strings, 65,535 char limit, list containers confirmed |
| EXPORT variable persistence | Confirmed; survives power-off |
| Russian (Cyrillic) rendering | Very likely; Cyrillic is a major Unicode block; probable font coverage |
| Search (substring match) | POS() function confirmed in PPL |
| Status bar | Trivial TEXTOUT_P rendering |
| Virtual Calculator development on PC | Confirmed; mouse = touch input |

### 4.2 Probably Feasible

| Feature | Evidence |
|---|---|
| Hebrew basic letter rendering via system font | Character browser shows 23,000+ chars; Hebrew block likely included; needs spike |
| Custom glyph rendering as fallback | GROB BLIT_P confirmed; embedding bitmaps is standard technique |
| RTL visual reversal (manual) | Trivially done in PPL by reversing string before TEXTOUT_P |
| Touch keyboard responsiveness | Event loop with WAIT(-1) or MOUSE() polling is standard; 3-event tap handling is documented |
| Mixed RTL/LTR display | With simplified model (no UAX#9), feasible via line-segment decomposition |

### 4.3 Risky / Uncertain

| Feature | Risk |
|---|---|
| Hebrew glyph coverage in system font | Unknown. If font lacks Hebrew glyphs, full custom render required |
| Hebrew diacritics (combining chars) | Combining char rendering in TEXTOUT_P unverified; likely broken |
| Performance on G1 hardware | 32 MB RAM, ~400 MHz; full custom glyph render may be slow |
| Correct cursor positioning in mixed RTL/LTR text | Complex semantics; needs careful design and validation |
| Line wrapping with mixed-direction runs | Very complex to implement correctly; deferred |

### 4.4 Likely Impossible or Too Expensive

| Feature | Reason |
|---|---|
| Full Unicode BiDi (UAX#9) | Requires O(n) state machine per line; too complex and slow in PPL |
| Hebrew vowel points (nikud) as combining chars | Combining glyph rendering unverified; likely broken |
| System clipboard integration | No clipboard API exists in HP PPL |
| Multiple simultaneous open documents | Memory and UX complexity not warranted |
| System-level IME | No IME API in HP PPL |

### 4.5 Requires Proof-of-Concept Before Commitment

| Feature | Why |
|---|---|
| Hebrew system font rendering | This is the most critical unknown; determines entire rendering architecture |
| Cyrillic TEXTOUT rendering | Must verify not garbled on current firmware |
| Touch event loop latency | Must measure actual key-to-display delay |
| Document size performance | Must verify list operations at 200 lines do not lag |

---

## 5. Rendering Architecture Options

### Option A: Native TEXTOUT-First Rendering

**Description:** Trust the HP Prime system font to render Hebrew and Cyrillic glyphs via `TEXTOUT_P`. Store text in logical order; reverse Hebrew strings before display. No custom glyph bitmaps.

| Criterion | Assessment |
|---|---|
| Implementation cost | LOW — no glyph assets needed |
| Hebrew RTL quality | MEDIUM — visual order achieved by string reversal; no per-character BiDi |
| Hebrew glyph quality | UNKNOWN — critical risk |
| Cyrillic quality | PROBABLY GOOD — if font covers Cyrillic |
| Mixed-text quality | MEDIUM — simplistic but workable with run detection |
| Risk level | VERY HIGH — entire approach fails if Hebrew glyphs are absent |
| Fallback | Must switch to Option B or C if font lacks Hebrew |
| Recommendation | **Do not commit to this without Spike-01 results** |

---

### Option B: Full Custom Glyph Bitmap Rendering

**Description:** Pre-render all needed characters (22 Hebrew letters + 33 Cyrillic letters + ASCII) as fixed-size bitmaps, embed in the app as GROB data, and composit them via `BLIT_P` instead of using `TEXTOUT_P` at all.

| Criterion | Assessment |
|---|---|
| Implementation cost | HIGH — must create ~80+ glyph bitmaps; GROB embedding is tedious |
| Hebrew glyph quality | COMPLETE CONTROL — render exactly what we design |
| Hebrew RTL quality | GOOD — glyph positioning fully controlled |
| Cyrillic quality | COMPLETE CONTROL |
| Mixed-text quality | BEST — full control over run layout |
| Risk level | LOW — no dependency on system font |
| Memory cost | ~80 glyphs × (12×18 pixels × 2 bytes) ≈ 35 KB — well within limits |
| Performance | BLIT_P is fast; acceptable for text editing redraw rates |
| Recommendation | **Safest option; recommended if Spike-01 fails** |

---

### Option C: Hybrid — TEXTOUT for ASCII/Cyrillic, Custom Glyphs for Hebrew

**Description:** Use native `TEXTOUT_P` for ASCII, digits, punctuation, and Cyrillic (if confirmed working). Use custom GROB bitmaps only for Hebrew characters (22–27 glyphs). This minimizes asset creation while solving the Hebrew rendering gap.

| Criterion | Assessment |
|---|---|
| Implementation cost | MEDIUM — only Hebrew glyphs need bitmaps |
| Hebrew glyph quality | FULL CONTROL for Hebrew portion |
| Cyrillic quality | DEPENDS on system font — same risk as Option A for Cyrillic |
| Mixed-text quality | MEDIUM — mixed rendering paths add complexity |
| Risk level | MEDIUM — still depends on Cyrillic font coverage |
| Alignment problems | Mixing TEXTOUT_P and BLIT_P glyph heights must be normalized |
| Recommendation | **Viable if Spike-01 confirms Cyrillic works, Hebrew doesn't** |

---

### Option D (Bonus): MicroPython Custom Renderer

**Description:** Implement the rendering engine in HP Prime MicroPython instead of PPL.

| Criterion | Assessment |
|---|---|
| Language capability | More expressive than PPL; easier to write BiDi logic |
| Performance | Community reports contradictory (10× faster / "buggy") |
| Stability | Reported as buggy by community; not production-ready |
| Risk level | HIGH — community stability reports are unfavorable |
| Recommendation | **Do not use for core rendering; consider for batch processing only** |

---

### Comparison Summary

| Option | Implementation Cost | Hebrew Quality | Risk | Recommended |
|---|---|---|---|---|
| A: Native TEXTOUT | Low | Unknown → High risk | Very High | No (without spike) |
| B: Full Custom Glyphs | High | Excellent | Low | YES (default fallback) |
| C: Hybrid | Medium | Good | Medium | Yes (if Cyrillic confirmed) |
| D: MicroPython | Medium | Unknown | High | No |

---

## 6. Recommended Architecture

**Primary recommendation: Option C (Hybrid), with validated fallback to Option B.**

Rationale: The hybrid approach minimizes asset creation work while addressing the Hebrew rendering risk definitively. Spike-01 will determine if Cyrillic works natively. If it does, we save ~33 Cyrillic glyph assets. If it doesn't, we fall back to full Option B without architectural changes — only asset additions.

---

### 6.1 Document Model

```
HPEDITOR_DOC : LIST of STRINGS
  Each element: one logical line (UTF-16 string)
  Logical order: characters stored in insertion order
  Hebrew characters stored L→R in logical buffer
  Russian characters stored L→R in logical buffer
  Max lines: 200
  Max chars per line: 80 (soft limit)
  Empty document: {""} (list with one empty string)
```

Line direction metadata (for display):

```
HPEDITOR_DIRS : LIST of INTEGERS
  Each element: 0 = line is predominantly LTR (Russian/ASCII)
                1 = line is predominantly RTL (Hebrew)
  Default: follows language mode at line creation time
```

---

### 6.2 Cursor Model

```
CURSOR_LINE : INTEGER  (0-based line index)
CURSOR_COL  : INTEGER  (0-based logical column; 0 = before first char)
```

Cursor semantics:
- In logical space (insertion order), not visual space
- Moving "right" in LTR text moves to higher logical column
- Moving "right" in RTL visual display moves to lower logical column (for the user: moves deeper into Hebrew text)
- Cursor is always valid: clamped to [0, LENGTH(current_line)]

---

### 6.3 Viewport Model

```
VIEW_TOP_LINE : INTEGER  (index of first visible line)
VIEW_LINES    : INTEGER  (number of visible lines; computed from editor area height / line_height)
```

Redraw triggers:
- Any cursor movement
- Any edit operation
- Mode change
- Search match highlight

---

### 6.4 Logical vs Visual Text Representation

For rendering a line `s` with direction `dir`:
- If `dir = 0` (LTR): render `s` left-to-right
- If `dir = 1` (RTL): render `REVERSE(s)` left-to-right starting from right edge of editor area

Mixed lines (Hebrew + Russian on same line):
- Phase 1: use paragraph-level direction only (whole-line direction)
- Phase 2: implement run-level BiDi (segment detection, per-run reversal)

---

### 6.5 Virtual Keyboard Subsystem

```
KB_MODE: INTEGER  (0 = Hebrew, 1 = Russian, 2 = Symbol/Numeric)
KB_LAYOUT: LIST of LISTS  (grid of {label, unicode_codepoint} pairs)
KB_KEY_W: INTEGER  (key width in pixels)
KB_KEY_H: INTEGER  (key height in pixels)
```

Keyboard occupies rows 120–219 (100 px height, 320 px width).
Key layout: 4 rows × 10 columns max (40 key slots; some merged for larger keys).

---

### 6.6 Search Subsystem

```
SEARCH_ACTIVE:  BOOLEAN
SEARCH_QUERY:   STRING
SEARCH_LINE:    INTEGER  (current match line)
SEARCH_COL:     INTEGER  (current match column)
SEARCH_RESULTS: LIST of {line, col} pairs
```

Implementation: `POS(haystack, needle)` within each line; iterate lines from cursor forward.

---

### 6.7 Persistence Subsystem

```
EXPORT HPEDITOR_DOC;    // Document lines
EXPORT HPEDITOR_DIRS;   // Line direction flags
EXPORT HPEDITOR_META;   // {cursor_line, cursor_col, view_top, kb_mode, last_saved_tick}
```

Auto-save trigger: every 300 event-loop iterations (approximately 5-10 seconds) or on ESC/exit.

---

### 6.8 Rendering Loop

```
LOOP:
  event = WAIT(-1)
  PROCESS_EVENT(event)        // update model state
  IF redraw_needed THEN
    RENDER_TO_G1()             // all drawing to G1
    BLIT_P(G0, 0,0,320,220, G1, 0,0,320,220)  // flip to screen
    redraw_needed = 0
  END
  IF auto_save_due THEN
    SAVE_DOCUMENT()
  END
END LOOP
```

Key principle: **dirty flag rendering** — only redraw when state changes.

---

### 6.9 Event Handling Model

Events from `WAIT(-1)`:
- Touch list `{type, {x,y}, ...}`:
  - type 0 (Down): record, no action
  - type 2 (Up): record, no action
  - type 3 (Click): dispatch to hit-test → keyboard key press OR scroll control OR search button
  - type 7 (Long Click): future selection start
- Integer (key code): dispatch to physical key handler
  - Key 2 (Up), 12 (Down), 7 (Left), 8 (Right): cursor movement
  - Key 30 (Enter): insert newline
  - Key codes for physical keyboard letters: insert ASCII character

---

## 7. Text Engine Design

### 7.1 Logical Storage Format

Document stored as `LIST` of `STRING`s. Each string is one paragraph (logical line). No embedded newlines within a string. Newline = end of list element.

```ppl
// Document initialization
EXPORT HPEDITOR_DOC;
HPEDITOR_DOC := {""};  // One empty line
```

### 7.2 Insertion Rules

```
INSERT_CHAR(ch):
  line_str := HPEDITOR_DOC(CURSOR_LINE + 1);
  left_part := MID(line_str, 1, CURSOR_COL);
  right_part := MID(line_str, CURSOR_COL + 1, SIZE(line_str) - CURSOR_COL);
  HPEDITOR_DOC(CURSOR_LINE + 1) := left_part + ch + right_part;
  CURSOR_COL := CURSOR_COL + 1;
  DIRTY := 1;
```

For Hebrew mode: `ch` is a Hebrew codepoint character inserted at logical position. Visual reversal is renderer's job.

### 7.3 Deletion Rules

```
BACKSPACE():
  IF CURSOR_COL > 0 THEN
    line_str := HPEDITOR_DOC(CURSOR_LINE + 1);
    left_part := MID(line_str, 1, CURSOR_COL - 1);
    right_part := MID(line_str, CURSOR_COL + 1, SIZE(line_str) - CURSOR_COL);
    HPEDITOR_DOC(CURSOR_LINE + 1) := left_part + right_part;
    CURSOR_COL := CURSOR_COL - 1;
  ELSE IF CURSOR_LINE > 0 THEN
    // Merge with previous line
    prev_line := HPEDITOR_DOC(CURSOR_LINE);
    curr_line := HPEDITOR_DOC(CURSOR_LINE + 1);
    HPEDITOR_DOC(CURSOR_LINE) := prev_line + curr_line;
    // Remove current line from list
    CURSOR_COL := SIZE(prev_line);
    CURSOR_LINE := CURSOR_LINE - 1;
    REMOVE_LINE(CURSOR_LINE + 2);
  END
```

### 7.4 Cursor Semantics

- Cursor is **between characters**, not on a character.
- Column 0 = before first character (or at start of empty line).
- Column `SIZE(line)` = after last character.
- In RTL lines: column 0 is the rightmost visual position; column `SIZE(line)` is leftmost visual position.
- Physical arrow key "Right":
  - LTR line: `CURSOR_COL++`
  - RTL line (Hebrew): `CURSOR_COL++` (still move right in logical space; visually moves left)
  - **UX note:** we must decide whether to expose "logical right" or "visual right" to the user.
  - **Phase 1 decision:** physical Right key = logical right (simpler; may confuse RTL users).
  - **Phase 2:** implement "visual right" navigation (more correct for RTL editing but complex).

### 7.5 Movement Rules for Mixed RTL/LTR Text

Phase 1 (simplified):
- All cursor movement is in **logical order**.
- The cursor position indicator in status bar shows logical column.
- No visual-order cursor flipping.

Phase 2 (correct bidi navigation):
- Detect RTL run at cursor position.
- Map logical ↔ visual position using run-level BiDi mapping.
- Implement visual cursor movement (Left key always moves cursor visually left, regardless of character direction).

### 7.6 Line Wrapping Strategy

Phase 1: **No soft wrap.** If a line exceeds viewport width, the renderer clips at the edge. A horizontal scroll offset (`H_SCROLL`) per line allows seeing the rest.

Phase 2: Soft wrap at character boundary (not word boundary, since RTL word boundaries are complex).

### 7.7 Search Strategy

```
SEARCH_FORWARD(query):
  n := SIZE(HPEDITOR_DOC);
  // Start from cursor position
  FOR line FROM CURSOR_LINE TO n-1 DO
    haystack := HPEDITOR_DOC(line + 1);
    IF KB_MODE == 0 THEN  // Hebrew search: both query and haystack in logical order
      pos := POS(haystack, query);
    ELSE
      pos := POS(UPCASE(haystack), UPCASE(query));
    END
    IF pos > 0 THEN
      SEARCH_LINE := line;
      SEARCH_COL := pos - 1;
      RETURN 1;
    END
  END
  RETURN 0;
```

### 7.8 Normalization Assumptions

- No Unicode normalization (NFC/NFD/NFKC) applied. Text stored as entered.
- Hebrew text without nikud (vowel points) assumed in MVP.
- Digits are always LTR regardless of surrounding context (Phase 1 simplification).

### 7.9 Punctuation and Bracket Behavior

Phase 1 (simplified):
- All punctuation treated as neutral direction (inserted at cursor, displayed per line direction).
- Brackets: not mirrored. In Hebrew text, an opening parenthesis `(` visually appears as `)` should — this is a known BiDi requirement. **Phase 1 explicitly does NOT implement bracket mirroring.**
- Phase 2: bracket mirroring as a dedicated fix after correct bidi navigation.

### 7.10 Mixed Run Representation

Phase 1: Each line has one direction flag (the dominant direction at line creation).

Phase 2: Each line stores a list of run segments: `{start_col, length, direction}`.
The renderer uses this to place each run correctly.

Example: `"שלום world"` → runs: `[{0, 4, RTL}, {5, 5, LTR}]`

---

## 8. UI/UX Architecture

### 8.1 Screen Layout

```
┌─────────────────────────────────┐  y=0
│  STATUS BAR (320 × 20 px)       │  y=0..19
├─────────────────────────────────┤  y=20
│                                 │
│  EDITOR AREA (320 × 100 px)     │
│                                 │
│  ~5 lines visible at 18px font  │
│                                 │
├─────────────────────────────────┤  y=120
│                                 │
│  VIRTUAL KEYBOARD (320 × 100px) │
│                                 │
└─────────────────────────────────┘  y=219
(bottom 20px = HP system menu bar, not used)
```

Total usable area: 320 × 220 px (HP Prime constraint: rows 0–219).

---

### 8.2 Status Bar (y=0..19, height=20px)

Layout (left to right):
```
[MODE: HE] [Line: 001 Col: 042] [● dirty indicator]
```

- Mode indicator: "HE" (Hebrew), "RU" (Russian), "EN" (ASCII) — colored background for quick recognition (blue=HE, green=RU, white=EN)
- Line/Col: always in logical space
- Dirty indicator: "●" when unsaved changes exist

---

### 8.3 Editor Area (y=20..119, height=100px)

- Line height: 18px (font size 3 = 14pt, with 4px leading)
- Visible lines: floor(100 / 18) = **5 lines**
- Line margin: 2px left, 2px right
- Usable text width: 316 px
- Approximate character width at 14pt: ~9px
- Characters per line visible: ~35

Line rendering rules:
- LTR lines: start rendering from x=2
- RTL lines: render reversed string from right edge inward (x start = 318 - rendered_width)
- Cursor visual: 2px wide vertical bar at computed x position
- Current line: background highlight (light grey: `RGB(220, 220, 220)`)
- Search match: highlight (yellow: `RGB(255, 255, 0)`)

Scrollbar indicator:
- Right edge 4px wide strip: visual position indicator (thumb = visible % of total)
- Not an interactive scroll target (no drag); PgUp/PgDn physical keys or touch arrow buttons instead

---

### 8.4 Virtual Keyboard Area (y=120..219, height=100px)

#### Hebrew Layout (KB_MODE = 0)
```
Row 0 (y=120): [ק][ר][א][ט][ו][ן][ם][פ][×del]
Row 1 (y=145): [ש][ד][ג][כ][ע][י][ח][ל][ך]
Row 2 (y=170): [ז][ס][ב][ה][נ][מ][צ][ת][↵]
Row 3 (y=195): [SPACE 120px][RU][EN][←][→]
```
Key size: 28×22px (10 keys across; some merged).

#### Russian Layout (KB_MODE = 1)
```
Row 0 (y=120): [й][ц][у][к][е][н][г][ш][щ][×]
Row 1 (y=145): [з][х][ъ][ф][ы][в][а][п][р][о]
Row 2 (y=170): [л][д][ж][э][я][ч][с][м][и][↵]
Row 3 (y=195): [SPACE 120px][HE][EN][←][→]
```

#### Symbol/Numeric Layout (KB_MODE = 2)
```
Row 0 (y=120): [1][2][3][4][5][6][7][8][9][0]
Row 1 (y=145): [!][?][.][,][;][:]["]['][()][×]
Row 2 (y=170): [@][#][$][%][&][-][_][=][+][↵]
Row 3 (y=195): [SPACE 120px][HE][RU][←][→]
```

#### Touch Target Requirements
- Minimum target: 26×20px
- Actual key: 28×22px — meets requirement
- Key labels centered horizontally and vertically within key bounds
- Key press feedback: brief color invert (render key as highlighted for 1 frame)

---

### 8.5 Scroll Controls (in Editor Area header/footer)

- ↑ button: top-right of editor area (y=20..35, x=305..319): scroll up one line
- ↓ button: bottom-right of editor area (y=104..119, x=305..319): scroll down one line
- These supplement physical Up/Down arrows

---

### 8.6 Search UI

Triggered by: long press on status bar, or dedicated key combo.

Search popup (modal overlay):
```
┌────────────────────────────┐
│ Search: [________________] │
│ [Find →]  [✕ Cancel]       │
└────────────────────────────┘
```
Rendered at y=40..80 (40px height overlay on editor area).
Input: uses same virtual keyboard; character input goes to search field while modal is active.

---

### 8.7 Mode Indicators and Language Switching

- Tap the "HE"/"RU"/"EN" button in keyboard row 3 to switch keyboard layout
- Current language mode shown in status bar with color background
- When switching from Hebrew to Russian mode: cursor stays; subsequent characters typed are Russian
- No automatic direction detection — user explicitly switches

---

### 8.8 Premium UX Constraints

| Constraint | Implementation |
|---|---|
| No cramped touch targets | All keys ≥ 26×20px; verified in layout |
| Consistent visual feedback | Key press: 1-frame highlight before action |
| No flicker on redraw | Double-buffer (G1 → BLIT_P → G0) mandatory |
| Deterministic behavior | No floating-point timing; event-count triggers for auto-save |
| Readable visual hierarchy | Status bar separated from editor by line; editor separated from keyboard by line |
| Readable cursor | 2px vertical bar; always visible against line highlight |

---

## 9. Risk Register

| ID | Risk | Likelihood | Impact | Detection | Mitigation | Fallback |
|---|---|---|---|---|---|---|
| R-01 | Hebrew glyphs absent from system font | HIGH | CRITICAL | Spike-01 | Use custom GROB glyph rendering | Option B: full custom glyphs |
| R-02 | Cyrillic/Russian glyphs garbled in TEXTOUT | MEDIUM | HIGH | Spike-02 | Test before committing to Option C | Fall back to custom Cyrillic glyphs |
| R-03 | RTL visual order incorrect in mixed text | HIGH | HIGH | Manual test: mixed string display | Simplified model per-line direction flag | Defer mixed-line RTL to Phase 2 |
| R-04 | Cursor/navigation semantic confusion (logical vs visual) | HIGH | MEDIUM | User acceptance test | Document explicitly which model is used | Phase 1: logical-only; Phase 2: visual |
| R-05 | Memory exhaustion (G1 glyph GROBs + document) | LOW | HIGH | Spike-05: load all glyphs + 16K doc | Limit document size; reduce glyph set | Reduce glyph count; chunk loading |
| R-06 | Slow redraw on G1 (32 MB, ~400 MHz) | MEDIUM | MEDIUM | Performance spike on G1 hardware | Partial redraw (dirty lines only) | Limit editor to G2 hardware; document G1 limitation |
| R-07 | Touch UX: accidental key presses from small targets | MEDIUM | MEDIUM | UX test on emulator | Minimum 26×20px enforced; debounce rapid taps | Increase key size; reduce keyboard layout density |
| R-08 | Persistence corruption (EXPORT var partial write on crash) | LOW | HIGH | Stress test: force power-off during edit | Atomic write model: write to temp var, swap on success | Backup variable: HPEDITOR_DOC_BAK |
| R-09 | Emulator vs real device behavior mismatch | MEDIUM | MEDIUM | Real device testing at each phase gate | Test critical paths (touch, rendering) on real device early | Document known differences |
| R-10 | PPL string operations slow at 80-char line length × 200 lines | LOW | MEDIUM | Spike-05: document size stress test | Cap document at 200 lines; lazy re-render | Reduce max document size |
| R-11 | Event loop misses rapid input (queuing gaps in WAIT(-1)) | LOW | LOW | Rapid typing test | Use MOUSE() polling alternative where needed | Acknowledge known gap; acceptable for calculator UX |
| R-12 | Hebrew diacritics (nikud) render incorrectly | HIGH | LOW for MVP | Explicitly out of scope in MVP | Declared out of scope | Not in MVP |
| R-13 | Auto-save EXPORT variable size exceeds PPL limits | LOW | HIGH | Test with max document (16K chars) | 65,535 char limit per string; store as list, not concat | Chunk storage into multiple variables |

---

## 10. Proof-of-Concept / Spike Plan

### Spike-01: Hebrew Glyph Rendering Feasibility

**Purpose:** Determine if HP Prime system font contains and correctly renders Hebrew Unicode glyphs via `TEXTOUT_P`.

**Test program:**

```ppl
EXPORT TestHebrew()
BEGIN
  RECT_P(G0, 0, 0, 320, 220, RGB(255,255,255), RGB(255,255,255));
  // Test: display Hebrew letters directly
  TEXTOUT_P(CHAR(0x05D0), G0, 10, 10, 3, RGB(0,0,0));   // א Alef
  TEXTOUT_P(CHAR(0x05D1), G0, 30, 10, 3, RGB(0,0,0));   // ב Bet
  TEXTOUT_P(CHAR(0x05D2), G0, 50, 10, 3, RGB(0,0,0));   // ג Gimel
  // Test: reversed string (RTL visual simulation)
  TEXTOUT_P(CHAR(0x05D2)+CHAR(0x05D1)+CHAR(0x05D0), G0, 10, 40, 3, RGB(0,0,0));
  // Test: mixed Hebrew + Latin
  TEXTOUT_P("Hello "+CHAR(0x05D0)+CHAR(0x05D1), G0, 10, 70, 3, RGB(0,0,0));
END
```

**Success criteria:**
- All three Hebrew glyphs render as recognizable Hebrew letters (not boxes, question marks, or garbage)
- Characters have consistent height with Latin text
- Mixed string renders with glyphs in specified pixel positions

**Failure criteria:**
- Any glyph renders as □, ?, or garbled pixel pattern
- Glyphs render but at inconsistent heights (combining char baseline issues)

**Decision impact:**
- PASS → Use Option C (Hybrid rendering); skip building Hebrew custom glyph assets
- FAIL → Use Option B (Full Custom Glyphs); build Hebrew bitmap glyph set before implementing editor

---

### Spike-02: Cyrillic/Russian Glyph Rendering Feasibility

**Purpose:** Confirm Cyrillic Unicode renders correctly via `TEXTOUT_P`.

**Test program:**

```ppl
EXPORT TestCyrillic()
BEGIN
  RECT_P(G0, 0, 0, 320, 220, RGB(255,255,255), RGB(255,255,255));
  TEXTOUT_P(CHAR(0x0410), G0, 10, 10, 3, RGB(0,0,0));   // А
  TEXTOUT_P(CHAR(0x0411), G0, 30, 10, 3, RGB(0,0,0));   // Б
  TEXTOUT_P("Привет", G0, 10, 40, 3, RGB(0,0,0));
  TEXTOUT_P("мир", G0, 10, 70, 3, RGB(0,0,0));
END
```

**Success criteria:** All Cyrillic glyphs render correctly and readably.
**Failure criteria:** Garbled, boxes, or partial rendering.
**Decision impact:** PASS → Cyrillic uses TEXTOUT_P (Option C). FAIL → build Cyrillic custom glyph set.

---

### Spike-03: Touch Event Loop Latency

**Purpose:** Measure actual key-to-screen latency for the event loop model.

**Test program:** Render a counter that increments on each tap. User taps repeatedly; observer measures perceived responsiveness.

**Success criteria:** User perceives < 200ms response; no missed taps at normal typing speed (< 3 taps/second).
**Failure criteria:** Consistent lag > 300ms; frequent missed taps.
**Decision impact:** PASS → event loop architecture confirmed. FAIL → switch to MOUSE() polling with tighter loop.

---

### Spike-04: Custom Glyph GROB Rendering

**Purpose:** Validate the custom glyph pipeline: create a GROB bitmap for one Hebrew letter; blit it at correct position; verify visual output.

**Test program:** Manually define a 12×18 pixel GROB for Alef (א) in hex format embedded after `END`. Blit it 5× across a line. Verify pixel-perfect rendering.

**Success criteria:** GROB renders clean glyph; blitting 30+ glyphs per line causes no visible artifacts.
**Failure criteria:** GROB format error; blitting performance visibly slow (> 200ms for one line of 30 glyphs).
**Decision impact:** PASS → custom glyph pipeline is confirmed viable for Option B/C fallback.

---

### Spike-05: Document Size Performance

**Purpose:** Verify that list operations on a 200-line document (80 chars/line = 16K total chars) do not cause unacceptable lag.

**Test program:** Initialize `HPEDITOR_DOC` with 200 strings of 80 random chars. Measure time to:
- Insert 1 character at line 100 (MID + concatenation)
- Search entire document for a substring using POS()
- Serialize to a single string (for backup variable test)

**Success criteria:** Each operation completes in < 50ms.
**Failure criteria:** Any operation > 200ms consistently.
**Decision impact:** PASS → proceed with 200-line document model. FAIL → reduce to 100-line limit; add explicit warning in UX.

---

## 11. Phased Implementation Plan

### Phase 0: Foundation & Validation (Weeks 1–2)

**Objective:** Validate all critical spikes before writing any editor code.

**Tasks:**
- [ ] Create repo structure (see Section 12)
- [ ] Write and run Spike-01 (Hebrew TEXTOUT test)
- [ ] Write and run Spike-02 (Cyrillic TEXTOUT test)
- [ ] Write and run Spike-03 (Touch event loop latency)
- [ ] Write and run Spike-04 (Custom GROB glyph pipeline)
- [ ] Write and run Spike-05 (Document size performance)
- [ ] Document all spike results in `research/spike-results.md`
- [ ] Based on results: confirm rendering architecture (B or C)
- [ ] If Option B required: design all Hebrew glyph bitmaps (22 letters × 12×18px)

**Files to create:**
- `spikes/spike01_hebrew_textout.ppl`
- `spikes/spike02_cyrillic_textout.ppl`
- `spikes/spike03_touch_latency.ppl`
- `spikes/spike04_grob_glyph.ppl`
- `spikes/spike05_doc_perf.ppl`
- `research/spike-results.md`
- `research/platform-facts.md`

**Exit criteria:** All spikes completed; rendering architecture confirmed; no open critical blockers.
**Rollback:** N/A (pure research; no production code at risk)

---

### Phase 1: Core Text Engine (Weeks 3–4)

**Objective:** Working text buffer with insert, delete, cursor movement, persistence.

**Tasks:**
- [ ] Implement `HPEDITOR_DOC` list model
- [ ] `INSERT_CHAR(ch)` function
- [ ] `BACKSPACE()` function
- [ ] `DELETE_FORWARD()` function
- [ ] `NEWLINE()` (split line) function
- [ ] Cursor movement: left, right, up, down, home, end
- [ ] EXPORT variables: `HPEDITOR_DOC`, `HPEDITOR_DIRS`, `HPEDITOR_META`
- [ ] `SAVE_DOCUMENT()` and `LOAD_DOCUMENT()` functions
- [ ] Unit tests (manual): create a document, insert chars, backspace, save, reload

**Files to create:**
- `src/text_engine.ppl` (core buffer operations)
- `src/persistence.ppl` (save/load)
- `tests/test_text_engine.md` (manual test cases)

**Exit criteria:**
- Insert/delete/cursor operations correct for LTR text
- Document survives power cycle (EXPORT variables persist)
- No data corruption on 200-line document

**Rollback:** Text engine is standalone; does not affect rendering or UI code.

---

### Phase 2: Rendering Engine (Weeks 5–6)

**Objective:** Visible text in editor area; double-buffered; correct RTL visual output.

**Tasks:**
- [ ] Implement `RENDER_EDITOR_AREA()`:
  - [ ] For each visible line: render text left-to-right (LTR) or reversed right-to-left (RTL)
  - [ ] Highlight current line
  - [ ] Render cursor bar at correct visual position
- [ ] Implement `RENDER_STATUS_BAR()`:
  - [ ] Mode indicator, line/col, dirty flag
- [ ] Implement `RENDER_KEYBOARD(kb_mode)`:
  - [ ] Draw all key cells with labels
  - [ ] Highlight active layout tab
- [ ] Implement full double-buffer: draw to G1, BLIT to G0
- [ ] Test: display a mixed Hebrew-Russian document (manually loaded); verify visual correctness

**Files to create:**
- `src/renderer.ppl`
- `assets/glyph_hebrew.ppl` (if Option B chosen after Spike-01)
- `assets/glyph_cyrillic.ppl` (if Option B chosen after Spike-02)
- `tests/render_tests.md`

**Exit criteria:**
- Hebrew text visually reverses correctly
- No flicker on redraw
- Cursor appears at correct visual position
- Keyboard renders all keys within bounds

---

### Phase 3: Input & Event Loop (Week 7)

**Objective:** Full interactive loop: keyboard → text engine → renderer.

**Tasks:**
- [ ] Implement main `EXPORT HPEDITOR_MAIN()` event loop
- [ ] Touch hit-testing: map (x, y) → keyboard key OR scroll button OR editor tap
- [ ] Dispatch character insertion from virtual keyboard
- [ ] Dispatch cursor movement from physical keys
- [ ] Implement language mode switching (HE/RU/EN)
- [ ] Implement newline on Enter key
- [ ] Implement backspace on delete key
- [ ] Auto-save trigger (every 300 iterations)
- [ ] Viewport scroll on cursor-out-of-bounds

**Files to create:**
- `src/main.ppl` (event loop)
- `src/input.ppl` (hit-test, dispatch)

**Exit criteria:**
- Can type Hebrew text; see it rendered RTL visually
- Can type Russian text; see it LTR
- Can backspace, navigate, scroll
- Mode indicator updates correctly

---

### Phase 4: Search & Polish (Week 8)

**Objective:** Search feature; UI polish; stability.

**Tasks:**
- [ ] Implement search popup UI
- [ ] Implement `SEARCH_FORWARD(query)` function
- [ ] Highlight search matches in editor area
- [ ] "Next match" navigation
- [ ] Edge case testing: search at end of document, no results
- [ ] Performance review: measure redraw timing on G2 and G1
- [ ] Visual polish: line separators, better cursor contrast, keyboard key borders
- [ ] Final EXPORT variable backup copy (`HPEDITOR_DOC_BAK`)

**Exit criteria:**
- Search finds correct matches in Hebrew and Russian text
- No match notification visible
- All known edge cases handled
- Redraw < 100ms on G2

---

### Phase 5: Real Device Testing & MVP Release (Week 9)

**Objective:** Validate on real HP Prime hardware; deliver MVP.

**Tasks:**
- [ ] Transfer app to real HP Prime G2 via Connectivity Kit
- [ ] Run full test matrix (see Section 13)
- [ ] Compare behavior with emulator; document differences
- [ ] Fix critical device-only bugs
- [ ] Create `runbooks/install-and-use.md`
- [ ] Tag MVP release

**Exit criteria:** All MVP DoD criteria (Section 14) satisfied on real hardware.

---

## 12. Repository Bootstrap Plan

### 12.1 Directory Structure

```
J:\Project_Vibe\HpPrimeEditor\
├── docs/
│   ├── PLAN.md              ← this document
│   ├── ARCHITECTURE.md      ← architecture decision record (ADR)
│   ├── GLYPH-DESIGN.md      ← glyph bitmap specifications
│   └── API-REFERENCE.md     ← PPL function reference for the project
├── research/
│   ├── platform-facts.md    ← confirmed HP Prime capabilities
│   ├── spike-results.md     ← spike test outcomes
│   └── references.md        ← bibliography of sources used
├── src/
│   ├── main.ppl             ← EXPORT HPEDITOR_MAIN(); event loop
│   ├── text_engine.ppl      ← buffer operations
│   ├── renderer.ppl         ← all drawing functions
│   ├── input.ppl            ← touch hit-test, event dispatch
│   ├── search.ppl           ← search subsystem
│   └── persistence.ppl      ← save/load
├── spikes/
│   ├── spike01_hebrew_textout.ppl
│   ├── spike02_cyrillic_textout.ppl
│   ├── spike03_touch_latency.ppl
│   ├── spike04_grob_glyph.ppl
│   └── spike05_doc_perf.ppl
├── assets/
│   ├── glyph_hebrew.ppl     ← Hebrew GROB bitmaps (if custom glyphs required)
│   └── glyph_cyrillic.ppl   ← Cyrillic GROB bitmaps (if custom glyphs required)
├── tests/
│   ├── test_text_engine.md
│   ├── test_render.md
│   ├── test_input.md
│   ├── test_search.md
│   └── test_matrix.md       ← full regression matrix
├── runbooks/
│   ├── install-and-use.md
│   └── development-workflow.md
└── Tasks/
    └── task1.md             ← original task definition
```

### 12.2 Coding Conventions

**Naming:**
- Functions: `UPPER_SNAKE_CASE` (PPL convention)
- Variables: `UPPER_SNAKE_CASE` for globals; `lower_snake_case` for locals
- Constants: prefix with `K_` (e.g., `K_EDITOR_TOP := 20`)
- GROB functions: suffix `_GFX` (e.g., `RENDER_LINE_GFX`)

**Module structure:**
- Each `.ppl` file begins with a comment block:
  ```
  // MODULE: text_engine.ppl
  // DEPENDS: (none)
  // EXPORTS: INSERT_CHAR, BACKSPACE, DELETE_FORWARD, NEWLINE, ...
  ```
- All RTL-specific logic blocks annotated with `// RTL:` comment prefix

**Style:**
- Max function length: 50 lines
- Prefer named constants over magic numbers
- All layout constants defined at the top of `renderer.ppl`

### 12.3 Required Initial Documents

Before Phase 1 begins:
- `docs/PLAN.md` (this file) ✓
- `research/platform-facts.md` (post-spike outcomes)
- `research/spike-results.md` (spike results)
- `docs/ARCHITECTURE.md` (selected architecture decision, with rationale)
- `docs/GLYPH-DESIGN.md` (if Option B/C chosen, define all glyph pixel layouts)

---

## 13. Test Strategy

### 13.1 Manual Tests (Emulator)

All tests run on HP Prime Virtual Calculator (Windows) with mouse as touch input.

| Test ID | Description | Steps | Expected |
|---|---|---|---|
| T-01 | Basic Latin insertion | Type ASCII letters via virtual keyboard Symbol layout | Characters appear in editor area |
| T-02 | Russian insertion | Switch to RU mode; type "привет" | "привет" appears LTR |
| T-03 | Hebrew insertion | Switch to HE mode; type Alef+Bet+Gimel | "אבג" appears; visual order right-to-left |
| T-04 | Backspace | Insert 5 chars; backspace 2 | 3 chars remain; cursor correct |
| T-05 | Cursor left/right | Insert 5 chars; arrow left 3; right 1 | Cursor at position 3 |
| T-06 | Home/End | In 10-char line; press End; cursor at 10; press Home; cursor at 0 | Correct |
| T-07 | New line | Place cursor mid-line; press Enter | Line splits at cursor |
| T-08 | Line merge (backspace at start) | Cursor at start of line 2; backspace | Line 2 merges into line 1 |
| T-09 | Mode switch | Type Hebrew; switch to RU; type Russian | Hebrew preserved; Russian appended |
| T-10 | Viewport scroll | Insert 10 lines; cursor at line 10 | Viewport scrolls to show cursor line |
| T-11 | Persistence | Type text; close and reopen app | Text restored |
| T-12 | Search (Russian) | Insert "Привет мир"; search "мир" | Match highlighted at correct position |
| T-13 | Search (Hebrew) | Insert "שלום"; search "לו" | Match highlighted |
| T-14 | Search no match | Search "xyz" in Hebrew text | "Not found" notification shown |
| T-15 | Document full | Insert 200 lines; attempt insert on line 200 | Error notification; no crash |
| T-16 | RTL visual order | Insert Hebrew "שלום"; verify visual order is right-to-left | ם-ו-ל-ש displayed left-to-right on screen (reversed visually) |

---

### 13.2 Mixed-Text Edge Case Matrix

| Test String | Expected Rendering |
|---|---|
| `"Hello"` | Pure LTR; left-aligned |
| `"Привет"` | Pure LTR (Cyrillic); left-aligned |
| `"שלום"` | Pure RTL; right-aligned (reversed visual) |
| `"Hello שלום"` | Phase 1: LTR line; Hebrew glyphs visible but not re-ordered correctly until Phase 2 |
| `"שלום World"` | Phase 1: RTL line; whole line reversed including "World" — known limitation |
| `"(שלום)"` | Brackets not mirrored in Phase 1 — known limitation |
| `"123 שלום"` | Digits treated as LTR neutral in Phase 1 |
| `"שלום\nПривет"` | Two-line document; line 1 RTL, line 2 LTR |
| `"אבגד" × 80` | Maximum line length; no overflow crash |
| `"" × 200` | Maximum line count; no crash |

---

### 13.3 Performance Checks

| Check | Target | Method |
|---|---|---|
| Full screen redraw time | < 100ms (G2) | Timestamp WAIT(-1) before/after BLIT_P |
| Insert char response | < 200ms | Visual observation; tap + count frames |
| Search 200 lines | < 500ms | Insert 200 lines; run search; measure by observation |
| App startup (load from EXPORT) | < 2 seconds | Cold start on device |
| Memory usage (200 lines + all glyphs) | Fits in available RAM | No OOM error during extended use |

---

### 13.4 Rendering Verification Cases

- Hebrew glyphs render as correct letter forms (visual comparison with printed reference)
- Glyph baseline consistent across Hebrew and Cyrillic characters on same line
- Cursor bar visible against all background colors
- Current-line highlight does not obscure text
- Keyboard keys legible at all font sizes
- Key labels centered correctly

---

### 13.5 Emulator vs Device Testing Plan

| Test Type | Emulator | Real Device |
|---|---|---|
| Logic correctness (insert, delete, search) | YES | YES (Phase 5) |
| Touch hit-testing | YES (mouse) | YES (Phase 5) |
| Hebrew glyph rendering | YES (primary) | YES (confirm match) |
| Redraw performance | Measure (not accurate) | Measure (authoritative) |
| EXPORT variable persistence | YES | YES (authoritative) |
| Multitouch (future gestures) | UNCONFIRMED | YES |
| Firmware-specific rendering | NO (may differ) | YES |

---

## 14. Definition of Done

### MVP (Phase 3 complete)

- [ ] Can insert Hebrew text via virtual keyboard; visually rendered right-to-left
- [ ] Can insert Russian text via virtual keyboard; visually rendered left-to-right
- [ ] Can insert digits and common punctuation
- [ ] Cursor navigation works (left, right, up, down, home, end)
- [ ] Backspace and delete work correctly
- [ ] Enter key creates new line
- [ ] Viewport scrolls for documents > 5 lines
- [ ] Language mode indicator in status bar is accurate
- [ ] Document persists across app restart (EXPORT variables)
- [ ] No crash on 200-line document
- [ ] Tested and passing on HP Prime Virtual Calculator (emulator)

---

### Beta (Phase 4 complete)

- [ ] All MVP criteria met
- [ ] Search feature working: finds matches in Hebrew and Russian text
- [ ] "No match" notification shown when search fails
- [ ] Auto-save every 5 seconds (or on exit)
- [ ] Backup EXPORT variable prevents data loss
- [ ] Redraw time < 100ms on G2 (measured)
- [ ] All T-01 through T-16 test cases passing
- [ ] No known crash paths

---

### Premium-Ready Release Candidate (Phase 5 complete)

- [ ] All Beta criteria met
- [ ] Tested on real HP Prime G2 hardware
- [ ] All emulator/device behavior differences documented
- [ ] `runbooks/install-and-use.md` complete
- [ ] Visual quality review: glyph readability, cursor visibility, keyboard usability
- [ ] Stress test: 200-line document; 30 minutes continuous editing; no crash or data loss
- [ ] Known limitations explicitly documented in `runbooks/`
- [ ] Code reviewed for correctness of RTL logic (peer or self-review with fresh eyes)

---

## 15. Blind Spots / Ambiguities / Shallowly-Specified Areas

### BS-01: Hebrew Font Coverage

**What is underspecified:** Whether `TEXTOUT_P` can render any Hebrew glyph at all on current firmware.

**Why dangerous:** This is the primary technical unknown. The entire Option A/C rendering path collapses to Option B if the font lacks Hebrew. Building the editor without confirming this first wastes weeks of work.

**Evidence missing:** No community test report found. No HP documentation on which Unicode blocks the system font covers.

**Resolution:** Spike-01 resolves this definitively. Must be the first thing executed.

**Spike required:** YES (Spike-01).

**Fallback:** Full custom GROB glyph pipeline (Option B). This fallback is fully specified and buildable.

---

### BS-02: Mixed-Direction Line Display Semantics

**What is underspecified:** The plan says "Phase 1: whole-line direction flag." But what happens when a user types Hebrew and then switches to Russian mid-line? The line direction flag would be set at line creation time, but the actual content is mixed.

**Why dangerous:** The visual output could be confusing or wrong — e.g., Russian words appearing reversed on a Hebrew-flagged line.

**Evidence missing:** No decided behavior for mid-line direction switches.

**Resolution:** Two options:
  1. Prevent mode-switching mid-line (force Enter before switching language direction)
  2. Allow mixed lines but document visual inaccuracy as a Phase 1 known limitation

**Recommendation:** Option 1 is safer for Phase 1. Enforce: "Direction can only switch at start of a new line." This eliminates the mixed-line ambiguity entirely.

**Spike required:** NO — pure design decision.

---

### BS-03: Cursor Visual Position in RTL Lines

**What is underspecified:** The cursor is at logical column `C` in a reversed (RTL) line. What is the correct pixel X position for the cursor bar?

**Why dangerous:** A wrong formula here makes cursor placement confusing or incorrect.

**Resolution:**

For RTL line with logical content `s` (length `N`):
- Visual string = `REVERSE(s)`
- Cursor at logical col `C` corresponds to visual position `N - C` from the right
- Pixel X = `(editor_right - (N - C) * char_width)`

This formula must be implemented correctly and explicitly tested.

**Spike required:** YES (covered in Spike-04 / Rendering spike).

---

### BS-04: Physical Keyboard Key Mapping for Hebrew

**What is underspecified:** When the virtual keyboard is in Hebrew mode, do physical HP Prime keyboard keys (A–Z) insert Hebrew letters, or do they still insert Latin?

**Why dangerous:** If physical keys always insert Latin, users of the physical keyboard in Hebrew mode get wrong characters. But mapping physical keys to Hebrew requires defining a specific layout.

**Resolution:** Phase 1: physical keys always insert their ASCII character regardless of mode. Virtual keyboard is the primary Hebrew input method. Physical keys are used only for navigation (arrows, Enter, ESC).

**Documented limitation:** Physical keyboard does not support Hebrew input in MVP.

---

### BS-05: TEXTOUT Character Width Measurement

**What is underspecified:** When computing cursor pixel X position, we need to know the pixel width of each character at the selected font size. HP PPL has no confirmed "measure text width" function.

**Why dangerous:** Without knowing glyph widths, cursor positioning will be wrong (especially for variable-width characters).

**Evidence missing:** No `TEXTSIZE()` or equivalent function found in documented PPL API.

**Resolution:**
- Option A: Use a fixed character width assumption. At font size 3 (14pt), assume ~9 px per character (monospace approximation). This is inaccurate for proportional rendering.
- Option B: Custom glyph rendering inherently has fixed width (bitmap glyphs are fixed-width by design).

**Recommendation:** Design all custom glyphs as fixed-width (monospace). For TEXTOUT_P path: measure empirically during Spike-01.

**Spike required:** YES (measure in Spike-01 and Spike-02).

---

### BS-06: GROB Glyph Asset Creation Workflow

**What is underspecified:** How will Hebrew glyph bitmaps be created and embedded in PPL source?

**Why dangerous:** If the asset pipeline is impractical, Option B becomes undeliverable.

**Resolution:**
1. Design glyphs as 12×18 pixel bitmaps in a spreadsheet or pixel editor
2. Convert to HP Prime ICON format (hex-encoded pixel data in PPL comments after `END`)
3. At runtime: `DIMGROB_P(G7, 12, 18, 0)` then write pixel data via `SETPIX_P` loop
4. Alternatively: encode all glyphs as a single GROB strip (22 Hebrew × 12 = 264 wide, 18 tall) and blit subregions

The single-strip approach is strongly preferred — one GROB asset load, subregion BLIT_P for each character.

**Evidence:** BLIT_P with source subregion coordinates is confirmed in PPL API.

**Spike required:** YES (Spike-04 validates this pipeline).

---

### BS-07: App Note vs EXPORT Variable for Document Storage

**What is underspecified:** The plan uses EXPORT variables as primary storage. The App Note (`.hpappnote`) is mentioned as a future option for readability. The relationship between these is unclear.

**Why dangerous:** If EXPORT variables have size limits that affect large documents, data loss risk.

**Resolution:**
- EXPORT variable holds the document as a list of strings (no size limit beyond RAM and the 65,535-char-per-string limit)
- A 200-line × 80-char document = 16,000 chars total, well within limits even as a single string
- App Note is considered for Phase 2 as a secondary "export" format — not primary storage

**No spike required.** Document this explicitly in `docs/ARCHITECTURE.md`.

---

## 16. Open Questions

| ID | Question | Blocking Level | Next Action |
|---|---|---|---|
| OQ-01 | Do Hebrew glyphs render in TEXTOUT_P? | **CRITICAL BLOCKER** | Run Spike-01 immediately |
| OQ-02 | Do Cyrillic glyphs render correctly (not garbled)? | HIGH | Run Spike-02 immediately |
| OQ-03 | What is the exact character width of HP Prime font at each size? | HIGH | Measure empirically in Spike-01 |
| OQ-04 | Is the HP Prime Virtual Calculator available and free for development? | MEDIUM | Confirmed (v2.4.15515, free); download now |
| OQ-05 | Can a `.hpprgm` file with embedded ICON GROB data be large enough for all glyph assets? | MEDIUM | Test with Spike-04 |
| OQ-06 | Does WAIT(-1) handle rapid repeated taps reliably, or does it miss events? | MEDIUM | Test in Spike-03 |
| OQ-07 | What is the actual recursion depth limit in HP PPL? | LOW | Not critical for Phase 1; test if needed for parser |
| OQ-08 | Does the HP Prime G1 (32MB RAM) have acceptable performance for this editor? | LOW | Test in Phase 5 if G1 device available |
| OQ-09 | Can MicroPython be used for preprocessing (e.g., glyph bitmap generation) offline? | LOW | Research MicroPython stability if needed |
| OQ-10 | How does the HP Connectivity Kit handle very large `.hpprgm` files (with embedded GROBs)? | LOW | Test during Phase 0 asset development |

---

## 17. Final Recommendation

### Is the Premium Vision Realistically Achievable on HP Prime?

**Partially yes — with explicit scope discipline.**

The premium vision as originally stated (full-featured Hebrew-Russian editor, high-quality RTL rendering, mixed-direction text handling) is achievable in a carefully scoped form. The following elements are realistically deliverable:

**Safely committable:**
- Hebrew character input via custom virtual keyboard
- Russian/Cyrillic character input
- Single-line direction model (RTL or LTR per line)
- Visual right-to-left display of Hebrew text
- Insert, delete, cursor navigation, viewport scrolling
- Substring search
- Document persistence
- Touch-driven virtual keyboard
- Premium-grade UI quality (double-buffered, no flicker, clear visual hierarchy)

**Deferred, not committed:**
- Full UAX#9 BiDi (mixed-direction within a single line)
- Hebrew diacritics/nikud
- Bracket mirroring
- Selection, copy/paste
- Multi-document
- Line wrapping

### The Critical Path

The entire project gates on **Spike-01** (Hebrew glyph rendering). This must be run in the first week of work. It determines whether the rendering engine is a 1-week or 3-week effort.

- If Spike-01 PASSES: rendering architecture is confirmed as Option C (Hybrid). Phase 2 is 1-2 weeks.
- If Spike-01 FAILS: fallback to Option B (Custom Glyphs). Glyph asset creation adds 1-2 weeks before Phase 2. This is manageable but must be planned for.

### Best Execution Path

1. **Week 1:** Run all 5 spikes. Confirm platform facts. Set up repo.
2. **Week 2:** Confirm rendering architecture based on spike results. Begin glyph assets if needed.
3. **Weeks 3–4:** Text engine (core buffer; pure logic; no UI).
4. **Weeks 5–6:** Rendering engine (visual output; RTL display).
5. **Week 7:** Event loop and interactive input.
6. **Week 8:** Search; polish; performance.
7. **Week 9:** Real device testing; MVP release.

### Honest Assessment of Platform Constraints

HP Prime is a capable platform for a text editor — its memory (G2: 128MB usable), speed (528 MHz ARM), and touch input are more than sufficient. The hard constraints are:

1. **No OS-level RTL/BiDi support** — everything must be implemented manually.
2. **Unknown Hebrew font coverage** — the highest uncertainty in the project.
3. **Limited persistence model** — EXPORT variables are workable but not a full file system.
4. **LTR-only TEXTOUT** — solvable by string reversal, but cursor math requires careful implementation.

None of these are blockers for a premium-quality product. They are engineering challenges that require careful, evidence-driven implementation — which is exactly what this plan provides.

**The product is achievable. Begin with Spike-01.**

---

*End of Planning Document. Version 1.0, 2026-03-10.*
