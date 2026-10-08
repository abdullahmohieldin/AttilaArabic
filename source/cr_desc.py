#!/usr/bin/env python3
"""Description-box line detector: local-contrast text mask, line bands and
dot-cluster (U+FE92/U+FEF2) pitch.

The parchment panel is textured, so a global threshold fails; ink = pixels
darker than the local (31 px) median by >= `delta`.

  cr_desc.py <ts> X0 Y0 X1 Y1 [--delta 45] [--art Y0 Y1]
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402


def local_mask(img, delta=45, win=31):
    a = img.astype(np.int16)
    # cheap box mean over a win x win window (uniform filter via cumsum)
    pad = win // 2
    p = np.pad(a, pad, mode="edge")
    c = np.cumsum(np.cumsum(p, axis=0), axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    H, W = a.shape
    y0 = np.arange(H)
    x0 = np.arange(W)
    y1 = y0 + win
    x1 = x0 + win
    S = (c[np.ix_(y1, x1)] - c[np.ix_(y0, x1)] - c[np.ix_(y1, x0)]
         + c[np.ix_(y0, x0)])
    med = S / float(win * win)
    return (med - a) >= delta


def bands(m, minrows=2):
    rows = m.sum(axis=1)
    out = []
    y = 0
    while y < len(rows):
        if rows[y] >= minrows:
            y0 = y
            while y < len(rows) and rows[y] >= minrows:
                y += 1
            out.append((y0, y))
        y += 1
    return out


def runs_in(m, y0, y1, minpx=1):
    cols = m[y0:y1].sum(axis=0)
    rr = []
    x = 0
    while x < len(cols):
        if cols[x] >= minpx:
            xs = x
            while x < len(cols) and cols[x] >= minpx:
                x += 1
            rr.append((xs, x))
        x += 1
    return rr


def main():
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    delta, art = 45, None
    for i, a in enumerate(sys.argv):
        if a == "--delta":
            delta = int(sys.argv[i + 1])
        if a == "--art":
            art = (int(sys.argv[i + 1]), int(sys.argv[i + 2]))
    img = np.array(Image.open(R.shot(ts)).convert("L"))[y0:y1, x0:x1]
    m = local_mask(img, delta)
    print(f"shot {ts} box=({x0},{y0})-({x1},{y1}) delta={delta} "
          f"ink={int(m.sum())}")
    bs = bands(m, 3)
    for (by0, by1) in bs:
        rr = runs_in(m, by0, by1, 2)
        ink = int(m[by0:by1].sum())
        print(f"  band y{y0 + by0}-{y0 + by1} h={by1 - by0} px={ink} "
              f"runs={len(rr)} x{x0 + rr[0][0] if rr else '-'}-"
              f"{x0 + rr[-1][1] if rr else '-'}")
        if len(rr) < 40:
            print(f"    run bounds {[(x0 + a, x0 + b) for a, b in rr]}")
    if art:
        ay0, ay1 = art
        sub = (img[ay0 - y0:ay1 - y0] if y0 <= ay0 else img[:ay1 - y0])
        mm = (m[ay0 - y0:ay1 - y0] if y0 <= ay0 else m[:ay1 - y0])
        print(f"  art rows {ay0}..{ay1}")
        for i, row in enumerate(mm):
            print(f"   {ay0 + i:4d} " + "".join(
                "#" if v else "." for v in row[:160]))


if __name__ == "__main__":
    main()
