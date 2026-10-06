# Test Pack Manifest — v2 (loc-only probe, NO CUF)

Pack: `D:\AttilaArabic\release\Attila_Arabic_POC_v2.pack`
SHA256: `C387D01D5ED6F4C3D8590CCB62AC2ABA346D9AD3B770181D7EF9C3057FDA1ABB`
Format: PFH4, type `mod (3)`, 4 files, 0 dependencies.
Built by: `source\build_v2.py` (asserts every key exists; full-file copies;
entry counts re-verified 3119/2703/618/1117; tooltips flags preserved).
Vanilla files changed: NONE.
Stored text = `Knn`/ASCII-ID prefix + pre-shaped visual-order Arabic
(arabic-reshaper 3.0.1 + python-bidi 0.6.11). No font files in this pack.

Note: bare `D\d\d` substrings also occur inside *unedited* vanilla English
rows (regex false positives during verification) — only the 32 keys below
were changed (VERIFIED by re-extract + re-decode).

## Probes

| ID | File | Key (suffix) | Vanilla | Screen |
|----|------|--------------|---------|--------|
| K01 | uied | `string_NewState_Text_3a000c` | Historical Battle | Battles menu, button 1 |
| K02 | uied | `string_NewState_Text_3a000cm` | Historical Battle | Battles menu, button 1 (variant) |
| K03 | uied | `button_txt_NewState_Text_36000f` | Custom Battle | Battles menu, button 2 |
| K04 | uied | `button_txt_NewState_Text_36000fs` | Custom Battle | Battles menu, button 2 (variant) |
| K05 | uied | `string_NewState_Text_250075` | Multiplayer Battle | Battles menu, button 3 (AR+EN: `K05 Rome 1200 — روما`) |
| K06 | uied | `string_NewState_Text_250075x` | Multiplayer Battle | Battles menu, button 3 (variant) |
| K07 | uied | `tx_title_mp_Text_250075` | Multiplayer Battle | Battles menu, button 3 (variant) |
| K08 | uied | `button_txt_NewState_Text_250075` | Multiplayer Battles | Battles menu, button 3 (variant) |
| K09 | uied | `string_NewState_Text_460009` | Quick Battle | Battles menu, button 4 |
| K10 | uied | `heading_tx_NewState_Text_460009j` | Quick Battle | Battles menu, button 4 (variant) |
| K11 | uied | `string_NewState_Text_1d002f` | Leaderboards | Battles menu, button 5 |
| K12 | uied | `button_txt_NewState_Text_700030` | Replays | Battles menu, button 6 |
| K13 | uied | `string_NewState_Text_700030` | Replays | Battles menu, button 6 (variant) |
| K14 | uied | `button_txt_NewState_Text_23001bb` | Load Campaign | Campaigns menu |
| K15 | uied | `button_txt_NewState_Text_530011r` | Grand Campaign | Campaigns menu |
| K16 | uied | `string_active_Text_c0020` | The Last Roman | Campaigns menu (candidate key) |
| K17 | uied | `string_active_Text_3b` | Age of Charlemagne | Campaigns menu (candidate key) |
| K18 | uied | `button_txt_NewState_Text_430007` | Multiplayer Campaign | Campaigns menu |
| K19 | uied | `button_txt_NewState_Text_380007` | Continue Campaign | Campaigns menu bottom button |
| K20 | uied | `button_txt_NewState_Text_30006e` | Start Campaign | Faction-select bottom button |
| K21 | uied | `tx_header_NewState_Text_530011` | New Campaign | Faction-select header |
| K22 | uied | `heading_tx_NewState_Text_79004a` | Difficulty | Faction-select right panel |
| K23 | factions | `factions_screen_name_bel_fact_byzantine_empire` | Roman Empire | Faction-select group tab (candidate key) |
| K24 | uied | `header_cultural_NewState_Text_5e0000` | Cultural Trait | Faction-select parchment |
| K25 | uied | `header_faction_NewState_Text_410063` | Faction Trait | Faction-select parchment |
| K26 | factions | `factions_screen_name_att_fact_eastern_roman_empire` | Eastern Roman Empire | Faction list (AR+numbers control) |
| D27 | startpos | `…_long_description_2120156889` | ERE English (2055 ch) | ERE description panel (mechanism control) |
| D28 | startpos | `…_long_description_2120156339` | WRE English (945 ch) | WRE description panel (v1 retest) |
| K29 | uied | `tx_header_NewState_Text_b0036` | Religion | Faction-select parchment (candidate) |
| K30 | uied | `medal1_default_Tooltip_5003a` | Hard | Difficulty medal hover tooltip (candidate location) |
| K31 | land_units | `land_units_onscreen_name_att_rom_legio` | Legio | Custom Battle → army-setup roster (frontend-reachable battle content) |
| K32 | uied | `StatusIcon_Wavering_Tooltip_a003d` | Wavering | BATTLE-ONLY: unit status-icon hover tooltip when a unit wavers (requires fighting a battle; not reachable from frontend) |

## Test steps for the user

1. Rename `%APPDATA%\The Creative Assembly\Attila\ui_cache` to
   `ui_cache_bak` (exact path given in report; cache regenerates).
2. Copy the pack to `…\Total War Attila\data\`, tick it in Mod Manager, Play.
3. Visit: Battles menu (K01–K13) → Campaigns menu (K14–K19) →
   Grand Campaign → faction select (K20–K30) → Custom Battle setup (K31) →
   fight a battle until wavering + hover (K32).
