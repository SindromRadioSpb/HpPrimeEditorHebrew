# SEARCH_PHASE1.md
## HP Prime Hebrew-Russian Editor — Search MVP

**Module:** `search_engine.ppl`
**Task:** 8C — Search MVP
**Status:** Implemented

---

## 1. Scope

### In scope
- Search query entry via virtual keyboard in search mode
- Forward document search through all lines
- Find-next (continues from after last match)
- Wrap-once: search wraps from end back to start with `[WR]` indicator
- Cursor jump to match
- Viewport adjustment so match is visible
- Visual feedback: `[OK]`, `[??]`, `[WR]` in header
- Hebrew search on logical Unicode text
- Search cancellation (CNL key or hardware ESC)

### Out of scope (deferred)
- Replace
- Regex
- Case-insensitive folding
- Search history
- Visual match highlighting overlay
- Fuzzy or morphological search
- Cross-document search

---

## 2. Dependencies

| Module | Used for |
|---|---|
| `text_engine` | `TE_GetLine(lnum)`, `TE_LineCount()` — safe document access |
| `editor_shell` | Mode management, query editing, cursor/viewport update, display |
| `renderer` | Renders document after cursor jump; no search logic |
| `hebrew_font_bitmap` | Hebrew letter keys in query entry; search logic is script-agnostic |

**Load order on HP Prime:**
1. `hebrew_font_bitmap`
2. `text_engine`
3. `renderer`
4. `search_engine`
5. `editor_shell`
6. `test_search_basic` (optional)

---

## 3. Search State Model

### `search_engine.ppl` globals

| Variable | Type | Meaning |
|---|---|---|
| `SE_QUERY` | string | Current search query. Empty = no active search. |
| `SE_LAST_LINE` | integer | Line of last successful match (0 = no prior match). |
| `SE_LAST_COL` | integer | Start column of last match (1-based). |

### `editor_shell.ppl` globals (search-related)

| Variable | Type | Values |
|---|---|---|
| `ES_SRCH_MODE` | integer | 0 = normal editing, 1 = search mode active |
| `ES_SRCH_MSG` | integer | 0=idle, 1=found, 2=not found, 3=found-after-wrap |

### State transitions

```
Normal mode:
  [SR key] -> SE_Init(); ES_SRCH_MODE=1; ES_SRCH_MSG=0

Search mode:
  char tap   -> SE_QUERY += char; SE_LAST_LINE=0 (reset)
  [BS key]   -> SE_QUERY remove last char; SE_LAST_LINE=0 (reset)
  [GO key]   -> SE_FindNext() -> update ES_CL/ES_CC + ES_SRCH_MSG
  [CNL key]  -> ES_SRCH_MODE=0 (return to normal)
  [ESC hw]   -> ES_SRCH_MODE=0 (return to normal; editor stays open)
  [LA key]   -> ES_KBD_LAY toggle (to type Hebrew or Latin queries)
```

### Why SE_LAST_LINE is reset on query change

When the query changes (char added or removed), `SE_LAST_LINE := 0` resets
the match position. This ensures the next `SE_FindNext()` call starts fresh
from line 1, not from a stale position belonging to the old query.

---

## 4. Query Input Model

### Entering search mode

Tap the `[SR]` key (key 13, rightmost in control row). `SE_Init()` is called,
clearing any previous query and match state.

### Typing a query

All character taps (letter keys + SP) in search mode append to `SE_QUERY`
instead of inserting into the document. There is no risk of accidentally
editing the document: `ES_SRCH_MODE` gates all character dispatch.

### Editing the query

- `[BS]` key: removes the last character from `SE_QUERY`
- No way to position a cursor within the query in MVP (append/delete-last only)

### Switching script for query

`[LA]` still works in search mode. Tap `[LA]` to toggle between HEB and CTL
layout to enter Hebrew or Latin/punctuation characters in the query.

**Note:** Hebrew characters in the query header will not render visually
(TEXTOUT_P uses system font which does not contain Hebrew). The search
itself works correctly — see Known Limitations.

### Executing search

Tap `[GO]` (key 4, label changes from "EN" to "GO" in search mode).

### Cancelling search

- Tap `[CNL]` (key 13, label changes from "SR" to "CNL" in search mode)
- Press hardware `ESC` key

In both cases: returns to normal editing mode. Cursor stays at its last
position (which may be the last found match location).

---

## 5. Match Semantics

### SE_FindNext() algorithm

1. **Determine start position:**
   - If `SE_LAST_LINE == 0`: start from line 1, column 1 (fresh search)
   - Else: start from `(SE_LAST_LINE, SE_LAST_COL + SIZE(SE_QUERY))` — position
     immediately after the end of the last match

2. **Forward pass:** scan from start position to end of document, line by line.
   On the start line, search begins at `start_col` (not col 1).
   Uses `INSTRING(MID(line, start_col, 500), SE_QUERY)`.

3. **If no match found, wrap pass:** if the start position is not (1,1),
   scan from line 1, col 1 up to (but not including) `start_col` on the
   start line. Returns status 2 (found-after-wrap).

4. **If still not found:** return `{0, 0, 0}` (not found).

5. **On success:** update `SE_LAST_LINE` and `SE_LAST_COL` so the next call
   advances past this match.

### First match vs. find-next

There is no separate "find first" operation. Both are handled by `SE_FindNext()`:
- After `SE_Init()` or after query change (`SE_LAST_LINE=0`): behaves as find-first
- After a successful match: behaves as find-next

### Wrap behavior

**Wrap-once.** The search wraps at most once. After wrapping, `ES_SRCH_MSG := 3`
and `[WR]` (yellow) is shown in the header. The next `SE_FindNext()` call will
start from the wrapped match position — if there is only one occurrence, it will
wrap again and find the same match, again marked `[WR]`. This is expected behavior
for a single-occurrence document.

### No match

`ES_SRCH_MSG := 2`, `[??]` (red) shown in header. Cursor does not move.
`SE_LAST_LINE` is not changed (stays at last successful match or 0 if never found).

### Empty query

`SE_FindNext()` returns `{0,0,0}` immediately. No cursor movement.

---

## 6. Viewport Behavior

After a successful match (`ES_CL`/`ES_CC` updated):
- `ES__AdjustViewport()` is called in the main event loop before redraw
- This adjusts `R_VIEW_TOP` so the cursor line is visible
- No special viewport logic is needed in the search path; the existing
  viewport mechanism handles it transparently

---

## 7. Status / Feedback Model

### Search mode indicator in header

While `ES_SRCH_MODE == 1`, the header shows:

```
[>>] [query text]                    [status]  [K]
```

- `>>` in cyan: search mode active
- query text in white: current `SE_QUERY` content
- status indicator on right:
  - (blank): idle — search mode entered but GO not yet tapped
  - `[OK]` green: last find succeeded (forward match)
  - `[??]` red: last find returned not-found
  - `[WR]` yellow: last find succeeded after wrapping from end to start

### Normal mode header (after cancelling search)

```
HP Ed  L:n C:n  [HEB]/[CTL]  [K]
```

Cursor position reflects where search left the cursor.

### Control row visual differentiation in search mode

Active keys (SP, BS, GO, LA, CNL) have normal blue background and labels.
Inactive keys (DL, <, >, ^, v, HM, ED, KB) are drawn with a dark gray
background and no label, making the search-relevant controls immediately clear.

---

## 8. Known Limitations

### Hebrew characters not visible in query header

`TEXTOUT_P` uses the HP Prime system font which does not contain Hebrew Unicode
characters (confirmed in Spike01). Hebrew characters in `SE_QUERY` will appear
as blank or placeholder glyphs in the header.

**Workaround:** Search logic operates on logical Unicode strings (as stored in
`L0` by `text_engine`), so Hebrew search works correctly even though the query
is invisible in the header. The user can confirm the query by observing which
Hebrew keys they tapped and counting characters.

**Future fix:** Render query using `HFB_BlitGlyph` for Hebrew characters in the
header. Requires per-character rendering loop in `ES__DrawHeader`.

### Search operates on logical text, not visual order

For RTL lines (Hebrew), the text is stored logically (first character of the
visual line = last character in `L0`). Search finds matches at their logical
position, and `ES_CC` is set to the logical column. The cursor position in the
document matches the logical text storage model used by `text_engine`.

### Match column for Hebrew lines

On a RTL Hebrew line, `ES_CC` after a match will be the logical column
(1 = first Hebrew character in storage order). The visual cursor will appear
correctly as rendered by `renderer.ppl`.

### No highlight overlay

The matched text is not visually highlighted in the editor area. The cursor
is placed at the start of the match, which is the primary match indicator.

### No replace

Not implemented. Deferred to Phase 3.

### Single-line query only

The query cannot span multiple lines.

---

## 9. Future Work

| Feature | Priority | Notes |
|---|---|---|
| Hebrew query header rendering | High | Use HFB_BlitGlyph per char in header |
| Match highlight overlay | Medium | Color background of matched text in renderer |
| Replace (single occurrence) | Medium | Task 8E candidate |
| Replace all | Low | Phase 3 |
| Case-insensitive Latin search | Low | Lowercase fold before comparison |
| Search history | Low | Keep last N queries |
| Search-within-selection | Very low | Not practical on HP Prime |

---

## 10. API Reference

### search_engine.ppl

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `SE_Init()` | — | — | Reset all search state (query + match position) |
| `SE_Reset()` | — | — | Reset match position only; keep query |
| `SE_FindNext()` | — | `{status, line, col}` | Find next match; status: 0=notfound, 1=found, 2=wrapped |

| Global | Type | Description |
|---|---|---|
| `SE_QUERY` | string | Current search query |
| `SE_LAST_LINE` | integer | Last matched line (0=none) |
| `SE_LAST_COL` | integer | Last matched column (1-based) |

### editor_shell.ppl (search-related additions)

| Global | Type | Description |
|---|---|---|
| `ES_SRCH_MODE` | integer | 0=normal, 1=search mode |
| `ES_SRCH_MSG` | integer | 0=idle, 1=found, 2=notfound, 3=wrapped |

| Function | Description |
|---|---|
| `ES__DoSearchAction(act)` | Handles all actions when `ES_SRCH_MODE==1` |

---

*Document created: Task 8C — Search MVP*
