#!/usr/bin/env python3
"""Overlay a candidate model render on the measured ERE band -> PNG.

  python source/cr_c4_overlay.py <font> <scale> [tax] [shift] [ytop] [reverse]
"""
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cr_c4_fit import render_line, measured_masks, BAND_Y, X0, X1, PITCH, LINE0_TOP  # noqa: E402
import cr_render as R  # noqa: E402


def main():
    from packfile import PackFile
    from loc import decode
    leaf = sys.argv[1]
    scale = float(sys.argv[2])
    tax = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    shift = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    ytop = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    reverse = bool(int(sys.argv[6])) if len(sys.argv) > 6 else False
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    lines = d["start_pos_factions_description_2120156326"].split("\n")[:5]
    c = R.font(leaf)
    meas = measured_masks("06.52.20.33")["g70"]
    H, W = meas.shape
    out = np.zeros((H, W, 3), np.uint8)
    print("red = measured, green = model, yellow = overlap")
    for li, text in enumerate(lines):
        r = render_line(c, text, scale, tax, shift, ytop + PITCH * li, H, W,
                        reverse)
        band = np.zeros((H, W), bool)
        y0 = max(0, LINE0_TOP - BAND_Y + PITCH * li - 7)
        band[y0:y0 + PITCH + 14] = meas[y0:y0 + PITCH + 14]
        out[..., 0] = np.where(band, 255, out[..., 0])
        out[..., 1] = np.where(r, 255, out[..., 1])
        rc = np.nonzero(r.sum(axis=0))[0]
        bc = np.nonzero(band.sum(axis=0))[0]
        print(f"  L{li}: meas x{X0+bc[0] if len(bc) else -1}.."
              f"{X0+bc[-1] if len(bc) else -1}  "
              f"mod x{X0+rc[0] if len(rc) else -1}..{X0+rc[-1] if len(rc) else -1}"
              f"  ink m={int(band.sum())} r={int(r.sum())}")
    img = Image.fromarray(out).resize((W * 3, H * 3), Image.NEAREST)
    tag = f"{os.path.splitext(leaf)[0]}_{scale}_t{tax}_s{shift}_y{ytop}_r{int(reverse)}"
    p = os.path.join(BASE, "logs", "crops", "C4", f"overlay_{tag}.png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    print(p)


if __name__ == "__main__":
    main()
