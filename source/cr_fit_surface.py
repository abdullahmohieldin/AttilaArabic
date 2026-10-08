#!/usr/bin/env python3
"""Fit font/scale/advance-model to C1 screenshot lines and report which of
Shyizer's aw / w controls the on-screen pitch.

For every (font, model, scale, tax) the line is rendered and compared to the
measured mask; the best fit gives the effective per-codepoint advance at the
size the surface actually draws. Reports aw, w and the fitted advance for the
codepoints of interest (U+FE92 initial beh, U+FEF2 initial yeh).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R     # noqa: E402
import cr_fit              # noqa: E402

PF = R.PackFile(R.SHY)
R._PACK = PF


def font(leaf):
    if leaf not in R._cache:
        name = next(n for n in PF.files if n.endswith(leaf))
        R._cache[leaf] = R.CUF.decode(PF.get_file(name))
    return R._cache[leaf]


R.font = font
ALL_FONTS = sorted(n.split("\\")[-1] for n in PF.files if n.endswith(".cuf"))
SCALES = [round(0.90 + 0.01 * i, 2) for i in range(71)]   # 0.90 .. 1.60

LINES = {
    "faction_title_ERE": ("06.52.20.33", (872, 95, 1045, 128), "light", 180,
                          "\uFE94\uFEF4\uFED7\uFEAE\uFEB8\uFEDF\uFE8D \uFE8E\uFEE3\uFEED\uFEAD"),
    "custom_battle_hdr": ("06.52.36.59", (885, 92, 1100, 127), "light", 180,
                          "\uFE94\uFEBC\uFEBC\uFEA8\uFEE3 \uFE94\uFEDB\uFEAE\uFECC\uFEE3"),
    "cmp_menu_btn": ("06.52.25.78", (128, 686, 330, 710), "light", 180,
                     "\uFE94\uFEE4\uFEF4\uFEDB \uFE94\uFEE0\uFEE4\uFEA4\uFE8D"),
    "custom_battle_btn": ("06.52.27.49", (155, 606, 296, 632), "light", 180,
                          "\uFE94\uFEBC\uFEBC\uFEA8\uFEE3 \uFE94\uFEDB\uFEAE\uFECC\uFEE3"),
    "hist_battle_btn": ("06.52.27.49", (155, 456, 300, 482), "light", 180,
                        "\uFE94\uFEDB\uFEAE\uFECC \uFE94\uFEF3\uFEAE\uFEF4\uFED7\uFEE8"),
    "wre_title": ("06.52.22.90", (872, 95, 1045, 128), "light", 180,
                  "\uFE94\uFEF4\uFE91\uFEAE\uFED0\uFEDF\uFE8D \uFE8E\uFEE3\uFEED\uFEAD"),
    "ere_desc_L0": ("06.52.20.33", (390, 630, 715, 658), "dark", 110,
                    "\u0640\uFEE5\uFE8E\uFEE8\uFECC\uFEDF\uFE8D \uFED6\uFEE0\uFEC3\uFE83 \uFE94\uFEF4\uFEE7\uFE8E\uFEE3\uFEED\uFEAE\uFEDF\uFE8D \uFE94\uFEF3\uFEAD\uFEEE\uFEC3\uFE8D\uFEAE\uFE92\uFEE3\uFEF9\uFE8D \uFEE1\uFE8E\uFEB4\uFED8\uFEE7\uFE8D"),
}

INTEREST = (0xFE92, 0xFEF2, 0xFEBC, 0xFE94, 0xFE8D)


def run_line(name, fonts, scales, models=("aw", "w"), taxes=(0,), top=6):
    ts, box, mode, thr, text = LINES[name]
    me = cr_fit.measured_mask(ts, *box, mode=mode, thr=thr)
    print(f"\n=== {name} {ts} box={box} ink={int(me.sum())} "
          f"({me.shape[1]}x{me.shape[0]}) text={text!r}")
    res = []
    for leaf in fonts:
        c = font(leaf)
        for model in models:
            for s in scales:
                for tax in taxes:
                    for yo in (-3, -1, 1, 3):
                        canvas, pens, total = cr_fit.render(c, text, s, tax,
                                                            model, yo)
                        r = cr_fit.fit(me, canvas)
                        if r is None:
                            continue
                        err, dx, dy, ri, mi = r
                        res.append((err, leaf, model, s, tax, yo, total))
    res.sort(key=lambda r: r[0])
    print(f"  {'err':>6} {'font':30s} {'model':5s} {'scale':5s} {'tax':3s} "
          f"{'yoff':4s} width")
    for r in res[:top]:
        print(f"  {r[0]:6d} {r[1]:30s} {r[2]:5s} {r[3]:5.2f} {r[4]:3d} "
              f"{r[5]:4d} {r[6]:6.1f}")
    # second stage: with the best (font, model, scale) fixed, fit a per-codepoint
    # advance by 1 px search around the model value
    if not res:
        return
    err, leaf, model, s, tax, yo, total = res[0]
    c = font(leaf)
    print(f"  best: {leaf} {model} scale={s} tax={tax} yoff={yo} "
          f"width={total:.1f}")
    for cp in INTEREST:
        i = c.table[cp]
        if i == 0xFFFF or i >= c.count:
            continue
        ah, aw, w, h = c.dims[i]
        if cp not in [ord(ch) for ch in text]:
            print(f"    U+{cp:04X}: aw={aw} w={w} -> fitted advance "
                  f"(not in string, no measurement)")
            continue
        base = aw if model == "aw" else w
        best = None
        for a in np.arange(max(0.5, base * s - 4), base * s + 5, 0.5):
            ov = {}
            for k, ch in enumerate(text):
                if ord(ch) == cp:
                    ov[k] = float(a)
            canvas, pens, tt = cr_fit.render(c, text, s, tax, model, yo,
                                             adv_override=ov)
            r = cr_fit.fit(me, canvas)
            if r and (best is None or r[0] < best[0]):
                best = (r[0], float(a))
        if best:
            print(f"    U+{cp:04X}: aw={aw} w={w} model*scale={base * s:.1f} "
                  f"-> fitted advance {best[1]:.1f} (err {best[0]})")


if __name__ == "__main__":
    names = sys.argv[1:] or list(LINES)
    for n in names:
        run_line(n, ALL_FONTS, SCALES)
