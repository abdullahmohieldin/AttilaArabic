#!/usr/bin/env python3
"""Clean-room scan: for every vanilla CUF, report how the 65536-entry char
table handles (a) the codepoints our loc actually uses and (b) Arabic
presentation forms in general. Key question: is table[cp] in range (< count)
or DANGLING (>= count)? A dangling entry cannot be a real glyph, so any
codepoint that is dangling in a font cannot be edited or drawn from it.
"""
import os
import sys
from collections import Counter

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF          # noqa: E402
from loc import decode       # noqa: E402
from packfile import PackFile  # noqa: E402

VF = os.path.join(BASE, "build", "vanilla_fonts")
V14 = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")
FILES = [
    r"text\db\uied_component_texts.loc", r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc", r"text\db\land_units.loc",
    r"text\db\faction_groups.loc", r"text\db\random_localisation_strings.loc",
    r"text\db\ui_unit_stats.loc", r"text\db\ui_unit_bullet_point_enums.loc",
]


def used_codepoints():
    pf = PackFile(V14)
    cps = Counter()
    for f in FILES:
        for _k, text, _t in decode(pf.get_file(f))[0]:
            for ch in text:
                cps[ord(ch)] += 1
    return cps


def main():
    used = used_codepoints()
    used_sorted = sorted(used)
    print(f"loc uses {len(used_sorted)} distinct codepoints")
    arab = [c for c in used_sorted if 0x0600 <= c <= 0x06FF
            or 0xFB50 <= c <= 0xFEFF]
    print(f"  arabic-range: {len(arab)}: "
          + " ".join(f"U+{c:04X}" for c in arab))
    other = [c for c in used_sorted if c not in set(arab)]
    print(f"  other: {' '.join(f'U+{c:04X}' for c in other)}")
    head = [f"loc uses {len(used_sorted)} distinct codepoints",
            f"  arabic-range {len(arab)}: "
            + " ".join(f"U+{c:04X}" for c in arab),
            f"  other {len(other)}: "
            + " ".join(f"U+{c:04X}" for c in other), ""]

    fonts = sorted(f for f in os.listdir(VF) if f.endswith(".cuf"))
    out = []
    for leaf in fonts:
        c = CUF.decode(open(os.path.join(VF, leaf), "rb").read())
        dvals = Counter(v for v in c.table if v >= c.count)
        inr = [cp for cp in arab if c.table[cp] < c.count]
        dang = [cp for cp in arab if c.table[cp] >= c.count]
        ffff = sum(1 for v in c.table if v == 0xFFFF)
        out.append(
            f"{leaf:32s} N={c.count:5d} 0xFFFF={ffff:5d} dangling={sum(dvals.values()):5d} "
            f"distinct_dangling={sorted(dvals)[:4]} "
            f"arabic_in_range={len(inr)}/{len(arab)} dang={len(dang)}")
        if len(inr) <= len(arab) // 2:
            out.append("    in_range_cps: "
                       + " ".join(f"U+{cp:04X}" for cp in inr))
        o_in = [cp for cp in other if c.table[cp] < c.count]
        out.append(f"    other_in_range={len(o_in)}/{len(other)}")
    print("\n".join(out))
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    with open(os.path.join(BASE, "logs", "cr_map_scan.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(head + out) + "\n")


if __name__ == "__main__":
    main()
