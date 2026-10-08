#!/usr/bin/env python3
"""Build v8 POC: per-glyph width tax (R*), 1px join overlap, yeh dot boost, ruler pack.

Changes vs v6/v7 (v6/v7 files untouched):
  FONTS (v8fonts):
    - Connecting-form advance: adv = ink_width - 1 (1px overlap), left=0 (same as v7).
    - Yeh dot boost (INFERENCE): U+FEF1/U+FEF2/U+064A alpha x1.6 capped 255.
    - All other placement identical to v6 (baseline-row aligned).

  LOC (v8.pack + v8_ruler.pack):
    1. Same screen-verified key mapping as v6.
    2. Width model R* (INFERENCE from 6-line fit ≤1.1%):
       - georgia_italic_12: every ADDED Arabic glyph +2.48 px (space=4, Latin unchanged)
       - la_gioconda_12: every ADDED Arabic glyph +1.32 px (space=5, Latin unchanged)
    3. Wrap at model px equivalent of engine ~280 px:
       - descriptions (geo12): wrap at 280 model px (engine ~320)
       - difficulty (lgi12): wrap at 280 model px (engine ~350)
    4. Right-align probe (UNVERIFIED: engine may trim leading spaces):
       - WRE/ERE desc lines padded to min(280, engine_cap) model px
       - Unit Info labels padded to longest label in list, cap engine width
       - Centered text NOT padded.
    4. Ruler pack (loc-only): ERE desc key + Hard diff key with
       20×medial beh, 20×isolated alef, isolated alef + 20 spaces + isolated alef.

Outputs:
  - build/v8fonts/*.cuf
  - release/Attila_Arabic_POC_v8_fonts.pack
  - release/Attila_Arabic_POC_v8.pack
  - release/Attila_Arabic_POC_v8_ruler.pack (loc-only)
  - logs/v8_build.txt
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

FONTS_BUILD = os.path.join(BASE, "build", "v8fonts")
LOC_BUILD   = os.path.join(BASE, "build", "v8")
FONTS_PACK  = os.path.join(BASE, "release", "Attila_Arabic_POC_v8_fonts.pack")
LOC_PACK    = os.path.join(BASE, "release", "Attila_Arabic_POC_v8.pack")
RULER_PACK  = os.path.join(BASE, "release", "Attila_Arabic_POC_v8_ruler.pack")

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

            # --- v7 CONNECTING-ADVANCE: 1px overlap ---
            # For Initial, Medial, Final forms and Tatweel:
            #   left = 0, adv_out = ink_width - 1 (min 1).
            # Cell width stays ink_width; advance overlaps 1px so strokes
            # touch even with antialiased edges.
            if is_connecting_cp(cp):
                left = 0
                cw = mw
                adv_out = max(mw - 1, 1)
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

            # --- v7 YEH DOT BOOST (INFERENCE) ---
            # Tajawal Yeh dots rasterize faint (alpha 30-150); the engine
            # appears to drop them, leaving Alef-Maksura look. Boost Yeh
            # family ink so dots survive. Source strings already use U+064A.
            if cp in (0xFEF1, 0xFEF2, 0x064A, 0xFEF3, 0xFEF4):
                cell = bytearray(min(255, int(b * 1.6) if b else 0) for b in cell)

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
    tmp_pack = os.path.join(BASE, "build", "v8_fonts_tmp.pack")
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


# R* width model (INFERENCE from 6-line fit ≤1.1%):
#   georgia_italic_12: every ADDED Arabic glyph (code >= geo12_vanilla_count) gets +2.48 px
#   la_gioconda_12: every ADDED Arabic glyph (code >= lgi12_vanilla_count) gets +1.32 px
# Space advance unchanged (4 / 5). Latin glyphs unchanged.
# For wrapping: visual_width(visual) = base_adv_sum + n_added * K_font

def visual_width_rstar(visual, c, adv, vanilla_count, k_geo):
    """R* model width: base advance sum + per-added-glyph tax."""
    total = 0
    for ch in visual:
        cp = ord(ch)
        code = c.table[cp] if cp < 65536 else 0xFFFF
        if code == 0xFFFF or code >= len(c.dims):
            total += adv[c.table[0x20]]  # space fallback
        else:
            total += adv[code]
            if code >= vanilla_count:
                total += k_geo
    return total


def pad_right_align_rstar(visual_line, c, adv, vanilla_count, k_font, width, log, label, engine_cap):
    """Prepend spaces to reach model width, capped at engine_cap real px."""
    w = visual_width_rstar(visual_line, c, adv, vanilla_count, k_font)
    space_adv = adv[c.table[0x20]]
    # target is min(width, engine_cap) in model px
    target = min(width, engine_cap)
    n = int(max((target - w) // space_adv, 0))
    padded = " " * n + visual_line
    w2 = visual_width_rstar(padded, c, adv, vanilla_count, k_font)
    assert w2 <= target, f"{label}: padded {w2} > {target}"
    log.append(f"PAD {label}: model_w={w} space_adv={space_adv} n={n} target={target} model_padded={w2}")
    return padded


def wrap_multi_rstar(logical, c, adv, vanilla_count, k_font, width):
    """R* greedy word wrap using visual_width_rstar."""
    lines = []
    cur = []
    for word in logical.split(" "):
        cand = " ".join(cur + [word]) if cur else word
        v = shape(cand)
        w = visual_width_rstar(v, c, adv, vanilla_count, k_font)
        if w <= width or not cur:
            cur.append(word)
        else:
            lines.append(shape(" ".join(cur)))
            cur = [word]
    if cur:
        lines.append(shape(" ".join(cur)))
    return lines


def build_want(fonts_dir, log=None):
    """
    Arabic strings keyed by FULL vanilla key.
    Same screen-verified key mapping as v6; wrap at 280 px (v7).
    """
    want = {}
    pad_log = [] if log is None else log
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
    # 6. DIFFICULTY DESCRIPTIONS — v8: R* model, lgi12 +1.32/ar-glyph, wrap 280
    #    Centered text NOT padded.
    # -------------------------------------------------------------------
    diff_texts = [
        "سهل: مناسب للمبتدئين وتجربة هادئة لاستكشاف اللعبة.",
        "عادي: تجربة متوازنة وتحدٍ استراتيجي معقول للجميع.",
        "صعب: يتطلب تخطيطاً دقيقاً وإدارة حازمة للجيوش والموارد.",
        "صعب جداً: خصوم أشداء ومكافآت كبرى لجيوش الأعداء.",
        "أسطوري: أعلى درجات المشقة والتحدي، وبدون إمكانية الحفظ اليدوي.",
    ]
    lgi12_vanilla = len(CUF.decode(open(os.path.join(BASE, "extracted", "fonts", "la_gioconda_12.cuf"), "rb").read()).dims)
    for i, txt in enumerate(diff_texts):
        lines = wrap_multi_rstar(txt, c_lgi12, adv_lgi12, lgi12_vanilla, 1.32, 280)
        wlist = [visual_width_rstar(l, c_lgi12, adv_lgi12, lgi12_vanilla, 1.32) for l in lines]
        pad_log.append(f"WRAP diff_{i}: {len(lines)} lines " +
                       ", ".join(str(w) for w in wlist) + "/280")
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
    # v8 right-align probe on two Unit Info labels (R* model, cap at engine width).
    # Longest label in list is reference; pad each to that width.
    lgi12_vanilla = len(CUF.decode(open(os.path.join(BASE, "extracted", "fonts", "la_gioconda_12.cuf"), "rb").read()).dims)
    unit_labels = [("stat_melee_attack", "هجوم الاشتباك"), ("stat_armour", "الدرع")]
    # measure model widths of all labels
    label_widths = {}
    for suffix, ar in unit_labels:
        v = shape(ar)
        w = visual_width_rstar(v, c_lgi12, adv_lgi12, lgi12_vanilla, 1.32)
        label_widths[suffix] = w
    max_w = max(label_widths.values())
    engine_cap_lgi12 = 350  # engine real width for lgi12 difficulty
    for suffix, ar in unit_labels:
        _k = f"ui_unit_stats_onscreen_name_{suffix}"
        v = shape(ar)
        want[_k] = pad_right_align_rstar(v, c_lgi12, adv_lgi12, lgi12_vanilla, 1.32, max_w, pad_log, suffix, engine_cap_lgi12)

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
    # 9. FACTION DESCRIPTIONS — v8: R* model, geo12 +2.48/ar-glyph, wrap 280
    #    right-align probe (leading spaces), cap at engine width.
    #    WRE key = 2120156339, ERE key = 2120156326 (same as v6).
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

    geo12_vanilla = len(CUF.decode(open(os.path.join(BASE, "extracted", "fonts", "georgia_italic_12.cuf"), "rb").read()).dims)
    engine_cap_geo12 = 320  # engine real width for geo12 description panel

    wre_lines = wrap_multi_rstar(wre_logical, c_geo12, adv_geo12, geo12_vanilla, 2.48, 280)
    ere_lines = wrap_multi_rstar(ere_logical, c_geo12, adv_geo12, geo12_vanilla, 2.48, 280)

    wre_w = [visual_width_rstar(l, c_geo12, adv_geo12, geo12_vanilla, 2.48) for l in wre_lines]
    ere_w = [visual_width_rstar(l, c_geo12, adv_geo12, geo12_vanilla, 2.48) for l in ere_lines]
    pad_log.append(f"WRAP WRE: {len(wre_lines)} lines " + ", ".join(str(w) for w in wre_w) + "/280")
    pad_log.append(f"WRAP ERE: {len(ere_lines)} lines " + ", ".join(str(w) for w in ere_w) + "/280")

    wre_lines = [pad_right_align_rstar(l, c_geo12, adv_geo12, geo12_vanilla, 2.48, 280, pad_log, f"WRE_L{i}", engine_cap_geo12)
                 for i, l in enumerate(wre_lines)]
    ere_lines = [pad_right_align_rstar(l, c_geo12, adv_geo12, geo12_vanilla, 2.48, 280, pad_log, f"ERE_L{i}", engine_cap_geo12)
                 for i, l in enumerate(ere_lines)]
    wre_joined = "\n".join(wre_lines)
    ere_joined = "\n".join(ere_lines)

    want["start_pos_factions_description_2120156339"]      = wre_joined   # WRE
    want["start_pos_factions_long_description_2120156339"] = wre_joined
    want["start_pos_factions_description_2120156326"]      = ere_joined   # ERE (CORRECTED key)
    want["start_pos_factions_long_description_2120156326"] = ere_joined

    return want


def build_loc(log, fonts_dir):
    os.makedirs(LOC_BUILD, exist_ok=True)
    want = build_want(fonts_dir, log)
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

    tmp_pack = os.path.join(BASE, "build", "v8_loc_tmp.pack")
    run(VENV_PY, PACK_PY, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for internal in FILES:
        run(VENV_PY, PACK_PY, "add", tmp_pack, internal, os.path.join(LOC_BUILD, internal.split("\\")[-1]))
    run(VENV_PY, PACK_PY, "set-type", tmp_pack, "3", "--output", LOC_PACK)
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    log.append(f"Wrote loc pack: {LOC_PACK} ({os.path.getsize(LOC_PACK)} B, SHA256={sha256_file(LOC_PACK)})")

    # Ruler pack (loc-only) — 3 test strings for geo12 + lgi12 advance measurement
    # Keys: ERE desc (geo12) + Hard diff (lgi12)
    ruler_log = []
    # ERE desc key
    ere_key = "start_pos_factions_description_2120156326"
    # Hard diff key
    hard_key = "random_localisation_strings_string_campaign_difficulty_description_2"
    # Test strings
    ruler_strings = {
        ere_key: {
            "ruler_beh20": "بببببببببببببببببببب",  # 20× medial beh U+FE92
            "ruler_alef20": "أأأأأأأأأأأأأأأأأأأأ",  # 20× isolated alef U+FE8D
            "ruler_alef_sp_alef": "أ" + " " * 20 + "أ",  # isolated alef + 20 spaces + isolated alef
        },
        hard_key: {
            "ruler_beh20": "بببببببببببببببببببب",  # 20× medial beh U+FE92
            "ruler_alef20": "أأأأأأأأأأأأأأأأأأأأ",  # 20× isolated alef U+FE8D
            "ruler_alef_sp_alef": "أ" + " " * 20 + "أ",
        },
    }
    # Build ruler want dict using same R* model
    ruler_want = {}
    for k, variants in ruler_strings.items():
        for tag, txt in variants.items():
            ruler_want[f"{k}_{tag}"] = txt

    # Create ruler pack
    tmp_ruler = os.path.join(BASE, "build", "v8_ruler_tmp.pack")
    run(VENV_PY, PACK_PY, "create", tmp_ruler, "--type", "3", "--version", "PFH4")
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        tmp = os.path.join(LOC_BUILD, "vanilla_" + leaf)
        rows, pos, total = decode(open(tmp, "rb").read())
        assert pos == total
        out = []
        for k, t, tip in rows:
            if k in ruler_want and _owner(k) == internal:
                val = ruler_want[k]
                shaped_val = val
                out.append((k, shaped_val, tip))
            else:
                out.append((k, t, tip))
        data = encode(out)
        out_path = os.path.join(LOC_BUILD, leaf + ".ruler")
        with open(out_path, "wb") as fh:
            fh.write(data)
        run(VENV_PY, PACK_PY, "add", tmp_ruler, internal, out_path)
    run(VENV_PY, PACK_PY, "set-type", tmp_ruler, "3", "--output", RULER_PACK)
    if os.path.exists(tmp_ruler):
        os.remove(tmp_ruler)
    log.append(f"Wrote ruler pack: {RULER_PACK} ({os.path.getsize(RULER_PACK)} B, SHA256={sha256_file(RULER_PACK)})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log = []
    sha_before = sha256_file(VANILLA_PACK)
    assert sha_before == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch BEFORE: {sha_before}"
    log.append(f"Vanilla local_en.pack SHA256 verified BEFORE: {sha_before}")

    print("Step 1: Building v8 Arabic fonts (1px overlap + yeh boost)...")
    build_fonts(log)

    print("Step 2: Building v8 loc tables (R* model wrap + right-align probe)...")
    build_loc(log, FONTS_BUILD)

    sha_after = sha256_file(VANILLA_PACK)
    assert sha_after == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch AFTER: {sha_after}"
    log.append(f"Vanilla local_en.pack SHA256 verified AFTER: {sha_after}")

    print("Step 3: Running v3_check on v8 fonts...")
    check_out = run(
        VENV_PY,
        os.path.join(BASE, "source", "v3_check.py"),
        FONTS_BUILD,
        os.path.join(BASE, "localization", "corpus_v4.txt"),
    )
    log.append("=== v3_check output ===")
    log.append(check_out)

    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    log_path = os.path.join(BASE, "logs", "v8_build.txt")
    with open(log_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    print(f"Build complete. Log written to {log_path}")


if __name__ == "__main__":
    main()
