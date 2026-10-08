#!/usr/bin/env python3
"""Kerning-tail analysis for the 37 Shyizer CUFs.

Layout: u16 ksize, u16 skip, ksize x ksize u8 matrix, entry [A][B] = the width
of A when followed by B. Codes below `skip` have no row/column. This script
reports, per font, the covered code range and whether the Arabic joining forms
our loc uses fall inside it; and it lists the largest negative deltas in the
matrix for the codes that ARE covered.
"""
import os
import struct
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF               # noqa: E402
from packfile import PackFile     # noqa: E402

SHY = os.path.join(BASE, "reference", "shyizer", "data", "Shyizer Arabic.pack")
JOIN_FORMS = [0xFE92, 0xFE8D, 0xFE8E, 0xFEF2, 0xFEBC, 0xFEDF, 0xFEE4, 0xFE94,
              0xFEE7, 0xFEAD, 0xFEAE, 0xFECC]


def analyse(path):
    pf = PackFile(path)
    names = sorted(n for n in pf.files if n.endswith(".cuf"))
    summary = {}
    for n in names:
        leaf = n.split("\\")[-1]
        c = CUF.decode(pf.get_file(n))
        if len(c.tail) < 4:
            summary[leaf] = ("no tail", len(c.tail), None, None, None)
            continue
        ks, skip = struct.unpack_from("<HH", c.tail, 0)
        mat = c.tail[4:4 + ks * ks]
        covered = (skip, skip + ks - 1)
        inside = [cp for cp in JOIN_FORMS if covered[0] <= cp <= covered[1]]
        neg = []
        for a in range(ks):
            for b in range(ks):
                v = mat[a * ks + b]
                if v == 0:
                    continue
                code_a = skip + a
                i = c.table[code_a] if code_a < 65536 else 0xFFFF
                if i == 0xFFFF or i >= c.count:
                    continue
                _ah, aw, _w, _h = c.dims[i]
                if v < aw:
                    neg.append((code_a, skip + b, aw, v, aw - v))
        neg.sort(key=lambda t: -t[4])
        summary[leaf] = (f"ksize={ks} skip={skip} codes {covered[0]}..{covered[1]}",
                         len(c.tail), inside, neg[:5], None)
    # print compactly
    print(f"file: {path}  ({len(names)} CUFs)")
    for leaf, (desc, tlen, inside, neg, _x) in summary.items():
        print(f"  {leaf:30s} {desc}")
        if inside is not None:
            print(f"      Arabic joining forms inside covered range: "
                  f"{['U+%04X' % c for c in inside] or 'NONE'}")
            if neg:
                print(f"      widest negative deltas (A,B,aw,entry,cut): {neg}")
    print("\nJOIN_FORMS checked: " + " ".join(f"U+{c:04X}" for c in JOIN_FORMS))


if __name__ == "__main__":
    analyse(SHY)
