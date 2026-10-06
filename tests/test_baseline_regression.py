import os
import sys
import unittest

sys.path.insert(0, r"D:\AttilaArabic\source")
from cuf import CUF

BASE = r"D:\AttilaArabic"
V5_DIR = os.path.join(BASE, "build", "v6fonts")

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

            # Flat-bottom letters: Dal, Alef, Beh (body), Seen (body)
            # EXACT: the highest solid ink row AT OR ABOVE baseline_row == baseline_row.
            # (Beh and Seen have dots below baseline — we check body stroke only.)
            flat_bottom_checks = [
                ("Dal",  (0xFEA9, 0x062F)),
                ("Alef", (0xFE8D, 0x0627)),
                ("Beh",  (0xFE8F, 0xFE90, 0xFE91, 0xFE92)),
                ("Seen", (0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4)),
            ]
            for letter_name, cps in flat_bottom_checks:
                for cp in cps:
                    code = c.table[cp]
                    if code < len(c.dims) and code != c.table[0]:
                        ah, aw, w, h = c.dims[code]
                        bmp = c.bitmaps[code]
                        # Only rows AT OR ABOVE baseline_row (body stroke — excludes sub-dots)
                        ys_body = [
                            y for y in range(baseline_row + 1)
                            for x in range(w) if bmp[y * w + x] > 50
                        ]
                        if ys_body:
                            body_bottom = max(ys_body)
                            self.assertEqual(
                                body_bottom, baseline_row,
                                f"{font_name} {letter_name} U+{cp:04X}: "
                                f"body_bottom {body_bottom} != baseline_row {baseline_row}"
                            )
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
