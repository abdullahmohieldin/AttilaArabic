import os
from PIL import Image
import numpy as np

# Let's inspect im_lp (left panel, 453x684)
# Let's print out the active text lines and find the text in each:
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')
arr_lp = np.array(im_lp.convert('L'))

# Find text rows in im_lp (parchment: text ink < 110)
ink_lp = arr_lp < 100
row_counts = np.sum(ink_lp, axis=1)

# Find contiguous blocks of active rows (row_count > 10)
lines = []
in_line = False
start_y = 0
for y, c in enumerate(row_counts):
    if c > 15:
        if not in_line:
            in_line = True
            start_y = y
    else:
        if in_line:
            in_line = False
            if y - start_y > 4: # at least 5px height
                lines.append((start_y, y - 1))

print(f"Total lines found in left panel: {len(lines)}")
for idx, (y0, y1) in enumerate(lines):
    # Find X range of ink in this line
    line_ink = ink_lp[y0:y1+1, :]
    xs = np.where(np.sum(line_ink, axis=0) > 0)[0]
    x0, x1 = (xs.min(), xs.max()) if len(xs) > 0 else (0, 0)
    print(f"  Line {idx:2d}: Y=[{y0:3d}..{y1:3d}] (h={y1-y0+1:2d}) X=[{x0:3d}..{x1:3d}] (w={x1-x0+1:3d})")
    # Save a crop of each line
    crop = im_lp.crop((max(0, x0 - 5), max(0, y0 - 3), min(im_lp.width, x1 + 5), min(im_lp.height, y1 + 3)))
    crop_4x = crop.resize((crop.width * 4, crop.height * 4), Image.Resampling.NEAREST)
    crop.save(f'scratch/r2_crops/lp_line_{idx:02d}_1x.png')
    crop_4x.save(f'scratch/r2_crops/lp_line_{idx:02d}_4x.png')
