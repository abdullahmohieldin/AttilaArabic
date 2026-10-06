import sys, os, unicodedata
from fontTools.ttLib import TTFont
from PIL import ImageFont

sys.path.insert(0, r"D:\AttilaArabic\source")
from cuf import CUF

BASE = r"D:\AttilaArabic"
TAJAWAL = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")
cmap = TTFont(TAJAWAL).getBestCmap()

def base_letter(cp):
    try:
        decomp = unicodedata.decomposition(chr(cp))
    except Exception:
        return None
    parts = decomp.split()
    if len(parts) >= 2 and parts[0].startswith("<"):
        try:
            return int(parts[1], 16)
        except ValueError:
            return None
    return None

target_cps = set()
target_cps.update(range(0x0621, 0x064B))
target_cps.add(0x0640)
target_cps.update(range(0x064B, 0x0653))
target_cps.add(0x0670)
target_cps.update([0x060C, 0x061B, 0x061F, 0x066A, 0x066B, 0x066C, 0x06D4])
target_cps.update(range(0x0660, 0x066A))
target_cps.update(range(0xFB50, 0xFE00))
target_cps.update(range(0xFE70, 0xFF00))

decomp_harakat = {
    0xFE70: 0x064B, 0xFE72: 0x064C, 0xFE74: 0x064D, 0xFE76: 0x064E,
    0xFE78: 0x064F, 0xFE7A: 0x0650, 0xFE7C: 0x0651, 0xFE7E: 0x0652
}

src_of = {}
for cp in sorted(target_cps):
    if cp in decomp_harakat:
        src_of[cp] = chr(decomp_harakat[cp])
    elif cp in cmap:
        src_of[cp] = chr(cp)
    else:
        b = base_letter(cp)
        if b is not None and b in cmap:
            src_of[cp] = chr(b)

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
        h = f.getbbox("H")[3] - f.getbbox("H")[1]
        if best is None or abs(h - vanilla_h_cap) < best:
            best, bestpx = abs(h - vanilla_h_cap), px
    return bestpx

SIZES_GIOC = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]
SIZES_GEORG = [10, 12, 14, 16, 18]
TARGETS = ([f"la_gioconda_{s}" for s in SIZES_GIOC]
           + [f"la_gioconda_uppercase_{s}" for s in SIZES_GIOC]
           + [f"georgia_italic_{s}" for s in SIZES_GEORG])

OVER = 2
fails = []

for name in TARGETS:
    src = os.path.join(BASE, "extracted", "fonts", name + ".cuf")
    c = CUF.decode(open(src, "rb").read())
    vm = vanilla_metrics(c)
    V = vm["cell_h"]
    baseline_row = vm["bottom"]
    px_cap = calibrate(vm["cap"])

    chosen = None
    for px in range(px_cap, 7, -1):
        f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        ascent, _ = f.getmetrics()
        ok = True
        for cp, ch in src_of.items():
            bbox = f.getbbox(ch)
            if not bbox:
                continue
            bx0, by0, bx1, by1 = bbox
            top = baseline_row + by0 - ascent
            bot = baseline_row + by1 - ascent
            if top < -OVER or bot > V + OVER:
                ok = False
                break
        if ok:
            chosen = px
            break
    if chosen is None:
        fails.append(name)
    else:
        print(f"{name:30}: cap={vm['cap']:2} V={V:2} base={baseline_row:2} px_cap={px_cap:2} chosen={chosen}")

print(f"Total fails: {len(fails)}")
