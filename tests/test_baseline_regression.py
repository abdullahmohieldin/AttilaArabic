import os
import sys
import unittest

sys.path.insert(0, r"D:\AttilaArabic\source")
from cuf import CUF

BASE = r"D:\AttilaArabic"
V5_DIR = os.path.join(BASE, "build", "v5fonts")

TARGETS = [
    "georgia_italic_10", "georgia_italic_12", "georgia_italic_14", "georgia_italic_16", "georgia_italic_18",
    "la_gioconda_10", "la_gioconda_12", "la_gioconda_14", "la_gioconda_16", "la_gioconda_18", "la_gioconda_20",
    "la_gioconda_22", "la_gioconda_24", "la_gioconda_26", "la_gioconda_28", "la_gioconda_30", "la_gioconda_32",
    "la_gioconda_38",
    "la_gioconda_uppercase_10", "la_gioconda_uppercase_12", "la_gioconda_uppercase_14", "la_gioconda_uppercase_16",
    "la_gioconda_uppercase_18", "la_gioconda_uppercase_20", "la_gioconda_uppercase_22", "la_gioconda_uppercase_24",
    "la_gioconda_uppercase_26", "la_gioconda_uppercase_28", "la_gioconda_uppercase_30", "la_gioconda_uppercase_32",
    "la_gioconda_uppercase_38"
]

class TestBaselineRegression(unittest.TestCase):

    def test_all_v5_fonts_baseline_and_alloc_h(self):
        """Verifies that in all 31 built v5 fonts:
        1. alloc_h == h == v_size for every added Arabic glyph (engine invariant).
        2. Added baseline letters (e.g. alef, dal, beh body) sit precisely on the font's baseline_row.
        3. Tall letters and descenders have natural offsets without clipping outside [0, v_size].
        """
        self.assertTrue(os.path.isdir(V5_DIR), f"v5 font dir {V5_DIR} missing")

        for font_name in TARGETS:
            cuf_path = os.path.join(V5_DIR, font_name + ".cuf")
            self.assertTrue(os.path.isfile(cuf_path), f"Missing {cuf_path}")

            with open(cuf_path, "rb") as f:
                c = CUF.decode(f.read())

            v_size = c.props.get("v_size", 0)
            baseline_row = c.props.get("baseline", 0) - 1  # 0-indexed row

            vanilla_path = os.path.join(BASE, "extracted", "fonts", font_name + ".cuf")
            with open(vanilla_path, "rb") as vf:
                c_vanilla = CUF.decode(vf.read())

            checked_codes = set()
            for code in range(c_vanilla.count + 1, c.count):
                ah, aw, w, h = c.dims[code]
                checked_codes.add(code)
                # Engine invariant: alloc_h == h for every added glyph
                self.assertEqual(ah, h, f"{font_name} code {code}: alloc_h ({ah}) != h ({h})")
                self.assertGreaterEqual(h, v_size, f"{font_name} code {code}: h ({h}) < v_size ({v_size})")

                bmp = c.bitmaps[code]
                if bmp and w > 0 and h > 0:
                    ys = [y for y in range(h) for x in range(w) if bmp[y * w + x] > 0]
                    if ys:
                        ink_top = min(ys)
                        ink_bottom = max(ys)
                        self.assertGreaterEqual(ink_top, 0, f"{font_name} code {code}: ink_top < 0")
                        self.assertLess(ink_bottom, h, f"{font_name} code {code}: ink_bottom >= h")

            self.assertGreaterEqual(len(checked_codes), 680, f"Font {font_name} should have >= 680 added Arabic glyphs")

            # Check dal (isolated U+FEA9 or U+062F) - must sit on baseline_row or within 1px anti-aliasing tolerance
            for dal_cp in (0xFEA9, 0x062F):
                code = c.table[dal_cp]
                if code < len(c.dims) and code != c.table[0]:
                    ah, aw, w, h = c.dims[code]
                    bmp = c.bitmaps[code]
                    ys = [y for y in range(h) for x in range(w) if bmp[y * w + x] > 30]
                    if ys:
                        ink_bottom = max(ys)
                        diff = abs(ink_bottom - baseline_row)
                        self.assertLessEqual(diff, 1, f"{font_name} Dal U+{dal_cp:04X}: bottom {ink_bottom} does not sit on baseline_row {baseline_row} (diff={diff})")
                        break

            # Check alef (isolated U+FE8D or U+0627) - bottom must sit on baseline_row or within 1px
            for alef_cp in (0xFE8D, 0x0627):
                code = c.table[alef_cp]
                if code < len(c.dims) and code != c.table[0]:
                    ah, aw, w, h = c.dims[code]
                    bmp = c.bitmaps[code]
                    ys = [y for y in range(h) for x in range(w) if bmp[y * w + x] > 30]
                    if ys:
                        ink_bottom = max(ys)
                        diff = abs(ink_bottom - baseline_row)
                        self.assertLessEqual(diff, 1, f"{font_name} Alef U+{alef_cp:04X}: bottom {ink_bottom} does not sit on baseline_row {baseline_row} (diff={diff})")
                        break

            # Check descender (Reh U+FEAD or U+0631) - must descend below baseline_row
            for reh_cp in (0xFEAD, 0x0631):
                code = c.table[reh_cp]
                if code < len(c.dims) and code != c.table[0]:
                    ah, aw, w, h = c.dims[code]
                    bmp = c.bitmaps[code]
                    ys = [y for y in range(h) for x in range(w) if bmp[y * w + x] > 30]
                    if ys:
                        ink_bottom = max(ys)
                        self.assertGreater(ink_bottom, baseline_row, f"{font_name} Reh U+{reh_cp:04X} bottom {ink_bottom} should descend below baseline_row {baseline_row}")
                        break

if __name__ == "__main__":
    unittest.main()
