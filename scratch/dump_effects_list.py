import json

with open('scratch/all_faction_trait_effects.json', 'r', encoding='utf-8') as f:
    effects = json.load(f)

with open('scratch/effects_list.txt', 'w', encoding='utf-8') as out:
    for i, e in enumerate(effects):
        out.write(f"{i:3d}: {e['key']} -> {e['en']}\n")

print(f"Wrote {len(effects)} to scratch/effects_list.txt")
