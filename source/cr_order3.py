#!/usr/bin/env python3
"""Whole-line order test: render a loc value's codepoints in stored order and
in reversed order with the SAME font/advance/offset model, and report which
one matches the screenshot mask. Only the order differs, so this is a direct
test of the drawn direction.

  cr_order3.py <ts> X0 Y0 X1 Y1 "<stored text>" [--thr 180] [--fonts a,b]
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

PF = R.PackFile(R.SHY)
_C = {}


def font(leaf):
    if leaf not in _C:
        n = next(x for x in PF.files if x.endswith(leaf))
        _C[leaf] = R.CUF.decode(PF.get_file(n))
    return _C[leaf]


def render(c, text, adv, scale, yoff=0):
    """place each codepoint bitmap at its own advance (adv per cp, or a
    single value) on a canvas of the font's v_size."""
    v = c.props["v_size"]
    base = c.props["baseline"]
    pens, x = [], 0.0
    for ch in text:
        cp = ord(ch)
        g = R.glyph(c, cp)
        pens.append((cp, g, x))
        x += (adv[0] * (g["aw"] if g else 0) + adv[1]) * scale
    W = int(x) + 4
    canvas = np.zeros((v, W), np.uint8)
    for cp, g, x in pens:
        if g is None or g["bmp"].size == 0:
            continue
        h, w = g["bmp"].shape
        y0 = base - h + yoff
        x0 = int(round(x))
        if y0 < 0 or y0 + h > v or x0 < 0 or x0 + w > W:
            continue
        np.maximum(canvas[y0:y0 + h, x0:x0 + w], g["bmp"],
                   out=canvas[y0:y0 + h, x0:x0 + w])
    return canvas


def bbox_ink(m):
    ys = np.nonzero(m.sum(axis=1))[0]
    xs = np.nonzero(m.sum(axis=0))[0]
    if not len(ys) or not len(xs):
        return None
    return m[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def score(rendered, measured):
    r = bbox_ink(rendered)
    m = bbox_ink(measured)
    if r is None or m is None:
        return None
    best = None
    for dy in range(-25, 26):
        for dx in range(-20, 21):
            H = max(r.shape[0], m.shape[0] + dy) - min(0, dy)
            W = max(r.shape[1], m.shape[1] + dx) - min(0, dx)
            a = np.zeros((H, W), np.uint8)
            b = np.zeros((H, W), np.uint8)
            a[-min(0, dy):-min(0, dy) + r.shape[0],
              -min(0, dx):-min(0, dx) + r.shape[1]] = r
            b[dy - min(0, dy):dy - min(0, dy) + m.shape[0],
              dx - min(0, dx):dx - min(0, dx) + m.shape[1]] = m
            e = int(np.sum(a != b))
            if best is None or e < best[0]:
                best = (e, dx, dy)
    return best


def main():
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    text = sys.argv[6]
    thr = 180
    fonts = ["georgia_italic_12.cuf", "georgia_italic_14.cuf",
             "georgia_italic_16.cuf", "la_gioconda_12.cuf",
             "la_gioconda_14.cuf", "la_gioconda_16.cuf",
             "arialunicode_12.cuf"]
    for i, a in enumerate(sys.argv):
        if a == "--thr":
            thr = int(sys.argv[i + 1])
        if a == "--fonts":
            fonts = sys.argv[i + 1].split(",")
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    me = (img[y0:y1, x0:x1] >= thr).astype(np.uint8)
    me = bbox_ink(me)
    print(f"shot {ts} box=({x0},{y0})-({x1},{y1}) thr={thr} "
          f"measured ink bbox {me.shape[1]}x{me.shape[0]} px={int(me.sum())}")
    print(f"text: {text!r}")
    print(f"  {'font':26s} {'order':9s} {'err':>6} {'dx':>4} {'dy':>4} "
          f"{'k(aw)':>6} {'b':>5} {'scale':>6} {'rendered w':>10}")
    results = []
    for leaf in fonts:
        c = font(leaf)
        for label, txt in (("stored", text), ("reversed", text[::-1])):
            best = None
            for k in (0.8, 0.9, 1.0, 1.1):
                for b in (0, 2, 4, 6):
                    for s in (0.8, 0.9, 1.0, 1.1, 1.2):
                        for yo in (0, 2, 4):
                            canv = render(c, txt, (k, b), s, yo)
                            r = score(canv, me)
                            if r is None:
                                continue
                            if best is None or r[0] < best[0]:
                                bb = bbox_ink(canv)
                                best = (r[0], r[1], r[2], k, b, s,
                                        bb.shape[1] if bb is not None else 0)
            if best:
                results.append((leaf, label, best))
    results.sort(key=lambda r: r[2][0])
    for leaf, label, b in results[:14]:
        print(f"  {leaf:26s} {label:9s} {b[0]:6d} {b[1]:4d} {b[2]:4d} "
              f"{b[3]:6.1f} {b[4]:5d} {b[5]:6.2f} {b[6]:10d}")
    # per font, who wins
    print("  per-font winner:")
    seen = {}
    for leaf, label, b in sorted(results, key=lambda r: (r[0], r[2][0])):
        if leaf in seen:
            continue
        seen[leaf] = (label, b[0])
    for leaf, (label, err) in seen.items():
        print(f"    {leaf:26s} {label:9s} err={err}")
    stored_wins = sum(1 for v in seen.values() if v[0] == "stored")
    print(f"  stored order wins in {stored_wins}/{len(seen)} fonts")


if __name__ == "__main__":
    main()
