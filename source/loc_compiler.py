#!/usr/bin/env python3
"""Data-Driven Universal Loc Compiler for Total War: ATTILA Arabic Localization

Compiles all modular JSON translations from `data/translations/` into `release/Attila_Arabic_Phase1.pack`.
Features:
  - Automatic Arabic visual LTR shaping + Forms-B mapping via `source.shape.shape()`
  - Zero-clipping ligature chunk mapping support (e.g., seamless chunks for 'الفصائل' and 'الشرقية')
  - Automatic right-margin flush alignment with PUA binary blank spacers (0xE010..0xE015) for multi-line narratives
  - Table-level validation against vanilla `extracted/local_en.copy.pack`
  - High-performance, reproducible PFH4 mod pack creation
"""
import os
import sys
import glob
import json
import hashlib
import unicodedata
from PIL import ImageFont
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from source.cuf import CUF
from source.loc import decode as loc_decode, encode as loc_encode
from source.shape import shape
from tools.packfile import PackFile

BASE = r"D:\AttilaArabic"
TAJAWAL = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")
VANILLA_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
TRANS_DIR = os.path.join(BASE, "data", "translations")
OUT_DIR = os.path.join(BASE, "release")

# PUA binary blank spacers (Unicode 0xE010..0xE015)
BLANK_SPACERS = [
    (32, 0xE010, 31),
    (16, 0xE011, 15),
    (8,  0xE012, 7),
    (4,  0xE013, 3),
    (2,  0xE014, 1),
    (1,  0xE015, 0),
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


def format_narrative(arabic_text: str, target_panel_w: int = 340) -> str:
    px_12 = calibrate_px(11)
    font_12 = ImageFont.truetype(TAJAWAL, px_12, layout_engine=ImageFont.Layout.BASIC)
    tt = TTFont(TAJAWAL)
    tajawal_cmap = tt.getBestCmap()

    lines = [line.strip() for line in arabic_text.split("\n") if line.strip()]
    narrative_lines = []
    for line_text in lines:
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
    return "\n".join(narrative_lines)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def write_pack(out_path: str, entries: dict) -> None:
    import subprocess
    tmp = out_path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    subprocess.run([
        sys.executable,
        os.path.join(BASE, "tools", "packfile.py"),
        "create",
        tmp,
        "--type", "3",
        "--version", "PFH4"
    ], check=True, capture_output=True)
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


def compile_all_locs(vanilla_pack_path: str = VANILLA_PACK,
                     translations_dir: str = TRANS_DIR,
                     out_pack_path: str = os.path.join(OUT_DIR, "Attila_Arabic_Phase1.pack")) -> tuple[str, str]:
    print("\n==================================================")
    print("UNIVERSAL DATA-DRIVEN LOCALIZATION COMPILER")
    print("==================================================")

    # 1. Load all JSON translation files
    json_files = sorted(glob.glob(os.path.join(translations_dir, "*.json")))
    if not json_files:
        raise RuntimeError(f"No translation JSON files found in {translations_dir}")

    total_translations = 0
    table_overrides = {}

    for jpath in json_files:
        rel_jpath = os.path.relpath(jpath, BASE)
        with open(jpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        entries = data.get("entries", [])
        print(f"Loaded {len(entries)} entries from {rel_jpath}")

        for item in entries:
            key = item["key"]
            table = item["table"].replace("/", "\\")
            raw_val = item.get("raw_value")

            ar_text = item.get("ar", "")
            if raw_val is None and not ar_text.strip():
                continue

            if key in table_overrides.get(table, {}) and "catalog" in jpath.lower():
                continue

            if raw_val is not None:
                final_text = raw_val
            elif item.get("is_narrative"):
                final_text = format_narrative(ar_text)
            else:
                shaped = shape(ar_text)
                # Apply seamless chunk ligatures for known sequences (e.g. الشرقية)
                # U+FE94 (Teh Marbuta final) + U+FEF4 (Yeh medial) + U+FED7 (Qaf medial) -> U+E112
                # U+FEAE (Reh final) + U+FEB8 (Sheen medial) + U+FEDF (Lam initial) -> U+E113
                shaped = shaped.replace("\uFE94\uFEF4\uFED7\uFEAE\uFEB8\uFEDF", "\uE112\uE113")
                # الفصائل: U+FEDE (Lam final) + U+FE8B (Yeh hamza medial) -> U+E110 (ئل)
                # U+FE8E (Alef final) + U+FEBC (Sad medial) + U+FED4 (Feh medial) + U+FEDF (Lam initial) -> U+E115 (لفصا)
                # U+FE8D (Alef isolated)
                shaped = shaped.replace("\uFEDE\uFE8B\uFE8E\uFEBC\uFED4\uFEDF\uFE8D", "\uE110\uE115\uFE8D")
                final_text = shaped

            table_overrides.setdefault(table, {})[key] = final_text
            total_translations += 1

    print(f"\nTotal unique tables to patch: {len(table_overrides)}")
    print(f"Total localized strings: {total_translations}")

    # 2. Open vanilla pack and patch tables
    pack = PackFile(vanilla_pack_path)
    loc_entries = {}

    for table_path, overrides in table_overrides.items():
        raw = pack.get_file(table_path)
        if raw is None:
            raw = pack.get_file(table_path.replace("\\", "/"))
        if raw is None:
            raise KeyError(f"Table missing in vanilla pack: {table_path}")

        rows, version, count = loc_decode(raw)
        updated_rows = []
        applied_count = 0

        # Create quick map of vanilla keys
        vanilla_keys = {r[0] for r in rows}
        for k in overrides:
            if k not in vanilla_keys:
                print(f"  [WARNING] Key '{k}' not found in vanilla '{table_path}'!")

        for k, text, flag in rows:
            if k in overrides:
                updated_rows.append((k, overrides[k], flag))
                applied_count += 1
            else:
                updated_rows.append((k, text, flag))

        print(f"  -> {table_path}: {applied_count}/{len(overrides)} overrides applied ({len(rows)} total rows)")
        encoded = loc_encode(updated_rows)
        loc_entries[table_path] = encoded

    # 2b. Add Arabic UI Layout Overrides (Faction Leader & Religion RTL position swap)
    uic_path = os.path.join(BASE, "data", "ui", "frontend ui", "sp_grand_campaign")
    if os.path.exists(uic_path):
        with open(uic_path, "rb") as f:
            loc_entries[r"ui\frontend ui\sp_grand_campaign"] = f.read()
            print("  -> Added Arabic UI Layout Override: ui\\frontend ui\\sp_grand_campaign")

    # 3. Write pack
    os.makedirs(os.path.dirname(out_pack_path), exist_ok=True)
    write_pack(out_pack_path, loc_entries)
    pack_hash = sha256_file(out_pack_path)
    print(f"\nSuccessfully compiled: {out_pack_path}")
    print(f"Tables in pack: {len(loc_entries)}")
    print(f"Pack SHA-256:   {pack_hash}")

    return out_pack_path, pack_hash


if __name__ == "__main__":
    compile_all_locs()
