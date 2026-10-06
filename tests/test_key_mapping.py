#!/usr/bin/env python3
"""test_key_mapping.py — ensures every screen uses distinct keys and meanings match.

Rules:
  1. No two SCREEN GROUPS share an identical key.
  2. Every key in the WANT table is actually present in the right vanilla .loc file.
  3. The Arabic meaning matches the English vanilla text for that key.
"""
import os
import sys
import unittest

sys.path.insert(0, r"D:\AttilaArabic\source")
import loc

BASE        = r"D:\AttilaArabic"
LOC_BUILD   = os.path.join(BASE, "build", "v6")

# Screen groups with (full_key, english_vanilla) per key
BATTLES = [
    ("uied_component_texts_localised_string_string_NewState_Text_3a000c",      "Historical Battle"),
    ("uied_component_texts_localised_string_button_txt_NewState_Text_36000f",  "Custom Battle"),
    ("uied_component_texts_localised_string_string_NewState_Text_250075",       "Multiplayer Battle"),
    ("uied_component_texts_localised_string_heading_tx_NewState_Text_460009j", "Quick Battle"),
    ("uied_component_texts_localised_string_string_NewState_Text_1d002f",      "Leaderboards"),
    ("uied_component_texts_localised_string_button_txt_NewState_Text_700030",  "Replays"),
]

CAMPAIGNS = [
    ("uied_component_texts_localised_string_button_txt_NewState_Text_23001bb", "Load Campaign"),
    ("uied_component_texts_localised_string_button_txt_NewState_Text_530011r", "Grand Campaign"),
    ("uied_component_texts_localised_string_string_active_Text_c0020",         "The Last Roman"),
    ("uied_component_texts_localised_string_string_active_Text_3b",            "Age of Charlemagne"),  # trailing space in vanilla
    ("uied_component_texts_localised_string_button_txt_NewState_Text_430007",  "Multiplayer Campaign"),
    ("uied_component_texts_localised_string_string_continue_campaign_Text_380007", "Continue Campaign"),
]

FACTION_SELECT = [
    ("uied_component_texts_localised_string_button_txt_NewState_Text_530011",  "New Campaign"),     # K33 header
    ("uied_component_texts_localised_string_button_txt_NewState_Text_30006e",  "Start Campaign"),   # K20 start btn
    ("uied_component_texts_localised_string_header_cultural_NewState_Text_5e0000", "Cultural Trait"),  # K24
    ("uied_component_texts_localised_string_header_faction_NewState_Text_410063",  "Faction Trait"),   # K25
    ("uied_component_texts_localised_string_tx_difficulty_NewState_Text_79004a",   "Difficulty"),       # K38
    ("uied_component_texts_localised_string_year_tx_NewState_Text_310064",     "Start year:"),     # K49
    ("uied_component_texts_localised_string_tx_initial_challenge:_NewState_Text_670040", "Initial challenge:"),  # K50
]

TABS = [
    ("faction_groups_name_localised_att_fact_group_roman",       None),
    ("faction_groups_name_localised_att_fact_group_eastern",     None),
    ("faction_groups_name_localised_att_fact_group_nomadic",     None),
    ("faction_groups_name_localised_att_fact_group_barbarian",   None),
    ("faction_groups_name_localised_att_fact_group_barbarian_m", None),
    ("faction_groups_name_localised_att_fact_group_sand",        None),
]


class TestKeyMapping(unittest.TestCase):

    def setUp(self):
        # Load vanilla uied loc
        uied_path = os.path.join(LOC_BUILD, "vanilla_uied_component_texts.loc")
        rows_u, _, _ = loc.decode(open(uied_path, "rb").read())
        self.vanilla_uied = {k: v for k, v, _ in rows_u}

        fg_path = os.path.join(LOC_BUILD, "vanilla_faction_groups.loc")
        rows_fg, _, _ = loc.decode(open(fg_path, "rb").read())
        self.vanilla_fg = {k: v for k, v, _ in rows_fg}

        # Load built v6 uied loc
        built_path = os.path.join(LOC_BUILD, "uied_component_texts.loc")
        rows_b, _, _ = loc.decode(open(built_path, "rb").read())
        self.built_uied = {k: v for k, v, _ in rows_b}

    def test_no_key_shared_across_screens(self):
        """Each key should appear in at most one screen group."""
        all_screens = {
            "BATTLES": [k for k, _ in BATTLES],
            "CAMPAIGNS": [k for k, _ in CAMPAIGNS],
            "FACTION_SELECT": [k for k, _ in FACTION_SELECT],
        }
        seen = {}
        for screen, keys in all_screens.items():
            for k in keys:
                if k in seen:
                    self.fail(f"Key {k!r} appears in both {seen[k]} and {screen}")
                seen[k] = screen

    def test_all_keys_exist_in_vanilla(self):
        """Every key must exist in the vanilla .loc file."""
        for k, _ in BATTLES + CAMPAIGNS + FACTION_SELECT:
            self.assertIn(k, self.vanilla_uied, f"Key missing from vanilla uied: {k}")
        for k, _ in TABS:
            self.assertIn(k, self.vanilla_fg, f"Key missing from vanilla faction_groups: {k}")

    def test_key_assigned_to_correct_screen_vanilla_text(self):
        """Vanilla English text for each key must match expected screen label (VERIFIED labels)."""
        for k, expected_en in BATTLES + CAMPAIGNS + FACTION_SELECT:
            if expected_en is None:
                continue
            actual_en = self.vanilla_uied.get(k, "").strip()
            self.assertEqual(
                actual_en, expected_en.strip(),
                f"Key {k!r}: expected English {expected_en!r} but vanilla has {actual_en!r}"
            )

    def test_arabic_keys_changed_in_built_loc(self):
        """Every key we intend to translate must differ from vanilla in the built loc."""
        for k, _ in BATTLES + CAMPAIGNS + FACTION_SELECT:
            vanilla_val = self.vanilla_uied.get(k, "")
            built_val   = self.built_uied.get(k, "")
            self.assertNotEqual(
                vanilla_val, built_val,
                f"Key {k!r} was NOT changed in the built loc (still vanilla: {vanilla_val!r})"
            )


if __name__ == "__main__":
    unittest.main()
