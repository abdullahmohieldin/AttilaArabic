#!/usr/bin/env python3
"""Real-vs-aliased Arabic coverage per arialunicode size.

Default glyph = most common table value, cross-checked against
known-unassigned codepoints (U+0378, U+2E9F). A mapping counts as REAL iff
its code differs from the default AND its bitmap is non-empty.

Usage: cuf_coverage.py <fonts_dir>
"""
import glob
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from cuf import CUF  # noqa: E402

RANGES = {
    "0600-06FF": (0x0600, 0x06FF),
    "FB50-FDFF": (0xFB50, 0xFDFF),
    "FE70-FEFF": (0xFE70, 0xFEFF),
}
PROBE_UNASSIGNED = [0x0378, 0x2E9F, 0xFFFF9 if False else 0x2E9F]


def analyze(path):
    data = open(path, "rb").read()
    c = CUF.decode(data)
    freq = {}
    for v in c.table:
        freq[v] = freq.get(v, 0) + 1
    default = max(freq, key=freq.get)
    probes = {hex(p): hex(c.table[p]) for p in (0x0378, 0x2E9F)}
    ddims = c.dims[default] if default < len(c.dims) else None
    dpix = int(sum(c.bitmaps[default])) if default < len(c.bitmaps) else -1

    def real(lo, hi):
        n = 0
        for i in range(lo, hi + 1):
            code = c.table[i]
            if code == default or code == 0xFFFF or code >= len(c.dims):
                continue
            ah, aw, w, h = c.dims[code]
            if w > 0 and h > 0 and len(c.bitmaps[code]) > 0:
                n += 1
        return n

    rows = {name: (real(lo, hi), hi - lo + 1) for name, (lo, hi) in RANGES.items()}
    return {
        "size": os.path.basename(path), "glyphs": len(c.dims),
        "default": default, "default_users": freq[default],
        "probes": probes, "default_dims": ddims, "default_ink": dpix,
        "rows": rows,
    }


if __name__ == "__main__":
    d = sys.argv[1]
    print("font | codes | default | users | probes(0378,2E9F) | "
          "def_dims | def_ink | 0600-06FF | FB50-FDFF | FE70-FEFF")
    for p in sorted(glob.glob(os.path.join(d, "arialunicode_*.cuf"))):
        r = analyze(p)
        rr = " ".join(f"{v}/{t}" for v, t in r["rows"].values())
        print(f"{r['size']} | {r['glyphs']} | {r['default']:#x} | "
              f"{r['default_users']} | {r['probes']} | {r['default_dims']} | "
              f"{r['default_ink']} | {rr}")
