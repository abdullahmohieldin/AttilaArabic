#!/usr/bin/env python3
"""Connected components of a local-median mask (no scipy, BFS label)."""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cr_desc import local_mask  # noqa: E402


def label(m):
    H, W = m.shape
    lab = np.zeros((H, W), np.int32)
    boxes = []
    cur = 0
    ys, xs = np.nonzero(m)
    for sy, sx in zip(ys, xs):
        if lab[sy, sx]:
            continue
        cur += 1
        stack = [(sy, sx)]
        lab[sy, sx] = cur
        y0 = y1 = sy
        x0 = x1 = sx
        n = 0
        while stack:
            y, x = stack.pop()
            n += 1
            if y < y0:
                y0 = y
            if y > y1:
                y1 = y
            if x < x0:
                x0 = x
            if x > x1:
                x1 = x
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and m[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = cur
                        stack.append((yy, xx))
        boxes.append((cur, x0, y0, x1, y1, n))
    return lab, boxes


def main():
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    delta = int(sys.argv[6]) if len(sys.argv) > 6 else 40
    img = np.array(Image.open(os.path.join(
        BASE, "screenshots",
        f"Total War  Attila Screenshot 2026.10.08 - {ts}.png")).convert("L"))
    m = local_mask(img[y0:y1, x0:x1], delta)
    lab, boxes = label(m)
    print(f"{ts} box ({x0},{y0})-({x1},{y1}) delta={delta} comps={len(boxes)}")
    for c, bx0, by0, bx1, by1, n in sorted(boxes, key=lambda b: (b[2], b[1])):
        print(f"  #{c:4d} x{x0+bx0:4d}-{x0+bx1:4d} (w{bx1-bx0+1:3d}) "
              f"y{y0+by0:4d}-{y0+by1:4d} (h{by1-by0+1:3d}) n={n}")


if __name__ == "__main__":
    main()
