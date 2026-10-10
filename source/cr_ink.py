#!/usr/bin/env python3
"""Region/ink analysis on screenshots for the clean-room measurements.

Light UI text (buttons, boxes) -> bright mask; dark UI text -> dark mask.
Prints row bands and, per band, the column runs (start, end, width) and the
run-to-run pitch/gap statistics.
"""
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"


def load(path, x0, y0, x1, y1):
    im = Image.open(path).convert("L")
    a = np.array(im)[y0:y1, x0:x1]
    return a


def describe(a, mode, thr, minrows=1, xoff=0, yoff=0, label=""):
    m = (a >= thr) if mode == "light" else (a <= thr)
    rows = m.sum(axis=1)
    bands = []
    y = 0
    while y < len(rows):
        if rows[y] >= minrows:
            y0 = y
            while y < len(rows) and rows[y] >= minrows:
                y += 1
            bands.append((y0, y))
        y += 1
    print(f"[{label}] region {a.shape[1]}x{a.shape[0]} mode={mode} thr={thr} "
          f"bands={len(bands)}")
    for (y0, y1) in bands:
        band = m[y0:y1]
        cols = band.sum(axis=0)
        runs = []
        x = 0
        while x < len(cols):
            if cols[x] > 0:
                xs = x
                while x < len(cols) and cols[x] > 0:
                    x += 1
                runs.append((xs + xoff, x + xoff))
            x += 1
        if not runs:
            continue
        starts = [r[0] for r in runs]
        widths = [r[1] - r[0] for r in runs]
        pitches = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        print(f"  y{y0 + yoff}-{y1 + yoff} h={y1 - y0} runs={len(runs)} "
              f"span={runs[-1][1] - runs[0][0]} x{runs[0][0]}-{runs[-1][1]}")
        print(f"    widths {widths}")
        print(f"    pitches {pitches}")
        print(f"    gaps   {gaps}")


def main():
    path = sys.argv[1]
    mode = sys.argv[2]
    thr = int(sys.argv[3])
    x0, y0, x1, y1 = (int(v) for v in sys.argv[4:8])
    tag = sys.argv[8] if len(sys.argv) > 8 else f"{x0},{y0}-{x1},{y1}"
    minrows = int(sys.argv[9]) if len(sys.argv) > 9 else 1
    a = load(path, x0, y0, x1, y1)
    describe(a, mode, thr, minrows, xoff=x0, yoff=y0, label=tag)


if __name__ == "__main__":
    main()
