#!/usr/bin/env python3
"""Arabic shaping pipeline v1 (project POC).

UTF-8 logical Arabic -> protect [[tags]]/%placeholders -> arabic_reshaper
-> python-bidi visual order -> game-ready string.

Usage: shape.py '<text>'  (prints codepoints + visual string)
"""
import re
import sys

import arabic_reshaper
from bidi.algorithm import get_display

TAG_RE = re.compile(r"(\[\[.*?\]\]|%[sdif]|{\d+})")
_MARK = "\ue000"


def shape(text: str, base_dir: str = "R") -> str:
    parts = TAG_RE.split(text)
    stash = {}
    # even indices are plain text, odd indices are protected tokens
    out, idx = [], 0
    for i, p in enumerate(parts):
        if i % 2 == 0:
            out.append(p)
        else:
            stash[idx] = p
            out.append(_MARK + chr(0xE001 + idx))
            idx += 1
    joined = "".join(out)
    reshaped = arabic_reshaper.reshape(joined)
    visual = get_display(reshaped, base_dir=base_dir)
    for i, tok in stash.items():
        visual = visual.replace(_MARK + chr(0xE001 + i), tok)
    return visual


if __name__ == "__main__":
    t = sys.argv[1]
    v = shape(t)
    print("logical :", " ".join(f"U+{ord(ch):04X}" for ch in t))
    print("visual  :", " ".join(f"U+{ord(ch):04X}" for ch in v))
    print("render  :", v)
