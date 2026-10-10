import os
from PIL import Image
import numpy as np

im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# In im_lp (453x684), let's inspect horizontal bands:
# Y=0..100: Faction title area?
# Y=100..300: Leader, religion, cultural trait?
# Y=300..684: Description box?
os.makedirs('scratch/r2_crops', exist_ok=True)

# Save 4x nearest neighbor crops for precise measurement
def save_4x(im, box, name):
    crop = im.crop(box)
    w, h = crop.size
    crop_4x = crop.resize((w * 4, h * 4), Image.Resampling.NEAREST)
    crop.save(f'scratch/r2_crops/{name}_1x.png')
    crop_4x.save(f'scratch/r2_crops/{name}_4x.png')
    return crop

# Let's save slices of im_lp to find exact Y positions
for y in range(0, 680, 50):
    y_end = min(y + 60, 684)
    im_lp.crop((0, y, 453, y_end)).save(f'scratch/r2_crops/lp_band_{y:03d}.png')

print("Saved left panel bands.")

# In im_no (1920x1080), let's find:
# 1. Start Campaign button (bottom right, usually around X=1600..1880, Y=980..1050)
save_4x(im_no, (1550, 950, 1900, 1060), "btn_start_campaign")

# 2. Factions header (top left or top center tabs, usually around X=50..500, Y=20..120)
save_4x(im_no, (50, 20, 500, 120), "header_factions_tab")

# 3. Difficulty slider and labels (bottom right or middle right, around X=1300..1900, Y=800..980)
save_4x(im_no, (1300, 780, 1900, 980), "difficulty_area_no_hover")
save_4x(im_sl, (1300, 600, 1900, 980), "difficulty_area_hover")

print("Saved surface crops.")
