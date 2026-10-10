import os
from PIL import Image
import numpy as np

# Load left panel
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# In R1:
# - Title bar was at crop Y ~ 215..230 (full Y ~ 521..536)
# - Faction Leader was at crop Y ~ 238
# - Cultural Trait was at crop Y ~ 300..320
# - Description box was at crop Y ~ 330..530
# Let's inspect these exact Y regions in im_lp:

# 1. Faction Title region in im_lp:
# Let's check Y=200..250
im_lp.crop((20, 200, 430, 250)).save('scratch/r2_crops/lp_title_area.png')
# 4x
im_lp.crop((20, 200, 430, 250)).resize(((410)*4, 50*4), Image.Resampling.NEAREST).save('scratch/r2_crops/lp_title_area_4x.png')

# 2. Cultural Trait region in im_lp:
# Let's check Y=290..340
im_lp.crop((20, 290, 430, 340)).save('scratch/r2_crops/lp_cultural_area.png')
im_lp.crop((20, 290, 430, 340)).resize(((410)*4, 50*4), Image.Resampling.NEAREST).save('scratch/r2_crops/lp_cultural_area_4x.png')

# 3. Description box in im_lp:
# Let's check Y=330..550
im_lp.crop((20, 330, 430, 550)).save('scratch/r2_crops/lp_desc_box.png')
im_lp.crop((20, 330, 430, 550)).resize(((410)*4, 220*4), Image.Resampling.NEAREST).save('scratch/r2_crops/lp_desc_box_4x.png')

print("Saved title, cultural, and desc_box crops.")
