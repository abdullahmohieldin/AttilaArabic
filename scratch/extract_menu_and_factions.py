import sys, os
sys.path.insert(0, ".")
from source.loc import decode as loc_decode
from tools.packfile import PackFile

pack = PackFile("extracted/local_en.copy.pack")

# 1. Main menu keys in uied_component_texts.loc
raw_ui = pack.get_file("text/db/uied_component_texts.loc")
ui_entries, _, _ = loc_decode(raw_ui)

print("--- Searching UI Menu Entries ---")
menu_words = [
    "Campaigns", "Load Campaign", "Prologue", "Grand Campaign",
    "The Last Roman", "Age of Charlemagne", "Multiplayer Campaign",
    "Continue Campaign", "Battles", "Historical Battle", "Custom Battle",
    "Multiplayer Battle", "Quick Battle", "Leaderboards", "Replays",
    "Options", "Exit", "Quit", "Credits", "Encyclopedia"
]

found_ui = {}
for item in ui_entries:
    k, text = item[0], item[1]
    clean = text.strip()
    for w in menu_words:
        if clean.lower() == w.lower():
            found_ui.setdefault(w, []).append((k, text))

for w, lst in found_ui.items():
    print(f"\n[{w}]: {len(lst)} keys")
    for k, text in lst[:4]:
        print(f"  {k} -> {repr(text)}")

# 2. Playable Factions in factions.loc
raw_factions = pack.get_file("text/db/factions.loc")
fact_entries, _, _ = loc_decode(raw_factions)

print("\n--- Searching Playable Faction Names in factions.loc ---")
grand_campaign_factions = [
    ("att_fact_eastern_roman_empire", "Eastern Roman Empire"),
    ("att_fact_western_roman_empire", "Western Roman Empire"),
    ("att_fact_sassanid_empire", "Sasanian Empire"),
    ("att_fact_huns", "Huns"),
    ("att_fact_alani", "Alans"),
    ("att_fact_vandals", "Vandals"),
    ("att_fact_visigoths", "Visigoths"),
    ("att_fact_ostrogoths", "Ostrogoths"),
    ("att_fact_franks", "Franks"),
    ("att_fact_saxons", "Saxons"),
    ("att_fact_danes", "Danes"),
    ("att_fact_geats", "Geats"),
    ("att_fact_jutes", "Jutes"),
    ("att_fact_suebi", "Suebi"),
    ("att_fact_burgundians", "Burgundians"),
    ("att_fact_alamans", "Alamans"),
    ("att_fact_langobards", "Langobards"),
    ("att_fact_white_huns", "White Huns"),
    ("att_fact_aksum", "Aksum"),
    ("att_fact_himyar", "Himyar"),
    ("att_fact_tanukhids", "Tanukhids"),
    ("att_fact_lakhmids", "Lakhmids"),
    ("att_fact_garamantians", "Garamantians"),
    ("att_fact_picti", "Picts"),
    ("att_fact_eblani", "Ebdani"),
    ("att_fact_caledonii", "Caledonians"),
]

found_factions = {}
for item in fact_entries:
    k, text = item[0], item[1]
    for fact_id, name in grand_campaign_factions:
        if fact_id in k and "screen_name" in k:
            found_factions[fact_id] = (k, text)

for fact_id, name in grand_campaign_factions:
    if fact_id in found_factions:
        k, text = found_factions[fact_id]
        print(f"  {fact_id:32s}: {k} -> {repr(text)}")
    else:
        print(f"  {fact_id:32s}: NOT FOUND directly, search needed")
