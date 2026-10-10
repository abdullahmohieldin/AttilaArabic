import os
from PIL import Image
import numpy as np

im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# Let's search for where the markers are:
# In im_lp, we know where [FT] is (Y ~ 225..240 in lp).
# Let's find [C1] in im_lp:
# Cultural trait is usually around Y=450..550 in full screen, or in lp?
# Let's search lp for '[C1]'
# An opening bracket '[' has a vertical bar of 1-2px, top bar of 3-4px, bottom bar of 3-4px.
# Let's print out all rows of im_lp where text appears and search for '['

def find_brackets(im, name, thresh=100, is_dark_bg=False):
    arr = np.array(im.convert('L'))
    h, w = arr.shape
    if is_dark_bg:
        ink = arr > thresh
    else:
        ink = arr < thresh
        
    print(f"\n--- Searching for '[' in {name} ---")
    # A '[' at typical sizes (10-24pt) has:
    # height 10 to 25px, width 3 to 6px
    # vertical stroke of width 1-2px, top horizontal of 2-4px, bottom horizontal of 2-4px.
    # Let's template match '['
    # We can take '[' from the known [FT] line!
    ft_crop = Image.open('scratch/r2_crops/title_line_exact.png').convert('L')
    arr_ft = np.array(ft_crop)
    # in title_line_exact, '[' is at X=10..15, Y=4..23 (height ~20px)
    bracket_patch = (arr_ft[4:24, 10:16] < 100).astype(float)
    bh, bw = bracket_patch.shape
    
    matches = []
    for y in range(0, h - bh, 2):
        for x in range(0, w - bw, 2):
            patch = ink[y:y+bh, x:x+bw].astype(float)
            score = np.sum(patch * bracket_patch) / np.sum(bracket_patch)
            if score > 0.75:
                matches.append((x, y, score))
    print(f"Found {len(matches)} candidate bracket matches.")
    # Cluster matches
    clusters = []
    for m in matches:
        if not any(abs(m[0]-c[0]) < 10 and abs(m[1]-c[1]) < 10 for c in clusters):
            clusters.append(m)
    for c in clusters:
        print(f"  Match at X={c[0]}, Y={c[1]}, score={c[2]:.2f}")
        # Save a 100x40 crop around match
        crop = im.crop((max(0, c[0]-10), max(0, c[1]-5), min(w, c[0]+150), min(h, c[1]+35)))
        crop.save(f'scratch/r2_crops/match_{name}_x{c[0]}_y{c[1]}.png')

find_brackets(im_lp, "left_panel")
find_brackets(im_no, "no_hover_dark", thresh=140, is_dark_bg=True)
find_brackets(im_no, "no_hover_light", thresh=100, is_dark_bg=False)
find_brackets(im_sl, "slider_hover", thresh=140, is_dark_bg=True)
