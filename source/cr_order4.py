#!/usr/bin/env python3
"""Render a stored loc value in stored order, word-reversed order and fully
reversed order, and save each next to the measured screenshot mask so the
drawn direction can be judged by eye and by overlap score."""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

PF = R.PackFile(R.SHY)
OUT = r"D:\AttilaArabic\logs\crops\C4_order"


def font(leaf):
    n = next(x for x in PF.files if x.endswith(leaf))
    return R.CUF.decode(PF.get_file(n))


def render(c, text, scale=1.0, tax=0.0):
    v = c.props["v_size"]
    base = c.props["baseline"]
    pens, x = [], 0.0
    for ch in text:
        g = R.glyph(c, ord(ch))
        pens.append((g, x))
        x += (g["aw"] * scale + tax) if g else 0
    W = int(x) + 6
    H = v + 20
    canvas = np.zeros((H, W), np.uint8)
    for g, x0f in pens:
        if g is None or g["bmp"].size == 0:
            continue
        h, w = g["bmp"].shape
        y0 = base - h + 10
        x0 = int(round(x0f))
        sy0, sy1 = max(0, y0), min(H, y0 + h)
        sx0, sx1 = max(0, x0), min(W, x0 + w)
        if sy1 <= sy0 or sx1 <= sx0:
            continue
        canvas[sy0:sy1, sx0:sx1] = np.maximum(
            canvas[sy0:sy1, sx0:sx1],
            g["bmp"][sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0])
    return canvas


def trim(a, thr=1):
    ys = np.nonzero((a > thr).sum(axis=1))[0]
    xs = np.nonzero((a > thr).sum(axis=0))[0]
    if not len(ys) or not len(xs):
        return a
    return a[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def sd(a, b):
    a, b = trim(a), trim(b)
    H = max(a.shape[0], b.shape[0])
    W = max(a.shape[1], b.shape[1])
    best = None
    for dy in range(-12, 13):
        for dx in range(-12, 13):
            A = np.zeros((H + 24, W + 24), np.uint8)
            B = np.zeros((H + 24, W + 24), np.uint8)
            A[12:12 + a.shape[0], 12:12 + a.shape[1]] = a > 0
            B[12 + dy:12 + dy + b.shape[0], 12 + dx:12 + dx + b.shape[1]] = b > 0
            e = int(np.sum(A != B))
            if best is None or e < best[0]:
                best = (e, dx, dy)
    return best


def main():
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    text = sys.argv[6]
    thr = int(sys.argv[7]) if len(sys.argv) > 7 else 180
    fonts = sys.argv[8].split(",") if len(sys.argv) > 8 else [
        "georgia_italic_12.cuf", "georgia_italic_14.cuf",
        "georgia_italic_16.cuf", "la_gioconda_12.cuf", "la_gioconda_16.cuf",
        "arialunicode_12.cuf"]
    img = np.array(Image.open(R.shot(ts)).convert("L"))[y0:y1, x0:x1]
    me = trim((img >= thr).astype(np.uint8))
    os.makedirs(OUT, exist_ok=True)
    variants = [("stored", text),
                ("wordrev", " ".join(w[::-1] for w in text.split(" "))),
                ("fullrev", text[::-1])]
    print(f"shot {ts} box=({x0},{y0})-({x1},{y1}) thr={thr}")
    print(f"measured ink {me.shape[1]}x{me.shape[0]} px={int(me.sum())}")
    for nm, txt in variants:
        print(f"  {nm:8s}: {txt!r}")
    Image.fromarray(255 - me * 255).resize(
        (me.shape[1] * 5, me.shape[0] * 5), Image.NEAREST).save(
        os.path.join(OUT, "measured.png"))
    print(f"  {'font':24s} {'variant':8s} {'ink':>5} {'w':>4} {'sd':>6} "
          f"{'dx':>4} {'dy':>4}")
    tally = {}
    for leaf in fonts:
        c = font(leaf)
        for nm, txt in variants:
            canv = trim(render(c, txt))
            r = sd(canv, me)
            tally.setdefault(leaf, []).append((r[0], nm))
            print(f"  {leaf:24s} {nm:8s} {int((canv > 0).sum()):5d} "
                  f"{canv.shape[1]:4d} {r[0]:6d} {r[1]:4d} {r[2]:4d}")
            Image.fromarray(255 - canv).resize(
                (canv.shape[1] * 5, canv.shape[0] * 5), Image.NEAREST).save(
                os.path.join(OUT, f"{leaf.split('.')[0]}_{nm}.png"))
    print("  winner per font:")
    for leaf, lst in tally.items():
        lst.sort()
        print(f"    {leaf:24s} {lst[0][1]:8s} sd={lst[0][0]}")
    wins = sum(1 for lst in tally.values() if sorted(lst)[0][1] == "stored")
    print(f"  stored wins in {wins}/{len(tally)} fonts")


if __name__ == "__main__":
    main()
