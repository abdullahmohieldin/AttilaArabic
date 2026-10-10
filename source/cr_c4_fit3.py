#!/usr/bin/env python3
"""C4 fit, stage 2: fine (alpha, space advance, y) for the best few fonts.

Stage 1 (cr_c4_fit2.py) gives a coarse alpha/spc; this script refines on a
narrow grid and reports the residual per line plus the model/measured x extents
for every line.

  python source/cr_c4_fit3.py <font> [font...]
"""
import json
import os
import sys
import time

import numpy as np

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cr_c4_fit2 import (dilate, measured, line_band, fit, evaluate,  # noqa: E402
                        X0, X1, OUT)

OUT3 = os.path.join(BASE, "logs", "cr_c4_fit3.json")


def main():
    from packfile import PackFile
    from loc import decode
    import cr_render as R
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    lines = d["start_pos_factions_description_2120156326"].split("\n")[:5]

    raw_masks = {}
    img = None
    from PIL import Image
    for thr in (60, 70, 80):
        img = np.array(Image.open(R.shot("06.52.20.33")).convert("L"))
        raw_masks[f"g{thr}"] = img[604:604 + 146, X0:X1] <= thr
    fonts = [a for a in sys.argv[1:] if a.endswith(".cuf")]
    if not fonts:
        raise SystemExit("give one or more font leaves")
    alphas = np.round(np.arange(1.10, 1.36, 0.01), 2)
    spcs = np.arange(3.0, 12.1, 0.5)
    t0 = time.time()
    out = {}
    for leaf in fonts:
        c = R.font(leaf)
        rec = {}
        for mname, raw in raw_masks.items():
            best = fit(c, lines, dilate(raw, 1), alphas, spcs, (0.0,),
                       range(-2, 12), range(-12, 13), reverse=False)
            per, iou = evaluate(c, lines, raw, best, reverse=False)
            rec[mname] = {"iou": float(iou), **best, "per": per}
            print(f"  {leaf:28s} {mname:5s} IoU={iou:.4f} alpha={best['alpha']:.2f}"
                  f" spc={best['spc']:.1f} ytop={best['ytop']} shift={best['shift']}"
                  f" sym={best['err']} [{time.time()-t0:.0f}s]")
            sys.stdout.flush()
        rec["iou"] = float(np.mean([rec[k]["iou"] for k in raw_masks]))
        out[leaf] = rec
    best_leaf = max(out, key=lambda k: out[k]["iou"])
    print(f"\n== best {best_leaf} (mean IoU {out[best_leaf]['iou']:.4f}) ==")
    b = out[best_leaf]["g70"]
    print(f"  alpha={b['alpha']} spc={b['spc']} ytop={b['ytop']} shift={b['shift']}")
    for p in b["per"]:
        print(f"   L{p['line']}: sym={p['sym']:5d} IoU={p['iou']:.3f} "
              f"meas x{p['meas_x'][0]}..{p['meas_x'][1]} "
              f"mod x{p['mod_x'][0]}..{p['mod_x'][1]} "
              f"ink m={p['meas_ink']} r={p['mod_ink']}")
    with open(OUT3, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {OUT3} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
