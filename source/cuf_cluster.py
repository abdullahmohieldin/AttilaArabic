#!/usr/bin/env python3
"""REAL Arabic coverage: cluster Arabic codepoints by bitmap identity.

A mapping is REAL iff its bitmap is non-empty AND not shared with a
known-unassigned probe (U+0378, U+2E9F) or with >40 unrelated codepoints
(fallback-box aliasing).

Usage: cuf_cluster.py <cuf> [out_txt]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from cuf import CUF  # noqa: E402

RANGES = {
    "0600-06FF": (0x0600, 0x06FF),
    "FB50-FDFF": (0xFB50, 0xFDFF),
    "FE70-FEFF": (0xFE70, 0xFEFF),
}
PROBES = [0x0378, 0x2E9F, 0x2B7F, 0x1FFFF & 0xFFFF]


def analyze(path):
    c = CUF.decode(open(path, "rb").read())
    # bitmap key per code: (w,h,bytes)
    Alley = {}
    for code in range(len(c.dims)):
        ah, aw, w, h = c.dims[code]
        key = (w, h, bytes(c.bitmaps[code]))
        Alley.setdefault(key, []).append(code)
    # code -> cluster size
    code_cluster = {}
    for key, codes in Alley.items():
        for cd in codes:
            code_cluster[cd] = len(codes)
    probe_codes = {p: c.table[p] for p in PROBES if p < 0x10000}
    fallback_keys = set()
    for p, code in probe_codes.items():
        if code == 0xFFFF or code >= len(c.dims):
            continue
        ah, aw, w, h = c.dims[code]
        fallback_keys.add((w, h, bytes(c.bitmaps[code])))

    out = {"codes": len(c.dims), "probe_codes": probe_codes, "ranges": {}}
    for name, (lo, hi) in RANGES.items():
        real, aliased, empty = [], [], []
        for i in range(lo, hi + 1):
            code = c.table[i]
            if code == 0xFFFF or code >= len(c.dims):
                empty.append(i)
                continue
            ah, aw, w, h = c.dims[code]
            key = (w, h, bytes(c.bitmaps[code]))
            if w == 0 or h == 0 or len(c.bitmaps[code]) == 0:
                empty.append(i)
            elif key in fallback_keys or code_cluster.get(code, 1) > 40:
                aliased.append(i)
            else:
                real.append(i)
        out["ranges"][name] = {"real": real, "aliased": aliased, "empty": empty}
    return out, c


if __name__ == "__main__":
    rep, c = analyze(sys.argv[1])
    print(f"codes={rep['codes']}")
    print("probe codes:", {k: hex(v) for k, v in rep["probe_codes"].items()})
    for name, r in rep["ranges"].items():
        print(f"{name}: REAL={len(r['real'])} ALIASED={len(r['aliased'])} "
              f"EMPTY={len(r['empty'])}")
        if r["aliased"] and len(r["aliased"]) <= 20:
            print("  aliased:", " ".join(f"U+{x:04X}" for x in r["aliased"]))
        if r["empty"] and len(r["empty"]) <= 20:
            print("  empty:", " ".join(f"U+{x:04X}" for x in r["empty"]))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            for name, r in rep["ranges"].items():
                f.write(f"[{name}] real={len(r['real'])}\n")
                f.write(" ".join(f"U+{x:04X}" for x in r["real"]) + "\n")
