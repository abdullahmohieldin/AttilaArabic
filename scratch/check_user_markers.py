import os
from PIL import Image
import numpy as np

# Load screenshots
im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# In Round 2, the user stated in the prompt:
# "By eye, on every surface the Arabic sits roughly 10-12 px LOWER than the Latin marker on the same string ([FT], [F2], [B1], [H1], [D1], [C1], and every description-box row)."
# NOTICE THIS:
# The user specifically named:
# [FT], [F2], [B1], [H1], [D1], [C1]!
# The user saw [FT], [F2], [B1], [H1], [D1], [C1] with their own eyes on screen!
# Let's locate the exact coordinates where the user saw each of [FT], [F2], [B1], [H1], [D1], [C1]!

print("User observed: [FT], [F2], [B1], [H1], [D1], [C1]!")
