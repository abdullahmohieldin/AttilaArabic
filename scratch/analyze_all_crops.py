import os
from PIL import Image
import numpy as np

def analyze_crop(img_path, name):
    im = Image.open(img_path)
    arr = np.array(im.convert('L'))
    h, w = arr.shape
    print(f"\n========================================================")
    print(f"ANALYZE: {name} ({w}x{h})")
    print(f"========================================================")
    
    # Try different thresholds to find text
    best_thresh = 0
    best_var = 0
    # Search threshold
    for t in [40, 60, 80, 100, 120, 140, 160, 180]:
        mask = arr < t if arr.mean() > 100 else arr > t
        row_counts = np.sum(mask, axis=1)
        var = np.std(row_counts)
        if var > best_var:
            best_var = var
            best_thresh = t
            
    is_dark = arr.mean() <= 100
    mask = arr > best_thresh if is_dark else arr < best_thresh
    row_counts = np.sum(mask, axis=1)
    
    # Print rows where row_counts > 5
    for y in range(h):
        if row_counts[y] > 5:
            xs = np.where(mask[y, :])[0]
            # print snippet of text
            chars = ''.join('#' if mask[y, x] else '.' for x in range(xs.min(), xs.max()+1))
            if len(chars) > 80: chars = chars[:80] + '...'
            print(f"y={y:2d} (x={xs.min():3d}..{xs.max():3d}): {chars}")

analyze_crop('scratch/tab_inspect_1x.png', "FACTIONS TAB")
analyze_crop('scratch/diff_inspect_1x.png', "DIFFICULTY AREA")
analyze_crop('scratch/tt_inspect_1x.png', "TOOLTIP")
analyze_crop('scratch/center_btn_1x.png', "CENTER BUTTON")
analyze_crop('scratch/cult_inspect_1x.png', "CULTURAL TRAIT")
analyze_crop('scratch/r2_crops/lp_title_area.png', "FACTION TITLE")
