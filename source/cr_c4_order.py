#!/usr/bin/env python3
"""Render a stored description line from Shyizer glyphs, both orders, to PNG.

Left-to-right pen order (as the engine is claimed to draw) with each glyph
bitmap in its natural orientation. Two variants:
  asis  - stored order, drawn left to right
  rev   - stored order reversed, drawn left to right
  mirror- stored order, drawn left to right, then the whole line mirrored
          horizontally (equivalent to the engine mirroring each rendered line)
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cr_render import font, glyph  # noqa: E402


def render(c, text, gap=0):
    v = c.props["v_size"]
    adv = []
    for ch in text:
        g = glyph(c, ord(ch))
        adv.append(0 if g is None else g["aw"] + gap)
    total = sum(adv) + 8
    canvas = np.zeros((v, total), np.uint8)
    x = 4
    for ch, a in zip(text, adv):
        g = glyph(c, ord(ch))
        if g is not None and g["bmp"].size:
            h, w = g["bmp"].shape
            y0 = max(0, min(v - h, c.props["baseline"] - h))
            x0 = int(round(x))
            canvas[y0:y0 + h, x0:x0 + w] = np.maximum(
                canvas[y0:y0 + h, x0:x0 + w], g["bmp"])
        x += a
    return canvas


def save(canvas, path, scale=3):
    img = Image.fromarray(255 - canvas).resize(
        (canvas.shape[1] * scale, canvas.shape[0] * scale), Image.NEAREST)
    img.save(path)
    return path


def main():
    leaf = sys.argv[1]
    hexline = sys.argv[2]
    text = "".join(chr(int(h, 16)) for h in hexline.split())
    c = font(leaf)
    out = os.path.join(BASE, "logs", "crops", "C4")
    os.makedirs(out, exist_ok=True)
    tag = os.path.splitext(leaf)[0]
    a = render(c, text)
    b = render(c, text[::-1])
    m = np.fliplr(a)
    for name, canv in (("asis", a), ("rev", b), ("mirror", m)):
        p = os.path.join(out, f"{tag}_{name}.png")
        save(canv, p)
        print(name, canv.shape, p)
    print("font", leaf, "v_size", c.props["v_size"],
          "baseline", c.props["baseline"])


if __name__ == "__main__":
    main()
