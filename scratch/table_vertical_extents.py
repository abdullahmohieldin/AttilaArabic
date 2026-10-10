import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from tools.packfile import PackFile
from source.cuf import CUF

BASE = r"D:\AttilaArabic"
VANILLA_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
RELEASE_PACK = os.path.join(BASE, "release", "Attila_Arabic_Phase1_fonts.pack")

vp = PackFile(VANILLA_PACK)
rp = PackFile(RELEASE_PACK)

target_groups = [
    ("la_gioconda_uppercase", [18, 20, 22, 24, 26, 28, 30, 32, 38]),
    ("la_gioconda", [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]),
    ("georgia_italic", [10, 12, 14, 16, 18]),
]

print("Family & Size | line_h | base | cell (v_size) | Latin [asc..desc] | Std Arabic [top..bot] | All Arabic [top..bot] | Exceeds Latin? | Exceeds Cell?")
print("-" * 130)

for fam, sizes in target_groups:
    for sz in sizes:
        fname = f"{fam}_{sz}.cuf"
        cv = CUF.decode(vp.get_file("font\\" + fname))
        cr = CUF.decode(rp.get_file("font\\" + fname))

        lh = cv.props["line_height"]
        base = cv.props["baseline"]
        v_size = cv.props["v_size"]

        latin_tops = []
        latin_bottoms = []
        for ch in ['l', 'd']:
            code = cv.table[ord(ch)]
            ah, aw, w, h = cv.dims[code]
            bm = cv.bitmaps[code]
            rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
            if rows: latin_tops.append(min(rows))
        for ch in ['g', 'p']:
            code = cv.table[ord(ch)]
            ah, aw, w, h = cv.dims[code]
            bm = cv.bitmaps[code]
            rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
            if rows: latin_bottoms.append(max(rows))

        if not latin_tops:
            for ch in ['H', 'A', 'L', 'D']:
                code = cv.table[ord(ch)]
                ah, aw, w, h = cv.dims[code]
                bm = cv.bitmaps[code]
                rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
                if rows: latin_tops.append(min(rows))
        if not latin_bottoms:
            for ch in ['Q', 'J']:
                code = cv.table[ord(ch)]
                ah, aw, w, h = cv.dims[code]
                bm = cv.bitmaps[code]
                rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
                if rows: latin_bottoms.append(max(rows))

        asc_top = min(latin_tops) if latin_tops else 0
        desc_bottom = max(latin_bottoms) if latin_bottoms else v_size

        std_ar = cr.dims[cv.count:-11]
        all_ar = cr.dims[cv.count:]

        std_top = min(d[0] for d in std_ar)
        std_bot = max(d[0] + d[3] for d in std_ar)

        all_top = min(d[0] for d in all_ar)
        all_bot = max(d[0] + d[3] for d in all_ar)

        # Check exceedances
        exceed_lat_std = []
        if std_top < asc_top: exceed_lat_std.append(f"top({std_top}<{asc_top})")
        if std_bot > desc_bottom: exceed_lat_std.append(f"bot({std_bot}>{desc_bottom})")

        exceed_cell_std = []
        if std_top < 0: exceed_cell_std.append(f"top({std_top}<0)")
        if std_bot > v_size: exceed_cell_std.append(f"bot({std_bot}>{v_size})")

        f_str = f"{fam}_{sz}"
        print(f"{f_str:26s} | {lh:6d} | {base:4d} | {v_size:13d} | [{asc_top:2d}..{desc_bottom:2d}]           | "
              f"[{std_top:2d}..{std_bot:2d}]             | [{all_top:2d}..{all_bot:2d}]             | "
              f"{', '.join(exceed_lat_std) if exceed_lat_std else 'No':14s} | "
              f"{', '.join(exceed_cell_std) if exceed_cell_std else 'No'}")
