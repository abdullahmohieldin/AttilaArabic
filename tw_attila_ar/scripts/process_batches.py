#!/usr/bin/env python3
"""Batch Processor and Sequencer for Part 1 Translations

Assembles Tier 1A and Tier 1B translations into ~100-150 entry JSONL batches,
validates each batch with validate.py, tracks progress, and saves validated
logical translations to `translated/`.
"""
import os
import sys
import json
import glob
from collections import OrderedDict

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
workdir = os.path.join(base, "tw_attila_ar")
batches_dir = os.path.join(workdir, "batches")
trans_out_dir = os.path.join(workdir, "translated")
os.makedirs(batches_dir, exist_ok=True)
os.makedirs(trans_out_dir, exist_ok=True)

sys.path.insert(0, workdir)
from scripts.validate import validate_batch

# Define Tier Order
TIER_1A_FILES = [
    "factions.json",
    "faction_groups.json",
    "leaders_and_campaign.json",
    "campaigns.json",
    "faction_select_ui.json",
    "faction_descriptions.json",
    "faction_traits_effects.json"
]

TIER_1B_FILES = [
    "main_menu.json",
    "settings_and_options.json",
    "custom_battle.json",
    "unit_ratings.json",
    "unit_stats.json"
]

def load_tier_entries(file_list, tier_name, seen_keys):
    entries = []
    for fn in file_list:
        fp = os.path.join(base, "data", "translations", fn)
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("entries", []):
            item["tier"] = tier_name
            item["source_catalog"] = fn
            k = item.get("key") or item.get("id")
            if k in seen_keys:
                continue
            seen_keys.add(k)
            item["id"] = k
            entries.append(item)
    return entries

def main():
    seen_keys = set()
    entries_1a = load_tier_entries(TIER_1A_FILES, "1A", seen_keys)
    entries_1b = load_tier_entries(TIER_1B_FILES, "1B", seen_keys)
    all_entries = entries_1a + entries_1b

    print(f"Total Tier 1A entries: {len(entries_1a)}")
    print(f"Total Tier 1B entries: {len(entries_1b)}")
    print(f"Total Part 1 entries:  {len(all_entries)}")

    # Split into batches of ~100-120 items
    batch_size = 110
    batches = [all_entries[i:i + batch_size] for i in range(0, len(all_entries), batch_size)]

    progress = {
        "total_entries": len(all_entries),
        "total_batches": len(batches),
        "completed_batches": 0,
        "batches_info": []
    }

    all_validated = []

    for b_idx, batch in enumerate(batches, 1):
        b_name = f"batch_{b_idx:02d}"
        b_file = os.path.join(batches_dir, f"{b_name}.jsonl")
        
        # Write JSONL
        with open(b_file, "w", encoding="utf-8") as bf:
            for item in batch:
                bf.write(json.dumps(item, ensure_ascii=False) + "\n")

        # Validate
        valid, errs = validate_batch(batch)
        if not valid:
            print(f"ERROR: {b_name} failed validation:")
            for err in errs[:5]:
                print(f"  {err}")
            sys.exit(1)

        progress["completed_batches"] += 1
        tier = batch[0].get("tier")
        progress["batches_info"].append({
            "batch": b_name,
            "count": len(batch),
            "tier": tier,
            "status": "VALIDATED"
        })
        print(f"Batch {b_name} ({len(batch)} entries, Tier {tier}): VALIDATED OK")
        all_validated.extend(batch)

    # Save progress.json
    prog_file = os.path.join(batches_dir, "progress.json")
    with open(prog_file, "w", encoding="utf-8") as pf:
        json.dump(progress, pf, indent=2, ensure_ascii=False)

    # Save RESUME.md
    resume_file = os.path.join(batches_dir, "RESUME.md")
    with open(resume_file, "w", encoding="utf-8") as rf:
        rf.write(f"# Part 1 Translation Progress & Resume Status\n\n")
        rf.write(f"- **Total Part 1 Strings:** {len(all_entries)}\n")
        rf.write(f"- **Total Batches:** {len(batches)}\n")
        rf.write(f"- **Completed Batches:** {progress['completed_batches']}/{len(batches)}\n")
        rf.write(f"- **Status:** ALL BATCHES VALIDATED\n\n")
        rf.write("| Batch | Count | Tier | Status |\n| :--- | :---: | :---: | :---: |\n")
        for bi in progress["batches_info"]:
            rf.write(f"| {bi['batch']} | {bi['count']} | {bi['tier']} | {bi['status']} |\n")

    # Save unified validated logical translations to translated/part1_logical.json
    translated_out = os.path.join(trans_out_dir, "part1_logical.json")
    with open(translated_out, "w", encoding="utf-8") as tof:
        json.dump({"entries": all_validated}, tof, indent=2, ensure_ascii=False)

    print(f"\nAll {len(batches)} batches validated and exported to {translated_out}!")

if __name__ == "__main__":
    main()
