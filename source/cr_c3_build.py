#!/usr/bin/env python3
"""C3 builder: Shyizer's 37 CUFs (C1) + ONE declared change - an advance-width
sweep on 4 Arabic codepoints.

For every one of the 37 fonts, four codepoints get a NEW glyph record (appended,
so no existing record, bitmap or header prop is modified) whose bitmap is a
width-clipped copy of that font's U+FE92 bitmap:

    U+FEC7  bitmap w = FE92.w - 3     U+FE9A  bitmap w = FE92.w - 2
    U+FEF5  bitmap w = FE92.w - 1     U+FE8E  bitmap w = FE92.w

The ONLY declared variable is `alloc_width` (the advance): it is set to
w+3 / w+2 / w+1 / w (in every font) i.e. FE92.w / FE92.w-1 / FE92.w-2 /
FE92.w-3. So on screen, four rows of the same shape with four different
advances tell us whether the engine's pitch follows `aw` (rows differ, and
the FE92.w row is the widest) or `w` (rows differ the other way / pitch
equals the drawn width).

  python source/cr_c3_build.py
"""
import hashlib
import json
import os
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF               # noqa: E402
from loc import decode, encode    # noqa: E402
from packfile import PackFile     # noqa: E402
import cr_build as B              # noqa: E402

SHY = os.path.join(BASE, "reference", "shyizer", "data", "Shyizer Arabic.pack")
REL = os.path.join(BASE, "release")
VANILLA = B.VANILLA

# (codepoint, bitmap width delta vs FE92.w, declared advance delta vs FE92.w)
# bitmap w-2 rows are feasible in every font because the narrowest FE92 in the
# set (la_gioconda_uppercase_8) has w=3.
SWEEP = [(0xFEC7, -2, -2), (0xFE9A, -1, -2), (0xFEF5, 0, -2), (0xFE8E, 1, -2)]
REPEAT = 20
LABELS = ["bitmap w-2, aw=w-2", "bitmap w-1, aw=w-2",
          "bitmap w,   aw=w-2", "bitmap w+1, aw=w-2"]

# loc surfaces that receive the sweep; *(key, mode)
PROBE_KEYS = [
    (r"text\db\random_localisation_strings.loc",
     "random_localisation_strings_string_campaign_difficulty_description_2",
     "prepend"),
    (r"text\db\start_pos_factions.loc",
     "start_pos_factions_description_2120156326", "prepend"),
    (r"text\db\start_pos_factions.loc",
     "start_pos_factions_description_2120156339", "prepend"),
    (r"text\db\uied_component_texts.loc",
     "uied_component_texts_localised_string_button_txt_NewState_Text_530011h",
     "prepend"),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def clip_bitmap(bm, w, h, new_w):
    """Crop (or left-pad with 0) a w x h bitmap to new_w columns."""
    rows = [bm[y * w:(y + 1) * w] for y in range(h)]
    out = bytearray()
    for r in rows:
        if new_w <= w:
            out += r[:new_w]
        else:
            out += r + bytes(new_w - w)
    return bytes(out)


def probe_glyphs(c, log, leaf):
    """Append one glyph record per sweep codepoint; return new table/dims/bmps."""
    n = c.count
    dims = list(c.dims)
    bmps = list(c.bitmaps)
    table = list(c.table)
    fe92 = c.table[0xFE92]
    ah92, aw92, w92, h92 = c.dims[fe92]
    assert ah92 == c.props["v_size"] or ah92 == h92, (ah92, c.props["v_size"])
    rows = []
    for cp, wd, ad in SWEEP:
        w = w92 + wd
        aw = aw92 + ad
        assert w >= 1 and aw >= 1, (cp, w, aw)
        idx = len(dims)
        dims.append((ah92, aw, w, h92))
        bmps.append(clip_bitmap(c.bitmaps[fe92], w92, h92, w))
        table[cp] = idx
        rows.append((cp, aw, w, h92, leaf))
    return table, dims, bmps, rows


def build_fonts(log):
    src = PackFile(SHY)
    names = sorted(n for n in src.files if n.endswith(".cuf"))
    entries = {}
    rows = []
    for n in names:
        raw = src.get_file(n)
        old = CUF.decode(raw)
        c = CUF.decode(raw)
        table, dims, bmps, rws = probe_glyphs(c, log, n.split("\\")[-1])
        c.table, c.dims, c.bitmaps = table, dims, bmps
        out = c.encode()
        chk = CUF.decode(out)
        assert chk.encode() == out, f"{n} unstable"
        assert chk.dims[:-len(SWEEP)] == old.dims, n
        assert chk.bitmaps[:-len(SWEEP)] == old.bitmaps, n
        assert chk.table[:] != old.table
        diff = [cp for cp in range(65536) if chk.table[cp] != old.table[cp]]
        assert sorted(diff) == sorted(cp for cp, _, _ in SWEEP), (n, diff)
        assert chk.props == old.props and chk.tail == old.tail, n
        assert len(chk.dims) == len(old.dims) + len(SWEEP), n
        entries[n if n.startswith("font") else
                f"font\\{n.split(chr(92))[-1]}"] = out
        rows += rws
    B.write_pack(os.path.join(REL, "Attila_Arabic_CR_C3_fonts.pack"), entries)
    log.append(f"fonts pack: {len(entries)} CUFs, {len(SWEEP)} new glyph "
               f"records each, only {len(SWEEP)} table entries changed per font")
    return rows


def probe_text():
    lines = ["".join(chr(cp) for _ in range(REPEAT))
             for cp, _, _ in SWEEP]
    return "\n".join(lines)


def build_loc(log):
    files = B.loc_rows({"test": "C3", "loc": {"descriptions_from_long": True}},
                       log)
    block = probe_text()
    for internal, key, mode in PROBE_KEYS:
        rows = files[internal]
        have = {k for k, _, _ in rows}
        assert key in have, f"missing loc key {key}"
        files[internal] = [
            (k, (block + "\n" + t) if (k == key and mode == "prepend") else t, tip)
            for k, t, tip in rows]
    entries = {internal: encode(rows) for internal, rows in files.items()}
    out = os.path.join(REL, "Attila_Arabic_CR_C3.pack")
    B.write_pack(out, entries)
    log.append(f"loc pack: {out} ({os.path.getsize(out)} B) "
               f"SHA256={sha256_file(out)[:16]}")
    log.append(f"loc probe block: {len(SWEEP)} lines x {REPEAT} copies, on "
               f"{len(PROBE_KEYS)} keys")
    return entries


def main():
    log = ["== C3 == declared change: advance-width sweep on 4 unused Arabic "
           "codepoints in all 37 Shyizer fonts (one new glyph record each, "
           "bitmap = clipped copy of that font's FE92)",
           f"vanilla local_en.pack SHA256 before: "
           f"{'OK' if sha256_file(VANILLA) == B.VANILLA_SHA else 'CHANGED!'}"]
    assert sha256_file(VANILLA) == B.VANILLA_SHA
    rows = build_fonts(log)
    build_loc(log)
    assert sha256_file(VANILLA) == B.VANILLA_SHA
    log.append("vanilla local_en.pack SHA256 after: OK")
    hdr = (f"  variant  cp    aw   w   h   | 20 copies advance-line width")
    log.append(hdr)
    per = {}
    for cp, aw, w, h, leaf in rows:
        per.setdefault((cp, aw, w), []).append(leaf)
    for cp, wd, ad in SWEEP:
        sel = sorted({(aw, w) for c2, aw, w, h, l in rows if c2 == cp})
        log.append(f"  U+{cp:04X} (bitmap w = FE92.w{wd:+d}): "
                   f"aw/w pairs across 37 fonts = {sel}")
    for i, (cp, _, _) in enumerate(SWEEP):
        log.append(f"  line {i + 1}: U+{cp:04X} x{REPEAT}   [{LABELS[i]}]")
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    with open(os.path.join(BASE, "logs", "cr_C3_build.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
