import os
from PIL import Image
import numpy as np

# Let's inspect where markers are in each crop and measure their pixel coordinates.

def measure_marker_and_arabic(crop_path, crop_name, latin_x_range, arabic_x_range, y_search_range, is_dark_bg=False):
    im = Image.open(crop_path)
    arr = np.array(im.convert('L'))
    
    # Text ink threshold
    if is_dark_bg or arr.mean() < 100:
        ink = arr > 120
    else:
        ink = arr < 100
        
    # Slices for Latin marker and Arabic body
    latin_slice = ink[y_search_range[0]:y_search_range[1], latin_x_range[0]:latin_x_range[1]]
    arabic_slice = ink[y_search_range[0]:y_search_range[1], arabic_x_range[0]:arabic_x_range[1]]
    
    # Find row sums in each
    lat_rows = np.where(np.sum(latin_slice, axis=1) > 2)[0]
    arab_rows = np.where(np.sum(arabic_slice, axis=1) > 2)[0]
    
    lat_min_y = y_search_range[0] + lat_rows.min() if len(lat_rows) > 0 else None
    lat_max_y = y_search_range[0] + lat_rows.max() if len(lat_rows) > 0 else None
    
    arab_min_y = y_search_range[0] + arab_rows.min() if len(arab_rows) > 0 else None
    arab_max_y = y_search_range[0] + arab_rows.max() if len(arab_rows) > 0 else None
    
    print(f"=== {crop_name} ===")
    print(f"  Latin ink Y range : [{lat_min_y} .. {lat_max_y}] (h = {lat_max_y - lat_min_y + 1 if lat_min_y is not None else 0})")
    print(f"  Arabic ink Y range: [{arab_min_y} .. {arab_max_y}] (h = {arab_max_y - arab_min_y + 1 if arab_min_y is not None else 0})")
    if lat_max_y is not None and arab_max_y is not None:
        delta_bottom = arab_max_y - lat_max_y
        delta_top = arab_min_y - lat_min_y
        print(f"  Delta bottom (Arabic - Latin): {delta_bottom} px")
        print(f"  Delta top    (Arabic - Latin): {delta_top} px")
    return lat_max_y, arab_max_y

# Let's inspect im_lp (left panel) in detail:
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')
print("im_lp size:", im_lp.size)
