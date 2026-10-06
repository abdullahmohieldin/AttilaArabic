# Test Pack Manifest — v2b (loc-only probe, NO CUF)

Pack: `D:\AttilaArabic\release\Attila_Arabic_POC_v2b.pack`
SHA256: `073C79021BA61821073A8BF3715B3BBA8304CF686B881FD40150495E8D17ACF2`
Format: PFH4, type `mod (3)`, 7 files, 0 dependencies.
Built by: `source\build_v2b.py` (asserts every key exists; full-file copies;
69/69 rows byte-exact vs expected incl. verbatim G02; tooltip flags kept).
Vanilla files changed: NONE. No fonts in this pack.

New files vs v2: `faction_groups.loc` (18), `random_localisation_strings.loc`
(1483), `ui_unit_stats.loc` (80). Carried v2: all 30 v2 keys+IDs unchanged
(K01–K26 minus K27/K28, K29–K32).

## New probes

| ID | File | Key suffix | Vanilla | Screen |
|----|------|-----------|---------|--------|
| K33/K34/K35 | uied | `button_txt_530011`, `string_530011`, `button_txt_530011h` | New Campaign (variants) | Campaigns menu (rule e) |
| K36/K37 | uied | `string_continue_campaign_380007`, `string_180007` | Continue Campaign (variants) | Campaigns menu (rule e) |
| K38 | uied | `tx_difficulty_79004a` | Difficulty | Faction select (rule e) |
| K39/K40/K41 | uied | `region_religion_Tooltip_b0036`, `tx_culture_b0036`, `religion_Tooltip_b0036` | Religion (variants) | Faction select (rule e) |
| K42–K47 | faction_groups | `…_group_roman/eastern/nomadic/barbarian/barbarian_m/sand` | Roman Empire … Desert Kingdoms | Group tabs (correct file; v2 K23 key was wrong) |
| K48/K49 | uied | `year_txt_310044`, `year_tx_310064` | Start year: | Faction select right panel |
| K50 | uied | `tx_initial_challenge:_670040` | Initial challenge: | Faction select right panel |
| K51–K55 | random | `…_difficulty_description_0..4` | difficulty level texts | Difficulty hover (5 levels) |
| T01 | uied | `handle_NewState_Tooltip_7000b` | Difficulty Slider\|\|… (long) | Difficulty slider hover (LONG Arabic) |
| T02/T03 | uied | `handle_Tooltip_7000b`, `cmp_diff_slider_Tooltip_7000b` | Difficulty Slider… (variants) | Slider hover (rule e) |
| U01–U05 | ui_unit_stats | `…_stat_melee_attack/armour/health/morale/speed` | Melee Attack…Speed | Custom Battle unit card |
| G01 | uied | `dy_text_accepted_35006c` | You have [[col:green]]accepted[[/col]]… | Diplomacy offer response (CAMPAIGN ONLY — not frontend/Custom Battle) |
| G02 | uied | `dy_text_rejected_330065` | They have [[col:red]]rejected[[/col]]… | Same; tags in post-bidi storage order (stored verbatim) |
| D27a/D27b | startpos | `description_6889` + `long_description_6889` | ERE English | ERE panel (task-1 pair fix) |
| D28a/D28b | startpos | `description_6339` + `long_description_6339` | WRE English | WRE panel (task-1 pair fix) |
| D29 | startpos | `long_description_2120156283` (Alamans) | English + LF newlines | Any faction panel (newline mechanics) |
| D29b | startpos | `long_description_2120156823` (Venedians) | English + CRLF newlines | Same (LF vs CRLF) |

Tag reachability note: no `[[col:]]` string was found in Custom-Battle-
reachable files (`land_units`, `units`, `ui_unit_stats`, strengths/weaknesses
all untagged — VERIFIED by grep); G01/G02 therefore live on the campaign
diplomacy screen. State: reachable only in campaign (not frontend).
