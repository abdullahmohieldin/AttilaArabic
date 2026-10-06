#!/usr/bin/env python3
"""Contact sheet: 28 base letters x 4 presentation forms from arialunicode_10.

Green border = real glyph (unique non-empty bitmap).
Red border   = aliased to a fallback / empty (would render wrong).
First row shows the fallback glyphs for reference.

Usage: cuf_sheet.py <arialunicode_10.cuf> <out.png>
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from cuf import CUF  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# (name, base_char, isolated, initial, medial, final); None = form doesn't exist
LETTERS = [
    ("ALEF", 0x0627, 0xFE8D, None, None, 0xFE8E),
    ("BEH", 0x0628, 0xFE8F, 0xFE91, 0xFE92, 0xFE90),
    ("TEH", 0x062A, 0xFE95, 0xFE97, 0xFE98, 0xFE96),
    ("THEH", 0x062B, 0xFE99, 0xFE9B, 0xFE9C, 0xFE9A),
    ("JEEM", 0x062C, 0xFE9D, 0xFE9F, 0xFEA0, 0xFE9E),
    ("HAH", 0x062D, 0xFEA1, 0xFEA3, 0xFEA4, 0xFEA2),
    ("KHAH", 0x062E, 0xFEA5, 0xFEA7, 0xFEA8, 0xFEA6),
    ("DAL", 0x062F, 0xFEA9, None, None, 0xFEAA),
    ("THAL", 0x0630, 0xFEAB, None, None, 0xFEAC),
    ("REH", 0x0631, 0xFEAD, None, None, 0xFEAE),
    ("ZAIN", 0x0632, 0xFEAF, None, None, 0xFEB0),
    ("SEEN", 0x0633, 0xFEB1, 0xFEB3, 0xFEB4, 0xFEB2),
    ("SHEEN", 0x0634, 0xFEB5, 0xFEB7, 0xFEB8, 0xFEB6),
    ("SAD", 0x0635, 0xFEB9, 0xFEBB, 0xFEBC, 0xFEBA),
    ("DAD", 0x0636, 0xFEBD, 0xFEBF, 0xFEC0, 0xFEBE),
    ("TAH", 0x0637, 0xFEC1, 0xFEC3, 0xFEC4, 0xFEC2),
    ("ZAH", 0x0638, 0xFEC5, 0xFEC7, 0xFEC8, 0xFEC6),
    ("AIN", 0x0639, 0xFEC9, 0xFECB, 0xFECC, 0xFECA),
    ("GHAIN", 0x063A, 0xFECD, 0xFECF, 0xFED0, 0xFECE),
    ("FEH", 0x0641, 0xFED1, 0xFED3, 0xFED4, 0xFED2),
    ("QAF", 0x0642, 0xFED5, 0xFED7, 0xFED8, 0xFED6),
    ("KAF", 0x0643, 0xFED9, 0xFEDB, 0xFEDC, 0xFEDA),
    ("LAM", 0x0644, 0xFEDD, 0xFEDF, 0xFEE0, 0xFEDE),
    ("MEEM", 0x0645, 0xFEE1, 0xFEE3, 0xFEE4, 0xFEE2),
    ("NOON", 0x0646, 0xFEE5, 0xFEE7, 0xFEE8, 0xFEE6),
    ("HEH", 0x0647, 0xFEE9, 0xFEEB, 0xFEEC, 0xFEEA),
    ("WAW", 0x0648, 0xFEED, None, None, 0xFEEE),
    ("YEH", 0x064A, 0xFEF1, 0xFEF3, 0xFEF4, 0xFEF2),
]
SCALE = 4
PROBES = [0x0378, 0x2E9F]


def glyph_image(c, code):
    ah, aw, w, h = c.dims[code]
    img = Image.new("RGB", (max(w, 1), max(h, 1)), "white")
    if w and h:
        px = img.load()
        data = c.bitmaps[code]
        for y in range(h):
            for x in range(w):
                a = data[y * w + x]
                v = 255 - a  # opaque ink -> black
                px[x, y] = (v, v, v)
    return img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)


def main(src, dst):
    c = CUF.decode(open(src, "rb").read())
    # fallback set = bitmaps shared with known-unassigned probes
    fb = set()
    for p in PROBES:
        code = c.table[p]
        if code != 0xFFFF and code < len(c.dims):
            ah, aw, w, h = c.dims[code]
            fb.add((w, h, bytes(c.bitmaps[code])))

    def status(cp):
        if cp is None:
            return None
        code = c.table[cp]
        if code == 0xFFFF or code >= len(c.dims):
            return "empty"
        ah, aw, w, h = c.dims[code]
        if w == 0 or h == 0 or not c.bitmaps[code]:
            return "empty"
        if (w, h, bytes(c.bitmaps[code])) in fb:
            return "alias"
        return "real"

    rows = []
    fb_row = [("FALLBACK", None)] + [(f"PROBE U+{p:04X}", p) for p in PROBES] + \
        [(None, None)]
    rows.append(fb_row)
    for name, base, isol, init, med, fin in LETTERS:
        rows.append([(name, base), ("isol", isol), ("init", init),
                     ("med", med), ("fin", fin)])

    # measure
    cw, chh = 30 * SCALE, 32 * SCALE
    label, pad, namew = 14, 6, 150
    W = namew + 5 * (cw + pad)
    H = len(rows) * (chh + label + pad) + pad
    sheet = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(sheet)
    y = pad
    for row in rows:
        x = 0
        label_text, cp0 = row[0]
        dr.text((x + 4, y + 4), label_text, fill="black")
        x = namew
        for tag, cp in row[1:]:
            if cp is None:
                dr.text((x + 4, y + 4), "--", fill=(150, 150, 150))
            else:
                st = status(cp)
                col = {"real": (0, 170, 0), "alias": (220, 0, 0),
                       "empty": (220, 0, 0)}[st]
                code = c.table[cp]
                if st != "empty":
                    g = glyph_image(c, code)
                    sheet.paste(g, (x + 2, y))
                dr.rectangle([x, y, x + cw, y + chh], outline=col, width=2)
                t = f"U+{cp:04X} {st}"
                dr.text((x + 2, y + chh + 1), t, fill=col)
            x += cw + pad
        y += chh + label + pad
    sheet.save(dst)
    # console summary
    bad = 0
    for name, base, isol, init, med, fin in LETTERS:
        sts = {k: status(v) for k, v in
               [("isol", isol), ("init", init), ("med", med), ("fin", fin)]
               if v is not None}
        flag = "" if all(s == "real" for s in sts.values()) else "  <-- CHECK"
        if flag:
            bad += 1
        print(f"{name:5s} " + " ".join(f"{k}={v or '-':4s}"
              for k, v in sts.items()) + flag)
    print(f"letters with non-real forms: {bad}/28 -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
