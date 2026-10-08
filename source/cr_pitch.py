#!/usr/bin/env python3
"""Per-surface pitch measurement for the C1 batch.

For every surface region:
  * vertical extent of the ink (glyph body) -> font size evidence
  * autocorrelation of the column ink profile -> dominant horizontal period
    (this is the on-screen pitch; reinforced by repeated letterforms)
  * runs / gaps inside the text (word gaps > 4 px are not joins)
  * per-codepoint centre-to-centre distances for repeated letterform stems
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

# name -> (shot, x0, y0, x1, y1, mode, thr, expected visual string or None)
SURFACES = {
    "faction_title_ERE": ("06.52.20.33", 870, 92, 1050, 130, "light", 180,
                          "\uFE94\uFEF4\uFED7\uFEAE\uFEB8\uFEDF\uFE8D \uFE8E\uFEE3\uFEED\uFEAD"),
    "custom_battle_hdr": ("06.52.36.59", 880, 90, 1110, 130, "light", 180,
                          "\uFE94\uFEBC\uFEBC\uFEA8\uFEE3 \uFE94\uFEDB\uFEAE\uFECC\uFEE3"),
    "cmp_menu_btn": ("06.52.25.78", 120, 545, 350, 600, "light", 175,
                     "\uFE94\uFEE4\uFEF4\uFEDB \uFE94\uFEE0\uFEE4\uFEA4"),
    "battle_btn_hist": ("06.52.27.49", 150, 445, 305, 485, "light", 180,
                        "\uFE94\uFEDB\uFEAE\uFECC \uFE94\uFEF3\uFEAE\uFEF4\uFED7\uFEE8"),
    "cmp_board_btn": ("06.52.25.78", 120, 685, 340, 715, "light", 180,
                      "\uFE95\uFE8E\uFEAA\uFE8D\uFEAA \uFEC1\uFE94\uFE8D"),
    "desc_line0_ERE": ("06.52.20.33", 500, 340, 960, 365, "dark", 120,
                       "\u0640\uFEE5\uFE8E\uFEE8\uFECC\uFEDF\uFE8D \uFED6\uFEE0\uFEC3\uFE83 \uFE94\uFEF4\uFEE7\uFE8E\uFEE3\uFEED\uFEAE\uFEDF\uFE8D \uFE94\uFEF3\uFEAD\uFEEE\uFEC3\uFE8D\uFEAE\uFE92\uFEE3\uFEF9\uFE8D \uFEE1\uFE8E\uFEB4\uFED8\uFEE7\uFE8D"),
    "unit_hero": ("06.52.36.59", 880, 90, 1110, 130, "light", 180, None),
    "difficulty_box": ("06.52.20.33", 1780, 430, 1930, 470, "light", 150, None),
    "stat_label_armour": ("06.52.36.59", 1780, 640, 2000, 680, "dark", 150,
                          "\uFE93\uFEE0\uFEE4\uFEA4\uFEDF\uFE8D"),
    "dropdown_group": ("06.52.36.59", 1140, 530, 1420, 560, "dark", 150, None),
}


def mask(shot, x0, y0, x1, y1, mode, thr):
    img = np.array(Image.open(R.shot(shot)).convert("L"))
    a = img[y0:y1, x0:x1]
    return ((a >= thr) if mode == "light" else (a <= thr)).astype(np.uint8)


def autocorr_pitch(prof, lo=4, hi=22):
    p = prof.astype(np.float64)
    p = p - p.mean()
    if not np.any(p):
        return None, []
    ac = np.correlate(p, p, mode="full")[len(p) - 1:]
    if ac[0] <= 0:
        return None, []
    ac = ac / ac[0]
    rng = ac[lo:hi + 1]
    k = int(np.argmax(rng)) + lo
    return k, [round(float(v), 3) for v in ac[lo:hi + 1]]


def word_runs(m, minwordgap=6):
    """Split the ink columns into words on gaps >= minwordgap, then report
    within-word blank columns (join gaps)."""
    cols = m.sum(axis=0)
    ink = cols > 0
    segs = []
    x = 0
    n = len(ink)
    while x < n:
        if ink[x]:
            xs = x
            while x < n and ink[x]:
                x += 1
            segs.append([xs, x])
        x += 1
    # merge segments separated by < minwordgap
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < minwordgap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return merged


def baseline_band(m):
    """Rows that carry the connecting baseline: the lowest contiguous ink row
    band (Arabic joins run along the baseline)."""
    rows = m.sum(axis=1)
    ys = np.nonzero(rows)[0]
    if not len(ys):
        return None
    return ys[-1] - 2, ys[-1] + 1


def report(name, verbose=True):
    shot, x0, y0, x1, y1, mode, thr, text = SURFACES[name]
    m = mask(shot, x0, y0, x1, y1, mode, thr)
    ys = np.nonzero(m.sum(axis=1))[0]
    xs = np.nonzero(m.sum(axis=0))[0]
    if not len(ys):
        print(f"\n=== {name}: no ink in box")
        return
    sub = m[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]
    cols = sub.sum(axis=0)
    prof = cols
    k, ac = autocorr_pitch(prof)
    words = word_runs(sub)
    bb = baseline_band(sub)
    print(f"\n=== {name}  {shot} box({x0},{y0})-({x1},{y1}) mode={mode} thr={thr}")
    print(f"  ink bbox x{x0 + xs[0]}-{x0 + xs[-1] + 1} y{y0 + ys[0]}-{y0 + ys[-1] + 1} "
          f"h={ys[-1] - ys[0] + 1} px={int(sub.sum())}")
    print(f"  autocorr pitch {k}  ac[4..22]={ac}")
    print(f"  words ({len(words)}, gap>=6px): " +
          " ".join(f"[{w[0]}-{w[1]}]{w[1] - w[0]}" for w in words))
    # within-word blank columns in the baseline band
    if bb:
        band = sub[bb[0]:bb[1], :]
        bcols = band.sum(axis=0)
        blanks = []
        for w in words:
            seg = bcols[w[0]:w[1]]
            z = 0
            for i, v in enumerate(seg):
                if v == 0:
                    z += 1
                else:
                    if z:
                        blanks.append((w[0] + i - z, z))
                    z = 0
            if z:
                blanks.append((w[1] - z, z))
        print(f"  baseline band rows {bb[0]}..{bb[1]} of {sub.shape[0]}: "
              f"blank runs (x,len) {blanks}")
    if verbose:
        print(f"  column profile: {list(prof)}")
    return sub


if __name__ == "__main__":
    names = sys.argv[1:] or list(SURFACES)
    for n in names:
        report(n)
