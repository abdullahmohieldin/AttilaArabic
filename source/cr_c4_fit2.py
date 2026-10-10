#!/usr/bin/env python3
"""C4 calibrator v3: split the horizontal model into
      alpha - scale on the advance of every NON-space codepoint
      spc   - advance used for U+0020
      pad   - constant added to every non-space advance (default 0)
and fit (alpha, spc, pad, y offset) by minimising the symmetric difference of
the rendered mask against the measured ink mask.

Word-level correlation is used first to get a robust alpha estimate from the
ink profiles alone (no mask dilation), then the mask fit refines it.

  python source/cr_c4_fit2.py [font_leaf ...] [--quick]
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
BAND_Y = 604
WINDOW_H = 146
PITCH = 18
LINE0_TOP = 612
X0, X1 = 366, 690
OUT = os.path.join(BASE, "logs", "cr_c4_fit2.json")


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


def measured(ts="06.52.20.33", thr=70):
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    return img[BAND_Y:BAND_Y + WINDOW_H, X0:X1] <= thr


def line_band(li):
    y0 = max(0, LINE0_TOP - BAND_Y + PITCH * li - 7)
    return y0, min(WINDOW_H, y0 + PITCH + 14)


def word_groups(text):
    """indices of the stored text grouped into words (split on U+0020)."""
    groups, cur = [], []
    for i, ch in enumerate(text):
        if ch == " ":
            if cur:
                groups.append(cur)
            cur = []
        else:
            cur.append(i)
    if cur:
        groups.append(cur)
    return groups


def pens(c, text, alpha, spc, pad, reverse=True):
    gs = [R.glyph(c, ord(ch)) for ch in text]
    aw = np.array([0.0 if g is None else
                   (spc if ch == " " else g["aw"] * alpha + pad)
                   for ch, g in zip(text, gs)], float)
    if reverse:
        cum = np.cumsum(aw[::-1])[::-1] - aw
    else:
        cum = np.cumsum(aw) - aw
    return gs, cum


def render_line(c, text, alpha, spc, pad, xoff, ytop, H, W, reverse=True):
    canvas = np.zeros((H, W), bool)
    gs, pens_v = pens(c, text, alpha, spc, pad, reverse)
    basey = c.props["baseline"]
    for i, g in enumerate(gs):
        if g is None or g["bmp"].size == 0:
            continue
        h, w = g["bmp"].shape
        yy = int(round(ytop + basey - h))
        xx = int(round(xoff + pens_v[i]))
        if xx + w <= 0 or xx >= W or yy + h <= 0 or yy >= H:
            continue
        ys0, ys1 = max(0, yy), min(H, yy + h)
        xs0, xs1 = max(0, xx), min(W, xx + w)
        canvas[ys0:ys1, xs0:xs1] |= (g["bmp"][ys0 - yy:ys1 - yy,
                                              xs0 - xx:xs1 - xx] >= 128)
    return canvas


def profile_word(c, idxs, text, alpha, pad):
    cols = {}
    for i in idxs:
        g = R.glyph(c, ord(text[i]))
        if g is None or g["bmp"].size == 0:
            continue
        cols[i] = g["bmp"].max(axis=0).astype(np.float64)
    return cols


def fit(c, lines, meas_d, alphas, spcs, pads, ytops, shifts, reverse=True,
        ms=40):
    H, W = meas_d.shape
    Wp = W + 2 * ms
    mdp = np.pad(meas_d, ((0, 0), (ms, ms)))
    bands = [line_band(li) for li in range(len(lines))]
    cache = {}
    for alpha in alphas:
        for spc in spcs:
            for pad in pads:
                for li, text in enumerate(lines):
                    cache[(alpha, spc, pad, li)] = dilate(
                        render_line(c, text, alpha, spc, pad, 0, 0, H, W,
                                    reverse), 1)
    best = None
    for alpha in alphas:
        for spc in spcs:
            for pad in pads:
                for ytop in ytops:
                    for s in shifts:
                        total = 0
                        for li in range(len(lines)):
                            y0, y1 = bands[li]
                            r = cache[(alpha, spc, pad, li)]
                            dy = ytop + PITCH * li
                            if dy:
                                r = np.roll(r, dy, axis=0)
                            rp = np.pad(r[y0:y1], ((0, 0), (ms, ms)))
                            if s >= 0:
                                total += int(np.sum(mdp[y0:y1, s:] ^ rp[:, :Wp - s]))
                            else:
                                total += int(np.sum(mdp[y0:y1, :Wp + s] ^ rp[:, -s:]))
                        if best is None or total < best["err"]:
                            best = {"err": total, "alpha": float(alpha),
                                    "spc": float(spc), "pad": float(pad),
                                    "ytop": int(ytop), "shift": int(s)}
    return best


def evaluate(c, lines, meas_raw, p, reverse=True):
    H, W = meas_raw.shape
    tot_sym = tot_union = 0
    per = []
    for li, text in enumerate(lines):
        y0, y1 = line_band(li)
        band = np.zeros((H, W), bool)
        band[y0:y1] = meas_raw[y0:y1]
        r = render_line(c, text, p["alpha"], p["spc"], p["pad"], p["shift"], 0,
                        H, W, reverse)
        dy = p["ytop"] + PITCH * li
        if dy:
            r = np.roll(r, dy, axis=0)
        rd, bd = dilate(r, 1), dilate(band, 1)
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
    lines = ere[:5]
    raw = measured()
    md70 = dilate(raw, 1)

    all_fonts = sorted(n.split("\\")[-1] for n in PackFile(os.path.join(
        BASE, "reference", "shyizer", "data",
        "Shyizer Arabic.pack")).files if n.endswith(".cuf"))
    args = [a for a in sys.argv[1:] if a.endswith(".cuf")]
    fonts = args or all_fonts
    alphas = np.round(np.arange(0.90, 1.51, 0.02), 2)
    spcs = (4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0)
    pads = (0.0,)
    ytops = range(-2, 12)
    shifts = range(-12, 13)
    t0 = time.time()
    results = []
    for leaf in fonts:
        c = R.font(leaf)
        best = fit(c, lines, md70, alphas, spcs, pads, ytops, shifts,
                   reverse=False)
        per, iou = evaluate(c, lines, raw, best, reverse=False)
        results.append({"leaf": leaf, "iou": float(iou), **best, "per": per})
        print(f"  {leaf:30s} IoU={iou:.4f} alpha={best['alpha']:.2f} "
              f"spc={best['spc']:.0f} ytop={best['ytop']} shift={best['shift']} "
              f"sym={best['err']}  [{time.time()-t0:.0f}s]")
        sys.stdout.flush()
    results.sort(key=lambda r: -r["iou"])
    print("\n== top 12 ==")
    for r in results[:12]:
        print(f"  {r['leaf']:32s} IoU={r['iou']:.4f} alpha={r['alpha']:.2f} "
              f"spc={r['spc']:.0f} mod_x={[p['mod_x'] for p in r['per']]}")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"ere": results}, f, indent=1)
    print(f"\nwrote {OUT} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
