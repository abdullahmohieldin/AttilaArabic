#!/usr/bin/env python3
"""Repeated-glyph pitch: distance between two occurrences of the same
codepoint in one measured line, divided by the sum of the font's advances
between them -> the implied scale. Repeat for several fonts to see which
advance table the engine is following."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_render as R  # noqa: E402

PF = R.PackFile(R.SHY)
_cache = {}


def font(leaf):
    if leaf not in _cache:
        name = next(n for n in PF.files if n.endswith(leaf))
        _cache[leaf] = R.CUF.decode(PF.get_file(name))
    return _cache[leaf]


def advances(c, text, model="aw"):
    out = []
    for ch in text:
        g = R.glyph(c, ord(ch))
        out.append(0 if g is None else (g["aw"] if model == "aw" else g["w"]))
    return out


def pair(text, cp, model="aw", fonts=None):
    """Report, per font, the advance span between the 1st and 2nd occurrence
    of cp (sum of advances of the characters in between) for both models."""
    idx = [i for i, ch in enumerate(text) if ord(ch) == cp]
    if len(idx) < 2:
        return
    a, b = idx[0], idx[1]
    print(f"  occurrences of U+{cp:04X} at {idx} -> span between positions "
          f"{a}..{b} covers {b - a} characters")
    for leaf in (fonts or sorted(n.split('\\')[-1] for n in PF.files
                                 if n.endswith('.cuf'))):
        c = font(leaf)
        if not all(c.table[ord(ch)] != 0xFFFF and c.table[ord(ch)] < c.count
                   for ch in text):
            continue
        av = advances(c, text, "aw")
        wv = advances(c, text, "w")
        sa = sum(av[a:b])
        sw = sum(wv[a:b])
        i = c.table[cp]
        ah, aw, w, h = c.dims[i]
        print(f"    {leaf:28s} cp aw={aw} w={w} | sum aw[a:b]={sa:3d} "
              f"sum w[a:b]={sw:3d}")


if __name__ == "__main__":
    # custom battle button: meem-to-meem, "معركة مخصصة" (visual order)
    t1 = "\uFE94\uFEBC\uFEBC\uFEA8\uFEE3 \uFE94\uFEDB\uFEAE\uFECC\uFEE3"
    print(f"custom battle button {t1!r}: measured meem start 162 -> 239 = 77 px")
    pair(t1, 0xFE94)
    # campaign button "إعدادات المعركة"
    t2 = "\uFE87\uFE8D\uFEA9\uFE8E\uFEAA\uFE8D\uFEAA \uFE94\uFEE0\uFEE4\uFEA4\uFEDF\uFE8D"
    print(f"\ncampaign btn {t2!r}: measured alif 240 -> 264 = 24 px, "
          f"teh 131 -> 193? n/a")
    pair(t2, 0xFE8D)
    pair(t2, 0xFEAA)
    # custom battle header "الحملة الجديدة"
    t3 = "\uFE8D\uFEDF\uFEE0\uFEE4\uFEA4\uFEDF\uFE8D \uFE8D\uFEDF\uFEE7\uFEAA\uFEF3\uFEAA\uFE93"
    print(f"\nheader {t3!r}")
    pair(t3, 0xFE8D)
    pair(t3, 0xFEAA)
    # ERE faction title "روما الشرقية"
    t4 = "\uFE8E\uFEE3\uFEED\uFEAD \uFE94\uFEF4\uFED7\uFEAE\uFEB8\uFEDF\uFE8D"
    print(f"\nERE title {t4!r}  (measured FEF4 cx 970.7, FE91 n/a; "
          f"FE8E cx 900.1)")
    pair(t4, 0xFEDF)
