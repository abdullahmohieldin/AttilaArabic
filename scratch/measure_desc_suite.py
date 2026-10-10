import os
from PIL import Image
import numpy as np

im = Image.open('scratch/r2_crops/desc_suite_1x.png').convert('L')
arr = np.array(im)

# Let's inspect each line in desc_suite:
# Total height is 140px (from Y=325 to 465 in im_lp)
# There are 8 lines spaced roughly 16-18px apart:
# Line 0: Y ~ 5..20   ([H3])
# Line 1: Y ~ 20..36  ([H4])
# Line 2: Y ~ 36..52  ([H5])
# Line 3: Y ~ 52..68  ([H6])
# Line 4: Y ~ 68..84  ([H7A])
# Line 5: Y ~ 84..100 ([H7B])
# Line 6: Y ~ 100..116([H7C])
# Line 7: Y ~ 116..135([H9])

line_slices = [
    (0, 18, "[H3] Joining/Bleed"),
    (17, 34, "[H4] Kerning"),
    (33, 50, "[H5] Ink/Diacritics"),
    (49, 67, "[H6] Tall/Deep"),
    (66, 84, "[H7A] Spaces"),
    (83, 101, "[H7B] Leading Blank"),
    (100, 118, "[H7C] Inline Blank"),
    (117, 138, "[H9] Color Tag"),
]

print("=== MEASURING DESCRIPTION BOX 8-LINE SUITE ===")
for y0, y1, label in line_slices:
    slice_arr = arr[y0:y1, :]
    ink = slice_arr < 95
    # Find Latin marker (X=15..65 approx) and Arabic text (X=70..380)
    # Let's print ASCII representation of the line
    print(f"\n--- Line: {label} (Y={y0}..{y1}) ---")
    for y in range(y1 - y0):
        row_str = ''.join('#' if slice_arr[y, x] < 95 else '.' for x in range(15, 380))
        if '#' in row_str:
            print(f"  y={y:2d}: {row_str[:120]}")
