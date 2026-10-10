#!/usr/bin/env python3
"""C4 probe: locate the C1 description-box lines (rows, baselines, x extents).

Read-only. Uses the local-median mask from cr_desc (parchment panel defeats a
global threshold). Prints one row per detected line band with its ink runs.
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
import cr_render as R          # noqa: E402
from cr_desc import local_mask  # noqa: E402


def shot_path(ts):
    return os.path.join(
        BASE, "screenshots",
        f"Total War  Attila Screenshot 2026.10.08 - {ts}.png")


def mask(ts, x0, y0, x1, y1, delta=40):
    img = np.array(Image.open(shot_path(ts)).convert("L"))
    return local_mask(img[y0:y1, x0:x1], delta)


def main():
    ts = sys.argv[1] if len(sys.argv) > 1 else "06.52.20.33"
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6]) if len(sys.argv) > 5 \
        else (360, 595, 760, 700)
    delta = 40
    m = mask(ts, x0, y0, x1, y1, delta)
    rows = m.sum(axis=1)
    print(f"shot {ts} window ({x0},{y0})-({x1},{y1}) delta={delta} "
          f"total ink {int(m.sum())}")
    print(f"col ink min x = {x0 + int(np.argmax(m.sum(axis=0) > 0))} "
          f"max x = {x0 + int(len(m.sum(axis=0)) - np.argmax(m.sum(axis=0)[::-1] > 0))}")
    for i, r in enumerate(rows):
        y = y0 + i
        cols = np.nonzero(m[i])[0]
        if len(cols):
            print(f"  y{y:4d} h={r:3d} x={x0 + cols[0]:4d}..{x0 + cols[-1]:4d} "
                  f"n={len(cols)}")
        else:
            print(f"  y{y:4d} h=  0 ---")


if __name__ == "__main__":
    main()
