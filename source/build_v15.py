#!/usr/bin/env python3
"""Build v15: pitch-control probe (aw matrix + drawn-column window).

Base: v14 packs. Questions answered by ONE launch:
  Q1 does alloc_width control pitch?  in-place aw edits on REAL codepoints,
      geo12 and gio12 with DIFFERENT values (font-independence cross-check).
  Q2 which bitmap columns does the engine draw?  half-block probes:
      FEF4 = solid cols 0-3 only (w8); FE8D = solid cols 4-9 only (w10, w>P).
  Q3 controls: FE9C/FE8E untouched aw, space-pad indent line.
Predictions (offline, stated in docs/test-pack-manifest-v15.md):
  H_aw   (P = aw + c, c~+3): ERE pitches L1~5 L2~15 L3 8 L4 8 L5 ~6 L6 6;
         Hard L1~15 L2~5 L3 8; WRE: phrase on L2 starts ~+70px vs L1.
  H_noaw (P engine-internal per cp): ERE pitches 8 8 8 8 ? 6; Hard 8 8 8;
         WRE: both phrases flush (same indent).
  Window: L4 ticks ink=3 (cols 1-3 drawn) proves +1 offset;
         L5 ink=6 => no clip at P (w>P drawn fully, pitch may follow w),
         L5 ink=4 => clip at P-1 (1px inter-cell column never drawable).
"""
import hashlib
import os
import shutil
import subprocess
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))

from cuf import CUF
from loc import decode, encode
from packfile import PackFile

V14_FONTS = os.path.join(BASE, "release", "Attila_Arabic_POC_v14_fonts.pack")
V14_PACK = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")
FONTS_OUT = os.path.join(BASE, "release", "Attila_Arabic_POC_v15_fonts.pack")
LOC_OUT = os.path.join(BASE, "release", "Attila_Arabic_POC_v15.pack")
VANILLA = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"

GEO = "font\\georgia_italic_12.cuf"
GIO = "font\\la_gioconda_12.cuf"

KEY_ERE = "start_pos_factions_description_2120156326"
KEY_WRE = "start_pos_factions_description_2120156339"
DIFF2 = "random_localisation_strings_string_campaign_difficulty_description_2"

FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
    r"text\db\land_units.loc",
    r"text\db\faction_groups.loc",
    r"text\db\random_localisation_strings.loc",
    r"text\db\ui_unit_stats.loc",
    r"text\db\ui_unit_bullet_point_enums.loc",
]

PHRASE = "FE94 FEF4 FE91 FEAE FED0 FEDF FE8D 0020 FE8E FEE3 FEED FEAD"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args):
    subprocess.run(args, check=True)


def half_block(h, c0, c1, w):
    bm = bytearray(w * h)
    for y in range(h):
        for x in range(c0, min(c1, w)):
            bm[y * w + x] = 255
    return bytes(bm)


def main():
    log = []
    assert sha256_file(VANILLA) == EXPECTED_VANILLA_SHA
    log.append("vanilla SHA256 before: OK")

    v14f = PackFile(V14_FONTS)
    new_files = {}
    for name in sorted(v14f.files):
        data = v14f.get_file(name)
        if name not in (GEO, GIO):
            new_files[name] = data
            continue
        c = CUF.decode(data)
        edits = []
        if name == GEO:
            aw_edits = {0xFE92: 2, 0xFE98: 12}
            for cp, aw in aw_edits.items():
                i = c.table[cp]
                ah, _, w, h = c.dims[i]
                c.dims[i] = (ah, aw, w, h)
                edits.append(f"U+{cp:04X} aw->{aw}")
            i = c.table[0xFEF4]
            ah, aw, w, h = c.dims[i]
            c.dims[i] = (ah, aw, 8, h)
            c.bitmaps[i] = half_block(h, 0, 4, 8)
            edits.append("FEF4 left-half block w8")
            i = c.table[0xFE8D]
            ah, aw, w, h = c.dims[i]
            c.dims[i] = (ah, aw, 10, h)
            c.bitmaps[i] = half_block(h, 4, 10, 10)
            edits.append("FE8D right-half block w10")
        else:
            for cp, aw in {0xFE92: 12, 0xFE98: 2}.items():
                i = c.table[cp]
                ah, _, w, h = c.dims[i]
                c.dims[i] = (ah, aw, w, h)
                edits.append(f"U+{cp:04X} aw->{aw}")
        out = c.encode()
        assert CUF.decode(out).encode() == out, name
        new_files[name] = out
        log.append(f"{name.split(chr(92))[-1]}: " + ", ".join(edits))

    tmpdir = os.path.join(BASE, "build", "v15_fonts")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)
    for name in sorted(new_files):
        with open(os.path.join(tmpdir, name.split("\\")[-1]), "wb") as f:
            f.write(new_files[name])
    PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
    PACK = os.path.join(BASE, "tools", "packfile.py")
    tmp = os.path.join(BASE, "build", "v15f_tmp.pack")
    if os.path.exists(tmp):
        os.remove(tmp)
    run(PY, PACK, "create", tmp, "--type", "3", "--version", "PFH4")
    for name in sorted(new_files):
        run(PY, PACK, "add", tmp, name, os.path.join(tmpdir, name.split("\\")[-1]))
    run(PY, PACK, "set-type", tmp, "3", "--output", FONTS_OUT)
    os.remove(tmp)
    log.append(f"v15_fonts SHA256: {sha256_file(FONTS_OUT)} ({os.path.getsize(FONTS_OUT)} B)")

    # ---- loc ----
    def ruler(cp, n=20):
        return "".join(chr(cp) for _ in range(n))

    ere = "\n".join([ruler(0xFE92), ruler(0xFE98), ruler(0xFE9C),
                     ruler(0xFEF4), ruler(0xFE8D), ruler(0xFE8E)])
    phrase = "".join(chr(int(t, 16)) for t in PHRASE.split())
    wre = "\n".join([ruler(0xFE9C, 10) + phrase, ruler(0xFE98, 10) + phrase])
    hard = "\n".join([ruler(0xFE92), ruler(0xFE98), ruler(0xFE9C)])

    v14 = PackFile(V14_PACK)
    tmpdir2 = os.path.join(BASE, "build", "v15_loc")
    shutil.rmtree(tmpdir2, ignore_errors=True)
    os.makedirs(tmpdir2)
    for internal in FILES:
        raw = v14.get_file(internal)
        leaf = internal.split("\\")[-1]
        if internal == r"text\db\start_pos_factions.loc":
            rows, p, t = decode(raw)
            assert p == t
            vals = {KEY_ERE: ere, KEY_WRE: wre}
            open(os.path.join(tmpdir2, leaf), "wb").write(encode(
                [(k, vals.get(k, x), tip) for k, x, tip in rows]))
        elif internal == r"text\db\random_localisation_strings.loc":
            rows, p, t = decode(raw)
            assert p == t
            open(os.path.join(tmpdir2, leaf), "wb").write(encode(
                [(k, hard if k == DIFF2 else x, tip) for k, x, tip in rows]))
        else:
            open(os.path.join(tmpdir2, leaf + ".raw"), "wb").write(raw)
    tmp2 = os.path.join(BASE, "build", "v15l_tmp.pack")
    if os.path.exists(tmp2):
        os.remove(tmp2)
    run(PY, PACK, "create", tmp2, "--type", "3", "--version", "PFH4")
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        src = os.path.join(tmpdir2, leaf + ".raw")
        if not os.path.exists(src):
            src = os.path.join(tmpdir2, leaf)
        run(PY, PACK, "add", tmp2, internal, src)
    run(PY, PACK, "set-type", tmp2, "3", "--output", LOC_OUT)
    os.remove(tmp2)

    v15 = PackFile(LOC_OUT)
    r, p, t = decode(v15.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: x for k, x, _ in r}
    assert d[KEY_ERE] == ere and d[KEY_WRE] == wre
    r2, p, t = decode(v15.get_file(r"text\db\random_localisation_strings.loc"))
    d2 = {k: x for k, x, _ in r2}
    assert d2[DIFF2] == hard
    log.append(f"v15 loc SHA256: {sha256_file(LOC_OUT)} ({os.path.getsize(LOC_OUT)} B)")
    assert sha256_file(VANILLA) == EXPECTED_VANILLA_SHA
    log.append("vanilla SHA256 after: OK")

    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    with open(os.path.join(BASE, "logs", "v15_build.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
