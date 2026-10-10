import os
from PIL import Image
import numpy as np

# Load crops
# 1. [FT] Faction Title (title_line_exact.png)
# 2. [C1] Cultural Trait (cult_line1.png or lp_cultural_area.png)
# 3. [H1] Hard Label (diff_full.png)
# 4. [D1] Difficulty Desc (diff_full.png)
# 5. [B1] Start Campaign Button (if visible)
# 6. [F2] Factions Header (tab_full.png)
# 7. [T3] Tooltip (legendary_tooltip.png)
# 8. Description box rows [H3], [H4], [H5], [H6], [H7A], [H7B], [H7C], [H9] (desc_suite_1x.png)

im_ft = Image.open('scratch/r2_crops/title_line_exact.png').convert('L')
arr_ft = np.array(im_ft)
# In title_line_exact: Latin baseline = 18, Arabic baseline = 28 -> delta = +10px

im_desc = Image.open('scratch/r2_crops/desc_suite_1x.png').convert('L')
arr_desc = np.array(im_desc)

line_coords = [
    ("[H3] (Line 1: Joining/Bleed)", 0, 18, 15, 65, 70, 360, "la_gioconda_12"),
    ("[H4] (Line 2: Kerning Pair)", 17, 34, 15, 65, 70, 360, "la_gioconda_12"),
    ("[H5] (Line 3: Solid/Gray/Diacritics)", 33, 50, 15, 65, 70, 360, "la_gioconda_12"),
    ("[H6] (Line 4: Tall Alef/Deep Yeh)", 49, 67, 15, 65, 70, 360, "la_gioconda_12"),
    ("[H7A] (Line 5: Leading Spaces)", 66, 84, 15, 80, 85, 360, "la_gioconda_12"),
    ("[H7B] (Line 6: Leading Blank 40px)", 83, 101, 55, 120, 125, 360, "la_gioconda_12"),
    ("[H7C] (Line 7: Inline Blank 40px)", 100, 118, 15, 80, 85, 360, "la_gioconda_12"),
    ("[H9] (Line 8: Yellow Color Tag)", 117, 138, 15, 65, 70, 360, "la_gioconda_12"),
]

print("=== MEASURING DESCRIPTION BOX ROWS ===")
desc_results = []
for label, y0, y1, lx0, lx1, ax0, ax1, font_name in line_coords:
    sub = arr_desc[y0:y1, :]
    lat_ink = sub[:, lx0:lx1] < 95
    ar_ink = sub[:, ax0:ax1] < 95
    
    # In Latin marker, find base of 'H' or digits
    # Capital 'H' has its base at max ink row of the letter (before lower bracket tip)
    lat_rows = np.where(np.sum(lat_ink, axis=1) > 2)[0]
    ar_rows = np.where(np.sum(ar_ink, axis=1) > 2)[0]
    
    # For Latin, capital letter baseline is typically lat_rows[lat_rows < lat_rows.max() - 1].max() if bracket dips 1-2px below
    lat_base = lat_rows.max() - 1 if len(lat_rows) > 0 else 0
    # For Arabic, body connecting stroke is at the main horizontal density peak
    ar_densities = np.sum(ar_ink, axis=1)
    ar_base = np.argmax(ar_densities) if len(ar_rows) > 0 else 0
    delta = ar_base - lat_base
    desc_results.append((label, font_name, lat_base, ar_base, delta))
    print(f"{label:35s} | Lat base={lat_base:2d}, Ar base={ar_base:2d} | Delta-Y = {delta:+2d} px")

# Check [H1] Hard label in diff_full
im_diff = Image.open('scratch/r2_crops/diff_full.png').convert('L')
arr_diff = np.array(im_diff)
# Hard label is around y=63..75, x=95..180
sub_h1 = arr_diff[60:85, 90:200]
lat_h1 = sub_h1[:, :45] < 90
ar_h1 = sub_h1[:, 50:] < 90
lat_rows_h1 = np.where(np.sum(lat_h1, axis=1) > 2)[0]
ar_rows_h1 = np.where(np.sum(ar_h1, axis=1) > 2)[0]
lat_base_h1 = lat_rows_h1.max() - 1
ar_base_h1 = np.argmax(np.sum(ar_h1, axis=1))
delta_h1 = ar_base_h1 - lat_base_h1
print(f"\n[H1] Hard Label (la_gioconda_14)    | Lat base={lat_base_h1:2d}, Ar base={ar_base_h1:2d} | Delta-Y = {delta_h1:+2d} px")

# Check [FT] Title
lat_base_ft = 18 # bottom of 'F' and 'T'
ar_base_ft = 28  # horizontal stroke of Arabic
delta_ft = ar_base_ft - lat_base_ft
print(f"[FT] Faction Title (la_gioconda_uppercase_18) | Lat base={lat_base_ft:2d}, Ar base={ar_base_ft:2d} | Delta-Y = {delta_ft:+2d} px")

# Check [T3] Tooltip in legendary_tooltip
im_tt = Image.open('scratch/r2_crops/legendary_tooltip.png').convert('L')
arr_tt = np.array(im_tt)
# [T3] is at y=15..28, x=190..290
sub_tt = arr_tt[12:30, 190:350]
lat_tt = sub_tt[:, :45] > 140
ar_tt = sub_tt[:, 50:] > 140
lat_rows_tt = np.where(np.sum(lat_tt, axis=1) > 2)[0]
ar_rows_tt = np.where(np.sum(ar_tt, axis=1) > 2)[0]
lat_base_tt = lat_rows_tt.max() - 1
ar_base_tt = np.argmax(np.sum(ar_tt, axis=1))
delta_tt = ar_base_tt - lat_base_tt
print(f"[T3] Tooltip Title (la_gioconda_10) | Lat base={lat_base_tt:2d}, Ar base={ar_base_tt:2d} | Delta-Y = {delta_tt:+2d} px")
