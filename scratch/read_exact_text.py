import os
from PIL import Image
import numpy as np

# Let's inspect cult_line1:
im_c1 = Image.open('scratch/r2_crops/cult_line1.png').convert('L')
arr_c1 = np.array(im_c1)
print("=== CULTURAL LINE 1 ===")
for y in range(len(arr_c1)):
    row = ''.join('#' if arr_c1[y, x] < 90 else '.' for x in range(len(arr_c1[0])))
    if '#' in row:
        print(f"y={y:2d} | {row[:100]}")

# Let's inspect diff_full:
im_d = Image.open('scratch/r2_crops/diff_full.png').convert('L')
arr_d = np.array(im_d)
print("\n=== DIFFICULTY FULL ===")
# In diff_full, where are the lines of text?
# Let's print out lines of ink < 90 (or > 120 if dark)
for y in range(0, len(arr_d), 2):
    row_dark = ''.join('#' if arr_d[y, x] < 90 else '.' for x in range(len(arr_d[0])))
    row_bright = ''.join('#' if arr_d[y, x] > 140 else '.' for x in range(len(arr_d[0])))
    if '#' in row_dark:
        print(f"y={y:2d} (dark)   | {row_dark[:100]}")
    if '#' in row_bright:
        print(f"y={y:2d} (bright) | {row_bright[:100]}")
