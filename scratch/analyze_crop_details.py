import os
from PIL import Image
import numpy as np

# Let's inspect each crop in scratch/r2_crops/
# 1. surface_FT
im_ft = Image.open('scratch/r2_crops/surface_FT_1x.png')
print("FT size:", im_ft.size)
# 2. surface_C1
im_c1 = Image.open('scratch/r2_crops/surface_C1_1x.png')
print("C1 size:", im_c1.size)
# 3. surface_B1_B2
im_b = Image.open('scratch/r2_crops/surface_B1_B2_1x.png')
print("B size:", im_b.size)
# 4. surface_F1_F2_F3
im_f = Image.open('scratch/r2_crops/surface_F1_F2_F3_1x.png')
print("F size:", im_f.size)
# 5. surface_diff_no_hover
im_d = Image.open('scratch/r2_crops/surface_diff_no_hover_1x.png')
print("Diff size:", im_d.size)
# 6. surface_diff_hover
im_dh = Image.open('scratch/r2_crops/surface_diff_hover_1x.png')
print("Diff hover size:", im_dh.size)
# 7. surface_desc_box
im_desc = Image.open('scratch/r2_crops/surface_desc_box_1x.png')
print("Desc box size:", im_desc.size)
