import sys, os, json
sys.path.insert(0, '.')
sys.path.insert(0, 'source')
from tools.packfile import PackFile
from source.loc import decode

pack = PackFile('extracted/local_en.copy.pack')
raw = pack.get_file('text/db/names.loc')
rows, _, _ = decode(raw)
name_map = {k: v for k, v, f in rows}

with open('data/translations/leaders_and_campaign.json', 'r', encoding='utf-8') as f:
    lc = json.load(f)

print('leaders_and_campaign entries count:', len(lc.get('entries', [])))
for e in lc['entries'][:25]:
    print(f"{e['key']}: en='{e.get('en')}' ar='{e.get('ar')}'")
