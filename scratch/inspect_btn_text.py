import os
from PIL import Image
import numpy as np

im = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')

# In cand_center_bottom (X=750..1150, Y=950..1070), row y=30..60 is full Y=980..1010
btn_crop = im.crop((820, 975, 1100, 1025))
btn_crop.save('scratch/r2_crops/start_campaign_button_exact_1x.png')
btn_4x = btn_crop.resize((btn_crop.width * 4, btn_crop.height * 4), Image.Resampling.NEAREST)
btn_4x.save('scratch/r2_crops/start_campaign_button_exact_4x.png')

# Print ASCII of the button text
arr = np.array(btn_crop.convert('L'))
ink = arr > 120 # text is bright on button

print("=== START CAMPAIGN BUTTON ASCII ===")
for y in range(len(arr)):
    row = ''.join('#' if ink[y, x] else '.' for x in range(len(arr[0])))
    if '#' in row:
        print(f"y={y:2d} | {row}")
