import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from tools.packfile import PackFile
from source.loc import decode

pf = PackFile(r"extracted\local_en.copy.pack")
loc_files = [p for p in pf.files if p.endswith('.loc')]
print(f"Total loc files in pack: {len(loc_files)}")

search_strings = [
    "Start Campaign",
    "Difficulty",
    "Factions",
    "Hard",
    "For players familiar with Total War.",
    "Difficulty Slider",
    "Grand Campaign",
    "Load Campaign",
    "Cultural Trait",
    "Initial challenge",
]

results = {s: [] for s in search_strings}

for p in sorted(loc_files):
    raw = pf.get_file(p)
    try:
        rows, ver, cnt = decode(raw)
    except Exception:
        continue
    for key, text, flag in rows:
        for s in search_strings:
            t_strip = text.strip()
            if t_strip == s:
                results[s].append((p, key, text, flag, "EXACT"))
            elif t_strip.lower() == s.lower():
                results[s].append((p, key, text, flag, "CASE_DIFF"))
            elif s in text:
                results[s].append((p, key, text, flag, "SUBSTRING"))

for s in search_strings:
    print(f"\n==================================================")
    print(f"TARGET: \"{s}\" (Total matches: {len(results[s])})")
    print(f"==================================================")
    exacts = [m for m in results[s] if m[4] == "EXACT"]
    case_diffs = [m for m in results[s] if m[4] == "CASE_DIFF"]
    substrings = [m for m in results[s] if m[4] == "SUBSTRING"]
    
    print(f"--- EXACT MATCHES ({len(exacts)}) ---")
    for p, k, txt, flg, _ in exacts:
        print(f"  File: {p}\n    Key: {k}\n    Text: {repr(txt)} (flag={flg})")
    
    if case_diffs:
        print(f"--- CASE-INSENSITIVE MATCHES ({len(case_diffs)}) ---")
        for p, k, txt, flg, _ in case_diffs:
            print(f"  File: {p}\n    Key: {k}\n    Text: {repr(txt)} (flag={flg})")

    if not exacts and not case_diffs and substrings:
        print(f"--- SUBSTRING MATCHES ({len(substrings)}) ---")
        for p, k, txt, flg, _ in substrings[:10]:
            print(f"  File: {p}\n    Key: {k}\n    Text: {repr(txt[:80])} (flag={flg})")
