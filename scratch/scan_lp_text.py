import os
from PIL import Image
import numpy as np

# Let's search im_lp for all rows that have text
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')
arr_lp = np.array(im_lp.convert('L'))

# Let's search across all Y in im_lp:
# Print any Y range where there is isolated text ink
print("Scanning im_lp (height 684)...")
for y in range(0, 684, 15):
    # check strip
    strip = arr_lp[y:min(y+15, 684), 50:400]
    ink_count = np.sum(strip < 90)
    if ink_count > 50:
        # let's save a thumbnail of this strip
        im_lp.crop((30, y, 420, min(y+18, 684))).save(f'scratch/r2_crops/lp_scan_y{y:03d}.png')
        print(f"  Y={y:3d}..{min(y+15, 684):3d}: ink_count={ink_count}")
