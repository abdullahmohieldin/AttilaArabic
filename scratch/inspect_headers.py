import os
from PIL import Image
import numpy as np

# 1. Factions header
im_fh = Image.open('scratch/r2_crops/check_factions_header.png').convert('L')
arr_fh = np.array(im_fh)
# Tab text is bright on dark bg
# Print rows where max > 150
print("=== FACTIONS HEADER AREA ===")
for y in range(len(arr_fh)):
    row = ''.join('#' if p > 140 else '.' for p in arr_fh[y, 10:250])
    if '#' in row:
        print(f"y={y:2d}: {row[:100]}")

# 2. Difficulty area
im_da = Image.open('scratch/r2_crops/check_difficulty_area.png').convert('L')
arr_da = np.array(im_da)
print("\n=== DIFFICULTY AREA ===")
for y in range(0, len(arr_da), 5):
    row = ''.join('#' if p > 140 else '.' for p in arr_da[y, 10:300])
    if '#' in row:
        print(f"y={y:2d}: {row[:100]}")

# 3. Tooltip area
im_tt = Image.open('scratch/r2_crops/check_tooltip_area.png').convert('L')
arr_tt = np.array(im_tt)
print("\n=== TOOLTIP AREA ===")
for y in range(0, len(arr_tt), 3):
    row = ''.join('#' if p > 140 else '.' for p in arr_tt[y, 10:300])
    if '#' in row:
        print(f"y={y:2d}: {row[:100]}")
