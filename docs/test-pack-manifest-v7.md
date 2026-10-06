# Test Pack Manifest v7

## Packs to copy into `data\`

| # | Pack file | What it does | Tick in |
|---|-----------|--------------|---------|
| 1 | `release\Attila_Arabic_POC_v7_fonts.pack` | Arabic glyphs, 1px join overlap, yeh dot boost | `mod manager` |
| 2 | `release\Attila_Arabic_POC_v7.pack` | Arabic strings, 280px wrap, right-align probe | `mod manager` |

> Only ONE font pack at a time. Remove v6 (and v5) font packs before adding v7. Copy both packs and tick both in the mod manager.

---

## Build details

| Item | Value |
|------|-------|
| Script | `source/build_v7.py` (v6 files untouched) |
| Font build dir | `build/v7fonts/` |
| Loc build dir | `build/v7/` |
| Fonts pack | `release/Attila_Arabic_POC_v7_fonts.pack` (SHA256 `26391316CEB483A9C417FAF2940FDCA782C75FBB65363CD242B6EE5CB8BAB995`) |
| Loc pack | `release/Attila_Arabic_POC_v7.pack` |
| vanilla SHA256 before/after | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` VERIFIED |

Changes vs v6:
- Fonts: connecting forms `adv = ink_width - 1` (1px overlap), left=0 kept. Yeh family (U+FEF1/FEF2/U+064A) alpha x1.6 dot boost (INFERENCE).
- Loc: all long strings re-wrapped at 280px (was 310 desc / 350 difficulty). WRE 8 lines, ERE 9 lines, each difficulty 2 lines. No trailing LF.
- Right-align probe (UNVERIFIED, engine may trim leading spaces): every WRE/ERE line + `stat_melee_attack` (35 spaces, 277/280) + `stat_armour` (49 spaces, 278/280) padded with leading spaces. georgia_italic_12 space=4px, la_gioconda_12 space=5px. Centered text NOT padded.
- Source Yeh is already U+064A (VERIFIED); final loc uses U+FEF2 (VERIFIED). No codepoint change.

---

## Screens to check

| Screen | What to verify |
|--------|----------------|
| Faction select WRE description | Right edge aligned? Orphan words gone? ("الخطر", "الدولة.", "انتقل" no longer orphaned?) |
| Faction select ERE description | Same; dots on final yeh visible? ("الروماني", "القسطنطينية") |
| Unit Info labels | `هجوم الاشتباك`, `الدرع` right-aligned or trimmed? (probe: 35/49 leading spaces) |
| Difficulty texts | 2 lines each, centered, no pad; Very Hard line1 (`الأعداء.`) position |
| Tabs | 2 lines each, unchanged from v6 |
| Joins | `الإمبراطوريات`, `تخطيطا دقيقا` joins closed? |
| Still English (keys found, not translated) | Roman Expedition tabs/desc, Purchase Campaign, Normal value, unit stat tooltip |

---

## Test results (before releasing)

| Test | Result |
|------|--------|
| `test_key_mapping` (4 tests) | PASS on v6 files (untouched) |
| `test_join_continuity` (2 tests) | PASS (0 overshoots all v6 fonts; gioconda_12 0 failed joins) |
| `test_baseline_regression` (1 test) | PASS |
| `v3_check` v7fonts (684 codepoints x31) | ALL FONTS PASS |
| `v3_check` v6fonts | ALL FONTS PASS |
| vanilla SHA256 before/after | VERIFIED |
| v7 overshoot (31 fonts) | 0 overshoots VERIFIED |
| v7 glyph sheet `docs/v7_glyph_sheet_geo12_v7.png` | 0/28 non-real, YEH final real VERIFIED |
