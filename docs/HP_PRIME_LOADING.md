# HP_PRIME_LOADING.md
## HP Prime — Loading PPL Programs: Critical Format Rules

**Project:** HP Prime Hebrew-Russian Editor
**Status:** Permanent reference — update if new issues are discovered

---

## CRITICAL: Module Name Line Rule

Every `.ppl` source file begins with a module name declaration:

```
editor_shell;
#pragma mode( separator(.,;) integer(h32) )
...
```

**This first line (`module_name;`) behaves differently depending on how you load the file:**

---

### Method A: HP Connectivity Kit (.hpprgm import)

**Include the module name line.**

When loading via HP Prime Connectivity Kit (drag-and-drop or sync), the `.hpprgm` container format requires the module name as the first line. HP Prime parses it correctly.

Files: `src/*.ppl` (canonical source, WITH module name)

---

### Method B: Manual paste into HP Prime built-in editor

**DO NOT include the module name line.**

When pasting code directly into the HP Prime program editor (typing/pasting into the CAS editor or program editor), the module name line (`editor_shell;`) must be **omitted**. If it is present:

- HP Prime parses it as a statement (a semicolon expression)
- This can corrupt the parser state
- Errors appear later — typically on a distant EXPORT declaration — **not** on the module name line itself
- The error message is misleading: it looks like `EXPORT some_function()` is wrong, when in fact the root cause is the module name line at the very top

**Files in `hpprgm/*.txt` are pre-stripped for manual paste use.**

They begin directly with:
```
#pragma mode( separator(.,;) integer(h32) )
```

---

## File Layout

```
src/*.ppl           Source of truth. WITH module name (Method A).
hpprgm/*.txt        Manual-paste copies. WITHOUT module name (Method B).
```

When updating a module, always regenerate the corresponding `.txt` file with the first line removed.

**Shell command to generate a correct `.txt` from a `.ppl`:**
```bash
tail -n +2 src/module_name.ppl > hpprgm/module_name.txt
```

---

## Module Load Order on HP Prime

All four modules must be loaded (via either method) in this order:

```
1. hebrew_font_bitmap   (font asset and blit functions)
2. text_engine          (document model and editing operations)
3. renderer             (screen rendering, uses font + doc)
4. editor_shell         (interactive shell, uses all above)
```

If a module is missing or out of order, you will see "Undefined name" errors at runtime.

---

## Confirmed Symptom Reference

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| Syntax error on a late EXPORT after manual paste | Module name line included in manual paste | Remove first line before pasting |
| "Undefined name: HFB_Init" at runtime | `hebrew_font_bitmap` not loaded | Load it first |
| "Undefined name: TE_Init" at runtime | `text_engine` not loaded | Load before `renderer` |
| "Undefined name: REND_Init" at runtime | `renderer` not loaded | Load before `editor_shell` |
| Program exits immediately with no error | `FREEZE` used — HP Prime bug with EXPORT helpers | Replace with `ev := WAIT(-1)` |
| Touch tap causes 3 events | HP Prime: Down + Up + Click per tap | Handle only Down (ev(1)==0) |

---

## #pragma Line

Always keep this line as the **first line** in manual-paste files (after removing the module name):

```
#pragma mode( separator(.,;) integer(h32) )
```

This sets:
- `.` and `;` as separators (not `,` and `:`)
- `integer(h32)` — 32-bit integer mode

Without this line, operators and separators may be interpreted differently.

---

## History

This issue was discovered and documented during Task 6 (editor_shell).
Prior occurrences: Task 3 (hebrew_font_bitmap), Task 5 (renderer).
The `FREEZE` vs `WAIT(-1)` issue was separately discovered in Task 4.
