import os
import sys
from PIL import Image
import numpy as np

os.makedirs('scratch/r2_crops', exist_ok=True)

# Load the screenshots
im_no_hover = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_slider = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_left_panel = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

print("im_no_hover:", im_no_hover.size)
print("im_slider:", im_slider.size)
print("im_left_panel:", im_left_panel.size)

# Let's inspect im_left_panel size and search for text rows
# im_left_panel is 453x684. Where did it come from in full screen?
# In R1, crop was X~340..790, Y~200..880 approx.
# Let's save a 1x version of left panel and slices of it.
im_left_panel.save('scratch/r2_crops/left_panel_1x.png')

# Let's find where [FT], [C1], and the description box rows are in im_left_panel.
# Let's write a quick script to find dark text rows
arr = np.array(im_left_panel.convert('L'))
print("Left panel luminance min:", arr.min(), "mean:", arr.mean())
