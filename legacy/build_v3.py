#!/usr/bin/env python3
"""v3 font merge (BUILD ONLY): rasterize Tajawal-Regular per CUF size,
calibrated to each vanilla font's Latin cap-height/baseline, and append
Arabic glyphs to copies of la_gioconda[_uppercase]_* and georgia_italic_*.

Rules enforced:
- native raster per size (never scale one bitmap)
- vanilla Latin glyphs + kerning tail byte-identical
- only Arabic-block codepoints added (+ blank placeholders preserving
  dangling PUA references)
- original magic (CUF0/CUF1) kept per file
- missing-codepoint check vs corpus (source/v3_check.py)

Usage: build_v3.py
Outputs: build/v3fonts/<name>.cuf, release/Attila_Arabic_POC_v3_fonttest.pack,
         docs/test-pack-manifest-v3.md, logs/v3_build.txt
"""
import os
import struct
import subprocess
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cuf import CUF  # noqa: E402
from PIL import ImageFont  # noqa: E402

VENV_PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
PACK_PY = os.path.join(BASE, "tools", "packfile.py")
COPY_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
TAJAWAL = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "v3"
# v3b: same rules as v3, extended corpus. v3b_big: cap-matched px, cells may
# exceed v_size by up to 2px (baseline row preserved, cell grows upward).
BIG = (VARIANT == "v3b_big")
CORPUS_FILE = {"v3": None, "v3b": "corpus_v2b_full.txt",
               "v3b_big": "corpus_v2b_full.txt"}[VARIANT]
FONTS_OUT = os.path.join(BASE, "build",
                         {"v3": "v3fonts", "v3b": "v3bfonts",
                          "v3b_big": "v3bbigfonts"}[VARIANT])
REL = os.path.join(BASE, "release",
                   {"v3": "Attila_Arabic_POC_v3_fonttest.pack",
                    "v3b": "Attila_Arabic_POC_v3b_fonttest.pack",
                    "v3b_big": "Attila_Arabic_POC_v3b_big.pack"}[VARIANT])
LOGNAME = {"v3": "v3_build.txt", "v3b": "v3b_build.txt",
           "v3b_big": "v3bbig_build.txt"}[VARIANT]
OVER = 2 if BIG else 0

SIZES_GIOC = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]
SIZES_GEORG = [10, 12, 14, 16, 18]
TARGETS = ([f"la_gioconda_{s}" for s in SIZES_GIOC]
           + [f"la_gioconda_uppercase_{s}" for s in SIZES_GIOC]
           + [f"georgia_italic_{s}" for s in SIZES_GEORG])


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args}\n{r.stderr[-2000:]}")
    return r.stdout


def is_arabic(cp):
    return (0x0600 <= cp <= 0x06FF or 0xFB50 <= cp <= 0xFDFF
            or 0xFE70 <= cp <= 0xFEFF)


def base_letter(cp):
    """Compatibility decomposition base, e.g. FE8D -> 0627. None if none."""
    try:
        decomp = unicodedata.decomposition(chr(cp))
    except Exception:
        return None
    parts = decomp.split()
    if len(parts) == 2 and parts[0].startswith("<"):
        try:
            return int(parts[1], 16)
        except ValueError:
            return None
    return None


def tajawal_cmap():
    from fontTools.ttLib import TTFont
    return TTFont(TAJAWAL).getBestCmap()


def cap_height(font):
    # BASIC layout: single-glyph bbox, no shaping
    x0, y0, x1, y1 = font.getbbox("H")
    return y1 - y0, (x0, y0, x1, y1)


def calibrate(vanilla_h_cap, lo=8, hi=64):
    best, bestpx = None, None
    for px in range(lo, hi + 1):
        f = ImageFont.truetype(TAJAWAL, px,
                               layout_engine=ImageFont.Layout.BASIC)
        h, _ = cap_height(f)
        if best is None or abs(h - vanilla_h_cap) < best:
            best, bestpx = abs(h - vanilla_h_cap), px
    return bestpx


def render_glyph(px, char, canvas=256):
    """Returns (ink_bytes, w, h, x0, y0_top, advance). y measured from top."""
    f = ImageFont.truetype(TAJAWAL, px,
                           layout_engine=ImageFont.Layout.BASIC)
    adv = int(round(f.getlength(char)))
    mask = f.getmask(char, mode="L")
    w, h = mask.size
    data = bytes(mask)
    # ink bbox
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
    """Baseline row + cap height from vanilla 'H'."""
    code = c.table[0x48]
    ah, aw, w, h = c.dims[code]
    d = c.bitmaps[code]
    rows = [y for y in range(h)
            if any(d[y * w + x] > 20 for x in range(w))]
    top, bottom = min(rows), max(rows)
    return {"cap": bottom - top + 1, "top": top, "bottom": bottom,
            "cell_h": h, "vsize": c.props["v_size"]}


def merge_one(name, corpus_ar, cmap, log):
    src = os.path.join(BASE, "extracted", "fonts", name + ".cuf")
    c = CUF.decode(open(src, "rb").read())
    assert c.bitmap_total() == c.size, name
    vm = vanilla_metrics(c)
    px_cap = calibrate(vm["cap"])
    V = vm["cell_h"]
    assert V == c.props["v_size"], (name, V, c.props["v_size"])
    # source char per corpus codepoint (before px loop: px-independent)
    src_of, missing = {}, []
    for cp in sorted(corpus_ar):
        if cp in cmap:
            src_of[cp] = chr(cp)
        else:
            b = base_letter(cp)
            if b is not None and b in cmap:
                src_of[cp] = chr(b)
            else:
                missing.append(cp)
    # px: cap-match upper bound, reduced until every glyph fits.
    # normal: inside V. BIG: cells may exceed V by OVER px (baseline kept).
    chosen, layouts = None, {}
    for px in range(px_cap, 7, -1):
        f = ImageFont.truetype(TAJAWAL, px,
                               layout_engine=ImageFont.Layout.BASIC)
        _, (_, ty0, _, ty1) = cap_height(f)
        shift = vm["bottom"] - ty1
        ok, cur = True, {}
        for cp, ch in src_of.items():
            ink, iw, ih, x0, y0, adv = render_glyph(px, ch)
            top = y0 + shift
            if not ink or top < -OVER or top + ih > V + OVER:
                ok = False
                break
            cur[cp] = (ink, iw, ih, x0, y0, adv)
        if ok:
            chosen, layouts = (px, shift), cur
            break
    assert chosen is not None, name + " no fitting px"
    px, shift = chosen
    # dangling codes referenced by table (preserve via blanks)
    dangling = sorted({v for v in c.table
                       if v != 0xFFFF and v >= len(c.dims)})
    new_dims = list(c.dims)
    new_maps = list(c.bitmaps)
    # blanks for dangling codes, in ascending code order
    for dcode in dangling:
        while len(new_dims) < dcode:
            raise AssertionError((name, dcode))  # non-contiguous; inspect
        new_dims.append((-128, 0, 0, 0))
        new_maps.append(b"")
    added = {}
    clipped = []
    for cp in sorted(corpus_ar):
        if cp not in layouts:
            continue  # no Tajawal source (see missing[]) — nothing else skips
        ink, iw, ih, x0, y0, adv = layouts[cp]
        top = y0 + shift
        # BIG cells may extend above row 0 (baseline row preserved).
        ctop = min(top, 0)
        cbot = max(top + ih, V)
        chh = cbot - ctop
        assert top >= -OVER and top + ih <= V + OVER, (cp, top, ih, V)
        assert chh <= V + OVER, (cp, chh, V)
        # cell keeps full ink incl. bearings; alloc_w = true advance
        # (RPFM: advance may differ from bitmap width).
        left = x0 if x0 >= 0 else 0
        cw = max(adv, left + iw)
        if adv <= 0:
            clipped.append((cp, "no-advance", adv))
            continue
        cell = bytearray(chh * cw)
        for y in range(ih):
            a, b = (top - ctop + y) * cw + left, \
                (top - ctop + y) * cw + left + iw
            assert b - a == iw and b <= len(cell), (cp, a, b, len(cell))
            cell[a:b] = ink[y * iw:(y + 1) * iw]
        code = len(new_dims)
        new_dims.append((chh if chh < 128 else 127, min(adv, 255), cw, chh))
        new_maps.append(bytes(cell))
        added[cp] = code
    # repoint table
    table = list(c.table)
    for cp, code in added.items():
        table[cp] = code
    c.table = table
    c.dims = new_dims
    c.bitmaps = new_maps
    # count/size auto-derived on encode
    out = c.encode()
    c2 = CUF.decode(out)
    assert c2.encode() == out, name + " unstable"
    open(os.path.join(FONTS_OUT, name + ".cuf"), "wb").write(out)
    maxh = max(h for (_, _, _, h) in new_dims[len(new_dims) - len(added):]
               ) if added else V
    log.append(f"{name}: magic={c.magic!r} px={px} cell={V} maxcell={maxh} "
               f"big={BIG} vanilla_codes={len(c.dims) - len(added) - len(dangling)} "
               f"+blanks={len(dangling)} +arabic={len(added)} "
               f"missing_src={len(missing)} clipped={len(clipped)}")
    for cp, *rest in clipped:
        log.append(f"  CLIP U+{cp:04X} {rest} src={src_of.get(cp, '?')!r}")
    for cp in missing:
        log.append(f"  NOSRC U+{cp:04X} {unicodedata.name(chr(cp), '?')}")
    return added, missing


def main():
    os.makedirs(FONTS_OUT, exist_ok=True)
    corpname = CORPUS_FILE or "corpus_v1v2.txt"
    corpus = [ord(ch) for ch in
              open(os.path.join(BASE, "localization", corpname),
                   encoding="utf-8").read()]
    corpus_ar = sorted({cp for cp in corpus if is_arabic(cp)})
    other = sorted({cp for cp in corpus if not is_arabic(cp)})
    print(f"corpus arabic: {len(corpus_ar)}, non-arabic: "
          f"{['U+%04X' % cp for cp in other]}")
    cmap = tajawal_cmap()
    log = [f"Tajawal-Regular.ttf SHA256 pinned in fonts doc; "
           f"corpus_ar={len(corpus_ar)}"]
    # U+2014 check on one vanilla font (all share Latin coverage approach)
    c0 = CUF.decode(open(os.path.join(
        BASE, "extracted", "fonts", "la_gioconda_10.cuf"), "rb").read())
    e14 = c0.table[0x2014]
    log.append(f"vanilla la_gioconda_10 U+2014 -> {e14:#x} "
               f"{'present' if e14 < len(c0.dims) else 'MISSING (not added)'}")
    for name in TARGETS:
        merge_one(name, corpus_ar, cmap, log)
    open(os.path.join(BASE, "logs", LOGNAME), "w",
         encoding="utf-8").write("\n".join(log) + "\n")
    print("\n".join(log[-8:]))
    # assemble pack
    run(VENV_PY, PACK_PY, "create", os.path.join(BASE, "build",
                                                 VARIANT + ".pack"),
        "--type", "3", "--version", "PFH4")
    for name in TARGETS:
        run(VENV_PY, PACK_PY, "add", os.path.join(BASE, "build",
                                                  VARIANT + ".pack"),
            "font\\" + name + ".cuf",
            os.path.join(FONTS_OUT, name + ".cuf"))
    run(VENV_PY, PACK_PY, "set-type", os.path.join(BASE, "build",
                                                   VARIANT + ".pack"),
        "3", "--output", REL)
    print(run(VENV_PY, PACK_PY, "info", REL))
    print("wrote", REL)


if __name__ == "__main__":
    main()
