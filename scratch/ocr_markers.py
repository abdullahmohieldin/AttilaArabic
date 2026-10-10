import os
from PIL import Image
import numpy as np

def dump_ascii(crop_path, label, thresh, is_dark_bg=True, max_w=120):
    im = Image.open(crop_path).convert('L')
    arr = np.array(im)
    if is_dark_bg:
        ink = arr > thresh
    else:
        ink = arr < thresh
        
    print(f"\n========================================================")
    print(f"ASCII DUMP: {label} (thresh={thresh}, dark_bg={is_dark_bg})")
    print(f"Size: {im.size}")
    print(f"========================================================")
    for y in range(len(arr)):
        row = ''.join('#' if ink[y, x] else '.' for x in range(min(arr.shape[1], max_w)))
        if '#' in row:
            print(f"y={y:2d} | {row}")

# 1. Factions Tab
dump_ascii('scratch/r2_crops/factions_tab_exact.png', "FACTIONS TAB", thresh=140, is_dark_bg=True)

# 2. Difficulty Area (slider label and description)
dump_ascii('scratch/r2_crops/difficulty_exact.png', "DIFFICULTY AREA", thresh=120, is_dark_bg=True)

# 3. Tooltip Area
dump_ascii('scratch/r2_crops/tooltip_exact.png', "TOOLTIP AREA", thresh=120, is_dark_bg=True)

# 4. Button Area
dump_ascii('scratch/r2_crops/btn_exact.png', "BUTTON AREA", thresh=120, is_dark_bg=True)
