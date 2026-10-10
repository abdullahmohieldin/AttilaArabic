import os
from PIL import Image
import numpy as np

# Let's inspect rows 11 to 25 of CULTURAL AREA:
im = Image.open('scratch/cult_inspect_1x.png')
# Save crop of y=10..30 and y=38..55
c1 = im.crop((50, 10, 380, 30))
c1.save('scratch/r2_crops/cult_line1.png')
c1.resize((c1.width*4, c1.height*4), Image.Resampling.NEAREST).save('scratch/r2_crops/cult_line1_4x.png')

c2 = im.crop((50, 38, 380, 58))
c2.save('scratch/r2_crops/cult_line2.png')
c2.resize((c2.width*4, c2.height*4), Image.Resampling.NEAREST).save('scratch/r2_crops/cult_line2_4x.png')

# Also inspect difficulty area lines:
im_diff = Image.open('scratch/diff_inspect_1x.png')
im_diff.save('scratch/r2_crops/diff_full.png')
im_diff.resize((im_diff.width*4, im_diff.height*4), Image.Resampling.NEAREST).save('scratch/r2_crops/diff_full_4x.png')

# Also inspect tooltip area:
im_tt = Image.open('scratch/tt_inspect_1x.png')
im_tt.save('scratch/r2_crops/tt_full.png')
im_tt.resize((im_tt.width*4, im_tt.height*4), Image.Resampling.NEAREST).save('scratch/r2_crops/tt_full_4x.png')

# Also inspect tab area:
im_tab = Image.open('scratch/tab_inspect_1x.png')
im_tab.save('scratch/r2_crops/tab_full.png')
im_tab.resize((im_tab.width*4, im_tab.height*4), Image.Resampling.NEAREST).save('scratch/r2_crops/tab_full_4x.png')

# Also inspect center button:
im_cb = Image.open('scratch/center_btn_1x.png')
im_cb.save('scratch/r2_crops/cb_full.png')
im_cb.resize((im_cb.width*4, im_cb.height*4), Image.Resampling.NEAREST).save('scratch/r2_crops/cb_full_4x.png')

print("Saved all 4x images for visual inspection.")
