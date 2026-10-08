#!/usr/bin/env python3
"""Join-gap measurement: horizontal seams between adjacent glyph cells.

For a text line and a font, the offline renderer predicts where each codepoint
cell is; this script measures, in the screenshot, the blank column runs along
the baseline strip (the rows that carry the Arabic connecting stroke) and
reports the seam widths inside words. A seam >= 2 px is what the eye reads as
a break in the connection.
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402


def crop(ts, x0, y0, x1, y1):
    return np.array(Image.open(R.shot(ts)).convert("L"))[y0:y1, x0:x1]


def ink_mask(a, mode, thr):
    return (a >= thr) if mode == "light" else (a <= thr)


def band_info(m, label, xoff=0, yoff=0):
    rows = m.sum(axis=1)
    ys = np.nonzero(rows)[0]
    if not len(ys):
        print(f"  {label}: no ink")
        return
    print(f"  {label}: ink rows y{yoff + ys[0]}..{yoff + ys[-1]} "
          f"(h={ys[-1] - ys[0] + 1})")
    return ys


def seams(m, y0, y1, xoff=0, label=""):
    strip = m[y0:y1, :]
    cols = strip.sum(axis=0) > 0
    n = len(cols)
    runs = []
    x = 0
    while x < n:
        if cols[x]:
            xs = x
            while x < n and cols[x]:
                x += 1
            runs.append((xs + xoff, x + xoff))
        x += 1
    # words: runs separated by >= 6 px
    words = []
    for r in runs:
        if words and r[0] - words[-1][-1][1] < 6:
            words[-1].append(r)
        else:
            words.append([r])
    out = []
    for w in words:
        for i in range(len(w) - 1):
            out.append(w[i + 1][0] - w[i][1])
    print(f"  {label}: baseline strip y{y0 + xoff * 0}..{y1} "
          f"runs={len(runs)} words={len(words)}")
    print(f"    run bounds {runs}")
    print(f"    intra-word seams {out}")
    if out:
        a = np.array(out)
        print(f"    seam min/med/max = {a.min()}/{int(np.median(a))}/{a.max()} "
              f"n>=2px={int((a >= 2).sum())}/{len(a)}")
    return runs, out


def analyse(ts, box, mode="light", thr=180, strip_frac=0.35, label=""):
    x0, y0, x1, y1 = box
    a = crop(ts, x0, y0, x1, y1)
    m = ink_mask(a, mode, thr)
    print(f"\n=== {label or ts} box={box} mode={mode} thr={thr}")
    ys = band_info(m, "line", xoff=x0, yoff=y0)
    if ys is None:
        return
    h = ys[-1] - ys[0] + 1
    top = ys[0]
    bot = ys[-1] + 1
    print("  row ink profile:", list(m[top:bot, :].sum(axis=1)))
    cut = int(bot - max(3, round(h * strip_frac)))
    seams(m, cut, bot, xoff=x0, label=f"strip({cut}..{bot})")
    seams(m, top, bot, xoff=x0, label=f"full({top}..{bot})")


if __name__ == "__main__":
    ts = sys.argv[1]
    box = tuple(int(v) for v in sys.argv[2:6])
    mode = sys.argv[6] if len(sys.argv) > 6 else "light"
    thr = int(sys.argv[7]) if len(sys.argv) > 7 else 180
    label = sys.argv[8] if len(sys.argv) > 8 else ""
    analyse(ts, box, mode, thr, label=label)
