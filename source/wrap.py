#!/usr/bin/env python3
"""wrap.py — CUF-advance-accurate wrapping for pre-shaped Arabic.

No estimated widths, no safety factor (per spec change #3): every candidate
line is shaped with source/shape.py and measured EXACTLY from the merged
CUF's per-code advances (alloc_w). The longest fitting candidate wins.

Engine model (VERIFIED by v2/v3 screenshots): the engine draws the stored
string left-to-right with no extra BiDi. Lines are stored top-to-bottom in
logical order.

Usage:
  wrap.py --font <merged.cuf> --width <px> [--single] '<logical text>'

  multi-line (default): greedy word wrap; overlong single words are emitted
    whole and flagged OVERFLOW (never silently split).
  --single: one visual line; if it overflows, words are dropped from the
    LOGICAL end and '…' appended at the logical end until it fits (fixes the
    dropdown clip, which cut the logical start).

Box widths come from tools/widths.cfg (screenshot-measured, 1920x1080,
UNVERIFIED for other resolutions).
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cuf import CUF  # noqa: E402
from shape import shape  # noqa: E402

ELLIPSIS = "…"


def load(font_path):
    c = CUF.decode(open(font_path, "rb").read())
    adv = {}
    for cidx in range(len(c.dims)):
        adv[cidx] = c.dims[cidx][1]  # alloc_w = advance (VERIFIED semantics)
    return c, adv


def visual_width(visual, c, adv):
    total, unknown = 0, []
    for ch in visual:
        cp = ord(ch)
        code = c.table[cp] if cp < 65536 else 0xFFFF
        if code == 0xFFFF or code >= len(c.dims):
            unknown.append(cp)
            w = adv_fallback(c)
        else:
            w = adv[code]
        total += w
    return total, unknown


def adv_fallback(c):
    return c.dims[c.table[0x20]][1]  # space advance


def wrap_multi(logical, c, adv, width):
    lines, dropped_overflow = [], []
    cur = []
    for word in logical.split(" "):
        cand = " ".join(cur + [word]) if cur else word
        v = shape(cand)
        w, _ = visual_width(v, c, adv)
        if w <= width or not cur:
            cur.append(word)
            if w > width:
                dropped_overflow.append(cand)
        else:
            lines.append(shape(" ".join(cur)))
            cur = [word]
    if cur:
        lines.append(shape(" ".join(cur)))
    return lines, dropped_overflow


def wrap_single(logical, c, adv, width):
    words = logical.split(" ")
    ell = ELLIPSIS if has_glyph(c, ord(ELLIPSIS)) else "..."
    while words:
        cand = " ".join(words)
        v = shape(cand)
        w, _ = visual_width(v, c, adv)
        if w <= width:
            return v, logical[len(cand):].strip()
        words = words[:-1]  # clip the LOGICAL end, never the start
    # even one word + ellipsis doesn't fit
    v = shape(ell)
    return v, logical


def has_glyph(c, cp):
    if cp >= 65536:
        return False
    code = c.table[cp]
    if code == 0xFFFF or code >= len(c.dims):
        return False
    ah, aw, w, h = c.dims[code]
    return w > 0 and h > 0 and len(c.bitmaps[code]) > 0


def main():
    args = sys.argv[1:]
    font = args[args.index("--font") + 1]
    width = int(args[args.index("--width") + 1])
    single = "--single" in args
    logical = args[-1]
    c, adv = load(font)
    if single:
        v, dropped = wrap_single(logical, c, adv, width)
        w, unk = visual_width(v, c, adv)
        print(f"width={w}/{width} dropped={dropped!r} "
              f"unknown={[hex(x) for x in unk]}")
        print("visual-codepoints:",
              " ".join(f"U+{ord(x):04X}" for x in v))
    else:
        lines, over = wrap_multi(logical, c, adv, width)
        for i, line in enumerate(lines):
            w, unk = visual_width(line, c, adv)
            print(f"line{i} width={w}/{width} "
                  f"unknown={[hex(x) for x in unk]}")
        for o in over:
            print(f"OVERFLOW-KEPT {o!r}")
        print("---")
        for line in lines:
            print(" ".join(f"U+{ord(x):04X}" for x in line))


if __name__ == "__main__":
    main()
