import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.shape_pipeline import shape_part1_entry


class TestShapePipeline(unittest.TestCase):
    def test_single_line_shaping(self):
        entry = {
            "key": "factions_screen_name_att_faction_eastern_roman_empire",
            "en": "Eastern Roman Empire",
            "ar": "الإمبراطورية الرومانية الشرقية"
        }
        shaped = shape_part1_entry(entry)
        self.assertIsInstance(shaped, str)
        # Verify it contains Presentation Forms-B
        has_forms_b = any(0xFE70 <= ord(c) <= 0xFEFF for c in shaped)
        self.assertTrue(has_forms_b)

    def test_multi_line_narrative_has_spacers(self):
        entry = {
            "key": "campaign_map_playable_areas_description_att_faction_eastern_roman_empire",
            "en": "Line one\nLine two",
            "ar": "السطر الأول من الوصف التاريخي\nالسطر الثاني من الوصف التاريخي",
            "is_narrative": True
        }
        shaped = shape_part1_entry(entry)
        # Should contain PUA blank spacer (0xE010..0xE015)
        has_spacer = any(0xE010 <= ord(c) <= 0xE015 for c in shaped)
        self.assertTrue(has_spacer)


if __name__ == "__main__":
    unittest.main()
