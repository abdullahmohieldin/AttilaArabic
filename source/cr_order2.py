#!/usr/bin/env python3
"""Decide the drawn order by matching measured ink components to the CUF
bitmaps of the very codepoints in the stored string.

For each measured component (connected ink blob, dots merged into the stroke
above them) we score every distinct codepoint of the stored string by
comparing the component's normalised aspect ratio and ink-row profile with
that codepoint's bitmap in the best-fitting font, then check which of the two
readings (stored left-to-right, or stored reversed) is consistent with a
monotone left-to-right assignment.

  cr_order2.py <ts> X0 Y0 X1 Y1 "<stored text>" [--thr 180] [--font leaf]
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

PF = R.PackFile(R.SHY)
_C = {}


def font(leaf):
    if leaf not in _C:
        n = next(x for x in PF.files if x.endswith(leaf))
        _C[leaf] = R.CUF.decode(PF.get_file(n))
    return _C[leaf]


def comps(m, minpx=8):
    h, w = m.shape
    lab = -np.ones((h, w), np.int32)
    out = []
    for yy in range(h):
        for xx in range(w):
            if not m[yy, xx] or lab[yy, xx] >= 0:
                continue
            cid = len(out)
            st = [(yy, xx)]
            lab[yy, xx] = cid
            pts = []
            while st:
                y, x = st.pop()
                pts.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1),
                               (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and m[ny, nx] \
                            and lab[ny, nx] < 0:
                        lab[ny, nx] = cid
                        st.append((ny, nx))
            if len(pts) < minpx:
                lab[lab == cid] = -2
                continue
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            out.append({"id": cid, "n": len(pts), "x0": min(xs), "x1": max(xs),
                        "y0": min(ys), "y1": max(ys),
                        "cx": float(np.mean(xs))})
    out.sort(key=lambda c: c["cx"])
    return out, lab


def signature(bm):
    """normalised (aspect, row-profile) of a bitmap."""
    ys = np.nonzero(bm.sum(axis=1))[0]
    xs = np.nonzero(bm.sum(axis=0))[0]
    if not len(ys) or not len(xs):
        return None
    b = bm[ys[0]:ys[-1] + 1, xs[0]:xs[-1] + 1]
    h, w = b.shape
    prof = b.sum(axis=1).astype(float) / max(1.0, b.sum())
    return {"h": h, "w": w, "ar": w / float(h), "prof": prof}


def profdist(p, q):
    n = max(len(p), len(q))
    a = np.zeros(n)
    b = np.zeros(n)
    a[:len(p)] = p
    b[:len(q)] = q
    return float(np.abs(a - b).sum())


def main():
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    text = sys.argv[6]
    thr, leaf = 180, "georgia_italic_14.cuf"
    for i, a in enumerate(sys.argv):
        if a == "--thr":
            thr = int(sys.argv[i + 1])
        if a == "--font":
            leaf = sys.argv[i + 1]
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    a = img[y0:y1, x0:x1]
    m = a >= thr
    cs, lab = comps(m)
    # merge dot comps into the nearest stroke below them (x overlap, small)
    strokes, dots = [], []
    for c in cs:
        (dots if (c["y1"] - c["y0"]) <= 5 and c["n"] <= 30 and
         c["x1"] - c["x0"] <= 8 else strokes).append(c)
    for d in dots:
        best, bd = None, 1e9
        for s in strokes:
            if s["y0"] > d["y1"]:
                ov = min(s["x1"], d["x1"]) - max(s["x0"], d["x0"])
                gap = s["y0"] - d["y1"]
                if gap <= 6 and (ov > 0 or abs(d["cx"] - s["cx"]) < 5):
                    sc = gap * 4 + abs(d["cx"] - s["cx"])
                    if sc < bd:
                        bd, best = sc, s
        if best is not None:
            best["dotted"] = best.get("dotted", 0) + 1
            best["y0"] = min(best["y0"], d["y0"])
            best["x0"] = min(best["x0"], d["x0"])
            best["x1"] = max(best["x1"], d["x1"])
    strokes.sort(key=lambda c: c["cx"])
    print(f"shot {ts} thr={thr} font={leaf}")
    print(f"  {len(strokes)} stroke groups (dots merged), "
          f"x{x0 + strokes[0]['x0']}..{x0 + strokes[-1]['x1']}")
    for s in strokes:
        print(f"    cx={x0 + s['cx']:7.1f} w={s['x1'] - s['x0']:3d} "
              f"h={s['y1'] - s['y0']:3d} ink={s['n']:4d} "
              f"dots={s.get('dotted', 0)}  "
              f"ar={(s['x1'] - s['x0']) / max(1, s['y1'] - s['y0']):.2f}")
    c = font(leaf)
    cps = [ord(ch) for ch in text if ch != " "]
    sigs = {}
    for cp in set(cps):
        i = c.table[cp]
        if i == 0xFFFF or i >= c.count:
            continue
        ah, aw, w, h = c.dims[i]
        if not (w and h):
            continue
        bm = np.frombuffer(c.bitmaps[i], np.uint8).reshape(h, w)
        sig = signature(bm)
        if sig:
            sigs[cp] = sig
    # score every stroke against every distinct codepoint
    print(f"  best bitmap match per stroke (font {leaf}):")
    for k, s in enumerate(strokes):
        sar = (s["x1"] - s["x0"]) / max(1, s["y1"] - s["y0"])
        sub = m[s["y0"]:s["y1"] + 1, s["x0"]:s["x1"] + 1]
        prof = sub.sum(axis=1).astype(float) / max(1.0, sub.sum())
        rank = []
        for cp, sig in sigs.items():
            d = abs(sar - sig["ar"]) * 2 + profdist(prof, sig["prof"])
            rank.append((d, cp))
        rank.sort()
        print(f"    stroke{k} cx={x0 + s['cx']:.0f}: " +
              ", ".join(f"U+{cp:04X}({d:.2f})" for d, cp in rank[:4]))
    print("  stored non-space order: " +
          " ".join(f"{'U+%04X' % cp}" for cp in cps))
    print("  reversed order        : " +
          " ".join(f"{'U+%04X' % cp}" for cp in cps[::-1]))


if __name__ == "__main__":
    main()
