import os
from PIL import Image
import numpy as np

# Let's inspect the exact pairs:
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png').convert('L')
arr_lp = np.array(im_lp)

# 1. Line 1: [H3] in description box
# In im_lp, line [H3] starts at Y=328 approx
# Let's print rows 325 to 355 of im_lp for X=40..75 (Latin [H3]) and X=80..130 (Arabic plain مصر)
print("=== [H3] LINE IN IM_LP (Y=325..355) ===")
for y in range(326, 352):
    lat = ''.join('#' if arr_lp[y, x] < 95 else '.' for x in range(40, 75))
    ar = ''.join('#' if arr_lp[y, x] < 95 else '.' for x in range(85, 125))
    print(f"lp Y={y:3d} (rel {y-326:2d}) | {lat} | {ar}")
