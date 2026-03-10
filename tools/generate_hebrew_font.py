#!/usr/bin/env python3
"""
generate_hebrew_font.py
=======================
Reproducible Hebrew bitmap font generator for HP Prime.

Output: 27 Hebrew glyphs (22 base + 5 final forms) encoded as
14x20 px, 1-bit, row-integer arrays.

Bit ordering: bit 13 (MSB of 14-bit field) = leftmost pixel.
  Row integer R: pixel at column x (0=left) = (R >> (13 - x)) & 1

Usage:
    python generate_hebrew_font.py [--font PATH] [--threshold N]
                                   [--out-ppl PATH] [--preview]

Dependencies:
    pip install Pillow

Refinement history:
  v1  Task 3: initial pipeline, scale=6, threshold=140
  v2  Task 4: larger glyphs (scale=8, size_frac=0.92, base_frac=0.83),
              better threshold=130, morphological cleanup,
              per-glyph correction framework, targeted fixes for Tav/Shin/He
"""

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Glyph set definition
# Index 0 = placeholder/space (not rendered), 1-22 = base Hebrew, 23-27 = finals
# ---------------------------------------------------------------------------

GLYPHS = [
    # idx, codepoint, name
    (0,    0x0020, "space"),
    (1,    0x05D0, "Alef"),
    (2,    0x05D1, "Bet"),
    (3,    0x05D2, "Gimel"),
    (4,    0x05D3, "Dalet"),
    (5,    0x05D4, "He"),
    (6,    0x05D5, "Vav"),
    (7,    0x05D6, "Zayin"),
    (8,    0x05D7, "Het"),
    (9,    0x05D8, "Tet"),
    (10,   0x05D9, "Yod"),
    (11,   0x05DB, "Kaf"),
    (12,   0x05DC, "Lamed"),
    (13,   0x05DE, "Mem"),
    (14,   0x05E0, "Nun"),
    (15,   0x05E1, "Samekh"),
    (16,   0x05E2, "Ayin"),
    (17,   0x05E4, "Pe"),
    (18,   0x05E6, "Tsadi"),
    (19,   0x05E7, "Qof"),
    (20,   0x05E8, "Resh"),
    (21,   0x05E9, "Shin"),
    (22,   0x05EA, "Tav"),
    # Final forms - DISTINCT glyphs, not aliases
    (23,   0x05DA, "Kaf_sofit"),
    (24,   0x05DD, "Mem_sofit"),
    (25,   0x05DF, "Nun_sofit"),
    (26,   0x05E3, "Pe_sofit"),
    (27,   0x05E5, "Tsadi_sofit"),
]

# Codepoint-to-index lookup
CP_TO_IDX = {cp: idx for (idx, cp, name) in GLYPHS}

# Cell dimensions
CELL_W = 14
CELL_H = 20

# ---------------------------------------------------------------------------
# Rendering parameters (v2 refined)
# ---------------------------------------------------------------------------
DEFAULT_SCALE     = 8      # Oversampling: render at 112x160, downsample to 14x20
DEFAULT_THRESHOLD = 130    # Binarization: pixel < threshold -> filled
SIZE_FRACTION     = 0.92   # Font pt = CELL_H * scale * SIZE_FRACTION
BASELINE_FRACTION = 0.83   # baseline_y position = rh * BASELINE_FRACTION
                           # Result: glyph body fills rows ~4-17 (14 rows)

# ---------------------------------------------------------------------------
# Per-glyph post-processing corrections (v2)
# Each entry: list of (row_1based, operation, value)
#   operation "set"  -> row[i] = value
#   operation "or"   -> row[i] |= value  (add pixels)
#   operation "and"  -> row[i] &= value  (remove pixels)
#   operation "xor"  -> row[i] ^= value  (toggle pixels)
#
# Corrections are applied AFTER auto-generation and cleanup.
# All values are 14-bit unsigned integers.
# Bit 13 = leftmost pixel (col 0), bit 0 = rightmost (col 13).
#
# Encoding helper:
#   cols_to_bits(col_list) = sum(1 << (13-c) for c in col_list)
# ---------------------------------------------------------------------------

def cols_to_bits(cols):
    """Convert list of column indices (0=left) to 14-bit row integer."""
    return sum(1 << (CELL_W - 1 - c) for c in cols)

# Precompute useful masks
FULL_ROW  = cols_to_bits(range(14))       # 16383
COLS_2_11 = cols_to_bits(range(2, 12))    # main body width
COLS_3_10 = cols_to_bits(range(3, 11))
LEFT_COL  = cols_to_bits([2, 3, 4])       # left leg mask
RIGHT_COL = cols_to_bits([9, 10, 11])     # right leg mask
MID_COL   = cols_to_bits([6, 7])          # center column

# Glyph corrections applied after auto-generation.
# Keyed by glyph index (1-27).
GLYPH_CORRECTIONS = {
    # Tav (22): Ensure BOTH feet reach the bottom rows.
    # The right foot (cols 9-11) tends to drop out in the last 2 rows.
    # Correction: force right foot pixels in rows 17-18.
    22: [
        (17, "or", cols_to_bits([9, 10])),
        (18, "or", cols_to_bits([9, 10])),
    ],

    # He (5): Reinforce the gap in the right leg at rows 16-17 to
    # distinguish from Het. He's right leg should NOT fill the bottom rows
    # continuously with the left leg.
    # Ensure rows 16-17 do NOT have left+right merged by clearing far-right
    # if auto-generation accidentally merges them.
    # Actually: ensure the gap between left (cols 2-3) and right (cols 9-11)
    # is visible in rows 16-17 by removing any stray middle pixels.
    5: [
        (16, "and", ~cols_to_bits([4, 5, 6, 7, 8]) & 0x3FFF),
        (17, "and", ~cols_to_bits([4, 5, 6, 7, 8]) & 0x3FFF),
    ],

    # Samekh (15): No correction needed.
    # The oval closes cleanly at row 16 with v2 rendering parameters.
    # Row 18 correction was removed -- it added a detached mark below the oval.
}

# ---------------------------------------------------------------------------
# Default font search paths
# ---------------------------------------------------------------------------
FONT_SEARCH = [
    "C:/Users/Win10_Game_OS/AppData/Local/Microsoft/Windows/Fonts/Heebo-Bold.ttf",
    "C:/Windows/Fonts/Heebo-Bold.ttf",
    os.path.join(os.path.dirname(__file__), "..", "assets", "Heebo-Bold.ttf"),
]


def find_font(hint=None):
    """Locate Heebo Bold. Returns path or raises FileNotFoundError."""
    candidates = ([hint] if hint else []) + FONT_SEARCH
    for p in candidates:
        if p and os.path.isfile(p):
            return p
    raise FileNotFoundError(
        "Heebo-Bold.ttf not found. Supply --font PATH or place it in assets/.\n"
        "Download from: https://fonts.google.com/specimen/Heebo"
    )


# ---------------------------------------------------------------------------
# Morphological helpers
# ---------------------------------------------------------------------------

def rows_to_grid(rows):
    """Convert list of row integers to 2D pixel grid (list of lists)."""
    return [
        [(r >> (CELL_W - 1 - x)) & 1 for x in range(CELL_W)]
        for r in rows
    ]


def grid_to_rows(grid):
    """Convert 2D pixel grid back to list of row integers."""
    result = []
    for row_pixels in grid:
        val = 0
        for x, p in enumerate(row_pixels):
            if p:
                val |= (1 << (CELL_W - 1 - x))
        result.append(val)
    return result


def remove_isolated_pixels(rows, min_neighbors=1):
    """
    Remove pixels with fewer than min_neighbors 4-connected filled neighbors.
    Removes single-pixel noise while preserving stroke structure.
    """
    h = len(rows)
    grid = rows_to_grid(rows)
    new_grid = [row[:] for row in grid]

    for y in range(h):
        for x in range(CELL_W):
            if not grid[y][x]:
                continue
            n = 0
            if y > 0 and grid[y-1][x]:   n += 1
            if y < h-1 and grid[y+1][x]: n += 1
            if x > 0 and grid[y][x-1]:   n += 1
            if x < CELL_W-1 and grid[y][x+1]: n += 1
            if n < min_neighbors:
                new_grid[y][x] = 0

    return grid_to_rows(new_grid)


def dilate_once(rows):
    """
    Dilate filled pixels by 1 step (4-connectivity).
    Use sparingly -- thickens ALL strokes uniformly.
    """
    h = len(rows)
    grid = rows_to_grid(rows)
    new_grid = [row[:] for row in grid]

    for y in range(h):
        for x in range(CELL_W):
            if grid[y][x]:
                new_grid[y][x] = 1
                if y > 0:         new_grid[y-1][x] = 1
                if y < h-1:       new_grid[y+1][x] = 1
                if x > 0:         new_grid[y][x-1] = 1
                if x < CELL_W-1:  new_grid[y][x+1] = 1

    return grid_to_rows(new_grid)


# ---------------------------------------------------------------------------
# Rasterizer
# ---------------------------------------------------------------------------

def render_glyph(font_path, codepoint, cell_w=CELL_W, cell_h=CELL_H,
                 render_scale=DEFAULT_SCALE, threshold=DEFAULT_THRESHOLD):
    """
    Render a single Unicode codepoint to a 1-bit cell_w x cell_h bitmap.

    Strategy:
      1. Render at render_scale x size on a white canvas.
      2. Lanczos-downsample to cell size.
      3. Binarize with threshold (0=bg, 1=filled).
      4. Remove isolated pixels (noise cleanup).

    Returns: list of cell_h integers, each cell_w-bit wide.
             Bit (cell_w-1) = leftmost pixel.
    """
    rw = cell_w * render_scale
    rh = cell_h * render_scale

    pt = int(cell_h * render_scale * SIZE_FRACTION)
    fnt = ImageFont.truetype(font_path, pt)

    char = chr(codepoint)

    # Measure glyph bounding box
    img_tmp = Image.new("L", (rw * 2, rh * 2), 255)
    draw_tmp = ImageDraw.Draw(img_tmp)
    bb = draw_tmp.textbbox((0, 0), char, font=fnt)
    gw = bb[2] - bb[0]
    gh = bb[3] - bb[1]

    # Center horizontally; align baseline at BASELINE_FRACTION of cell height
    baseline_y = int(rh * BASELINE_FRACTION)
    ox = (rw - gw) // 2 - bb[0]
    oy = baseline_y - bb[3]

    # Render onto white background
    img = Image.new("L", (rw, rh), 255)
    draw = ImageDraw.Draw(img)
    draw.text((ox, oy), char, font=fnt, fill=0)

    # Scale down with Lanczos
    img_small = img.resize((cell_w, cell_h), Image.LANCZOS)

    # Binarize
    rows = []
    pixels = img_small.load()
    for y in range(cell_h):
        row_val = 0
        for x in range(cell_w):
            if pixels[x, y] < threshold:
                row_val |= (1 << (cell_w - 1 - x))
        rows.append(row_val)

    # Morphological cleanup: remove isolated noise pixels
    rows = remove_isolated_pixels(rows, min_neighbors=1)

    return rows


def apply_corrections(idx, rows):
    """Apply per-glyph corrections from GLYPH_CORRECTIONS."""
    if idx not in GLYPH_CORRECTIONS:
        return rows
    corrected = rows[:]
    for (row_1based, op, value) in GLYPH_CORRECTIONS[idx]:
        r = row_1based - 1  # convert to 0-indexed
        if r < 0 or r >= len(corrected):
            continue
        if op == "set":
            corrected[r] = value & 0x3FFF
        elif op == "or":
            corrected[r] = (corrected[r] | value) & 0x3FFF
        elif op == "and":
            corrected[r] = (corrected[r] & value) & 0x3FFF
        elif op == "xor":
            corrected[r] = (corrected[r] ^ value) & 0x3FFF
    return corrected


def render_glyph_safe(font_path, codepoint, idx=0, **kwargs):
    """Render with fallback and apply per-glyph corrections."""
    try:
        rows = render_glyph(font_path, codepoint, **kwargs)
        rows = apply_corrections(idx, rows)
        if all(r == 0 for r in rows):
            print(f"  WARNING: glyph U+{codepoint:04X} rendered blank", file=sys.stderr)
        return rows
    except Exception as e:
        print(f"  ERROR: glyph U+{codepoint:04X}: {e}", file=sys.stderr)
        return [0] * kwargs.get("cell_h", CELL_H)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_glyphs(glyph_data):
    """Bounded validation: dimensions, range, non-empty, body coverage."""
    errors = []
    for idx, name, rows in glyph_data:
        if len(rows) != CELL_H:
            errors.append(f"  idx={idx} {name}: expected {CELL_H} rows, got {len(rows)}")
        for r, val in enumerate(rows):
            if val < 0 or val >= (1 << CELL_W):
                errors.append(f"  idx={idx} {name} row {r}: value {val} out of 14-bit range")
        if idx > 0 and all(v == 0 for v in rows):
            errors.append(f"  idx={idx} {name}: glyph is entirely blank")
        if idx > 0:
            filled_rows = sum(1 for v in rows if v != 0)
            if filled_rows < 6:
                errors.append(f"  idx={idx} {name}: only {filled_rows} non-empty rows (too sparse)")
    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return False
    return True


# ---------------------------------------------------------------------------
# PPL output
# ---------------------------------------------------------------------------

def emit_ppl_asset(glyph_data, cp_to_idx, out_path):
    """Write assets/hebrew_font_bitmap.ppl with embedded glyph data."""

    cp_pairs = sorted(
        [(cp, idx) for (idx, cp, name) in GLYPHS if idx > 0],
        key=lambda x: x[0]
    )
    cp_table_lines = []
    for cp, idx in cp_pairs:
        cp_table_lines.append(f"    IF cp=={cp} THEN RETURN {idx}; END;  // U+{cp:04X}")
    cp_table = "\n".join(cp_table_lines)

    glyph_count = len(glyph_data) - 1
    flat_rows = []
    for idx, name, rows in glyph_data:
        flat_rows.extend(rows)
    flat_str = ",".join(str(v) for v in flat_rows)

    ppl = f"""hebrew_font_bitmap;
#pragma mode( separator(.,;) integer(h32) )

// ================================================================
// HP Prime - Hebrew Bitmap Font Asset Module  v2 (Task 4 refined)
//
// CELL SIZE : {CELL_W} x {CELL_H} pixels
// BIT DEPTH : 1-bit (0=background, 1=filled)
// ENCODING  : Row integers - {CELL_W} bits per row, {CELL_H} rows per glyph
//             Bit {CELL_W-1} (MSB of {CELL_W}-bit field) = leftmost pixel
//             Pixel at column x (0=left): (row >> ({CELL_W-1}-x)) & 1
//
// GLYPH LAYOUT (v2 refinement):
//   Rows 1-4   : ascender space (used by Lamed only)
//   Rows 5-17  : main body (~14 rows, up from 10 in v1)
//   Rows 18-20 : descender space (used by final forms)
//
// GLYPH INDEX:
//   0       = space/blank (not drawn)
//   1-22    = Hebrew base letters (Alef..Tav)
//   23-27   = Hebrew final forms (Kaf/Mem/Nun/Pe/Tsadi sofit)
//
// STORAGE: HFB_DAT - flat PPL list, 28 glyphs x {CELL_H} rows = {28*CELL_H} integers
//   Glyph k at positions k*{CELL_H}+1 through (k+1)*{CELL_H}  [k=0..27]
//   HFB_GetRow(k, r) = HFB_DAT(k*{CELL_H} + r)  r=1..{CELL_H}
//
// API:
//   HFB_Init()               - load HFB_DAT (MUST call before rendering)
//   HFB_GlyphCount()         - 27
//   HFB_CodeToIdx(cp)        - decimal codepoint -> glyph index (0=unknown)
//   HFB_GetRow(idx, row)     - row integer for glyph rendering
//   HFB_BlitGlyph(idx,x,y)  - render glyph to screen at (x,y)
//   HFB_BlitRow(cp_list,x,y,sp) - render codepoint list LTR with spacing sp
// ================================================================


// ----------------------------------------------------------------
// GLYPH DATA - flat list, {28*CELL_H} integers
// Generated by tools/generate_hebrew_font.py v2
// Params: scale={DEFAULT_SCALE} threshold={DEFAULT_THRESHOLD} size_frac={SIZE_FRACTION} base_frac={BASELINE_FRACTION}
// ----------------------------------------------------------------
EXPORT HFB_DAT;

EXPORT HFB_Init()
BEGIN
  HFB_DAT := {{{flat_str}}};
END;


// ----------------------------------------------------------------
// HFB_GlyphCount
// ----------------------------------------------------------------
EXPORT HFB_GlyphCount()
BEGIN
  RETURN {glyph_count};
END;


// ----------------------------------------------------------------
// HFB_CodeToIdx - decimal Unicode codepoint to glyph index
// Returns 0 for unknown codepoints.
// ----------------------------------------------------------------
EXPORT HFB_CodeToIdx(cp)
BEGIN
{cp_table}
  RETURN 0;
END;


// ----------------------------------------------------------------
// HFB_GetRow - row integer for glyph idx at row r (1..{CELL_H})
// Returns 0 for out-of-range inputs.
// ----------------------------------------------------------------
EXPORT HFB_GetRow(idx, row)
BEGIN
  LOCAL base;
  IF idx < 0 OR idx > 27 THEN RETURN 0; END;
  IF row < 1 OR row > {CELL_H} THEN RETURN 0; END;
  base := idx * {CELL_H};
  RETURN HFB_DAT(base + row);
END;


// ----------------------------------------------------------------
// HFB_BlitGlyph - render glyph idx at screen pixel (x,y)
// Draws filled pixels using LINE_P(G0,...) single-pixel points.
// Background pixels are skipped (transparent).
// x,y = top-left corner of the {CELL_W}x{CELL_H} cell.
// ----------------------------------------------------------------
EXPORT HFB_BlitGlyph(idx, gx, gy)
BEGIN
  LOCAL rr, row_val, cx, bit_val, col_fg;
  LOCAL px, py;
  IF idx < 0 OR idx > 27 THEN RETURN; END;
  col_fg := RGB(0, 0, 0);
  FOR rr FROM 1 TO {CELL_H} DO
    row_val := HFB_GetRow(idx, rr);
    IF row_val <> 0 THEN
      py := gy + rr - 1;
      FOR cx FROM 0 TO {CELL_W-1} DO
        bit_val := BITAND(BITSR(row_val, {CELL_W-1} - cx), 1);
        IF bit_val THEN
          px := gx + cx;
          LINE_P(G0, px, py, px, py, col_fg);
        END;
      END;
    END;
  END;
END;


// ----------------------------------------------------------------
// HFB_BlitRow - render a list of codepoints left-to-right
// cp_list : PPL list of decimal codepoints
// x, y    : top-left of first glyph
// spacing : extra pixels between glyphs (0 = tight)
// ----------------------------------------------------------------
EXPORT HFB_BlitRow(cp_list, x, y, spacing)
BEGIN
  LOCAL nn, kk, cp, idx_g, cur_x;
  nn := SIZE(cp_list);
  cur_x := x;
  FOR kk FROM 1 TO nn DO
    cp := cp_list(kk);
    idx_g := HFB_CodeToIdx(cp);
    HFB_BlitGlyph(idx_g, cur_x, y);
    cur_x := cur_x + {CELL_W} + spacing;
  END;
END;
"""
    with open(out_path, "w", encoding="ascii") as f:
        f.write(ppl)
    print(f"Written: {out_path}")


# ---------------------------------------------------------------------------
# ASCII preview
# ---------------------------------------------------------------------------

def print_preview(glyph_data, cols_per_row=6):
    """Print all glyphs as ASCII art."""
    for start in range(0, len(glyph_data), cols_per_row):
        chunk = glyph_data[start:start + cols_per_row]
        headers = [f"[{idx:2d}] {name[:8]:8s}" for idx, name, rows in chunk]
        print("  " + "  ".join(headers))
        for row_n in range(CELL_H):
            parts = []
            for idx, name, rows in chunk:
                val = rows[row_n]
                bits = "".join("X" if (val >> (CELL_W - 1 - x)) & 1 else "." for x in range(CELL_W))
                parts.append(bits)
            print("  " + "  ".join(parts))
        print()


def print_pair_comparison(glyph_data, pairs):
    """
    Print specific glyph pairs side by side for visual comparison.
    pairs: list of (label, [idx_a, idx_b, ...])
    """
    # Build lookup dict
    data_by_idx = {idx: (name, rows) for idx, name, rows in glyph_data}

    print("=== Confusable Pair Comparison ===\n")
    for label, indices in pairs:
        chunk = [(i, data_by_idx[i][0], data_by_idx[i][1]) for i in indices if i in data_by_idx]
        headers = [f"[{idx:2d}] {name[:8]:8s}" for idx, name, rows in chunk]
        print(f"  {label}:   " + "  ".join(headers))
        for row_n in range(CELL_H):
            parts = []
            for idx, name, rows in chunk:
                val = rows[row_n]
                bits = "".join("X" if (val >> (CELL_W - 1 - x)) & 1 else "." for x in range(CELL_W))
                parts.append(bits)
            print("  " + " | ".join(parts))
        print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

CONFUSABLE_PAIRS = [
    ("Dalet/Resh",     [4, 20]),
    ("He/Het",         [5, 8]),
    ("Vav/Yod",        [6, 10]),
    ("Kaf/Bet",        [11, 2]),
    ("Kaf/KafSofit",   [11, 23]),
    ("Mem/MemSofit",   [13, 24]),
    ("Nun/NunSofit",   [14, 25]),
    ("Pe/PeSofit",     [17, 26]),
    ("Tsadi/TsadiSof", [18, 27]),
    ("Shin/Tav",       [21, 22]),
    ("Samekh/Tet/Ayn", [15, 9, 16]),
]


def main():
    parser = argparse.ArgumentParser(description="Hebrew bitmap font generator for HP Prime v2")
    parser.add_argument("--font",      default=None)
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--scale",     type=int, default=DEFAULT_SCALE)
    parser.add_argument("--out-ppl",   default=None)
    parser.add_argument("--preview",   action="store_true")
    parser.add_argument("--pairs",     action="store_true",
                        help="Print confusable pair comparison after preview")
    parser.add_argument("--no-ppl",    action="store_true")
    args = parser.parse_args()

    font_path = find_font(args.font)
    print(f"Font:   {font_path}")
    print(f"Cell:   {CELL_W}x{CELL_H}  scale={args.scale}  threshold={args.threshold}")
    print(f"Params: size_frac={SIZE_FRACTION}  baseline_frac={BASELINE_FRACTION}")
    print(f"Generating {len(GLYPHS)} glyphs...")

    glyph_data = []
    for idx, cp, name in GLYPHS:
        if idx == 0:
            rows = [0] * CELL_H
        else:
            print(f"  {idx:2d}/{len(GLYPHS)-1}  U+{cp:04X}  {name}")
            rows = render_glyph_safe(
                font_path, cp, idx=idx,
                cell_w=CELL_W, cell_h=CELL_H,
                render_scale=args.scale,
                threshold=args.threshold
            )
        glyph_data.append((idx, name, rows))

    print("\nValidating...")
    ok = validate_glyphs(glyph_data)
    print("  All glyphs passed validation." if ok else "  Validation had warnings.")

    if args.preview:
        print("\n=== Full Glyph Preview ===\n")
        print_preview(glyph_data)

    if args.pairs:
        print_pair_comparison(glyph_data, CONFUSABLE_PAIRS)

    if not args.no_ppl:
        if args.out_ppl:
            out_path = args.out_ppl
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            out_path = os.path.join(base, "assets", "hebrew_font_bitmap.ppl")
        print(f"\nEmitting PPL -> {out_path}")
        emit_ppl_asset(glyph_data, CP_TO_IDX, out_path)

    print("\nDone.")
    return glyph_data


if __name__ == "__main__":
    main()
