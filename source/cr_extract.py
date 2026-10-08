#!/usr/bin/env python3
"""Clean-room step 0: extract every vanilla CUF from local_en.pack
(data.pack contains no font entries - verified 2026-10-08) into
build/vanilla_fonts/, read-only on the game dir. Then round-trip gate:
decode->encode each CUF and require byte-identical output."""
import hashlib
import os
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF
from packfile import PackFile

VANILLA = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
OUT = os.path.join(BASE, "build", "vanilla_fonts")


def main():
    pf = PackFile(VANILLA)
    names = sorted(n for n in pf.files if n.startswith("font") and n.endswith(".cuf"))
    os.makedirs(OUT, exist_ok=True)
    log = []
    bad = []
    for n in names:
        raw = pf.get_file(n)
        leaf = n.split("\\")[-1]
        with open(os.path.join(OUT, leaf), "wb") as f:
            f.write(raw)
        c = CUF.decode(raw)
        rt = c.encode()
        ok = rt == raw
        if not ok:
            bad.append(leaf)
        log.append(f"{leaf:34s} {len(raw):9d} B  magic={c.magic.decode()} "
                   f"glyphs={len(c.dims)} roundtrip={'IDENTICAL' if ok else 'DIFFERS'} "
                   f"tail={c.parse_tail()}")
    print("\n".join(log))
    print(f"\n{len(names)} CUFs, {len(bad)} round-trip failures: {bad if bad else 'none'}")
    with open(os.path.join(BASE, "logs", "cr_gate.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + f"\nfailures: {bad if bad else 'none'}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
