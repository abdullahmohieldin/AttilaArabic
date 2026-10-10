#!/usr/bin/env python3
"""C4 per-codepoint advance recovery.

The 19 drawn description lines give 19 equations
      measured_ink_width(line) = sum over codepoints in the line of adv[cp]
                                + n_space * adv[U+0020]
which is a linear system in the unknown per-codepoint advances. Solving it
(every non-space codepoint is kept when it occurs in at least two measured
lines) gives the engine's own pitch table directly, instead of forcing it
through a one-parameter "scale x CUF alloc_width" model -- which is what kept
the residual at ~20 px.

  python source/cr_adv_solve.py [font_leaf]
"""
import json
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R                     # noqa: E402
import cr_c4_wrap as W                    # noqa: E402

CAL = os.path.join(BASE, "logs", "cr_c4_adv.json")


def main():
    leaf = sys.argv[1] if len(sys.argv) > 1 else "la_gioconda_12.cuf"
    c = R.font(leaf)
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(W.V14)
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    ERE = d["start_pos_factions_description_2120156326"].split("\n")
    WRE = d["start_pos_factions_description_2120156339"].split("\n")

    eb = W.detect_bands(W.ERE_TS, 600)
    wb = W.detect_bands(W.WRE_TS, 600)
    print(f"ERE bands {len(eb)}  WRE bands {len(wb)}")
    # (text, measured width) pairs that are unambiguous: ERE bands 0-9 are the
    # stored lines 0-9 (the box clips line 10+), WRE bands 0-8 the stored 0-8
    eqs = []
    for label, ls, bands, n in (("ERE", ERE, eb, 10), ("WRE", WRE, wb, 9)):
        for i in range(min(n, len(bands), len(ls))):
            ya, yb, a, b, ink = bands[i]
            w = b - a + 1
            if w < 200:
                continue
            eqs.append((f"{label}{i}", ls[i], w))
    print(f"usable equations: {len(eqs)}")
    for tag, t, w in eqs:
        print(f"   {tag:6s} meas_w={w:4d} n={len(t):3d}")

    # design matrix
    cps = sorted({ord(ch) for _t, txt, _w in eqs for ch in txt}
                 - {0x0020})
    cnt = {cp: sum(1 for _t, txt, _w in eqs if chr(cp) in txt) for cp in cps}
    used = [cp for cp in cps if cnt[cp] >= 2]
    idx = {cp: j for j, cp in enumerate(used)}
    SP = len(used)
    M = np.zeros((len(eqs), SP + 1))
    Y = np.zeros(len(eqs))
    for i, (_t, txt, w) in enumerate(eqs):
        for ch in txt:
            cp = ord(ch)
            if cp == 0x0020:
                M[i, SP] += 1
            elif cp in idx:
                M[i, idx[cp]] += 1
        Y[i] = w
    print(f"unknowns: {SP} codepoints + 1 space")
    # ridge-regularised least squares, prior = 1.2 * CUF aw + 0.5
    prior = np.array([1.2 * R.glyph(c, cp)["aw"] + 0.5 for cp in used] + [5.0])
    lam = 1.0
    MtM = M.T @ M + lam * np.eye(SP + 1)
    sol = np.linalg.solve(MtM, M.T @ Y + lam * prior)
    pred = M @ sol
    res = pred - Y
    print(f"rms={np.sqrt(np.mean(res**2)):.2f} max={np.max(np.abs(res)):.2f}")
    for (tag, t, w), p, r in zip(eqs, pred, res):
        print(f"   {tag:6s} meas={w:4d} pred={p:7.1f} err={r:+6.1f}")
    print("\nrecovered advances (cp: solved / prior=CUF aw):")
    for j, cp in enumerate(used):
        g = R.glyph(c, cp)
        print(f"   U+{cp:04X} solved={sol[j]:6.2f} cuf_aw={g['aw']:3d} "
              f"ratio={sol[j]/g['aw']:.3f} lines={cnt[cp]}")
    print(f"   U+0020 solved={sol[SP]:.2f}")
    with open(CAL, "w", encoding="utf-8") as f:
        json.dump({"leaf": leaf, "adv": {f"{cp:04X}": float(sol[j])
                                        for j, cp in enumerate(used)},
                   "space": float(sol[SP]),
                   "rms": float(np.sqrt(np.mean(res ** 2))),
                   "eqs": [{"tag": t, "meas": w, "pred": float(p)}
                           for (t, _x, w), p in zip(eqs, pred)]},
                  f, indent=1)
    print(f"wrote {CAL}")


if __name__ == "__main__":
    main()
