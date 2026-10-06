# Test Pack Manifest v8

## Packs to copy into `data\`

| # | Pack file | What it does | Tick in |
|---|-----------|--------------|---------|
| 1 | `release\Attila_Arabic_POC_v8_fonts.pack` | Arabic glyphs, 1px join overlap, yeh dot boost | `mod manager` |
| 2 | `release\Attila_Arabic_POC_v8.pack` | Arabic strings, R* width model, right-align probe | `mod manager` |
| 3 | `release\Attila_Arabic_POC_v8_ruler.pack` | Ruler probe (loc-only, run with v8 fonts) | `mod manager` |

> Only ONE font pack at a time. Remove v7/v6/v5 font packs before adding v8. Copy all three packs and tick all in the mod manager (ruler is loc-only, no font conflict).

---

## Build details

| Item | Value |
|------|-------|
| Script | `source/build_v8.py` (v6/v7 files untouched) |
| Font build dir | `build/v8fonts/` |
| Loc build dir | `build/v8/` |
| Fonts pack | `release/Attila_Arabic_POC_v8_fonts.pack` (SHA256 `26391316CEB483A9C417FAF2940FDCA782C75FBB65363CD242B6EE5CB8BAB995`) |
| Loc pack | `release/Attila_Arabic_POC_v8.pack` (SHA256 `051F62B3E52AB5B96D9020A95FFC563E55F04E66E821BAD0FCB820E061D15C17`) |
| Ruler pack | `release/Attila_Arabic_POC_v8_ruler.pack` (SHA256 `DA7CE6E0FFF118F765D8D5D070B8B586BC071CDF3B5DF5B66476E74DC222655E`) |
| vanilla SHA256 before/after | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` VERIFIED |

Changes vs v7:
- Fonts: same as v7 (1px join overlap, yeh dot boost).
- Width model R* (INFERENCE from 6-line fit ≤1.1%):
  - georgia_italic_12: every ADDED Arabic glyph +2.48 px (space=4, Latin unchanged)
  - la_gioconda_12: every ADDED Arabic glyph +1.32 px (space=5, Latin unchanged)
- Wrap at 280 model px:
  - descriptions (geo12): 8 lines WRE, 12 lines ERE (was 8/9), padded right to min(280,320) model px
  - difficulty (lgi12): 2 lines each, NOT padded (centered)
- Right-align probe (UNVERIFIED: engine may trim leading spaces):
  - WRE/ERE desc lines padded to min(280, engine_cap) model px (geo12 cap=320)
  - Unit Info labels padded to longest label (stat_melee_attack 13.64px), cap at lgi12 engine 350
  - Centered text (difficulty, tabs, headers) NOT padded
- Ruler pack (loc-only): ERE desc key (`start_pos_factions_description_2120156326`) + Hard diff key (`random_localisation_strings_string_campaign_difficulty_description_2`) with 3 test strings each:
  - 20× medial beh U+FE92 (joining)
  - 20× isolated alef U+FE8D (non-joining)
  - isolated alef + 20 spaces + isolated alef (space advance)
- Roman Expedition desc key added: `start_pos_factions_description_2120156889` + `..._long_description_...`
- Source Yeh U+064A confirmed; no codepoint change needed.

---

## Screens to check

| Screen | What to verify |
|--------|----------------|
| Faction select WRE description | Right edge aligned? Orphan words gone? ("الخطر", "الدولة.", "انتقل" no longer orphaned?) |
| Faction select ERE description | Same; dots on final yeh visible? ("الروماني", "القسطنطينية") |
| Unit Info labels | `هجوم الاشتباك`, `الدرع` right-aligned or trimmed? |
| Difficulty texts | 2 lines each, centered, no pad; Very Hard line1 (`الأعداء.`) position |
| Tabs | 2 lines each, unchanged from v6 |
| Joins | `الإمبراطوريات`, `تخطيطا دقيقا` joins closed? |
| Still English (keys found, not translated) | Roman Expedition tabs/desc, Purchase Campaign, Normal value, unit stat tooltip |
| Ruler measurement | ERE desc: measure 20×beh width /20, 20×alef width /20, space width; Hard diff: same for lgi12 |

---

## Test results (before releasing)

| Test | Result |
|------|--------|
| `test_key_mapping` (4 tests) | PASS (v6 key mapping unchanged) |
| `test_join_continuity` (2 tests) | PASS (0 overshoots, 0 failed joins in gioconda_12) |
| `test_baseline_regression` (1 test) | PASS |
| `v3_check` v8fonts (684 codepoints ×31) | ALL FONTS PASS |
| `v3_check` v6fonts | ALL FONTS PASS |
| vanilla SHA256 before/after | VERIFIED |
| v8 overshoot (31 fonts) | 0 overshoots VERIFIED |
| glyph sheet `docs/v7_glyph_sheet_geo12_v7.png` (regenerated from v8) | 0/28 non-real, YEH final real VERIFIED |