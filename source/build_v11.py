#!/usr/bin/env python3
"""Build v11 probe (round 11): three IN-PLACE geo12 glyph changes.

Base = v10 packs (clones/PUA glyphs kept untouched, all other glyphs unchanged):

  FEF2  bitmap replaced with the 18-row refit (E120's resample), dims
        (ah=18, aw=8, w=9, h=18).  Tests whether the missing final-yeh dots
        are caused by the over-box geometry (clipping) or something else.
        Horizontal geometry unchanged -> engine advance should stay 12.0.
  FE92  bitmap stretched horizontally 6 -> 8 px (nearest column), aw/w
        updated only as needed for storage (aw=5 kept, w=8).  Tests whether
        stretching ink to the fixed engine advance (8.0) closes the join gap.
  FE8D  bitmap stretched horizontally 3 -> 5 px (aw=3 kept, w=5).
        Engine advance 5.0 -> stretched ink should close the gap.

v11.loc = v10.loc with the WRE description extended by 3 lines (20xFE92,
20xFE8D, one shaped sentence reusing stretched FE92/FEF8D forms); ERE and all
other rows/files byte-identical to v10.  The v10 WRE line 1 (20 x FEF2) stays
and becomes the refit test line; the v10 screenshot is its control.
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
from loc import decode, encode  # noqa: E402
from packfile import PackFile  # noqa: E402
from shape import shape    # noqa: E402

V10_FONTS = os.path.join(BASE, "release", "Attila_Arabic_POC_v10_fonts.pack")
V10_PACK  = os.path.join(BASE, "release", "Attila_Arabic_POC_v10.pack")
FONTS_OUT = os.path.join(BASE, "release", "Attila_Arabic_POC_v11_fonts.pack")
LOC_OUT   = os.path.join(BASE, "release", "Attila_Arabic_POC_v11.pack")
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


def stretch_columns(bm, old_w, new_w, h):
    """Nearest-neighbor horizontal stretch of a packed 8-bit bitmap."""
    out = bytearray(new_w * h)
    for r in range(h):
        for c in range(new_w):
            out[r * new_w + c] = bm[r * old_w + min(old_w - 1, c * old_w // new_w)]
    return bytes(out)


def main():
    log = []
    sha_before = sha256_file(VANILLA)
    assert sha_before == EXPECTED_VANILLA_SHA, sha_before
    log.append(f"vanilla SHA256 before: {sha_before}")

    # ---------------- fonts ----------------
    v10f = PackFile(V10_FONTS)
    geo = CUF.decode(v10f.get_file("font\\georgia_italic_12.cuf"))
    old_bitmaps = list(geo.bitmaps)
    old_dims = list(geo.dims)

    i_fef2 = geo.table[0xFEF2]
    i_fe92 = geo.table[0xFE92]
    i_fe8d = geo.table[0xFE8D]
    i_e120 = geo.table[0xE120]

    # FEF2 -> refit 18 rows (reuse E120's resampled bitmap, FEF2's horizontal metrics)
    geo.dims[i_fef2] = (18, 8, 9, 18)
    geo.bitmaps[i_fef2] = geo.bitmaps[i_e120]
    # FE92 -> stretch ink 6 -> 8
    bm = geo.bitmaps[i_fe92]
    geo.dims[i_fe92] = (18, 5, 8, 18)
    geo.bitmaps[i_fe92] = stretch_columns(bm, 6, 8, 18)
    # FE8D -> stretch ink 3 -> 5
    bm = geo.bitmaps[i_fe8d]
    geo.dims[i_fe8d] = (18, 3, 5, 18)
    geo.bitmaps[i_fe8d] = stretch_columns(bm, 3, 5, 18)

    print("== in-place record changes (georgia_italic_12) ==")
    for lab, i in [("FEF2", i_fef2), ("FE92", i_fe92), ("FE8D", i_fe8d)]:
        print(f"  {lab}: {old_dims[i]} -> {geo.dims[i]}  bitmap {len(old_bitmaps[i])}B -> {len(geo.bitmaps[i])}B")

    changed = {i_fef2, i_fe92, i_fe8d}
    for i in range(len(geo.dims)):
        if i not in changed:
            assert geo.dims[i] == old_dims[i] and geo.bitmaps[i] == old_bitmaps[i], f"glyph {i} drifted"
    log.append("geo12: all glyphs byte-identical to v10 except FEF2/FE92/FE8D")

    geo12_new = geo.encode()
    chk = CUF.decode(geo12_new)
    assert chk.dims[chk.table[0xFEF2]] == (18, 8, 9, 18)
    assert chk.dims[chk.table[0xFE92]] == (18, 5, 8, 18)
    assert chk.dims[chk.table[0xFE8D]] == (18, 3, 5, 18)
    assert chk.bitmaps[chk.table[0xFEF2]] == geo.bitmaps[i_fef2]

    tmpdir = os.path.join(BASE, "build", "v11_fonts")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)
    for name in sorted(v10f.files):
        data = geo12_new if name.endswith("georgia_italic_12.cuf") else v10f.get_file(name)
        with open(os.path.join(tmpdir, name.split("\\")[-1]), "wb") as f:
            f.write(data)
    tmp_pack = os.path.join(BASE, "build", "v11f_tmp.pack")
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
    PACK = os.path.join(BASE, "tools", "packfile.py")
    run(PY, PACK, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in sorted(v10f.files):
        run(PY, PACK, "add", tmp_pack, name, os.path.join(tmpdir, name.split("\\")[-1]))
    run(PY, PACK, "set-type", tmp_pack, "3", "--output", FONTS_OUT)
    os.remove(tmp_pack)

    v11f = PackFile(FONTS_OUT)
    assert v11f.header.version == b"PFH4" and v11f.header.pack_type == 3
    for name in v10f.files:
        if name.endswith("georgia_italic_12.cuf"):
            continue
        assert v11f.get_file(name) == v10f.get_file(name), name
    log.append("v11_fonts: other 30 CUFs byte-identical to v10_fonts")

    # ---------------- loc ----------------
    v10 = PackFile(V10_PACK)
    rows0, _, _ = decode(v10.get_file(r"text\db\start_pos_factions.loc"))
    d10 = {k: t for k, t, _ in rows0}
    wre_v11 = d10[KEY_WRE] + "\n" + "\n".join([
        "\uFE92" * 20,
        "\uFE8D" * 20,
        shape("اثبات ثبات ثبت ثوب اثبات ثبات ثبت"),
    ])
    repl = {KEY_WRE: wre_v11}

    tmpdir2 = os.path.join(BASE, "build", "v11_loc")
    shutil.rmtree(tmpdir2, ignore_errors=True)
    os.makedirs(tmpdir2)
    for internal in FILES:
        raw = v10.get_file(internal)
        if internal != r"text\db\start_pos_factions.loc":
            out = os.path.join(tmpdir2, internal.split("\\")[-1] + ".raw")
            open(out, "wb").write(raw)
            continue
        rows, pos, total = decode(raw)
        assert pos == total
        out_rows = [(k, repl.get(k, t), tip) for k, t, tip in rows]
        out = os.path.join(tmpdir2, internal.split("\\")[-1] + ".loc")
        open(out, "wb").write(encode(out_rows))

    tmp2 = os.path.join(BASE, "build", "v11l_tmp.pack")
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

    v11 = PackFile(LOC_OUT)
    assert v11.header.version == b"PFH4" and v11.header.pack_type == 3
    for internal in FILES:
        if internal == r"text\db\start_pos_factions.loc":
            r10, _, _ = decode(v10.get_file(internal))
            r11, _, _ = decode(v11.get_file(internal))
            d11 = {k: t for k, t, _ in r11}
            assert {k for k, _, _ in r10} == set(d11)
            for k, t, _ in r10:
                if k != KEY_WRE:
                    assert d11[k] == t, k
            assert d11[KEY_ERE] == d10[KEY_ERE], "ERE drifted"
        else:
            assert v11.get_file(internal) == v10.get_file(internal), internal
    log.append("v11 loc: ERE + all other rows/files identical to v10; WRE = v10 + 3 lines")
    print("== WRE lines added ==")
    for i, ln in enumerate(wre_v11.split("\n")[-3:], start=len(wre_v11.split("\n")) - 2):
        print(f"  L{i}: {' '.join('%04X' % ord(c2) for c2 in ln[:30])}{' ...' if len(ln) > 30 else ''}")

    log.append(f"v11_fonts SHA256: {sha256_file(FONTS_OUT)} ({os.path.getsize(FONTS_OUT)} B)")
    log.append(f"v11 loc SHA256: {sha256_file(LOC_OUT)} ({os.path.getsize(LOC_OUT)} B)")
    sha_after = sha256_file(VANILLA)
    assert sha_after == EXPECTED_VANILLA_SHA, sha_after
    log.append(f"vanilla SHA256 after: {sha_after}")
    print("\n".join(log))


if __name__ == "__main__":
    main()
