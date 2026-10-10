#!/usr/bin/env python3
"""C4 final calibration of the advance model (row-band based).

Model, established by the overlay images in logs/crops/C4/ and by
cr_c4_diag.py:

    * the screen order is the STORED order (the engine does not mirror);
    * glyph bitmaps are drawn at their native CUF size;
    * the pen advances by a per-codepoint width
          w(cp) = alpha * aw(cp) + tax          (cp != U+0020)
          w(U+0020) = space
    * the engine honours the hard U+000A in the loc value: every stored line is
      drawn as its own line, at an 18 px pitch (fits la_gioconda_12 exactly:
      v_size 18, line_height 12).

Calibration: row-band line detection in the parchment description boxes gives
one measured ink width per drawn line; the stored line of the same index gives
sum(aw), n_space and n_chars; the three model parameters are then the least
squares solution of  measured_width = alpha*sum_aw + space*n_space + tax*n.

  python source/cr_pitch_fit.py
"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R  # noqa: E402

THR = 70
WINDOW = 205
OUT = os.path.join(BASE, "logs", "cr_c4_pitch_model.json")


def detect_bands(ts, y0, x0, x1, min_ink=5, split=3):
    """-> list of (ytop, ybot, xleft, xright, ink) text bands, top to bottom."""
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    sub = img[y0:y0 + WINDOW, x0:x1] <= THR
    rows = sub.sum(axis=1)
    bands, y = [], 0
    while y < len(rows):
        if rows[y] >= min_ink:
            ys = y
            gap = 0
            while y < len(rows):
                if rows[y] >= min_ink:
                    gap = 0
                else:
                    gap += 1
                    if gap >= split:
                        break
                y += 1
            ye = y - gap
            band = sub[ys:ye]
            cols = band.sum(axis=0)
            xs = np.nonzero(cols)[0]
            if len(xs):
                bands.append((y0 + ys, y0 + ye, int(xs[0]) + x0,
                              int(xs[-1]) + x0, int(band.sum())))
        y += 1
    return bands


def feat(c, text):
    aw = sp = n = 0
    for ch in text:
        n += 1
        if ch == " ":
            sp += 1
            continue
        g = R.glyph(c, ord(ch))
        if g is not None:
            aw += g["aw"]
    return aw, sp, n


def fit_alpha_space(c, lines, spans, min_alpha=1.05):
    feats = [feat(c, t) for t in lines]
    A = np.array([f[0] for f in feats], float)
    S = np.array([f[1] for f in feats], float)
    N = np.array([f[2] for f in feats], float)
    Y = np.array(spans, float)
    best = None
    for alpha in np.arange(min_alpha, 1.50, 0.002):
        for space in np.arange(0.0, 14.01, 0.25):
            base = Y - alpha * A - space * S
            tax = float(np.sum(base * N) / np.sum(N * N))
            res = base - tax * N
            # robust: least-median-of-squares style score (median |res|) plus rms
            rms = float(np.sqrt(np.mean(res ** 2)))
            if best is None or rms < best["rms"]:
                best = {"alpha": float(alpha), "space": float(space),
                        "tax": tax, "rms": rms,
                        "max": float(np.max(np.abs(res))),
                        "resid": [round(float(x), 2) for x in res],
                        "pred": [round(float(x), 1) for x in (Y - res)]}
    return best


def report(c, lines, spans, title, alpha, space, tax):
    print(f"\n--- {title}: alpha={alpha:.3f} space={space:.2f} tax={tax:+.3f}")
    tot_e = 0.0
    for t, y in zip(lines, spans):
        aw, sp, n = feat(c, t)
        pred = alpha * aw + space * sp + tax * n
        tot_e += abs(pred - y)
        print(f"   meas={y:4d} pred={pred:7.1f} err={pred-y:+6.1f} "
              f"sum_aw={aw:6.1f} sp={sp} n={n:3d}  {t[:34]}")
    print(f"   mean|err| = {tot_e/len(spans):.2f} px")


def main():
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    cases = [
        ("ERE", "06.52.20.33", "start_pos_factions_description_2120156326"),
        ("WRE", "06.52.22.90", "start_pos_factions_description_2120156339"),
    ]
    det = {}
    for label, ts, key in cases:
        bands = detect_bands(ts, 600, 366, 690)
        det[label] = (d[key].split("\n"), bands)
        print(f"{label}: stored lines={len(det[label][0])} bands={len(bands)}")
        for i, (ya, yb, a, b, ink) in enumerate(bands):
            st = det[label][0][i] if i < len(det[label][0]) else ""
            print(f"   band{i} y{ya}-{yb} x{a}..{b} w={b-a+1:3d} ink={ink:5d} "
                  f"stored[{i}] n={len(st)}")
    fonts = sorted(n.split("\\")[-1] for n in PackFile(os.path.join(
        BASE, "reference", "shyizer", "data",
        "Shyizer Arabic.pack")).files if n.endswith(".cuf"))
    # lines that are fully inside the box: ERE bands 0-4, WRE bands 0,2,4,5,7,8
    usable = {"ERE": [0, 1, 2, 3, 4], "WRE": [0, 2, 4, 5, 7, 8]}
    results = []
    for leaf in fonts:
        c = R.font(leaf)
        lines, spans, tags = [], [], []
        for label in ("ERE", "WRE"):
            ls, bands = det[label]
            for i in usable[label]:
                if i < len(bands) and i < len(ls):
                    lines.append(ls[i])
                    spans.append(bands[i][3] - bands[i][2] + 1)
                    tags.append(f"{label}{i}")
        best = fit_alpha_space(c, lines, spans)
        results.append({"leaf": leaf, "n": len(lines), "tags": tags, **best})
    results.sort(key=lambda r: (r["rms"], r["max"]))
    print("\n== best 20 (constrained linear model, 11 measurable lines) ==")
    for r in results[:20]:
        print(f"  {r['leaf']:30s} n={r['n']:2d} alpha={r['alpha']:.3f} "
              f"space={r['space']:5.2f} tax={r['tax']:+.3f} rms={r['rms']:6.2f} "
              f"max={r['max']:6.2f}")
    top = results[0]
    c = R.font(top["leaf"])
    lines, spans = [], []
    for label in ("ERE", "WRE"):
        ls, bands = det[label]
        for i in usable[label]:
            if i < len(bands) and i < len(ls):
                lines.append(ls[i])
                spans.append(bands[i][3] - bands[i][2] + 1)
    report(c, lines, spans, f"{top['leaf']} (best lsq)", top["alpha"],
           top["space"], top["tax"])
    # runner-up for comparison
    for r in results[1:4]:
        c2 = R.font(r["leaf"])
        report(c2, lines, spans, f"{r['leaf']} (runner-up)", r["alpha"],
               r["space"], r["tax"])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
