# Phase 0 Audit: Prompt Assumptions Against Reality

**Document:** `<WORKDIR>/AUDIT_PROMPT.md`  
**Execution Date:** 2026-10-10  
**Target:** Total War: Attila Installation & Arabic Localization Workspace  

---

## 1. Summary of Audit Findings

| Prompt Assumption | Status | Core Reality & Evidence |
| :--- | :---: | :--- |
| **1. Pack Names (`local_en.pack`, etc.)** | **VERIFIED** | `local_en.pack` (211,301,042 B) and `local_en_shared_rome2.pack` (1,014,553,082 B) exist in `data/`. No `patch*.pack` files exist for Attila. |
| **2. Loc File Paths (`text/db/*.loc`)** | **VERIFIED** | All 171 `.loc` files in `local_en.pack` reside strictly within `text/db/`. Exactly 0 `.loc` files exist outside `text/db/`. |
| **3. Loc Columns (`key`, `text`, `tooltip`)** | **VERIFIED** | Binary format (14-byte header: `\xff\xfeLOC\x00` + ver=1 + count) maps each entry to `(key: u16+utf16le, text: u16+utf16le, tooltip: u8)`. |
| **4. RPFM Game Key (`"attila"`)** | **VERIFIED** | Verified from `rpfm_lib::games::supported_games::KEY_ATTILA = "attila"`. Schemas in `rpfm-schemas` use `schema_att.ron`. |
| **5. RPFM CLI Subcommands & Availability** | **WRONG** | Official RPFM v5 release packages (`rpfm-v5.1.1-x86_64-pc-windows-msvc.zip`) do NOT include `rpfm_cli.exe`. Python CLI tools (`packfile.py`, `loc.py`) provide identical functionality. |
| **6. Markup Patterns** | **VERIFIED** | Text uses tags `[[col:color]]...[[/col]]`, `[[rgba:...]]...[[/rgba]]`, `[[url:...]]...[[/url]]`, and printf placeholders `%s`, `%d`. |
| **7. Load-Order & Override Behavior** | **VERIFIED** | Mod packs override Release packs. The engine merges `.loc` files by key into a global dictionary rather than replacing entire files. |
| **8. Faction Select UI Location** | **VERIFIED** | The UI layout lives at `ui/frontend ui/sp_grand_campaign` in `data.pack` and is overridden in `data/ui/frontend ui/sp_grand_campaign`. |
| **9. Project Layout** | **VERIFIED** | Workspace `D:\AttilaArabic` contains active translations in `data/translations/`, fonts in `fonts/upstream/`, and tools in `tools/` and `source/`. |

---

## 2. Detailed Technical Evidence

### Assumption 1: Pack Names in Total War: Attila
- **Prompt:** Assumes `local_en.pack`, patch packs, DLC packs.
- **Audit Findings:**
  - Files scanned in `D:\SteamLibrary\steamapps\common\Total War Attila\data`:
    - Base / Loc: `data.pack` (1,648,871,278 B), `local_en.pack` (211,301,042 B), `local_en_shared_rome2.pack` (1,014,553,082 B), `boot.pack` (21,499 B)
    - DLC Packs: `charlemagne.pack`, `belisarius.pack`, `slavs.pack`, `blood.pack`
    - Audio/Media: `music.pack`, `music_en_shared_rome2.pack`, `sound.pack`, `movies.pack`
    - Models/Terrain/Tiles: `models.pack` (1..3), `terrain.pack` (1..2), `tiles.pack` (1..4)
  - **Correction/Note:** Unlike Total War: Rome II or Warhammer, Attila was never updated with sequential `patch*.pack` files; updates were rolled into base packs.
  - **Verdict:** **VERIFIED** (with specific note on absence of `patch*.pack`).

### Assumption 2: Location of `.loc` Files
- **Prompt:** Assumes paths follow `text/db/*.loc` or `text/**/*.loc`.
- **Audit Findings:**
  - `local_en.pack` contains exactly 171 `.loc` files.
  - 100% of these 171 files are located under `text\db\` (e.g., `text\db\factions.loc`, `text\db\names.loc`, `text\db\campaigns.loc`).
  - Scan of `local_en_shared_rome2.pack` and `data.pack` showed 0 `.loc` files.
  - **Verdict:** **VERIFIED**.

### Assumption 3: Loc Table Schema (`key | text | tooltip`)
- **Prompt:** Assumes columns are `key`, `text`, and `tooltip`.
- **Audit Findings:**
  - Verified through clean-room decoder `source/loc.py` matching `rpfm_lib::files::loc`:
    - File magic: `\xff\xfeLOC\x00` (6 bytes)
    - Version: `i32` (value = 1)
    - Entry count: `u32`
    - Entries: `(u16 length + UTF-16LE key, u16 length + UTF-16LE text, u8 tooltip flag)`
  - **Verdict:** **VERIFIED**.

### Assumption 4: RPFM Game Key `"attila"`
- **Prompt:** Assumes RPFM game key is `"attila"`.
- **Audit Findings:**
  - Verified in `Frodo45127/rpfm/rpfm_lib/src/games/supported_games.rs`:
    `pub const KEY_ATTILA: &str = "attila";`
  - In `Frodo45127/rpfm-schemas`, the schema file is named `schema_att.ron`.
  - **Verdict:** **VERIFIED**.

### Assumption 5: RPFM CLI Subcommands & Availability
- **Prompt:** Assumes `rpfm_cli` is shipped in latest RPFM releases and can be executed headlessly for pack/loc operations.
- **Audit Findings:**
  - Inspected official release `rpfm-v5.1.1-x86_64-pc-windows-msvc.zip`: It contains `rpfm_ui.exe` and `rpfm_server.exe`. It does NOT contain `rpfm_cli.exe`.
  - Audited previous workspace research in `docs/environment-audit.md`: Confirms `v5.x ships NO rpfm_cli.exe`.
  - Crates.io package `rpfm_cli` was last released at version 4.5.4, and the user environment has no Rust compiler (`cargo`/`rustc`) installed.
  - **Workaround & Correction:**
    - The repository already has complete, native Python implementations: `tools/packfile.py` (reads and writes binary PFH4 packs) and `source/loc.py` (encodes and decodes `.loc` binary format).
    - We will clone `rpfm` and `rpfm-schemas` into `<WORKDIR>/vendor` for reference, schemas, and documentation.
    - Automated pack operations will use verified Python scripts adhering to the Ponytail principle (prefer existing tools and Python stdlib over unnecessary external compile overhead).
  - **Verdict:** **WRONG** (corrected with verified Python tooling).

### Assumption 6: Markup and Substitution Patterns
- **Prompt:** Mentions protecting formatting tokens and placeholders.
- **Audit Findings:**
  - Regex scan across all 171 vanilla loc files identified:
    - URL tags: `[[url:...]]...[[/url]]` (frequently used in encyclopedia/help text)
    - Color tags: `[[col:...]]...[[/col]]`, `[[rgba:...]]...[[/rgba]]`
    - Printf specifiers: `%s` and `%d` (used for dynamic counts and names)
  - **Verdict:** **VERIFIED**.

### Assumption 7: Pack Load Order and Key Override Semantics
- **Prompt:** Assumes standalone override mod pack can override individual keys.
- **Audit Findings:**
  - Total War Warscape engine initializes localization into a global key-value hashtable.
  - Files in `text/db/*.loc` from higher-priority packs (Mod type loaded via mod manager or user script) override individual `key` entries from lower-priority packs (Release/data packs).
  - Pack header `pack_type = 3` designates a Mod pack.
  - **Verdict:** **VERIFIED**.

### Assumption 8: Faction Selection UI Component Location
- **Prompt:** Assumes faction selection UI layout lives in the packs.
- **Audit Findings:**
  - Packed at `ui\frontend ui\sp_grand_campaign` in `data.pack`.
  - The repository already contains an edited version at `data/ui/frontend ui/sp_grand_campaign` where Leader and Religion coordinates were previously adjusted.
  - **Verdict:** **VERIFIED**.

### Assumption 9: Existing Project Layout
- **Prompt:** Assumes project contains source, tools, data, fonts, tests, and documentation.
- **Audit Findings:**
  - Verified directory structure: `data/translations/`, `data/ui/`, `fonts/upstream/`, `tools/`, `source/`, `tests/`, `docs/`, `reference/`, `release/`, `scratch/`.
  - **Verdict:** **VERIFIED**.
