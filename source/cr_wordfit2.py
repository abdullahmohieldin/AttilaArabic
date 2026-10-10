#!/usr/bin/env python3
"""C4 pitch model from matched screen word spans.

Neither side can be segmented perfectly (the flame ornament clips the rightmost
word and some space gaps are small), so this script segments BOTH the stored
line (on U+0020) and the screen ink (on gaps >= GAP) and pairs the spans from
the LEFT edge, using only the pairs that exist on both sides, with the last
screen span discarded when the stored line has more words (the flame eats it).

Then it regresses, for every candidate font,
      width_meas = alpha * sum(aw) + pad * n_glyphs
and also reports the pure ratio.

  python source/cr_wordfit2.py [GAP]
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
X0, X1 = 366, 694
PITCH = 18
LINE0_TOP = 612
THR = 70
GAP = int(sys.argv[1]) if len(sys.argv) > 1 else 3


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
    for i, ch in enumerate(text):
        if ch == " ":
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append((i, ch))
    if cur:
        out.append(cur)
    return out


def collect(c, lines, m, gap):
    """-> list of (label, sum_aw, n, measured_width, x0, x1)"""
    pairs = []
    for li, text in enumerate(lines):
        y0 = max(0, LINE0_TOP - BAND_Y + PITCH * li - 7)
        cols = m[y0:y0 + PITCH + 14].sum(axis=0)
        sp = spans(cols, gap)
        ws = words_of(text)
        n = min(len(sp), len(ws))
        for k in range(n):
            a, b = sp[k]
            w = ws[k]
            # a screen span may merge two stored words; skip when the pixel
            # width suggests a merge (span much longer than the glyph count)
            pairs.append({
                "label": f"L{li}w{k}",
                "sum_aw": sum(R.glyph(c, ord(ch))["aw"] for _i, ch in w),
                "n": len(w),
                "meas": b - a + 1,
                "x0": X0 + a, "x1": X0 + b,
                "text": "".join(ch for _i, ch in w),
            })
    return pairs


def main():
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    dd = {k: t for k, t, _ in rows}
    lines = dd["start_pos_factions_description_2120156326"].split("\n")[:5]
    m = screen_mask()
    fonts = ("la_gioconda_10.cuf", "la_gioconda_11.cuf", "la_gioconda_12.cuf",
             "la_gioconda_13.cuf", "la_gioconda_14.cuf", "la_gioconda_16.cuf",
             "georgia_italic_10.cuf", "georgia_italic_11.cuf",
             "georgia_italic_12.cuf", "georgia_italic_13.cuf",
             "georgia_italic_14.cuf", "georgia_italic_16.cuf",
             "arialunicode_12.cuf", "arialunicode_14.cuf")
    for gap in (3, 4):
        print(f"\n########## gap={gap}")
        for leaf in fonts:
            try:
                c = R.font(leaf)
            except StopIteration:
                continue
            pr = collect(c, lines, m, gap)
            # drop obvious merges: measured far above the biggest single word
            A = np.array([p["sum_aw"] for p in pr], float)
            N = np.array([p["n"] for p in pr], float)
            B = np.array([p["meas"] for p in pr], float)
            keep = A > 25
            coef, *_ = np.linalg.lstsq(np.column_stack([A[keep], N[keep]]),
                                       B[keep], rcond=None)
            pred = coef[0] * A[keep] + coef[1] * N[keep]
            rms = float(np.sqrt(np.mean((pred - B[keep]) ** 2)))
            ratios = (B[keep] / A[keep])
            print(f"  {leaf:22s} n={keep.sum():2d} "
                  f"width={coef[0]:.4f}*sum_aw{coef[1]:+.3f}*n rms={rms:5.2f} "
                  f"ratio_med={np.median(ratios):.3f} "
                  f"ratio_iqr=({np.percentile(ratios,25):.3f},"
                  f"{np.percentile(ratios,75):.3f})")
        if gap == 3:
            c = R.font("la_gioconda_12.cuf")
            for p in collect(c, lines, m, gap):
                print(f"     {p['label']:6s} meas={p['meas']:3d} "
                      f"sum_aw={p['sum_aw']:5.1f} n={p['n']:2d} "
                      f"ratio={p['meas']/max(1,p['sum_aw']):.3f} "
                      f"x{p['x0']}..{p['x1']} {p['text']}")


if __name__ == "__main__":
    main()
