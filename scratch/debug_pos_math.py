import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from PIL import ImageFont
from tools.packfile import PackFile
from source.cuf import CUF
from source.cr_phase1_build import render_char_mask, calibrate_px, TAJAWAL

p = PackFile(r'extracted\local_en.copy.pack')
for fname in ['la_gioconda_18.cuf', 'la_gioconda_uppercase_18.cuf', 'la_gioconda_12.cuf']:
    c = CUF.decode(p.get_file('font\\' + fname))
    code_H = c.table[ord('H')]
    ah_H, aw_H, w_H, h_H = c.dims[code_H]
    bm_H = c.bitmaps[code_H]
    rows_H = [y for y in range(h_H) if any(bm_H[y * w_H + x] > 20 for x in range(w_H))]
    cap_h = (max(rows_H) - min(rows_H) + 1) if rows_H else h_H
    baseline_H = max(rows_H) if rows_H else c.props['baseline']
    
    px = calibrate_px(cap_h)
    font = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
    bbox_H = font.getbbox('H')
    taj_base = bbox_H[3] if bbox_H else cap_h
    
    print(f'=== {fname} ===')
    lh = c.props["line_height"]
    base = c.props["baseline"]
    v_size = c.props["v_size"]
    print(f'  vanilla props: line_height={lh}, baseline={base}, v_size={v_size}')
    print(f'  H dims: ah={ah_H}, aw={aw_H}, w={w_H}, h={h_H}')
    print(f'  rows_H: min={min(rows_H)}, max={max(rows_H)}, cap_h={cap_h}, baseline_H={baseline_H}')
    print(f'  Tajawal px={px}, bbox_H={bbox_H}, taj_base={taj_base}')
    
    # Test for standard Arabic letter Baa / Seen / Meem
    for ch_name, ch in [('Baa medial (U+FE90)', chr(0xFE90)), ('Seen medial (U+FEB4)', chr(0xFEB4)), ('Alef isolated (U+FE8D)', chr(0xFE8D))]:
        ink, iw, ih, x0, y0 = render_char_mask(font, ch)
        y_offset = (y0 + ih) - taj_base
        ah = int(baseline_H - (ih - y_offset))
        print(f'    {ch_name}: iw={iw}, ih={ih}, x0={x0}, y0={y0}')
        print(f'      y_offset={y_offset}, ah={ah}, bottom (ah+ih)={ah+ih}')
