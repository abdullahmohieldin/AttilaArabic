import os
from PIL import Image
import numpy as np

im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')

# In Total War Attila Faction Select screen:
# Where is the Start Campaign button?
# In Grand Campaign faction select:
# At the bottom right of the center frame? Or bottom center?
# Let's save a full downscaled 960x540 version of both screenshots so we can see the full layout!
im_no.resize((960, 540)).save('scratch/overview_no_hover.png')
im_sl.resize((960, 540)).save('scratch/overview_slider.png')

print("Saved overview_no_hover.png and overview_slider.png")
