#!/usr/bin/env python3
"""test_join_continuity.py — verifies Arabic glyph connectivity and no overshoot.

Rules:
  1. For each pair of letters that should connect (initial followed by final),
     ink at the connecting row touches or overlaps by at most 1 px (gap <= 0).
  2. No glyph's ink extends outside its cell (x < aw).
"""
import os
import sys
import unittest
import arabic_reshaper

sys.path.insert(0, r"D:\AttilaArabic\source")
from cuf import CUF

BASE = r"D:\AttilaArabic"
FONTS_DIR = os.path.join(BASE, "build", "v6fonts")

# Standard 22 Arabic letters connecting on both sides
CONNECTING_LETTERS = [
    0x0628, 0x062A, 0x062B, 0x062C, 0x062D, 0x062E, 0x0633, 0x0634,
    0x0635, 0x0636, 0x0637, 0x0638, 0x0639, 0x063A, 0x0641, 0x0642,
    0x0643, 0x0644, 0x0645, 0x0646, 0x0647, 0x064A
]


class TestJoinContinuity(unittest.TestCase):

    def test_overshoots_zero(self):
        """No glyph's ink should extend outside its advance width."""
        for font_name in ["la_gioconda_12.cuf", "la_gioconda_16.cuf", "georgia_italic_12.cuf"]:
            path = os.path.join(FONTS_DIR, font_name)
            if not os.path.exists(path):
                continue
            c = CUF.decode(open(path, "rb").read())
            overshoots = []
            for code, (ah, aw, w, h) in enumerate(c.dims):
                if ah == -128 or w == 0 or h == 0:
                    continue
                bm = c.bitmaps[code]
                xs = [x for y in range(h) for x in range(w) if bm[y * w + x] > 20]
                if xs and max(xs) >= aw:
                    overshoots.append((code, max(xs) - aw + 1))
            self.assertEqual(
                len(overshoots), 0,
                f"{font_name} has {len(overshoots)} overshooting glyphs: {overshoots[:10]}"
            )

    def test_gioconda_12_join_continuity(self):
        """In la_gioconda_12, 100% of connecting letter pairs touch or overlap <= 1px."""
        path = os.path.join(FONTS_DIR, "la_gioconda_12.cuf")
        c = CUF.decode(open(path, "rb").read())
        base_row = c.props["baseline"] - 1

        failed = 0
        tested = 0
        for l1 in CONNECTING_LETTERS:
            for l2 in CONNECTING_LETTERS:
                word = chr(l1) + chr(l2)
                reshaped = arabic_reshaper.reshape(word)
                cp1, cp2 = ord(reshaped[0]), ord(reshaped[1])
                c1, c2 = c.table[cp1], c.table[cp2]
                aw1, w1, h1 = c.dims[c1][1], c.dims[c1][2], c.dims[c1][3]
                aw2, w2, h2 = c.dims[c2][1], c.dims[c2][2], c.dims[c2][3]
                bm1, bm2 = c.bitmaps[c1], c.bitmaps[c2]

                cols1 = [x for r in (base_row, base_row-1, base_row+1) if 0 <= r < h1 for x in range(w1) if bm1[r * w1 + x] > 20]
                cols2 = [x for r in (base_row, base_row-1, base_row+1) if 0 <= r < h2 for x in range(w2) if bm2[r * w2 + x] > 20]
                if not cols1 or not cols2:
                    continue
                gap = (aw2 + min(cols1)) - max(cols2) - 1
                tested += 1
                if gap < -1 or gap > 0:
                    failed += 1

        self.assertEqual(failed, 0, f"la_gioconda_12 has {failed}/{tested} failed joins")


if __name__ == "__main__":
    unittest.main()
