import os
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF
from packfile import PackFile

cps = [0xFE92, 0xFE98, 0xFE9C, 0xFEF4, 0xFE8D, 0xFE8E, 0xFEF2, 0x20, 0x640]
targets = [
    ("release/Attila_Arabic_POC_v8_fonts.pack", "font\\georgia_italic_12.cuf"),
    ("release/Attila_Arabic_POC_v10_fonts.pack", "font\\georgia_italic_12.cuf"),
    ("release/Attila_Arabic_POC_v11_fonts.pack", "font\\georgia_italic_12.cuf"),
    ("release/Attila_Arabic_POC_v13_fonts.pack", "font\\georgia_italic_12.cuf"),
    ("release/Attila_Arabic_POC_v14_fonts.pack", "font\\georgia_italic_12.cuf"),
    ("release/Attila_Arabic_POC_v14_fonts.pack", "font\\la_gioconda_12.cuf"),
    ("extracted/fonts/arialunicode_12.cuf", None),
    ("extracted/fonts/georgia_italic_12.cuf", None),
]
for pack, fn in targets:
    path = pack if os.path.isabs(pack) else os.path.join(BASE, pack)
    if not os.path.exists(path):
        print("MISSING", pack)
        continue
    if fn is None:
        c = CUF.decode(open(path, "rb").read())
        tag = pack.split("/")[-1]
    else:
        c = CUF.decode(PackFile(path).get_file(fn))
        tag = pack.split("_")[-2] + " " + fn.split("\\")[-1]
    row = []
    for cp in cps:
        i = c.table[cp]
        if i >= len(c.dims):
            row.append(f"{cp:04X}:--")
            continue
        ah, aw, w, h = c.dims[i]
        row.append(f"{cp:04X}:aw{aw}/w{w}/h{h}")
    print(f"{tag:28s}", " ".join(row))
