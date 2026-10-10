import os, glob, sys
sys.path.insert(0, '.')
from source.loc import decode

# Check extracted loc files
extracted_locs = glob.glob('extracted/loc/*.loc')
print(f"Extracted loc files count: {len(extracted_locs)}")

# Search for candidate keys
candidates = [
    "factions_screen_name_att_fact_eastern_roman_empire",
    "start_pos_factions_description_2120156326",
    "uied_component_texts_localised_string_medal1_default_Tooltip_5003a",
    "uied_component_texts_localised_string_button_txt_NewState_Text_530011h",
]

found = {}
all_uied = {}

for p in extracted_locs:
    base = os.path.basename(p)
    data = open(p, 'rb').read()
    rows, _, _ = decode(data)
    d = {r[0]: (r[1], r[2]) for r in rows}
    if "uied" in base:
        all_uied.update(d)
    for c in candidates:
        if c in d:
            found[c] = (base, d[c][0])

for c in candidates:
    if c in found:
        print(f"FOUND: {c} in {found[c][0]}: {repr(found[c][1][:40])}")
    else:
        print(f"NOT FOUND: {c}")

# Let's search all_uied for main menu campaign button and battle settings button
print("\n--- Searching uied for Campaign and Battle buttons ---")
for k, (v, flag) in all_uied.items():
    if v in ["Campaign", "Grand Campaign", "Main Campaign", "Custom Battle", "Battle Settings", "Battle Setup"]:
        print(f"Key: {k} | Value: {repr(v)}")
    elif "campaign" in v.lower() and len(v) < 20 and "button" in k.lower():
        print(f"Button key: {k} | Value: {repr(v)}")
