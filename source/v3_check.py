#!/usr/bin/env python3
"""v3 check (required): for every merged font, list corpus Arabic codepoints
that are still missing (no code, empty bitmap, or fallback-shared). Also
verifies Latin untouched, kerning tail identical, magic preserved.

Usage: v3_check.py  (prints per-font verdict; exit 1 on any missing)
"""
import glob
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cuf import CUF  # noqa: E402

PROBES = [0x0378, 0x2E9F]


def is_arabic(cp):
    return (0x0600 <= cp <= 0x06FF or 0xFB50 <= cp <= 0xFDFF
            or 0xFE70 <= cp <= 0xFEFF)


def check(path, corpus_ar):
    new = CUF.decode(open(path, "rb").read())
    vanilla = CUF.decode(open(os.path.join(
        BASE, "extracted", "fonts", os.path.basename(path)), "rb").read())
    errs = []
    if new.magic != vanilla.magic:
        errs.append(f"magic {vanilla.magic!r}->{new.magic!r}")
    if new.tail != vanilla.tail:
        errs.append("kerning tail changed")
    # Latin spot-check: codes 0x20..0x7E bitmaps identical
    for cp in range(0x20, 0x7F):
        vc = vanilla.table[cp]
        nc = new.table[cp]
        if vc != nc or vanilla.bitmaps[vc] != new.bitmaps[nc]:
            errs.append(f"latin U+{cp:04X} changed")
            break
    # fallback set of merged font
    fb = set()
    for p in PROBES:
        code = new.table[p]
        if code != 0xFFFF and code < len(new.dims):
            ah, aw, w, h = new.dims[code]
            fb.add((w, h, bytes(new.bitmaps[code])))
    missing = []
    for cp in corpus_ar:
        code = new.table[cp]
        if code == 0xFFFF or code >= len(new.dims):
            missing.append((cp, "no-code"))
            continue
        ah, aw, w, h = new.dims[code]
        key = (w, h, bytes(new.bitmaps[code]))
        if w == 0 or h == 0 or not new.bitmaps[code]:
            missing.append((cp, "empty"))
        elif key in fb:
            missing.append((cp, "fallback-shared"))
    return errs, missing, len(new.dims)


def main():
    fonts_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        BASE, "build", "v3fonts")
    corpus_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        BASE, "localization", "corpus_v1v2.txt")
    corpus = [ord(ch) for ch in open(corpus_file, encoding="utf-8").read()]
    corpus_ar = sorted({cp for cp in corpus if is_arabic(cp)})
    bad = 0
    for p in sorted(glob.glob(os.path.join(fonts_dir, "*.cuf"))):
        errs, missing, n = check(p, corpus_ar)
        name = os.path.basename(p)
        if errs or missing:
            bad += 1
            print(f"FAIL {name} codes={n} " +
                  " ".join(errs) +
                  " ".join(f"U+{cp:04X}:{why}" for cp, why in missing))
        else:
            print(f"OK   {name} codes={n} missing=0")
    print(f"{'ALL FONTS PASS' if bad == 0 else f'{bad} FONTS FAIL'} "
          f"({len(corpus_ar)} corpus codepoints each)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
