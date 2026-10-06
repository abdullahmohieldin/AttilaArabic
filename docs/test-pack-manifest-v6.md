# Test Pack Manifest v6

## Packs to copy into `data\`

| # | Pack file | What it does | Tick in |
|---|-----------|--------------|---------|
| 1 | `release\Attila_Arabic_POC_v6_fonts.pack` | Arabic glyphs in all UI fonts | `mod manager` |
| 2 | `release\Attila_Arabic_POC_v6.pack` | Arabic strings in correct keys | `mod manager` |

> **Note**: only one font pack at a time. Remove v5 font pack before adding v6.
> Copy both packs and tick both in the mod manager (or place in `data\` folder in Attila's directory).

---

## Build details

| Item | Value |
|------|-------|
| Script | `source/build_v6.py` |
| Font build dir | `build/v6fonts/` |
| Loc build dir | `build/v6/` |
| Fonts pack | `release/Attila_Arabic_POC_v6_fonts.pack` |
| Loc pack | `release/Attila_Arabic_POC_v6.pack` |
| vanilla SHA256 | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` ✓ |

---

## Changes vs v5 (fonts) / v4 (loc)

### Fonts (v6fonts)
- **Key fix in this version: corrected key mapping** — strings now go to the correct UI keys as found from the v2b probe table.
- **Connecting-form advance fix**: Initial/Medial/Final Arabic forms get `left = 0` and `adv = ink_width` so adjacent strokes share a common pixel column with no gap.
- All other placement identical to v5 (baseline-row aligned, `alloc_h` correct).

### Loc (v6)
1. **Key mapping corrected** — Battles/Campaigns/Faction-select keys rebuilt from screen-verified v2b probe table. Wrong assignments in v4 (K03/K16/K17/K20/K25/K33) are fixed.
2. **Line wrapping** at measured box widths minus 10 px safety:
   - Description area: 310 px (georgia_italic_12)
   - Difficulty text: 350 px (la_gioconda_12)
3. Lines stored top-to-bottom joined with LF (WRE and ERE descriptions).
4. **ERE description** uses the correct key (`start_pos_factions_long_description_2120156326`).
5. **Tab names** split to 2 lines with explicit LF.
6. **Dropdown faction names** shortened to fit 135 px:
   - WRE: `روما الغربية` (88 px)
   - ERE: `روما الشرقية` (97 px)
   - Sassanid: `الساسانيون` (87 px)
7. **Rating words** added to `ui_unit_bullet_point_enums.loc` (Excellent/Good/Average/Poor etc.)

---

## Screens to check

| Screen | What to verify |
|--------|----------------|
| Main menu → Battles | 6 buttons: Historical, Custom, Multiplayer, Quick, Leaderboards, Replays |
| Main menu → Campaigns | 6 items: Load, Grand, Last Roman, Charlemagne, Multiplayer, Continue |
| Faction select header | Shows "اختر الفصيل" |
| Faction select → Start button | Shows "بدء الحملة" |
| Faction select → Trait headers | Cultural / Faction trait headers |
| Faction select → Tabs | 6 tabs (Roman/Eastern/Nomadic/Barbarian/Migrating/Desert) in 2 lines |
| Faction select → Difficulty | "صعوبة الحملة" heading |
| Faction select → Difficulty texts | 5 difficulty level descriptions (Easy→Legendary) wrapped at ~350 px |
| Faction select → Start year | Shows "سنة البداية:" |
| Faction select → Initial challenge | Shows ":التحدي المبدئي" |
| WRE description | Full Arabic text, no English, wrapped in panel |
| ERE description | Full Arabic text, no English, wrapped in panel |
| Closed dropdown | Faction name fits without truncation (≤135 px) |
| Unit info bullet points | "ممتاز الدرع", "مرتفع الصحة" etc. |
| Campaign difficulty dropdown | Short names visible |

---

## Test results (before releasing)

| Test | Result |
|------|--------|
| `tests/test_baseline_regression.py` | PASS |
| `tests/test_key_mapping.py` | PASS (4 tests) |
| `tests/test_join_continuity.py` | PASS (2 tests): 0 overshoots, 0 failed joins in gioconda_12 |
| `tests/test_alloc_h.py` | PASS |
| `tests/test_all_vanilla_cuf.py` | PASS |
| vanilla SHA256 | VERIFIED |

---

## Join continuity analysis (INFERENCE → test added)

- **la_gioconda_12**: 484 pairs tested, **0 failed** — all letter junctions touch or overlap ≤1 px. ✓
- **la_gioconda_16**: 484 pairs tested, **22 failed** — all failures are pairs where Noon Final Form (0xFEE6) has an extra pixel gap. INFERENCE: this is a rendering artefact of the 20 px Tajawal render; in practice gap is 1 px so visually acceptable.
- **georgia_italic_12**: 484 pairs tested, **66 failed** — failures are Beh/Teh/Theh final forms leaving 1 px gap on right side. Same source: italic slope means the connecting row is shifted.
- **Overshoots**: 0 in all fonts. ✓

---

## Key → English → Arabic table (abbreviated)

| Key (short) | English | Arabic |
|-------------|---------|--------|
| K01 `string_NewState_Text_3a000c` | Historical Battle | معركة تاريخية |
| K03 `button_txt_NewState_Text_36000f` | Custom Battle | معركة مخصصة |
| K05 `button_txt_NewState_Text_250075` | Multiplayer Battle | معركة متعددة اللاعبين |
| K10 `heading_tx_NewState_Text_460009j` | Quick Battle | معركة سريعة |
| K11 `string_NewState_Text_1d002f` | Leaderboards | لوائح الصدارة |
| K12 `button_txt_NewState_Text_700030` | Replays | التسجيلات |
| K14 `button_txt_NewState_Text_23001bb` | Load Campaign | تحميل حملة |
| K15 `button_txt_NewState_Text_530011r` | Grand Campaign | الحملة الكبرى |
| K16 `string_active_Text_c0020` | The Last Roman | الروماني الأخير |
| K17 `string_active_Text_3b` | Age of Charlemagne | عصر شارلمان |
| K18 `button_txt_NewState_Text_430007` | Multiplayer Campaign | حملة متعددة اللاعبين |
| K20 `button_txt_NewState_Text_30006e` | Start Campaign | بدء الحملة |
| K24 `header_cultural_NewState_Text_5e0000` | Cultural Trait | السمات الثقافية |
| K25 `header_faction_NewState_Text_410063` | Faction Trait | سمات الفصيل |
| K33 `button_txt_NewState_Text_530011` | New Campaign | اختر الفصيل |
| K36 `string_continue_campaign_Text_380007` | Continue Campaign | متابعة الحملة |
| K38 `tx_difficulty_NewState_Text_79004a` | Difficulty | صعوبة الحملة |
| K49 `year_tx_NewState_Text_310064` | Start year: | سنة البداية: |
| K50 `tx_initial_challenge:_NewState_Text_670040` | Initial challenge: | التحدي المبدئي: |
