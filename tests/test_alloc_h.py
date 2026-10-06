import sys, os
sys.path.insert(0, r"D:\AttilaArabic\source")
from cuf import CUF

def inspect_chars(font, chars, label):
    b_prop = font.props["baseline"]
    v_prop = font.props["v_size"]
    print(f"=== {label} (props: baseline={b_prop}, v_size={v_prop}) ===")
    for item in chars:
        if isinstance(item, tuple):
            name_label, cp = item
        elif isinstance(item, str):
            name_label, cp = item, ord(item)
        else:
            name_label, cp = hex(item), item
        code = font.table[cp]
        if code >= len(font.dims):
            print(f"  {name_label:20} (U+{cp:04X}): UNMAPPED (code={code})")
            continue
        ah, aw, w, h = font.dims[code]
        bm = font.bitmaps[code]
        ink_rows = [y for y in range(h) if any(bm[y*w + x] > 0 for x in range(w))]
        if ink_rows:
            ink_top, ink_bot = min(ink_rows), max(ink_rows)
            ih = ink_bot - ink_top + 1
        else:
            ink_top, ink_bot, ih = None, None, 0
        print(f"  {name_label:20} (U+{cp:04X}, code={code:4}): ah={ah:3}, aw={aw:2}, w={w:2}, h={h:2} | ink_top={ink_top}, ink_bot={ink_bot}, ih={ih}")

a12 = CUF.decode(open(r"extracted\fonts\arialunicode_12.cuf", "rb").read())

# Arabic characters in U+0600..06FF and Presentation Forms-B U+FE70..FEFF
ar_chars = [
    ("alef (0627)", 0x0627),
    ("beh (0628)", 0x0628),
    ("jeem (062C)", 0x062C),
    ("dal (062F)", 0x062F),
    ("reh (0631)", 0x0631),
    ("lam (0644)", 0x0644),
    ("meem (0645)", 0x0645),
    ("alef final (FE8E)", 0xFE8E),
    ("beh final (FE90)", 0xFE90),
    ("jeem final (FE9E)", 0xFE9E),
    ("dal final (FEAA)", 0xFEAA),
    ("reh final (FEAE)", 0xFEAE),
    ("lam final (FEDE)", 0xFEDE),
    ("meem final (FEE2)", 0xFEE2),
]
inspect_chars(a12, ar_chars, "arialunicode_12 Arabic")

# Also check across ALL dims in arialunicode_12 and la_gioconda_12 to see distribution of ah vs h!
print("\n=== arialunicode_12 dims distribution ===")
ah_h_diffs = set()
for i, (ah, aw, w, h) in enumerate(a12.dims):
    if ah != h:
        ah_h_diffs.add((ah, h))
print("Pairs of (ah, h) where ah != h in arialunicode_12:", len(ah_h_diffs), list(ah_h_diffs)[:10])

print("\n=== la_gioconda_12 dims distribution ===")
g12 = CUF.decode(open(r"extracted\fonts\la_gioconda_12.cuf", "rb").read())
g_diffs = set()
for i, (ah, aw, w, h) in enumerate(g12.dims):
    if ah != h:
        g_diffs.add((ah, h))
print("Pairs of (ah, h) where ah != h in la_gioconda_12:", len(g_diffs), list(g_diffs)[:10])
