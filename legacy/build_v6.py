#!/usr/bin/env python3
"""Build v6 POC: corrected key mapping, line wrapping, ERE description, rating words.

Changes vs v4:
  FONTS (v6fonts):
    - Connecting-form advance: INITIAL/MEDIAL/FINAL forms get adv = ink_width,
      left=0, so adjacent strokes share a common pixel column (gap=0).
    - All other glyph placement identical to v5 (baseline-row aligned).

  LOC (v6.pack):
    1. Key mapping rebuilt from screen-verified v2b probe table. Wrong
       assignments in v4 (K03/K16/K17/K20/K25/K33) are corrected.
    2. Line wrapping uses measured box widths (minus 10 px safety):
         description area  : 310 px (georgia_italic_12)
         difficulty text   : 350 px (la_gioconda_12)
    3. Lines stored top-to-bottom joined with LF (both WRE and ERE).
    4. ERE description uses the correct key (2120156326, not 2120156889).
    5. Tab names split to 2 lines with explicit LF at the word boundary.
    6. Dropdown faction names shortened to fit 125 px closed-dropdown width.
    7. Rating words (Excellent/Good/Average/Poor/Very Poor/High/Very High/Low)
       added to ui_unit_bullet_point_enums.loc.

Outputs:
  - build/v6fonts/*.cuf
  - release/Attila_Arabic_POC_v6_fonts.pack
  - release/Attila_Arabic_POC_v6.pack
  - logs/v6_build.txt
"""
import hashlib
import os
import subprocess
import sys
import unicodedata
from fontTools.ttLib import TTFont
from PIL import ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cuf import CUF          # noqa: E402
from loc import decode, encode  # noqa: E402
from shape import shape      # noqa: E402
from wrap import wrap_multi, wrap_single, visual_width  # noqa: E402

VENV_PY    = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
PACK_PY    = os.path.join(BASE, "tools", "packfile.py")
COPY_PACK  = os.path.join(BASE, "extracted", "local_en.copy.pack")
VANILLA_PACK = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"
TAJAWAL    = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")

FONTS_BUILD = os.path.join(BASE, "build", "v6fonts")
LOC_BUILD   = os.path.join(BASE, "build", "v6")
FONTS_PACK  = os.path.join(BASE, "release", "Attila_Arabic_POC_v6_fonts.pack")
LOC_PACK    = os.path.join(BASE, "release", "Attila_Arabic_POC_v6.pack")

SIZES_GIOC  = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]
SIZES_GEORG = [10, 12, 14, 16, 18]
TARGETS = (  [f"la_gioconda_{s}"           for s in SIZES_GIOC]
           + [f"la_gioconda_uppercase_{s}" for s in SIZES_GIOC]
           + [f"georgia_italic_{s}"        for s in SIZES_GEORG])

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

OVER = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args}\n{r.stderr[-2000:]}")
    return r.stdout


def base_letter(cp):
    try:
        decomp = unicodedata.decomposition(chr(cp))
    except Exception:
        return None
    parts = decomp.split()
    if len(parts) >= 2 and parts[0].startswith("<"):
        try:
            return int(parts[1], 16)
        except ValueError:
            return None
    return None


def is_connecting_cp(cp):
    """True for Initial, Medial, Final forms and Tatweel (they connect to neighbour)."""
    name = unicodedata.name(chr(cp), "")
    return any(f in name for f in ("INITIAL FORM", "MEDIAL FORM", "FINAL FORM")) or cp == 0x0640


def vanilla_metrics(c):
    code = c.table[0x48]  # 'H'
    ah, aw, w, h = c.dims[code]
    d = c.bitmaps[code]
    rows = [y for y in range(h) if any(d[y * w + x] > 20 for x in range(w))]
    top, bottom = min(rows), max(rows)
    return {"cap": bottom - top + 1, "top": top, "bottom": bottom, "cell_h": h, "vsize": c.props["v_size"]}


def calibrate(vanilla_h_cap, lo=8, hi=64):
    best, bestpx = None, None
    for px in range(lo, hi + 1):
        f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        h = f.getbbox("H")[3] - f.getbbox("H")[1]
        if best is None or abs(h - vanilla_h_cap) < best:
            best, bestpx = abs(h - vanilla_h_cap), px
    return bestpx


# ---------------------------------------------------------------------------
# Font build (v6) – connecting-advance fix
# ---------------------------------------------------------------------------

def build_fonts(log):
    os.makedirs(FONTS_BUILD, exist_ok=True)
    cmap = TTFont(TAJAWAL).getBestCmap()

    target_cps = set()
    target_cps.update(range(0x0621, 0x064B))
    target_cps.add(0x0640)
    target_cps.update(range(0x064B, 0x0653))
    target_cps.add(0x0670)
    target_cps.update([0x060C, 0x061B, 0x061F, 0x066A, 0x066B, 0x066C, 0x06D4])
    target_cps.update(range(0x0660, 0x066A))
    target_cps.update(range(0xFB50, 0xFE00))
    target_cps.update(range(0xFE70, 0xFF00))

    decomp_harakat = {
        0xFE70: 0x064B, 0xFE72: 0x064C, 0xFE74: 0x064D, 0xFE76: 0x064E,
        0xFE78: 0x064F, 0xFE7A: 0x0650, 0xFE7C: 0x0651, 0xFE7E: 0x0652,
    }

    src_of = {}
    missing = []
    for cp in sorted(target_cps):
        if cp in decomp_harakat:
            src_of[cp] = chr(decomp_harakat[cp])
        elif cp in cmap:
            src_of[cp] = chr(cp)
        else:
            b = base_letter(cp)
            if b is not None and b in cmap:
                src_of[cp] = chr(b)
            else:
                missing.append(cp)

    log.append(f"Tajawal-Regular.ttf FULL Arabic set: {len(src_of)} sourceable codepoints")
    log.append(f"Unmapped / non-standard in range: {len(missing)} codepoints")

    for name in TARGETS:
        src = os.path.join(BASE, "extracted", "fonts", name + ".cuf")
        c = CUF.decode(open(src, "rb").read())
        assert c.bitmap_total() == c.size, name
        vm = vanilla_metrics(c)
        V = vm["cell_h"]
        baseline_row = vm["bottom"]
        px_cap = calibrate(vm["cap"])

        chosen = None
        for px in range(px_cap, 7, -1):
            f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
            ascent, _ = f.getmetrics()
            ok = True
            for cp, ch in src_of.items():
                bbox = f.getbbox(ch)
                if not bbox:
                    continue
                bx0, by0, bx1, by1 = bbox
                top = baseline_row + by0 - ascent + 1
                bot = baseline_row + by1 - ascent + 1
                if top < -OVER or bot > V + OVER:
                    ok = False
                    break
            if ok:
                chosen = px
                break

        assert chosen is not None, f"{name}: no fitting px"
        px = chosen

        f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        ascent, descent = f.getmetrics()

        dangling = sorted({v for v in c.table if v != 0xFFFF and v >= len(c.dims)})
        new_dims = list(c.dims)
        new_maps = list(c.bitmaps)
        for dcode in dangling:
            while len(new_dims) < dcode:
                raise AssertionError((name, dcode))
            new_dims.append((-128, 0, 0, 0))
            new_maps.append(b"")

        added = {}
        for cp in sorted(src_of.keys()):
            ch = src_of[cp]
            mask = f.getmask(ch, mode="L")
            mw, mh = mask.size
            data = bytes(mask)
            adv = int(round(f.getlength(ch)))
            bbox = f.getbbox(ch)

            if not bbox or not any(data):
                adv_out = max(adv, 4)
                new_dims.append((V, adv_out, adv_out, V))
                new_maps.append(bytes(V * adv_out))
                added[cp] = len(new_dims) - 1
                continue

            bx0, by0, bx1, by1 = bbox

            # Baseline placement (identical to v5)
            top = baseline_row + by0 - ascent + 1
            bot = top + mh
            ctop = min(top, 0)
            cbot = max(bot, V)
            chh = cbot - ctop

            # --- v6 CONNECTING-ADVANCE FIX ---
            # For Initial, Medial, Final forms and Tatweel:
            #   left = 0 (ink starts at column 0, no left bearing gap)
            #   adv_out = mw (cell width equals ink width, no extra trailing space)
            # This ensures adjacent glyphs share a column edge with no pixel gap.
            if is_connecting_cp(cp):
                left = 0
                cw = mw
                adv_out = mw
            else:
                left = bx0 if bx0 >= 0 else 0
                adv_out = max(adv, left + mw)
                cw = adv_out

            cell = bytearray(chh * cw)
            for y in range(mh):
                cy = top - ctop + y
                if 0 <= cy < chh:
                    src_row = data[y * mw : (y + 1) * mw]
                    cell[cy * cw + left : cy * cw + left + mw] = src_row

            code = len(new_dims)
            new_dims.append((chh if chh < 128 else 127, adv_out, cw, chh))
            new_maps.append(bytes(cell))
            added[cp] = code

        table = list(c.table)
        for cp, code in added.items():
            table[cp] = code
        c.table = table
        c.dims = new_dims
        c.bitmaps = new_maps

        out = c.encode()
        c2 = CUF.decode(out)
        assert c2.encode() == out, f"{name} unstable"
        out_path = os.path.join(FONTS_BUILD, name + ".cuf")
        with open(out_path, "wb") as fh:
            fh.write(out)
        log.append(f"{name}: px={px} cell={V} baseline_row={baseline_row} +arabic={len(added)} size={len(out)}B")

    # Package
    tmp_pack = os.path.join(BASE, "build", "v6_fonts_tmp.pack")
    run(VENV_PY, PACK_PY, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in TARGETS:
        run(VENV_PY, PACK_PY, "add", tmp_pack, f"font\\{name}.cuf", os.path.join(FONTS_BUILD, f"{name}.cuf"))
    run(VENV_PY, PACK_PY, "set-type", tmp_pack, "3", "--output", FONTS_PACK)
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    log.append(f"Wrote fonts pack: {FONTS_PACK} ({os.path.getsize(FONTS_PACK)} B, SHA256={sha256_file(FONTS_PACK)})")


# ---------------------------------------------------------------------------
# Loc build (v6) – corrected key mapping
# ---------------------------------------------------------------------------

def _owner(k):
    for prefix, f in [
        ("uied_", 0), ("factions_", 1), ("start_pos_", 2),
        ("land_units_", 3), ("faction_groups_", 4),
        ("random_localisation_", 5), ("ui_unit_stats_", 6),
        ("ui_unit_bullet_", 7),
    ]:
        if k.startswith(prefix):
            return FILES[f]
    raise AssertionError(k)


def build_want(fonts_dir):
    """
    Arabic strings keyed by FULL vanilla key.
    Key mapping is rebuilt from screen-verified v2b probe table.
    """
    want = {}
    U = "uied_component_texts_localised_string_"

    # Load la_gioconda_12 metrics for UI wrapping
    c_lgi12 = CUF.decode(open(os.path.join(fonts_dir, "la_gioconda_12.cuf"), "rb").read())
    adv_lgi12 = {i: c_lgi12.dims[i][1] for i in range(len(c_lgi12.dims))}
    # Load georgia_italic_12 for description wrapping
    c_geo12 = CUF.decode(open(os.path.join(fonts_dir, "georgia_italic_12.cuf"), "rb").read())
    adv_geo12 = {i: c_geo12.dims[i][1] for i in range(len(c_geo12.dims))}

    # -------------------------------------------------------------------
    # 1. BATTLES MENU
    #    v2b verified: K01=Historical Battle, K03=Custom Battle (button+title),
    #                  K05=Multiplayer Battle, K10=Quick Battle (heading),
    #                  K11=Leaderboards, K12=Replays
    # -------------------------------------------------------------------
    want[U + "string_NewState_Text_3a000c"]          = "معركة تاريخية"      # K01 button 1
    want[U + "string_NewState_Text_3a000cm"]         = "معركة تاريخية"      # K01 variant
    want[U + "button_txt_NewState_Text_36000f"]      = "معركة مخصصة"        # K03 button 2 (also Custom Battle title on faction-select panel)
    want[U + "button_txt_NewState_Text_36000fs"]     = "معركة مخصصة"        # K03 variant
    want[U + "string_NewState_Text_250075"]          = "معركة متعددة اللاعبين"  # K05 button 3
    want[U + "string_NewState_Text_250075x"]         = "معركة متعددة اللاعبين"
    want[U + "tx_title_mp_Text_250075"]              = "معركة متعددة اللاعبين"
    want[U + "button_txt_NewState_Text_250075"]      = "معركة متعددة اللاعبين"
    want[U + "heading_tx_NewState_Text_460009j"]     = "معركة سريعة"         # K10 button 4 heading
    want[U + "string_NewState_Text_460009"]          = "معركة سريعة"         # K09
    want[U + "string_NewState_Text_1d002f"]          = "لوحات الصدارة"        # K11 button 5
    want[U + "button_txt_NewState_Text_700030"]      = "التسجيلات"            # K12 button 6

    # -------------------------------------------------------------------
    # 2. CAMPAIGNS MENU
    #    K14=Load Campaign, K15=Grand Campaign, K16=The Last Roman,
    #    K17=Age of Charlemagne, K18=Multiplayer Campaign, K36=Continue Campaign (bottom)
    # -------------------------------------------------------------------
    want[U + "button_txt_NewState_Text_23001bb"]     = "تحميل حملة"           # K14
    want[U + "button_txt_NewState_Text_530011r"]     = "الحملة الكبرى"        # K15 Grand Campaign
    want[U + "string_active_Text_c0020"]             = "الروماني الأخير"      # K16 The Last Roman
    want[U + "string_active_Text_3b"]                = "عصر شارلمان"          # K17 Age of Charlemagne
    want[U + "button_txt_NewState_Text_430007"]      = "حملة متعددة اللاعبين" # K18
    want[U + "string_continue_campaign_Text_380007"] = "متابعة الحملة"        # K36 bottom button (Continue Campaign)
    want[U + "string_NewState_Text_180007"]          = "متابعة الحملة"        # K37 variant
    want[U + "button_txt_NewState_Text_380007"]      = "القائمة الرئيسية"

    # -------------------------------------------------------------------
    # 3. FACTION SELECT
    #    K33=faction-select header ("New Campaign"), K20=Start button,
    #    K24=Cultural Trait header, K25=Faction Trait header,
    #    K38=Difficulty heading, K42-K47=group tabs, K49=Start year label,
    #    K50=Initial challenge label, K51-K55=difficulty descriptions,
    #    K26=faction name
    # -------------------------------------------------------------------

    # K33: header of faction-select panel (vanilla: "New Campaign")
    want[U + "button_txt_NewState_Text_530011"]      = "اختر الفصيل"          # K33 faction-select header
    want[U + "string_NewState_Text_530011"]          = "اختر الجيوش"          # K34 army-select variant
    want[U + "button_txt_NewState_Text_530011h"]     = "إعدادات المعركة"       # K35

    # K20: Start button (vanilla: "Start Campaign")
    want[U + "button_txt_NewState_Text_30006e"]      = "بدء الحملة"           # K20

    # K21: tx_header (panel heading)
    want[U + "tx_header_NewState_Text_530011"]       = "الحملة الجديدة"

    # K22: Difficulty heading (vanilla: "Difficulty")
    want[U + "heading_tx_NewState_Text_79004a"]      = "مستوى الصعوبة"         # K22
    want[U + "tx_difficulty_NewState_Text_79004a"]   = "صعوبة الحملة"          # K38

    # K24/K25: trait panel headers
    want[U + "header_cultural_NewState_Text_5e0000"] = "السمات الثقافية"       # K24
    want[U + "header_faction_NewState_Text_410063"]  = "سمات الفصيل"           # K25

    # Faction-select misc labels
    want[U + "tx_header_NewState_Text_b0036"]        = "تفاصيل الفصيل"
    want[U + "tx_culture_NewState_Text_b0036"]       = "الثقافة"
    want[U + "region_religion_Tooltip_b0036"]        = "دين الإقليم"
    want[U + "religion_Tooltip_b0036"]               = "دين الدولة"

    # K48/K49: Start year labels (vanilla: "Start year:")
    want[U + "year_txt_NewState_Text_310044"]        = "سنة البداية:"          # K48
    want[U + "year_tx_NewState_Text_310064"]         = "سنة البداية:"          # K49

    # K50: Initial challenge (vanilla: "Initial challenge:")
    want[U + "tx_initial_challenge:_NewState_Text_670040"] = "التحدي المبدئي:" # K50

    # Tooltips
    want[U + "handle_Tooltip_7000b"]                = "مستوى صعوبة الحملة"
    want[U + "cmp_diff_slider_Tooltip_7000b"]       = "تعديل مستوى الصعوبة"
    want[U + "medal1_default_Tooltip_5003a"]        = "مستوى الصعوبة: صعب"
    want[U + "StatusIcon_Wavering_Tooltip_a003d"]   = "الروح المعنوية: متزعزعة"
    want[U + "string_NewState_Text_700030"]         = "التسجيلات"

    # -------------------------------------------------------------------
    # 4. FACTION GROUP TABS (K42-K47)
    #    Two-line names, LF-separated, top line first.
    #    Measured max: Roman=98px/63px, Eastern=60/62, Nomadic=50/49,
    #    Barbarian=60/54, Migrating=50/65, Desert=48/60 — all fit in 100px.
    # -------------------------------------------------------------------
    want["faction_groups_name_localised_att_fact_group_roman"]       = shape("الإمبراطوريات") + "\n" + shape("الرومانية")
    want["faction_groups_name_localised_att_fact_group_eastern"]     = shape("الممالك") + "\n" + shape("الشرقية")
    want["faction_groups_name_localised_att_fact_group_nomadic"]     = shape("القبائل") + "\n" + shape("البدوية")
    want["faction_groups_name_localised_att_fact_group_barbarian"]   = shape("الممالك") + "\n" + shape("البربرية")
    want["faction_groups_name_localised_att_fact_group_barbarian_m"] = shape("القبائل") + "\n" + shape("المهاجرة")
    want["faction_groups_name_localised_att_fact_group_sand"]        = shape("ممالك") + "\n" + shape("الصحراء")

    # -------------------------------------------------------------------
    # 5. FACTION NAMES — short to fit 125 px closed dropdown
    #    Measured: "روما الغربية"=88px, "روما الشرقية"=97px, "الساسانيون"=87px
    # -------------------------------------------------------------------
    wre_name = shape("روما الغربية")    # 88 px
    ere_name = shape("روما الشرقية")    # 97 px
    sas_name = shape("الساسانيون")      # 87 px
    byz_name = shape("البيزنطيون")

    want["factions_screen_name_att_fact_western_roman_empire"]       = wre_name
    want["factions_screen_name_att_fact_eastern_roman_empire"]       = ere_name
    want["factions_screen_name_att_fact_sassanid_empire"]            = sas_name
    want["factions_screen_name_bel_fact_byzantine_empire"]           = byz_name

    # -------------------------------------------------------------------
    # 6. K51-K55 DIFFICULTY DESCRIPTIONS — wrap at 350 px, LF-joined
    # -------------------------------------------------------------------
    diff_texts = [
        "سهل: مناسب للمبتدئين وتجربة هادئة لاستكشاف اللعبة.",
        "عادي: تجربة متوازنة وتحدٍ استراتيجي معقول للجميع.",
        "صعب: يتطلب تخطيطاً دقيقاً وإدارة حازمة للجيوش والموارد.",
        "صعب جداً: خصوم أشداء ومكافآت كبرى لجيوش الأعداء.",
        "أسطوري: أعلى درجات المشقة والتحدي، وبدون إمكانية الحفظ اليدوي.",
    ]
    for i, txt in enumerate(diff_texts):
        lines, _ = wrap_multi(txt, c_lgi12, adv_lgi12, 350)
        want[f"random_localisation_strings_string_campaign_difficulty_description_{i}"] = "\n".join(lines)

    # -------------------------------------------------------------------
    # 7. LAND UNITS / UI UNIT STATS
    # -------------------------------------------------------------------
    want["land_units_onscreen_name_att_rom_legio"] = shape("فيلق روماني")

    for suffix, ar in [
        ("stat_melee_attack",          "هجوم الاشتباك"),
        ("stat_melee_defence",         "دفاع الاشتباك"),
        ("stat_armour",                "الدرع"),
        ("stat_health",                "الصحة"),
        ("stat_morale",                "المعنويات"),
        ("stat_speed",                 "السرعة"),
        ("stat_weapon_damage",         "ضرر السلاح"),
        ("stat_charge_bonus",          "مكافأة الهجوم"),
        ("stat_accuracy",              "الدقة"),
        ("stat_reloading",             "سرعة الإطلاق"),
        ("stat_ammo",                  "الذخيرة"),
        ("stat_weapon_range",          "المدى"),
        ("stat_men_count",             "عدد الجند"),
        ("stat_missile_block_chance",  "صد المقذوفات"),
        ("stat_missile_damage_ap",     "اختراق الدروع"),
        ("stat_melee_damage_ap",       "اختراق دروع الاشتباك"),
        ("stat_missile_damage_base",   "ضرر المقذوفات الأساسي"),
        ("stat_melee_damage_base",     "ضرر الاشتباك الأساسي"),
        ("stat_bonus_vs_cavalry",      "مكافأة ضد الفرسان"),
        ("stat_bonus_vs_infantry",     "مكافأة ضد المشاة"),
    ]:
        want[f"ui_unit_stats_onscreen_name_{suffix}"] = shape(ar)

    # -------------------------------------------------------------------
    # 8. RATING WORDS (ui_unit_bullet_point_enums.loc)
    #    INFERENCE: engine prepends rating left of stat name; pre-shaped
    #    Arabic rating on left reads RTL as "stat rating" which matches
    #    Arabic adjective-after-noun order.
    # -------------------------------------------------------------------
    for suffix, ar in [
        ("att_excellent",         "ممتاز"),
        ("att_good",              "جيد"),
        ("att_average_positive",  "متوسط"),
        ("att_average_negative",  "متوسط"),
        ("att_poor",              "ضعيف"),
        ("att_very_poor",         "ضعيف جداً"),
        ("att_high",              "مرتفع"),
        ("att_very_high",         "مرتفع جداً"),
        ("att_low",               "منخفض"),
        ("att_very_low",          "منخفض جداً"),
    ]:
        want[f"ui_unit_bullet_point_enums_onscreen_name_{suffix}"] = shape(ar)

    # -------------------------------------------------------------------
    # 9. FACTION DESCRIPTIONS — wrap at 310 px (georgia_italic_12), LF-joined
    #    WRE key = 2120156339 (unchanged)
    #    ERE key = 2120156326 (CORRECTED from v4's wrong 2120156889)
    # -------------------------------------------------------------------
    wre_logical = (
        "تقف الإمبراطورية الرومانية الغربية على شفا الانهيار والضياع. "
        "تنهش الحدود هجمات البرابرة المتواصلة، بينما ينخر الفساد السياسي والتمرد الداخلي في قلب الدولة. "
        "روما العظيمة لم تعد العاصمة، بل انتقل الحكم إلى ميديولانوم ورافينّا تحت وطأة التهديد. "
        "إن بقاء الإمبراطورية يتطلب قائداً حازماً يعيد الانضباط إلى الفيالق، ويثبت أركان الاقتصاد المتداعي، "
        "ويصد جحافل الغزاة قبل فوات الأوان."
    )

    # ERE description — uses the "unshackled" key found via phrase search
    ere_logical = (
        "انقسام الإمبراطورية الرومانية أطلق العنان للشرق، وأتاح له الإمساك بزمام العالم الروماني. "
        "عاصمتها القسطنطينية مهيبة الأسوار وعقدة التجارة العالمية، وخزائنها عامرة بالذهب. "
        "ومع ذلك، فإن الخطر يحيط بها من كل جانب؛ فالساسانيون يتربصون بالحدود الشرقية، "
        "والقبائل المهاجرة تهدد مقاطعات البلقان. "
        "إن الحفاظ على هذا الإرث العظيم يتطلب دبلوماسية بارعة، وحملات عسكرية حاسمة، وجيوشاً لا تلين."
    )

    wre_lines, _ = wrap_multi(wre_logical, c_geo12, adv_geo12, 310)
    ere_lines, _ = wrap_multi(ere_logical, c_geo12, adv_geo12, 310)
    wre_joined = "\n".join(wre_lines)
    ere_joined = "\n".join(ere_lines)

    want["start_pos_factions_description_2120156339"]      = wre_joined   # WRE
    want["start_pos_factions_long_description_2120156339"] = wre_joined
    want["start_pos_factions_description_2120156326"]      = ere_joined   # ERE (CORRECTED key)
    want["start_pos_factions_long_description_2120156326"] = ere_joined

    return want


def build_loc(log, fonts_dir):
    os.makedirs(LOC_BUILD, exist_ok=True)
    want = build_want(fonts_dir)
    log.append(f"Prepared {len(want)} Arabic strings")

    changed = {}
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        tmp = os.path.join(LOC_BUILD, "vanilla_" + leaf)
        run(VENV_PY, PACK_PY, "extract", COPY_PACK, internal, "--output", tmp)
        rows, pos, total = decode(open(tmp, "rb").read())
        assert pos == total, f"slack in {internal}"

        keys = {k for k, _, _ in rows}
        missing = [k for k in want if _owner(k) == internal and k not in keys]
        assert not missing, f"missing keys in {internal}: {missing}"

        out = []
        for k, t, tip in rows:
            if k in want and _owner(k) == internal:
                val = want[k]
                # Tab names, descriptions, and faction names are already shaped
                if (k.startswith("start_pos_factions_")
                        or k.startswith("faction_groups_")
                        or k.startswith("factions_screen_name_")
                        or k.startswith("random_localisation_")
                        or k.startswith("ui_unit_stats_")
                        or k.startswith("ui_unit_bullet_")):
                    shaped_val = val
                else:
                    shaped_val = shape(val)
                changed[k] = (t, shaped_val)
                out.append((k, shaped_val, tip))
            else:
                out.append((k, t, tip))

        data = encode(out)
        rows2, pos2, _ = decode(data)
        assert pos2 == len(data) and len(rows2) == len(rows)
        out_path = os.path.join(LOC_BUILD, leaf)
        with open(out_path, "wb") as fh:
            fh.write(data)

    log.append(f"Successfully modified {len(changed)} keys across {len(FILES)} loc files")

    tmp_pack = os.path.join(BASE, "build", "v6_loc_tmp.pack")
    run(VENV_PY, PACK_PY, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for internal in FILES:
        run(VENV_PY, PACK_PY, "add", tmp_pack, internal, os.path.join(LOC_BUILD, internal.split("\\")[-1]))
    run(VENV_PY, PACK_PY, "set-type", tmp_pack, "3", "--output", LOC_PACK)
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    log.append(f"Wrote loc pack: {LOC_PACK} ({os.path.getsize(LOC_PACK)} B, SHA256={sha256_file(LOC_PACK)})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log = []
    sha_before = sha256_file(VANILLA_PACK)
    assert sha_before == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch BEFORE: {sha_before}"
    log.append(f"Vanilla local_en.pack SHA256 verified BEFORE: {sha_before}")

    print("Step 1: Building v6 Arabic fonts (connecting-advance fix)...")
    build_fonts(log)

    print("Step 2: Building v6 loc tables (corrected key mapping)...")
    build_loc(log, FONTS_BUILD)

    sha_after = sha256_file(VANILLA_PACK)
    assert sha_after == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch AFTER: {sha_after}"
    log.append(f"Vanilla local_en.pack SHA256 verified AFTER: {sha_after}")

    print("Step 3: Running v3_check on v6 fonts...")
    check_out = run(
        VENV_PY,
        os.path.join(BASE, "source", "v3_check.py"),
        FONTS_BUILD,
        os.path.join(BASE, "localization", "corpus_v4.txt"),
    )
    log.append("=== v3_check output ===")
    log.append(check_out)

    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    log_path = os.path.join(BASE, "logs", "v6_build.txt")
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    print(f"Build complete. Log written to {log_path}")


if __name__ == "__main__":
    main()
