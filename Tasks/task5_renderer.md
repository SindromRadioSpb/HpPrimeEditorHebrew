# Claude Code Prompt — Task: Renderer MVP for HP Prime Editor
## Project: Premium Hebrew-Russian Editor for HP Prime
## Repository: `J:\Project_Vibe\HpPrimeEditor`

You are working as a senior software architect and implementation engineer on a premium-grade Hebrew-Russian editor for HP Prime.

This task is to implement the first real **renderer MVP** that connects:

- the logical document model from `text_engine`
- the Hebrew bitmap font from `hebrew_font_bitmap`
- the screen output on HP Prime

This is the first phase where the project stops being a set of isolated modules and becomes a visible editor surface.

Treat this as a serious production foundation, not a toy demo.

---

## Mission

Build a first working **renderer module** for the HP Prime editor that:

- renders visible document lines to screen,
- uses the existing text engine state,
- uses the Hebrew bitmap font for Hebrew characters,
- supports a deterministic viewport,
- renders a visible cursor,
- is stable enough to become the base for the keyboard/event-loop phase.

This task is **not yet** about full bidi or full production visual polish.

It is about building the first robust and clean rendering layer.

---

## Current Confirmed State

These components already exist and must be treated as the current foundation:

### 1. Text engine exists
There is already a logical text engine module with:
- document as list of strings,
- cursor line / cursor column,
- insertion / deletion / newline / merge / movement logic,
- basic tests.

### 2. Hebrew bitmap font exists
The current Hebrew font pipeline already provides:
- 27 Hebrew glyphs,
- 14x20 fixed-cell bitmap font,
- distinct final forms,
- generated asset module,
- visual validation test,
- API including:
  - `HFB_Init()`
  - `HFB_CodeToIdx(cp)`
  - `HFB_BlitGlyph(idx, x, y)`
  - `HFB_BlitRow(list, x, y, sp)`

### 3. Old `LINE_P` Hebrew system is deprecated
Do not use old `HEB_*` glyph functions for new renderer work.

### 4. Visual tests already exist
The font can be visually verified independently.

Use the new bitmap font as the only Hebrew rendering source.

---

## Critical Constraints

- Do **not** implement full Unicode bidi in this task.
- Do **not** tightly couple rendering logic to input handling.
- Do **not** rebuild editor logic inside the renderer.
- Do **not** regress or bypass the text engine contract.
- Do **not** use the deprecated hand-drawn Hebrew glyph path.
- Do **not** over-engineer layout beyond what is needed for MVP.

This task must produce a renderer that is:
- stable,
- modular,
- deterministic,
- ready for later keyboard/event-loop integration.

---

## Mandatory Pre-Implementation Audit

Before coding, inspect the repository:

`J:\Project_Vibe\HpPrimeEditor`

You must explicitly confirm:
- the current location and naming of the text engine module,
- the current location and naming of the bitmap font module,
- existing tests,
- any current placeholder renderer or screen drawing code,
- whether there is already a direction model or line metadata model,
- whether current docs need updating.

Also verify how the current font asset API is exposed in the actual PPL files, and do not assume names unless confirmed in repo.

If names differ from the planning docs, use the actual repo state and document the mismatch.

---

## Scope of This Task

### In scope
- renderer module MVP,
- line rendering,
- basic Hebrew-aware rendering path,
- visible cursor rendering,
- viewport rendering,
- basic line-direction handling,
- test harness for renderer,
- renderer documentation.

### Out of scope
- full bidi algorithm,
- selection rendering,
- touch keyboard UI,
- event loop,
- search UI,
- file persistence UI,
- production styling polish,
- Russian rendering finalization if not yet available.

---

## Rendering Model to Implement

You must implement a **clean renderer MVP** with the following design principle:

### Principle
The text engine stores text in **logical order**.  
The renderer is responsible for turning that logical order into screen output using a **bounded visual strategy**.

For this phase, the visual strategy should be intentionally limited and deterministic.

---

## Required Direction Strategy

For this renderer MVP, use a **line-level direction model**.

That means each line is rendered as one of:

- **LTR**
- **RTL**

Do not implement mixed-run bidi at this phase.

### Required behavior
- Hebrew lines should render in RTL mode.
- Non-Hebrew lines may render in LTR mode.
- Mixed lines may use a documented fallback rule for MVP.

### Required deliverable
You must define and document the rule used to classify or mark line direction.

Possible acceptable MVP strategies:
- explicit per-line direction array,
- heuristic “contains Hebrew => RTL”,
- test harness manual direction assignment.

But do not leave it vague.  
Document the exact behavior.

---

## Renderer Requirements

Implement and/or update the following:

### 1. `src/renderer.ppl`
Main renderer module.

### 2. `tests/test_renderer_basic.ppl`
Renderer MVP test harness.

### 3. `docs/RENDERER_PHASE1.md`
Documentation of:
- renderer contract,
- viewport model,
- line direction model,
- cursor model,
- limitations,
- deferred items.

---

## Required Renderer Responsibilities

The renderer module must at minimum handle:

### A. Initialization
- renderer initialization,
- font initialization integration,
- screen constants,
- line height,
- text area geometry,
- viewport defaults.

### B. Line rendering
Render one logical line to screen at a given `(x, y)`.

The renderer must support:
- drawing a line in LTR mode,
- drawing a line in RTL mode,
- clipping or truncation strategy if needed,
- deterministic spacing.

### C. Document rendering
Render a document viewport:
- visible lines only,
- top visible line index,
- current cursor position,
- active line awareness if needed.

### D. Cursor rendering
Render a cursor that is visible and predictable:
- inside a line,
- at line start,
- at line end,
- on empty lines.

### E. Hebrew glyph rendering
If a character maps to a Hebrew glyph:
- resolve codepoint,
- map it using `HFB_CodeToIdx(cp)`,
- render via bitmap font.

### F. Fallback rendering
You must define what happens for non-Hebrew characters in this phase.

Possible MVP options:
- render via `TEXTOUT_P`,
- render only a limited safe subset,
- use placeholder boxes for unsupported characters.

Whatever you choose, document it clearly.

---

## Required Design Decisions

You must explicitly define and document:

### 1. Viewport model
At minimum:
- `view_top_line`
- visible line count
- line height
- left/right/top/bottom bounds

### 2. Cursor model
How the logical cursor position maps to screen coordinates in:
- LTR line,
- RTL line,
- empty line,
- line end position.

### 3. Glyph spacing
How many pixels advance per Hebrew glyph in the 14x20 bitmap font.

### 4. Non-Hebrew fallback
How digits / punctuation / placeholders are rendered in this phase.

### 5. Clipping policy
What happens when a line is wider than the viewport:
- clip,
- hard truncate,
- no wrapping in MVP,
- or another clearly documented rule.

My recommendation:
- **no wrapping in MVP**
- horizontal clipping only

unless repo constraints strongly suggest otherwise.

---

## Strong Implementation Guidance

### Recommended MVP geometry
You may adapt to the actual screen mode, but keep a disciplined layout such as:
- editor area starting below a simple title/header line,
- fixed line height,
- fixed left/right padding,
- enough room for cursor visibility.

### Recommended line policy
- One rendered row per document line
- No soft wrap in MVP
- Viewport scrolling deferred to later event-loop phase, but `view_top_line` must already exist

### Recommended Hebrew rendering
For RTL lines:
- determine the visible glyph sequence
- render from the right side inward
- use fixed-cell advance

### Recommended cursor policy
For RTL:
- cursor position should still be computed from the logical column
- but the screen x position must reflect the RTL visual placement

This is the key bounded challenge of this phase.

---

## Required Test Harness

Create `tests/test_renderer_basic.ppl` or equivalent.

It must provide practical visual validation, not just a smoke call.

At minimum test these scenarios:

### Scenario 1 — Empty document
- render empty doc
- cursor visible on empty line

### Scenario 2 — LTR line
- one plain LTR line
- cursor at start / middle / end

### Scenario 3 — RTL Hebrew line
- one Hebrew line
- cursor at start / middle / end

### Scenario 4 — Multi-line document
- 4–6 lines
- mixed LTR/RTL by line
- viewport top at first line

### Scenario 5 — Final forms
- lines containing final forms
- confirm glyph mapping and display

### Scenario 6 — Mixed-content fallback
- line containing Hebrew + digits or punctuation
- verify the documented fallback behavior

### Scenario 7 — Cursor on empty line between content lines
- ensure stable cursor drawing and spacing

### Scenario 8 — Viewport slice
- document longer than visible region
- render a non-zero `view_top_line`

The test harness should make it easy to visually inspect correctness.

---

## Minimum API Expectations

You may adapt naming to repo style, but the renderer should expose a clear API such as:

- initialization function
- line render function
- document render function
- cursor render helper
- codepoint/glyph helper(s)

Possible example names:
- `REND_Init()`
- `REND_DrawLine(...)`
- `REND_DrawDocument(...)`
- `REND_DrawCursor(...)`
- `REND_LineDir(...)`
- `REND_IsHebrewCodepoint(...)`

These are examples only; choose names that match repo conventions.

---

## Mandatory Risk Review

Before implementing, explicitly address the risks below:

### 1. RTL cursor placement risk
Logical cursor vs visual position mismatch.

### 2. Mixed-line ambiguity risk
A line with Hebrew + digits/punctuation may not have a clean MVP rendering rule.

### 3. Font fallback mismatch risk
Hebrew may use bitmap font while digits/punctuation use another path, creating spacing inconsistencies.

### 4. Off-by-one cursor risk
Especially at:
- empty line,
- line start,
- line end,
- after final glyph.

### 5. Viewport clipping risk
Long lines may overflow or clip unpredictably.

### 6. Over-coupling risk
Renderer may accidentally start owning text-engine logic.

For each risk:
- mitigate,
- test,
- or explicitly defer with a documented bounded limitation.

---

## Documentation Requirements

`docs/RENDERER_PHASE1.md` must include:

### 1. Scope
What renderer MVP covers and what it does not.

### 2. Dependencies
Text engine and bitmap font modules.

### 3. Layout model
Screen regions, line height, viewport assumptions.

### 4. Direction model
How LTR/RTL is determined in this phase.

### 5. Cursor model
How cursor position is computed and rendered.

### 6. Rendering behavior
How Hebrew is rendered, how fallback is handled.

### 7. Known limitations
Especially mixed-content behavior and lack of full bidi.

### 8. Future integration
Keyboard loop, scrolling, full editor shell.

---

## Acceptance Criteria

This task is complete only if all of the following are true:

1. A renderer module exists and compiles.
2. It renders visible document lines to screen.
3. It uses the new Hebrew bitmap font for Hebrew glyphs.
4. It renders a visible cursor.
5. It supports at least line-level RTL/LTR behavior.
6. It supports a deterministic viewport start line.
7. A visual renderer test exists and is runnable.
8. The behavior is documented clearly.
9. The renderer is suitable as the base for the next keyboard/event-loop phase.

---

## Output Format

Your response must include:

### 1. Repo audit findings
What renderer-related files exist or do not exist.

### 2. Design decisions
Viewport, line direction, cursor mapping, clipping, fallback behavior.

### 3. Implementation plan
Files to create/update and what each does.

### 4. Code
Provide actual implementation code for:
- `src/renderer.ppl`
- `tests/test_renderer_basic.ppl`

and any small helper code only if truly needed.

### 5. Documentation
Provide the content for:
- `docs/RENDERER_PHASE1.md`

### 6. Test plan
How to load and run the renderer test on HP Prime.

### 7. Definition of Done
Concrete acceptance criteria.

### 8. Deferred items
Clearly list what remains for future phases.

---

## Important Engineering Behavior

- Keep the renderer modular.
- Keep the MVP bounded.
- Do not hide uncertainty.
- Prefer deterministic simplified rules over fake completeness.
- Build something stable enough for the next phase.
- Preserve the text engine as the source of truth for editing logic.
- Preserve the Hebrew bitmap font as the source of truth for Hebrew glyph rendering.

---

## Final Instruction

Start with repo audit and contract clarification.

Then implement a bounded but real **renderer MVP** that connects:
- document model,
- viewport,
- cursor,
- line-level direction,
- Hebrew bitmap font rendering.

Prioritize stability, deterministic behavior, and future integration over premature sophistication.