#!/usr/bin/env python3
"""Does the engine re-wrap, or does it honour our hard newlines?

For each drawn line of the ERE and WRE description boxes: measure the ink
column span and compare it with the stored line's codepoint sequence rendered
at the calibrated metrics. If the engine re-wrapped, the chain of codepoints
drawn per screen line would differ from the stored lines; if it honours the
hard newlines, stored line i is exactly screen line i.

  python source/cr_wrapcheck.py
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R  # noqa: E402

THR = 70
PITCH = 18


def mask(ts, y0, y1, x0, x1):
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    return img[y0:y1, x0:x1] <= THR


def bands(ts, ytop, x0, x1, n=8):
    """-> list of (y0, y1, cols) for each drawn text line"""
    m = mask(ts, ytop - 10, ytop + PITCH * n + 10, x0, x1)
    out = []
    for li in range(n):
        y = ytop - (ytop - 10) + PITCH * li
        sub = m[y - 7:y + PITCH + 8]
        cols = sub.sum(axis=0)
        xs = np.nonzero(cols)[0]
        out.append((xs[0] + x0 if len(xs) else None,
                    xs[-1] + x0 if len(xs) else None, int(sub.sum())))
    return out


def main():
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    for label, ts, key, ytop, x0, x1 in (
            ("ERE", "06.52.20.33", "start_pos_factions_description_2120156326",
             612, 366, 690),
            ("WRE", "06.52.22.90", "start_pos_factions_description_2120156339",
             612, 366, 690)):
        stored = d[key].split("\n")
        print(f"\n=== {label} {ts}")
        for li, (a, b, ink) in enumerate(bands(ts, ytop, x0, x1)):
            txt = stored[li] if li < len(stored) else ""
            print(f"  y{ytop + PITCH * li}: x{a}..{b} w={(b - a + 1) if a else 0:3d} "
                  f"ink={ink:4d} stored[{li}] n={len(txt)}")


if __name__ == "__main__":
    main()
