# Claude Code Prompt — Editor UX Phase 2
## Project: Premium Hebrew-Russian Editor for HP Prime
## Repository: `J:\Project_Vibe\HpPrimeEditor`

You are working as a senior software architect and product-focused implementation planner on a premium-grade Hebrew-Russian editor for HP Prime.

This task is **not** to implement one isolated patch.
This task is to define, document, and structure the next major product phase:

**Editor UX Phase 2**

This phase comes after:
- text engine,
- Hebrew bitmap font,
- renderer MVP,
- interactive editor shell MVP.

The editor is already interactive, but the UX and feature surface are still at an early MVP stage.  
The goal of this task is to formalize the next product phase in a serious, engineering-driven way.

---

## Mission

Produce a structured **Phase 2 product/engineering plan** for improving the editor UX and expanding the editor’s practical capabilities.

The output must serve as a stable documentation anchor for the next development phase.

This phase must cover the likely next directions:

1. keyboard UX improvements,
2. mixed-text behavior improvements,
3. basic editor commands and document actions,
4. document search,
5. viewport and navigation improvements.

Do not treat them as random feature ideas.  
Treat them as a coherent next-phase roadmap.

---

## Required Goal of Phase 2

The purpose of Editor UX Phase 2 is to move the project from:

- “interactive technical editor MVP”

toward:

- “usable editor with practical workflows”

without overreaching into a full desktop-class editor.

Phase 2 should improve:
- usability,
- discoverability,
- editing efficiency,
- text legibility in realistic use,
- navigation,
- task completion flow,
- readiness for future Russian support.

---

## Mandatory Pre-Planning Audit

Before planning, inspect the repository:

`J:\Project_Vibe\HpPrimeEditor`

You must explicitly review the current state of:
- `text_engine`
- bitmap Hebrew font module
- renderer
- editor shell
- current tests
- current docs
- current HP Prime loader copies
- any existing keyboard layout logic
- any existing search or document command scaffolding

Do not assume the current state from memory.  
Verify what already exists and what is still missing.

Document any mismatch between prior planning docs and actual repo state.

---

## Scope of This Phase Plan

This task is about **planning and documentation**, not necessarily implementing everything now.

You must define:
- what belongs in Phase 2,
- what should be prioritized,
- what should be deferred,
- what dependencies exist,
- what should be grouped together,
- what should be split into separate tasks.

---

## Required Phase-2 Focus Areas

You must explicitly address all of the following areas.

### 1. Keyboard UX improvement
Examples:
- better key layout,
- multi-page keyboard if needed,
- punctuation page,
- improved control layout,
- preparation for future Russian layout,
- better key grouping and labeling,
- more usable tap targets or state transitions.

### 2. Mixed-text improvement
Examples:
- Hebrew + digits,
- Hebrew + punctuation,
- later Hebrew + Russian,
- reduced fallback ugliness,
- better visual behavior for practical mixed lines.

### 3. Basic editor commands / user functions
Examples:
- new / clear document,
- open / save workflow,
- simple commands,
- status line,
- minimal command surface.

### 4. Search
Examples:
- search mode,
- find next,
- cursor jump to match,
- viewport update on match,
- minimal search UI.

### 5. Viewport and navigation
Examples:
- better long-document behavior,
- jump actions,
- better vertical navigation,
- preferred-column handling,
- more practical movement in bigger documents.

---

## Required Planning Deliverables

Your response must produce a structured Phase 2 document containing:

### 1. Repo audit findings
Current implementation state relevant to Phase 2.

### 2. Problem framing
What is still weak in the current editor UX and why Phase 2 is needed.

### 3. Phase 2 goals
What this phase is meant to achieve.

### 4. Candidate workstreams
A structured breakdown of:
- keyboard UX,
- mixed text,
- basic editor commands,
- search,
- viewport/navigation.

### 5. Recommended prioritization
A recommended order of implementation with justification.

### 6. Dependencies
What depends on what.

### 7. Risk review
What can go wrong if these areas are implemented in the wrong order or coupled too tightly.

### 8. Recommended task breakdown
How Phase 2 should be split into concrete development tasks.

### 9. Suggested milestones
Examples:
- Search MVP
- Keyboard UX Upgrade
- Mixed Text Refinement
- Basic Commands MVP
- Navigation Upgrade

### 10. Definition of Done for Phase 2
What would count as meaningful completion of this phase.

### 11. Deferred items
What should explicitly remain out of scope for now.

---

## Important Product Reasoning Requirement

Do not simply list all possible features.

You must decide:
- which direction brings the biggest practical gain first,
- which direction has the lowest architecture risk,
- which direction is best as the immediate next implementation phase,
- which direction should wait.

You must make explicit recommendations.

---

## Recommended Prioritization Logic

Use practical product logic, not arbitrary ordering.

You should seriously evaluate:
- search as a high-value low-risk feature,
- keyboard UX as a usability multiplier,
- mixed text as a higher-risk rendering refinement,
- editor commands as practical but dependent on shell maturity,
- navigation improvements as important but possibly partly polish-oriented.

If your recommendation differs, justify it clearly.

---

## Required Output Format

Write the result as a professional markdown phase-planning document with the following top-level structure:

1. Repo audit findings  
2. Current UX limitations  
3. Phase 2 goals  
4. Candidate workstreams  
5. Recommended prioritization  
6. Dependencies and sequencing  
7. Risk review  
8. Recommended task breakdown  
9. Suggested milestones  
10. Definition of Done  
11. Deferred items  
12. Final recommendation  

---

## Engineering and Product Constraints

- Keep recommendations bounded for HP Prime realities.
- Do not assume desktop-class resources.
- Do not promise full bidi or full file-management sophistication unless justified.
- Do not collapse all workstreams into one giant task.
- Prefer modular progression and testable increments.

---

## Final Instruction

Produce a serious, engineering-grounded documentation package for **Editor UX Phase 2**.

This document should act as the authoritative planning anchor for the next stage of the project and should clearly identify the best immediate next task to implement.