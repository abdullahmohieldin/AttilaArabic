import os
from PIL import Image
import numpy as np

# 1. Factions Tab
im = Image.open('scratch/tab_inspect_1x.png')
print("Tab size:", im.size)
# 2. Difficulty Area
im_diff = Image.open('scratch/diff_inspect_1x.png')
print("Diff size:", im_diff.size)
# 3. Tooltip Area
im_tt = Image.open('scratch/tt_inspect_1x.png')
print("Tooltip size:", im_tt.size)
# 4. Center Button
im_cb = Image.open('scratch/center_btn_1x.png')
print("Center btn size:", im_cb.size)
# 5. Bottom Right Button
im_br = Image.open('scratch/br_btn_1x.png')
print("BR btn size:", im_br.size)
# 6. Cultural Area
im_cult = Image.open('scratch/cult_inspect_1x.png')
print("Cultural size:", im_cult.size)

def dump_lines(im, name, is_dark_bg=False, thresh=110):
    arr = np.array(im.convert('L'))
    h, w = arr.shape
    if is_dark_bg:
        ink = arr > thresh
    else:
        ink = arr < thresh
    print(f"\n========================================================")
    print(f"SURFACE: {name} ({w}x{h}) | is_dark_bg={is_dark_bg}, thresh={thresh}")
    print(f"========================================================")
    
    # Active rows
    row_sums = np.sum(ink, axis=1)
    for y in range(h):
        if row_sums[y] > 5:
            # print ascii representation
            row_chars = ''.join('#' if ink[y, x] else '.' for x in range(w))
            # find first and last ink
            xs = np.where(ink[y, :])[0]
            print(f"y={y:2d} (x={xs.min():3d}..{xs.max():3d}): {row_chars[xs.min():xs.max()+1][:100]}")

dump_lines(im, "FACTIONS TAB", is_dark_bg=True, thresh=100)
dump_lines(im_diff, "DIFFICULTY AREA", is_dark_bg=False, thresh=100)
dump_lines(im_tt, "TOOLTIP", is_dark_bg=True, thresh=120)
dump_lines(im_cb, "CENTER BUTTON", is_dark_bg=True, thresh=120)
dump_lines(im_br, "BR BUTTON", is_dark_bg=True, thresh=100)
dump_lines(im_cult, "CULTURAL AREA", is_dark_bg=False, thresh=100)
