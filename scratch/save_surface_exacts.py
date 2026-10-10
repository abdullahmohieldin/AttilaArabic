import os
from PIL import Image
import numpy as np

# 1. Top tabs (Factions header)
# In im_no, let's find the Factions tab!
im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')

# In R1, Factions header tab was around X=100..400, Y=25..65
tab_crop = im_no.crop((100, 20, 350, 70))
tab_crop.save('scratch/r2_crops/factions_tab_exact.png')
tab_crop_4x = tab_crop.resize((tab_crop.width * 4, tab_crop.height * 4), Image.Resampling.NEAREST)
tab_crop_4x.save('scratch/r2_crops/factions_tab_exact_4x.png')

# 2. Difficulty area
# Slider label (Hard / Legendary) and description
# In im_no, let's check Y=840..950, X=1340..1610
diff_crop = im_no.crop((1340, 840, 1610, 950))
diff_crop.save('scratch/r2_crops/difficulty_exact.png')
diff_crop_4x = diff_crop.resize((diff_crop.width * 4, diff_crop.height * 4), Image.Resampling.NEAREST)
diff_crop_4x.save('scratch/r2_crops/difficulty_exact_4x.png')

# 3. Tooltip area in im_sl
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
# Where is the tooltip? In im_sl, let's find the tooltip box
# Tooltip box has bright/gold text and dark background
# In check_tooltip_area (X=1550..1900, Y=650..820), let's crop the text inside
tt_crop = im_sl.crop((1400, 650, 1850, 800))
tt_crop.save('scratch/r2_crops/tooltip_exact.png')
tt_crop_4x = tt_crop.resize((tt_crop.width * 4, tt_crop.height * 4), Image.Resampling.NEAREST)
tt_crop_4x.save('scratch/r2_crops/tooltip_exact_4x.png')

# 4. Start Campaign button: Where is it?
# Let's check X=1350..1610, Y=980..1060
btn_crop = im_no.crop((1350, 980, 1610, 1060))
btn_crop.save('scratch/r2_crops/btn_exact.png')
btn_crop_4x = btn_crop.resize((btn_crop.width * 4, btn_crop.height * 4), Image.Resampling.NEAREST)
btn_crop_4x.save('scratch/r2_crops/btn_exact_4x.png')

print("Saved exact crops for tabs, difficulty, tooltip, button.")
