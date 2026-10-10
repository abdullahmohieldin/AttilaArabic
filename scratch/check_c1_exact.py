import os
from PIL import Image
import numpy as np

im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# Let's search each screenshot for text matching:
# We know:
# - [FT] is SEEN in im_lp (and im_no) at Y=525..550 (lp Y=225..240)
# - [H1] is SEEN in im_no at Y=885..910 (diff panel)
# - [T3] is SEEN in im_sl at Y=410..430 (legendary tooltip)
# - Description box markers: [H3], [H4], [H5], [H6], [H7A], [H7B], [H7C], [H9] are all SEEN in im_lp (Y=325..465)

# Now what about:
# [B1], [B2] (Start Campaign button)
# [F1], [F2], [F3] (Factions header)
# [T1], [T2] (Difficulty tooltip handles)
# [H2], [H3] (Other Hard labels)
# [D1] (Difficulty description)
# [C1] (Cultural trait header)

# Let's write targeted checks for each:

# 1. Cultural trait header [C1]:
# In im_lp, cultural trait section is at Y=280..325.
# Let's print out ASCII of Y=280..325 in im_lp:
print("=== CHECKING [C1] IN IM_LP (Y=280..325) ===")
arr_lp = np.array(im_lp.convert('L'))
for y in range(280, 325):
    row = ''.join('#' if arr_lp[y, x] < 90 else '.' for x in range(30, 200))
    if '#' in row:
        print(f"y={y:3d} | {row}")
