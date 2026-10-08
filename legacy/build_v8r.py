#!/usr/bin/env python3
"""Build v8r diagnostics pack (v9 round).

v8r.pack = v8.pack with exactly 3 values replaced; everything else is a raw
byte copy of v8's stored file data (not re-encoded).

  ERE  start_pos_factions_description_2120156326      -> 4 ruler lines
  Hard random_localisation_strings_string_campaign_difficulty_description_2
                                                       -> same 4 ruler lines
  WRE  start_pos_factions_description_2120156339      -> 6 pad-probe lines

Ruler lines are stored VERBATIM (no reshaper, no bidi).  WRE phrase is shaped
FIRST (reshaper + bidi), THEN the pad prefix is concatenated, so pads sit at
stored positions 0-9 (leftmost on screen).

Rationale for the round (v9 report): the v8_ruler pack shipped vanilla text
because build_v8.py's ruler section keyed ruler_want with "<key>_<tag>"
suffixes that match no real key, and because 3 variants cannot share one .loc
key -- the variants must be LF-separated lines inside one value, which is what
this builder stores.
"""
import hashlib
import os
import shutil
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))

from loc import decode, encode          # noqa: E402
from packfile import PackFile           # noqa: E402
from shape import shape                 # noqa: E402

V8_PACK    = os.path.join(BASE, "release", "Attila_Arabic_POC_v8.pack")
V8R_PACK   = os.path.join(BASE, "release", "Attila_Arabic_POC_v8r.pack")
VANILLA    = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"

KEY_ERE  = "start_pos_factions_description_2120156326"
KEY_WRE  = "start_pos_factions_description_2120156339"
KEY_HARD = "random_localisation_string" \
           "s_string_campaign_difficulty_description_2"

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


def ruler_value():
    """4 LF-separated ruler lines, stored verbatim (no shaping)."""
    l1 = "\uFE92" * 20                       # medial beh x20
    l2 = "\uFE8D" * 20                       # isolated alef x20
    l3 = "\uFEF2" * 20                       # final yeh x20 (dots test)
    l4 = "\uFE8D" + " " * 20 + "\uFE8D"      # space advance test
    return "\n".join([l1, l2, l3, l4])


def pad_value():
    """6 lines: pads (x10) + short shaped phrase. Pads AFTER shaping."""
    phrase = shape("روما الغربية")
    lines = (
        ["\u00A0" * 10 + phrase] * 2 +       # NBSP   (space-like, blank)
        ["\u2003" * 10 + phrase] * 2 +       # EM SPACE (stray dash ink)
        ["\uE000" * 10 + phrase] * 2         # PUA (visible marker glyph)
    )
    return "\n".join(lines)


def main():
    log = []
    sha_before = sha256_file(VANILLA)
    assert sha_before == EXPECTED_VANILLA_SHA, f"vanilla hash BEFORE: {sha_before}"
    log.append(f"vanilla SHA256 before: {sha_before}")

    v8 = PackFile(V8_PACK)
    assert v8.header.version == b"PFH4" and v8.header.pack_type == 3
    assert sorted(v8.files) == sorted(FILES), "v8 file list mismatch"

    repl = {KEY_ERE: ruler_value(), KEY_HARD: ruler_value(), KEY_WRE: pad_value()}
    touched = {r"text\db\start_pos_factions.loc", r"text\db\random_localisation_strings.loc"}

    tmpdir = os.path.join(BASE, "build", "v8r_files")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)

    for internal in FILES:
        raw = v8.get_file(internal)
        if internal not in touched:
            out = os.path.join(tmpdir, internal.split("\\")[-1] + ".raw")
            with open(out, "wb") as f:
                f.write(raw)
            continue
        rows, pos, total = decode(raw)
        assert pos == total
        keys = {k for k, _, _ in rows}
        for k in repl:
            if _own(k) == internal:
                assert k in keys, f"key {k} not in {internal}"
        out_rows = []
        for k, t, tip in rows:
            out_rows.append((k, repl[k], tip) if k in repl else (k, t, tip))
        out = os.path.join(tmpdir, internal.split("\\")[-1] + ".loc")
        with open(out, "wb") as f:
            f.write(encode(out_rows))

    tmp_pack = os.path.join(BASE, "build", "v8r_tmp.pack")
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    import subprocess
    PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
    PACK = os.path.join(BASE, "tools", "packfile.py")
    subprocess.run([PY, PACK, "create", tmp_pack, "--type", "3", "--version", "PFH4"], check=True)
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        src = os.path.join(tmpdir, leaf + ".raw")
        if not os.path.exists(src):
            src = os.path.join(tmpdir, leaf + ".loc")
        subprocess.run([PY, PACK, "add", tmp_pack, internal, src], check=True)
    subprocess.run([PY, PACK, "set-type", tmp_pack, "3", "--output", V8R_PACK], check=True)
    os.remove(tmp_pack)

    # ---------------- self-check ----------------
    v8r = PackFile(V8R_PACK)
    assert v8r.header.version == b"PFH4" and v8r.header.pack_type == 3, "v8r header"
    assert sorted(v8r.files) == sorted(FILES), "v8r file list"
    log.append("v8r header PFH4 type 3, file list matches v8")

    rows_v8, rows_v8r = {}, {}
    for internal in FILES:
        if internal in touched:
            r8, _, _ = decode(v8.get_file(internal))
            rr, _, _ = decode(v8r.get_file(internal))
            d8 = {k: (t, tip) for k, t, tip in r8}
            dr = {k: (t, tip) for k, t, tip in rr}
            assert d8.keys() == dr.keys(), f"key set drift in {internal}"
            for k in d8:
                if k not in repl:
                    assert d8[k] == dr[k], f"row drift: {k}"
            rows_v8[internal], rows_v8r[internal] = d8, dr
        else:
            assert v8.get_file(internal) == v8r.get_file(internal), f"raw drift: {internal}"
    log.append("untouched 6 files byte-identical; untouched rows of 2 edited files identical")

    for k in (KEY_ERE, KEY_WRE, KEY_HARD):
        val = rows_v8r[r"text\db\start_pos_factions.loc" if "start_pos" in k
                       else r"text\db\random_localisation_strings.loc"][k][0]
        print(f"--- {k}")
        for i, ln in enumerate(val.split("\n")):
            print(f"  L{i+1}: {' '.join('%04X' % ord(c) for c in ln)}")

    log.append(f"v8r SHA256: {sha256_file(V8R_PACK)}")
    log.append(f"v8r size: {os.path.getsize(V8R_PACK)} bytes")
    sha_after = sha256_file(VANILLA)
    assert sha_after == EXPECTED_VANILLA_SHA, f"vanilla hash AFTER: {sha_after}"
    log.append(f"vanilla SHA256 after: {sha_after}")
    print("\n".join(log))


def _own(k):
    for prefix, f in [("start_pos_", 0), ("random_localisation_", 1)]:
        if k.startswith(prefix):
            return (r"text\db\start_pos_factions.loc",
                    r"text\db\random_localisation_strings.loc")[f]
    raise AssertionError(k)


if __name__ == "__main__":
    main()
