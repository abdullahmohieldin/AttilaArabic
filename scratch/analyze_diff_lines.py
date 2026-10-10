import os
from PIL import Image
import numpy as np

# Let's inspect the 4x images:
# scratch/r2_crops/diff_full_4x.png
# scratch/r2_crops/tt_full_4x.png
# scratch/r2_crops/tab_full_4x.png
# scratch/r2_crops/cb_full_4x.png

# Let's find out what text is in diff_full (X=1350..1620, Y=820..950 in im_no):
# In im_no, difficulty slider has:
# - Label for difficulty: [H1] or [H2] or [H3]
# - Description: [D1]
im_diff = Image.open('scratch/r2_crops/diff_full.png').convert('L')
arr_diff = np.array(im_diff)
# Let's find rows with text ink
# In the difficulty panel, background is parchment (bright) or dark?
print("im_diff shape:", arr_diff.shape, "mean:", arr_diff.mean(), "min:", arr_diff.min(), "max:", arr_diff.max())
# Find where ink is: text ink < 100
ink_diff = arr_diff < 100
row_sums = np.sum(ink_diff, axis=1)
for y, s in enumerate(row_sums):
    if s > 10:
        # print snippet
        xs = np.where(ink_diff[y, :])[0]
        line = ''.join('#' if ink_diff[y, x] else '.' for x in range(xs.min(), min(xs.min()+100, arr_diff.shape[1])))
        print(f"diff y={y:2d} (x={xs.min():3d}..{xs.max():3d}): {line[:80]}")
