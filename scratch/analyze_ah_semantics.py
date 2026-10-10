import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from PIL import ImageFont
from tools.packfile import PackFile
from source.cuf import CUF
from source.cr_phase1_build import render_char_mask, calibrate_px, TAJAWAL

p = PackFile(r'extracted\local_en.copy.pack')

fonts_to_test = [
    ('la_gioconda_uppercase_18.cuf', '[FT] Faction Title (18pt uppercase)'),
    ('la_gioconda_uppercase_20.cuf', '[FT] candidate / [B1] Start Button'),
    ('la_gioconda_uppercase_22.cuf', '[FT] candidate / [B1] Start Button'),
    ('la_gioconda_18.cuf', '18pt regular'),
    ('la_gioconda_14.cuf', '[C1] Cultural / [H1] Hard label'),
    ('la_gioconda_12.cuf', 'Description Box rows [H3]-[H9] / [D1]'),
    ('la_gioconda_10.cuf', 'Tooltip [T3]'),
]

print("=== CUF VERTICAL SEMANTICS & DELTA-Y ANALYSIS ===")

for fname, desc in fonts_to_test:
    raw = p.get_file('font\\' + fname)
    c = CUF.decode(raw)
    
    lh = c.props["line_height"]
    base_prop = c.props["baseline"]
    v_size = c.props["v_size"]
    
    # Measure vanilla 'H'
    code_H = c.table[ord('H')]
    ah_H, aw_H, w_H, h_H = c.dims[code_H]
    bm_H = c.bitmaps[code_H]
    rows_H = [y for y in range(h_H) if any(bm_H[y * w_H + x] > 20 for x in range(w_H))]
    cap_h = (max(rows_H) - min(rows_H) + 1) if rows_H else h_H
    lat_ink_top = min(rows_H)
    lat_ink_bottom = max(rows_H)
    
    # Calibrate Tajawal
    px = calibrate_px(cap_h)
    font = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
    bbox_H = font.getbbox("H")
    taj_base = bbox_H[3] if bbox_H else cap_h
    
    # Test Arabic medial Baa (representing the flat connecting baseline stroke)
    ink, iw, ih, x0, y0 = render_char_mask(font, chr(0xFE90)) # Baa medial
    y_offset = (y0 + ih) - taj_base
    
    # What cr_phase1_build.py currently calculates:
    baseline_H = max(rows_H)
    ah_curr = int(baseline_H - (ih - y_offset))
    if ah_curr < 0: ah_curr = 0
    
    # Under Engine Quad placement model:
    # Top of glyph quad is placed at: y_screen = Baseline - ah (or Cell_Top + ah?)
    # Let's inspect both models:
    # Model 1: Quad Top = Baseline - ah
    #   Latin ink top = (Baseline - ah_H) + lat_ink_top
    #   Latin ink baseline = (Baseline - ah_H) + lat_ink_bottom
    #   Arabic quad top = Baseline - ah_curr
    #   Arabic ink baseline = (Baseline - ah_curr) + (ih - y_offset)
    #   Delta = Arabic baseline - Latin baseline
    #         = (Baseline - ah_curr + ih - y_offset) - (Baseline - ah_H + lat_ink_bottom)
    #         = (-ah_curr + ih - y_offset) - (-ah_H + lat_ink_bottom)
    
    # Since ah_curr = baseline_H - (ih - y_offset) = lat_ink_bottom - (ih - y_offset):
    # -ah_curr + ih - y_offset = -(lat_ink_bottom - ih + y_offset) + ih - y_offset = -lat_ink_bottom + 2*(ih - y_offset)...
    # But wait! If ah is NOT "ascent from baseline", but "offset from top of cell":
    # Let's check Model 2: Quad Top = Cell_Top + ah:
    # If Quad Top = Cell_Top + ah:
    #   Latin ah_H = 28 (or v_size). But wait, if ah_H = 28, then Latin Quad Top = Cell_Top + 28?
    #   No! In CUF: dims are (alloc_h, alloc_w, w, h).
    #   In CUF standard specs:
    #   alloc_h is usually 'bearing Y' (ascent) or 'offset Y'!
    
    delta_model1 = (-ah_curr + (ih - y_offset)) - (-ah_H + lat_ink_bottom)
    
    print(f"\nFont: {fname} ({desc})")
    print(f"  Vanilla: v_size={v_size}, baseline={base_prop}, line_height={lh}")
    print(f"  Latin 'H': ah={ah_H}, h={h_H}, ink_rows=[{lat_ink_top}..{lat_ink_bottom}] (cap={cap_h})")
    print(f"  Arabic Baa: ih={ih}, ah_curr={ah_curr}")
    print(f"  Model 1 predicted Delta-Y: {delta_model1} px")
    print(f"  Difference between ah_H and ah_curr: {ah_H - ah_curr} px")
