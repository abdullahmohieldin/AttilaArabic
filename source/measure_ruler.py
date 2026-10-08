import sys

from PIL import Image
import numpy as np

path = sys.argv[1] if len(sys.argv) > 1 else r"D:\AttilaArabic\screenshots\Total War  Attila Screenshot 2026.10.08 - 02.19.08.05.png"
X0, X1, Y0, Y1 = 372, 660, 600, 725
img = np.array(Image.open(path).convert("L"))
sub = img[Y0:Y1, X0:X1]
dark = sub < 140
# mask vertical border columns: dark in >60% of rows
colfrac = dark.mean(axis=0)
badcols = colfrac > 0.6
dark = dark & ~badcols[None, :]
rows = dark.sum(axis=1)
bands = []
y = 0
while y < len(rows):
    if rows[y] >= 2:
        y0 = y
        while y < len(rows) and rows[y] >= 2:
            y += 1
        if y - y0 >= 3:
            bands.append((y0, y))
    y += 1
names = ["FE92", "FE98", "FE9C", "FEF4", "FE8D", "FE8E"]
for bi, (y0, y1) in enumerate(bands):
    band = dark[y0:y1]
    cols = band.sum(axis=0)
    runs = []
    x = 0
    while x < len(cols):
        if cols[x] > 0:
            x0 = x
            while x < len(cols) and cols[x] > 0:
                x += 1
            runs.append((x0, x))
        else:
            x += 1
    if len(runs) < 4:
        print(f"band y{Y0+y0}-{Y0+y1} n={len(runs)} runs={runs[:8]}")
        continue
    starts = [r[0] for r in runs]
    widths = [r[1] - r[0] for r in runs]
    pitches = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
    gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
    tag = names[bi] if bi < len(names) else "?"
    print(f"{tag} y{Y0+y0}-{Y0+y1} n={len(runs)} ink_w min/med/max={min(widths)}/{sorted(widths)[len(widths)//2]}/{max(widths)} "
          f"pitch min/med/max={min(pitches)}/{sorted(pitches)[len(pitches)//2]}/{max(pitches)} "
          f"gap min/med/max={min(gaps)}/{sorted(gaps)[len(gaps)//2]}/{max(gaps)} span={runs[-1][1]-runs[0][0]}")
