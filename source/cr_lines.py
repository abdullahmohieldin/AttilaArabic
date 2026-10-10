#!/usr/bin/env python3
"""Auto-locate bright text lines in a screenshot and report their glyph runs.

  cr_lines.py <shot-timestamp> [--thr 180] [--minw 40] [--mode light|dark]
              [--find X Y]           nearest line to (X,Y)
              [--list]               all lines with bbox/runs summary
              [--runs X Y]           full run/pitch/gap detail for that line
"""
import os
import sys

import numpy as np
from PIL import Image

SHOTS = r"D:\AttilaArabic\screenshots"


def shot(t):
    return os.path.join(SHOTS, f"Total War  Attila Screenshot 2026.10.08 - {t}.png")


def mask_of(img, mode, thr):
    return (img >= thr) if mode == "light" else (img <= thr)


def find_lines(m, minw=40, minh=4, minpx=30):
    """Group ink rows into lines, then each line into x-clusters (gap>14 px
    split). Returns list of dicts with bbox and runs."""
    rows = m.sum(axis=1)
    lines = []
    y = 0
    H = len(rows)
    while y < H:
        if rows[y] >= 2:
            y0 = y
            while y < H and rows[y] >= 2:
                y += 1
            if y - y0 < minh:
                continue
            band = m[y0:y, :]
            colink = band.sum(axis=0)
            xs = np.nonzero(colink)[0]
            if not len(xs):
                continue
            # split into segments on gaps > 14 columns
            segs = []
            start = xs[0]
            prev = xs[0]
            for x in xs[1:]:
                if x - prev > 14:
                    segs.append((start, prev + 1))
                    start = x
                prev = x
            segs.append((start, prev + 1))
            for (sx, ex) in segs:
                sub = band[:, sx:ex]
                if sub.sum() < minpx or (ex - sx) < minw:
                    continue
                ys = np.nonzero(sub.sum(axis=1))[0]
                lines.append({"x0": int(sx), "x1": int(ex),
                              "y0": int(y0 + ys[0]), "y1": int(y0 + ys[-1] + 1),
                              "band": (int(y0), int(y)),
                              "px": int(sub.sum())})
        y += 1
    return lines


def runs(m, x0, x1, y0, y1):
    sub = m[y0:y1, x0:x1]
    cols = sub.sum(axis=0)
    rr = []
    x = 0
    while x < len(cols):
        if cols[x] > 0:
            xs = x
            while x < len(cols) and cols[x] > 0:
                x += 1
            rr.append((xs, x))
        x += 1
    return rr


def main():
    args = sys.argv[1:]
    ts = args[0]
    thr = 180
    mode = "light"
    minw = 40
    action = "list"
    find = None
    for i, a in enumerate(args):
        if a == "--thr":
            thr = int(args[i + 1])
        elif a == "--mode":
            mode = args[i + 1]
        elif a == "--minw":
            minw = int(args[i + 1])
        elif a == "--find":
            find = (int(args[i + 1]), int(args[i + 2]))
            action = "runs"
        elif a in ("--list",):
            action = "list"
        elif a == "--runs":
            find = (int(args[i + 1]), int(args[i + 2]))
            action = "runs"
    img = np.array(Image.open(shot(ts)).convert("L"))
    m = mask_of(img, mode, thr)
    lines = find_lines(m, minw=minw)
    if action == "list":
        print(f"shot {ts} thr={thr} mode={mode}: {len(lines)} lines")
        for L in lines:
            print(f"  x{L['x0']:5d}-{L['x1']:5d} y{L['y0']:4d}-{L['y1']:4d} "
                  f"w={L['x1'] - L['x0']:4d} h={L['y1'] - L['y0']:3d} "
                  f"px={L['px']:6d}")
        return
    fx, fy = find
    best, bd = None, 1 << 30
    for L in lines:
        cx = (L["x0"] + L["x1"]) / 2
        cy = (L["y0"] + L["y1"]) / 2
        d = (cx - fx) ** 2 + (cy - fy) ** 2
        if d < bd:
            best, bd = L, d
    L = best
    print(f"shot {ts} line x{L['x0']}-{L['x1']} y{L['y0']}-{L['y1']} "
          f"w={L['x1'] - L['x0']} h={L['y1'] - L['y0']} (query {fx},{fy})")
    rr = runs(m, L["x0"], L["x1"], L["y0"], L["y1"])
    starts = [r[0] + L["x0"] for r in rr]
    widths = [r[1] - r[0] for r in rr]
    pitches = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
    gaps = [rr[i + 1][0] - rr[i][1] for i in range(len(rr) - 1)]
    print(f"  runs={len(rr)}")
    print(f"  widths  {widths}")
    print(f"  starts  {starts}")
    print(f"  pitches {pitches}")
    print(f"  gaps    {gaps}")
    # per-row ink profile, useful for spotting glyph separation vertically
    print("  row ink:", list(m[L["y0"]:L["y1"], L["x0"]:L["x1"]].sum(axis=1)))


if __name__ == "__main__":
    main()
