#!/usr/bin/env python3
"""Build v12 fonts pack: LOUD bitmap probe.

Takes v11_fonts and, in EVERY one of the 31 CUFs, replaces the bitmaps of
FEF2 (final yeh), FE92 (medial beh) and FE8D (alef) with SOLID blocks
(all pixels 255).  Dims/records unchanged -> advances and pitch stay the
same, so the only thing that can change on screen is the glyph ink.

Purpose: if the engine draws Arabic presentation forms from ANY of our merged
CUFs, the three ruler lines (20 x FEF2 / 20 x FE92 / 20 x FE8D, already in
v11.loc) render as unbroken solid bars.  If the lines still show the normal
hooks/teeth, the engine sources Arabic bitmaps from outside our packs
entirely (internal/system font) and the CUF-merge approach cannot touch them.

v11.pack is reused unchanged (same ruler lines).
"""
import hashlib
import os
import shutil
import subprocess
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))

from cuf import CUF        # noqa: E402
from packfile import PackFile  # noqa: E402

V11_FONTS = os.path.join(BASE, "release", "Attila_Arabic_POC_v11_fonts.pack")
FONTS_OUT = os.path.join(BASE, "release", "Attila_Arabic_POC_v12_fonts.pack")
VANILLA   = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"

PROBES = (0xFEF2, 0xFE92, 0xFE8D)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args):
    subprocess.run(args, check=True)


def main():
    sha = sha256_file(VANILLA)
    assert sha == EXPECTED_VANILLA_SHA, sha
    print("vanilla SHA256 OK")

    v11f = PackFile(V11_FONTS)
    tmpdir = os.path.join(BASE, "build", "v12_fonts")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)

    for name in sorted(v11f.files):
        data = v11f.get_file(name)
        c = CUF.decode(data)
        touched = []
        for cp in PROBES:
            i = c.table[cp]
            if i != 0xFFFF and i < c.count:
                ah, aw, w, h = c.dims[i]
                if w and h:
                    c.bitmaps[i] = b"\xff" * (w * h)
                    touched.append(f"U+{cp:04X}({w}x{h})")
        if touched:
            data = c.encode()
            chk = CUF.decode(data)
            for cp in PROBES:
                i = chk.table[cp]
                if i != 0xFFFF and i < c.count and chk.dims[i][2] and chk.dims[i][3]:
                    assert set(chk.bitmaps[i]) == {255}, f"{name} U+{cp:04X} not solid"
        print(f"  {name.split(chr(92))[-1]:34s} solid: {', '.join(touched) if touched else '-'}")
        with open(os.path.join(tmpdir, name.split("\\")[-1]), "wb") as f:
            f.write(data)

    tmp_pack = os.path.join(BASE, "build", "v12f_tmp.pack")
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
    PACK = os.path.join(BASE, "tools", "packfile.py")
    run(PY, PACK, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in sorted(v11f.files):
        run(PY, PACK, "add", tmp_pack, name, os.path.join(tmpdir, name.split("\\")[-1]))
    run(PY, PACK, "set-type", tmp_pack, "3", "--output", FONTS_OUT)
    os.remove(tmp_pack)

    out = PackFile(FONTS_OUT)
    assert out.header.version == b"PFH4" and out.header.pack_type == 3
    print(f"v12_fonts SHA256: {sha256_file(FONTS_OUT)} ({os.path.getsize(FONTS_OUT)} B)")


if __name__ == "__main__":
    main()
