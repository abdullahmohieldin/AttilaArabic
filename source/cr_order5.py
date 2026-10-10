#!/usr/bin/env python3
"""Drawn-direction test on the dot pattern alone.

Diacritic dots sit at a fixed x range inside each glyph's own advance cell, so
their positions depend only on the ORDER of the codepoints, not on glyph
artwork. For a stored string we predict, for every codepoint that carries
dots, the x window of its cell under an advance model; then we score the
measured dot clusters in the screenshot against the stored-order prediction
and the reversed-order prediction.

  cr_order5.py <ts> X0 Y0 X1 Y1 "<stored text>" [--font leaf] [--scale s]
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

PF = R.PackFile(R.SHY)

# codepoints with dots and where they sit (above/below) - by construction
DOT_ABOVE = set()
DOT_BELOW = set()
for cp, above in [
    (0xFE8E, 0), (0xFEF4, 1), (0xFEF2, 1), (0xFE92, 0), (0xFE94, 1),
    (0xFEE7, 1), (0xFEE8, 1), (0xFEE3, 0), (0xFEE4, 0), (0xFEB8, 1),
    (0xFEB7, 1), (0xFEB4, 1), (0xFEB3, 1), (0xFEDF, 0), (0xFEE0, 0),
    (0xFEAD, 0), (0xFEAE, 0), (0xFECC, 0), (0xFECB, 0), (0xFE9F, 1),
    (0xFEA0, 1), (0xFEA3, 1), (0xFEA4, 1), (0xFEC3, 1), (0xFEC4, 1),
    (0xFED3, 0), (0xFED4, 0), (0xFEF3, 1), (0xFEEB, 1), (0xFEEC, 1),
    (0xFE8B, 1), (0xFE8C, 1), (0xFE97, 1), (0xFE98, 1), (0xFE9B, 1),
    (0xFE9C, 1), (0xFEA7, 1), (0xFEA8, 1), (0xFEBF, 1), (0xFEC0, 1),
    (0xFED7, 0), (0xFED8, 0), (0xFEDB, 0), (0xFEDC, 0), (0xFEC7, 1),
    (0xFEC8, 1), (0xFECF, 0), (0xFED0, 0), (0xFEE9, 0), (0xFEEA, 0),
]:
    (DOT_ABOVE if above else DOT_BELOW).add(cp)


def font(leaf):
    n = next(x for x in PF.files if x.endswith(leaf))
    return R.CUF.decode(PF.get_file(n))


def cells(c, text, scale):
    """-> list of (cp, cell_x0, cell_x1, aw) in the given draw order."""
    out, x = [], 0.0
    for ch in text:
        g = R.glyph(c, ord(ch))
        cp = ord(ch)
        aw = (g["aw"] * scale) if g else 0.0
        out.append((cp, x, x + aw, aw))
        x += aw
    return out, x


def measured_dots(img, thr):
    """dot clusters = small components in the top / bottom few rows."""
    m = (img >= thr).astype(np.uint8)
    ys = np.nonzero(m.sum(axis=1))[0]
    if not len(ys):
        return [], []
    body = m[ys[0]:ys[-1] + 1]
    h = body.shape[0]
    lab = -np.ones(body.shape, np.int32)
    comps = []
    for yy in range(h):
        for xx in range(body.shape[1]):
            if not body[yy, xx] or lab[yy, xx] >= 0:
                continue
            st = [(yy, xx)]
            lab[yy, xx] = 0
            pts = []
            while st:
                y, x = st.pop()
                pts.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1),
                               (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < body.shape[1] \
                            and body[ny, nx] and lab[ny, nx] < 0:
                        lab[ny, nx] = 0
                        st.append((ny, nx))
            pts = np.array(pts)
            comps.append((pts[:, 1].min(), pts[:, 1].max() + 1,
                          pts[:, 0].min(), pts[:, 0].max() + 1, len(pts)))
    # dots = small components in the top 40% or bottom 25% of the band
    top, bot = [], []
    for (x0, x1, y0, y1, n) in comps:
        small = (x1 - x0) <= 5 and (y1 - y0) <= 4 and n <= 16
        if not small:
            continue
        if y1 <= 0.45 * h:
            top.append((x0 + x1) / 2.0)
        elif y0 >= 0.75 * h:
            bot.append((x0 + x1) / 2.0)
    return sorted(top), sorted(bot)


def score(predicted, observed):
    """sum of distances from each observed dot to the nearest predicted cell
    centre (px); lower is better, and a wrong order doubles it."""
    if not observed:
        return None, []
    d = []
    for o in observed:
        d.append(min(abs(o - p) for p in predicted) if predicted else 1e9)
    return sum(d) / len(d), d


def main():
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    text = sys.argv[6]
    thr, leaf, scales = 180, "georgia_italic_16.cuf", None
    for i, a in enumerate(sys.argv):
        if a == "--thr":
            thr = int(sys.argv[i + 1])
        if a == "--font":
            leaf = sys.argv[i + 1]
        if a == "--scale":
            scales = [float(v) for v in sys.argv[i + 1].split(",")]
    if scales is None:
        scales = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    img = np.array(Image.open(R.shot(ts)).convert("L"))[y0:y1, x0:x1]
    top, bot = measured_dots(img, thr)
    xs = np.nonzero((img >= thr).sum(axis=0))[0]
    print(f"shot {ts} box=({x0},{y0})-({x1},{y1}) text ink x{x0 + xs[0]}.."
          f"{x0 + xs[-1] + 1} (width {xs[-1] - xs[0] + 1})")
    print(f"  measured dots ABOVE at x: {[round(x0 + v, 1) for v in top]}")
    print(f"  measured dots BELOW at x: {[round(x0 + v, 1) for v in bot]}")
    c = font(leaf)
    print(f"  font {leaf}: {c.props}")
    for label, txt in (("stored", text),
                       ("wordrev", " ".join(w[::-1] for w in text.split(" "))),
                       ("fullrev", text[::-1])):
        print(f"  --- {label}: {txt!r}")
        for s in scales:
            cl, total = cells(c, txt, s)
            above = [x0 + (a + b) / 2.0 for cp, a, b, aw in cl
                     if cp in DOT_ABOVE and aw > 0]
            below = [x0 + (a + b) / 2.0 for cp, a, b, aw in cl
                     if cp in DOT_BELOW and aw > 0]
            sa, da = score(above, top)
            sb, db = score(below, bot)
            if sa is None and sb is None:
                continue
            tot = (sa or 0) * len(top) + (sb or 0) * len(bot)
            print(f"      scale={s:4.2f} width={total:6.1f} "
                  f"pred_above={[round(v) for v in above]} "
                  f"match_above={None if sa is None else round(sa, 1)} "
                  f"pred_below={[round(v) for v in below]} "
                  f"match_below={None if sb is None else round(sb, 1)}")


if __name__ == "__main__":
    main()
