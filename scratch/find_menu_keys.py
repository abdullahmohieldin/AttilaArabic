import sys, os
sys.path.insert(0, ".")
from source.loc import decode as loc_decode
from tools.packfile import PackFile

pack = PackFile('extracted/local_en.copy.pack')
menu_targets = [
    'CAMPAIGNS', 'LOAD CAMPAIGN', 'PROLOGUE', 'GRAND CAMPAIGN',
    'THE LAST ROMAN', 'AGE OF CHARLEMAGNE', 'MULTIPLAYER CAMPAIGN',
    'BATTLES', 'HISTORICAL BATTLE', 'CUSTOM BATTLE', 'MULTIPLAYER BATTLE',
    'QUICK BATTLE', 'LEADERBOARDS', 'REPLAYS', 'CONTINUE CAMPAIGN'
]

matches = {}
for fname in pack.files:
    if fname.endswith('.loc'):
        raw = pack.get_file(fname)
        entries, _, _ = loc_decode(raw)
        for item in entries:
            key, text = item[0], item[1]
            clean = text.strip()
            for t in menu_targets:
                if clean.upper() == t:
                    matches.setdefault(t, []).append((fname, key, text))

for t in menu_targets:
    print(f'=== {t} ===')
    for m in matches.get(t, [])[:3]:
        print(f'  [{m[0]}] {m[1]} -> "{m[2]}"')
