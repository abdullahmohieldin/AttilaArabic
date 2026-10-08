#!/usr/bin/env python3
"""Clean-room builder: ONE declared change per test, read from configs/<T>.json.

Inputs are vanilla CUFs (build/vanilla_fonts/, produced by cr_extract.py from
local_en.pack) and the v14 loc text. Nothing is ever written into the game
directory or into vanilla packs.

  python source/cr_build.py C0|C1|C2
"""
import hashlib
import json
import os
import subprocess
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF            # noqa: E402
from loc import decode, encode  # noqa: E402
from packfile import PackFile   # noqa: E402

PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
PACK = os.path.join(BASE, "tools", "packfile.py")
VF = os.path.join(BASE, "build", "vanilla_fonts")
V14 = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")
SHY = os.path.join(BASE, "reference", "shyizer", "data", "Shyizer Arabic.pack")
REL = os.path.join(BASE, "release")
VANILLA = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"

LOC_FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
    r"text\db\land_units.loc",
    r"text\db\faction_groups.loc",
    r"text\db\random_localisation_strings.loc",
    r"text\db\ui_unit_stats.loc",
    r"text\db\ui_unit_bullet_point_enums.loc",
]

# ---------------------------------------------------------------- C2 markers
# 11 real (non-PUA), spacing, unused-by-our-loc Arabic codepoints. Per font the
# barcode is: BLOCK BLOCK <8 id bits MSB first> BLOCK. The asymmetric sync pair
# reveals whether the engine bidi-reversed the run.
MARKER_CPS = [0x0606, 0x0607, 0x0608, 0x0609, 0x060A, 0x060B, 0x060D,
              0x060E, 0x060F, 0x0620, 0x06FD]
MARKER_BITS = 8
MARK_W, MARK_AW = 10, 12

# surface -> (loc file, key, mode). mode "prepend" puts the barcode on its own
# first line above the existing Arabic; "replace" swaps the value outright.
SURFACES = [
    ("ERE faction description", r"text\db\start_pos_factions.loc",
     "start_pos_factions_description_2120156326", "prepend"),
    ("WRE faction description", r"text\db\start_pos_factions.loc",
     "start_pos_factions_description_2120156339", "prepend"),
    ("ERE faction title", r"text\db\factions.loc",
     "factions_screen_name_att_fact_eastern_roman_empire", "replace"),
    ("WRE faction title", r"text\db\factions.loc",
     "factions_screen_name_att_fact_western_roman_empire", "replace"),
    ("faction group dropdown", r"text\db\faction_groups.loc",
     "faction_groups_name_localised_att_fact_group_roman", "replace"),
    ("difficulty box", r"text\db\random_localisation_strings.loc",
     "random_localisation_strings_string_campaign_difficulty_description_2",
     "prepend"),
    ("main menu button (custom battle)", r"text\db\uied_component_texts.loc",
     "uied_component_texts_localised_string_button_txt_NewState_Text_36000f",
     "replace"),
    ("battle setup button", r"text\db\uied_component_texts.loc",
     "uied_component_texts_localised_string_button_txt_NewState_Text_530011h",
     "replace"),
    ("choose-army header", r"text\db\uied_component_texts.loc",
     "uied_component_texts_localised_string_tx_header_NewState_Text_530011",
     "replace"),
    ("difficulty tooltip", r"text\db\uied_component_texts.loc",
     "uied_component_texts_localised_string_medal1_default_Tooltip_5003a",
     "prepend"),
    ("unit stat label (armour)", r"text\db\ui_unit_stats.loc",
     "ui_unit_stats_onscreen_name_stat_armour", "replace"),
    ("unit name", r"text\db\land_units.loc",
     "land_units_onscreen_name_att_rom_legio", "replace"),
    ("unit bullet point", r"text\db\ui_unit_bullet_point_enums.loc",
     "ui_unit_bullet_point_enums_onscreen_name_att_high", "replace"),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def vanilla_fonts():
    return sorted(f for f in os.listdir(VF) if f.endswith(".cuf"))


def write_pack(out_path, entries):
    """entries: {internal_path: bytes} -> PFH4 type-3 .pack (CLI-proven path)."""
    tmp = out_path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    subprocess.run([PY, PACK, "create", tmp, "--type", "3", "--version", "PFH4"],
                   check=True, capture_output=True)
    pf = PackFile(tmp)
    for name in sorted(entries):
        pf.set_file(name, entries[name])
    pf.save(out_path)
    os.remove(tmp)
    back = PackFile(out_path)
    assert back.header.version == b"PFH4" and back.header.pack_type == 3
    assert len(back.files) == len(entries), (len(back.files), len(entries))
    for name, data in entries.items():
        assert back.get_file(name) == data, f"pack verify failed: {name}"


# ------------------------------------------------------------------ loc side
def loc_rows(cfg, log):
    v14 = PackFile(V14)
    files = {}
    for internal in LOC_FILES:
        rows, pos, total = decode(v14.get_file(internal))
        assert pos == total, internal
        files[internal] = rows

    if cfg["loc"].get("descriptions_from_long", False):
        spf = files[r"text\db\start_pos_factions.loc"]
        d = {k: t for k, t, _ in spf}
        n = 0
        for suf in ("2120156326", "2120156339"):
            long = d["start_pos_factions_long_description_" + suf]
            files[r"text\db\start_pos_factions.loc"] = [
                (k, long if k == "start_pos_factions_description_" + suf else t, tip)
                for k, t, tip in files[r"text\db\start_pos_factions.loc"]]
            n += 1
        log.append(f"loc change: {n} description keys := long_description "
                   f"(tatweel pads dropped)")

    if cfg["loc"].get("marker", False):
        line = "".join(chr(cp) for cp in MARKER_CPS)
        by_file = {}
        for _surf, internal, key, mode in SURFACES:
            by_file.setdefault(internal, []).append((key, mode))
        for internal, targets in by_file.items():
            rows = files[internal]
            have = {k for k, _, _ in rows}
            for key, _mode in targets:
                assert key in have, f"missing loc key {key}"
            new = []
            for k, t, tip in rows:
                for key, mode in targets:
                    if k != key:
                        continue
                    t = (line + "\n" + t) if mode == "prepend" else line
                new.append((k, t, tip))
            files[internal] = new
        log.append(f"loc change: barcode on {len(SURFACES)} keys "
                   f"({len(by_file)} files), {len(MARKER_CPS)} glyphs/line")
    return files


def build_loc(cfg, log):
    files = loc_rows(cfg, log)
    entries = {internal: encode(rows) for internal, rows in files.items()}
    out = os.path.join(REL, f"Attila_Arabic_CR_{cfg['test']}.pack")
    write_pack(out, entries)
    log.append(f"loc pack: {out} ({os.path.getsize(out)} B) "
               f"SHA256={sha256_file(out)[:16]}")
    return entries


# ----------------------------------------------------------------- font side
def marker_glyphs(cuf, font_id):
    """-> (new_table, new_dims, new_bitmaps, n_appended).

    Appends exactly 3 glyph records at indices N, N+1, N+2:
      N   blank  - absorbs the pre-existing dangling entries (code == N), which
                   currently draw the engine placeholder; nothing else changes.
      N+1 block  - solid 255, w=MARK_W h=v_size
      N+2 blank  - same dims as the block, zero bitmap (bit value 0)
    Only the 11 marker codepoints are remapped; no existing glyph is touched.
    """
    n = cuf.count
    v = cuf.props["v_size"]
    dims = list(cuf.dims) + [(0, 8, 0, 0),
                             (v, MARK_AW, MARK_W, v),
                             (v, MARK_AW, MARK_W, v)]
    bitmaps = list(cuf.bitmaps) + [b"",
                                   bytes([255]) * (MARK_W * v),
                                   bytes(MARK_W * v)]
    bits = [(font_id >> (MARKER_BITS - 1 - i)) & 1 for i in range(MARKER_BITS)]
    pattern = [1, 1] + bits + [1]
    assert len(pattern) == len(MARKER_CPS)
    table = list(cuf.table)
    for cp, bit in zip(MARKER_CPS, pattern):
        table[cp] = n + 1 if bit else n + 2
    return table, dims, bitmaps, 3


def build_fonts_marker(cfg, log):
    fonts = vanilla_fonts()
    entries = {}
    table_lines = []
    for idx, leaf in enumerate(fonts):
        raw = open(os.path.join(VF, leaf), "rb").read()
        old = CUF.decode(raw)
        c = CUF.decode(raw)
        table, dims, bitmaps, napp = marker_glyphs(c, idx)
        c.table, c.dims, c.bitmaps = table, dims, bitmaps
        out = c.encode()
        chk = CUF.decode(out)
        assert chk.encode() == out, f"{leaf} unstable"
        # original glyph records, bitmaps and kerning tail untouched
        assert chk.dims[:len(dims) - napp] == old.dims
        assert chk.bitmaps[:len(bitmaps) - napp] == old.bitmaps
        assert chk.tail == old.tail and chk.props == old.props
        assert len(chk.dims) == len(old.dims) + napp
        diff = [cp for cp, v in enumerate(chk.table) if v != old.table[cp]]
        assert sorted(diff) == sorted(MARKER_CPS), (leaf, diff)
        entries[f"font\\{leaf}"] = out
        bits = "".join(str((idx >> (MARKER_BITS - 1 - i)) & 1)
                       for i in range(MARKER_BITS))
        table_lines.append(f"{idx:3d}  {bits}  {leaf}")
    write_pack(os.path.join(REL, f"Attila_Arabic_CR_{cfg['test']}_fonts.pack"),
               entries)
    log.append(f"fonts pack: {len(entries)} vanilla CUFs + 3 appended glyphs "
               f"each, 11 table entries remapped each")
    hdr = "  id  barcode   font"
    log.append("font -> marker table:\n" + hdr + "\n" + "\n".join(table_lines))
    with open(os.path.join(BASE, "logs", f"cr_{cfg['test']}_markers.txt"), "w",
              encoding="utf-8") as f:
        f.write(hdr + "\n" + "\n".join(table_lines) + "\n")
    return entries


def build_fonts_shyizer(cfg, log):
    src = PackFile(SHY)
    names = sorted(n for n in src.files if n.endswith(".cuf"))
    entries = {}
    for n in names:
        data = src.get_file(n)
        entries[n if n.startswith("font") else f"font\\{n.split(chr(92))[-1]}"] = data
    assert len(entries) == len(names) == 37, (len(entries), len(names))
    write_pack(os.path.join(REL, f"Attila_Arabic_CR_{cfg['test']}_fonts.pack"),
               entries)
    log.append(f"fonts pack: {len(entries)} Shyizer CUFs, byte-for-byte "
               f"(test only, never committed)")
    return entries


def coverage_check(cfg, loc_entries, font_entries, log):
    """Every codepoint the loc uses must exist with ink in the shipped fonts."""
    used = {}
    for internal, data in loc_entries.items():
        for _k, text, _t in decode(data)[0]:
            for ch in text:
                used.setdefault(ord(ch), set()).add(internal.split("\\")[-1])
    lines = [f"loc codepoints: {len(used)}"]
    for name in sorted(font_entries):
        c = CUF.decode(font_entries[name])
        missing, blank = [], []
        for cp in sorted(used):
            i = c.table[cp]
            if i == 0xFFFF or i >= c.count:
                missing.append(cp)
                continue
            _ah, _aw, w, h = c.dims[i]
            if not (w and h) or not any(c.bitmaps[i]):
                blank.append(cp)
        lines.append(f"{name.split(chr(92))[-1]:32s} missing={len(missing):3d} "
                     f"blank={len(blank):3d}")
        if missing:
            lines.append("    missing: " + " ".join(f"U+{c2:04X}" for c2 in missing))
        if blank:
            lines.append("    blank  : " + " ".join(f"U+{c2:04X}" for c2 in blank))
    txt = "\n".join(lines)
    with open(os.path.join(BASE, "logs", f"cr_{cfg['test']}_coverage.txt"), "w",
              encoding="utf-8") as f:
        f.write(txt + "\n")
    log.append(f"coverage -> logs/cr_{cfg['test']}_coverage.txt")
    return lines


def main():
    test = sys.argv[1]
    cfg = json.load(open(os.path.join(BASE, "configs", f"{test}.json"),
                         encoding="utf-8"))
    assert cfg["test"] == test
    log = [f"== {test} == declared change: {cfg['change']}",
           f"vanilla local_en.pack SHA256 before: "
           f"{'OK' if sha256_file(VANILLA) == VANILLA_SHA else 'CHANGED!'}"]
    assert sha256_file(VANILLA) == VANILLA_SHA

    loc_entries = build_loc(cfg, log)
    mode = cfg["fonts"]["mode"]
    if mode == "none":
        log.append("fonts pack: none (vanilla fonts only)")
    elif mode == "shyizer":
        coverage_check(cfg, loc_entries, build_fonts_shyizer(cfg, log), log)
    elif mode == "vanilla_marker":
        build_fonts_marker(cfg, log)
    else:
        raise SystemExit(f"unknown fonts mode {mode}")

    assert sha256_file(VANILLA) == VANILLA_SHA
    log.append("vanilla local_en.pack SHA256 after: OK")
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    with open(os.path.join(BASE, "logs", f"cr_{test}_build.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
