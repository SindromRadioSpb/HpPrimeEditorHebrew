# Claude Code Prompt — Task: Search MVP for HP Prime Editor
## Project: Premium Hebrew-Russian Editor for HP Prime
## Repository: `J:\Project_Vibe\HpPrimeEditor`

You are working as a senior software architect and implementation engineer on a premium-grade Hebrew-Russian editor for HP Prime.

This task is to implement the next concrete feature phase:

**Search MVP for HP Prime editor**

This must be a real, bounded, production-minded MVP search feature, not a fake placeholder.

---

## Mission

Build a practical document search feature that integrates with the existing editor architecture:

- text engine,
- renderer,
- editor shell,
- viewport behavior.

The search system must allow the user to:
- enter a search query,
- search through the document,
- jump to the first or next match,
- move the cursor to the match,
- keep the match visible,
- receive a clear “not found” result.

This phase should significantly improve real usability while keeping the scope bounded.

---

## Existing Foundation

These components already exist and must be used, not reimplemented:

### 1. Text engine
Already handles:
- document as list of strings,
- cursor line / cursor column,
- editing logic,
- line access helpers.

### 2. Renderer
Already handles:
- document rendering,
- cursor rendering,
- viewport start,
- Hebrew bitmap rendering,
- line-level RTL/LTR behavior.

### 3. Editor shell
Already handles:
- event loop,
- actions,
- redraw,
- keyboard visibility,
- viewport management,
- input handling.

### 4. Hebrew bitmap font
Already exists and must continue to be used for Hebrew display.

---

## Critical Constraints

- Do **not** implement replace in this task.
- Do **not** implement regex.
- Do **not** implement full linguistic search.
- Do **not** implement case-folding complexity unless clearly justified for current supported scripts.
- Do **not** rebuild the text engine inside search code.
- Do **not** turn the shell into a giant monolith.

This task is strictly:
- search query input,
- find,
- find next,
- cursor jump,
- viewport sync,
- user feedback.

---

## Mandatory Pre-Implementation Audit

Before coding, inspect the repository:

`J:\Project_Vibe\HpPrimeEditor`

You must verify:
- actual text engine file and API names,
- actual editor shell file and API names,
- actual renderer file and viewport behavior,
- current keyboard/layout model,
- any current status line or mode system,
- whether any search scaffolding already exists,
- what test harnesses currently exist and how they are run.

Do not assume names or APIs without checking repo state.

---

## Scope of Search MVP

### In scope
- search state,
- search query entry,
- search execution through all document lines,
- next-match navigation,
- match-to-cursor jump,
- viewport movement to found match,
- visible search status / feedback,
- manual test harness and docs.

### Out of scope
- replace,
- regex,
- advanced highlight overlays,
- persistent search history,
- case-insensitive normalization across all scripts,
- fuzzy search,
- morphological search,
- cross-document search.

---

## Product Goal

This feature must make the editor more useful for real work.

The user must be able to:
1. open search mode,
2. enter a query,
3. run search,
4. jump to a match,
5. continue to next match,
6. know when nothing is found.

This should be practical and understandable on HP Prime.

---

## Required Search Design

You must define and implement a clear search state model.

At minimum include:

- search mode active / inactive
- current search query
- last found line
- last found column
- current search start position for “find next”
- status message or equivalent result state

You may adapt names, but the model must be explicit and documented.

---

## Required Search Semantics

### 1. Search domain
Search through the document line by line using the logical text stored in the text engine.

### 2. Match behavior
When a match is found:
- move cursor to the match,
- move viewport if needed so the match is visible,
- set search state so “find next” continues from after the current match.

### 3. Not found behavior
If no match is found:
- show a clear status message,
- do not crash,
- do not leave the editor in a confusing partial state.

### 4. Search order
Use a deterministic forward search order:
- current line from current start position,
- then remaining lines downward,
- optionally wrap or explicitly do not wrap — but document the chosen behavior.

### 5. MVP choice on wrap
You must explicitly choose one:
- no wrap
- wrap once

Document the exact rule.  
My recommendation for MVP: **wrap once with a clear status indication**, or **no wrap with explicit “end reached”**. Choose one and be consistent.

---

## Query Input Requirements

You must define how the user enters the search query.

Possible acceptable MVP patterns:
- a dedicated search mode using the virtual keyboard,
- a simple input panel / query bar,
- a temporary mode where keyboard input goes into the search query instead of the document.

But do not leave it vague.

### Required behavior
- user can enter characters for the query,
- user can backspace query characters,
- user can confirm search,
- user can cancel search mode.

Document the exact controls.

---

## Renderer / UI Integration Requirements

You must define how search is represented visually.

At minimum the UI must show:
- that search mode is active, or
- the current query, or
- a status line / message.

When a match is found, the user must be able to tell that:
- search happened,
- the cursor moved,
- the viewport moved if needed.

A separate highlight overlay is optional, not required for MVP.

---

## Required Files

Create and/or update the following:

### 1. Search implementation
If repo style supports a separate module, create something like:
- `src/search_engine.ppl`

or, if better for the current codebase,
- bounded search helpers inside `editor_shell.ppl`

But do not hide major search logic in random places.  
Keep the design explicit.

### 2. Shell integration
Update:
- `src/editor_shell.ppl`

to support search mode and search actions.

### 3. Test harness
Create:
- `tests/test_search_basic.ppl`

or an equivalent search-specific manual validation harness.

### 4. Documentation
Create or update:
- `docs/SEARCH_PHASE1.md`

### 5. HP Prime loader copies
If repo convention already uses them, also provide:
- `hpprgm/search_*.txt`
- updated shell/test copies

according to repo conventions.

---

## Required Search API / Responsibilities

You must clearly separate responsibilities.

### Search logic responsibilities
- query matching
- next-match progression
- returned match position

### Shell responsibilities
- entering/exiting search mode
- query editing
- calling search
- moving cursor/viewport
- status updates
- redraw

### Renderer responsibilities
- displaying whatever search mode/status indicators are needed
- not owning the search logic itself

---

## Required Test Scenarios

Your test harness must allow practical manual verification of at least these cases:

### Scenario 1 — Search mode entry
- enter search mode
- query area/status appears
- no crash

### Scenario 2 — Query input
- type a short query
- verify characters appear in query state
- backspace works

### Scenario 3 — First match
- query exists in document
- search finds first match
- cursor jumps correctly
- viewport adjusts if needed

### Scenario 4 — Find next
- same query appears multiple times
- next match advances correctly
- does not repeat the same match incorrectly

### Scenario 5 — Not found
- query does not exist
- clear “not found” behavior shown

### Scenario 6 — End-of-document behavior
- search reaches last match
- behavior matches documented no-wrap/wrap rule

### Scenario 7 — Hebrew search
- Hebrew query against Hebrew lines
- correct match movement

### Scenario 8 — Mixed-content line
- search query against a line containing Hebrew + digits or punctuation
- behavior consistent with logical text storage

### Scenario 9 — Search cancellation
- enter search mode
- cancel
- return to normal editing cleanly

---

## Required Risk Review

Before implementing, explicitly address these risks:

### 1. Query-entry vs document-entry confusion
Search mode must not accidentally insert query text into the document.

### 2. Cursor/search state desync
Search result must not leave cursor and status inconsistent.

### 3. Viewport mismatch
Found match must remain visible.

### 4. RTL/LTR interpretation confusion
Search operates on logical stored text, not on visual glyph order.
This must be documented clearly.

### 5. Repeated find-next bugs
Must not get stuck on the same match forever.

### 6. Empty query edge case
You must explicitly define what happens when the query is empty.

For each risk:
- mitigate,
- test,
- or document bounded behavior.

---

## Documentation Requirements

`docs/SEARCH_PHASE1.md` must include:

### 1. Scope
What Search MVP includes and excludes.

### 2. Dependencies
Text engine, shell, renderer.

### 3. Search state model
What state is stored and how it is used.

### 4. Query input model
How the user enters and edits a search query.

### 5. Match semantics
How first match and next match behave.

### 6. Viewport behavior
How the found result is made visible.

### 7. Status / feedback model
How “found”, “not found”, and search mode are communicated.

### 8. Known limitations
Especially logical-text search vs visual rendering, lack of replace, etc.

### 9. Future work
Replace, highlight, better mixed-line support, richer query UX.

---

## Acceptance Criteria

This task is complete only if all of the following are true:

1. Search mode exists and is enterable.
2. A user can type and edit a query.
3. Search finds matches in the current document.
4. Find-next works across multiple matches.
5. Cursor jumps to the match.
6. Viewport keeps the match visible.
7. Not-found behavior is clear and stable.
8. Hebrew search works against logical stored Hebrew text.
9. A search-specific test harness exists.
10. The feature is documented clearly.

---

## Output Format

Your response must include:

### 1. Repo audit findings
What already exists and what will be created/updated.

### 2. Design decisions
Search mode, state model, query input model, match semantics, wrap/no-wrap choice.

### 3. Implementation plan
Files to create/update and their roles.

### 4. Code
Provide actual implementation code for:
- search module/helpers,
- updated shell integration,
- test harness.

### 5. Documentation
Provide content for:
- `docs/SEARCH_PHASE1.md`

### 6. Test plan
How to load and run on HP Prime.

### 7. Definition of Done
Concrete acceptance criteria.

### 8. Deferred items
Clearly list what remains for future phases.

---

## Important Engineering Behavior

- Keep the MVP bounded.
- Keep the search logic explicit.
- Use the text engine as the source of truth for document contents.
- Use the shell for mode management and action dispatch.
- Keep renderer responsibilities limited to display.
- Do not fake full search sophistication.
- Build a clean and useful MVP.

---

## Final Instruction

Start with repo audit and contract clarification.

Then implement a bounded but real **Search MVP** for the HP Prime editor that:
- supports query entry,
- finds matches,
- supports find-next,
- moves cursor and viewport,
- provides clear user feedback,
- integrates cleanly with the existing architecture.