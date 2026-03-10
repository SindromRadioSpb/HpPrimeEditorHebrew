# EDITOR_UX_PHASE2_PLAN.md
## HP Prime Hebrew-Russian Editor — Editor UX Phase 2 Planning Document

**Date:** 2026-03-10
**Status:** Planning anchor — authoritative Phase 2 reference
**Follows:** Tasks 1–6 (text engine, font, renderer, editor shell MVP)

---

## 1. Repo Audit Findings

### Confirmed existing modules

| Module | File | Lines | Status |
|--------|------|-------|--------|
| Text engine | `src/text_engine.ppl` | 355 | Complete, all tests passing |
| Hebrew bitmap font | `assets/hebrew_font_bitmap.ppl` | 155 | Complete v2, 27 glyphs |
| Renderer | `src/renderer.ppl` | 339 | MVP — documented limitations |
| Editor shell | `src/editor_shell.ppl` | 438 | MVP — several gaps |

### Text engine — what exists vs what is wired to the shell

| Function | Exists in TE | Wired to keyboard |
|----------|-------------|-------------------|
| `TE_InsertChar` | YES | YES |
| `TE_Backspace` | YES | YES |
| `TE_Delete` | YES | **NO** — not in shell |
| `TE_Newline` | YES | YES |
| `TE_MoveLeft/Right` | YES | YES |
| `TE_MoveUp/Down` | YES | YES |
| `TE_MoveLineStart` | YES | **NO** — not in shell |
| `TE_MoveLineEnd` | YES | **NO** — not in shell |
| `TE_InsertText` | YES | Not needed yet |
| Search (find/match) | **NO** | — |
| Clear document | **NO** | — |
| Preferred column | **NO** | — |
| Save / load | **NO** | — |

### Renderer — what exists vs what is needed

| Feature | Status |
|---------|--------|
| Hebrew RTL rendering | Working |
| LTR text rendering | Working (uniform 7px advance) |
| Cursor rendering | Working |
| Viewport scrolling | Working (manual via R_VIEW_TOP) |
| `REND_DrawStatus` | Exists — used only in test harness, NOT in live shell |
| Status strip y=214..239 | Reserved in comments, not implemented |
| Mixed-content (Hebrew+digits) in RTL | Placeholder gray boxes — ugly |
| Search match highlight | Not implemented |
| Proportional LTR spacing | Not implemented (all chars = 7px) |

### Editor shell — current gaps

| Gap | Impact |
|-----|--------|
| No DEL key on keyboard | Can only delete backwards |
| No HOME/END on keyboard | No line-start/line-end access |
| No cursor position in header | User cannot see L:x C:y |
| KBD not re-showable when hidden | Dead end — requires restart |
| No preferred column for ↑↓ | Cursor jumps to col 1 on short lines |
| No hardware arrow keys | All navigation via touch only |
| No search | Cannot find text |
| No clear/new document | Cannot start fresh without restart |
| No status bar | No document state feedback |
| Full screen redraw each keystroke | Performance: keyboard redrawn needlessly |
| Only ESC handled as hardware key | All other hardware buttons dead |
| No Russian layout | Latin/Cyrillic via CTL digits only |

### No search, Russian, or save/load code exists anywhere in the repo.

---

## 2. Current UX Limitations

### 2.1 Keyboard is too sparse for real editing
The current control row has: SP BS ENT ← → ↑ ↓ LAY KBD.
Missing: DEL (forward delete), HOME (line start), END (line end).
These are all already implemented in `text_engine.ppl` — they just aren't wired.

### 2.2 Keyboard hide/show is broken as a workflow
When the user taps KBD to hide the keyboard, there is no way to re-show it.
The KBD button disappears with the keyboard. This is a usability dead end.

### 2.3 No feedback on cursor position
The header shows `[HEB]` or `[CTL]` but nothing about where the cursor is.
In a multi-line document, users cannot tell which line they are on.

### 2.4 Non-Hebrew characters in RTL lines look wrong
Digits and punctuation in Hebrew lines render as gray placeholder boxes.
This makes "שלום 2024" unreadable. This is the most visually damaging limitation
for practical use of the editor.

### 2.5 No search
Finding a word requires scrolling manually. Even in a short document this is
frustrating. Search is the single feature most associated with "usable editor".

### 2.6 No vertical navigation preference column
When the cursor is at col 8 on a long line, pressing ↑ to a short line (len 3)
drops the cursor to col 4 (TE_MoveUp clamps to slen+1). When ↓ returns to
the long line, the cursor is now at col 4, not col 8. The original column
is lost. This is a known omission in `TE_MoveUp/Down`.

### 2.7 Performance: full redraw on every keystroke
`ES__DrawAll()` redraws the entire keyboard (27 Hebrew glyphs via HFB_BlitGlyph)
on every key tap, even when only the editor content changed. This causes visible
flicker and slows response. The keyboard only needs redraw on layout switch.

### 2.8 No document-level commands
No way to clear the document, jump to a specific line, or know document length
from within the editor.

---

## 3. Phase 2 Goals

Phase 2 transforms the editor from:

> "An interactive technical MVP that can insert Hebrew text"

into:

> "A practically usable Hebrew text editor with real navigation, search, and legible mixed content"

Specific goals:

1. **Every key the text engine supports is accessible from the keyboard panel.**
2. **The user always knows where they are** (cursor position in header).
3. **The keyboard panel is always accessible** (persistent toggle, not a dead end).
4. **Hebrew + digits/punctuation can coexist visually** in the same line.
5. **The user can find text** via a simple search mode.
6. **Vertical navigation preserves the preferred column.**
7. **Keyboard redraws only when necessary** (layout or visibility change).
8. **Basic document commands exist** (new document, jump to start/end).

---

## 4. Candidate Workstreams

### Workstream A — Keyboard UX Upgrade

**What:**
- Add DEL, HOME, END to control row
- Redesign control row for the expanded key set
- Fix keyboard hide/show: add persistent KBD toggle button in header bar
- Add cursor position display (L:x C:y) in header
- Wire `TE_Delete`, `TE_MoveLineStart`, `TE_MoveLineEnd` to new action codes
- Add action codes -11 (delete), -12 (home), -13 (end)
- Hardware arrow key support (requires HP Prime key code verification)

**Files affected:** `src/editor_shell.ppl` only

**Complexity:** Low — mostly additive changes to existing shell
**Risk:** Low — no renderer or text engine changes needed
**Value:** High — fixes the most immediately annoying gaps

**Design note on control row:**
Current 9 keys at 35px = 315px. Adding DEL, HOME, END = 12 keys.
Options:
- 12 keys × 26px = 312px — still fits, slightly smaller tap targets
- Split into two rows: navigation row + editing row
- Preferred: keep 1 row, 12 keys × 26px, accept smaller targets for controls
  (control area is expected to have smaller keys than letter rows)

**Design note on persistent KBD toggle:**
Add a small `[K]` button in the header bar (e.g. at x=285..319, y=0..15).
This button is always visible regardless of keyboard state.
Tap it → toggle KBD_VIS. This replaces the KBD key in the control row.
This frees one slot in the control row for DEL or HOME/END.

---

### Workstream B — Mixed-Text Rendering Improvement

**What:**
- Render digits and punctuation in RTL lines using `TEXTOUT_P` at the correct
  x position instead of gray placeholder boxes
- Correct vertical alignment between TEXTOUT_P chars and HFB glyphs
- This makes "שלום 2024" display correctly instead of showing gray boxes

**Files affected:** `src/renderer.ppl` — `REND_DrawLine` RTL path

**Current behavior:**
In RTL mode, any non-Hebrew char → `REND__PlaceholderBox(bx, scr_y, 14, 20)`

**Target behavior:**
In RTL mode, non-Hebrew char → `TEXTOUT_P(ch, bx+1, scr_y+6, 1, R_COL_FG)`
using the same `bx` position as the glyph would have occupied.
This preserves RTL layout geometry while showing real characters.

**Cursor model impact:** None — cursor formula is based on slot position,
not glyph type. Mixed content keeps the same advance (R_ADV_HEB per slot).

**Complexity:** Low-medium — localized change to REND_DrawLine
**Risk:** Medium — visual alignment of TEXTOUT_P vs HFB glyphs needs tuning
**Value:** High for practical use — makes the editor usable for Hebrew text
  with numbers, dates, punctuation

**Deferral candidate:** Russian in RTL lines deferred until Russian font ready.

---

### Workstream C — Search MVP

**What:**
- Search mode: user enters a query string, editor finds matches in document
- `TE_FindNext(query, from_cl, from_cc)` — new text engine function using INSTRING
- Search UI: query bar appears at bottom of editor area (or status strip y=214..239)
- Find next: moves cursor to next match, adjusts viewport
- Visual feedback: matched line gets a different highlight color
- Exit search: tap outside or press ESC

**Files affected:**
- `src/text_engine.ppl` — add `TE_FindNext`
- `src/renderer.ppl` — add search highlight color support (optional for MVP)
- `src/editor_shell.ppl` — add search mode state, query input mode, search dispatch

**New shell state for search:**
- `ES_SEARCH` — 1 = search mode active
- `ES_QUERY` — current search string
- `ES_MATCH_CL`, `ES_MATCH_CC` — last found position

**Search flow:**
1. User triggers search (new "SRC" key on control row, or hardware key)
2. Shell enters `ES_SEARCH=1` mode
3. Keyboard taps append chars to `ES_QUERY` (displayed in status strip)
4. "Find" button or ENT executes `TE_FindNext`
5. On match: cursor jumps, viewport adjusts, match line highlighted
6. Repeat taps for "find next"
7. ESC or miss exits search mode

**`TE_FindNext` design:**
```
TE_FindNext(query, from_cl, from_cc)
  FOR each line from_cl..TE_LineCount():
    pos := INSTRING(TE_GetLine(ln), query)
    if pos > 0 and (ln > from_cl OR pos > from_cc):
      RETURN {ln, pos}   // found
  RETURN {0, 0}          // not found
```
Uses `INSTRING` which is already confirmed in the project.

**Complexity:** Medium — requires new shell mode and minor TE extension
**Risk:** Low-medium — INSTRING is proven; the new shell mode needs care
**Value:** Very high — search is the most impactful "real editor" feature

---

### Workstream D — Navigation Upgrade

**What:**
- Preferred column: remember the desired column across ↑↓ moves
  New shell global `ES_PREF_CC` — set on horizontal move, preserved on vertical
- Page Up / Page Down: move viewport by `R_LINES_VIS` lines
- Jump to document start / end (Ctrl+Home, Ctrl+End equivalent)
- Jump to line number (optional, if search bar reusable)

**Files affected:** `src/editor_shell.ppl` primarily; possibly small TE additions

**Preferred column design:**
- `ES_PREF_CC` tracks the "intended" column before short-line clamping
- Set to `ES_CC` on any horizontal move or text edit
- On ↑/↓: call TE_MoveUp/Down with `ES_PREF_CC` as target, not current `ES_CC`
  This requires a `TE_MoveUpTo(cl, cc, target_cc)` variant or post-correction:
  ```
  res := TE_MoveUp(ES_CL, ES_CC)
  new_cl := res(1)
  // Try to restore preferred col on new line
  new_cc := ES_PREF_CC
  res2 := TE_ClampCursor(new_cl, new_cc)
  ES_CL := res2(1); ES_CC := res2(2)
  ```

**Complexity:** Low-medium — mostly shell logic, no new TE functions needed
**Risk:** Low — additive, no existing behavior broken
**Value:** Medium-high — important for editing longer documents

---

### Workstream E — Basic Editor Commands

**What:**
- New document / clear: resets L0 to `{""}`, cursor to (1,1)
- Jump to document start (line 1, col 1)
- Jump to document end (last line, last col)
- Line counter in header (already needed for cursor position display)
- Simple status strip: show `L:x/total C:y` using the y=214..239 reserved area

**Files affected:** `src/editor_shell.ppl`, minor update to `src/renderer.ppl`
  (to use y=214..239 status strip)

**Complexity:** Low
**Risk:** Low
**Value:** Medium — quality-of-life but not critical path

---

## 5. Recommended Prioritization

### Recommendation

```
PRIORITY 1: Workstream A — Keyboard UX Upgrade
PRIORITY 2: Workstream C — Search MVP
PRIORITY 3: Workstream B — Mixed-Text Rendering Improvement
PRIORITY 4: Workstream D — Navigation Upgrade
PRIORITY 5: Workstream E — Basic Editor Commands
```

### Justification

**A first (Keyboard UX):**
Everything else in Phase 2 requires tapping keys that don't yet exist or
can't be reached. The keyboard gap (no DEL, HOME, END, broken KBD toggle)
is a prerequisite blocker for comfortably testing all other features.
This is also the lowest-risk workstream — pure shell changes, no
renderer or text engine involvement.

**C second (Search):**
Search transforms the editor from a "typing tool" into a "text editor".
It is bounded, testable, uses proven primitives (INSTRING), and requires
only one new TE function. Every subsequent use of the editor benefits
from search. Implementing it second makes testing all other Phase 2
features easier. The risk is that search mode adds shell state complexity —
but it is self-contained and can be disabled cleanly.

**B third (Mixed-Text):**
Digits and punctuation in Hebrew text are unavoidable in real documents.
After search is working, the renderer limitation becomes the next most
visible pain point. This is localized to REND_DrawLine and can be
implemented without touching the cursor model or TE.

**D fourth (Navigation):**
Preferred column and page navigation become more relevant as users
write longer documents (enabled by search finding things). This is
lower urgency than visual legibility but significantly improves
editing experience.

**E fifth (Basic Commands):**
"New document" is useful but not critical for the editing workflow.
Status strip polish is incremental improvement, not a blocker.

---

## 6. Dependencies and Sequencing

```
text_engine.ppl (existing)
    |
    +-- A: Keyboard UX Upgrade
    |       (wires TE_Delete, TE_MoveLineStart, TE_MoveLineEnd)
    |       (enables DEL, HOME, END in all subsequent testing)
    |
    +-- C: Search MVP
    |       (adds TE_FindNext to text engine)
    |       (depends on: keyboard UX for query input)
    |
    +-- D: Navigation Upgrade
    |       (uses TE_ClampCursor for preferred column)
    |       (best implemented after A — benefits from HOME/END)
    |
renderer.ppl (existing)
    |
    +-- B: Mixed-Text Rendering
    |       (modifies REND_DrawLine RTL path only)
    |       (independent of A, C, D — can be done in parallel)
    |
    +-- E: Basic Commands / Status Strip
            (uses reserved y=214..239 area)
            (minor renderer change to draw status area)
```

**Key dependency:** Workstream C (Search) benefits from A being complete,
because the user needs to type queries using the keyboard — which is more
comfortable after the keyboard UX upgrade.

**Independent tracks:** B (Mixed-Text) can be developed in parallel with A/C/D
since it only touches the renderer's RTL line drawing path.

---

## 7. Risk Review

### Risk 1: Control row overcrowding (Workstream A)
Adding DEL, HOME, END to 9-key control row → 12 keys.
At 26px per key = 312px: fits, but tap targets drop from 35px to 26px.
**Mitigation:** Acceptable — control keys are expected to be smaller.
Alternatively, split navigation (HOME/END/↑/↓) and editing (BS/DEL/ENT)
into two strips, but this reduces the letter area to 3 lines at lower y.
**Recommendation:** 12 keys × 26px in one strip. Re-evaluate after testing.

### Risk 2: Persistent KBD toggle in header conflicts with header content
Header currently shows "HP Prime Editor" + "[HEB]/[CTL]".
Adding `[K]` at x=285 consumes 35px of a 320px header.
**Mitigation:** Shrink title text or abbreviate. "Editor [HEB] [K]" fits.

### Risk 3: Search mode adds state complexity to the shell (Workstream C)
Two main risks: (a) search mode state leaks into normal editing; (b) query
input mode (Hebrew keyboard typing into query instead of document) is confusing.
**Mitigation:** Strict `ES_SEARCH` flag — all drawing and touch dispatch
branches explicitly check this flag. A visible "SEARCH:" prompt in the
status strip makes mode clear to the user. Exit via ESC or a "cancel" tap.

### Risk 4: Mixed-text TEXTOUT_P vertical alignment (Workstream B)
TEXTOUT_P size-1 chars (~10px tall) vs HFB glyphs (20px cell, content rows 7–17).
If vertical offsets mismatch, the line looks jagged.
**Mitigation:** Use `scr_y + 6` offset for TEXTOUT_P (already documented as
approximate alignment). Test on hardware to confirm. If still misaligned,
adjust the offset — it is a single constant.

### Risk 5: Preferred column and TE_MoveUp/Down interaction (Workstream D)
`TE_MoveUp(cl, cc)` already clamps `cc` to the previous line's length.
Adding preferred column post-correction (`TE_ClampCursor`) requires
careful ordering: move first, then restore preferred column on new line.
**Mitigation:** The logic is: move to new line, set cc = min(ES_PREF_CC, SIZE(new_line)+1).
This is safe and deterministic. Document it clearly.

### Risk 6: Search performance on long documents (Workstream C)
`TE_FindNext` loops over all document lines using INSTRING. On HP Prime,
a 100-line document scan should be fast enough. A 1000-line document may
show a short pause.
**Mitigation:** Document the performance limitation. No optimization needed
for MVP. If needed, add a progress indicator in the status strip.

### Risk 7: Redraw performance regression (cross-cutting)
Phase 2 adds more drawing (status strip, search highlight) on top of
existing full-screen redraws.
**Mitigation:** Workstream A should also implement the partial redraw
optimization: introduce `ES_DOC_DIRTY` and `ES_KBD_DIRTY` flags to redraw
editor and keyboard independently. This reduces the per-keystroke cost.

---

## 8. Recommended Task Breakdown

### Task 8A — Keyboard UX Upgrade (implement first)

**Scope:**
- Redesign control row: 12 keys × 26px
  New layout: SP BS DEL ENT ← → ↑ ↓ HM END LAY [persistent KBD in header]
- Add action codes: -11 (DEL), -12 (HOME), -13 (END), -14 (new doc)
- Wire TE_Delete, TE_MoveLineStart, TE_MoveLineEnd
- Add persistent `[K]` toggle in header bar (always visible)
- Add cursor position display in header: `L:x C:y`
- Implement partial redraw: `ES_DOC_DIRTY` + `ES_KBD_DIRTY` flags
- Update `hpprgm/7. editor_shell.txt`

**Files:** `src/editor_shell.ppl`
**Tests:** Manual — verify all 12 control keys, KBD toggle from both states,
cursor position display updates, partial redraw (no flicker on text edit)

---

### Task 8B — Search MVP (implement second)

**Scope:**
- Add `TE_FindNext(query, from_cl, from_cc)` to text_engine
- Add search state to shell: `ES_SEARCH`, `ES_QUERY`, `ES_MATCH_CL`, `ES_MATCH_CC`
- Add search mode draw: query display in status strip (y=214..239)
- Add "SRC" key to control row (replace LAY or add to 2nd control strip)
- Touch dispatch: in search mode, letter taps append to ES_QUERY
- Implement find-next: calls TE_FindNext, jumps cursor, adjusts viewport
- Add search match highlight (different active-line color for match line)
- Exit search: ESC key or "X" button
- Update test harness with search scenario

**Files:** `src/text_engine.ppl`, `src/editor_shell.ppl`, `src/renderer.ppl` (minor)
**Tests:** Manual + TE unit test for TE_FindNext

---

### Task 8C — Mixed-Text Rendering (implement third)

**Scope:**
- Modify `REND_DrawLine` RTL path: replace `REND__PlaceholderBox` for
  non-Hebrew chars with `TEXTOUT_P(ch, bx+1, scr_y+6, 1, R_COL_FG)`
- Adjust vertical offset constant if alignment is imperfect on hardware
- Update renderer test (test_renderer_basic S6) to verify mixed content
- Update `docs/RENDERER_PHASE1.md` to reflect the improvement
- Update `hpprgm/5. renderer.txt`

**Files:** `src/renderer.ppl`
**Tests:** S6 scenario in test_renderer_basic — "שלום 2024" should show
real digits instead of gray boxes

---

### Task 8D — Navigation Upgrade (implement fourth)

**Scope:**
- Add `ES_PREF_CC` global to shell
- Set `ES_PREF_CC` on: any horizontal move, text insertion, line change
- Apply `ES_PREF_CC` on ↑/↓: after TE_MoveUp/Down, restore preferred col
  via `TE_ClampCursor`
- Add page up / page down: shift R_VIEW_TOP by R_LINES_VIS, clamp, redraw
- Add jump to document start/end: new action codes -15, -16
- Add "⊤" (doc start) and "⊥" (doc end) keys somewhere accessible
- Update test harness

**Files:** `src/editor_shell.ppl`
**Tests:** Manual — verify column preservation across up/down; page scroll

---

### Task 8E — Basic Editor Commands (implement fifth)

**Scope:**
- Add `TE_ClearDoc()` to text engine: resets L0 to `{""}`, returns {1,1}
- Add "NEW" action to shell (-14, already reserved in 8A)
- Implement status strip (y=214..239): show `L:x/total  C:y`
  Draw status strip in `ES__DrawAll()` — use `REND_DrawStatus` or direct draw
- Update `docs/EDITOR_SHELL_PHASE1.md` or write `EDITOR_SHELL_PHASE2.md`

**Files:** `src/text_engine.ppl`, `src/editor_shell.ppl`, `src/renderer.ppl` (minor)

---

## 9. Suggested Milestones

| Milestone | Tasks | Marker |
|-----------|-------|--------|
| **M1: Keyboard Complete** | 8A | All TE operations accessible via touch; KBD toggle works from both states; cursor position visible |
| **M2: Search Working** | 8A + 8B | User can find text in document; cursor jumps to match; viewport follows |
| **M3: Mixed Text Legible** | 8C | Hebrew + digits/punctuation render correctly in RTL lines |
| **M4: Navigation Smooth** | 8D | Preferred column preserved; page up/down work |
| **M5: Phase 2 Complete** | 8A–8E | All above + status strip + new document command |

---

## 10. Definition of Done for Phase 2

Phase 2 is meaningfully complete when all of the following are true:

1. DEL, HOME, END are accessible from the keyboard panel
2. Keyboard panel can be toggled from both visible and hidden states
3. Cursor position (L:x C:y) is visible in the header at all times
4. Search finds the next occurrence of a query string and jumps the cursor
5. Hebrew + digits/punctuation in the same line renders without gray boxes
6. Vertical navigation (↑/↓) preserves the preferred column
7. Page up/page down works
8. All items above tested and documented

**Not required for Phase 2 done:** Russian layout, full file I/O, full bidi,
copy/paste, undo/redo.

---

## 11. Deferred Items

| Feature | Reason for deferral |
|---------|---------------------|
| Russian / Cyrillic keyboard layout | Requires confirming Cyrillic via TEXTOUT_P (Spike02 says it works) — worth adding but needs layout design. Defer to Phase 3. |
| File save / load | Requires HP Prime file API. Not confirmed in spikes. Separate research spike needed. |
| Full Unicode bidi (mixed runs) | High complexity, low marginal benefit for current use cases. Defer to Phase 4+. |
| Copy / paste | Requires clipboard API or internal buffer. Not in HP Prime spikes. |
| Undo / redo | Requires change history. Significant TE redesign. Phase 4+. |
| Find and replace | Search MVP covers find-only. Replace requires careful TE integration. Phase 3. |
| Touch selection | Requires tap-and-drag handling. Complex touch model. Phase 4+. |
| Hardware key mapping (full) | HP Prime hardware key codes not confirmed for most keys. Needs a dedicated spike. |
| Proportional LTR spacing | Non-Hebrew chars all advance 7px. True proportional spacing needs font metrics. Deferred — 7px is close enough for Latin. |
| Niqqud / cantillation marks | Unicode 1456–1479 range. Not in current font. Separate font task if needed. |

---

## 12. Final Recommendation

**The best immediate next implementation task is Task 8A: Keyboard UX Upgrade.**

Reasoning:
- It unblocks everything else. Without DEL, HOME, END, and a reliable KBD toggle,
  testing any Phase 2 feature is frustrating.
- It is the lowest-risk task: pure shell changes, no renderer or TE involvement.
- It delivers visible, immediate improvement that users will notice on every
  interaction.
- It enables the partial redraw optimization (ES_DOC_DIRTY / ES_KBD_DIRTY),
  which reduces flicker and makes all subsequent work more stable.

**After 8A, the best next task is 8B: Search MVP.**

Search is the single feature that most transforms the editor from "can type text"
to "can work with text". It is well-bounded, uses proven primitives (INSTRING),
and its implementation is isolated enough that it can be done cleanly after the
keyboard redesign stabilizes the shell structure.

**Task 8C (Mixed-Text) should follow Search**, not precede it, because:
- It requires renderer changes (higher risk than shell changes).
- Users can tolerate gray boxes while learning the editor's other capabilities.
- Once search works, users will write longer documents and encounter mixed content
  more frequently — making 8C feel more impactful at that point.

**Tasks 8D and 8E** are real improvements but they address polish concerns rather
than blocking gaps. Implement them after the first three tasks validate the
overall Phase 2 architecture.
