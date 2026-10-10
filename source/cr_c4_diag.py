#!/usr/bin/env python3
"""C4 diagnostic: does the engine scale glyph bitmaps, advances, or both?

Renders one ERE description line (and its mirror) with independent
  gscale - multiplier on glyph bitmap w and h
  ascale - multiplier on the per-codepoint advance
and prints the ink bounding box, ink pixel count and stroke-height histogram,
side by side with the measured values from the screenshot band.
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R           # noqa: E402
from cr_desc import local_mask  # noqa: E402


def scale_bmp(bm, gscale):
    if gscale == 1.0 or bm.size == 0:
        return bm
    h, w = bm.shape
    nh, nw = max(1, int(round(h * gscale))), max(1, int(round(w * gscale)))
    yi = np.clip((np.arange(nh) / gscale).astype(int), 0, h - 1)
    xi = np.clip((np.arange(nw) / gscale).astype(int), 0, w - 1)
    return bm[np.ix_(yi, xi)]


def render(c, text, gscale, ascale, tax=0.0, mirror=False):
    v = c.props["v_size"]
    base = c.props["baseline"]
    advs = []
    for ch in text:
        g = R.glyph(c, ord(ch))
        a = 0.0 if g is None else g["aw"]
        advs.append(a * ascale + tax)
    total = int(round(sum(advs))) + 4
    vv = int(round(v * gscale)) + 2
    canvas = np.zeros((vv, total), np.uint8)
    x = 0.0
    for ch, a in zip(text, advs):
        g = R.glyph(c, ord(ch))
        if g is not None and g["bmp"].size:
            bm = scale_bmp(g["bmp"], gscale)
            h, w = bm.shape
            y0 = max(0, min(vv - h, int(round((base - g["h"] * 1.0) * gscale)) + 1))
            x0 = max(0, min(total - w, int(round(x))))
            canvas[y0:y0 + h, x0:x0 + w] = np.maximum(
                canvas[y0:y0 + h, x0:x0 + w], (bm >= 128) * 255)
        x += a
    if mirror:
        canvas = np.fliplr(canvas).copy()
    return canvas


def stats(mask, name):
    ys = np.nonzero(mask.sum(axis=1) > 0)[0]
    xs = np.nonzero(mask.sum(axis=0) > 0)[0]
    hh = []
    for x in xs:
        col = np.nonzero(mask[:, x])[0]
        if len(col):
            hh.append(col[-1] - col[0] + 1)
    hh = np.array(hh)
    print(f"  {name:34s} bbox {xs[0]}..{xs[-1]} (w{xs[-1]-xs[0]+1}) "
          f"y{ys[0]}..{ys[-1]} (h{ys[-1]-ys[0]+1}) ink={int(mask.sum())} "
          f"colh-med={int(np.median(hh))} p90={int(np.percentile(hh, 90))} "
          f"max={int(hh.max())}")


def main():
    from packfile import PackFile
    from loc import decode
    pf = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(pf.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    stored = d["start_pos_factions_description_2120156326"].split("\n")
    leaf = sys.argv[1] if len(sys.argv) > 1 else "georgia_italic_12.cuf"
    li = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    c = R.font(leaf)
    text = stored[li]

    img = np.array(Image.open(R.shot("06.52.20.33")).convert("L"))
    mm = local_mask(img[600:710, 360:760], 35)
    mm[:, 690 - 360:] = False
    Y0 = 612 + li * 18
    band = mm[Y0 - 600:Y0 - 600 + 18, 6 - 0:330]
    print(f"font={leaf} line={li} stored n={len(text)}")
    stats(band.astype(np.uint8), "MEASURED")
    for gscale in (1.0, 1.45):
        for ascale in (1.0, 1.45):
            for mirror in (False, True):
                r = render(c, text, gscale, ascale, mirror=mirror)
                stats((r >= 128).astype(np.uint8),
                      f"g={gscale} a={ascale} mirror={mirror}")


if __name__ == "__main__":
    main()
