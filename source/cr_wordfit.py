#!/usr/bin/env python3
"""C4 screen word extraction + pitch-model regression (fixed).

For every drawn ERE line: split the measured ink columns at gaps >= GAP px,
match the resulting spans to the space-separated words of the stored line, and
regress   width_meas = alpha * sum(aw) + pad * n_glyphs   per candidate font.

  python source/cr_wordfit.py [GAP]
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
GAP = int(sys.argv[1]) if len(sys.argv) > 1 else 4


def screen_mask():
    img = np.array(Image.open(R.shot("06.52.20.33")).convert("L"))
    return img[BAND_Y:BAND_Y + 146, X0:X1] <= THR


def spans(cols, gap):
    xs = np.nonzero(cols)[0]
    if not len(xs):
        return []
    out = [[xs[0], xs[0]]]
    for x in xs[1:]:
        if x - out[-1][1] - 1 >= gap:
            out.append([x, x])
        else:
            out[-1][1] = x
    return out


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


def main():
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    dd = {k: t for k, t, _ in rows}
    lines = dd["start_pos_factions_description_2120156326"].split("\n")[:5]
    m = screen_mask()
    print(f"gap={GAP} window x{X0}..{X1}")
    for li, text in enumerate(lines):
        y0 = max(0, LINE0_TOP - BAND_Y + PITCH * li - 7)
        cols = m[y0:y0 + PITCH + 14].sum(axis=0)
        sp = spans(cols, GAP)
        ws = words_of(text)
        print(f"L{li}: nwords_stored={len(ws)} nspans={len(sp)} "
              f"spans={[[X0+a, X0+b] for a, b in sp]}")
        for w in ws:
            print("     word " + "".join(w))
    for leaf in ("la_gioconda_12.cuf", "georgia_italic_12.cuf",
                 "georgia_italic_14.cuf", "la_gioconda_14.cuf",
                 "georgia_italic_16.cuf", "la_gioconda_16.cuf",
                 "arialunicode_12.cuf"):
        c = R.font(leaf)
        A, B, N, tags = [], [], [], []
        for li, text in enumerate(lines):
            y0 = max(0, LINE0_TOP - BAND_Y + PITCH * li - 7)
            cols = m[y0:y0 + PITCH + 14].sum(axis=0)
            sp = spans(cols, GAP)
            ws = words_of(text)
            if len(sp) != len(ws):
                print(f"  {leaf:24s} L{li}: span/word mismatch "
                      f"({len(sp)}/{len(ws)}) skipped")
                continue
            for (a, b), w in zip(sp, ws):
                aw = sum(R.glyph(c, ord(ch))["aw"] for ch in w)
                A.append(aw)
                B.append(b - a + 1)
                N.append(len(w))
                tags.append(f"L{li}:{''.join(w)}")
        A, B, N = map(np.array, (A, B, N))
        if len(A) < 4:
            continue
        M = np.column_stack([A, N])
        coef, *_ = np.linalg.lstsq(M, B, rcond=None)
        pred = M @ coef
        rms = float(np.sqrt(np.mean((pred - B) ** 2)))
        print(f"  {leaf:24s} n={len(A):2d}  width = {coef[0]:.4f}*sum_aw "
              f"{coef[1]:+.3f}*n   rms={rms:.2f}px  "
              f"alpha_only={(B / A).mean():.3f}")


if __name__ == "__main__":
    main()
