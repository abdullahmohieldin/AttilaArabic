import os
from PIL import Image
import numpy as np

# Load the full screenshots
im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

print("Loaded screenshots.")

# Let's inspect where [B1] or [B2] is:
# In TW Attila Faction Select, where is the button?
# Let's search in im_no around the bottom panel for '[B'
# Where are text pixels in im_no?
# Let's crop candidate regions:
# 1. Top tabs (Factions header)
# In im_no, top area Y=20..100, X=50..500
im_no.crop((50, 20, 500, 100)).save('scratch/r2_crops/check_factions_header.png')
im_no.crop((50, 20, 500, 100)).resize((450*4, 80*4), Image.Resampling.NEAREST).save('scratch/r2_crops/check_factions_header_4x.png')

# 2. Difficulty slider area (H1, H2, H3, D1)
# In im_no, Y=800..980, X=1300..1650
im_no.crop((1300, 800, 1650, 980)).save('scratch/r2_crops/check_difficulty_area.png')
im_no.crop((1300, 800, 1650, 980)).resize((350*4, 180*4), Image.Resampling.NEAREST).save('scratch/r2_crops/check_difficulty_area_4x.png')

# 3. Tooltip area in im_sl (T1, T2, T3)
# In im_sl, Y=650..820, X=1550..1900
im_sl.crop((1550, 650, 1900, 820)).save('scratch/r2_crops/check_tooltip_area.png')
im_sl.crop((1550, 650, 1900, 820)).resize((350*4, 170*4), Image.Resampling.NEAREST).save('scratch/r2_crops/check_tooltip_area_4x.png')

# 4. Start button: let's search where '[B' is across whole im_no
arr_no = np.array(im_no.convert('L'))
print("Searching for button...")
# Where are gold/bright buttons on dark background or text?
# Let's search Y=900..1070 across all X
for y in range(920, 1060, 20):
    for x in range(1200, 1800, 100):
        patch = arr_no[y:y+20, x:x+100]
        if np.max(patch) > 180 and np.mean(patch) < 150:
            # candidate text on dark background
            im_no.crop((x, y, x+100, y+20)).save(f'scratch/r2_crops/btn_cand_x{x}_y{y}.png')

print("Done saving checks.")
