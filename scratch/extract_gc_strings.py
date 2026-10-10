#!/usr/bin/env python3
"""Extract ALL English strings needed for the 10 Grand Campaign (395 AD) factions.

Output: scratch/grand_campaign_strings.json with all keys, tables, and English text
that need Arabic translations for the faction selection screen.
"""
import sys, os, json
sys.path.insert(0, 'source')
sys.path.insert(0, '.')
from source.loc import decode
from tools.packfile import PackFile

pack = PackFile('extracted/local_en.copy.pack')

# The 10 vanilla Grand Campaign playable factions and their identifiers:
# Key mapping: faction internal name -> numeric IDs for start_pos
FACTIONS = {
    'Eastern Roman Empire': {
        'fact_key': 'att_fact_eastern_roman_empire',
        'desc_ids': [2120156326],
        'trait_keys': ['att_faction_trait_roman', 'att_faction_trait_roman_east'],
        'leader_name_keys': ['names_name_2147354342', 'names_name_2147343965'],  # Arcadius
        'religion_key': 'att_rel_chr_orthodox',
    },
    'Western Roman Empire': {
        'fact_key': 'att_fact_western_roman_empire',
        'desc_ids': [2120156339],
        'trait_keys': ['att_faction_trait_roman', 'att_faction_trait_roman_west'],
        'leader_name_keys': ['names_name_2147343967', 'names_name_2147353201'],  # Honorius
        'religion_key': 'att_rel_chr_catholic',
    },
    'Sassanid Empire': {
        'fact_key': 'att_fact_sassanid_empire',
        'desc_ids': [2120156314],
        'trait_keys': ['att_faction_trait_eastern', 'att_faction_trait_eastern_sassanid'],
        'leader_name_keys': ['names_name_2147344246'],  # Yazdegerd
        'religion_key': 'att_rel_east_zoroastrian',
    },
    'Huns': {
        'fact_key': 'att_fact_hunni',
        'desc_ids': [2120156317],
        'trait_keys': ['att_faction_trait_nomad', 'att_faction_trait_nomad_huns'],
        'leader_name_keys': ['names_name_2147345288'],  # Uldin
        'religion_key': 'att_rel_pag_tengri',
    },
    'Visigoths': {
        'fact_key': 'att_fact_visigothi',
        'desc_ids': [2120156274],
        'trait_keys': ['att_faction_trait_migrators', 'att_faction_trait_migrators_visigoths'],
        'leader_name_keys': ['names_name_2147343885', 'names_name_2147347397', 'names_name_2147345091'],  # Alaric
        'religion_key': 'att_rel_chr_arian',
    },
    'Ostrogoths': {
        'fact_key': 'att_fact_ostrogothi',
        'desc_ids': [2120156270],
        'trait_keys': ['att_faction_trait_migrators', 'att_faction_trait_migrators_ostrogoths'],
        'leader_name_keys': ['names_name_2147344895', 'names_name_2147348049'],  # Valamir, Vandalarius
        'religion_key': 'att_rel_chr_arian',
    },
    'Vandals': {
        'fact_key': 'att_fact_vandali',
        'desc_ids': [2120156272],
        'trait_keys': ['att_faction_trait_migrators', 'att_faction_trait_migrators_vandals'],
        'leader_name_keys': ['names_name_2147344836', 'names_name_2147344851'],  # Godigisel, Gunderic
        'religion_key': 'att_rel_chr_arian',
    },
    'Franks': {
        'fact_key': 'att_fact_franci',
        'desc_ids': [2120156278],
        'trait_keys': ['att_faction_trait_barbarian', 'att_faction_trait_barbarian_franks'],
        'leader_name_keys': ['names_name_2147334233'],  # Marcomer
        'religion_key': 'att_rel_pag_germanic',
    },
    'Saxons': {
        'fact_key': 'att_fact_saxones',
        'desc_ids': [2120156281],
        'trait_keys': ['att_faction_trait_barbarian', 'att_faction_trait_barbarian_saxons'],
        'leader_name_keys': [],  # Need to find
        'religion_key': 'att_rel_pag_germanic',
    },
    'Suebi': {
        'fact_key': 'att_fact_suebi',
        'desc_ids': [2120156287],
        'trait_keys': ['att_faction_trait_suebi'],
        'leader_name_keys': [],  # Need to find  
        'religion_key': 'att_rel_pag_germanic',
    },
}

# Load all tables
tables = {}
for tpath in ['text/db/start_pos_factions.loc', 'text/db/effect_bundles.loc', 
              'text/db/effects.loc', 'text/db/names.loc', 'text/db/factions.loc',
              'text/db/religions.loc']:
    raw = pack.get_file(tpath)
    if raw:
        rows, _, _ = decode(raw)
        tables[tpath] = {k: v for k,v,f in rows}

# Load existing translations
existing_keys = set()
for fname in os.listdir('data/translations'):
    if fname.endswith('.json'):
        with open(f'data/translations/{fname}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data.get('entries', []):
                existing_keys.add(entry['key'])

# Collect all needed strings
needed = []

for faction_name, info in FACTIONS.items():
    # 1. Faction descriptions
    for desc_id in info['desc_ids']:
        for prefix in ['start_pos_factions_description_', 'start_pos_factions_long_description_']:
            key = f'{prefix}{desc_id}'
            en = tables['text/db/start_pos_factions.loc'].get(key, '')
            if en and en != 'PLACEHOLDER':
                needed.append({
                    'faction': faction_name,
                    'category': 'description',
                    'key': key,
                    'table': 'text/db/start_pos_factions.loc',
                    'en': en,
                    'already_translated': key in existing_keys,
                })
    
    # 2. Trait titles and descriptions
    for trait_key in info['trait_keys']:
        for prefix in ['effect_bundles_localised_title_', 'effect_bundles_localised_description_']:
            key = f'{prefix}{trait_key}'
            en = tables['text/db/effect_bundles.loc'].get(key, '')
            if en:
                needed.append({
                    'faction': faction_name,
                    'category': 'trait_title' if '_title_' in prefix else 'trait_description',
                    'key': key,
                    'table': 'text/db/effect_bundles.loc',
                    'en': en,
                    'already_translated': key in existing_keys,
                })
    
    # 3. Effect lines for traits
    for trait_key in info['trait_keys']:
        for key, en in tables['text/db/effects.loc'].items():
            if trait_key in key and 'faction_trait' in key:
                needed.append({
                    'faction': faction_name,
                    'category': 'effect_line',
                    'key': key,
                    'table': 'text/db/effects.loc',
                    'en': en,
                    'already_translated': key in existing_keys,
                })
    
    # 4. Leader names
    for name_key in info['leader_name_keys']:
        en = tables['text/db/names.loc'].get(name_key, '')
        if en:
            needed.append({
                'faction': faction_name,
                'category': 'leader_name',
                'key': name_key,
                'table': 'text/db/names.loc',
                'en': en,
                'already_translated': key in existing_keys,
            })

# Summary
missing = [n for n in needed if not n['already_translated']]
print(f"Total strings needed: {len(needed)}")
print(f"Already translated: {len(needed) - len(missing)}")
print(f"Missing: {len(missing)}")
print()

# Group by category
from collections import Counter
cat_counts = Counter()
missing_cats = Counter()
for n in needed:
    cat_counts[n['category']] += 1
for n in missing:
    missing_cats[n['category']] += 1

print("By category:")
for cat in sorted(cat_counts):
    print(f"  {cat}: {cat_counts[cat] - missing_cats[cat]}/{cat_counts[cat]} translated")

# Write the missing strings
with open('scratch/grand_campaign_missing.json', 'w', encoding='utf-8') as f:
    json.dump({'missing_count': len(missing), 'entries': missing}, f, ensure_ascii=False, indent=2)

print(f"\nMissing strings written to scratch/grand_campaign_missing.json")
