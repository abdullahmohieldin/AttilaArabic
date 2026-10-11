import unittest
import sys
import os

# Add tw_attila_ar to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.validate import validate_entry, validate_batch


class TestBatchValidator(unittest.TestCase):
    def test_valid_entry(self):
        entry = {
            "id": "factions_screen_name_att_faction_eastern_roman_empire",
            "en": "Eastern Roman Empire",
            "ar": "الإمبراطورية الرومانية الشرقية"
        }
        res, msg = validate_entry(entry)
        self.assertTrue(res, msg)

    def test_placeholder_mismatch(self):
        entry = {
            "id": "test_ph_mismatch",
            "en": "Turns remaining: %d (%s)",
            "ar": "الأدوار المتبقية: %d"  # missing %s
        }
        res, msg = validate_entry(entry)
        self.assertFalse(res)
        self.assertIn("Placeholder mismatch", msg)

    def test_stray_latin_letters(self):
        entry = {
            "id": "test_latin",
            "en": "Warrior of the North",
            "ar": "محارب من الـ North"  # stray English word
        }
        res, msg = validate_entry(entry)
        self.assertFalse(res)
        self.assertIn("Latin leftover", msg)

    def test_allowlist_latin_tags(self):
        entry = {
            "id": "test_tags",
            "en": "[[col:yellow]]Gold[[/col]]",
            "ar": "[[col:yellow]]ذهب[[/col]]"  # allowed tag
        }
        res, msg = validate_entry(entry)
        self.assertTrue(res, msg)

    def test_reject_presentation_forms_in_translation_layer(self):
        entry = {
            "id": "test_forms_b",
            "en": "Rome",
            "ar": "\uFE8E\uFE8D"  # Presentation Forms-B character
        }
        res, msg = validate_entry(entry)
        self.assertFalse(res)
        self.assertIn("Presentation Forms-B detected", msg)


if __name__ == "__main__":
    unittest.main()
