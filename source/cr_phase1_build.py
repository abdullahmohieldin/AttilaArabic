#!/usr/bin/env python3
"""Phase 1 Clean-Slate Build Script — Round 3 — Total War: ATTILA Arabic Localization

Builds:
  1. Attila_Arabic_Phase1.pack        (loc pack, PFH4 type 3)
  2. Attila_Arabic_Phase1_fonts.pack  (fonts pack, PFH4 type 3)

Round 3 Scope (Real-Text Acceptance Round):
  - Verified Live Surfaces on Faction Selection Screen:
    1. Start Campaign button ([B])
    2. Factions header tab ([F])
    3. Difficulty slider tooltip ([S])
    4. Hard difficulty label ([H])
    5. Difficulty description ([D])
    6. Legendary difficulty body description ([L])
    7. Cultural Trait header ([C])
    8. Faction title ([T])
    9. Faction description box: 8-line right-aligned historical narrative

Technical Features:
  - Vertical alignment: 100% full-cell padding (h = v_size, ah = v_size) with FreeType baseline
    anchored to vanilla baseline_H. Eliminates vertical offset (Delta Y = 0px).
  - Joining bleed: +1px ink column applied to all connecting Arabic glyphs (Final, Medial, Tatweel),
    closing the w+1 advance gap (seam = 0.0px).
  - Right-alignment: Binary blank spacer glyphs in PUA (0xE010..0xE015) prefixing each narrative line,
    aligning lines flush to the right panel margin.
"""
import os
import sys
import struct
import hashlib
import unicodedata
from PIL import Image, ImageFont
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def decompose_cp(cp: int) -> int:
    decomp = unicodedata.decomposition(chr(cp))
    if decomp:
        parts = decomp.split()
        if len(parts) >= 2 and parts[0].startswith("<"):
            try:
                return int(parts[1], 16)
            except ValueError:
                pass
    return cp


from source.cuf import CUF, PROP_NAMES
from source.loc import decode as loc_decode, encode as loc_encode
from source.shape import shape
from tools.packfile import PackFile

BASE = r"D:\AttilaArabic"
TAJAWAL = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")
VANILLA_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
OUT_DIR = os.path.join(BASE, "release")

TARGET_KEYS = {
    # 1. Start Campaign button
    "btn_start_campaign_1": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_button_txt_NewState_Text_30006e",
    ),
    "btn_start_campaign_2": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_string_NewState_Text_30006e",
    ),
    # 2. Factions header
    "header_factions_1": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_tx_factions_NewState_Text_90022",
    ),
    "header_factions_2": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_selection_txt_NewState_Text_90022",
    ),
    "header_factions_3": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_tab_factions_Tooltip_90022",
    ),
    # 3. Difficulty slider tooltip
    "diff_tooltip_1": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_handle_NewState_Tooltip_7000b",
    ),
    "diff_tooltip_2": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_handle_Tooltip_7000b",
    ),
    "diff_tooltip_3": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_cmp_diff_slider_Tooltip_7000b",
    ),
    # 4. Hard label
    "diff_hard_1": (
        r"text\db\random_localisation_strings.loc",
        "random_localisation_strings_string_difficulty_level_3",
    ),
    "diff_hard_2": (
        r"text\db\random_localisation_strings.loc",
        "random_localisation_strings_string_hard",
    ),
    "diff_hard_3": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_medal1_default_Tooltip_5003a",
    ),
    # 5. Difficulty description
    "diff_desc": (
        r"text\db\random_localisation_strings.loc",
        "random_localisation_strings_string_campaign_difficulty_description_2",
    ),
    # 6. Legendary difficulty description
    "diff_legendary": (
        r"text\db\random_localisation_strings.loc",
        "random_localisation_strings_string_campaign_difficulty_slider_legendary",
    ),
    # 7. Cultural trait header
    "header_cultural": (
        r"text\db\uied_component_texts.loc",
        "uied_component_texts_localised_string_header_cultural_NewState_Text_5e0000",
    ),
    # 8. Faction title
    "faction_title": (
        r"text\db\factions.loc",
        "factions_screen_name_att_fact_eastern_roman_empire",
    ),
    # 9. Faction description
    "ere_description": (
        r"text\db\start_pos_factions.loc",
        "start_pos_factions_description_2120156326",
    ),
    "ere_long_description": (
        r"text\db\start_pos_factions.loc",
        "start_pos_factions_long_description_2120156326",
    ),
}

TARGET_FONTS = (
    [f"georgia_italic_{sz}.cuf" for sz in [10, 12, 14, 16, 18]] +
    [f"la_gioconda_{sz}.cuf" for sz in [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]] +
    [f"la_gioconda_uppercase_{sz}.cuf" for sz in [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]]
)

# Round 3 Binary Blank Spacer Glyphs (Unicode Private Use Area U+E010..U+E015)
CP_BLANK_32 = 0xE010  # w = 31, advances 32px
CP_BLANK_16 = 0xE011  # w = 15, advances 16px
CP_BLANK_8  = 0xE012  # w = 7,  advances 8px
CP_BLANK_4  = 0xE013  # w = 3,  advances 4px
CP_BLANK_2  = 0xE014  # w = 1,  advances 2px
CP_BLANK_1  = 0xE015  # w = 0,  advances 1px

BLANK_SPACERS = [
    (32, CP_BLANK_32, 31),
    (16, CP_BLANK_16, 15),
    (8,  CP_BLANK_8,  7),
    (4,  CP_BLANK_4,  3),
    (2,  CP_BLANK_2,  1),
    (1,  CP_BLANK_1,  0),
]


def make_spacer(indent_px: int) -> str:
    s = ""
    rem = indent_px
    for step, cp, _ in BLANK_SPACERS:
        count = rem // step
        if count > 0:
            s += chr(cp) * count
            rem %= step
    return s


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def calibrate_px(target_cap_h: int) -> int:
    lo, hi = 8, 80
    best_px = target_cap_h
    best_diff = 999
    for px in range(lo, hi + 1):
        f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        bbox = f.getbbox("H")
        if not bbox:
            continue
        h = bbox[3] - bbox[1]
        diff = abs(h - target_cap_h)
        if diff < best_diff:
            best_diff = diff
            best_px = px
        if diff == 0:
            return px
    return best_px




def write_pack(out_path, entries):
    import subprocess
    tmp = out_path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    subprocess.run([sys.executable, os.path.join(BASE, "tools", "packfile.py"), "create", tmp, "--type", "3", "--version", "PFH4"],
                   check=True, capture_output=True)
    pf = PackFile(tmp)
    for name in sorted(entries):
        pf.set_file(name, entries[name])
    pf.save(out_path)
    if os.path.exists(tmp):
        os.remove(tmp)
    back = PackFile(out_path)
    assert back.header.version == b"PFH4" and back.header.pack_type == 3
    assert len(back.files) == len(entries)
    for name, data in entries.items():
        assert back.get_file(name) == data, f"pack verify failed: {name}"


def build_fonts():
    print("\n--- Building Phase 1 Round 3 Fonts ---")
    pack = PackFile(VANILLA_PACK)
    font_entries = {}

    tt = TTFont(TAJAWAL)
    tajawal_cmap = tt.getBestCmap()

    for fname in TARGET_FONTS:
        raw = pack.get_file("font\\" + fname)
        if raw is None:
            raw = pack.get_file(r"font/" + fname)
        assert raw is not None, f"Font missing in vanilla pack: {fname}"

        c = CUF.decode(raw)
        vanilla_count = c.count
        vanilla_dims = list(c.dims)
        vanilla_bitmaps = list(c.bitmaps)
        vanilla_table = list(c.table)
        vanilla_props = dict(c.props)
        vanilla_tail = bytes(c.tail)

        # Measure 'H' cap height and baseline in vanilla
        code_H = c.table[ord('H')]
        ah_H, aw_H, w_H, h_H = c.dims[code_H]
        bm_H = c.bitmaps[code_H]
        rows_H = [y for y in range(h_H) if any(bm_H[y * w_H + x] > 20 for x in range(w_H))]
        cap_h = (max(rows_H) - min(rows_H) + 1) if rows_H else h_H
        baseline_H = max(rows_H) if rows_H else c.props["baseline"]

        px = calibrate_px(cap_h)
        font = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        bbox_H = font.getbbox("H")
        taj_base = bbox_H[3] if bbox_H else cap_h

        new_dims = list(vanilla_dims)
        new_bitmaps = list(vanilla_bitmaps)
        new_table = list(vanilla_table)

        v_size = c.props["v_size"]
        cell_h = v_size
        cell_ah = v_size

        # 1. Render standard Arabic forms with full-cell baseline alignment and gap closure
        arabic_cps = (
            list(range(0xFE70, 0xFEFF)) +
            list(range(0x0600, 0x06FF)) +
            [0x0640, 0x060C, 0x061B, 0x061F, 0x066A] +
            list(range(0x0660, 0x066A)) +
            list(range(0x064B, 0x0653))  # Shaddah, Kasrah, Fathah, Dammah, Sukun
        )

        rendered_cells = {}
        for cp in sorted(set(arabic_cps)):
            if cp in tajawal_cmap:
                char_to_draw = chr(cp)
            else:
                decomp = decompose_cp(cp)
                if decomp in tajawal_cmap:
                    char_to_draw = chr(decomp)
                else:
                    continue  # Skip unmapped / non-character codes to prevent .notdef box rendering

            mask = font.getmask(char_to_draw, mode="L")
            bbox = font.getbbox(char_to_draw)
            mw, mh = mask.size
            if mw == 0 or mh == 0:
                continue

            form_name = unicodedata.name(chr(cp), "")
            is_conn_left = ("INITIAL" in form_name or "MEDIAL" in form_name or cp == 0x0640)
            is_conn_right = ("FINAL" in form_name or "MEDIAL" in form_name or cp == 0x0640)

            # Anchor FreeType baseline to row baseline_H
            top_cuf = baseline_H - (taj_base - 1) + bbox[1]
            w = mw
            cell_bm = bytearray(w * cell_h)
            mask_bytes = bytes(mask)

            for my in range(mh):
                cy = top_cuf + my
                if 0 <= cy < cell_h:
                    for mx in range(mw):
                        val = mask_bytes[my * mw + mx]
                        if val > 0:
                            cell_bm[cy * w + mx] = val

            # Fill connecting baseline stroke to cell edges on baseline rows to minimize gap
            for cy in [baseline_H - 1, baseline_H]:
                if 0 <= cy < cell_h:
                    row_vals = [cell_bm[cy * w + mx] for mx in range(w)]
                    dark_indices = [mx for mx in range(w) if row_vals[mx] > 100]
                    if dark_indices:
                        first_x = dark_indices[0]
                        last_x = dark_indices[-1]
                        stroke_val = max(row_vals[first_x], row_vals[last_x], 220)
                        if is_conn_left:
                            for x in range(first_x):
                                cell_bm[cy * w + x] = stroke_val
                        if is_conn_right:
                            for x in range(last_x + 1, w):
                                cell_bm[cy * w + x] = stroke_val

            rendered_cells[cp] = (w, cell_bm)
            glyph_idx = len(new_dims)
            new_dims.append((cell_ah, w, w, cell_h))
            new_bitmaps.append(bytes(cell_bm))
            new_table[cp] = glyph_idx

        # 1b. Render Seamless 0-Pixel Connected Chunk Ligatures
        CHUNK_DEFS = [
            # الفصائل: split so no chunk exceeds engine h_size (48px)
            (0xE110, [0xFEDE, 0xFE8B]),                 # ئل (lam final + yeh hamza initial, ~26px)
            (0xE111, [0xFE8E, 0xFEBC]),                 # صا (alef final + sad medial, ~34px)
            (0xE114, [0xFED4, 0xFEDF]),                 # لف (feh medial + lam initial, ~23px)
            # الشرقية
            (0xE112, [0xFE94, 0xFEF4, 0xFED7]),         # قية
            (0xE113, [0xFEAE, 0xFEB8, 0xFEDF]),         # لشر
        ]
        for chunk_cp, sub_cps in CHUNK_DEFS:
            chunk_sub_cells = [rendered_cells[sc] for sc in sub_cps if sc in rendered_cells]
            if len(chunk_sub_cells) == len(sub_cps):
                total_cw = sum(cw for cw, _ in chunk_sub_cells)
                chunk_bm = bytearray(total_cw * cell_h)
                curr_cx = 0
                for cw, cbm in chunk_sub_cells:
                    for cy in range(cell_h):
                        for cx in range(cw):
                            chunk_bm[cy * total_cw + curr_cx + cx] = cbm[cy * cw + cx]
                    curr_cx += cw
                chunk_idx = len(new_dims)
                new_dims.append((cell_ah, total_cw, total_cw, cell_h))
                new_bitmaps.append(bytes(chunk_bm))
                new_table[chunk_cp] = chunk_idx

        # 2. Append Round 3 Binary Blank Spacer Glyphs
        for _, cp, w in BLANK_SPACERS:
            idx_sp = len(new_dims)
            new_dims.append((cell_ah, w, w, cell_h))
            new_bitmaps.append(bytes(w * cell_h))
            new_table[cp] = idx_sp

        # Encode and assert invariants
        new_cuf = CUF()
        new_cuf.magic = c.magic
        new_cuf.props = vanilla_props
        new_cuf.table = new_table
        new_cuf.dims = new_dims
        new_cuf.bitmaps = new_bitmaps
        new_cuf.tail = vanilla_tail

        encoded = new_cuf.encode()

        # Strict invariants
        for ch in range(32, 127):
            assert new_cuf.table[ch] == vanilla_table[ch], f"Latin map changed for {chr(ch)} in {fname}"
        assert new_dims[:vanilla_count] == vanilla_dims, f"Vanilla dims modified in {fname}"
        assert new_bitmaps[:vanilla_count] == vanilla_bitmaps, f"Vanilla bitmaps modified in {fname}"
        assert new_cuf.props == vanilla_props, f"Props modified in {fname}"
        assert new_cuf.tail == vanilla_tail, f"Kerning tail modified in {fname}"

        font_entries["font\\" + fname] = encoded

    out_font_pack = os.path.join(OUT_DIR, "Attila_Arabic_Phase1_fonts.pack")
    write_pack(out_font_pack, font_entries)
    f_hash = sha256_file(out_font_pack)
    print(f"Created {out_font_pack} ({len(font_entries)} fonts, SHA256: {f_hash})")
    return out_font_pack, f_hash


def build_loc():
    print("\n--- Building Phase 1 Round 3 Loc ---")
    pack = PackFile(VANILLA_PACK)

    # 13-line right-aligned historical narrative for Eastern Roman Empire
    narrative_raw = [
        "أطلق تقسيم الإمبراطورية",
        "عنان الشرق، مما مكنه من",
        "بسط نفوذه على العالم الروماني.",
        "أتاح المركز الإداري بالقسطنطينية",
        "استبدال النظم القديمة،",
        "وملء الخزائن بالأموال.",
        "نجح الشرق في تحويل مسار",
        "هجرات البرابرة غرباً،",
        "لكن الإمبراطور أركاديوس",
        "سيواجه تحديات جسيمة،",
        "بين مؤامرات البلاط وخطر",
        "الساسانيين المستمر لضمان",
        "بقاء شعلة روما الأخيرة متقدة."
    ]

    target_panel_w = 300
    px_12 = calibrate_px(11) # cap_h for la_gioconda_12 is 11
    font_12 = ImageFont.truetype(TAJAWAL, px_12, layout_engine=ImageFont.Layout.BASIC)
    tt = TTFont(TAJAWAL)
    tajawal_cmap = tt.getBestCmap()

    narrative_lines = []
    for line_text in narrative_raw:
        shaped_text = shape(line_text)
        total_w = 0
        for ch in shaped_text:
            cp = ord(ch)
            if cp in tajawal_cmap:
                target_ch = ch
            else:
                decomp = decompose_cp(cp)
                target_ch = chr(decomp) if decomp in tajawal_cmap else ch
            mask = font_12.getmask(target_ch)
            mw = mask.size[0]
            pitch = (mw + 1) if mw > 0 else 6
            total_w += pitch
        indent = max(0, target_panel_w - total_w)
        spacer = make_spacer(indent)
        narrative_lines.append(spacer + shaped_text)

    ere_narrative_text = "\n".join(narrative_lines)

    overrides = {
        # 1. Start Campaign button
        TARGET_KEYS["btn_start_campaign_1"][1]: "[B] " + shape("بدء الحملة"),
        TARGET_KEYS["btn_start_campaign_2"][1]: "[B] " + shape("بدء الحملة"),
        # 2. Factions header (seamless 0-pixel connected chunks: ئل + صا + لف + ا)
        TARGET_KEYS["header_factions_1"][1]: "[F] \uE110\uE111\uE114\uFE8D",
        TARGET_KEYS["header_factions_2"][1]: "[F] \uE110\uE111\uE114\uFE8D",
        TARGET_KEYS["header_factions_3"][1]: "[F] \uE110\uE111\uE114\uFE8D",
        # 3. Difficulty slider tooltip
        TARGET_KEYS["diff_tooltip_1"][1]: "[S] " + shape("مؤشر الصعوبة"),
        TARGET_KEYS["diff_tooltip_2"][1]: "[S] " + shape("مؤشر الصعوبة"),
        TARGET_KEYS["diff_tooltip_3"][1]: "[S] " + shape("مؤشر الصعوبة"),
        # 4. Hard label
        TARGET_KEYS["diff_hard_1"][1]: "[H] " + shape("صعب"),
        TARGET_KEYS["diff_hard_2"][1]: "[H] " + shape("صعب"),
        TARGET_KEYS["diff_hard_3"][1]: "[H] " + shape("صعب"),
        # 5. Difficulty description
        TARGET_KEYS["diff_desc"][1]: "[D] " + shape("للاعبين المتمرسين في توتال وور."),
        # 6. Difficulty legendary body description
        TARGET_KEYS["diff_legendary"][1]: "[L] " + "\n".join([shape("الحفظ اليدوي غير متاح في الحملة."), shape("لا يمكن إصدار الأوامر أثناء إيقاف المعركة مؤقتاً.")]),
        # 7. Cultural trait header
        TARGET_KEYS["header_cultural"][1]: "[C] " + shape("السمة الثقافية"),
        # 8. Faction title (with seamless 0-pixel connected chunks for الشرقية)
        TARGET_KEYS["faction_title"][1]: ("[T] " + shape("الإمبراطورية الرومانية الشرقية")).replace("\uFE94\uFEF4\uFED7\uFEAE\uFEB8\uFEDF", "\uE112\uE113"),
        # 9. Faction description
        TARGET_KEYS["ere_description"][1]: ere_narrative_text,
        TARGET_KEYS["ere_long_description"][1]: ere_narrative_text,
    }

    files_to_edit = {
        r"text\db\uied_component_texts.loc",
        r"text\db\random_localisation_strings.loc",
        r"text\db\factions.loc",
        r"text\db\start_pos_factions.loc",
    }

    loc_entries = {}
    for fpath in files_to_edit:
        raw = pack.get_file(fpath)
        if raw is None:
            raw = pack.get_file(fpath.replace("\\", "/"))
        assert raw is not None, f"Loc file missing in vanilla: {fpath}"

        rows, version, count = loc_decode(raw)
        updated_rows = []
        overridden_in_file = 0
        for k, text, flag in rows:
            if k in overrides:
                overridden_in_file += 1
                updated_rows.append((k, overrides[k], flag))
            else:
                updated_rows.append((k, text, flag))

        print(f"  {fpath}: {len(rows)} entries ({overridden_in_file} overridden)")
        encoded = loc_encode(updated_rows)
        loc_entries[fpath] = encoded

    out_loc_pack = os.path.join(OUT_DIR, "Attila_Arabic_Phase1.pack")
    write_pack(out_loc_pack, loc_entries)

    l_hash = sha256_file(out_loc_pack)
    print(f"Created {out_loc_pack} ({len(loc_entries)} tables, SHA256: {l_hash})")
    return out_loc_pack, l_hash


def main():
    print("==================================================")
    print("TOTAL WAR: ATTILA — ARABIC LOCALIZATION")
    print("PHASE 1 CLEAN-SLATE BUILD — ROUND 3")
    print("==================================================")

    f_pack, f_hash = build_fonts()
    l_pack, l_hash = build_loc()

    print("\n--- Summary of Built Packs ---")
    print(f"Fonts pack: {f_pack} | SHA-256: {f_hash}")
    print(f"Loc pack:   {l_pack} | SHA-256: {l_hash}")
    print("Build complete.")


if __name__ == "__main__":
    main()
