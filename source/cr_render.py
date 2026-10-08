#!/usr/bin/env python3
"""Offline line renderer for CUF glyphs + matcher against a screenshot line.

Render model (hypothesis, to be calibrated):
  * the loc string is stored in *visual* order (leftmost character first) and
    the engine draws it left to right without reordering;
  * each codepoint's advance is a model parameter:
        aw     -> the CUF alloc_width
        w      -> the bitmap width
        aw+2   -> alloc_width + 2 (the "+2.82 px/appended glyph" tax seen in v9)
        dp     -> per-codepoint advance fitted from the screenshot
  * a glyph's bitmap is drawn at the pen position; only solid (>=thr) pixels
    count as ink.

The matcher slides the rendered line over the measured screenshot band and
reports the best alignment and residual, so "does this model explain the
pixels" becomes a number.
"""
import os
import struct
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF                 # noqa: E402
from packfile import PackFile       # noqa: E402

SHY = os.path.join(BASE, "reference", "shyizer", "data", "Shyizer Arabic.pack")
SHOTS = os.path.join(BASE, "screenshots")
_cache = {}


def shot(t):
    return os.path.join(SHOTS, f"Total War  Attila Screenshot 2026.10.08 - {t}.png")


def font(leaf):
    if leaf not in _cache:
        pf = PackFile(SHY)
        name = next(n for n in pf.files if n.endswith("\\" + leaf)
                    or n == leaf or n.endswith(leaf))
        _cache[leaf] = CUF.decode(pf.get_file(name))
    return _cache[leaf]


def glyph(c, cp):
    i = c.table[cp]
    if i == 0xFFFF or i >= c.count:
        return None
    ah, aw, w, h = c.dims[i]
    bm = c.bitmaps[i]
    return {"aw": aw, "w": w, "h": h, "ah": ah,
            "bmp": np.frombuffer(bm, dtype=np.uint8).reshape(h, w) if w and h
            else np.zeros((0, 0), np.uint8)}


def advances(c, text, model):
    """-> list of (cp, advance) in visual order."""
    out = []
    for ch in text:
        cp = ord(ch)
        g = glyph(c, cp)
        if g is None:
            out.append((cp, 0))
            continue
        if model == "aw":
            out.append((cp, g["aw"]))
        elif model == "w":
            out.append((cp, g["w"]))
        elif model == "aw+2":
            out.append((cp, g["aw"] + 2))
        else:
            raise ValueError(model)
    return out


def build_pen(c, text, model, adv_override=None):
    """-> (pen positions, glyph list)."""
    pens = []
    x = 0.0
    adv = advances(c, text, model)
    for i, (cp, a) in enumerate(adv):
        pens.append((cp, x))
        x += adv_override.get(i, a) if adv_override else a
    return pens, adv, x


def render_line(c, text, model, adv_override=None, pad=40):
    pens, adv, total = build_pen(c, text, model, adv_override)
    v = c.props["v_size"]
    base = c.props["baseline"]
    W = int(total) + 2 * pad
    canvas = np.zeros((v, W), np.uint8)
    for cp, x in pens:
        g = glyph(c, cp)
        if g is None or g["bmp"].size == 0:
            continue
        h, w = g["bmp"].shape
        y0 = base - h
        x0 = int(round(x)) + pad
        y0 = max(0, min(v - h, y0))
        x0 = max(0, min(W - w, x0))
        np.maximum(canvas[y0:y0 + h, x0:x0 + w], g["bmp"],
                   out=canvas[y0:y0 + h, x0:x0 + w])
    return canvas, pens, adv, total, pad


def measure_band(ts, x0, y0, x1, y1, mode="light", thr=180):
    img = np.array(Image.open(shot(ts)).convert("L"))
    a = img[y0:y1, x0:x1]
    m = (a >= thr) if mode == "light" else (a <= thr)
    return m.astype(np.uint8)


def crop_ink(rendered, threshold=1):
    ys = np.nonzero(rendered.sum(axis=1) > threshold)[0]
    xs = np.nonzero(rendered.sum(axis=0) > threshold)[0]
    return rendered[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]


def best_align(rendered, measured, y_search=6, x_search=14):
    """Slide the rendered mask over the measured mask; return (err, dx, dy).

    err = symmetric difference (false positive + false negative pixels),
    counted over the whole union of the two masks so a wrong total width is
    penalised. Both masks are cropped to their ink bounding boxes, so dx/dy
    is the ink-to-ink offset.
    """
    r = crop_ink(rendered)
    mm = crop_ink(measured)
    mh, mw = mm.shape
    v, W = r.shape
    best = None
    for dy in range(-y_search, y_search + 1):
        for dx in range(-x_search, x_search + 1):
            oy0 = min(0, dy)
            oy1 = max(v, mh + dy)
            ox0 = min(0, dx)
            ox1 = max(W, mw + dx)
            a = np.zeros((oy1 - oy0, ox1 - ox0), np.uint8)
            b = np.zeros_like(a)
            a[-oy0:-oy0 + v, -ox0:-ox0 + W] = r
            b[dy - oy0:dy - oy0 + mh, dx - ox0:dx - ox0 + mw] = mm
            err = int(np.sum(a != b))
            if best is None or err < best[0]:
                best = (err, dx, dy)
    return best


def describe(c, text, model):
    pens, adv, total = build_pen(c, text, model)
    print(f"    {model:5s} total={total:6.1f}  " + " ".join(
        f"{cp:04X}:{a}" for cp, a in [(p[0], a) for p, a in zip(pens, adv)]))
    return total


def try_line(label, ts, x0, y0, x1, y1, text, fonts, mode="light", thr=180):
    print(f"\n=== {label}: {text!r}")
    me = measure_band(ts, x0, y0, x1, y1, mode, thr)
    print(f"  measured band {me.shape[1]}x{me.shape[0]} ink={int(me.sum())}")
    for leaf in fonts:
        c = font(leaf)
        for model in ("aw", "w", "aw+2"):
            canvas, pens, adv, total, pad = render_line(c, text, model)
            res = best_align(canvas, me)
            if res is None:
                print(f"    {leaf:28s} {model:5s} no overlap")
                continue
            err, dx, dy = res
            print(f"    {leaf:28s} {model:5s} total={total:6.1f} "
                  f"dx={dx:4d} dy={dy:3d} err={err:6d}")


if __name__ == "__main__":
    fonts = sys.argv[1:] or ["georgia_italic_12.cuf", "la_gioconda_12.cuf",
                             "la_gioconda_14.cuf", "arialunicode_12.cuf",
                             "georgia_italic_14.cuf", "la_gioconda_16.cuf"]
    # strings in *visual* order as stored
    try_line("custom battle button", "06.52.27.49", 150, 605, 300, 635,
             "\uFE94\uFEBC\uFEBC\uFEA8\uFEE3 \uFE94\uFEDB\uFEAE\uFECC\uFEE3",
             fonts)
