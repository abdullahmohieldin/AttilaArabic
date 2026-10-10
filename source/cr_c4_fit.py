#!/usr/bin/env python3
"""C4 calibrator v2: (font, advance scale, per-glyph tax, shared x shift,
shared y offset) fitted on the ERE description box of screenshot 06.52.20.33.

Model (see logs/cr_c4_*):
  * glyph bitmaps are drawn at their NATIVE CUF size (cr_c4_diag.py: measured
    ink heights and stroke widths match the font bitmaps 1:1 while the line is
    1.2-1.6x wider than a scale-1.0 layout);
  * the pen advances by `scale` x the CUF alloc_width; `tax` is an optional
    constant added to every advance;
  * stored index 0 is the RIGHTMOST codepoint on screen, so
        pen_screen(i) = scale * sum(aw[j] for j > i) + tax * (n-1-i).

Both masks live in the same window frame: the model block is rendered with
line i at y = ytop + i * 18 and then compared band by band.

  python source/cr_c4_fit.py [font_leaf ...] [--quick] [--lines N] [--maxscale S]
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
import cr_render as R           # noqa: E402
from cr_desc import local_mask  # noqa: E402

ERE = "06.52.20.33"
BAND_Y = 604            # below the panel's top border rule (y600-601)
WINDOW_H = 146
PITCH = 18
LINE0_TOP = 612
X0, X1 = 366, 690       # left of the flame ornament (x692+) and border (x740+)
OUT = os.path.join(BASE, "logs", "cr_c4_fit.json")


def dilate(m, n=1):
    out = m.copy()
    for _ in range(n):
        d = out.copy()
        d[1:, :] |= out[:-1, :]
        d[:-1, :] |= out[1:, :]
        d[:, 1:] |= out[:, :-1]
        d[:, :-1] |= out[:, 1:]
        out = d
    return out


def measured_masks(ts, x0=X0, x1=X1):
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    sub = img[BAND_Y:BAND_Y + WINDOW_H, x0:x1]
    out = {}
    for thr in (50, 60, 70, 80):
        out[f"g{thr}"] = sub <= thr
    out["l45"] = local_mask(sub, 45)
    return out


def line_band(li):
    y0 = max(0, LINE0_TOP - BAND_Y + PITCH * li - 7)
    return y0, min(WINDOW_H, y0 + PITCH + 14)


def advances(c, text, reverse=True):
    """reverse=True: stored index 0 is the RIGHTMOST screen codepoint
    (pen = sum of aw to the right). reverse=False: stored order is drawn left
    to right (pen = sum of aw to the left)."""
    gs = [R.glyph(c, ord(ch)) for ch in text]
    aw = np.array([0 if g is None else g["aw"] for g in gs], float)
    if reverse:
        cum = np.cumsum(aw[::-1])[::-1] - aw
        idx = np.arange(len(text) - 1, -1, -1)
    else:
        cum = np.cumsum(aw) - aw
        idx = np.arange(len(text))
    return gs, cum, idx


def render_line(c, text, scale, tax, xoff, ytop, H, W, reverse=True):
    canvas = np.zeros((H, W), bool)
    gs, cum, idx = advances(c, text, reverse)
    pens = cum * scale + tax * idx
    basey = c.props["baseline"]
    for i, g in enumerate(gs):
        if g is None or g["bmp"].size == 0:
            continue
        h, w = g["bmp"].shape
        yy = int(round(ytop + basey - h))
        xx = int(round(xoff + pens[i]))
        if xx + w <= 0 or xx >= W or yy + h <= 0 or yy >= H:
            continue
        ys0, ys1 = max(0, yy), min(H, yy + h)
        xs0, xs1 = max(0, xx), min(W, xx + w)
        canvas[ys0:ys1, xs0:xs1] |= (g["bmp"][ys0 - yy:ys1 - yy,
                                              xs0 - xx:xs1 - xx] >= 128)
    return canvas


def fit(c, lines, meas_d, scales, taxes, ytops, shifts, ms=40, reverse=True):
    """meas_d: dilated measured mask of the whole window."""
    H, W = meas_d.shape
    Wp = W + 2 * ms
    mdp = np.pad(meas_d, ((0, 0), (ms, ms)))
    bands = [line_band(li) for li in range(len(lines))]
    cache = {}
    for scale in scales:
        for tax in taxes:
            for li, text in enumerate(lines):
                cache[(scale, tax, li)] = dilate(
                    render_line(c, text, float(scale), float(tax), 0, 0, H, W,
                                reverse), 1)
    best = None
    for scale in scales:
        for tax in taxes:
            for ytop in ytops:
                for s in shifts:
                    total = 0
                    for li in range(len(lines)):
                        y0, y1 = bands[li]
                        r = cache[(scale, tax, li)]
                        dy = ytop + PITCH * li
                        if dy:
                            r = np.roll(r, dy, axis=0)
                        rp = np.pad(r[y0:y1], ((0, 0), (ms, ms)))
                        if s >= 0:
                            total += int(np.sum(mdp[y0:y1, s:] ^ rp[:, :Wp - s]))
                        else:
                            total += int(np.sum(mdp[y0:y1, :Wp + s] ^ rp[:, -s:]))
                    if best is None or total < best["err"]:
                        best = {"err": total, "scale": float(scale),
                                "tax": float(tax), "ytop": int(ytop),
                                "shift": int(s)}
    return best


def evaluate(c, lines, meas_raw, p, reverse=True):
    H, W = meas_raw.shape
    tot_sym = tot_union = 0
    per = []
    for li, text in enumerate(lines):
        y0, y1 = line_band(li)
        band = np.zeros((H, W), bool)
        band[y0:y1] = meas_raw[y0:y1]
        r = render_line(c, text, p["scale"], p["tax"], p["shift"], 0, H, W,
                        reverse)
        dy = p["ytop"] + PITCH * li
        if dy:
            r = np.roll(r, dy, axis=0)
        rd = dilate(r, 1)
        bd = dilate(band, 1)
        sym = int(np.sum(rd ^ bd))
        uni = int(np.sum(rd | bd))
        tot_sym += sym
        tot_union += uni
        bc = np.nonzero(band.sum(axis=0))[0]
        rc = np.nonzero(r[y0:y1].sum(axis=0))[0]
        per.append({"line": li, "sym": sym, "union": uni,
                    "iou": float(1 - sym / max(1, uni)),
                    "meas_ink": int(band.sum()), "mod_ink": int(r.sum()),
                    "meas_x": [int(bc[0]) + X0, int(bc[-1]) + X0] if len(bc) else [],
                    "mod_x": [int(rc[0]) + X0, int(rc[-1]) + X0] if len(rc) else []})
    return per, 1 - tot_sym / max(1, tot_union)


def main():
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    ere = d["start_pos_factions_description_2120156326"].split("\n")
    nlines = int(sys.argv[sys.argv.index("--lines") + 1]) if "--lines" in sys.argv \
        else 5
    maxscale = float(sys.argv[sys.argv.index("--maxscale") + 1]) \
        if "--maxscale" in sys.argv else 1.61
    lines = ere[:nlines]

    meas = measured_masks(ERE)
    print(f"measured window x{X0}..{X1} y{BAND_Y}..{BAND_Y+WINDOW_H}")
    for k, m in meas.items():
        print(f"  {k:5s} ink={int(m.sum()):5d} per-line="
              f"{[int(m[line_band(i)[0]:line_band(i)[1]].sum()) for i in range(nlines)]}")

    all_fonts = sorted(n.split("\\")[-1] for n in PackFile(os.path.join(
        BASE, "reference", "shyizer", "data",
        "Shyizer Arabic.pack")).files if n.endswith(".cuf"))
    args = [a for a in sys.argv[1:] if a.endswith(".cuf")]
    fonts = args or all_fonts
    quick = "--quick" in sys.argv
    scales = np.round(np.arange(1.00, maxscale, 0.02 if quick else 0.01), 2)
    taxes = (0.0, 0.5, -0.5)
    ytops = range(-4, 9)
    shifts = range(-20, 21)
    t0 = time.time()
    results = []
    for leaf in fonts:
        c = R.font(leaf)
        for reverse in (False, True):
            rec = {"leaf": leaf, "reverse": reverse, "by_mask": {}}
            for mname in ("g50", "g60", "g70", "g80", "l45"):
                mm = meas[mname]
                best = fit(c, lines, dilate(mm, 1), scales, taxes, ytops, shifts,
                           reverse=reverse)
                per, iou = evaluate(c, lines, mm, best, reverse)
                rec["by_mask"][mname] = {"iou": float(iou), **best, "per": per}
                print(f"  {leaf:30s} rev={int(reverse)} {mname:5s} IoU={iou:.4f}"
                      f" scale={best['scale']:.2f} tax={best['tax']:+.1f}"
                      f" ytop={best['ytop']:2d} sym={best['err']:6d}"
                      f" shift={best['shift']:3d}  [{time.time()-t0:.0f}s]")
                sys.stdout.flush()
            rec["iou"] = float(np.mean([rec["by_mask"][k]["iou"]
                                        for k in ("g50", "g60", "g70")]))
            results.append(rec)
    results.sort(key=lambda r: -r["iou"])
    print("\n== top 12 by mean IoU (g50/g60/g70) ==")
    for r in results[:12]:
        b = r["by_mask"]["g60"]
        print(f"  {r['leaf']:32s} rev={int(r['reverse'])} IoU={r['iou']:.4f} "
              f"g60 scale={b['scale']:.2f} tax={b['tax']:+.1f} shift={b['shift']} "
              f"mod_x={[p['mod_x'] for p in b['per']]}")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"ere": results}, f, indent=1)
    print(f"\nwrote {OUT} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
