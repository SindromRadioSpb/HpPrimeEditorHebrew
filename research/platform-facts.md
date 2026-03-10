# HP Prime Platform Facts

**Last updated:** 2026-03-10
**Status:** Pre-spike (research phase; spikes not yet run)

---

## Hardware

| Fact | G1 | G2 | Confidence |
|---|---|---|---|
| CPU | ARM ~400 MHz | ARM Cortex-A7 @ 528 MHz | CONFIRMED |
| RAM | 32 MB | 256 MB DDR3 | CONFIRMED |
| Usable RAM (estimated) | ~16 MB | ~128 MB | CONFIRMED (estimate) |
| Flash storage | 256 MB | 512 MB | CONFIRMED |
| Screen resolution | 320 × 240 px | 320 × 240 px | CONFIRMED |
| Color format | 16-bit A1R5G5B5 | 16-bit A1R5G5B5 | CONFIRMED |
| OS | FreeRTOS variant | FreeRTOS | CONFIRMED |

## Screen Layout

- Total: 320 × 240 px
- Bottom 20 rows (220–239): HP system soft-key menu bar — **do not draw here**
- Usable programming area: **320 × 220 px** (rows 0–219)
- G0 = physical display (always 320×240)
- G1–G9 = off-screen GROBs (user-defined dimensions, RAM-limited)

## HP PPL Language

- Paradigm: procedural, Pascal-inspired
- String encoding: **UTF-16 Little Endian** (confirmed)
- String max length: **65,535 characters** (confirmed; error 38 if exceeded)
- `CHAR(n)`: converts Unicode codepoint integer to single-char string
- `ASC(s)`: returns codepoint integer of first character in string
- `MID(s, start, len)`: substring (1-based indexing)
- `POS(haystack, needle)`: substring search; returns 1-based index or 0
- `SIZE(s)` or `LENGTH(s)`: string length in characters
- `REPLACE(s, old, new)`: replace first occurrence

## Graphics API (confirmed _P / pixel-coordinate variants)

| Command | Purpose |
|---|---|
| `RECT_P(grob, x1, y1, x2, y2, edgecol, fillcol)` | Filled rectangle |
| `FILLRECT_P(grob, x1, y1, x2, y2, color)` | Fill rectangle (no border) |
| `LINE_P(x1, y1, x2, y2, color)` | Draw line |
| `TEXTOUT_P(text, grob, x, y, fontsize, textcol, width, bgcol)` | Render text |
| `BLIT_P(dst, dx1,dy1,dx2,dy2, src, sx1,sy1,sx2,sy2)` | Copy GROB region |
| `DIMGROB_P(grob, w, h, color)` | Create/resize GROB |
| `GETPIX_P(grob, x, y)` | Read pixel color |
| `SETPIX_P(grob, x, y, color)` | Write pixel color |
| `ARC_P(x, y, r, a1, a2, color)` | Draw arc/circle |
| `RGB(r, g, b)` | Create color value (0–255 each channel) |
| `RECT()` | Clear G0 to white |

## Font Sizes (TEXTOUT_P fontsize parameter)

| Code | Size |
|---|---|
| 0 | Current home setting |
| 1 | 10pt |
| 2 | 12pt |
| 3 | 14pt |
| 4 | 16pt |
| 5 | 18pt |
| 6 | 20pt |
| 7 | 22pt |

**Font selection:** None — single system font only.

## Touch Input

- `WAIT(-1)`: blocks until event; returns integer (key code) or list (touch event)
- `MOUSE()`: non-blocking; returns current touch state or -1
- `GETKEY()`: non-blocking; returns key code or -1
- `ISKEYDOWN(key)`: returns 1 if key held

### Touch event structure from WAIT(-1):
`{type, {x, y}, {dx, dy}}`

| Type | Meaning |
|---|---|
| 0 | Mouse Down |
| 1 | Mouse Move |
| 2 | Mouse Up |
| 3 | Mouse Click (tap) |
| 5 | Stretch (pinch) |
| 6 | Rotate |
| 7 | Long Click |

**Important:** A single tap generates 3 events (Down → Up → Click). Three calls to `WAIT(-1)` needed per tap.

### Physical key codes (partial):
| Code | Key |
|---|---|
| 2 | Up arrow |
| 7 | Left arrow |
| 8 | Right arrow |
| 12 | Down arrow |
| 30 | Enter |

## Persistence

- `EXPORT varname;` — global variable persists across power cycles
- Exported variables stored in flash on power-off
- App Note (`.hpappnote`) — text file per app, editable and persistent
- **No general file I/O API** (no fopen/fwrite/fread)
- CAS variables: unreliable (may clear with CAS history)

## Emulator

- **HP Prime Virtual Calculator** v2.4.15515 (released 2025-09-15)
- Platform: Windows 10+ 64-bit (free download)
- Mouse = touch input (confirmed)
- Multi-touch via mouse: UNCONFIRMED

## Character Support — UNCONFIRMED (Critical Gap)

| Block | Unicode Range | System Font Coverage |
|---|---|---|
| ASCII | U+0020–U+007E | CONFIRMED |
| Cyrillic | U+0400–U+04FF | UNCONFIRMED (probably yes) |
| Hebrew | U+0590–U+05FF | UNCONFIRMED (likely risky) |
| Hebrew combining (nikud) | U+05B0–U+05C7 | UNCONFIRMED (likely broken) |

Character browser contains 23,000+ characters — but browser inclusion ≠ TEXTOUT renderability.

**TEXTOUT direction:** Always left-to-right. No RTL parameter. No BiDi support.

## Sources

- HP Prime User Guide (official HP Inc. documentation)
- HP Prime Programming Tutorial — Edward Shore (literature.hpcalc.org)
- TI-Planet HP Prime Wiki (wiki.tiplanet.org/HP_Prime)
- HP Museum Forum (hpmuseum.org/forum)
- Cemetech HP Prime discussions
- codewalr.us HP Prime community
- holyjoe.net HP Prime reserved variables reference
- HP Prime G2 official datasheet
- hpcalc.org archive (software and documentation)
