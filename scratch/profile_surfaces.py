import os
from PIL import Image
import numpy as np

# Let's inspect each image with horizontal profile / ink detection
# On parchment / UI buttons, text is dark ink (luminance < 100 or 120), or on dark UI (like button / tab) it might be light/gold/white ink!
# Let's analyze surface by surface.

def analyze_surface(name, img_path, is_dark_bg=False):
    im = Image.open(img_path)
    arr = np.array(im.convert('L'))
    h, w = arr.shape
    print(f"\n=== Analyzing {name} ({w}x{h}) ===")
    print(f"Luminance range: [{arr.min()}..{arr.max()}], mean={arr.mean():.1f}")
    
    # If dark bg (like button/tooltip/tab), text ink is bright (e.g. > 150)
    # If light bg (like parchment), text ink is dark (e.g. < 100)
    if is_dark_bg or arr.mean() < 100:
        ink_mask = arr > 140
    else:
        ink_mask = arr < 100
        
    # Row ink sums
    row_sums = np.sum(ink_mask, axis=1)
    active_rows = np.where(row_sums > 5)[0]
    if len(active_rows) > 0:
        print(f"Active ink rows: Y=[{active_rows.min()}..{active_rows.max()}]")
        # Find local peaks / clusters in active rows
        diffs = np.diff(active_rows)
        splits = np.where(diffs > 3)[0]
        row_ranges = []
        start = active_rows[0]
        for s in splits:
            row_ranges.append((start, active_rows[s]))
            start = active_rows[s+1]
        row_ranges.append((start, active_rows[-1]))
        for r_start, r_end in row_ranges:
            print(f"  Line band: Y=[{r_start}..{r_end}] (height {r_end - r_start + 1}px)")
    else:
        print("No active ink rows found with default threshold.")

analyze_surface("FT (Faction Title)", "scratch/r2_crops/surface_FT_1x.png")
analyze_surface("C1 (Cultural Trait)", "scratch/r2_crops/surface_C1_1x.png")
analyze_surface("B1/B2 (Button)", "scratch/r2_crops/surface_B1_B2_1x.png", is_dark_bg=True)
analyze_surface("F1/F2/F3 (Factions Tab)", "scratch/r2_crops/surface_F1_F2_F3_1x.png", is_dark_bg=True)
analyze_surface("Diff Area (No Hover)", "scratch/r2_crops/surface_diff_no_hover_1x.png")
analyze_surface("Diff Area (Hover)", "scratch/r2_crops/surface_diff_hover_1x.png", is_dark_bg=True)
analyze_surface("Desc Box", "scratch/r2_crops/surface_desc_box_1x.png")
