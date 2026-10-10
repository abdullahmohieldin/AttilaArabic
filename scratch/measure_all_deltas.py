import os
from PIL import Image
import numpy as np

# Load screenshots
im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# We will measure each surface carefully:
# Surface, Inferred Font, Latin Marker, Latin Baseline Y (in surface crop), Arabic Baseline Y (in surface crop)

# 1. [FT] Faction Title:
# In scratch/r2_crops/title_line_exact.png (from im_lp Y=200..250):
im_ft = Image.open('scratch/r2_crops/title_line_exact.png').convert('L')
arr_ft = np.array(im_ft)
# In arr_ft:
# Latin [FT] is at X=10..45. Base of 'F' and 'T' is at Y=18!
# Arabic body is at X=60..350. Arabic connecting baseline stroke is at Y=27..28!
# Delta Y = 28 - 18 = +10 px!

# 2. Description box lines in im_lp (scratch/r2_crops/desc_suite_1x.png):
im_desc = Image.open('scratch/r2_crops/desc_suite_1x.png').convert('L')
arr_desc = np.array(im_desc)

# Let's write a function to measure Latin baseline and Arabic baseline for a line in arr_desc:
def measure_line(arr, y_min, y_max, lat_x0, lat_x1, ar_x0, ar_x1, name):
    sub = arr[y_min:y_max, :]
    ink = sub < 95
    # Latin marker ink:
    lat_ink = ink[:, lat_x0:lat_x1]
    # In Latin marker (like [H3]), find the bottom of 'H' or '3':
    lat_rows = np.where(np.sum(lat_ink, axis=1) > 2)[0]
    # For Latin, baseline is max row of the capital letter (before bottom of bracket)
    # Let's inspect rows
    lat_base = lat_rows.max() if len(lat_rows) > 0 else 0
    
    # Arabic ink:
    ar_ink = ink[:, ar_x0:ar_x1]
    ar_rows = np.where(np.sum(ar_ink, axis=1) > 2)[0]
    ar_base = ar_rows.max() if len(ar_rows) > 0 else 0
    
    return lat_base, ar_base

print("Measuring baselines...")
