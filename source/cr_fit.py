#!/usr/bin/env python3
"""Fit a font + advance model to a measured text line in a screenshot.

Model: the loc string is stored in visual order and drawn left to right; each
codepoint's advance = (font aw or w) * scale + tax; the bitmap is drawn at the
pen position, vertically placed to best match. The fit searches font, scale,
tax, vertical placement and x offset, and reports the best symmetric-difference
residual plus the resulting per-codepoint advances (the on-screen pitch).

  cr_fit.py "<ts>" X0 Y0 X1 Y1 "<visual-order text>" [--mode light|dark]
            [--thr 180] [--fonts a,b] [--top 8] [--models aw,w,aw+tax]
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

OUT = os.path.join(r"D:\AttilaArabic", "logs", "crops", "C1")


def glyphs(c, text):
    return [(ord(ch), R.glyph(c, ord(ch))) for ch in text]


def render(c, text, scale, tax, model="aw", yoff=0, adv_override=None):
    gl = glyphs(c, text)
    v = c.props["v_size"]
    base = c.props["baseline"]
    pens, x = [], 0.0
    for k, (cp, g) in enumerate(gl):
        pens.append((cp, g, x))
        if g is None:
            continue
        a = g["aw"] if model == "aw" else g["w"]
        a = a * scale + tax
        if adv_override and k in adv_override:
            a = adv_override[k]
        x += a
    W = int(x) + 2
    canvas = np.zeros((v, W), np.uint8)
    for cp, g, x in pens:
        if g is None or g["bmp"].size == 0:
            continue
        h, w = g["bmp"].shape
        y0 = base - h + yoff
        x0 = int(round(x))
        if y0 < 0 or y0 + h > v or x0 + w > W:
            continue
        np.maximum(canvas[y0:y0 + h, x0:x0 + w], g["bmp"],
                   out=canvas[y0:y0 + h, x0:x0 + w])
    return canvas, pens, x


def sd_at(a, off, shape):
    """Place mask `a` into a canvas of `shape` at integer offset (dx,dy)."""
    dx, dy = off
    H, W = shape
    out = np.zeros(shape, np.uint8)
    ay0, ax0 = max(0, -dy), max(0, -dx)
    by0, bx0 = max(0, dy), max(0, dx)
    h = min(a.shape[0] - ay0, H - by0)
    w = min(a.shape[1] - ax0, W - bx0)
    if h > 0 and w > 0:
        out[by0:by0 + h, bx0:bx0 + w] = a[ay0:ay0 + h, ax0:ax0 + w]
    return out


def fit(measured, rendered, ymax=6, xmax=6):
    """return (err, dx, dy) minimising the symmetric difference."""
    mh, mw = measured.shape
    rh, rw = rendered.shape
    # ink bounding boxes make the search cheap and meaningful
    my = np.nonzero(measured.sum(axis=1))[0]
    mx = np.nonzero(measured.sum(axis=0))[0]
    if not len(my) or not len(mx):
        return None
    m = measured[my[0]:my[-1] + 1, mx[0]:mx[-1] + 1]
    ry = np.nonzero(rendered.sum(axis=1))[0]
    rx = np.nonzero(rendered.sum(axis=0))[0]
    if not len(ry) or not len(rx):
        return None
    r = rendered[ry[0]:ry[-1] + 1, rx[0]:rx[-1] + 1]
    best = None
    for dy in range(-ymax, ymax + 1):
        for dx in range(-xmax, xmax + 1):
            H = max(r.shape[0], m.shape[0] + dy) - min(0, dy)
            W = max(r.shape[1], m.shape[1] + dx) - min(0, dx)
            a = sd_at(r, (-min(0, dx), -min(0, dy)), (H, W))
            b = sd_at(m, (dx - min(0, dx), dy - min(0, dy)), (H, W))
            err = int(np.sum(a != b))
            if best is None or err < best[0]:
                best = (err, dx, dy, a.sum(), b.sum())
    return best


def measured_mask(ts, x0, y0, x1, y1, mode, thr):
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    a = img[y0:y1, x0:x1]
    m = (a >= thr) if mode == "light" else (a <= thr)
    return m.astype(np.uint8)


def run(ts, box, text, mode="light", thr=180, fonts=None, top=8,
        scales=None, taxes=(0, 1, 2), models=("aw", "w"), yoffs=(-4, 4)):
    x0, y0, x1, y1 = box
    me = measured_mask(ts, x0, y0, x1, y1, mode, thr)
    print(f"line {text!r} box={box} measured ink={int(me.sum())} "
          f"size={me.shape[1]}x{me.shape[0]}")
    if scales is None:
        scales = [round(0.80 + 0.01 * i, 2) for i in range(56)]
    results = []
    for leaf in fonts:
        c = R.font(leaf)
        for model in models:
            for s in scales:
                for tax in taxes:
                    for yo in yoffs:
                        canvas, pens, total = render(c, text, s, tax, model, yo)
                        res = fit(me, canvas)
                        if res is None:
                            continue
                        err, dx, dy, ri, mi = res
                        results.append((err, leaf, model, s, tax, yo, total, dx, dy))
    results.sort(key=lambda r: r[0])
    print(f"  {'err':>6} {'font':28s} {'model':5s} {'scale':5s} {'tax':3s} "
          f"{'yoff':4s} {'width':>6} dx dy")
    for r in results[:top]:
        print(f"  {r[0]:6d} {r[1]:28s} {r[2]:5s} {r[3]:5.2f} {r[4]:3d} "
              f"{r[5]:4d} {r[6]:6.1f} {r[7]:3d} {r[8]:3d}")
    return results


if __name__ == "__main__":
    ts = sys.argv[1]
    box = tuple(int(v) for v in sys.argv[2:6])
    text = sys.argv[6]
    kw = {}
    args = sys.argv[7:]
    for i, a in enumerate(args):
        if a == "--mode":
            kw["mode"] = args[i + 1]
        elif a == "--thr":
            kw["thr"] = int(args[i + 1])
        elif a == "--fonts":
            kw["fonts"] = args[i + 1].split(",")
        elif a == "--top":
            kw["top"] = int(args[i + 1])
        elif a == "--models":
            kw["models"] = args[i + 1].split(",")
        elif a == "--scales":
            kw["scales"] = [float(v) for v in args[i + 1].split(",")]
    if "fonts" not in kw:
        pf = R.PackFile(R.SHY)
        kw["fonts"] = sorted(n.split("\\")[-1] for n in pf.files
                             if n.endswith(".cuf"))
    run(ts, box, text, **kw)
