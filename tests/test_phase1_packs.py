import unittest
import os
import hashlib
from tools.packfile import PackFile
from source.cuf import CUF
from source.loc import decode as loc_decode

BASE = r"D:\AttilaArabic"
VANILLA_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
LOC_PACK = os.path.join(BASE, "release", "Attila_Arabic_Phase1.pack")
FONT_PACK = os.path.join(BASE, "release", "Attila_Arabic_Phase1_fonts.pack")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


class TestPhase1Packs(unittest.TestCase):
    def test_vanilla_integrity(self):
        h = sha256_file(VANILLA_PACK)
        self.assertEqual(h, "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D")

    def test_loc_pack_structure(self):
        self.assertTrue(os.path.exists(LOC_PACK))
        pf = PackFile(LOC_PACK)
        self.assertEqual(pf.header.version, b"PFH4")
        self.assertEqual(pf.header.pack_type, 3) # mod type
        self.assertEqual(len(pf.files), 4)

        expected_keys = [
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_button_txt_NewState_Text_30006e"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_string_NewState_Text_30006e"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_tx_factions_NewState_Text_90022"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_selection_txt_NewState_Text_90022"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_tab_factions_Tooltip_90022"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_handle_NewState_Tooltip_7000b"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_handle_Tooltip_7000b"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_cmp_diff_slider_Tooltip_7000b"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_medal1_default_Tooltip_5003a"),
            ("text\\db\\uied_component_texts.loc", "uied_component_texts_localised_string_header_cultural_NewState_Text_5e0000"),
            ("text\\db\\random_localisation_strings.loc", "random_localisation_strings_string_difficulty_level_3"),
            ("text\\db\\random_localisation_strings.loc", "random_localisation_strings_string_hard"),
            ("text\\db\\random_localisation_strings.loc", "random_localisation_strings_string_campaign_difficulty_description_2"),
            ("text\\db\\random_localisation_strings.loc", "random_localisation_strings_string_campaign_difficulty_slider_legendary"),
            ("text\\db\\factions.loc", "factions_screen_name_att_fact_eastern_roman_empire"),
            ("text\\db\\start_pos_factions.loc", "start_pos_factions_description_2120156326"),
            ("text\\db\\start_pos_factions.loc", "start_pos_factions_long_description_2120156326"),
        ]

        for internal_file, key in expected_keys:
            raw = pf.get_file(internal_file)
            self.assertIsNotNone(raw, f"Missing loc file in pack: {internal_file}")
            rows, _, _ = loc_decode(raw)
            d = {r[0]: r[1] for r in rows}
            self.assertIn(key, d, f"Key {key} not found in {internal_file}")
            self.assertTrue(len(d[key]) > 0, f"Key {key} has empty text")

    def test_fonts_pack_structure(self):
        self.assertTrue(os.path.exists(FONT_PACK))
        pf = PackFile(FONT_PACK)
        self.assertEqual(pf.header.version, b"PFH4")
        self.assertEqual(pf.header.pack_type, 3) # mod type
        self.assertEqual(len(pf.files), 31)

        v_pack = PackFile(VANILLA_PACK)

        for fpath in pf.files:
            v_raw = v_pack.get_file(fpath)
            self.assertIsNotNone(v_raw, f"Missing vanilla counterpart for {fpath}")
            v_cuf = CUF.decode(v_raw)

            m_raw = pf.get_file(fpath)
            m_cuf = CUF.decode(m_raw)

            # Assert properties match
            self.assertEqual(m_cuf.props, v_cuf.props)
            # Assert kerning tail matches
            self.assertEqual(m_cuf.tail, v_cuf.tail)
            # Assert original glyph count preserved
            self.assertGreater(len(m_cuf.dims), len(v_cuf.dims))
            self.assertEqual(m_cuf.dims[:len(v_cuf.dims)], v_cuf.dims)
            self.assertEqual(m_cuf.bitmaps[:len(v_cuf.bitmaps)], v_cuf.bitmaps)

            # Assert Latin characters map to original indices
            for ch in range(32, 127):
                self.assertEqual(m_cuf.table[ch], v_cuf.table[ch])

            # Assert Round 3 PUA blank spacer codes map to appended glyphs in PUA (0xE010-0xE015)
            self.assertGreater(m_cuf.table[0xE010], len(v_cuf.dims) - 1)  # Blank 32px
            self.assertGreater(m_cuf.table[0xE011], len(v_cuf.dims) - 1)  # Blank 16px
            self.assertGreater(m_cuf.table[0xE012], len(v_cuf.dims) - 1)  # Blank 8px
            self.assertGreater(m_cuf.table[0xE013], len(v_cuf.dims) - 1)  # Blank 4px
            self.assertGreater(m_cuf.table[0xE014], len(v_cuf.dims) - 1)  # Blank 2px
            self.assertGreater(m_cuf.table[0xE015], len(v_cuf.dims) - 1)  # Blank 1px

            # Assert real Forms-B characters are mapped to appended glyphs
            for real_cp in [0xFE80, 0xFE8E, 0xFE90, 0xFE92, 0xFEBC, 0xFEE3]:
                self.assertGreater(m_cuf.table[real_cp], len(v_cuf.dims) - 1)

            # Assert positional forms are distinct from isolated forms (anti-regression check for decompose_cp bug)
            idx_initial_beh = m_cuf.table[0xFE91]
            idx_isolated_beh = m_cuf.table[0xFE8F]
            self.assertNotEqual(m_cuf.bitmaps[idx_initial_beh], m_cuf.bitmaps[idx_isolated_beh])

            # Assert isolated Alef (0xFE8D) has ink and is not empty
            idx_alef = m_cuf.table[0xFE8D]
            self.assertGreater(idx_alef, len(v_cuf.dims) - 1)
            bm_alef = m_cuf.bitmaps[idx_alef]
            self.assertTrue(any(b > 0 for b in bm_alef))


if __name__ == "__main__":
    unittest.main()

