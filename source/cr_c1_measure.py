#!/usr/bin/env python3
"""C1 screenshot measurement: find text bands and per-glyph run pitch.

Regions are given in full 1920x1080 screenshot coordinates. For each region
the script auto-detects text rows (ink bands) and prints the horizontal runs
of ink per band: count, widths, pitches, gaps. A "cell" histogram groups the
run starts modulo a candidate pitch so repeated identical glyph cells show up
as a peak (used for FE92/FEF2 pitch on surfaces whose text repeats one form).
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
SHOTS = os.path.join(BASE, "screenshots", )


def shot(t):
    return os.path.join(SHOTS, f"Total War  Attila Screenshot 2026.10.08 - {t}.png")


# name -> (shot, x0, y0, x1, y1, mode, thr, pitch_hint)
#   mode: 'light' = bright text on dark, 'dark' = dark text on light
REGIONS = {
    "A_title":      ("06.52.20.33", 700, 60, 1250, 190, "light", 170, None),
    "A_grouplabel": ("06.52.20.33", 600, 370, 870, 480, "light", 170, None),
    "A_difficulty": ("06.52.20.33", 2350, 430, 2560, 620, "light", 140, None),
    "A_desc_L0":    ("06.52.20.33", 620, 890, 1540, 960, "dark", 120, None),
    "A_desc_L1":    ("06.52.20.33", 620, 960, 1540, 1010, "dark", 120, None),
    "A_desc_all":   ("06.52.20.33", 620, 880, 1540, 1080, "dark", 120, None),
    "C_btn_load":   ("06.52.25.78", 220, 380, 520, 450, "light", 170, None),
    "C_btn_big":    ("06.52.25.78", 220, 520, 520, 600, "light", 170, None),
    "D_hist":       ("06.52.27.49", 220, 500, 520, 590, "light", 170, None),
    "D_custom":     ("06.52.27.49", 220, 600, 520, 680, "light", 170, None),
    "E_hero":       ("06.52.36.59", 1650, 125, 2000, 185, "light", 170, None),
    "E_stat_a":     ("06.52.36.59", 2350, 1150, 2620, 1200, "dark", 150, None),
    "E_stat_all":   ("06.52.36.59", 2350, 1140, 2620, 1520, "dark", 150, None),
}


def runs_of(mask, minrows=1):
    rows = mask.sum(axis=1)
    bands = []
    y = 0
    while y < len(rows):
        if rows[y] >= minrows:
            y0 = y
            while y < len(rows) and rows[y] >= minrows:
                y += 1
            bands.append((y0, y))
        y += 1
    out = []
    for (y0, y1) in bands:
        band = mask[y0:y1]
        cols = band.sum(axis=0)
        rr = []
        x = 0
        while x < len(cols):
            if cols[x] > 0:
                xs = x
                while x < len(cols) and cols[x] > 0:
                    x += 1
                rr.append((xs, x))
            x += 1
        out.append(((y0, y1), rr))
    return out


def report(name, verbose=True):
    shot_id, x0, y0, x1, y1, mode, thr, _hint = REGIONS[name]
    a = np.array(Image.open(shot(shot_id)).convert("L"))[y0:y1, x0:x1]
    m = (a >= thr) if mode == "light" else (a <= thr)
    print(f"\n=== {name}  shot {shot_id}  box ({x0},{y0})-({x1},{y1}) "
          f"mode={mode} thr={thr}")
    for (by0, by1), rr in runs_of(m, 2):
        if len(rr) < 3:
            print(f"  band y{y0 + by0}-{y0 + by1} h={by1 - by0} runs={len(rr)} {rr}")
            continue
        starts = [r[0] + x0 for r in rr]
        widths = [r[1] - r[0] for r in rr]
        pitches = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
        gaps = [rr[i + 1][0] - rr[i][1] for i in range(len(rr) - 1)]
        print(f"  band y{y0 + by0}-{y0 + by1} h={by1 - by0} runs={len(rr)} "
              f"span={starts[-1] + widths[-1] - starts[0]} "
              f"x{starts[0]}-{starts[-1] + widths[-1]}")
        print(f"    widths {widths}")
        print(f"    starts {starts}")
        print(f"    pitches {pitches}")
        print(f"    gaps   {gaps}")
    return m


def profile(name, step=1):
    """Print the column ink profile (count of bright pixels per column) so a
    repeated letterform can be located by eye in numbers."""
    shot_id, x0, y0, x1, y1, mode, thr, _hint = REGIONS[name]
    a = np.array(Image.open(shot(shot_id)).convert("L"))[y0:y1, x0:x1]
    m = (a >= thr) if mode == "light" else (a <= thr)
    cols = m.sum(axis=0)
    print(f"\n--- profile {name} x{x0}..{x1} (col:count)")
    line = []
    for i, c in enumerate(cols):
        line.append(f"{x0 + i}:{c}")
        if len(line) == 20:
            print("   " + " ".join(line))
            line = []
    if line:
        print("   " + " ".join(line))


if __name__ == "__main__":
    names = sys.argv[1:] or list(REGIONS)
    for n in names:
        if n.startswith("profile:"):
            profile(n.split(":", 1)[1])
        else:
            report(n)
