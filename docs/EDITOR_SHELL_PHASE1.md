# EDITOR_SHELL_PHASE1.md
## HP Prime Hebrew-Russian Editor — Editor Shell MVP

**Phase:** Task 6
**Status:** MVP complete
**Date:** 2026-03-10

---

## 1. Scope

### In scope
- `src/editor_shell.ppl` — shell module with event loop and virtual keyboard
- `editor_shell()` — entry point for fresh empty document
- `editor_shell_from(lines_list)` — entry point with pre-loaded document
- Virtual keyboard panel: Hebrew layout + Ctrl/digits layout
- Touch-driven input (virtual keyboard tap targets)
- Hardware ESC key to exit shell
- Cursor movement: left, right, up, down
- Editing: insert character, backspace, newline
- Layout switching: Hebrew ↔ Ctrl/digits
- Keyboard panel show/hide toggle
- Viewport management: cursor always stays in visible region
- Dirty-flag redraw discipline
- Test harness `tests/test_editor_shell_basic.ppl`
- This documentation

### Out of scope (deferred)
- Delete-forward key
- Home / End (line start / line end) via keyboard panel
- Russian / Cyrillic layout
- Copy, paste, selection
- File open / save UI
- Search and replace
- Full mixed-run bidi
- Hardware key mapping beyond ESC
- Advanced menus

---

## 2. Dependencies

| Module | Used symbols |
|--------|-------------|
| `text_engine` | `TE_Init()`, `TE_InitFrom()`, `TE_InsertChar()`, `TE_Backspace()`, `TE_Newline()`, `TE_MoveLeft/Right/Up/Down()` |
| `renderer` | `REND_Init()`, `REND_DrawDoc()`, `R_VIEW_TOP`, `R_LINES_VIS`, `R_Y_TOP` |
| `hebrew_font_bitmap` | loaded via `REND_Init()`; `HFB_CodeToIdx()`, `HFB_BlitGlyph()` used by keyboard drawing |

Load order on HP Prime: `hebrew_font_bitmap` → `text_engine` → `renderer` → `editor_shell`

---

## 3. State Model

| Global | Type | Default | Meaning |
|--------|------|---------|---------|
| `ES_CL` | int | 1 | Cursor line (1-based) |
| `ES_CC` | int | 1 | Cursor column (1-based) |
| `ES_DIRTY` | int | 0 | 1 = screen needs redraw |
| `ES_KBD_VIS` | int | 1 | 1 = keyboard panel visible |
| `ES_KBD_LAY` | int | 0 | 0 = Hebrew, 1 = Ctrl layout |
| `ES_RUNNING` | int | 0 | 1 = event loop active |
| `ES_KB_HEB` | list(27) | — | Hebrew codepoints in key order |
| `ES_KB_CTL` | list(27) | — | Ctrl-layout codepoints in key order |

The renderer globals `R_VIEW_TOP`, `R_LINES_VIS`, `R_Y_TOP` are shared state managed by the shell via `ES__ConfigRenderer()` and `ES__AdjustViewport()`.

`ES__InitState()` resets all shell globals. It does NOT touch the document (`L0`) — that is managed by `TE_Init()` / `TE_InitFrom()` before calling `ES__Run()`.

---

## 4. Input Model

### Touch events
HP Prime touch events are detected via `WAIT(-1)` returning a list:
- `ev(1)` = event type: 0=Down, 2=Up, 3=Click
- `ev(2)` = x coordinate (for type 0 and 3)
- `ev(3)` = y coordinate (for type 0 and 3)

The shell handles **Down events only** (type 0). Up and Click events are ignored. This gives immediate response on finger contact without waiting for lift.

The shell uses `IFERR ev(1) THEN ...` to distinguish touch lists from hardware key integers.

### Hardware keys
`WAIT(-1)` returns an integer for hardware key presses. Key code 4 (ESC/Back) exits the shell. All other hardware key codes are ignored in this phase.

### Launch bleed-through mitigation
After the initial screen draw, one `WAIT(-1)` is called and discarded before the main loop begins. This drains any residual event from the keypress used to launch the program.

### Touch target geometry
All keyboard rows use 35px-wide keys starting at x=2. Control row and letter rows share the same column grid. Hit testing uses `IP((tx-2)/35)+1` for column (1-based, clamped 1..9) and `IP((ty-139)/32)+1` for letter row (1-based, clamped 1..3).

---

## 5. Keyboard Model

### Screen region
Keyboard panel: y=107..234 (4 rows × 32px each)
- Control row: y=107..138
- Letter row 1: y=139..170
- Letter row 2: y=171..202
- Letter row 3: y=203..234

### Control row (always same regardless of layout)
9 keys at 35px each, light-blue background:

| Col | Label | Action |
|-----|-------|--------|
| 1 | SP | Insert space (codepoint 32) |
| 2 | BS | Backspace |
| 3 | ENT | Enter / newline |
| 4 | < | Move cursor left |
| 5 | > | Move cursor right |
| 6 | ^ | Move cursor up |
| 7 | v | Move cursor down |
| 8 | LAY | Switch layout (HEB ↔ CTL) |
| 9 | KBD | Toggle keyboard visibility |

### Hebrew layout (ES_KBD_LAY = 0)
Light-purple background. Each key shows a 14×20 Hebrew bitmap glyph centered in the key.

| Row | Keys (left to right) |
|-----|---------------------|
| 1 | alef(1488) bet(1489) gimel(1490) dalet(1491) he(1492) vav(1493) zayin(1494) het(1495) tet(1496) |
| 2 | yod(1497) kaf-sofit(1498) kaf(1499) lamed(1500) mem-sofit(1501) mem(1502) nun-sofit(1503) nun(1504) samekh(1505) |
| 3 | ayin(1506) pe-sofit(1507) pe(1508) tsadi-sofit(1509) tsadi(1510) qof(1511) resh(1512) shin(1513) tav(1514) |

Final forms (sofit variants) are included in row 2 and row 3 alongside their base forms. Tapping any key inserts that codepoint at the current cursor position.

### Ctrl layout (ES_KBD_LAY = 1)
Light-green background. Keys show ASCII characters via `TEXTOUT_P`.

| Row | Keys |
|-----|------|
| 1 | 1 2 3 4 5 6 7 8 9 |
| 2 | 0 . , ! ? ( ) : ; |
| 3 | - / _ @ * + = < > |

### Layout switching
Tapping LAY (col 8) toggles `ES_KBD_LAY` between 0 and 1. The header indicator updates: `[HEB]` (green) or `[CTL]` (cyan). The keyboard letter rows are redrawn on the next dirty redraw.

---

## 6. Redraw Contract

**Rule:** `ES_DIRTY := 1` is set by any action that changes document or shell state.

**Cycle:**
1. `ES__DoAction()` sets `ES_DIRTY := 1` if state changed
2. At end of each loop iteration: if `ES_DIRTY`, call `ES__AdjustViewport()` then `ES__DrawAll()`, then clear `ES_DIRTY`
3. If no action occurred (touch miss, ignored key), `ES_DIRTY` stays 0 and no redraw happens

**`ES__DrawAll()` steps:**
1. `ES__ConfigRenderer()` — update `R_LINES_VIS`
2. `RECT_P(0,0,319,239,white,white)` — clear full screen
3. `ES__DrawHeader()` — header bar with layout indicator
4. `REND_DrawDoc(ES_CL, ES_CC)` — editor viewport with cursor
5. If `ES_KBD_VIS`: `ES__DrawKbdCtrlRow()` + `ES__DrawKbdLetterRows()`

The full-screen clear at step 2 ensures no stale pixels from previous states (e.g., keyboard area when keyboard is hidden). This is safe for MVP; performance optimization can defer partial redraws to later phases.

---

## 7. Viewport Behavior

`R_VIEW_TOP` controls which document line appears at the top of the editor area. It is managed entirely by the shell.

**`ES__AdjustViewport()` algorithm:**
```
if ES_CL < R_VIEW_TOP:
    R_VIEW_TOP = ES_CL
if ES_CL >= R_VIEW_TOP + R_LINES_VIS:
    R_VIEW_TOP = ES_CL - R_LINES_VIS + 1
clamp R_VIEW_TOP >= 1
```

This is called before each redraw when `ES_DIRTY` is set. It guarantees the cursor line is always visible.

**Keyboard visibility and line count:**
- Keyboard visible: `R_LINES_VIS = 4` — editor shows 4 lines
- Keyboard hidden: `R_LINES_VIS = 9` — editor shows 9 lines

Toggling keyboard visibility triggers a dirty redraw which reconfigures `R_LINES_VIS` before rendering.

---

## 8. Known Limitations

### 1. No Delete-forward key
Only Backspace is implemented. Delete-forward (`TE_Delete`) is not accessible from the keyboard panel in this phase.

### 2. No Home/End keys in keyboard panel
Line-start and line-end movement are not in the control row. The control row has 9 keys; adding Home/End would require removing other keys or shrinking them below usable size. Deferred.

### 3. Keyboard always starts visible
When `editor_shell()` starts, the keyboard is always visible (4-line editor view). There is no remembered preference. Deferred to settings/persistence phase.

### 4. When keyboard is hidden, KBD toggle is inaccessible
The KBD button only appears in the keyboard panel. When hidden, the only way to re-show the keyboard is to restart the shell. Mitigation: document this clearly. Future fix: reserve a persistent status bar with a KBD toggle button outside the keyboard panel.

### 5. Hardware key codes unverified
Key code 4 is used for ESC/Back based on typical HP Prime behavior, but this has not been confirmed via spike testing in this project. If ESC does not work, the shell requires a hardware HOME button or program restart to exit.

### 6. Mixed-content rendering limitation
Inherited from renderer MVP: lines with Hebrew + non-Hebrew chars render fully RTL with gray placeholder boxes for non-Hebrew. See RENDERER_PHASE1.md.

### 7. Keyboard redraw on every keystroke
`ES__DrawAll()` redraws the entire keyboard panel on every state change. For rapid typing this may cause visible flicker. Optimization (partial keyboard redraw only on layout change) is deferred.

### 8. IFERR touch detection
The `IFERR ev(1) THEN` pattern is used to distinguish touch lists from hardware key integers. This relies on `ev(1)` throwing an error for integers. Confirmed behavior from project Spike03.

---

## 9. Future Phases

| Feature | Phase |
|---------|-------|
| Hardware arrow key support | Phase 2 |
| Home / End keys | Phase 2 |
| Russian / Cyrillic layout | Phase 3 |
| Delete-forward key | Phase 2 |
| Persistent KBD toggle button | Phase 2 |
| Partial redraw (kbd only on layout change) | Phase 2 optimization |
| File open / save dialog | Phase 4 |
| Copy / paste / selection | Phase 4 |
| Search and replace | Phase 5 |
| Full Unicode bidi | Phase 6 |

---

## 10. Module Load Order

```
1. hebrew_font_bitmap  (HFB_DAT, HFB_BlitGlyph, etc.)
2. text_engine         (L0, TE_Init, TE_InsertChar, etc.)
3. renderer            (REND_Init, REND_DrawDoc, R_* globals)
4. editor_shell        (ES_* globals, editor_shell, editor_shell_from)
```

**To run:**
- `test_editor_shell_basic()` — blank document
- `editor_shell_demo()` — pre-loaded 6-line Hebrew/English document

**To exit:** Press hardware ESC/Back key.
