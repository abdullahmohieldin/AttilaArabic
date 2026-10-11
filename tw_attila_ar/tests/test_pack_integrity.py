import unittest
import sys
import os
import struct

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from source.loc import decode
from tools.packfile import PackFile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PACK_PATH = os.path.join(PROJECT_ROOT, "tw_attila_ar", "out", "Attila_Arabic_Part1.pack")


class TestPackIntegrity(unittest.TestCase):
    def test_pack_exists_and_header(self):
        self.assertTrue(os.path.exists(PACK_PATH), f"Pack file missing at {PACK_PATH}")
        pack = PackFile(PACK_PATH)
        self.assertEqual(pack.header.version, b"PFH4", "Magic header must be PFH4")
        self.assertEqual(pack.header.pack_type, 3, "Pack type must be 3 (Mod pack)")
        self.assertEqual(pack.header.file_count, 15, "Expected exactly 15 files (14 locs + 1 UI layout)")

    def test_pack_contents_listing(self):
        pack = PackFile(PACK_PATH)
        files = pack.list_files()
        self.assertEqual(len(files), 15)

        expected_locs = [
            "text/db/campaign_effect_scopes.loc",
            "text/db/campaign_map_playable_areas.loc",
            "text/db/campaigns.loc",
            "text/db/effect_bundles.loc",
            "text/db/effects.loc",
            "text/db/faction_groups.loc",
            "text/db/factions.loc",
            "text/db/names.loc",
            "text/db/random_localisation_strings.loc",
            "text/db/religions.loc",
            "text/db/start_pos_factions.loc",
            "text/db/ui_unit_bullet_point_enums.loc",
            "text/db/ui_unit_stats.loc",
            "text/db/uied_component_texts.loc",
        ]
        for loc_path in expected_locs:
            self.assertIn(loc_path.replace("/", "\\"), [f.replace("/", "\\") for f in files])

        self.assertIn("ui\\frontend ui\\sp_grand_campaign", [f.replace("/", "\\") for f in files])

    def test_loc_deserialization(self):
        pack = PackFile(PACK_PATH)
        factions_data = pack.get_file("text\\db\\factions.loc") or pack.get_file("text/db/factions.loc")
        self.assertIsNotNone(factions_data)

        rows, pos, total = decode(factions_data)
        self.assertEqual(pos, total)
        self.assertGreater(len(rows), 2000)
        # Find Eastern Roman Empire key
        match = [r for r in rows if r[0] == "factions_screen_name_att_fact_eastern_roman_empire"]
        self.assertEqual(len(match), 1)
        # Ensure it is shaped
        self.assertTrue(any(0xFE70 <= ord(c) <= 0xFEFF for c in match[0][1]))


if __name__ == "__main__":
    unittest.main()
