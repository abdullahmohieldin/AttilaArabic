#!/usr/bin/env python3
"""List every loc value in the v14 pack that contains U+000A.

  python source/cr_nl_scan.py [--tsv logs/cr_c4_nl.tsv]
"""
import json
import os
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from packfile import PackFile  # noqa: E402
from loc import decode         # noqa: E402
from cr_build import LOC_FILES  # noqa: E402

V14 = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")


def scan():
    pf = PackFile(V14)
    out = []
    for internal in LOC_FILES:
        rows, pos, total = decode(pf.get_file(internal))
        assert pos == total, internal
        for key, text, tip in rows:
            if "\n" in text:
                out.append({"file": internal, "key": key, "text": text,
                            "tip": tip, "lines": text.split("\n")})
    return out


def main():
    data = scan()
    print(f"{len(data)} loc values contain U+000A")
    for e in data:
        tg = "".join("." if not (0x0600 <= ord(c) <= 0x06FF
                                 or 0xFE70 <= ord(c) <= 0xFEFF) else "#"
                     for c in e["text"])
        tat = sum(1 for c in e["text"] if ord(c) == 0x0640)
        print(f"  {e['file'].split(chr(92))[-1]:34s} {e['key'][:58]:58s} "
              f"lines={len(e['lines']):2d} len={len(e['text']):4d} tatweel={tat}")
        print(f"      {tg}")
    if "--tsv" in sys.argv:
        p = sys.argv[sys.argv.index("--tsv") + 1]
        with open(p, "w", encoding="utf-8") as f:
            for e in data:
                for i, ln in enumerate(e["lines"]):
                    f.write(f"{e['file']}\t{e['key']}\t{i}\t"
                            f"{' '.join(f'{ord(c):04X}' for c in ln)}\n")
        print(f"wrote {p}")
    with open(os.path.join(BASE, "logs", "cr_c4_nl.json"), "w",
              encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote logs/cr_c4_nl.json")


if __name__ == "__main__":
    main()
