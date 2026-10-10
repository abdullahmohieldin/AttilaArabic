import os
from PIL import Image
import numpy as np

im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')

# Let's save 4x nearest neighbor crops of each target surface:
# 1. Faction Title [FT] (around X=340..700, Y=515..550 in full screen? Let's check where it is in im_lp)
# In R1: title was at full screen Y~521..536. In im_lp (offset Y=108), that corresponds to lp Y = 521 - 108 = 413!
# Let's check lp Y=400..450!

def save_crop_4x(im, box, name):
    c = im.crop(box)
    c.save(f'scratch/r2_crops/{name}_1x.png')
    c_4x = c.resize((c.width * 4, c.height * 4), Image.Resampling.NEAREST)
    c_4x.save(f'scratch/r2_crops/{name}_4x.png')
    return c

# Faction title area (around full Y=510..555, X=360..700)
save_crop_4x(im_no, (360, 510, 710, 555), "surface_FT")

# Cultural Trait header area (around full Y=590..635, X=360..550)
save_crop_4x(im_no, (360, 580, 560, 630), "surface_C1")

# Description box area (full Y=620..810, X=360..710)
save_crop_4x(im_no, (360, 620, 710, 810), "surface_desc_box")

# Start Campaign button (bottom right, full Y=980..1050, X=1580..1880)
save_crop_4x(im_no, (1580, 980, 1880, 1050), "surface_B1_B2")

# Factions tab header (top left, full Y=20..80, X=50..300)
save_crop_4x(im_no, (50, 20, 300, 80), "surface_F1_F2_F3")

# Difficulty area (slider, hard label, description)
# In im_no (no hover):
save_crop_4x(im_no, (1350, 830, 1900, 960), "surface_diff_no_hover")
# In im_sl (with hover on Legendary):
save_crop_4x(im_sl, (1350, 700, 1900, 960), "surface_diff_hover")

print("Saved all 4x surface crops.")
