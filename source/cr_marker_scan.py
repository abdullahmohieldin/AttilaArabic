#!/usr/bin/env python3
"""C2 prep: find marker codepoints that are safe to overwrite in every vanilla
CUF. A codepoint is SAFE in a font when table[cp] is referenced by no other
char (owners == 1), so writing a solid block into that glyph cannot change any
other character. Prints per-font candidate coverage and dangling-entry counts.
"""
import os
import sys
from collections import Counter

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cuf import CUF  # noqa: E402

VF = os.path.join(BASE, "build", "vanilla_fonts")

CANDIDATES = (
    list(range(0x0605, 0x060C)) + list(range(0x060D, 0x0610)) +
    list(range(0x0614, 0x061B)) + [0x0620] +
    list(range(0x0655, 0x0660)) + list(range(0x065C, 0x0660)) +
    [0x0670] + list(range(0x06D6, 0x06EE)) + [0x06FD, 0x06FE, 0x06FF] +
    list(range(0x08A0, 0x08A5)) + list(range(0x08E3, 0x08F0)) +
    [0x205A, 0x205C, 0x205E, 0x2061, 0x2064, 0x206A, 0x2071]
)


def main():
    fonts = sorted(f for f in os.listdir(VF) if f.endswith(".cuf"))
    safe_sets = {}
    out = []
    for leaf in fonts:
        c = CUF.decode(open(os.path.join(VF, leaf), "rb").read())
        owners = Counter(v for v in c.table if v != 0xFFFF)
        dangling = sum(1 for v in c.table if v >= c.count)
        safe, inked = [], []
        for cp in dict.fromkeys(CANDIDATES):
            code = c.table[cp]
            if code == 0xFFFF or code >= c.count:
                continue
            if owners[code] == 1:
                safe.append(cp)
                ah, aw, w, h = c.dims[code]
                if w and h and any(c.bitmaps[code]):
                    inked.append(cp)
        safe_sets[leaf] = set(safe)
        out.append(f"{leaf:32s} N={c.count:5d} dangling={dangling:5d} "
                   f"safe={len(safe):3d} inked={len(inked):3d}")
    print("\n".join(out))

    common = set.intersection(*safe_sets.values()) if safe_sets else set()
    print(f"\nsafe in ALL {len(fonts)} fonts: {len(common)}")
    for cp in sorted(common):
        print(f"  U+{cp:04X}")
    with open(os.path.join(BASE, "logs", "cr_marker_scan.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(out) + f"\n\nsafe in all: "
                + " ".join(f"U+{cp:04X}" for cp in sorted(common)) + "\n")


if __name__ == "__main__":
    main()
