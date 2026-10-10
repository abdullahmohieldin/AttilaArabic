import os
from PIL import Image
import numpy as np

im = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')

# Let's inspect where buttons are.
# In Total War Attila Grand Campaign Faction Select screen:
# At the bottom right, there is typically a button with a checkmark or arrow or text 'START CAMPAIGN'.
# Let's check coordinates around X=1400..1600, Y=980..1060.
crop_btn = im.crop((1350, 950, 1610, 1070))
crop_btn.save('scratch/r2_crops/start_btn_area.png')

# Let's check Factions tabs at top (X=0..600, Y=0..150)
crop_top = im.crop((0, 0, 600, 150))
crop_top.save('scratch/r2_crops/top_left_area.png')

# Let's check where [H1] Hard label is:
# In difficulty area (X=1350..1610, Y=820..950)
crop_diff = im.crop((1350, 820, 1610, 950))
crop_diff.save('scratch/r2_crops/diff_area_exact.png')

print("Saved start_btn_area, top_left_area, diff_area_exact.")
