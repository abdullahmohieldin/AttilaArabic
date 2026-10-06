#!/usr/bin/env python3
"""Build v4 POC: connected vertical slice with full Arabic font set and
real Arabic strings (no ID prefixes).

Outputs:
  - build/v4fonts/*.cuf (31 merged fonts)
  - release/Attila_Arabic_POC_v4_fonts.pack
  - build/v4/*.loc (7 full-file loc copies)
  - release/Attila_Arabic_POC_v4.pack
  - docs/test-pack-manifest-v4.md
  - docs/composed-labels-design-note.md
  - localization/corpus_v4.txt
  - logs/v4_build.txt
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
from cuf import CUF  # noqa: E402
from loc import decode, encode  # noqa: E402
from shape import shape  # noqa: E402
from wrap import wrap_multi, wrap_single, visual_width  # noqa: E402

VENV_PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
PACK_PY = os.path.join(BASE, "tools", "packfile.py")
COPY_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
VANILLA_PACK = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"
TAJAWAL = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")

FONTS_BUILD = os.path.join(BASE, "build", "v4fonts")
LOC_BUILD = os.path.join(BASE, "build", "v4")
FONTS_PACK = os.path.join(BASE, "release", "Attila_Arabic_POC_v4_fonts.pack")
LOC_PACK = os.path.join(BASE, "release", "Attila_Arabic_POC_v4.pack")

SIZES_GIOC = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]
SIZES_GEORG = [10, 12, 14, 16, 18]
TARGETS = ([f"la_gioconda_{s}" for s in SIZES_GIOC]
           + [f"la_gioconda_uppercase_{s}" for s in SIZES_GIOC]
           + [f"georgia_italic_{s}" for s in SIZES_GEORG])

OVER = 2  # v3b_big setting

FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
    r"text\db\land_units.loc",
    r"text\db\faction_groups.loc",
    r"text\db\random_localisation_strings.loc",
    r"text\db\ui_unit_stats.loc",
]


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


_glyph_cache = {}


def render_glyph(px, char):
    key = (px, char)
    if key in _glyph_cache:
        return _glyph_cache[key]
    f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
    adv = int(round(f.getlength(char)))
    mask = f.getmask(char, mode="L")
    w, h = mask.size
    data = bytes(mask)
    xs = [x for y in range(h) for x in range(w) if data[y * w + x] > 0]
    ys = [y for y in range(h) for x in range(w) if data[y * w + x] > 0]
    if not xs:
        res = (b"", 0, 0, 0, 0, max(adv, 1))
        _glyph_cache[key] = res
        return res
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    ink = bytearray()
    for y in range(y0, y1 + 1):
        ink += data[y * w + x0:y * w + x1 + 1]
    iw = x1 - x0 + 1
    ih = y1 - y0 + 1
    # Combining marks with 0 advance treated as spacing marks
    adv_out = max(adv, iw)
    res = (bytes(ink), iw, ih, x0, y0, adv_out)
    _glyph_cache[key] = res
    return res


_cap_cache = {}


def cap_metrics(px):
    if px in _cap_cache:
        return _cap_cache[px]
    f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
    x0, y0, x1, y1 = f.getbbox("H")
    res = (y1 - y0, y0, y1)
    _cap_cache[px] = res
    return res


def calibrate(vanilla_h_cap, lo=8, hi=64):
    best, bestpx = None, None
    for px in range(lo, hi + 1):
        h, _, _ = cap_metrics(px)
        if best is None or abs(h - vanilla_h_cap) < best:
            best, bestpx = abs(h - vanilla_h_cap), px
    return bestpx


def vanilla_metrics(c):
    code = c.table[0x48]
    ah, aw, w, h = c.dims[code]
    d = c.bitmaps[code]
    rows = [y for y in range(h) if any(d[y * w + x] > 20 for x in range(w))]
    top, bottom = min(rows), max(rows)
    return {"cap": bottom - top + 1, "top": top, "bottom": bottom,
            "cell_h": h, "vsize": c.props["v_size"]}


def build_fonts(log):
    os.makedirs(FONTS_BUILD, exist_ok=True)
    cmap = TTFont(TAJAWAL).getBestCmap()

    # Full target sets
    target_cps = set()
    target_cps.update(range(0x0621, 0x064B))  # U+0621-064A
    target_cps.add(0x0640)  # tatweel
    target_cps.update(range(0x064B, 0x0653))  # harakat
    target_cps.add(0x0670)  # superscript alef
    target_cps.update([0x060C, 0x061B, 0x061F, 0x066A, 0x066B, 0x066C, 0x06D4])  # punctuation
    target_cps.update(range(0x0660, 0x066A))  # digits 0660-0669
    target_cps.update(range(0xFB50, 0xFE00))  # Forms-A
    target_cps.update(range(0xFE70, 0xFF00))  # Forms-B

    # Isolated Harakat Forms-B in Tajawal cmap have zero ink; map to combining bases
    decomp_harakat = {
        0xFE70: 0x064B, 0xFE72: 0x064C, 0xFE74: 0x064D, 0xFE76: 0x064E,
        0xFE78: 0x064F, 0xFE7A: 0x0650, 0xFE7C: 0x0651, 0xFE7E: 0x0652
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

    # Save corpus_v4.txt containing all merged Arabic codepoints
    corpus_v4_path = os.path.join(BASE, "localization", "corpus_v4.txt")
    with open(corpus_v4_path, "w", encoding="utf-8") as f:
        f.write("".join(chr(cp) for cp in sorted(src_of.keys())))

    for name in TARGETS:
        src = os.path.join(BASE, "extracted", "fonts", name + ".cuf")
        c = CUF.decode(open(src, "rb").read())
        assert c.bitmap_total() == c.size, name
        vm = vanilla_metrics(c)
        px_cap = calibrate(vm["cap"])
        V = vm["cell_h"]

        chosen, layouts = None, {}
        for px in range(px_cap, 7, -1):
            _, _, ty1 = cap_metrics(px)
            shift = vm["bottom"] - ty1
            ok, cur = True, {}
            for cp, ch in src_of.items():
                ink, iw, ih, x0, y0, adv = render_glyph(px, ch)
                top = y0 + shift
                if not ink or top < -OVER or top + ih > V + OVER:
                    ok = False
                    break
                cur[cp] = (ink, iw, ih, x0, y0, adv)
            if ok:
                chosen, layouts = (px, shift), cur
                break

        assert chosen is not None, f"{name}: no fitting px"
        px, shift = chosen

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
            ink, iw, ih, x0, y0, adv = layouts[cp]
            top = y0 + shift
            ctop = min(top, 0)
            cbot = max(top + ih, V)
            chh = cbot - ctop
            left = x0 if x0 >= 0 else 0
            cw = max(adv, left + iw)
            cell = bytearray(chh * cw)
            for y in range(ih):
                a = (top - ctop + y) * cw + left
                b = a + iw
                cell[a:b] = ink[y * iw:(y + 1) * iw]
            code = len(new_dims)
            new_dims.append((chh if chh < 128 else 127, min(adv, 255), cw, chh))
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
        with open(out_path, "wb") as f:
            f.write(out)

        maxh = max(h for (_, _, _, h) in new_dims[len(new_dims) - len(added):])
        log.append(f"{name}: px={px} cell={V} maxcell={maxh} vanilla_codes={len(c.dims) - len(added) - len(dangling)} "
                   f"+blanks={len(dangling)} +arabic={len(added)} size={len(out)}B")

    # Package into fonts pack
    tmp_pack = os.path.join(BASE, "build", "v4_fonts_tmp.pack")
    run(VENV_PY, PACK_PY, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in TARGETS:
        run(VENV_PY, PACK_PY, "add", tmp_pack, f"font\\{name}.cuf", os.path.join(FONTS_BUILD, f"{name}.cuf"))
    run(VENV_PY, PACK_PY, "set-type", tmp_pack, "3", "--output", FONTS_PACK)
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    log.append(f"Wrote fonts pack: {FONTS_PACK} ({os.path.getsize(FONTS_PACK)} B, SHA256={sha256_file(FONTS_PACK)})")


def build_want():
    """Real Arabic sentences, no ID prefixes, covering all requested UI scopes."""
    want = {}
    U = "uied_component_texts_localised_string_"

    # 1. Battles Menu
    want[U + "string_NewState_Text_250075x"] = "المعارك التاريخية"
    want[U + "tx_title_mp_Text_250075"] = "معركة مخصصة"
    want[U + "button_txt_NewState_Text_250075"] = "معركة سريعة"
    want[U + "button_txt_NewState_Text_430007"] = "رجوع"
    want[U + "button_txt_NewState_Text_380007"] = "القائمة الرئيسية"

    # 2. Campaigns Menu
    want[U + "string_NewState_Text_3a000c"] = "الحملة الكبرى"
    want[U + "string_NewState_Text_3a000cm"] = "المقدمة التعليمية"
    want[U + "button_txt_NewState_Text_36000f"] = "حملة جديدة"
    want[U + "button_txt_NewState_Text_36000fs"] = "متابعة الحملة"
    want[U + "string_continue_campaign_Text_380007"] = "متابعة الحملة"
    want[U + "string_NewState_Text_460009"] = "تحميل حملة"
    want[U + "heading_tx_NewState_Text_460009j"] = "حملة متعددة اللاعبين"
    want[U + "string_NewState_Text_1d002f"] = "خيارات"
    want[U + "string_NewState_Text_180007"] = "العودة"

    # 3. Custom Battle (Titles, Labels, Buttons)
    want[U + "tx_header_NewState_Text_530011"] = "معركة مخصصة"
    want[U + "button_txt_NewState_Text_530011"] = "بدء المعركة"
    want[U + "string_NewState_Text_530011"] = "اختيار الجيوش"
    want[U + "button_txt_NewState_Text_530011h"] = "إعدادات المعركة"
    want[U + "button_txt_NewState_Text_530011r"] = "إعادة التعيين"
    want[U + "string_active_Text_c0020"] = "الجيش المهاجم"
    want[U + "string_active_Text_3b"] = "الجيش المدافع"
    want["land_units_onscreen_name_att_rom_legio"] = "فيلق روماني"

    # Unit Info Stat Names (ui_unit_stats.loc)
    want["ui_unit_stats_onscreen_name_stat_melee_attack"] = "هجوم الاشتباك"
    want["ui_unit_stats_onscreen_name_stat_melee_defence"] = "دفاع الاشتباك"
    want["ui_unit_stats_onscreen_name_stat_armour"] = "الدرع"
    want["ui_unit_stats_onscreen_name_stat_health"] = "الصحة"
    want["ui_unit_stats_onscreen_name_stat_morale"] = "المعنويات"
    want["ui_unit_stats_onscreen_name_stat_speed"] = "السرعة"
    want["ui_unit_stats_onscreen_name_stat_weapon_damage"] = "ضرر السلاح"
    want["ui_unit_stats_onscreen_name_stat_charge_bonus"] = "مكافأة الهجوم"
    want["ui_unit_stats_onscreen_name_stat_accuracy"] = "الدقة"
    want["ui_unit_stats_onscreen_name_stat_reloading"] = "سرعة الإطلاق"
    want["ui_unit_stats_onscreen_name_stat_ammo"] = "الذخيرة"
    want["ui_unit_stats_onscreen_name_stat_weapon_range"] = "المدى"
    want["ui_unit_stats_onscreen_name_stat_men_count"] = "عدد الجند"
    want["ui_unit_stats_onscreen_name_stat_missile_block_chance"] = "صد المقذوفات"
    want["ui_unit_stats_onscreen_name_stat_missile_damage_ap"] = "اختراق الدروع"
    want["ui_unit_stats_onscreen_name_stat_melee_damage_ap"] = "اختراق دروع الاشتباك"
    want["ui_unit_stats_onscreen_name_stat_missile_damage_base"] = "ضرر المقذوفات الأساسي"
    want["ui_unit_stats_onscreen_name_stat_melee_damage_base"] = "ضرر الاشتباك الأساسي"
    want["ui_unit_stats_onscreen_name_stat_bonus_vs_cavalry"] = "مكافأة ضد الفرسان"
    want["ui_unit_stats_onscreen_name_stat_bonus_vs_infantry"] = "مكافأة ضد المشاة"

    # 4. Faction Selection (Header, Group tabs, Labels, Difficulty text, Buttons)
    want[U + "header_faction_NewState_Text_410063"] = "اختر الفصيل"
    want[U + "header_cultural_NewState_Text_5e0000"] = "السمات الثقافية"
    want[U + "tx_header_NewState_Text_b0036"] = "تفاصيل الفصيل"

    # Group tabs (faction_groups.loc)
    want["faction_groups_name_localised_att_fact_group_roman"] = "الإمبراطوريات الرومانية"
    want["faction_groups_name_localised_att_fact_group_eastern"] = "الممالك الشرقية"
    want["faction_groups_name_localised_att_fact_group_nomadic"] = "القبائل البدوية"
    want["faction_groups_name_localised_att_fact_group_barbarian"] = "الممالك البربرية"
    want["faction_groups_name_localised_att_fact_group_barbarian_m"] = "القبائل المهاجرة"
    want["faction_groups_name_localised_att_fact_group_sand"] = "ممالك الصحراء"

    # Faction names (factions.loc)
    # Closed dropdown is ~135 px wide; truncated at logical end with ellipsis
    c_drop, adv_drop = CUF.decode(open(os.path.join(FONTS_BUILD, "la_gioconda_12.cuf"), "rb").read()), {}
    for cidx in range(len(c_drop.dims)):
        adv_drop[cidx] = c_drop.dims[cidx][1]

    wre_name = "الإمبراطورية الرومانية الغربية"
    ere_name = "الإمبراطورية الرومانية الشرقية"
    sas_name = "الإمبراطورية الساسانية"

    # Truncate ERE name with wrap_single for 135px dropdown test
    v_ere_drop, dropped_ere = wrap_single(ere_name, c_drop, adv_drop, 135)

    want["factions_screen_name_att_fact_western_roman_empire"] = wre_name
    want["factions_screen_name_att_fact_eastern_roman_empire"] = v_ere_drop
    want["factions_screen_name_att_fact_sassanid_empire"] = sas_name
    want["factions_screen_name_bel_fact_byzantine_empire"] = "الإمبراطورية البيزنطية"

    # Labels
    want[U + "year_txt_NewState_Text_310044"] = "السنة"
    want[U + "year_tx_NewState_Text_310064"] = "395 م"
    want[U + "tx_initial_challenge:_NewState_Text_670040"] = "التحدي المبدئي:"
    want[U + "tx_difficulty_NewState_Text_79004a"] = "صعوبة الحملة"
    want[U + "heading_tx_NewState_Text_79004a"] = "قائد الفصيل"
    want[U + "tx_culture_NewState_Text_b0036"] = "الثقافة"
    want[U + "region_religion_Tooltip_b0036"] = "دين الإقليم"
    want[U + "religion_Tooltip_b0036"] = "دين الدولة"

    # Difficulty descriptions (random_localisation_strings.loc)
    want["random_localisation_strings_string_campaign_difficulty_description_0"] = (
        "سهل: مناسب للمبتدئين وتجربة هادئة لاستكشاف اللعبة."
    )
    want["random_localisation_strings_string_campaign_difficulty_description_1"] = (
        "عادي: تجربة متوازنة وتحدٍ استراتيجي معقول للجميع."
    )
    want["random_localisation_strings_string_campaign_difficulty_description_2"] = (
        "صعب: يتطلب تخطيطاً دقيقاً وإدارة حازمة للجيوش والموارد."
    )
    want["random_localisation_strings_string_campaign_difficulty_description_3"] = (
        "صعب جداً: خصوم أشداء ومكافآت كبرى لجيوش الأعداء."
    )
    want["random_localisation_strings_string_campaign_difficulty_description_4"] = (
        "أسطوري: أعلى درجات المشقة والتحدي، وبدون إمكانية الحفظ اليدوي."
    )

    # Buttons
    want[U + "button_txt_NewState_Text_700030"] = "بدء الحملة"
    want[U + "string_NewState_Text_700030"] = "بدء الحملة"
    want[U + "button_txt_NewState_Text_23001bb"] = "رجوع"
    want[U + "button_txt_NewState_Text_30006e"] = "خيارات الحملة"

    # Tooltips
    want[U + "handle_Tooltip_7000b"] = "مستوى صعوبة الحملة"
    want[U + "cmp_diff_slider_Tooltip_7000b"] = "تعديل مستوى الصعوبة"
    want[U + "medal1_default_Tooltip_5003a"] = "مستوى الصعوبة: صعب"
    want[U + "StatusIcon_Wavering_Tooltip_a003d"] = "الروح المعنوية: متزعزعة"

    # 5. Faction Descriptions (WRE + ERE)
    # Using source/wrap.py with exact CUF metrics at width 400px
    # Newlines test: WRE uses LF (\n), ERE uses CRLF (\r\n)
    c_desc = CUF.decode(open(os.path.join(FONTS_BUILD, "georgia_italic_12.cuf"), "rb").read())
    adv_desc = {cidx: c_desc.dims[cidx][1] for cidx in range(len(c_desc.dims))}

    wre_logical = (
        "تقف الإمبراطورية الرومانية الغربية على شفا الانهيار والضياع. "
        "تنهش الحدود هجمات البرابرة المتواصلة، بينما ينخر الفساد السياسي والتمرد الداخلي في قلب الدولة. "
        "روما العظيمة لم تعد العاصمة، بل انتقل الحكم إلى ميديولانوم ورافينّا تحت وطأة التهديد. "
        "إن بقاء الإمبراطورية يتطلب قائداً حازماً يعيد الانضباط إلى الفيالق، ويثبت أركان الاقتصاد المتداعي، "
        "ويصد جحافل الغزاة قبل فوات الأوان."
    )

    ere_logical = (
        "تعتبر الإمبراطورية الرومانية الشرقية الحصن المنيع في وجه عواصف العصر. "
        "عاصمتها القسطنطينية مهيبة الأسوار وعقدة التجارة العالمية، وخزائنها عامرة بالذهب. "
        "ومع ذلك، فإن الخطر يحيط بها من كل جانب؛ فالساسانيون يتربصون بالحدود الشرقية، "
        "والقبائل المهاجرة تهدد مقاطعات البلقان. "
        "إن الحفاظ على هذا الإرث العظيم يتطلب دبلوماسية بارعة، وحملات عسكرية حاسمة، وجيوشاً لا تلين."
    )

    wre_lines, _ = wrap_multi(wre_logical, c_desc, adv_desc, 400)
    ere_lines, _ = wrap_multi(ere_logical, c_desc, adv_desc, 400)

    # Pre-shaped and joined with LF (\n) for WRE
    wre_joined_lf = "\n".join(wre_lines)
    # Pre-shaped and joined with CRLF (\r\n) for ERE
    ere_joined_crlf = "\r\n".join(ere_lines)

    want["start_pos_factions_description_2120156339"] = wre_joined_lf
    want["start_pos_factions_long_description_2120156339"] = wre_joined_lf
    want["start_pos_factions_description_2120156889"] = ere_joined_crlf
    want["start_pos_factions_long_description_2120156889"] = ere_joined_crlf

    return want


def _owner(k):
    for prefix, f in [("uied_", 0), ("factions_", 1), ("start_pos_", 2),
                      ("land_units_", 3), ("faction_groups_", 4),
                      ("random_localisation_", 5), ("ui_unit_stats_", 6)]:
        if k.startswith(prefix):
            return FILES[f]
    raise AssertionError(k)


def build_loc(log):
    os.makedirs(LOC_BUILD, exist_ok=True)
    want = build_want()
    log.append(f"Prepared {len(want)} real Arabic strings (no ID prefixes)")

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
                # Faction descriptions and pre-wrapped dropdown string are already shaped
                if k.startswith("start_pos_factions_") or k == "factions_screen_name_att_fact_eastern_roman_empire":
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
        with open(out_path, "wb") as f:
            f.write(data)

    log.append(f"Successfully modified {len(changed)} keys across 7 loc files")

    # Package into loc pack
    tmp_pack = os.path.join(BASE, "build", "v4_loc_tmp.pack")
    run(VENV_PY, PACK_PY, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for internal in FILES:
        run(VENV_PY, PACK_PY, "add", tmp_pack, internal, os.path.join(LOC_BUILD, internal.split("\\")[-1]))
    run(VENV_PY, PACK_PY, "set-type", tmp_pack, "3", "--output", LOC_PACK)
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    log.append(f"Wrote loc pack: {LOC_PACK} ({os.path.getsize(LOC_PACK)} B, SHA256={sha256_file(LOC_PACK)})")


def main():
    log = []
    # Rule: Hash vanilla BEFORE build
    sha_before = sha256_file(VANILLA_PACK)
    assert sha_before == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch before build: {sha_before}"
    log.append(f"Vanilla local_en.pack SHA256 verified BEFORE build: {sha_before}")

    print("Step 1.1: Building v4 full Arabic fonts...")
    build_fonts(log)

    print("Step 1.2: Building v4 loc tables...")
    build_loc(log)

    # Rule: Hash vanilla AFTER build
    sha_after = sha256_file(VANILLA_PACK)
    assert sha_after == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch after build: {sha_after}"
    log.append(f"Vanilla local_en.pack SHA256 verified AFTER build: {sha_after}")

    # Run v3_check on v4 fonts
    print("Step 1.3: Running v3_check on v4 fonts...")
    check_out = run(VENV_PY, os.path.join(BASE, "source", "v3_check.py"),
                    FONTS_BUILD, os.path.join(BASE, "localization", "corpus_v4.txt"))
    log.append("=== v3_check output ===")
    log.append(check_out)

    log_path = os.path.join(BASE, "logs", "v4_build.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print(f"Build complete. Log written to {log_path}")


if __name__ == "__main__":
    main()
