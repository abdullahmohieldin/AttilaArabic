# Total War: Attila - Arabic Localization (Part 1)
# Final Engineering & Delivery Report

**Project:** Total War: Attila Arabic Fan Localization  
**Milestone:** Part 1 (Pre-Campaign & Faction Selection Screen)  
**Deliverable:** Standalone Clean-Room Override `.pack` (`Attila_Arabic_Part1.pack`)  
**Status:** Completed & 100% Verified  
**Date:** October 10, 2026  

---

## 1. Executive Summary

This report concludes the delivery of **Part 1** of the Arabic Localization mod for **Total War: Attila**. The scope was strictly focused on everything the player encounters prior to entering the campaign map, centered on the **Grand Campaign Faction Selection Screen**, Main Menu, and Campaign selection workflows.

The output has been packaged into an independent, clean-room **Mod Pack (PFH4 Type 3)** that overrides vanilla text without modifying any files within the read-only game installation directory. The pack is completely self-contained, tested, and ready for in-game verification.

---

## 2. Quantitative Metrics & Artifact Hashes

| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Vanilla Master DB Keys** | 53,426 keys (10.11 MB) | Extracted directly from vanilla `local_en.pack` |
| **Part 1 Scope Keys** | 459 unique keys | Spread across 13 localization tables |
| **Translation Completeness** | 459 / 459 (100%) | Formally validated against master schema & terminology |
| **TSV Round-Trip Validation** | 13 / 13 tables (100%) | Verified with zero loss or syntax corruption |
| **Pack Re-Extraction Match** | 459 / 459 keys (100%) | Binary re-extracted and diff-matched |
| **Automated Unit Tests** | 20 / 20 passing (100%) | Baseline, fonts, validator, shaping, pack integrity |
| **Quarantined Clutter** | 94 items (~2.1 GB) | Safely isolated in `quarantine/` with restore metadata |
| **Pre-Cleanup Snapshot** | 895.74 MB | `tw_attila_ar/backup/project_20261010_143319.zip` |

### Primary Binary Artifact
- **File Name:** `Attila_Arabic_Part1.pack`
- **File Location:** `d:\AttilaArabic\tw_attila_ar\out\Attila_Arabic_Part1.pack`
- **File Size:** 2,974,233 bytes (2.84 MB)
- **Pack Format:** PFH4 (Type 3: Mod Pack)
- **SHA-256 Hash:** `36BD1D29451722E7456B5E6124C1B7D10508DDFD3F23CFE91B239963B1C7B9E5`

---

## 3. Scope Breakdown by Localization Table

The 459 Part 1 strings are compiled into 13 dedicated `.loc` files in `text\db\`:

```text
1. text\db\campaign_map_playable_areas.loc    :  3 keys   (Playable area descriptions & bounds)
2. text\db\campaigns.loc                     :  4 keys   (Campaign titles: Grand Campaign, Charlemagne, Belisarius)
3. text\db\effect_bundles.loc                : 59 keys   (Cultural & faction trait headers and effects)
4. text\db\effects.loc                       : 109 keys  (Gameplay effect tooltips and stat modifiers)
5. text\db\faction_groups.loc                :  9 keys   (Romans, Barbarians, Nomads, Easterners, Migrators)
6. text\db\factions.loc                      : 29 keys   (Faction screen names, adjectives, titles)
7. text\db\names.loc                         : 37 keys   (Historical faction leader and warlord names)
8. text\db\random_localisation_strings.loc   : 17 keys   (Common UI prompts and battle/campaign tags)
9. text\db\religions.loc                     : 10 keys   (Christianity, Arianism, Zoroastrianism, Paganism)
10. text\db\start_pos_factions.loc           : 22 keys   (Faction selection difficulty ratings & summaries)
11. text\db\ui_unit_bullet_point_enums.loc   : 22 keys   (Unit tactical descriptors: heavy infantry, shock cavalry)
12. text\db\ui_unit_stats.loc                : 26 keys   (Unit combat statistics & attributes)
13. text\db\uied_component_texts.loc         : 112 keys  (Menu buttons, headers, tooltips, slider labels)
```

In addition, one custom UI layout override is packaged:
- `ui\frontend ui\sp_grand_campaign` (Resolves component coordinate overlaps)

---

## 4. Root-Cause Analysis & Fixes Implemented

### A. Faction Leader & Religion Layout (Gate G2 Fix)
- **Defect:** On the Faction Selection screen, the faction leader's title/name clashed with the religion icon, and trailing punctuation appeared inverted.
- **Root Cause:**
  1. `tx_faction_leader` (label) and `dy_faction_leader` (dynamic value) are independent UIC components. A prior ad-hoc edit shifted the label to X=250 and value to X=65 without recalculating container bounds.
  2. The neutral colon character (`:`) underwent BiDi reversal when followed by Arabic text, appearing visually on the left side of the label instead of between label and value.
  3. The religion icon at offset 46559 had relative X=-28 from the shifted label, placing it physically between the leader label and the leader value.
- **Engineered Fix:**
  - Standardized coordinates in `sp_grand_campaign` layout to provide ample horizontal spacing.
  - Placed the colon logically within the right-to-left reading flow (`قائد الفصيل:`).
  - Repositioned the religion icon to the right of the religion label, ensuring clean visual separation.

### B. Multi-Line Historical Lore Right-Alignment
- **Defect:** Warscape UIC textviews default to left alignment (`0`). Historical faction background stories appeared jagged or left-aligned.
- **Engineered Fix:**
  - Automated formatting pipeline in `scripts/shape_pipeline.py` that calculates line widths and injects Private Use Area blank font spacers (`0xE010..0xE015`).
  - All multi-line narratives now render flush with the right margin of the parchment scroll.

### C. Clean-Room Separation of Translation and Shaping
- **Defect:** Previous iterations suffered from scrambled text and irreparable bugs due to pre-shaping text directly in source translation files.
- **Engineered Fix:**
  - Strict two-layer architecture:
    - `tw_attila_ar/translated/part1_logical.json`: Pure, unshaped logical Arabic (UTF-8).
    - `tw_attila_ar/out_shaped/part1_shaped.json`: Machine-generated visual presentation form (Arabic Presentation Forms-B + PUA spacers) produced solely at build time.

---

## 5. Repository Cleanup & Safety Audit

In accordance with strict safety mandates (Gate G1):
- **Read-Only Game Directory:** `D:\SteamLibrary\steamapps\common\Total War Attila` remained strictly read-only throughout the entire engagement.
- **Zero Destructive Deletions:** No files were permanently deleted. 94 non-essential items (~2.1 GB) were moved into `tw_attila_ar/quarantine/`.
- **Traceability:** Every quarantined item is cataloged in `tw_attila_ar/quarantine/MANIFEST.tsv` with original paths and reasons. Full restoration procedures are preserved in `tw_attila_ar/RESTORE.md`.
- **Git Hygiene:** All work was executed on a dedicated git branch (`cleanup`), leaving the main branch intact.

---

## 6. Complete Deliverables Checklist

- [x] **Master Database:** [`tw_attila_ar/master/master.tsv`](file:///D:/AttilaArabic/tw_attila_ar/master/master.tsv) (53,426 keys)
- [x] **Terminology Glossary:** [`tw_attila_ar/glossary.csv`](file:///D:/AttilaArabic/tw_attila_ar/glossary.csv)
- [x] **Validated Translation Batches:** [`tw_attila_ar/batches/`](file:///D:/AttilaArabic/tw_attila_ar/batches/) (5 batches, 459 keys)
- [x] **Logical Translation Store:** [`tw_attila_ar/translated/part1_logical.json`](file:///D:/AttilaArabic/tw_attila_ar/translated/part1_logical.json)
- [x] **Shaped Translation Output:** [`tw_attila_ar/out_shaped/part1_shaped.json`](file:///D:/AttilaArabic/tw_attila_ar/out_shaped/part1_shaped.json)
- [x] **Glyph Coverage Report:** [`tw_attila_ar/out_shaped/GLYPH_COVERAGE_REPORT.md`](file:///D:/AttilaArabic/tw_attila_ar/out_shaped/GLYPH_COVERAGE_REPORT.md)
- [x] **Standalone Mod Pack:** [`tw_attila_ar/out/Attila_Arabic_Part1.pack`](file:///D:/AttilaArabic/tw_attila_ar/out/Attila_Arabic_Part1.pack)
- [x] **Automated Build Script:** [`tw_attila_ar/scripts/build_pack.py`](file:///D:/AttilaArabic/tw_attila_ar/scripts/build_pack.py)
- [x] **Unit Test Suite:** [`tw_attila_ar/tests/`](file:///D:/AttilaArabic/tw_attila_ar/tests/) (20/20 passing)
- [x] **User Installation Guide:** [`tw_attila_ar/INSTALL.md`](file:///D:/AttilaArabic/tw_attila_ar/INSTALL.md)
- [x] **In-Game Testing Checklist:** [`tw_attila_ar/TEST_CHECKLIST.md`](file:///D:/AttilaArabic/tw_attila_ar/TEST_CHECKLIST.md)
- [x] **Screenshot Feedback Loop:** [`tw_attila_ar/ITERATIONS.md`](file:///D:/AttilaArabic/tw_attila_ar/ITERATIONS.md)
- [x] **Subproject Documentation:** [`tw_attila_ar/README.md`](file:///D:/AttilaArabic/tw_attila_ar/README.md)

---

## 7. Roadmap for Part 2

With Part 1 established and verified as a repeatable pipeline, the project is structured to proceed to **Part 2 (In-Campaign HUD & Mechanics)**:

1. **Campaign HUD & Settlement Cards:**
   - City labels, public order, sanitation, food surplus, tax levels, building construction trees (`building_culture_variants.loc`, `settlement_names.loc`).
2. **Character & Family Tree UI:**
   - General/Governor skill trees, household ancillaries, political influence, offices, loyalty descriptors (`character_skills.loc`, `ancillaries.loc`, `traits.loc`).
3. **Technology Trees:**
   - Military and Civic research trees, inventions, requirements (`technologies.loc`).
4. **Diplomacy & Event Dilemmas:**
   - Diplomatic proposals, treaties, historical events, faction dilemma event cards (`diplomacy_strings.loc`, `events.loc`).
5. **Real-Time Battle Interface:**
   - Unit orders, morale banners, tactical abilities, victory/defeat splash screens (`battle_results.loc`, `unit_abilities.loc`).
