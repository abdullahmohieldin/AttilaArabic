#!/usr/bin/env python3
"""Build v2b probe pack (loc-only, NO CUF): full-file copies with ~67 rows
replaced by ASCII-ID-prefixed pre-shaped Arabic.

Usage: build_v2b.py
Writes: build/v2b/*.loc, release/Attila_Arabic_POC_v2b.pack,
        docs/test-pack-manifest-v2b.md (ids table appended),
        localization/corpus_v2b.txt
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
BUILD = os.path.join(BASE, "build", "v2b")
REL = os.path.join(BASE, "release", "Attila_Arabic_POC_v2b.pack")

U = "uied_component_texts_localised_string_"
LONG_AR = ("الإمبراطورية الرومانية الغربية على حافة الانهيار. الإمبراطور يرقص "
           "على أنغام قائدٍ من الوندال، ومجلس الشيوخ عاجزٌ في ضياعٍ واسعة. "
           "روما — أم الإمبراطورية — أُهملت لصالح عاصمةٍ عملية في ميديولانوم. "
           "منذ انقسام الإمبراطورية (395م) تفاقمت العيوب بسرعة: التجارة 1200 "
           "قطعة ذهبية والضرائب أعلى بنسبة 25%.")
WORDS = ["القاهرة", "الحملة", "الجيش", "روما", "الإمبراطورية"]

FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
    r"text\db\land_units.loc",
    r"text\db\faction_groups.loc",
    r"text\db\random_localisation_strings.loc",
    r"text\db\ui_unit_stats.loc",
]


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args}\n{r.stderr[-2000:]}")
    return r.stdout


def build_want():
    want = {}
    # ---- carry over all v2 probes (same IDs, same formula) ----
    v2keys = [
        ("K01", U + "string_NewState_Text_3a000c"),
        ("K02", U + "string_NewState_Text_3a000cm"),
        ("K03", U + "button_txt_NewState_Text_36000f"),
        ("K04", U + "button_txt_NewState_Text_36000fs"),
        ("K06", U + "string_NewState_Text_250075x"),
        ("K07", U + "tx_title_mp_Text_250075"),
        ("K08", U + "button_txt_NewState_Text_250075"),
        ("K09", U + "string_NewState_Text_460009"),
        ("K10", U + "heading_tx_NewState_Text_460009j"),
        ("K11", U + "string_NewState_Text_1d002f"),
        ("K12", U + "button_txt_NewState_Text_700030"),
        ("K13", U + "string_NewState_Text_700030"),
        ("K14", U + "button_txt_NewState_Text_23001bb"),
        ("K15", U + "button_txt_NewState_Text_530011r"),
        ("K16", U + "string_active_Text_c0020"),
        ("K17", U + "string_active_Text_3b"),
        ("K18", U + "button_txt_NewState_Text_430007"),
        ("K19", U + "button_txt_NewState_Text_380007"),
        ("K20", U + "button_txt_NewState_Text_30006e"),
        ("K21", U + "tx_header_NewState_Text_530011"),
        ("K22", U + "heading_tx_NewState_Text_79004a"),
        ("K24", U + "header_cultural_NewState_Text_5e0000"),
        ("K25", U + "header_faction_NewState_Text_410063"),
        ("K29", U + "tx_header_NewState_Text_b0036"),
        ("K30", U + "medal1_default_Tooltip_5003a"),
        ("K32", U + "StatusIcon_Wavering_Tooltip_a003d"),
    ]
    for i, (tag, k) in enumerate(v2keys):
        word = {"K30": "صعب", "K32": "متردد"}.get(tag, WORDS[i % len(WORDS)])
        want[k] = f"{tag} {word}"
    want[U + "string_NewState_Text_250075"] = "K05 Rome 1200 — روما"
    want["factions_screen_name_bel_fact_byzantine_empire"] = "K23 روما"
    want["factions_screen_name_att_fact_eastern_roman_empire"] = \
        "K26 الجيش الأول: 1200 جندي"
    want["land_units_onscreen_name_att_rom_legio"] = "K31 فيلق"
    # ---- new: miss variants (rule e) ----
    want[U + "button_txt_NewState_Text_530011"] = "K33 القاهرة"
    want[U + "string_NewState_Text_530011"] = "K34 الحملة"
    want[U + "button_txt_NewState_Text_530011h"] = "K35 الجيش"
    want[U + "string_continue_campaign_Text_380007"] = "K36 روما"
    want[U + "string_NewState_Text_180007"] = "K37 الإمبراطورية"
    want[U + "tx_difficulty_NewState_Text_79004a"] = "K38 القاهرة"
    want[U + "region_religion_Tooltip_b0036"] = "K39 الحملة"
    want[U + "tx_culture_NewState_Text_b0036"] = "K40 الجيش"
    want[U + "religion_Tooltip_b0036"] = "K41 روما"
    # ---- group tabs (faction_groups) ----
    want["faction_groups_name_localised_att_fact_group_roman"] = "K42 روما"
    want["faction_groups_name_localised_att_fact_group_eastern"] = "K43 القاهرة"
    want["faction_groups_name_localised_att_fact_group_nomadic"] = "K44 الحملة"
    want["faction_groups_name_localised_att_fact_group_barbarian"] = "K45 الجيش"
    want["faction_groups_name_localised_att_fact_group_barbarian_m"] = "K46 روما"
    want["faction_groups_name_localised_att_fact_group_sand"] = "K47 الإمبراطورية"
    # ---- labels ----
    want[U + "year_txt_NewState_Text_310044"] = "K48 القاهرة"
    want[U + "year_tx_NewState_Text_310064"] = "K49 الحملة"
    want[U + "tx_initial_challenge:_NewState_Text_670040"] = "K50 الجيش"
    # ---- difficulty descriptions ----
    want["random_localisation_strings_string_campaign_difficulty_description_0"] = \
        "K51 القاهرة"
    want["random_localisation_strings_string_campaign_difficulty_description_1"] = \
        "K52 الحملة"
    want["random_localisation_strings_string_campaign_difficulty_description_2"] = \
        "K53 الإمبراطورية"
    want["random_localisation_strings_string_campaign_difficulty_description_3"] = \
        "K54 الجيش"
    want["random_localisation_strings_string_campaign_difficulty_description_4"] = \
        "K55 روما"
    # ---- slider tooltips: T01 long, T02/T03 short ----
    want[U + "handle_NewState_Tooltip_7000b"] = "T01 " + LONG_AR
    want[U + "handle_Tooltip_7000b"] = "T02 التجارة 1200"
    want[U + "cmp_diff_slider_Tooltip_7000b"] = "T03 الحملة"
    # ---- unit info labels ----
    want["ui_unit_stats_onscreen_name_stat_melee_attack"] = "U01 هجوم"
    want["ui_unit_stats_onscreen_name_stat_armour"] = "U02 درع"
    want["ui_unit_stats_onscreen_name_stat_health"] = "U03 صحة"
    want["ui_unit_stats_onscreen_name_stat_morale"] = "U04 معنويات"
    want["ui_unit_stats_onscreen_name_stat_speed"] = "U05 سرعة"
    # ---- tag probes: (a) logical order, (b) post-bidi storage order ----
    va = shape("الحملة")
    want["uied_component_texts_localised_string_dy_text_accepted_Text_35006c"] = \
        "G01 [[col:green]]" + "الحملة" + "[[/col]]"
    # (b): tags placed where bidi moved them (close-tag first in storage)
    want["uied_component_texts_localised_string_dy_text_rejected_Text_330065"] = \
        "G02 [[/col]] " + va + " [[col:red]]"
    # NOTE: shape() would also move tags; store (b) WITHOUT reshaping so the
    # storage order is exactly as written (tags must survive byte-identical).
    want["_raw_G02"] = None
    # ---- descriptions: short + long, WRE + ERE ----
    want["start_pos_factions_description_2120156339"] = "D28a " + LONG_AR
    want["start_pos_factions_long_description_2120156339"] = "D28b " + LONG_AR
    want["start_pos_factions_description_2120156889"] = "D27a " + LONG_AR
    want["start_pos_factions_long_description_2120156889"] = "D27b " + LONG_AR
    # ---- newline probes on other long keys ----
    nl = LONG_AR.replace(". ", ".\n", 2)
    want["start_pos_factions_long_description_2120156283"] = \
        "D29 " + nl.replace("\n", "\n")
    want["start_pos_factions_long_description_2120156823"] = \
        "D29b " + nl.replace("\n", "\r\n")
    return want


def _owner(k):
    for prefix, f in [("uied_", 0), ("factions_", 1), ("start_pos_", 2),
                      ("land_units_", 3), ("faction_groups_", 4),
                      ("random_localisation_", 5), ("ui_unit_stats_", 6)]:
        if k.startswith(prefix):
            return FILES[f]
    raise AssertionError(k)


def main():
    os.makedirs(BUILD, exist_ok=True)
    want = build_want()
    raw_g02 = ("G02 [[/col]] " + shape("الحملة") + " [[col:red]]")
    changed, corpus = {}, set()
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        tmp = os.path.join(BUILD, "vanilla_" + leaf)
        run(VENV_PY, PACK_PY, "extract", COPY_PACK, internal, "--output", tmp)
        rows, pos, total = decode(open(tmp, "rb").read())
        assert pos == total, f"slack in {internal}"
        keys = {k for k, _, _ in rows}
        missing = [k for k in want if not k.startswith("_")
                   and _owner(k) == internal and k not in keys]
        assert not missing, f"missing keys in {internal}: {missing}"
        out = []
        for k, t, tip in rows:
            if k in want and _owner(k) == internal:
                if k.endswith("_330065"):
                    v = raw_g02  # stored verbatim, NOT reshaped
                else:
                    v = shape(want[k])
                changed[k] = (t, v)
                corpus.update(ch for ch in v if ord(ch) > 127)
                out.append((k, v, tip))
            else:
                out.append((k, t, tip))
        data = encode(out)
        rows2, pos2, _ = decode(data)
        assert pos2 == len(data) and len(rows2) == len(rows)
        open(os.path.join(BUILD, leaf), "wb").write(data)
    # ERE short-description twin (assert separately; may not exist)
    print(f"edited {len(changed)} keys")
    with open(os.path.join(BASE, "localization", "corpus_v2b.txt"),
              "w", encoding="utf-8") as f:
        f.write("".join(sorted(corpus)))
    print(f"v2b new non-ascii codepoints: {len(corpus)}")
    run(VENV_PY, PACK_PY, "create", os.path.join(BUILD, "v2b.pack"),
        "--type", "3", "--version", "PFH4")
    for internal in FILES:
        run(VENV_PY, PACK_PY, "add", os.path.join(BUILD, "v2b.pack"),
            internal, os.path.join(BUILD, internal.split("\\")[-1]))
    run(VENV_PY, PACK_PY, "set-type", os.path.join(BUILD, "v2b.pack"),
        "3", "--output", REL)
    print(run(VENV_PY, PACK_PY, "info", REL))
    print(run(VENV_PY, PACK_PY, "list", REL))
    print("wrote", REL)


if __name__ == "__main__":
    main()
