# Claude Code Prompt — Task 1
## Project: Premium Hebrew-Russian Editor for HP Prime
## Repository: `J:\Project_Vibe\HpPrimeEditor`

You are working as a senior software architect and implementation planner for a professional premium-grade application.

Your task is to produce a **deep planning package** for building from scratch a **full-featured Hebrew-Russian text editor with high-quality RTL rendering and mixed-direction text handling** for **HP Prime**.

This is **not** a toy prototype and **not** a quick demo.  
Treat it as a **serious premium product** with strict engineering discipline, explicit risk control, high implementation realism, and detailed delivery planning.

---

## Mission

Create a planning and architecture package for a **professional Hebrew-Russian editor** running on **HP Prime**, with:

- high-quality Hebrew RTL text support,
- mixed Hebrew/Russian/numbers/punctuation text,
- virtual on-screen keyboard optimized for touch,
- text editing operations,
- search,
- premium UX expectations,
- bounded performance and memory expectations for HP Prime,
- realistic implementation strategy in HP PPL,
- fallback strategies where platform limitations are severe.

The final output must be suitable as the basis for actual implementation work in the repository:

`J:\Project_Vibe\HpPrimeEditor`

---

## Critical Operating Rules

Before proposing architecture or implementation steps, you must first do a **full discovery and validation pass**.

You must **not** guess.  
You must **not** hand-wave platform constraints.  
You must **not** leave major ambiguities unresolved.  
You must **not** produce a shallow or generic plan.

You must first verify all relevant assumptions through:
1. repository inspection,
2. official documentation,
3. reliable internet sources,
4. community knowledge where official documentation is incomplete,
5. explicit identification of unknowns, contradictions, and risky assumptions.

If something is uncertain, you must label it clearly and reduce risk by:
- finding stronger evidence,
- proposing validation spikes,
- defining decision gates,
- defining fallback paths.

---

## Mandatory Discovery Phase

Before planning, you must thoroughly review **all necessary documentation and references**, including but not limited to:

### A. Platform / language / device documentation
- HP Prime programming model
- HP PPL capabilities and limitations
- graphics APIs, drawing primitives, touch input, event handling
- text rendering capabilities
- string support and encoding limitations
- memory/storage constraints
- app/program lifecycle
- persistence/file/storage options if any
- performance constraints for redraw-heavy UI

### B. Rendering / text-system topics
- RTL rendering fundamentals
- bidi / mixed-direction text handling
- cursor movement semantics in mixed-direction text
- logical text order vs visual order
- Hebrew punctuation / numerals / brackets in mixed text
- line breaking / wrapping implications for RTL + LTR
- font/rendering constraints on HP Prime
- custom glyph rendering feasibility if native support is insufficient

### C. Existing ecosystem / references
- official HP Prime docs
- official manuals
- trusted forum discussions
- example HP Prime text/graphics/touch projects
- any relevant community examples for keyboard UIs, text widgets, custom rendering, or editor-like behavior

### D. Repository discovery
Inspect the repository root:

`J:\Project_Vibe\HpPrimeEditor`

Since the project is created from scratch, verify and document:
- current repo state,
- missing scaffolding,
- recommended initial structure,
- docs that must exist before implementation starts,
- whether build/run/test conventions need to be established from zero.

---

## Preconditions Checklist

You must explicitly verify whether the following preconditions are satisfied **before implementation planning is considered valid**:

1. Clear target runtime confirmed:
   - real HP Prime hardware,
   - emulator,
   - or both.

2. Target language/runtime confirmed:
   - HP PPL only,
   - or any allowed auxiliary assets/tools for code generation/preprocessing.

3. Text rendering strategy feasibility checked:
   - native rendering,
   - custom rendering,
   - hybrid rendering.

4. Character support feasibility checked:
   - Hebrew letters,
   - Russian/Cyrillic letters,
   - punctuation,
   - digits,
   - brackets,
   - whitespace behavior.

5. RTL/mixed-text behavior feasibility checked:
   - insertion,
   - deletion,
   - cursor navigation,
   - line wrapping,
   - searching.

6. Touch UI feasibility checked:
   - touch hit testing,
   - screen partitioning,
   - keyboard layout switching,
   - responsiveness.

7. Persistence feasibility checked:
   - how documents are stored and reloaded.

8. Performance feasibility checked:
   - expected document size bounds,
   - redraw cost,
   - search cost,
   - memory cost.

9. Testability feasibility checked:
   - what can be tested on emulator,
   - what must be verified on real device.

10. Unknowns / blockers / hard platform limits explicitly listed.

If any precondition is missing, uncertain, or contradicted by sources, you must stop and elevate it as a planning risk.

---

## Blind-Spot Elimination Requirement

Your planning must actively search for and eliminate blind spots.

Specifically, identify:
- anything described too vaguely,
- any hidden dependency,
- any platform assumption that might fail on real hardware,
- any area where “simple editor” assumptions break once mixed RTL/LTR text is introduced,
- any mismatch between ideal product goals and HP Prime constraints.

You must explicitly include a section:

## Blind Spots / Ambiguities / Shallowly-Specified Areas

For each item provide:
- what is underspecified,
- why it is dangerous,
- what evidence is missing,
- how to resolve it,
- whether a spike/prototype is required,
- whether scope reduction or fallback is needed.

---

## Product Intent

Treat the product as a **premium professional application**, not a student exercise.

That means the plan must consider:
- architecture cleanliness,
- maintainability,
- deterministic behavior,
- UI consistency,
- predictable editing semantics,
- resilience under platform limits,
- bounded complexity,
- staged rollout,
- premium-grade documentation,
- evidence-based decisions.

This does **not** mean pretending the platform is more capable than it is.  
Premium quality here means **serious engineering under constraints**.

---

## Planning Deliverables Required

Produce a structured planning package with the following sections.

# 1. Repo Audit Findings
Document:
- current repository state,
- discovered constraints,
- relevant docs/sources reviewed,
- confirmed platform capabilities,
- confirmed platform limits,
- critical feasibility conclusions,
- major risks discovered during research.

# 2. Problem Framing
Define clearly:
- what “full-featured Hebrew-Russian editor” means on HP Prime,
- what is in scope,
- what is not in scope,
- which “desktop-grade” expectations are impossible or unsafe to promise.

# 3. Product Requirements
Define functional requirements, including at minimum:
- text buffer model,
- Hebrew input,
- Russian input,
- mixed text input,
- virtual keyboard,
- navigation,
- editing operations,
- search,
- selection support or explicit deferral,
- persistence,
- document open/save model,
- viewport scrolling,
- line wrapping model,
- status bar / mode indicators,
- error states.

Also define non-functional requirements:
- responsiveness,
- maximum acceptable latency,
- memory limits,
- redraw budget,
- UX consistency,
- recoverability,
- maintainability.

# 4. Technical Feasibility Assessment
Provide a brutally honest assessment of:
- what is definitely feasible,
- what is probably feasible,
- what is risky,
- what is likely impossible or too expensive,
- what requires proof-of-concept before commitment.

# 5. Rendering Architecture Options
Compare at least 3 architecture approaches, for example:
- native text rendering first,
- custom visual rendering with logical text storage,
- hybrid/fallback model.

For each option include:
- pros,
- cons,
- HP Prime constraints,
- implementation cost,
- UX quality,
- RTL quality,
- mixed-text quality,
- risk level,
- recommendation.

# 6. Recommended Architecture
Select one recommended architecture and justify it rigorously.

Include:
- document model,
- line model,
- logical vs visual text representation,
- cursor model,
- viewport model,
- virtual keyboard subsystem,
- search subsystem,
- persistence subsystem,
- rendering loop,
- event handling model.

# 7. Text Engine Design
Design the editor core:
- logical storage format,
- insertion/deletion rules,
- cursor semantics,
- movement rules for mixed RTL/LTR text,
- line wrapping strategy,
- search strategy,
- normalization assumptions if any,
- punctuation/bracket behavior assumptions,
- how mixed runs are represented.

Be explicit about what will be “true bidi”, what will be approximated, and what will be intentionally simplified.

# 8. UI/UX Architecture
Design the screen layout:
- editor area,
- virtual keyboard area,
- status bar,
- language switchers,
- touch target sizing,
- paging/scroll controls,
- mode indicators,
- search UI,
- dialog flows.

Include premium UX constraints:
- no cramped interactions,
- clear touch hit areas,
- consistent navigation,
- readable visual hierarchy,
- low redraw flicker,
- deterministic behavior.

# 9. Risk Register
Create a serious risk register with:
- risk ID,
- description,
- likelihood,
- impact,
- detection method,
- mitigation,
- fallback.

This must include at least:
- encoding/rendering risk,
- RTL visual correctness risk,
- mixed-direction cursor/navigation risk,
- memory exhaustion risk,
- slow redraw risk,
- touch UX risk,
- persistence corruption/data-loss risk,
- emulator vs device mismatch risk.

# 10. Proof-of-Concept / Spike Plan
Define the minimum validation spikes that must be built before full implementation.

Examples:
- glyph rendering feasibility spike,
- touch keyboard spike,
- mixed-direction cursor spike,
- search-on-buffer spike,
- document-size stress spike.

For each spike include:
- purpose,
- exact success criteria,
- failure criteria,
- decision impact.

# 11. Phased Implementation Plan
Break implementation into phases with explicit gates.

For each phase include:
- objective,
- files/modules/docs to create,
- implementation tasks,
- test tasks,
- exit criteria,
- rollback/fallback if phase fails.

Do not jump directly into full implementation.  
Sequence the work so the hardest uncertainties are retired early.

# 12. Repository Bootstrap Plan
Since the repo is new, propose initial repo structure, for example:
- docs/
- research/
- src/
- spikes/
- tests/
- assets/
- runbooks/

Adjust structure appropriately for HP Prime project realities.

Specify:
- required initial markdown documents,
- research evidence files,
- architecture decision records if helpful,
- coding conventions,
- naming conventions,
- how to store spike results.

# 13. Test Strategy
Define:
- manual tests,
- emulator tests,
- real-device tests,
- regression checklist,
- performance checks,
- rendering verification cases,
- mixed-text edge-case matrix.

Include example test strings combining:
- Hebrew,
- Russian,
- numbers,
- punctuation,
- parentheses,
- spaces,
- mixed runs.

# 14. Definition of Done
Provide a realistic DoD for:
- MVP,
- beta,
- premium-ready release candidate.

# 15. Open Questions
List all unresolved items that remain after research, with:
- why unresolved,
- blocking level,
- next action needed.

# 16. Final Recommendation
Conclude with a direct answer:
- whether the premium vision is realistically achievable on HP Prime,
- which subset is safe to commit to first,
- which features should be deferred,
- what the best execution path is.

---

## Required Research Discipline

You must explicitly cite or summarize the evidence behind important claims from:
- official documentation,
- trusted sources,
- observed repository state,
- prototype evidence if produced.

If multiple sources disagree, note the disagreement and reduce risk accordingly.

Do not assume that because something is theoretically possible in a scripting environment, it is product-viable on real HP Prime hardware.

---

## Implementation Planning Standard

Your planning must be:
- detailed,
- production-oriented,
- honest,
- bounded,
- risk-aware,
- repo-specific,
- evidence-driven.

Avoid vague phrases like:
- “should be straightforward”
- “can likely be done”
- “just implement”
- “simply use RTL”
unless they are backed by validated evidence.

---

## Output Format

Write the result as a professional planning document in clean markdown.

Use this exact top-level structure:

1. Repo audit findings  
2. Problem framing  
3. Product requirements  
4. Technical feasibility assessment  
5. Rendering architecture options  
6. Recommended architecture  
7. Text engine design  
8. UI/UX architecture  
9. Risk register  
10. Proof-of-concept / spike plan  
11. Phased implementation plan  
12. Repository bootstrap plan  
13. Test strategy  
14. Definition of Done  
15. Blind spots / ambiguities / shallowly-specified areas  
16. Open questions  
17. Final recommendation  

---

## Additional Strict Instructions

- Start by inspecting the repository and researching the platform thoroughly.
- Verify all preconditions before planning.
- Minimize risk from shallowly-mentioned areas.
- Surface contradictions early.
- Do not hide uncertainty.
- Do not compress hard problems into optimistic wording.
- Prefer evidence and validation gates over assumptions.
- Treat this as a premium engineering effort under severe platform constraints.
- If the target vision is partially unrealistic, say so clearly and recommend a staged scope.