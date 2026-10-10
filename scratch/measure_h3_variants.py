import os
from PIL import Image
import numpy as np

# Load desc_suite
im_desc = Image.open('scratch/r2_crops/desc_suite_1x.png').convert('L')
arr = np.array(im_desc)

# Line 1 is Y=0..20 in desc_suite_1x
# Let's crop Y=0..25, X=50..380
h3_crop = arr[0:25, 50:380]
# Save 4x
h3_img = Image.fromarray(h3_crop)
h3_img.save('scratch/r2_crops/h3_line_1x.png')
h3_img.resize((h3_img.width * 4, h3_img.height * 4), Image.Resampling.NEAREST).save('scratch/r2_crops/h3_line_4x.png')

# Let's inspect the baseline row of the Arabic text in h3_crop:
# We know earlier that the Arabic baseline stroke sits at lp Y=338..342 (which is rel Y=13..17 in h3_crop)!
print("=== H3 LINE BASELINE ROWS (rel Y=10..20) ===")
for y in range(10, 20):
    row = ''.join('#' if h3_crop[y, x] < 95 else '.' for x in range(len(h3_crop[0])))
    if '#' in row:
        print(f"y={y:2d} | {row[:150]}")
