import os
from PIL import Image
import numpy as np

# Let's inspect FACTIONS TAB (scratch/tab_inspect_1x.png)
im_tab = Image.open('scratch/tab_inspect_1x.png').convert('L')
arr_tab = np.array(im_tab)
# In tab, text is bright on dark bg
# Print rows where max > 100
print("=== FACTIONS TAB ===")
for y in range(len(arr_tab)):
    row = ''.join('#' if arr_tab[y, x] > 90 else '.' for x in range(len(arr_tab[0])))
    if '#' in row:
        print(f"y={y:2d} | {row[:100]}")

# Let's inspect TOOLTIP (scratch/tt_inspect_1x.png)
im_tt = Image.open('scratch/tt_inspect_1x.png').convert('L')
arr_tt = np.array(im_tt)
print("\n=== TOOLTIP ===")
for y in range(0, len(arr_tt), 2):
    row = ''.join('#' if arr_tt[y, x] > 100 else '.' for x in range(len(arr_tt[0])))
    if '#' in row:
        print(f"y={y:2d} | {row[:100]}")

# Let's inspect CENTER BUTTON (scratch/center_btn_1x.png)
im_cb = Image.open('scratch/center_btn_1x.png').convert('L')
arr_cb = np.array(im_cb)
print("\n=== CENTER BUTTON ===")
for y in range(0, len(arr_cb), 2):
    row = ''.join('#' if arr_cb[y, x] > 100 else '.' for x in range(len(arr_cb[0])))
    if '#' in row:
        print(f"y={y:2d} | {row[:100]}")
