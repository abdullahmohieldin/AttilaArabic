#!/usr/bin/env python3
"""Audit faction selection screen translation coverage."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'source'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from source.loc import decode
from tools.packfile import PackFile

BASE = r"D:\AttilaArabic"
pack = PackFile(os.path.join(BASE, 'extracted', 'local_en.copy.pack'))

# Load all translation keys
trans_keys = set()
for fname in os.listdir(os.path.join(BASE, 'data', 'translations')):
    if fname.endswith('.json'):
        with open(os.path.join(BASE, 'data', 'translations', fname), 'r', encoding='utf-8') as f:
            data = json.load(f)
            for entry in data.get('entries', []):
                trans_keys.add(entry['key'])

# 1. Faction descriptions (start_pos_factions.loc)
spf = pack.get_file('text/db/start_pos_factions.loc')
rows, _, _ = decode(spf)
real_descs = [(k,v) for k,v,f in rows if '_description_' in k and v != 'PLACEHOLDER' and len(v) > 20]
covered_descs = [k for k,v in real_descs if k in trans_keys]

# 2. Effect bundles (faction traits)
eb = pack.get_file('text/db/effect_bundles.loc')
eb_rows, _, _ = decode(eb)
trait_titles = [(k,v) for k,v,f in eb_rows if 'faction_trait' in k and '_title_' in k]
trait_descs = [(k,v) for k,v,f in eb_rows if 'faction_trait' in k and '_description_' in k]
covered_titles = [k for k,v in trait_titles if k in trans_keys]
covered_tdescs = [k for k,v in trait_descs if k in trans_keys]

# 3. Effects (trait tooltip effects)
ef = pack.get_file('text/db/effects.loc')
ef_rows, _, _ = decode(ef)
trait_effects = [(k,v) for k,v,f in ef_rows if 'faction_trait' in k]
covered_effects = [k for k,v in trait_effects if k in trans_keys]

# 4. Write report
report = os.path.join(BASE, 'scratch', 'coverage_report.txt')
with open(report, 'w', encoding='utf-8') as f:
    f.write("=== FACTION SELECTION SCREEN TRANSLATION COVERAGE ===\n\n")
    
    f.write(f"Faction descriptions: {len(covered_descs)}/{len(real_descs)} translated\n")
    f.write(f"Trait titles (effect_bundles): {len(covered_titles)}/{len(trait_titles)} translated\n")
    f.write(f"Trait descriptions (effect_bundles): {len(covered_tdescs)}/{len(trait_descs)} translated\n")
    f.write(f"Trait effects (tooltip lines): {len(covered_effects)}/{len(trait_effects)} translated\n\n")
    
    f.write("--- MISSING FACTION DESCRIPTIONS ---\n")
    for k,v in real_descs:
        if k not in trans_keys:
            f.write(f"  {k}\n    EN: {v[:120]}\n\n")
    
    f.write("\n--- MISSING TRAIT TITLES (effect_bundles) ---\n")
    for k,v in trait_titles:
        if k not in trans_keys:
            f.write(f"  {k} => {v}\n")
    
    f.write("\n--- MISSING TRAIT DESCRIPTIONS (effect_bundles) ---\n")
    for k,v in trait_descs:
        if k not in trans_keys:
            f.write(f"  {k}\n    EN: {v[:120]}\n")
    
    f.write("\n--- MISSING TRAIT EFFECTS (tooltip lines) ---\n")
    for k,v in trait_effects:
        if k not in trans_keys:
            f.write(f"  {k}\n    EN: {v[:120]}\n")

print(f"Report written to {report}")
print(f"\nSUMMARY:")
print(f"  Faction descriptions: {len(covered_descs)}/{len(real_descs)}")
print(f"  Trait titles: {len(covered_titles)}/{len(trait_titles)}")
print(f"  Trait descriptions: {len(covered_tdescs)}/{len(trait_descs)}")
print(f"  Trait effect lines: {len(covered_effects)}/{len(trait_effects)}")
