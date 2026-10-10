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

def analyze_font(family, size):
    fname = f"{family}_{size}.cuf"
    raw_v = vp.get_file("font\\" + fname)
    raw_r = rp.get_file("font\\" + fname)
    if raw_v is None or raw_r is None:
        return f"Missing {fname}"

    cv = CUF.decode(raw_v)
    cr = CUF.decode(raw_r)

    lh = cv.props["line_height"]
    base = cv.props["baseline"]
    v_size = cv.props["v_size"]  # cell height in CUF bitmaps

    # Latin ascender top ('l', 'd') and descender bottom ('g', 'p')
    # In vanilla CUF, bitmap has height v_size
    latin_tops = []
    latin_bottoms = []
    for ch in ['l', 'd']:
        if ord(ch) < len(cv.table):
            code = cv.table[ord(ch)]
            ah, aw, w, h = cv.dims[code]
            bm = cv.bitmaps[code]
            rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
            if rows:
                latin_tops.append(min(rows))
    for ch in ['g', 'p']:
        if ord(ch) < len(cv.table):
            code = cv.table[ord(ch)]
            ah, aw, w, h = cv.dims[code]
            bm = cv.bitmaps[code]
            rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
            if rows:
                latin_bottoms.append(max(rows))

    # Also for uppercase, check 'H', 'A', 'J', 'Q' if l/d/g/p are not present or uppercase
    if not latin_tops:
        for ch in ['H', 'A', 'L', 'D']:
            if ord(ch) < len(cv.table):
                code = cv.table[ord(ch)]
                ah, aw, w, h = cv.dims[code]
                bm = cv.bitmaps[code]
                rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
                if rows:
                    latin_tops.append(min(rows))
    if not latin_bottoms:
        for ch in ['Q', 'J']:
            if ord(ch) < len(cv.table):
                code = cv.table[ord(ch)]
                ah, aw, w, h = cv.dims[code]
                bm = cv.bitmaps[code]
                rows = [y for y in range(h) if any(bm[y * w + x] > 20 for x in range(w))]
                if rows:
                    latin_bottoms.append(max(rows))

    asc_top = min(latin_tops) if latin_tops else 0
    desc_bottom = max(latin_bottoms) if latin_bottoms else v_size

    # Arabic glyphs in cr
    arabic_dims = cr.dims[cv.count:]
    # alloc_height = ah, height = h
    # top = ah
    # bottom = ah + h
    ar_tops = [d[0] for d in arabic_dims]
    ar_bottoms = [d[0] + d[3] for d in arabic_dims]
    ar_heights = [d[3] for d in arabic_dims]

    tallest_top = min(ar_tops) # lowest value = highest up on screen/cell
    lowest_bottom = max(ar_bottoms) # highest value = lowest down on screen/cell
    max_h = max(ar_heights)

    # Check overflow
    # Relative to Latin extents:
    exceeds_latin_top = tallest_top < asc_top
    exceeds_latin_bottom = lowest_bottom > desc_bottom
    # Relative to cell (0 .. v_size or line_height):
    exceeds_cell_top = tallest_top < 0
    exceeds_cell_bottom_vsize = lowest_bottom > v_size
    exceeds_cell_bottom_lh = lowest_bottom > lh

    return {
        "family": family,
        "size": size,
        "line_height": lh,
        "baseline": base,
        "v_size": v_size,
        "latin_asc_top": asc_top,
        "latin_desc_bottom": desc_bottom,
        "ar_tallest_top": tallest_top,
        "ar_lowest_bottom": lowest_bottom,
        "ar_max_h": max_h,
        "exceeds_latin": (tallest_top < asc_top) or (lowest_bottom > desc_bottom),
        "exceeds_cell": (tallest_top < 0) or (lowest_bottom > v_size),
        "exceeds_latin_top": exceeds_latin_top,
        "exceeds_latin_bottom": exceeds_latin_bottom,
        "exceeds_cell_top": exceeds_cell_top,
        "exceeds_cell_bottom": exceeds_cell_bottom_vsize,
    }

print("Running vertical extents analysis...")
results = []
for fam, sizes in target_groups:
    for sz in sizes:
        res = analyze_font(fam, sz)
        results.append(res)

for r in results:
    f_str = f"{r['family']}_{r['size']}"
    print(f"{f_str:28s} | lh={r['line_height']:2d} base={r['baseline']:2d} cell={r['v_size']:2d} | "
          f"Latin: [{r['latin_asc_top']:2d}..{r['latin_desc_bottom']:2d}] | "
          f"Arabic: top={r['ar_tallest_top']:2d}, bot={r['ar_lowest_bottom']:2d} | "
          f"Exceeds Lat: {r['exceeds_latin']} (top={r['exceeds_latin_top']}, bot={r['exceeds_latin_bottom']}) | "
          f"Exceeds Cell: {r['exceeds_cell']} (top={r['exceeds_cell_top']}, bot={r['exceeds_cell_bottom']})")
