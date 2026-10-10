#!/usr/bin/env python3
"""C4 pitch model from screen word widths.

The measured ink of each space-separated word gives one equation
      width_meas(word) = alpha * sum(aw) + pad * n_glyph + (ink overhang)
and each inter-word gap gives
      gap_meas = space advance + rounding.

Fitting these across every word of the five drawn ERE lines identifies the
pitch model far more tightly than a whole-line mask IoU, because the ink of a
word is bounded by that word's own codepoints.

  python source/cr_pitch_model.py
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R  # noqa: E402

BAND_Y = 604
X0, X1 = 366, 690
PITCH = 18
LINE0_TOP = 612
THR = 70


def line_bands():
    img = np.array(Image.open(R.shot("06.52.20.33")).convert("L"))
    sub = (img[BAND_Y:BAND_Y + 146, X0:X1] <= THR)
    return sub


def words_of(text):
    out, cur = [], []
    for ch in text:
        if ch == " ":
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append(cur)
    return out


def runs(cols, min_gap=5):
    """split the measured ink columns into word spans at gaps >= min_gap"""
    xs = np.nonzero(cols)[0]
    if not len(xs):
        return []
    out = [[xs[0], xs[0]]]
    for x in xs[1:]:
        if x - out[-1][1] - 1 >= min_gap:
            out.append([x, x])
        else:
            out[-1][1] = x
    return out


def main():
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    lines = d["start_pos_factions_description_2120156326"].split("\n")[:5]
    m = line_bands()
    for leaf in (sys.argv[1:] or ["la_gioconda_12.cuf", "georgia_italic_12.cuf",
                                  "georgia_italic_14.cuf", "la_gioconda_14.cuf"]):
        c = R.font(leaf)
        print(f"\n=== {leaf}")
        rowsX, rowsY = [], []
        for li, text in enumerate(lines):
            y0 = max(0, LINE0_TOP - BAND_Y + PITCH * li - 7)
            cols = m[y0:y0 + PITCH + 14].sum(axis=0)
            sp = runs(cols, 5)
            ws = words_of(text)
            aws = [sum(R.glyph(c, ord(ch))["aw"] for ch in w) for w in ws]
            ns = [len(w) for w in ws]
            wm = [b - a + 1 for a, b in sp]
            # last span may merge with the flame ornament; drop the last if the
            # count does not match
            if len(sp) != len(ws):
                print(f"  L{li}: spans={len(sp)} words={len(ws)} -> skipped")
                continue
            print(f"  L{li}: meas {wm}  sum_aw {aws}  n {ns}")
            for w, a, n in zip(wm, aws, ns):
                rowsX.append(a)
                rowsY.append(w)
                print(f"      w={w:3d} sum_aw={a:5.1f} n={n:2d} "
                      f"ratio={w / a:.3f}")
        A = np.array(rowsX, float)
        B = np.array(rowsY, float)
        if len(A) > 3:
            slope, inter = np.polyfit(A, B, 1)
            print(f"  >> width = {slope:.4f} * sum_aw + {inter:+.2f}")
            # per-glyph model: width = (aw+pad)*alpha summed
            # regress on (sum_aw, n) jointly
            X = np.column_stack([A, np.array([len(w) for w in
                                              sum([words_of(t) for t in lines],
                                                  [])], float)[:0] or
                                 np.ones(len(A))])
            # least squares width = alpha*sum_aw + pad*n
            ns = []
            for li, text in enumerate(lines):
                for w in words_of(text):
                    ns.append(len(w))
            ns = np.array(ns[:len(A)], float)
            M = np.column_stack([A, ns])
            coef, *_ = np.linalg.lstsq(M, B, rcond=None)
            print(f"  >> width = {coef[0]:.4f} * sum_aw + {coef[1]:+.3f} * n")
            pred = M @ coef
            print(f"     rms resid = {np.sqrt(np.mean((pred-B)**2)):.3f} px")


if __name__ == "__main__":
    main()
