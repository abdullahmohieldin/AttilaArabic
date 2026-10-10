import os
from PIL import Image
import numpy as np

im = Image.open('scratch/r2_crops/lp_title_area.png')
# Save close crop of the title line
title_line = im.crop((20, 10, 400, 45))
title_line.save('scratch/r2_crops/title_line_exact.png')
title_line_4x = title_line.resize((title_line.width * 4, title_line.height * 4), Image.Resampling.NEAREST)
title_line_4x.save('scratch/r2_crops/title_line_exact_4x.png')

print("Saved title_line_exact_4x.png")

# Let's inspect where ink is on this line:
arr = np.array(title_line.convert('L'))
ink = arr < 100

# Print horizontal columns to see where the Latin marker [FT] is vs where the Arabic text is!
col_sums = np.sum(ink, axis=0)
print("Col sums length:", len(col_sums))
for x in range(0, len(col_sums), 10):
    chunk = col_sums[x:x+10]
    print(f"X={x:3d}..{x+9:3d}: sum={np.sum(chunk):3d}, max={chunk.max():2d}")
