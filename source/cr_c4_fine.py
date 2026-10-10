#!/usr/bin/env python3
"""C4 fine fit: dense (alpha, spc, ytop, shift) grid for one font, scored on
several measured masks; also writes an overlay PNG of the best fit.

  python source/cr_c4_fine.py <font> [--mask g70] [--write]
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R                                    # noqa: E402
from cr_c4_fit2 import (dilate, line_band, fit, evaluate,  # noqa: E402
                        render_line, X0, X1, BAND_Y, WINDOW_H)


def masks():
    img = np.array(Image.open(R.shot("06.52.20.33")).convert("L"))
    sub = img[BAND_Y:BAND_Y + WINDOW_H, X0:X1]
    return {f"g{t}": sub <= t for t in (55, 65, 75, 85)}


def main():
    from packfile import PackFile
    from loc import decode
    leaf = sys.argv[1]
    only = None
    if "--mask" in sys.argv:
        only = sys.argv[sys.argv.index("--mask") + 1]
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    lines = d["start_pos_factions_description_2120156326"].split("\n")[:5]
    c = R.font(leaf)
    mm = masks()
    alphas = np.round(np.arange(1.05, 1.41, 0.01), 2)
    spcs = np.arange(2.5, 12.1, 0.5)
    t0 = time.time()
    res = {}
    for name, raw in mm.items():
        if only and name != only:
            continue
        best = fit(c, lines, dilate(raw, 1), alphas, spcs, (0.0,),
                   range(-2, 12), range(-14, 15), reverse=False)
        per, iou = evaluate(c, lines, raw, best, reverse=False)
        res[name] = {"iou": float(iou), **best, "per": per}
        print(f"{leaf} {name} IoU={iou:.4f} alpha={best['alpha']:.2f} "
              f"spc={best['spc']:.1f} ytop={best['ytop']} shift={best['shift']} "
              f"sym={best['err']} [{time.time()-t0:.0f}s]")
        for p in per:
            print(f"    L{p['line']}: IoU={p['iou']:.3f} sym={p['sym']:5d} "
                  f"meas x{p['meas_x'][0]}..{p['meas_x'][1]} "
                  f"mod x{p['mod_x'][0]}..{p['mod_x'][1]} "
                  f"ink m={p['meas_ink']} r={p['mod_ink']}")
        sys.stdout.flush()
    best_name = max(res, key=lambda k: res[k]["iou"])
    b = res[best_name]
    out = {}
    with open(os.path.join(BASE, "logs", "cr_c4_fine.json"), "w",
              encoding="utf-8") as f:
        json.dump({leaf: res}, f, indent=1)
    if "--write" in sys.argv:
        raw = mm[best_name]
        H, W = raw.shape
        rgb = np.zeros((H, W, 3), np.uint8)
        for li, text in enumerate(lines):
            r = render_line(c, text, b["alpha"], b["spc"], b["pad"], b["shift"],
                            b["ytop"] + 18 * li, H, W, False)
            band = np.zeros((H, W), bool)
            y0 = max(0, 612 - BAND_Y + 18 * li - 7)
            band[y0:y0 + 32] = raw[y0:y0 + 32]
            rgb[..., 0] = np.where(band, 255, rgb[..., 0])
            rgb[..., 1] = np.where(r, 255, rgb[..., 1])
        p = os.path.join(BASE, "logs", "crops", "C4",
                         f"fine_{os.path.splitext(leaf)[0]}_a{b['alpha']}"
                         f"_s{b['spc']}_y{b['ytop']}.png")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        Image.fromarray(rgb).resize((W * 3, H * 3), Image.NEAREST).save(p)
        print(p)


if __name__ == "__main__":
    main()
