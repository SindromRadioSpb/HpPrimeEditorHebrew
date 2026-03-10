# Claude Code Prompt — Task 2
## Phase 1B: Text Engine Core
## Project: Premium Hebrew-Russian Editor for HP Prime
## Repository: `J:\Project_Vibe\HpPrimeEditor`

You are working as a senior software architect and implementation engineer on a professional premium-grade editor for HP Prime.

This task is **not** about rendering polish yet.  
This task is about building the **editor core / text engine** that all later rendering, keyboard input, search, and RTL behavior will depend on.

Treat this as a **serious production-quality foundation**, not a throwaway prototype.

---

## Context Already Confirmed from Phase 0

Phase 0 spikes are complete and the following platform/runtime rules are now validated:

- Do **not** rely on global variables like `A`, `B`, `C` — they are unsafe / reserved in HP Prime contexts.
- Use explicit `LOCAL` variables.
- `LOCAL i; FOR i FROM ...` works.
- For substring search in strings, use:
  - `INSTRING(str, substr)`
  and **not** `POS(str, substr)`.
- Do **not** use `L0–L9` as the document storage model.
- Use:
  - `LOCAL doc`
  where `doc` is a list of strings.
- Basic local-list document operations are now validated:
  - create list,
  - access element,
  - search in element,
  - grow list to 200 lines,
  - modify line,
  - merge/delete via rebuild.
- GROB rendering feasibility has already been separately validated, but this task is **not** about glyph implementation yet.

These facts are no longer assumptions.  
Use them as constraints.

---

## Mission

Design and implement the initial **text engine core** for the HP Prime Hebrew-Russian editor.

The text engine must become the stable logical foundation for:

- document storage,
- cursor movement,
- insertion,
- deletion,
- line split/merge,
- viewport-oriented editing later,
- renderer integration later,
- search integration later,
- future mixed RTL/LTR visual logic later.

At this phase, prioritize **correct logical editing behavior** over visual sophistication.

---

## Critical Rules

- Do **not** jump ahead into full RTL rendering.
- Do **not** couple editor logic to screen drawing more than necessary.
- Do **not** hard-wire text engine logic into UI code.
- Do **not** guess HP Prime semantics where a smaller validated helper can remove uncertainty.
- Keep the engine **modular, testable, and deterministic**.
- Separate:
  - logical text model
  - cursor model
  - editor operations
  - debug/test harness

This phase should produce a solid core that later renderer and keyboard modules can call.

---

## Mandatory Pre-Implementation Audit

Before writing code, inspect the repository and confirm the current state of:

`J:\Project_Vibe\HpPrimeEditor`

Specifically verify:
- current directory structure,
- whether `src/` already exists,
- whether there are any Phase 0 artifacts that should be referenced,
- whether docs need updating alongside implementation,
- whether a test harness file already exists or should be created now.

Also review existing planning docs from Task 1 and ensure the implementation matches the documented architecture direction.

If implementation details conflict with the existing plan, surface that conflict explicitly.

---

## Scope of This Task

This task is for the **logical editor core only**.

### In scope
- document model,
- cursor model,
- text insertion,
- character insertion,
- backspace,
- delete,
- newline / split line,
- line merge,
- cursor movement,
- safe boundary behavior,
- helper functions for line read/write,
- debug/test harness,
- documentation for the engine contract.

### Out of scope for this task
- final Hebrew glyph drawing,
- final mixed-direction visual layout,
- full bidi algorithm,
- touch keyboard UI,
- production renderer,
- file persistence UI,
- search panel UI,
- selection model unless you explicitly define it as deferred.

---

## Architecture Goal

Implement a clean logical engine that stores text in **logical order**, independent of future visual rendering order.

That means:
- the text engine should not try to visually reverse Hebrew,
- the engine should not implement full bidi,
- the engine should preserve inserted text in consistent logical storage,
- later rendering layers may choose how to display a line.

This is essential to keep the core stable.

---

## Required Deliverables

Produce and/or update the following:

### 1. `src/text_engine.ppl`
Main editor core module.

### 2. `tests/` or `spikes/` test harness file
A runnable validation program for editor operations.
Suggested name:
- `tests/test_text_engine_basic.ppl`
or equivalent if project conventions differ.

### 3. Documentation update
Create or update a doc such as:
- `docs/TEXT_ENGINE_PHASE1.md`

Document:
- the engine state model,
- function contracts,
- known limitations,
- deferred features,
- Phase 1 acceptance criteria.

---

## Required Engine Design

The engine must define a stable editor state.

At minimum, include a state model equivalent to:

- `doc` — list of strings
- `cur_line` — 1-based current line index
- `cur_col` — 1-based logical cursor column, or clearly documented equivalent
- optional viewport state if useful, but keep it minimal unless justified

You must explicitly define:
- whether cursor is 1-based or 0-based,
- how cursor-at-end-of-line is represented,
- how empty lines behave,
- how insertions at start / middle / end behave,
- how backspace behaves at column 1,
- how delete behaves at end of line,
- how newline splits a line,
- how cursor moves across line boundaries.

Use one consistent contract and document it clearly.

---

## Required Functions

Implement a practical initial function set.  
You may adapt names if HP Prime style or file organization requires it, but keep the API clean and documented.

Minimum required functionality:

### Initialization / state
- initialize empty document
- initialize from list of strings
- get current state
- reset state if needed

### Access helpers
- get line count
- get line text
- set line text
- clamp cursor to valid bounds

### Editing operations
- insert character
- insert text
- backspace
- delete char
- newline / split current line

### Cursor movement
- move left
- move right
- move up
- move down
- move to line start
- move to line end

### Optional but strongly recommended
- insert at explicit position helper
- split-line helper
- merge-with-next helper
- merge-with-previous helper
- safe substring helper(s) if HP Prime string slicing needs containment

---

## Behavior Requirements

### Document model
Use:
- `LOCAL doc`
where `doc` is a list of strings.

Do not use `L0-L9`.

### Cursor semantics
You must define consistent logical semantics.  
A good default is:

- `cur_line` in range `1..SIZE(doc)`
- `cur_col` in range `1..(LEN(line)+1)`

where `LEN(line)+1` represents the caret position just after the last character.

If you choose a different contract, justify it clearly.

### Backspace
Must support:
- delete previous character inside a line
- if at start of a non-first line: merge current line into previous line and move cursor appropriately
- if at start of first line: no-op safely

### Delete
Must support:
- delete current character inside a line
- if at end of line and not last line: merge next line into current line
- if at end of last line: no-op safely

### Newline
Must:
- split current line at cursor position
- keep text before cursor on current line
- move text after cursor to new line
- place cursor at start of new line

### Move left / right
Must safely cross line boundaries:
- left at column 1 moves to previous line end if previous line exists
- right at end moves to next line start if next line exists

### Move up / down
Must preserve preferred horizontal position as reasonably as possible, or explicitly defer that feature and document the simpler behavior.

If preferred-column preservation is deferred, say so explicitly and implement a deterministic simpler rule.

---

## String Handling Discipline

Because HP Prime string/list behavior can be tricky, you must be conservative and explicit.

- Avoid risky shorthand if helper functions make behavior clearer.
- Use validated string operations.
- If substring extraction is needed, implement tiny helper wrappers and test them.
- Do not assume unsupported string APIs.

If string slicing semantics are uncertain, create tiny validated helpers first and reuse them.

---

## Mandatory Risk-Control Section in the Output

Before implementation, explicitly identify all remaining risks relevant to this phase, including:

- string slicing assumptions,
- cursor off-by-one risks,
- line merge edge cases,
- empty-line behavior,
- document with one line only,
- very short vs very long lines,
- consistency between logical state and future renderer expectations.

If something is still uncertain, implement a bounded helper test instead of burying the risk.

---

## Testing Requirements

You must create a runnable validation harness for this phase.

It must exercise at least the following scenarios:

### Scenario 1 — Empty document init
- initialize empty doc
- verify line count
- verify cursor position

### Scenario 2 — Insert chars into empty line
- insert characters one by one
- verify final line content
- verify cursor position

### Scenario 3 — Mid-line insertion
- start with a line like `ABEF`
- place cursor between `B` and `E`
- insert `CD`
- verify result becomes `ABCDEF`

### Scenario 4 — Newline split
- split a line in the middle
- verify two lines created correctly
- verify cursor moved correctly

### Scenario 5 — Backspace inside line
- remove one char from middle
- verify line content and cursor

### Scenario 6 — Backspace at line start
- merge current line into previous
- verify line count decreases
- verify merged text is correct
- verify cursor lands correctly

### Scenario 7 — Delete inside line
- remove current char
- verify result

### Scenario 8 — Delete at line end
- merge next line into current
- verify result

### Scenario 9 — Move across boundaries
- move left from start of line
- move right from end of line
- verify cross-line behavior

### Scenario 10 — Up/down movement
- verify deterministic behavior across lines of different lengths

### Scenario 11 — Hebrew/Russian/mixed logical storage smoke
Use example lines containing:
- Hebrew,
- Russian,
- digits,
- punctuation.

Do not validate full visual bidi here.  
Only validate that logical storage and editing operations do not corrupt the text.

Suggested examples:
- `שלום`
- `привет`
- `שלום 123`
- `иврит: שלום`
- `abc שלום 123 привет`

### Scenario 12 — 200-line stability smoke
- initialize/grow document to 200 lines
- perform a few edits near beginning, middle, and end
- confirm no crash and state remains consistent

---

## Output / Reporting Format

Your response must include:

### 1. Repo audit findings
- current relevant files/folders,
- what exists already,
- what is missing,
- what docs are referenced.

### 2. Design decisions
- document model,
- cursor model,
- logical storage contract,
- deferred behavior.

### 3. Implementation plan
- files to create/update,
- exact responsibilities per file,
- sequence of implementation.

### 4. Code
Provide the actual implementation code for:
- `src/text_engine.ppl`
- test harness file
- any helper file if truly needed

### 5. Test plan
- manual run steps,
- what outputs should be expected,
- edge cases covered.

### 6. Definition of Done
Concrete acceptance criteria for Phase 1B.

### 7. Deferred items
Clearly list what is intentionally postponed to later phases.

---

## Coding Discipline

- Use explicit `LOCAL` declarations.
- Avoid reserved/global shorthand variable names.
- Prefer readable, bounded helper functions over clever compact code.
- Keep module boundaries clean.
- Add concise comments where they reduce ambiguity.
- Do not over-engineer beyond this phase.

---

## Important Design Constraint

This engine is the foundation for a **premium editor** under severe platform constraints.

Therefore:
- correctness first,
- deterministic behavior first,
- stable contracts first,
- visual sophistication later.

Do not let renderer concerns contaminate the text-engine contract.

---

## Final Instruction

Start with repo audit and contract clarification, then implement the engine and test harness.

If any HP Prime language behavior needed by the engine is still uncertain, first isolate it in a tiny validated helper test before building on top of it.

Do not hide uncertainty.  
Do not skip edge cases.  
Do not assume that because a behavior feels editor-like, it is already validated on HP Prime.

Build the smallest correct text engine that can become the stable core for later RTL-aware rendering.