import os
from PIL import Image
import numpy as np

im = Image.open('scratch/r2_crops/bottom_right_panel.png')
# Size is 410x280 (X=1200..1610, Y=800..1080)
# Let's save 4 vertical slices:
im.crop((0, 0, 410, 70)).save('scratch/r2_crops/br_00_70.png')
im.crop((0, 70, 410, 140)).save('scratch/r2_crops/br_70_140.png')
im.crop((0, 140, 410, 210)).save('scratch/r2_crops/br_140_210.png')
im.crop((0, 210, 410, 280)).save('scratch/r2_crops/br_210_280.png')

print("Saved BR slices.")
