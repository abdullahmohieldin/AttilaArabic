#!/usr/bin/env python3
"""Build v10 calibration probe (round 10).

v10_fonts.pack = v8_fonts with 11 PUA calibration glyphs ADDED to
georgia_italic_12 only.  No existing glyph is modified; the other 30 CUFs are
raw byte copies.

  E100-E105  beh clones (FE92 ink), (aw,w) = (6,6) (5,6) (6,4) (4,6) (8,6) (6,8)
  E110-E112  blank clones (no ink), (aw,w) = (4,4) (8,8) (8,0)
  E120       FEF2 refit into 18 rows (dots inside the box), ah=18
  E121       FEF2 shifted up 2 rows (same 20-row record, ink moved up)

v10.pack = v8.pack with exactly 2 values replaced (ERE + WRE descriptions);
lines stored verbatim (no reshaper/bidi) except the WRE phrase, which is
shaped first and then prefixed with E111 pads (same order as v8r).

Purpose: measure the engine's advance rule directly on screen.
  - v9 finding: advance per codepoint is font-independent (geo12 vs gio12
    identical spans) and matches NEITHER aw NOR w of the rendering CUF nor
    arialunicode records nor GDI fallbacks tested.  FE92->8, FE8D->5,
    FEF2->12, space->5, U+2003->6, U+E000->14, NBSP->~0.9 (all VERIFIED).
  - v6 vs v8 FE92 differ only in aw (6 vs 5); screen unchanged -> aw ignored.
  - The clone lines test whether aw or w drives pitch for NEW codepoints;
    the blank lines measure blank advance; the FEF2 variants test the
    over-box clipping hypothesis for the missing final-yeh dots.
"""
import hashlib
import os
import shutil
import struct
import subprocess
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))

from cuf import CUF       # noqa: E402
from loc import decode, encode  # noqa: E402
from packfile import PackFile  # noqa: E402
from shape import shape   # noqa: E402

V8_FONTS  = os.path.join(BASE, "release", "Attila_Arabic_POC_v8_fonts.pack")
V8_PACK   = os.path.join(BASE, "release", "Attila_Arabic_POC_v8.pack")
FONTS_OUT = os.path.join(BASE, "release", "Attila_Arabic_POC_v10_fonts.pack")
LOC_OUT   = os.path.join(BASE, "release", "Attila_Arabic_POC_v10.pack")
VANILLA   = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"

KEY_ERE = "start_pos_factions_description_2120156326"
KEY_WRE = "start_pos_factions_description_2120156339"

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


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args):
    subprocess.run(args, check=True)


def build_calibration_glyphs(geo: CUF):
    """Append 11 PUA glyphs; returns the list of records written."""
    fe92 = geo.bitmaps[geo.table[0xFE92]]          # 6x18 ink, 108 bytes
    w_fe92, h_fe92 = 6, 18
    fef2 = geo.bitmaps[geo.table[0xFEF2]]          # 9x20, 180 bytes
    wf, hf = 9, 20

    def beh_clone(aw, w):
        if w >= w_fe92:
            bm = fe92 + b"\x00" * ((w - w_fe92) * h_fe92)
        else:
            bm = b"".join(fe92[r * w_fe92:r * w_fe92 + w] for r in range(h_fe92))
        return (18, aw, w, 18), bm

    def blank(aw, w, h=18, ah=18):
        return (ah, aw, w, h), bytes(w * h)

    def refit18():
        rows = []
        for r in range(18):
            src = min(hf - 1, r * hf // 18)
            rows.append(fef2[src * wf:(src + 1) * wf])
        return (18, 8, 9, 18), b"".join(rows)

    def shift_up2():
        rows = [fef2[(r + 2) * wf:(r + 3) * wf] for r in range(hf - 2)]
        rows += [bytes(wf) for _ in range(2)]
        return (20, 8, 9, 20), b"".join(rows)

    specs = []
    for i, (aw, w) in enumerate([(6, 6), (5, 6), (6, 4), (4, 6), (8, 6), (6, 8)]):
        specs.append((0xE100 + i, f"beh clone (aw={aw},w={w})", beh_clone(aw, w)))
    for i, (aw, w) in enumerate([(4, 4), (8, 8)]):
        specs.append((0xE110 + i, f"blank (aw={aw},w={w})", blank(aw, w)))
    specs.append((0xE112, "blank (aw=8,w=0)", blank(8, 0, 0, ah=-128)))
    specs.append((0xE120, "FEF2 refit 18 rows", refit18()))
    specs.append((0xE121, "FEF2 shifted up 2", shift_up2()))

    print("== records to write (georgia_italic_12) ==")
    for cp, label, (dims, bm) in specs:
        print(f"  U+{cp:04X} {label:24s} dims={dims} bitmap={len(bm)}B")

    base = geo.count
    for j, (cp, label, (dims, bm)) in enumerate(specs):
        geo.dims.append(dims)
        geo.bitmaps.append(bm)
        geo.table[cp] = base + j
    return specs


def main():
    log = []
    sha_before = sha256_file(VANILLA)
    assert sha_before == EXPECTED_VANILLA_SHA, sha_before
    log.append(f"vanilla SHA256 before: {sha_before}")

    # ---------------- fonts pack ----------------
    vf = PackFile(V8_FONTS)
    geo = CUF.decode(vf.get_file("font\\georgia_italic_12.cuf"))
    specs = build_calibration_glyphs(geo)
    geo12_new = geo.encode()
    chk = CUF.decode(geo12_new)
    for cp, label, (dims, bm) in specs:
        i = chk.table[cp]
        assert chk.dims[i] == dims and chk.bitmaps[i] == bm, f"record round-trip {hex(cp)}"
    print("== round-trip check: aw and w written independently (decoded back) ==")
    for cp in (0xE100, 0xE101, 0xE102, 0xE103, 0xE104, 0xE105, 0xE110, 0xE111, 0xE112, 0xE120, 0xE121):
        i = chk.table[cp]
        print(f"  U+{cp:04X} decoded dims={chk.dims[i]}")
    assert geo12_new[:32 + 131072] != b""  # table region present

    tmpdir = os.path.join(BASE, "build", "v10_fonts")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)
    for name in sorted(vf.files):
        data = geo12_new if name.endswith("georgia_italic_12.cuf") else vf.get_file(name)
        with open(os.path.join(tmpdir, name.split("\\")[-1]), "wb") as f:
            f.write(data)
    tmp_pack = os.path.join(BASE, "build", "v10f_tmp.pack")
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
    PACK = os.path.join(BASE, "tools", "packfile.py")
    run(PY, PACK, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in sorted(vf.files):
        run(PY, PACK, "add", tmp_pack, name, os.path.join(tmpdir, name.split("\\")[-1]))
    run(PY, PACK, "set-type", tmp_pack, "3", "--output", FONTS_OUT)
    os.remove(tmp_pack)

    v10f = PackFile(FONTS_OUT)
    assert v10f.header.version == b"PFH4" and v10f.header.pack_type == 3
    for name in vf.files:
        if name.endswith("georgia_italic_12.cuf"):
            continue
        assert v10f.get_file(name) == vf.get_file(name), f"drift {name}"
    log.append("v10_fonts: 30 CUFs byte-identical to v8_fonts; geo12 = v8 + 11 PUA glyphs")

    # ---------------- loc pack ----------------    (from v8.pack, 2 values)
    v8 = PackFile(V8_PACK)
    ere = "\n".join([chr(0xE100 + i) * 20 for i in range(6)] +
                    ["\uFE8D" + chr(0xE110) * 20 + "\uFE8D",
                     "\uFE8D" + chr(0xE111) * 20 + "\uFE8D",
                     "\uFE8D" + chr(0xE112) * 20 + "\uFE8D"])
    phrase = shape("روما الغربية")
    wre = "\n".join(["\uFEF2" * 20, "\uE120" * 20, "\uE121" * 20,
                     "\uE111" * 10 + phrase, "\uE111" * 10 + phrase])
    repl = {KEY_ERE: ere, KEY_WRE: wre}
    touched = {r"text\db\start_pos_factions.loc"}

    tmpdir2 = os.path.join(BASE, "build", "v10_loc")
    shutil.rmtree(tmpdir2, ignore_errors=True)
    os.makedirs(tmpdir2)
    for internal in FILES:
        raw = v8.get_file(internal)
        if internal not in touched:
            out = os.path.join(tmpdir2, internal.split("\\")[-1] + ".raw")
            open(out, "wb").write(raw)
            continue
        rows, pos, total = decode(raw)
        assert pos == total
        keys = {k for k, _, _ in rows}
        for k in repl:
            assert k in keys, k
        out_rows = [(k, repl.get(k, t), tip) for k, t, tip in rows]
        out = os.path.join(tmpdir2, internal.split("\\")[-1] + ".loc")
        open(out, "wb").write(encode(out_rows))

    tmp2 = os.path.join(BASE, "build", "v10l_tmp.pack")
    if os.path.exists(tmp2):
        os.remove(tmp2)
    run(PY, PACK, "create", tmp2, "--type", "3", "--version", "PFH4")
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        src = os.path.join(tmpdir2, leaf + ".raw")
        if not os.path.exists(src):
            src = os.path.join(tmpdir2, leaf + ".loc")
        run(PY, PACK, "add", tmp2, internal, src)
    run(PY, PACK, "set-type", tmp2, "3", "--output", LOC_OUT)
    os.remove(tmp2)

    v10 = PackFile(LOC_OUT)
    assert v10.header.version == b"PFH4" and v10.header.pack_type == 3
    assert sorted(v10.files) == sorted(FILES)
    for internal in FILES:
        if internal in touched:
            r8, _, _ = decode(v8.get_file(internal))
            r10, _, _ = decode(v10.get_file(internal))
            d8 = {k: (t, tip) for k, t, tip in r8}
            d10 = {k: (t, tip) for k, t, tip in r10}
            assert d8.keys() == d10.keys()
            for k in d8:
                if k not in repl:
                    assert d8[k] == d10[k], k
        else:
            assert v10.get_file(internal) == v8.get_file(internal), internal
    log.append("v10 loc: untouched 7 files byte-identical; untouched rows identical")
    print("== ERE value lines ==")
    for i, ln in enumerate(ere.split("\n")):
        print(f"  L{i+1}: {' '.join('%04X' % ord(c2) for c2 in ln[:24])}{' ...' if len(ln) > 24 else ''}")
    print("== WRE value lines ==")
    for i, ln in enumerate(wre.split("\n")):
        print(f"  L{i+1}: {' '.join('%04X' % ord(c2) for c2 in ln[:24])}{' ...' if len(ln) > 24 else ''}")

    log.append(f"v10_fonts SHA256: {sha256_file(FONTS_OUT)} ({os.path.getsize(FONTS_OUT)} B)")
    log.append(f"v10 loc SHA256: {sha256_file(LOC_OUT)} ({os.path.getsize(LOC_OUT)} B)")
    sha_after = sha256_file(VANILLA)
    assert sha_after == EXPECTED_VANILLA_SHA, sha_after
    log.append(f"vanilla SHA256 after: {sha_after}")
    print("\n".join(log))


if __name__ == "__main__":
    main()
