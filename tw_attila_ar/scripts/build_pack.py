#!/usr/bin/env python3
"""Phase 7 Standalone Mod Pack Builder & Round-Trip Verifier

Rebuilds loc TSVs, verifies round-trip integrity, compiles binary `.loc` tables,
incorporates UI layout overrides, builds standalone Mod-type PFH4 `.pack` in `out/`,
and re-extracts the pack to diff and confirm 100% key integrity.
"""
import os
import sys
import json
import csv
import hashlib
from typing import Dict, List, Tuple

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, base)
sys.path.insert(0, os.path.join(base, "source"))

from tools.packfile import PackFile
from source.loc import decode as loc_decode, encode as loc_encode

WORK_DIR = os.path.join(base, "tw_attila_ar")
OUT_DIR = os.path.join(WORK_DIR, "out")
TSV_DIR = os.path.join(OUT_DIR, "tsv")
VERIFY_DIR = os.path.join(OUT_DIR, "verify_extract")
VANILLA_PACK = os.path.join(base, "extracted", "local_en.copy.pack")
SHAPED_JSON = os.path.join(WORK_DIR, "out_shaped", "part1_shaped.json")
OUT_PACK_PATH = os.path.join(OUT_DIR, "Attila_Arabic_Part1.pack")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TSV_DIR, exist_ok=True)
os.makedirs(VERIFY_DIR, exist_ok=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def test_roundtrip(name: str, rows: List[Tuple[str, str, int]]) -> bool:
    """Test TSV -> binary .loc -> decode roundtrip."""
    tsv_path = os.path.join(TSV_DIR, f"{name}.tsv")
    with open(tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["key", "text", "tooltip"])
        writer.writerows(rows)

    # Read back TSV
    read_rows = []
    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader)
        for r in reader:
            if len(r) >= 3:
                read_rows.append((r[0], r[1], int(r[2])))

    # Encode both to binary
    enc_orig = loc_encode(rows)
    enc_tsv = loc_encode(read_rows)

    assert enc_orig == enc_tsv, f"Roundtrip failed for {name}"
    return True


def build_and_verify():
    print("==================================================")
    print("PHASE 7: BUILDING STANDALONE MOD PACK & VERIFYING")
    print("==================================================")

    # 1. Load shaped translations
    with open(SHAPED_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    shaped_entries = data.get("entries", [])
    print(f"Loaded {len(shaped_entries)} shaped Part 1 translations.")

    # Group overrides by target table
    table_overrides = {}
    key_to_expected = {}
    for item in shaped_entries:
        k = item["key"]
        tbl = item["table"].replace("/", "\\")
        val = item["shaped_value"]
        table_overrides.setdefault(tbl, {})[k] = val
        key_to_expected[k] = val

    # 2. Patch vanilla tables and verify roundtrip
    p_vanilla = PackFile(VANILLA_PACK)
    pack_entries = {}
    roundtrips_passed = 0

    for tbl_path, overrides in sorted(table_overrides.items()):
        raw = p_vanilla.get_file(tbl_path)
        if raw is None:
            raw = p_vanilla.get_file(tbl_path.replace("\\", "/"))
        if raw is None:
            raise KeyError(f"Table missing in vanilla pack: {tbl_path}")

        rows, ver, count = loc_decode(raw)
        updated_rows = []
        applied = 0
        for k, text, tip in rows:
            if k in overrides:
                updated_rows.append((k, overrides[k], tip))
                applied += 1
            else:
                updated_rows.append((k, text, tip))

        tbl_name = os.path.basename(tbl_path).replace(".loc", "")
        test_roundtrip(tbl_name, updated_rows)
        roundtrips_passed += 1

        binary_loc = loc_encode(updated_rows)
        pack_entries[tbl_path] = binary_loc
        print(f"  -> {tbl_path}: {applied}/{len(overrides)} keys patched ({len(updated_rows)} total rows) [TSV Roundtrip OK]")

    print(f"\nAll {roundtrips_passed} tables passed TSV round-trip validation.")

    # 3. Add approved UI layout override (sp_grand_campaign)
    uic_path = os.path.join(base, "data", "ui", "frontend ui", "sp_grand_campaign")
    if os.path.exists(uic_path):
        with open(uic_path, "rb") as f:
            pack_entries[r"ui\frontend ui\sp_grand_campaign"] = f.read()
        print("  -> Added approved UI layout override: ui\\frontend ui\\sp_grand_campaign")

    # 4. Assemble standalone Mod-type pack (PFH4, Mod type 3)
    import subprocess
    tmp_pack = OUT_PACK_PATH + ".tmp"
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    if os.path.exists(OUT_PACK_PATH):
        os.remove(OUT_PACK_PATH)

    subprocess.run([
        sys.executable,
        os.path.join(base, "tools", "packfile.py"),
        "create",
        tmp_pack,
        "--type", "3",
        "--version", "PFH4"
    ], check=True, capture_output=True)

    out_pack = PackFile(tmp_pack)
    for rel_path in sorted(pack_entries.keys()):
        out_pack.set_file(rel_path, pack_entries[rel_path])
    out_pack.save(OUT_PACK_PATH)
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    pack_size = os.path.getsize(OUT_PACK_PATH)
    pack_hash = sha256_file(OUT_PACK_PATH)
    print(f"\nStandalone Mod Pack created: {OUT_PACK_PATH}")
    print(f"  Pack Size: {pack_size / (1024*1024):.2f} MB ({pack_size} bytes)")
    print(f"  SHA-256:   {pack_hash}")

    # 5. Re-extract and diff to verify integrity
    print("\nVerifying by re-extracting generated pack...")
    extracted_pack = PackFile(OUT_PACK_PATH)
    assert extracted_pack.header.version == b"PFH4", "Corrupt pack version"
    assert extracted_pack.header.pack_type == 3, "Wrong pack type (must be 3 = Mod)"
    assert len(extracted_pack.files) == len(pack_entries), "Mismatched packed file count"

    verified_keys = 0
    for tbl_path, expected_bytes in pack_entries.items():
        extracted_data = extracted_pack.get_file(tbl_path)
        assert extracted_data == expected_bytes, f"Extracted file data mismatch in {tbl_path}"

        if tbl_path.endswith(".loc"):
            ex_rows, _, _ = loc_decode(extracted_data)
            ex_dict = {k: text for k, text, _ in ex_rows}
            for k in table_overrides.get(tbl_path, {}):
                expected_val = key_to_expected[k]
                assert ex_dict[k] == expected_val, f"Key mismatch for {k}"
                verified_keys += 1

    print(f"VERIFICATION SUCCESSFUL: All {verified_keys} Part 1 localized keys re-extracted and diff-matched 100%!")


if __name__ == "__main__":
    build_and_verify()
