#!/usr/bin/env python3
"""Build v13 probe (round 13): edge-crop spacing variants + alignment probes.

Base: v11 packs (real ink everywhere; v12 solids dropped).
Vanilla local_en.pack is verified SHA256 before AND after (never modified).

FONTS (v13_fonts): georgia_italic_12 ONLY, 4 in-place bitmap surgeries on
REAL codepoints (PUA clones render as engine placeholder, so variants reuse
distinct real glyphs of the same teeth ductus). All other glyphs in geo12
and the other 30 CUFs byte-identical to v11.

  FE92  control (v11 stretched ink, untouched)
  FE98  solid: cell 6->8, join row = full-width 255 bar (alpha-threshold test)
  FE9C  alpha: cell 6->8, join row extended with edge alpha (geometry test)
  FEF4  solid overlap: cell 6->7, join row 255 across (overlap/clip test)
  FE8D  alpha: join rows shifted + extended to cell edge (alef gap test)
  FE8E  control (alef final, untouched)
  FEF2  control (v11 refit, untouched)

LOC (v13): ERE description = 6 ruler lines (one variant each) + 1 real
sentence; WRE description byte-identical to v11 (control); difficulty _2
Hard byte-identical (control); _0/_1/_3/_4 = Hard-text order/period probes.
All other rows/files byte-identical to v11.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import unicodedata

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))

from cuf import CUF        # noqa: E402
from loc import decode, encode  # noqa: E402
from packfile import PackFile  # noqa: E402
from shape import shape    # noqa: E402

V11_FONTS = os.path.join(BASE, "release", "Attila_Arabic_POC_v11_fonts.pack")
V11_PACK  = os.path.join(BASE, "release", "Attila_Arabic_POC_v11.pack")
FONTS_OUT = os.path.join(BASE, "release", "Attila_Arabic_POC_v13_fonts.pack")
LOC_OUT   = os.path.join(BASE, "release", "Attila_Arabic_POC_v13.pack")
VANILLA   = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"

KEY_ERE = "start_pos_factions_description_2120156326"
KEY_WRE = "start_pos_factions_description_2120156339"
DIFF = "random_localisation_strings_string_campaign_difficulty_description_"
HARD = "صعب: يتطلب تخطيطاً دقيقاً وإدارة حازمة للجيوش والموارد."
ERE_SENTENCE = "الشرق يمسك بزمام العالم الروماني."
INK_THRESH = 20
RLM = "\u200F"

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

# cp -> (label, treatment, new_w). Treatments on JOIN rows only
# (rows whose ink touches both edges of the ink bbox = connecting stroke):
#   control      untouched (v11 ink)
#   solid        new_w cell, join rows = full-width solid 255 bar
#   alpha        new_w cell, join rows shifted + extended with edge alpha
#   (other rows only shift left by x0, dots/stems untouched).
TARGETS = {
    0xFE92: ("beh medial", "control", None),
    0xFE98: ("teh medial", "solid", 8),
    0xFE9C: ("theh medial", "alpha", 8),
    0xFEF4: ("yeh medial", "solid", 7),
    0xFE8D: ("alef isolated", "alpha", 5),
    0xFE8E: ("alef final", "control", None),
}
EXPECT_NAME = {
    0xFE92: "BEH MEDIAL", 0xFE98: "TEH MEDIAL", 0xFE9C: "THEH MEDIAL",
    0xFEF4: "YEH MEDIAL", 0xFE8D: "ALEF ISOLATED", 0xFE8E: "ALEF FINAL",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args):
    subprocess.run(args, check=True)


def surgery(bm, w, h, treatment, new_w):
    """Join-row surgery. Join rows = ink touches both bbox edges.
    Returns (out_w, new_bitmap, info)."""
    rows = [list(bm[y * w:(y + 1) * w]) for y in range(h)]
    ink_cols = [x for y in range(h) for x in range(w) if rows[y][x] > INK_THRESH]
    assert ink_cols, "empty glyph"
    x0, x1 = min(ink_cols), max(ink_cols)
    out_w = new_w
    out = bytearray(out_w * h)
    n_join = 0
    for y in range(h):
        old = rows[y]
        is_join = old[x0] > INK_THRESH and old[x1] > INK_THRESH
        if is_join:
            n_join += 1
            if treatment == "solid":
                for j in range(out_w):
                    out[y * out_w + j] = 255
            else:  # alpha: shift + extend with edge value
                for j in range(out_w):
                    src = x0 + j
                    out[y * out_w + j] = old[src] if src < w else 0
                for j in range(x1 - x0 + 1, out_w):
                    out[y * out_w + j] = old[x1]
        else:
            for j in range(out_w):
                src = x0 + j
                out[y * out_w + j] = old[src] if src < w else 0
    assert n_join > 0, "no join rows -> treatment would be a no-op"
    return out_w, bytes(out), \
        f"x0={x0} x1={x1} w={w}->{out_w} join_rows={n_join}/{h}"


def main():
    log = []
    sha_before = sha256_file(VANILLA)
    assert sha_before == EXPECTED_VANILLA_SHA, sha_before
    log.append(f"vanilla SHA256 before: {sha_before}")

    # ---------------- fonts ----------------
    v11f = PackFile(V11_FONTS)
    assert len(v11f.files) == 31
    geo = CUF.decode(v11f.get_file("font\\georgia_italic_12.cuf"))
    old_bitmaps = list(geo.bitmaps)
    old_dims = list(geo.dims)

    # Base cleanliness: v11 must contain NO v12 solids on probed codepoints.
    for cp in (0xFEF2, 0xFE92, 0xFE8D):
        bm = geo.bitmaps[geo.table[cp]]
        assert set(bm) != {255}, f"U+{cp:04X} still solid in v11 base!"

    changed = {}
    print("== geo12 surgeries ==")
    for cp, (label, treatment, want_w) in TARGETS.items():
        nm = unicodedata.name(chr(cp), "")
        assert EXPECT_NAME[cp] in nm, f"U+{cp:04X} is {nm}, expected {EXPECT_NAME[cp]}"
        i = geo.table[cp]
        assert i < geo.count
        ah, aw, w, h = geo.dims[i]
        bm = geo.bitmaps[i]
        assert w and h and any(b > INK_THRESH for b in bm), f"U+{cp:04X} empty"
        if treatment == "control":
            print(f"  U+{cp:04X} {label:14s} control dims={(ah, aw, w, h)}")
            continue
        new_w, new_bm, info = surgery(bm, w, h, treatment, want_w)
        geo.dims[i] = (ah, aw, new_w, h)
        geo.bitmaps[i] = new_bm
        changed[i] = cp
        print(f"  U+{cp:04X} {label:14s} {treatment:3s} {(ah, aw, w, h)} -> {(ah, aw, new_w, h)} {info}")

    for i in range(len(geo.dims)):
        if i not in changed:
            assert geo.dims[i] == old_dims[i] and geo.bitmaps[i] == old_bitmaps[i], f"glyph {i} drifted"
    order = sorted(TARGETS.keys(), key=lambda codepoint: geo.table[codepoint])
    changed_labels = ", ".join(
        f"U+{cp:04X}={TARGETS[cp][1]}" for cp in order if geo.table[cp] in changed)
    log.append(f"geo12: {len(changed)} glyphs surgered " + changed_labels)

    geo12_new = geo.encode()
    chk = CUF.decode(geo12_new)
    assert chk.encode() == geo12_new, "geo12 unstable"
    for cp, (label, treatment, want_w) in TARGETS.items():
        i = chk.table[cp]
        assert chk.bitmaps[i] == geo.bitmaps[geo.table[cp]], f"round-trip U+{cp:04X}"

    tmpdir = os.path.join(BASE, "build", "v13_fonts")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)
    for name in sorted(v11f.files):
        data = geo12_new if name.endswith("georgia_italic_12.cuf") else v11f.get_file(name)
        with open(os.path.join(tmpdir, name.split("\\")[-1]), "wb") as f:
            f.write(data)
    tmp_pack = os.path.join(BASE, "build", "v13f_tmp.pack")
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
    PACK = os.path.join(BASE, "tools", "packfile.py")
    run(PY, PACK, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in sorted(v11f.files):
        run(PY, PACK, "add", tmp_pack, name, os.path.join(tmpdir, name.split("\\")[-1]))
    run(PY, PACK, "set-type", tmp_pack, "3", "--output", FONTS_OUT)
    os.remove(tmp_pack)

    v13f = PackFile(FONTS_OUT)
    assert v13f.header.version == b"PFH4" and v13f.header.pack_type == 3
    for name in v11f.files:
        if name.endswith("georgia_italic_12.cuf"):
            continue
        assert v13f.get_file(name) == v11f.get_file(name), f"drift {name}"
    log.append("v13_fonts: other 30 CUFs byte-identical to v11_fonts")

    # ---------------- loc ----------------
    v11 = PackFile(V11_PACK)
    rows_spf, pos, total = decode(v11.get_file(r"text\db\start_pos_factions.loc"))
    assert pos == total
    d_spf = {k: (t, tip) for k, t, tip in rows_spf}
    assert KEY_ERE in d_spf and KEY_WRE in d_spf
    wre_v11 = d_spf[KEY_WRE][0]

    ere_v13 = "\n".join([
        "\uFE92" * 20,   # L1 control beh medial
        "\uFE98" * 20,   # L2 V1 teh medial
        "\uFE9C" * 20,   # L3 V2 theh medial
        "\uFEF4" * 20,   # L4 V3 yeh medial
        "\uFE8D" * 20,   # L5 V1 alef
        "\uFE8E" * 20,   # L6 control alef final
        shape(ERE_SENTENCE),
    ])
    hard_full = shape(HARD)
    words = HARD.split(" ")
    half = len(words) // 2
    narrow = shape(" ".join(words[:half])) + "\n" + shape(" ".join(words[half:]))
    rows_r, p2, t2 = decode(v11.get_file(r"text\db\random_localisation_strings.loc"))
    assert p2 == t2
    d_r = {k: t for k, t, _ in rows_r}
    repl_r = {
        DIFF + "0": hard_full,              # engine-wrap test (no LF)
        DIFF + "1": d_r[DIFF + "2"] + RLM,  # RLM at stored end
        DIFF + "3": RLM + d_r[DIFF + "2"],  # RLM at stored start
        DIFF + "4": narrow,                 # different break positions
    }
    assert d_r[DIFF + "2"] == d_r[DIFF + "2"]  # control stays
    repl_spf = {KEY_ERE: ere_v13}

    tmpdir2 = os.path.join(BASE, "build", "v13_loc")
    shutil.rmtree(tmpdir2, ignore_errors=True)
    os.makedirs(tmpdir2)
    for internal in FILES:
        raw = v11.get_file(internal)
        if internal == r"text\db\start_pos_factions.loc":
            rows, p, t = decode(raw)
            assert p == t
            out = os.path.join(tmpdir2, "start_pos_factions.loc")
            open(out, "wb").write(encode(
                [(k, repl_spf.get(k, x), tip) for k, x, tip in rows]))
        elif internal == r"text\db\random_localisation_strings.loc":
            rows, p, t = decode(raw)
            assert p == t
            out = os.path.join(tmpdir2, "random_localisation_strings.loc")
            open(out, "wb").write(encode(
                [(k, repl_r.get(k, x), tip) for k, x, tip in rows]))
        else:
            out = os.path.join(tmpdir2, internal.split("\\")[-1] + ".raw")
            open(out, "wb").write(raw)

    tmp2 = os.path.join(BASE, "build", "v13l_tmp.pack")
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

    v13 = PackFile(LOC_OUT)
    assert v13.header.version == b"PFH4" and v13.header.pack_type == 3
    for internal in FILES:
        if internal in (r"text\db\start_pos_factions.loc",
                        r"text\db\random_localisation_strings.loc"):
            continue
        assert v13.get_file(internal) == v11.get_file(internal), internal
    r13, p, t = decode(v13.get_file(r"text\db\start_pos_factions.loc"))
    assert p == t
    d13 = {k: x for k, x, _ in r13}
    assert d13[KEY_WRE] == wre_v11, "WRE drifted"
    assert d13[KEY_ERE] == ere_v13
    assert {k for k, _, _ in rows_spf} == set(d13)
    rr13, p, t = decode(v13.get_file(r"text\db\random_localisation_strings.loc"))
    assert p == t
    dd13 = {k: x for k, x, _ in rr13}
    assert dd13[DIFF + "2"] == d_r[DIFF + "2"], "Hard control drifted"
    for k, v in repl_r.items():
        assert dd13[k] == v, k
    log.append("v13 loc: WRE + Hard/_2 identical to v11; ERE desc + _0/_1/_3/_4 replaced")

    print("== ERE lines ==")
    for i, ln in enumerate(ere_v13.split("\n"), start=1):
        print(f"  L{i}: {' '.join('%04X' % ord(c) for c in ln[:24])}{' ...' if len(ln) > 24 else ''}")
    print("== difficulty probes ==")
    for k in (DIFF + "0", DIFF + "1", DIFF + "2", DIFF + "3", DIFF + "4"):
        print(f"  {k[-2:]}: {' '.join('%04X' % ord(c) for c in dd13[k][:16])} ... len={len(dd13[k])}")

    log.append(f"v13_fonts SHA256: {sha256_file(FONTS_OUT)} ({os.path.getsize(FONTS_OUT)} B)")
    log.append(f"v13 loc SHA256: {sha256_file(LOC_OUT)} ({os.path.getsize(LOC_OUT)} B)")
    sha_after = sha256_file(VANILLA)
    assert sha_after == EXPECTED_VANILLA_SHA, sha_after
    log.append(f"vanilla SHA256 after: {sha_after}")
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    with open(os.path.join(BASE, "logs", "v13_build.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
