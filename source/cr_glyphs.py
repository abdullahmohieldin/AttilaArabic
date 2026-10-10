#!/usr/bin/env python3
"""Connected-component glyph analysis of a cropped text line.

Prints, per component, the bbox and centroid, then the centroid-to-centroid
pitch sequence (the "letter pitch" as seen on screen). Also writes a zoomed,
colour-coded crop with component indices and a 5 px grid so the components can
be matched to codepoints by eye.

  cr_glyphs.py <shot-ts> X0 Y0 X1 Y1 <out.png> [zoom]
"""
import os
import sys

import numpy as np
from PIL import Image

SHOTS = r"D:\AttilaArabic\screenshots"


def shot(t):
    return os.path.join(SHOTS, f"Total War  Attila Screenshot 2026.10.08 - {t}.png")


def components(mask, xoff, yoff, minpx=6):
    """4-connected components via iterative flood fill (small crops only)."""
    h, w = mask.shape
    lab = -np.ones((h, w), dtype=np.int32)
    comps = []
    for yy in range(h):
        for xx in range(w):
            if not mask[yy, xx] or lab[yy, xx] >= 0:
                continue
            cid = len(comps)
            stack = [(yy, xx)]
            lab[yy, xx] = cid
            pts = []
            while stack:
                y, x = stack.pop()
                pts.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] \
                            and lab[ny, nx] < 0:
                        lab[ny, nx] = cid
                        stack.append((ny, nx))
            if len(pts) < minpx:
                lab[lab == cid] = -2
                continue
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            comps.append({
                "id": cid, "n": len(pts),
                "x0": min(xs) + xoff, "x1": max(xs) + 1 + xoff,
                "y0": min(ys) + yoff, "y1": max(ys) + 1 + yoff,
                "cx": float(np.mean(xs)) + xoff, "cy": float(np.mean(ys)) + yoff,
            })
    return comps, lab


def analyze(ts, x0, y0, x1, y1, out=None, zoom=8, mode="light", thr=180,
            minpx=6, label=""):
    img = np.array(Image.open(shot(ts)).convert("L"))
    a = img[y0:y1, x0:x1]
    m = (a >= thr) if mode == "light" else (a <= thr)
    comps, lab = components(m, x0, y0, minpx)
    comps.sort(key=lambda c: c["cx"])
    print(f"\n=== {label or ts}  box ({x0},{y0})-({x1},{y1}) mode={mode} "
          f"thr={thr}: {len(comps)} components")
    for c in comps:
        print(f"  id{c['id']:3d} x{c['x0']:5d}-{c['x1']:5d} "
              f"w={c['x1'] - c['x0']:3d} y{c['y0']:4d}-{c['y1']:4d} "
              f"h={c['y1'] - c['y0']:3d} px={c['n']:5d} cx={c['cx']:8.2f}")
    if len(comps) > 1:
        cs = [c["cx"] for c in comps]
        pitch = [round(cs[i + 1] - cs[i], 2) for i in range(len(cs) - 1)]
        print(f"  centroid pitch: {pitch}")
    if out:
        rgb = np.array(Image.open(shot(ts)).convert("RGB"))[y0:y1, x0:x1].copy()
        rng = np.random.default_rng(7)
        palette = {c["id"]: rng.integers(60, 255, 3) for c in comps}
        for c in comps:
            sel = lab == c["id"]
            rgb[sel] = palette[c["id"]]
        im = Image.fromarray(rgb).resize(
            ((x1 - x0) * zoom, (y1 - y0) * zoom), Image.NEAREST)
        arr = np.array(im)
        # 5 px grid in source space
        for gx in range(x0, x1):
            if gx % 5 == 0:
                xx = (gx - x0) * zoom
                arr[:, xx] = np.where(gx % 25 == 0,
                                      np.array([255, 0, 0]), arr[:, xx])
        for gy in range(y0, y1):
            if gy % 5 == 0:
                yy = (gy - y0) * zoom
                arr[yy, :] = np.where(gy % 25 == 0,
                                      np.array([0, 0, 255]), arr[yy, :])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        Image.fromarray(arr).save(out)
        print(f"  -> {out}")
    return comps


if __name__ == "__main__":
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    out = sys.argv[6] if len(sys.argv) > 6 else None
    zoom = int(sys.argv[7]) if len(sys.argv) > 7 else 8
    thr = int(sys.argv[8]) if len(sys.argv) > 8 else 180
    analyze(ts, x0, y0, x1, y1, out, zoom, thr=thr, label=f"{ts} {x0},{y0}")
