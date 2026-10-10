import os
from PIL import Image
import numpy as np

# Load R2 left panel
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')
w, h = im_lp.size

os.makedirs('scratch/r2_slices', exist_ok=True)

# Save 10 slices of im_lp (each ~70px high)
for i in range(0, h, 60):
    i_end = min(i + 70, h)
    slice_img = im_lp.crop((0, i, w, i_end))
    slice_img.save(f'scratch/r2_slices/slice_{i:03d}_{i_end:03d}.png')

print("Saved slices.")
