#!/usr/bin/env python3
"""C4 calibrator step 1: which glyph order, which font, what scale?

For each candidate font, each stored ERE description line is rendered in
left-to-right pen order (the order the engine is claimed to draw) and compared
to the measured column ink profile of the matching screenshot band.

Two render variants:
  asis   glyph bitmaps drawn upright, stored order left to right
  mirror stored order left to right, whole line then flipped horizontally
         (equivalent to the engine mirroring each rendered line, with the
          pen order being the reverse of the stored order)

Score = 1 - symmetric_difference/profile_union on the binarised column
profile, maximised over a horizontal shift. Reported per font.
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R              # noqa: E402
from cr_desc import local_mask     # noqa: E402

ERE_TS = "06.52.20.33"
X0, X1 = 360, 760
Y_TOP = 606
LINE_CUT = 18
DELTA = 35


def line_bands():
    """-> list of (y0, y1) per drawn line, derived from the measured mask."""
    img = np.array(Image.open(R.shot(ERE_TS)).convert("L"))
    m = local_mask(img[600:710, X0:X1], DELTA)
    # text rows only: exclude panel border columns x>=740 and the flame x>=690
    m[:, (740 - X0):] = False
    rows = m.sum(axis=1)
    return m, rows


def text_columns(m, y0, y1, xmin=366, xmax=725):
    band = m[y0 - 600:y1 - 600, (xmin - X0):(xmax - X0)]
    return band.sum(axis=0).astype(np.float64)


def render_profile(c, text, scale, tax, cap=255, thr=128, gapmode="aw",
                   mirror=False):
    """-> (columns, width) of the rendered line as a column ink count."""
    advs, glyphs = [], []
    for ch in text:
        g = R.glyph(c, ord(ch))
        glyphs.append(g)
        a = 0 if g is None else (g["aw"] if gapmode == "aw" else g["w"])
        advs.append(a)
    pens = np.cumsum([0.0] + advs[:-1]) if advs else np.zeros(0)
    widths = [0 if g is None else g["w"] for g in glyphs]
    total = int(round((sum(advs) + tax * len(advs)) * scale)) + 2
    total = max(total, 1)
    prof = np.zeros(total, np.float64)
    for g, pen in zip(glyphs, pens):
        if g is None or g["bmp"].size == 0 or g["w"] == 0:
            continue
        w = max(1, int(round(g["w"] * scale)))
        x0 = int(round((pen + tax * 0) * scale))
        bm = g["bmp"]
        colmax = bm.max(axis=0).astype(np.float64) if bm.size else np.zeros(0)
        if w != len(colmax):
            idx = np.clip((np.arange(w) / scale).astype(int), 0, len(colmax) - 1)
            colmax = colmax[idx]
        xs = np.clip(np.arange(x0, x0 + w), 0, total - 1)
        np.maximum.at(prof, xs, colmax)
    if mirror:
        prof = prof[::-1].copy()
    return prof


def best_shift_err(a, b, max_shift=40):
    """IoU-based cost between two ink-count profiles, over integer shifts."""
    a = (a > 0).astype(np.uint8)
    b = (b > 0).astype(np.uint8)
    best = None
    for s in range(-max_shift, max_shift + 1):
        oa = max(0, -s)
        ob = max(0, s)
        n = max(len(a) + oa, len(b) + ob)
        A = np.zeros(n, np.uint8)
        B = np.zeros(n, np.uint8)
        A[oa:oa + len(a)] = a
        B[ob:ob + len(b)] = b
        inter = int(np.sum(A & B))
        union = int(np.sum(A | B))
        iou = inter / union if union else 0.0
        if best is None or iou > best[0]:
            best = (iou, s, inter, union)
    return best


def main():
    from packfile import PackFile
    from loc import decode
    pf = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(pf.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    stored = d["start_pos_factions_description_2120156326"].split("\n")

    m, _ = line_bands()
    bands = [(612, 630), (630, 648), (648, 666), (666, 684), (684, 702)]
    bands = bands[:len(stored)]
    fonts = sorted(n.split("\\")[-1] for n in PackFile(
        os.path.join(BASE, "reference", "shyizer", "data",
                     "Shyizer Arabic.pack")).files if n.endswith(".cuf"))

    print(f"fonts={len(fonts)} bands={len(bands)}")
    measured = [text_columns(m, y0, y1) for (y0, y1) in bands]
    for (y0, y1), tx in zip(bands, stored):
        c = R.glyph
        print(f"  band {y0}-{y1} stored n={len(tx)} meas ink cols="
              f"{int((measured[bands.index((y0, y1))] > 0).sum())}")
    results = []
    scales = np.arange(0.4, 2.21, 0.05)
    for leaf in fonts:
        c = R.font(leaf)
        for mirror in (False, True):
            best = (0.0, 0.0)
            for scale in scales:
                tot = 0.0
                for meas, text in zip(measured, stored):
                    prof = render_profile(c, text, float(scale), 0.0,
                                          mirror=mirror)
                    iou = best_shift_err(meas, prof)[0]
                    tot += iou
                tot /= len(measured)
                if tot > best[0]:
                    best = (tot, float(scale))
            results.append((best[0], leaf, best[1], mirror))
    results.sort(reverse=True)
    for iou, leaf, scale, mirror in results[:30]:
        print(f"  IoU={iou:.4f}  {leaf:32s} scale={scale:.2f} "
              f"mirror={mirror}")


if __name__ == "__main__":
    main()
