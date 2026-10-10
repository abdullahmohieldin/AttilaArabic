import os
from PIL import Image
import numpy as np

# Load im_no
im_no = Image.open('screenshots/Phase1_R2_01_faction_select_no_hover.png')
print("Searching full 1920x1080 image for buttons and text...")

# Let's inspect bottom right quadrant:
# In Total War Attila, the "Start Campaign" button is a large checkmark or circular button, or a rectangular button in the bottom right corner of the screen!
# Wait! In 1920x1080, why was X ending at 1607?
# Wait! Let's check why arr[800:1080, :] ended at 1607!
# Is the game running at 1680x1050 or 1600x900, or is the right side of the screen black (4:3 pillarbox)?
arr = np.array(im_no.convert('L'))
print("Width non-black check for all Y:")
for y in range(100, 1000, 100):
    xs = np.where(arr[y, :] > 30)[0]
    if len(xs) > 0:
        print(f"  Y={y:3d}: X=[{xs.min()}..{xs.max()}]")
    else:
        print(f"  Y={y:3d}: all black")
