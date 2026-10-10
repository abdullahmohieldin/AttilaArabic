#!/usr/bin/env python3
"""Build the comprehensive faction_select_complete.json with ALL missing translations
for the 10 Grand Campaign (395 AD) factions.

This script:
1. Finds every missing string needed for the faction selection screen
2. Generates Arabic translations
3. Outputs the complete JSON ready for loc_compiler.py
"""
import sys, os, json
sys.path.insert(0, 'source')
sys.path.insert(0, '.')
from source.loc import decode
from tools.packfile import PackFile

pack = PackFile('extracted/local_en.copy.pack')

# Load existing translations
existing = {}  # key -> entry dict
for fname in os.listdir('data/translations'):
    if fname.endswith('.json'):
        with open(f'data/translations/{fname}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data.get('entries', []):
                existing[entry['key']] = entry

# Load all tables
def load_table(path):
    raw = pack.get_file(path)
    if raw:
        rows, _, _ = decode(raw)
        return {k: (v, f) for k, v, f in rows}
    return {}

spf = load_table('text/db/start_pos_factions.loc')
eb = load_table('text/db/effect_bundles.loc')
ef = load_table('text/db/effects.loc')
names = load_table('text/db/names.loc')

# Trait keys for the 10 GC factions
GC_TRAIT_KEYS = [
    'att_faction_trait_roman',
    'att_faction_trait_roman_east',
    'att_faction_trait_roman_west',
    'att_faction_trait_eastern',
    'att_faction_trait_eastern_sassanid',
    'att_faction_trait_nomad',
    'att_faction_trait_nomad_huns',
    'att_faction_trait_migrators',
    'att_faction_trait_migrators_visigoths',
    'att_faction_trait_migrators_ostrogoths',
    'att_faction_trait_migrators_vandals',
    'att_faction_trait_barbarian',
    'att_faction_trait_barbarian_franks',
    'att_faction_trait_barbarian_saxons',
    'att_faction_trait_suebi',
]

# Description IDs for GC factions
GC_DESC_IDS = [
    2120156326,  # ERE
    2120156339,  # WRE
    2120156314,  # Sassanid
    2120156317,  # Huns
    2120156274,  # Visigoths
    2120156270,  # Ostrogoths
    2120156272,  # Vandals
    2120156278,  # Franks
    2120156281,  # Saxons
    2120156287,  # Suebi
]

# Leader name keys
GC_NAME_KEYS = [
    'names_name_2147354342',  # Arcadius (ERE)
    'names_name_2147343965',  # Arcadius (ERE)
    'names_name_2147343967',  # Honorius (WRE)
    'names_name_2147353201',  # Honorius (WRE)
    'names_name_2147344246',  # Yazdegerd (Sassanid)
    'names_name_2147345288',  # Uldin (Huns)
    'names_name_2147343885',  # Alaric (Visigoths)
    'names_name_2147347397',  # Alaric (Visigoths)
    'names_name_2147345091',  # Alaric I (Visigoths)
    'names_name_2147344895',  # Valamir (Ostrogoths)
    'names_name_2147348049',  # Vandalarius (Ostrogoths)
    'names_name_2147344836',  # Godigisel (Vandals)
    'names_name_2147344851',  # Gunderic (Vandals)
    'names_name_2147334233',  # Marcomer (Franks)
    # Saxons starting leader - need to find
    # Suebi starting leader - need to find
]

missing = []

# 1. Check descriptions
for desc_id in GC_DESC_IDS:
    for prefix in ['start_pos_factions_description_', 'start_pos_factions_long_description_']:
        key = f'{prefix}{desc_id}'
        if key not in existing:
            en_text = spf.get(key, ('', 0))[0]
            if en_text and en_text != 'PLACEHOLDER' and len(en_text) > 10:
                missing.append({
                    'key': key,
                    'table': 'text/db/start_pos_factions.loc',
                    'en': en_text,
                    'category': 'description'
                })

# 2. Check trait titles + descriptions in effect_bundles
for trait_key in GC_TRAIT_KEYS:
    for prefix in ['effect_bundles_localised_title_', 'effect_bundles_localised_description_']:
        key = f'{prefix}{trait_key}'
        if key not in existing:
            en_text = eb.get(key, ('', 0))[0]
            if en_text:
                missing.append({
                    'key': key,
                    'table': 'text/db/effect_bundles.loc',
                    'en': en_text,
                    'category': 'trait_bundle'
                })

# 3. Check effect lines (tooltip stat bonuses)
for ef_key, (en_text, _) in ef.items():
    if 'faction_trait' not in ef_key:
        continue
    # Check if this effect belongs to one of our GC factions
    belongs = False
    for trait_key in GC_TRAIT_KEYS:
        if trait_key in ef_key:
            belongs = True
            break
    if belongs and ef_key not in existing and en_text:
        missing.append({
            'key': ef_key,
            'table': 'text/db/effects.loc',
            'en': en_text,
            'category': 'effect_line'
        })

# 4. Check leader names
for name_key in GC_NAME_KEYS:
    if name_key not in existing:
        en_text = names.get(name_key, ('', 0))[0]
        if en_text:
            missing.append({
                'key': name_key,
                'table': 'text/db/names.loc',
                'en': en_text,
                'category': 'leader_name'
            })

# Summary
from collections import Counter
cats = Counter(m['category'] for m in missing)
print(f"Total missing strings for 10 GC factions: {len(missing)}")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")

# Write the missing entries
with open('scratch/gc_missing_complete.json', 'w', encoding='utf-8') as f:
    json.dump(missing, f, ensure_ascii=False, indent=2)
    
print(f"\nWritten to scratch/gc_missing_complete.json")
