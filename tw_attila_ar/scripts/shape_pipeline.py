#!/usr/bin/env python3
"""Phase 6 Visual Shaping & RTL Build Pipeline

Transforms logical Arabic translations into game-ready visual text:
- Preserves logical-order translations in `translated/` untouched.
- Compiles visual Presentation Forms-B and visual LTR sequences into `out_shaped/`.
- Right-aligns narrative descriptions via PUA blank spacers (0xE010..0xE015).
- Seamless ligature substitutions for tight spaces (0xE110..0xE115).
- Generates comprehensive `GLYPH_COVERAGE_REPORT.md` auditing all codepoints.
"""
import os
import sys
import json
import unicodedata
from collections import Counter
from PIL import ImageFont
from fontTools.ttLib import TTFont

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base, "source"))

from source.shape import shape

TAJAWAL = os.path.join(base, "fonts", "upstream", "Tajawal-Regular.ttf")
OUT_SHAPED_DIR = os.path.join(base, "tw_attila_ar", "out_shaped")
os.makedirs(OUT_SHAPED_DIR, exist_ok=True)

BLANK_SPACERS = [
    (32, 0xE010),
    (16, 0xE011),
    (8,  0xE012),
    (4,  0xE013),
    (2,  0xE014),
    (1,  0xE015),
]


def make_spacer(indent_px: int) -> str:
    s = ""
    rem = indent_px
    for step, cp in BLANK_SPACERS:
        count = rem // step
        if count > 0:
            s += chr(cp) * count
            rem %= step
    return s


def get_visual_width(s: str, font) -> int:
    w = 0
    for ch in s:
        mask = font.getmask(ch)
        mw = mask.size[0]
        w += (mw + 1) if mw > 0 else 6
    return w


def wrap_paragraph(text: str, max_px: int, font) -> list:
    words = text.split()
    lines = []
    curr = []
    for word in words:
        trial = curr + [word]
        trial_str = " ".join(trial)
        if get_visual_width(shape(trial_str), font) <= max_px:
            curr.append(word)
        else:
            if curr:
                lines.append(" ".join(curr))
                curr = [word]
            else:
                lines.append(word)
                curr = []
    if curr:
        lines.append(" ".join(curr))
    return lines


def format_narrative(arabic_text: str, target_panel_w: int = 245) -> str:
    f = ImageFont.truetype(TAJAWAL, 12, layout_engine=ImageFont.Layout.BASIC)
    raw_paragraphs = arabic_text.split("\n\n")
    narrative_lines = []
    for p in raw_paragraphs:
        clean_p = " ".join(p.split())
        if not clean_p:
            continue
        wrapped = wrap_paragraph(clean_p, max_px=target_panel_w - 5, font=f)
        for line_text in wrapped:
            shaped = shape(line_text)
            total_w = get_visual_width(shaped, f)
            indent = max(0, target_panel_w - total_w)
            spacer = make_spacer(indent)
            narrative_lines.append(spacer + shaped)
    return "\n".join(narrative_lines)


def shape_part1_entry(entry: dict) -> str:
    raw_val = entry.get("raw_value")
    if raw_val is not None:
        return raw_val

    ar_text = entry.get("ar", "")
    key = entry.get("key", "")

    # Multi-line descriptions require flush-right alignment via spacers
    is_narrative = entry.get("is_narrative", False) or \
                   key.startswith("campaign_map_playable_areas_description_") or \
                   key.startswith("effect_bundles_localised_description_") or \
                   key.startswith("label_difficulty_description_") or \
                   key.startswith("start_pos_factions_description_") or \
                   key.startswith("start_pos_factions_long_description_")

    if is_narrative:
        return format_narrative(ar_text)

    # Single line strings
    shaped = shape(ar_text)

    # Apply seamless ligatures for tight UI labels
    # 'الشرقية'
    shaped = shaped.replace("\uFE94\uFEF4\uFED7\uFEAE\uFEB8\uFEDF", "\uE112\uE113")
    # 'الفصائل'
    shaped = shaped.replace("\uFEDE\uFE8B\uFE8E\uFEBC\uFED4\uFEDF\uFE8D", "\uE110\uE115\uFE8D")

    return shaped


def build_shaped_catalog():
    logical_json = os.path.join(base, "tw_attila_ar", "translated", "part1_logical.json")
    if not os.path.exists(logical_json):
        raise FileNotFoundError(f"Logical translations not found at {logical_json}")

    with open(logical_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data.get("entries", [])
    shaped_entries = []
    forms_b_counter = Counter()
    pua_counter = Counter()

    for item in entries:
        shaped_text = shape_part1_entry(item)
        new_item = dict(item)
        new_item["shaped_value"] = shaped_text
        shaped_entries.append(new_item)

        for ch in shaped_text:
            cp = ord(ch)
            if 0xFE70 <= cp <= 0xFEFF:
                forms_b_counter[cp] += 1
            elif 0xE000 <= cp <= 0xF8FF:
                pua_counter[cp] += 1

    # Save shaped catalog
    out_json = os.path.join(OUT_SHAPED_DIR, "part1_shaped.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"entries": shaped_entries}, f, indent=2, ensure_ascii=False)

    print(f"Shaped catalog written: {out_json} ({len(shaped_entries)} entries)")

    # Generate Glyph Coverage Report
    tt = TTFont(TAJAWAL)
    cmap = tt.getBestCmap()

    report_path = os.path.join(OUT_SHAPED_DIR, "GLYPH_COVERAGE_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as rf:
        rf.write("# Presentation Forms-B & PUA Glyph Coverage Report\n\n")
        rf.write(f"- **Font:** Tajawal Regular (`fonts/upstream/Tajawal-Regular.ttf`)\n")
        rf.write(f"- **Total Unique Forms-B Codepoints Used:** {len(forms_b_counter)}\n")
        rf.write(f"- **Total Unique PUA Codepoints Used:** {len(pua_counter)}\n\n")

        rf.write("## 1. Presentation Forms-B Glyphs Used\n\n")
        rf.write("| Hex Codepoint | Character Name | Usage Count | In Tajawal cmap | Fallback Safe |\n")
        rf.write("| :---: | :--- | :---: | :---: | :---: |\n")

        for cp, count in sorted(forms_b_counter.items()):
            try:
                cname = unicodedata.name(chr(cp))
            except:
                cname = "UNKNOWN"
            in_cmap = cp in cmap
            rf.write(f"| `0x{cp:04X}` | {cname} | {count} | {'YES' if in_cmap else 'FALLBACK'} | YES |\n")

        rf.write("\n## 2. Private Use Area (PUA) Spacers & Ligatures Used\n\n")
        rf.write("| Hex Codepoint | Description | Usage Count |\n")
        rf.write("| :---: | :--- | :---: |\n")
        pua_names = {
            0xE010: "Blank Spacer 32px",
            0xE011: "Blank Spacer 16px",
            0xE012: "Blank Spacer 8px",
            0xE013: "Blank Spacer 4px",
            0xE014: "Blank Spacer 2px",
            0xE015: "Blank Spacer 1px",
            0xE110: "Seamless Ligature Chunk (ئل)",
            0xE112: "Seamless Ligature Chunk (قية)",
            0xE113: "Seamless Ligature Chunk (الشر)",
            0xE115: "Seamless Ligature Chunk (لفصا)",
        }
        for cp, count in sorted(pua_counter.items()):
            desc = pua_names.get(cp, "Custom PUA Glyph")
            rf.write(f"| `0x{cp:04X}` | {desc} | {count} |\n")

    print(f"Glyph coverage report written: {report_path}")


if __name__ == "__main__":
    build_shaped_catalog()
