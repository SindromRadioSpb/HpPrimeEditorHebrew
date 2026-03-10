# Text Engine — Phase 1B Contract

**Module:** `src/text_engine.ppl`
**Phase:** 1B (Logical Editor Core)
**Status:** Implemented, awaiting test harness validation

---

## State Model

| Variable | Type | Range | Meaning |
|---|---|---|---|
| `L0` | Global list of strings | 1-based | Document lines |
| `cur_line` (cl) | Integer | 1 .. SIZE(L0) | Current line |
| `cur_col` (cc) | Integer | 1 .. SIZE(line)+1 | Current column |

**Cursor convention:** 1-based. `cur_col = SIZE(line)+1` means caret is after the last character (end-of-line insert position). Empty line has `cur_col` range `1..1`.

**Document invariant:** L0 always contains at least 1 element. `TE_Init()` initializes to `{""}` (one empty line).

---

## Calling Convention

All editing and movement functions accept `(cl, cc)` and return `{new_cl, new_cc}`:

```ppl
LOCAL res, cl, cc;
res := TE_Init();
cl  := res(1);
cc  := res(2);

res := TE_InsertChar(cl, cc, "A");
cl  := res(1);
cc  := res(2);
```

Document state is held in the global `L0`. Callers do not pass `L0` explicitly.

---

## Public API

### Initialization

| Function | Signature | Returns | Description |
|---|---|---|---|
| `TE_Init` | `()` | `{1, 1}` | Empty doc (one empty line), cursor at start |
| `TE_InitFrom` | `(lines_list)` | `{1, 1}` | Doc from list of strings; empty list → one empty line |

### Access Helpers

| Function | Signature | Returns | Description |
|---|---|---|---|
| `TE_LineCount` | `()` | integer | Number of lines |
| `TE_GetLine` | `(lnum)` | string | Line text; `""` if out of range |
| `TE_SetLine` | `(lnum, txt)` | — | Replace line; no-op if out of range |
| `TE_ClampCursor` | `(cl, cc)` | `{cl, cc}` | Clamp to valid bounds |

### String Helpers (also exported for test harness)

| Function | Signature | Returns | Description |
|---|---|---|---|
| `TE_StrLeft` | `(txt, n)` | string | First n chars; safe for n≤0 and n≥len |
| `TE_StrRight` | `(txt, from_col)` | string | Chars from 1-based col to end; safe |

### Editing Operations

| Function | Signature | Returns | Description |
|---|---|---|---|
| `TE_InsertChar` | `(cl, cc, ch)` | `{cl, cc+1}` | Insert single char at cursor |
| `TE_InsertText` | `(cl, cc, txt)` | `{cl, cc+len}` | Insert string at cursor |
| `TE_Backspace` | `(cl, cc)` | `{new_cl, new_cc}` | Delete char left; merge if at line start |
| `TE_Delete` | `(cl, cc)` | `{new_cl, new_cc}` | Delete char at cursor; merge if at line end |
| `TE_Newline` | `(cl, cc)` | `{cl+1, 1}` | Split line at cursor |

### Cursor Movement

| Function | Signature | Returns | Description |
|---|---|---|---|
| `TE_MoveLeft` | `(cl, cc)` | `{new_cl, new_cc}` | Left; crosses to previous line end |
| `TE_MoveRight` | `(cl, cc)` | `{new_cl, new_cc}` | Right; crosses to next line start |
| `TE_MoveUp` | `(cl, cc)` | `{new_cl, new_cc}` | Up; column preserved, clamped |
| `TE_MoveDown` | `(cl, cc)` | `{new_cl, new_cc}` | Down; column preserved, clamped |
| `TE_MoveLineStart` | `(cl, cc)` | `{cl, 1}` | Jump to column 1 |
| `TE_MoveLineEnd` | `(cl, cc)` | `{cl, len+1}` | Jump to after last char |

---

## Defined Edge Case Behaviors

| Situation | Behavior |
|---|---|
| Backspace at `{1, 1}` | No-op. Cursor unchanged. |
| Delete at end of last line | No-op. Cursor unchanged. |
| MoveLeft at `{1, 1}` | No-op. Cursor unchanged. |
| MoveRight at end of last line | No-op. Cursor unchanged. |
| MoveUp at line 1 | No-op. Cursor unchanged. |
| MoveDown at last line | No-op. Cursor unchanged. |
| Insert into empty line | Line becomes single char. |
| Backspace at start of non-first line | Merge: `prev_line + cur_line`. Cursor → `{cl-1, SIZE(prev)+1}`. |
| Delete at end of non-last line | Merge: `cur_line + next_line`. Cursor stays. |
| Newline at line end | New empty line inserted. Cursor → `{cl+1, 1}`. |
| Newline at line start | Empty line inserted before current text. Cursor → `{cl+1, 1}`. |
| MoveDown to shorter line | Column clamped to `SIZE(next_line)+1`. |
| MoveUp to shorter line | Column clamped to `SIZE(prev_line)+1`. |

---

## Internal Implementation Notes

**Document mutation:** All modifications rebuild L0 via CONCAT (O(n) per operation). This is safe and confirmed working. For 200 lines at ~5μs/iteration, total rebuild is ~1ms — acceptable.

**String slicing:** Uses `TE_StrLeft` and `TE_StrRight` — safe wrappers around `MID()` that handle 0-length and out-of-bounds cases without error.

**No element-assignment to L0:** `L0(n) := value` is avoided; full rebuild is used instead. This is a conservative choice to avoid untested behavior.

**Preferred-column preservation (MoveUp/MoveDown):** Column is clamped to the shorter line's length+1. True "sticky column" (remembering the column before clamping) is **deferred to Phase 2**.

---

## Risk Register

| Risk | Mitigation |
|---|---|
| `LOCAL i` in test harness shadows imaginary unit | Confirmed safe from Spike05e |
| `result(1)` on returned list | Same pattern as `doc(n)` — confirmed in Spike05e |
| Nested list `{new_doc, cl, cc}` as return type | Not used — only `{cl, cc}` returned (doc via L0 global) |
| `MID(str, n, 0)` edge case | Avoided via `TE_StrLeft/TE_StrRight` guards |
| Cross-file EXPORT function calls | Standard HP PPL behavior; both files must be loaded |
| `LOCAL PROCEDURE` calling another `LOCAL PROCEDURE` | Confirmed pattern from Spike04 |
| Hebrew chars in strings causing encoding issues | CHAR(n) decimal syntax confirmed from Spike02 |

---

## Known Limitations (Phase 1B)

- No visual BiDi — logical order only. Renderer decides display order.
- No undo/redo. Deferred to Phase 2.
- No selection model. Deferred to Phase 2.
- No viewport state — text engine is pure logical; renderer manages scroll.
- Preferred column for up/down not sticky — simple clamp only.
- No search in engine — INSTRING available, search UI is separate module.
- Performance: O(n) per edit for 200-line doc. Acceptable but not O(1).

---

## Phase 1B Acceptance Criteria

All 12 test scenarios in `tests/test_text_engine_basic.ppl` must show **PASS**.

| # | Scenario | Validates |
|---|---|---|
| S01 | Empty init | TE_Init, TE_LineCount, TE_GetLine |
| S02 | Insert A B C | TE_InsertChar, cursor advance |
| S03 | Mid-line "ABEF"→"ABCDEF" | TE_InsertText, TE_MoveRight |
| S04 | Newline "ABCD"→"AB"+"CD" | TE_Newline, line split |
| S05 | Backspace inside line | TE_Backspace char delete |
| S06 | Backspace at line start | TE_Backspace line merge |
| S07 | Delete inside line | TE_Delete char delete |
| S08 | Delete at line end | TE_Delete line merge |
| S09 | Cross-line move L/R | TE_MoveLeft, TE_MoveRight boundary |
| S10 | Up/down column clamp | TE_MoveUp, TE_MoveDown |
| S11 | Hebrew/Russian storage | No corruption of Unicode chars |
| S12 | 200-line stability | Large doc edits, split, count |
