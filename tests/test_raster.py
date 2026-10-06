import os, sys
from PIL import ImageFont
import unicodedata

sys.path.insert(0, r"D:\AttilaArabic\source")
from cuf import CUF

BASE = r"D:\AttilaArabic"
TAJAWAL = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")

def render_glyph(px, char):
    f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
    adv = int(round(f.getlength(char)))
    mask = f.getmask(char, mode="L")
    w, h = mask.size
    data = bytes(mask)
    xs = [x for y in range(h) for x in range(w) if data[y * w + x] > 0]
    ys = [y for y in range(h) for x in range(w) if data[y * w + x] > 0]
    if not xs:
        return b"", 0, 0, 0, 0, adv
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    ink = bytearray()
    for y in range(y0, y1 + 1):
        ink += data[y * w + x0:y * w + x1 + 1]
    return bytes(ink), x1 - x0 + 1, y1 - y0 + 1, x0, y0, adv

def vanilla_metrics(c):
    code = c.table[0x48]
    ah, aw, w, h = c.dims[code]
    d = c.bitmaps[code]
    rows = [y for y in range(h) if any(d[y * w + x] > 20 for x in range(w))]
    top, bottom = min(rows), max(rows)
    return {"cap": bottom - top + 1, "top": top, "bottom": bottom,
            "cell_h": h, "vsize": c.props["v_size"]}

def calibrate(vanilla_h_cap, lo=8, hi=64):
    best, bestpx = None, None
    for px in range(lo, hi + 1):
        f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        x0, y0, x1, y1 = f.getbbox("H")
        h = y1 - y0
        if best is None or abs(h - vanilla_h_cap) < best:
            best, bestpx = abs(h - vanilla_h_cap), px
    return bestpx

c = CUF.decode(open(os.path.join(BASE, "extracted", "fonts", "la_gioconda_10.cuf"), "rb").read())
vm = vanilla_metrics(c)
px_cap = calibrate(vm["cap"])
V = vm["cell_h"]
OVER = 2

print(f"la_gioconda_10: V={V} cap={vm['cap']} bottom={vm['bottom']} px_cap={px_cap}")

f = ImageFont.truetype(TAJAWAL, px_cap, layout_engine=ImageFont.Layout.BASIC)
_, (_, ty0, _, ty1) = 0, f.getbbox("H")
shift = vm["bottom"] - ty1

test_cps = list(range(0x0621, 0x064B)) + [0x0640] + list(range(0x064B, 0x0653)) + [0x0670] + [0x060C, 0x061B, 0x061F] + list(range(0x0660, 0x066A)) + [0xFEFF]
for cp in test_cps:
    ch = chr(cp)
    ink, iw, ih, x0, y0, adv = render_glyph(px_cap, ch)
    top = y0 + shift
    fits = (top >= -OVER and top + ih <= V + OVER) if ink else "NO INK"
    if fits != True:
        print(f"U+{cp:04X} {unicodedata.name(ch, '?')}: ink={len(ink)} top={top} bottom={top+ih} (V={V}, range [-{OVER}..{V+OVER}]) -> {fits}")
