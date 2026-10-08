#!/usr/bin/env python3
"""Decide the drawn direction of a stored loc string from pixel topology only.

Arabic Presentation Forms have a fixed joining rule that needs no font
identity:

  initial form  (e.g. FEBC) base stroke attaches ONLY to its right neighbour
  medial  form  (e.g. FEA8) base stroke attaches to BOTH neighbours
  final   form  (e.g. FEE3) base stroke attaches ONLY to its left neighbour
  isolated form (e.g. FE94) attaches to NEITHER

So for the run of ink at baseline height we can label every run's attachment
(LEFT / RIGHT / BOTH / NONE). Reading the stored codepoint sequence in stored
order must then produce a consistent attachment sequence; reading it in the
reverse direction generally produces impossible shapes (a final form that has
to attach on its right, an isolated form that has to attach).

  cr_order.py <ts> X0 Y0 X1 Y1 "<stored visual-order text>" [--thr 180]
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

# attachment rules by codepoint, from the Presentation-Forms-B naming
FORM = {}
for cp in range(0xFE70, 0xFF00):
    FORM[cp] = "?"


def attach_rule(cp):
    """-> (left, right) booleans: which sides this form can join on."""
    # initial forms (odd-ish naming) FE8B FE91 FE97 FE9B FE9F FEA3 FEA7 FEB3
    # FEB7 FEBB FEBF FEC3 FEC7 FECB FECF FED3 FED7 FEDB FEDF FEE3 FEE7 FEEB
    # FEF3 -> attach RIGHT only
    initial = {0xFE8B, 0xFE91, 0xFE97, 0xFE9B, 0xFE9F, 0xFEA3, 0xFEA7,
               0xFEB3, 0xFEB7, 0xFEBB, 0xFEBF, 0xFEC3, 0xFEC7, 0xFECB,
               0xFECF, 0xFED3, 0xFED7, 0xFEDB, 0xFEDF, 0xFEE3, 0xFEE7,
               0xFEEB, 0xFEF3}
    # medial forms -> attach BOTH
    medial = {0xFE8C, 0xFE92, 0xFE98, 0xFE9C, 0xFEA0, 0xFEA4, 0xFEA8,
              0xFEB4, 0xFEB8, 0xFEBC, 0xFEC0, 0xFEC4, 0xFEC8, 0xFECC,
              0xFED0, 0xFED4, 0xFED8, 0xFEDC, 0xFEE0, 0xFEE4, 0xFEE8,
              0xFEEC, 0xFEF4}
    # final forms -> attach LEFT only
    final = {0xFE82, 0xFE84, 0xFE88, 0xFE8A, 0xFE8E, 0xFE90, 0xFE94,
             0xFE96, 0xFE98_0 if False else 0xFE9A, 0xFE9E, 0xFEA2, 0xFEA6,
             0xFEAA, 0xFEAC, 0xFEAE, 0xFEB0, 0xFEB2, 0xFEB6, 0xFEBA,
             0xFEBE, 0xFEC2, 0xFEC6, 0xFECA, 0xFECE, 0xFED2, 0xFED6,
             0xFEDA, 0xFEDE, 0xFEE2, 0xFEE6, 0xFEEA, 0xFEEE, 0xFEF0,
             0xFEF2, 0xFEFC}
    # isolated forms -> attach NEITHER
    isolated = {0xFE80, 0xFE81, 0xFE83, 0xFE85, 0xFE87, 0xFE89, 0xFE8D,
                0xFE8F, 0xFE93, 0xFE95, 0xFE99, 0xFE9D, 0xFEA1, 0xFEA5,
                0xFEA9, 0xFEAB, 0xFEAD, 0xFEAF, 0xFEB1, 0xFEB5, 0xFEB9,
                0xFEBD, 0xFEC1, 0xFEC5, 0xFEC9, 0xFECD, 0xFED1, 0xFED5,
                0xFED9, 0xFEDD, 0xFEE1, 0xFEE5, 0xFEE9, 0xFEED, 0xFEEF,
                0xFEF1, 0xFEF5, 0xFEF6, 0xFEF7, 0xFEF8, 0xFEF9, 0xFEFA,
                0xFEFB}
    if cp in initial:
        return (False, True)
    if cp in medial:
        return (True, True)
    if cp in final:
        return (True, False)
    if cp in isolated:
        return (False, False)
    return None


def runs_at_baseline(m, thresh=1):
    """runs of ink columns over the whole band; returns [(x0,x1)]."""
    cols = m.sum(axis=0)
    rr = []
    x = 0
    n = len(cols)
    while x < n:
        if cols[x] >= thresh:
            xs = x
            while x < n and cols[x] >= thresh:
                x += 1
            rr.append((xs, x))
        x += 1
    return rr


def main():
    ts = sys.argv[1]
    x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
    text = sys.argv[6]
    thr = 180
    for i, a in enumerate(sys.argv):
        if a == "--thr":
            thr = int(sys.argv[i + 1])
    img = np.array(Image.open(R.shot(ts)).convert("L"))
    a = img[y0:y1, x0:x1]
    m = a >= thr
    rows = m.sum(axis=1)
    ys = np.nonzero(rows)[0]
    if not len(ys):
        print("no ink")
        return
    # baseline = the bottom rows of the glyph body; take the bottom 4 rows of
    # the "tall" ink (ignore dots above)
    tall = np.nonzero(rows >= 0.25 * rows.max())[0]
    base_lo, base_hi = tall[-1] - 2, tall[-1] + 1
    strip = m[base_lo:base_hi + 1, :]
    rr = runs_at_baseline(strip)
    print(f"shot {ts} box=({x0},{y0})-({x1},{y1}) thr={thr}")
    print(f"  body rows {ys[0]}..{ys[-1]}, baseline strip rows "
          f"{base_lo}..{base_hi}")
    print(f"  baseline runs (image x): {[(x0 + p, x0 + q) for p, q in rr]}")
    # attachment: does the run touch its neighbours? merge runs separated by
    # 1 px first (hairline), then look at the gap pattern of the ORIGINAL runs
    gaps = [rr[i + 1][0] - rr[i][1] for i in range(len(rr) - 1)]
    print(f"  gaps between runs: {gaps}   (0 => joined)")
    # classify each run by whether it has a neighbour within 1 px on each side
    labels = []
    for i, (p, q) in enumerate(rr):
        left = i > 0 and (p - rr[i - 1][1]) <= 1
        right = i < len(rr) - 1 and (rr[i + 1][0] - q) <= 1
        labels.append("BOTH" if left and right else
                      "LEFT" if left else "RIGHT" if right else "NONE")
    print(f"  attachment read left-to-right: {labels}")
    print()
    # now the two readings of the stored string, minus spaces
    stored = [ord(c) for c in text if c != " "]
    for name, seq in (("STORED order", stored), ("REVERSED order", stored[::-1])):
        bad = []
        ok = 0
        for cp in seq:
            r = attach_rule(cp)
            if r is None:
                bad.append(f"U+{cp:04X}:unknown")
            else:
                ok += 1
        print(f"  {name}: {len(seq)} non-space codepoints, "
              f"{ok} with a known form")
        print("    forms: " + " ".join(
            (lambda r: ("iso" if r == (False, False) else
                        "ini" if r == (False, True) else
                        "med" if r == (True, True) else "fin"))(attach_rule(cp))
            if attach_rule(cp) else f"U+{cp:04X}?" for cp in seq))
    print()
    # consistency test: in the drawn direction, a shape's attachment must
    # match whether the corresponding run has a joining neighbour
    n = min(len(rr), len(stored))
    for name, seq in (("STORED", stored), ("REVERSED", stored[::-1])):
        score, total = 0, 0
        detail = []
        for i, cp in enumerate(seq):
            if i >= len(labels):
                break
            r = attach_rule(cp)
            if r is None:
                continue
            total += 1
            want_left, want_right = r
            got = labels[i]
            ok = ((want_left and got in ("LEFT", "BOTH")) or
                  (not want_left and got in ("NONE", "RIGHT"))) and \
                 ((want_right and got in ("RIGHT", "BOTH")) or
                  (not want_right and got in ("NONE", "LEFT")))
            score += 1 if ok else 0
            if not ok:
                detail.append(f"#{i} U+{cp:04X} wants "
                              f"{'L' if want_left else '-'}"
                              f"{'R' if want_right else '-'} got {got}")
        print(f"  {name}: attachment-consistent {score}/{total}"
              + ("" if not detail else "  violations: " + "; ".join(detail[:8])))


if __name__ == "__main__":
    main()
