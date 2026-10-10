import os
from PIL import Image
import numpy as np

im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
im_sl = Image.open('screenshots/Phase1_R2_02_slider_hover_legendary.png')
im_lp = Image.open('screenshots/Phase1_R2_03_left_panel_crop.png')

# 1. Factions Header Tab (top area in im_no)
# In R1, the header was around X=100..400, Y=25..80
# Let's inspect rows 20 to 80, cols 80 to 350
tab = im_no.crop((80, 20, 350, 75))
tab.save('scratch/tab_inspect_1x.png')
tab.resize((tab.width * 4, tab.height * 4), Image.Resampling.NEAREST).save('scratch/tab_inspect_4x.png')

# 2. Difficulty Area (middle-right/bottom-right)
# In im_no, difficulty slider is around X=1350..1650, Y=820..950
diff = im_no.crop((1350, 820, 1620, 950))
diff.save('scratch/diff_inspect_1x.png')
diff.resize((diff.width * 4, diff.height * 4), Image.Resampling.NEAREST).save('scratch/diff_inspect_4x.png')

# 3. Tooltip in im_sl
# Let's find the tooltip box in im_sl
# Tooltip box has bright parchment/gold border and dark background
# In im_sl, diff against im_no was around X=1610..1890, Y=600..810!
tt = im_sl.crop((1580, 580, 1900, 820))
tt.save('scratch/tt_inspect_1x.png')
tt.resize((tt.width * 4, tt.height * 4), Image.Resampling.NEAREST).save('scratch/tt_inspect_4x.png')

# 4. Start Campaign Button:
# In Grand Campaign, the button is around X=1400..1610, Y=980..1060?
# But earlier we checked cand_center_bottom (X=750..1150, Y=950..1070) and found text at Y=982!
# Let's crop X=700..1200, Y=960..1040:
center_btn = im_no.crop((700, 960, 1200, 1040))
center_btn.save('scratch/center_btn_1x.png')
center_btn.resize((center_btn.width * 4, center_btn.height * 4), Image.Resampling.NEAREST).save('scratch/center_btn_4x.png')

# Also check bottom-right button around X=1400..1610, Y=950..1060:
br_btn = im_no.crop((1380, 950, 1610, 1060))
br_btn.save('scratch/br_btn_1x.png')
br_btn.resize((br_btn.width * 4, br_btn.height * 4), Image.Resampling.NEAREST).save('scratch/br_btn_4x.png')

# 5. Cultural Trait in im_lp:
# Where is Cultural Trait in im_lp?
# In im_lp (height 684), between leader and description box (Y=240..330)
cult = im_lp.crop((30, 240, 420, 330))
cult.save('scratch/cult_inspect_1x.png')
cult.resize((cult.width * 4, cult.height * 4), Image.Resampling.NEAREST).save('scratch/cult_inspect_4x.png')

print("Saved all 5 surface inspection crops!")
