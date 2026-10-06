#!/usr/bin/env python3
"""Build v2 probe pack (loc-only, NO CUF): full-file copies of 4 vanilla .loc
files with ~33 rows replaced by ASCII-ID-prefixed pre-shaped Arabic.

Usage: build_v2.py
Writes: build/v2/*.loc, release/Attila_Arabic_POC_v2.pack,
        docs/test-pack-manifest-v2.md, localization/corpus_v1v2.txt
"""
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from loc import decode, encode  # noqa: E402
from shape import shape  # noqa: E402

VENV_PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
PACK_PY = os.path.join(BASE, "tools", "packfile.py")
COPY_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
BUILD = os.path.join(BASE, "build", "v2")
REL = os.path.join(BASE, "release", "Attila_Arabic_POC_v2.pack")

U = "uied_component_texts_localised_string_"
LONG_AR = ("الإمبراطورية الرومانية الغربية على حافة الانهيار. الإمبراطور يرقص "
           "على أنغام قائدٍ من الوندال، ومجلس الشيوخ عاجزٌ في ضياعٍ واسعة. "
           "روما — أم الإمبراطورية — أُهملت لصالح عاصمةٍ عملية في ميديولانوم. "
           "منذ انقسام الإمبراطورية (395م) تفاقمت العيوب بسرعة: التجارة 1200 "
           "قطعة ذهبية والضرائب أعلى بنسبة 25%.")
WORDS = ["القاهرة", "الحملة", "الجيش", "روما", "الإمبراطورية"]

# (key, logical-arabic) in file order below; IDs must be unique
PROBES = [
    # --- uied: Battles menu ---
    (U + "string_NewState_Text_3a000c", "K01"),
    (U + "string_NewState_Text_3a000cm", "K02"),
    (U + "button_txt_NewState_Text_36000f", "K03"),
    (U + "button_txt_NewState_Text_36000fs", "K04"),
    (U + "string_NewState_Text_250075", "K05"),
    (U + "string_NewState_Text_250075x", "K06"),
    (U + "tx_title_mp_Text_250075", "K07"),
    (U + "button_txt_NewState_Text_250075", "K08"),
    (U + "string_NewState_Text_460009", "K09"),
    (U + "heading_tx_NewState_Text_460009j", "K10"),
    (U + "string_NewState_Text_1d002f", "K11"),
    (U + "button_txt_NewState_Text_700030", "K12"),
    (U + "string_NewState_Text_700030", "K13"),
    # --- uied: Campaigns menu + faction select + battle HUD ---
    (U + "button_txt_NewState_Text_23001bb", "K14"),
    (U + "button_txt_NewState_Text_530011r", "K15"),
    (U + "string_active_Text_c0020", "K16"),
    (U + "string_active_Text_3b", "K17"),
    (U + "button_txt_NewState_Text_430007", "K18"),
    (U + "button_txt_NewState_Text_380007", "K19"),
    (U + "button_txt_NewState_Text_30006e", "K20"),
    (U + "tx_header_NewState_Text_530011", "K21"),
    (U + "heading_tx_NewState_Text_79004a", "K22"),
    (U + "header_cultural_NewState_Text_5e0000", "K24"),
    (U + "header_faction_NewState_Text_410063", "K25"),
    (U + "tx_header_NewState_Text_b0036", "K29"),
    (U + "medal1_default_Tooltip_5003a", "K30"),
    (U + "StatusIcon_Wavering_Tooltip_a003d", "K32"),
]
# special-content probes (id, key, logical)
SPECIAL = [
    ("K05", U + "string_NewState_Text_250075", "K05 Rome 1200 — روما"),
    ("K26", "factions_screen_name_att_fact_eastern_roman_empire",
     "K26 الجيش الأول: 1200 جندي"),
    ("K27", "start_pos_factions_long_description_2120156889", None),  # long
    ("K28", "start_pos_factions_long_description_2120156339", None),  # long
    ("K23", "factions_screen_name_bel_fact_byzantine_empire", None),  # word
    ("K31", "land_units_onscreen_name_att_rom_legio", "K31 فيلق"),
]
FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
    r"text\db\land_units.loc",
]


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args}\n{r.stderr[-2000:]}")
    return r.stdout


def main():
    os.makedirs(BUILD, exist_ok=True)
    want = {}
    for i, (k, tag) in enumerate(PROBES):
        if k == U + "string_NewState_Text_250075":
            continue  # K05 handled by SPECIAL (AR+EN content)
        want[k] = f"{tag} {WORDS[i % len(WORDS)]}"
    want["factions_screen_name_bel_fact_byzantine_empire"] = "K23 روما"
    want["land_units_onscreen_name_att_rom_legio"] = "K31 فيلق"
    want[U + "medal1_default_Tooltip_5003a"] = "K30 صعب"
    want[U + "StatusIcon_Wavering_Tooltip_a003d"] = "K32 متردد"
    want["start_pos_factions_long_description_2120156889"] = "D27 " + LONG_AR
    want["start_pos_factions_long_description_2120156339"] = "D28 " + LONG_AR
    for tag, k, logical in SPECIAL:
        if logical is not None and k != U + "string_NewState_Text_250075":
            want[k] = logical
    want[U + "string_NewState_Text_250075"] = "K05 Rome 1200 — روما"

    changed, corpus = {}, set()
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        tmp = os.path.join(BUILD, "vanilla_" + leaf)
        run(VENV_PY, PACK_PY, "extract", COPY_PACK, internal, "--output", tmp)
        rows, pos, total = decode(open(tmp, "rb").read())
        assert pos == total, f"slack in {internal}"
        keys = {k for k, _, _ in rows}
        missing = [k for k in want if _owner(k) == internal and k not in keys]
        assert not missing, f"missing keys in {internal}: {missing}"
        out = []
        for k, t, tip in rows:
            if k in want and _owner(k) == internal:
                v = shape(want[k])
                changed[k] = (t, want[k])
                corpus.update(ch for ch in v if ord(ch) > 127)
                out.append((k, v, tip))
            else:
                out.append((k, t, tip))
        data = encode(out)
        rows2, pos2, _ = decode(data)
        assert pos2 == len(data) and len(rows2) == len(rows)
        open(os.path.join(BUILD, leaf), "wb").write(data)
    print(f"edited {len(changed)} keys")
    with open(os.path.join(BASE, "localization", "corpus_v1v2.txt"),
              "w", encoding="utf-8") as f:
        f.write("".join(sorted(corpus)))
    print(f"corpus non-ascii codepoints: {len(corpus)}")
    run(VENV_PY, PACK_PY, "create", os.path.join(BUILD, "v2.pack"),
        "--type", "3", "--version", "PFH4")
    for internal in FILES:
        run(VENV_PY, PACK_PY, "add", os.path.join(BUILD, "v2.pack"),
            internal, os.path.join(BUILD, internal.split("\\")[-1]))
    run(VENV_PY, PACK_PY, "set-type", os.path.join(BUILD, "v2.pack"),
        "3", "--output", REL)
    print(run(VENV_PY, PACK_PY, "info", REL))
    print(run(VENV_PY, PACK_PY, "list", REL))
    print("wrote", REL)


def _file_keys(internal, want):
    if internal.endswith("uied_component_texts.loc"):
        return {k for k in want if k.startswith("uied_")}
    if internal.endswith("factions.loc"):
        return {k for k in want if k.startswith("factions_")}
    if internal.endswith("start_pos_factions.loc"):
        return {k for k in want if k.startswith("start_pos_")}
    if internal.endswith("land_units.loc"):
        return {k for k in want if k.startswith("land_units_")}
    return set()


def _owner(k):
    for prefix, f in [("uied_", 0), ("factions_", 1), ("start_pos_", 2),
                      ("land_units_", 3)]:
        if k.startswith(prefix):
            return FILES[f]
    raise AssertionError(k)


if __name__ == "__main__":
    main()
