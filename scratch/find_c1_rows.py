import os
from PIL import Image
import numpy as np

# Load screenshots
im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# Helper to find text baselines and print ASCII art
def inspect_text_strip(im, box, name, thresh=100, is_dark_bg=False):
    crop = im.crop(box)
    arr = np.array(crop.convert('L'))
    if is_dark_bg:
        ink = arr > thresh
    else:
        ink = arr < thresh
    print(f"\n========================================================")
    print(f"SURFACE: {name} | Box: {box} | Size: {crop.size}")
    print(f"========================================================")
    
    # Save 4x
    crop_4x = crop.resize((crop.width * 4, crop.height * 4), Image.Resampling.NEAREST)
    crop.save(f'scratch/r2_crops/{name}_1x.png')
    crop_4x.save(f'scratch/r2_crops/{name}_4x.png')
    return crop, arr, ink

# 1. Cultural Trait [C1]: In im_lp around Y=290..340
# In im_lp, let's find the exact Y where [C1] is
arr_lp = np.array(im_lp.convert('L'))
for y in range(290, 360):
    row_str = ''.join('#' if p < 100 else '.' for p in arr_lp[y, 20:250])
    if '#' in row_str:
        print(f"lp Y={y:3d} (full Y={y+108:3d}): {row_str[:80]}")
