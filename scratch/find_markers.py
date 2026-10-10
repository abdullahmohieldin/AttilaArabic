import os
from PIL import Image
import numpy as np

# Let's inspect im_lp (left panel) in detail:
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')
print("im_lp size:", im_lp.size)

# Let's print out text presence in bands:
# We know the description box in left panel has 8 lines:
# [H3], [H4], [H5], [H6], [H7A], [H7B], [H7C], [H9]
# And above it: Faction title [FT] and Cultural trait [C1]!

# Let's write a script to crop specific suspected sub-regions:
# Faction title: top of left panel?
im_lp.crop((0, 0, 453, 50)).save('scratch/r2_crops/lp_00_50.png')
im_lp.crop((0, 50, 453, 100)).save('scratch/r2_crops/lp_50_100.png')
im_lp.crop((0, 100, 453, 200)).save('scratch/r2_crops/lp_100_200.png')
im_lp.crop((0, 200, 453, 350)).save('scratch/r2_crops/lp_200_350.png')
im_lp.crop((0, 350, 453, 500)).save('scratch/r2_crops/lp_350_500.png')
im_lp.crop((0, 500, 453, 684)).save('scratch/r2_crops/lp_500_684.png')

# Let's also check where left panel is located in im_no (1920x1080):
im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
# Find where im_lp template matches in im_no
arr_lp = np.array(im_lp.convert('L'))
arr_no = np.array(im_no.convert('L'))

# Sample a 50x50 patch from im_lp (e.g. from row 100 to 150, col 100 to 150)
patch = arr_lp[100:150, 100:150]
# Find match in arr_no
h_lp, w_lp = im_lp.size[1], im_lp.size[0]
best_err = 1e9
best_pos = (0, 0)

# Check search area around X=300..450, Y=150..350
for y in range(150, 400):
    for x in range(300, 500):
        err = np.mean(np.abs(arr_no[y:y+50, x:x+50].astype(int) - patch.astype(int)))
        if err < best_err:
            best_err = err
            best_pos = (x - 100, y - 100)

print(f"im_lp matches at full-screen coords: X={best_pos[0]}, Y={best_pos[1]}, err={best_err}")
