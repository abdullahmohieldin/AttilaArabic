#!/usr/bin/env python3
"""Check what Arabic text already exists in english_catalog_core.json"""
import json

with open('data/translations/english_catalog_core.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

filled = [e for e in catalog['entries'] if e.get('ar', '').strip()]
total = catalog.get('total', len(catalog['entries']))
print(f"Entries with Arabic in catalog: {len(filled)} / {total}")

# Check faction-related ones
keywords = ['faction', 'start_pos', 'effect_bundle', 'effects_desc', 'names_name', 'religion']
faction_related = [e for e in filled if any(x in e['key'] for x in keywords)]
print(f"Faction-related with Arabic: {len(faction_related)}")
for e in faction_related:
    ar_preview = e['ar'][:80].replace('\n', '\\n')
    print(f"  {e['key']}")
    print(f"    ar: {ar_preview}")
