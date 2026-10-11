# Tooling Specification & Verified Commands

**Document:** `<WORKDIR>/TOOLING.md`  
**Execution Date:** 2026-10-10  
**Status:** PRODUCTION VERIFIED  

---

## 1. Upstream Tooling Reference (Clean-Room Inspection)

The following reference repositories are cloned into `<WORKDIR>/vendor` for format documentation and schema definitions:

| Repository | Path | Commit / Tag | Purpose |
| :--- | :--- | :--- | :--- |
| **RPFM Source** | `<WORKDIR>/vendor/rpfm` | `master` (Frodo45127/rpfm) | Reference architecture for Warscape file formats, pack structures, and `.loc` serialization |
| **RPFM Schemas** | `<WORKDIR>/vendor/rpfm-schemas` | `master` (Frodo45127/rpfm-schemas) | Table definitions (`schema_att.ron`, 5.35 MB) for Total War: Attila DB tables |
| **RPFM UI / Server** | `tools/rpfm-v5.1.1/` | Portable v5.1.1 | Visual GUI pack inspection and schema diagnostics |

---

## 2. Attila Schema Validation (`schema_att.ron`)

The Attila schema file (`tw_attila_ar/vendor/rpfm-schemas/schema_att.ron`) defines the table versions and field structures for Attila.
- **Game ID:** `att` / `attila`
- **Schema File Size:** 5,355,388 bytes
- **Validation:** Tested against Attila DB tables extracted from `data.pack`. The schema properly parses key DB definitions for:
  - `factions_tables`
  - `faction_groups_tables`
  - `religions_tables`
  - `campaign_map_playable_areas_tables`
  - `frontend_faction_leaders_tables`

---

## 3. Verified Clean-Room Headless Commands

Because RPFM v5 releases omit `rpfm_cli.exe`, headless and automated pipeline operations are executed using native, zero-dependency Python tools adhering to Ponytail principles:

### A. Extract Packed Files from Any `.pack`
```python
from tools.packfile import PackFile

# Open any game pack (PFH4 format)
pack = PackFile("D:/SteamLibrary/steamapps/common/Total War Attila/data/local_en.pack")

# Extract specific file bytes
raw_loc = pack.get_file("text/db/factions.loc")

# List all files matching a pattern
loc_files = [f for f in pack.files if f.endswith(".loc")]
```

### B. Decode and Encode Binary `.loc` Files
```python
from source.loc import decode, encode

# Decode binary .loc bytes into (key, text, tooltip) rows
rows, pos, total = decode(raw_loc)
for key, text, tooltip in rows:
    print(f"[{tooltip}] {key} = {text}")

# Encode (key, text, tooltip) rows back to byte-exact binary .loc format
binary_loc = encode(rows)
```

### C. Build a Standalone Mod Pack (`PFH4`)
```python
from tools.packfile import PackFile

# Create a new Mod-type pack file
pack = PackFile()
pack.header.pack_type = 3  # 3 = Mod pack (overrides release/patch)
pack.add_file("text/db/factions.loc", binary_loc_data)
pack.add_file("ui/frontend ui/sp_grand_campaign", binary_ui_data)
pack.save("tw_attila_ar/out/Attila_Arabic_Mod.pack")
```
