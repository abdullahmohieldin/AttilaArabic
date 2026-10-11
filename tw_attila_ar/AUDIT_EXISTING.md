# Phase 3 Audit: Existing Arabic Localization Pipeline & Translation Tables

**Document:** `<WORKDIR>/AUDIT_EXISTING.md`  
**Execution Date:** 2026-10-10  
**Baseline Dataset:** `data/translations/*.json` (12 Modular Catalogs)  
**Comparison Master:** `tw_attila_ar/master/master.tsv` (53,426 Vanilla Entries)  

---

## 1. Key Coverage & Master Table Verification

Every translation file in `data/translations/` was cross-referenced against the master extract of Total War: Attila (`local_en.pack`).

| Translation File | Keys Count | In Master | Master % | Placeholder Errors | Latin Leftovers |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `campaigns.json` | 7 | 7 | 100.0% | 0 | 0 |
| `custom_battle.json` | 16 | 16 | 100.0% | 0 | 0 |
| `faction_descriptions.json` | 14 | 14 | 100.0% | 0 | 0 |
| `faction_groups.json` | 9 | 9 | 100.0% | 0 | 0 |
| `faction_select_ui.json` | 115 | 115 | 100.0% | 0 | 0 |
| `faction_traits_effects.json` | 109 | 109 | 100.0% | 0 | 0 |
| `factions.json` | 29 | 29 | 100.0% | 0 | 0 |
| `leaders_and_campaign.json` | 59 | 59 | 100.0% | 0 | 0 |
| `main_menu.json` | 38 | 38 | 100.0% | 0 | 0 |
| `settings_and_options.json` | 35 | 35 | 100.0% | 0 | 0 |
| `unit_ratings.json` | 43 | 43 | 100.0% | 0 | 0 |
| `unit_stats.json` | 26 | 26 | 100.0% | 0 | 0 |
| **TOTAL** | **500** | **500** | **100.0%** | **0** | **0** |

- **Invalid / Phantom Keys:** 0. All 500 keys exist in the official game `.loc` tables.
- **Placeholder Parity:** 100% of printf specifiers (`%s`, `%d`) match 1:1 between English and Arabic.
- **Latin Residue:** 0 unintended English words or stray characters.
- **Encoding Quality:** 100% valid UTF-8. No BOM corruption, zero mojibake.

---

## 2. Text Representation Layer (Source vs Compiled)

- **Source Storage Form:**
  - 100% of the 500 entries are stored in **Canonical Base Arabic (`U+0600..U+06FF`) in logical reading order**.
  - Exactly 0 Presentation Forms-B (`U+FE70..U+FEFF`), 0 reversed character strings, and 0 directional marks exist in the source JSON files.
- **Compiled Form Transformation:**
  - Transformation happens exclusively at compile time via `source/shape.py` and `source/loc_compiler.py`.
  - Stage 1: Protect formatting tokens (`[[col:...]]`, `%s`, `%d`) using private marker `\uE000`.
  - Stage 2: `arabic_reshaper.reshape()` substitutes base characters into contextual glyph variants (Presentation Forms-B).
  - Stage 3: `bidi.algorithm.get_display(..., base_dir='R')` reverses the reading order into visual left-to-right sequence required by Warscape's LTR text rasterizer.
  - Stage 4: Multi-line narratives calculate rendered pixel width against panel width (340 px) and prepend PUA blank spacers (`0xE010..0xE015`) to achieve flush-right appearance.

---

## 3. Font Glyph Coverage vs Shipped Codepoints

- **Upstream Typeface:** Tajawal Regular (`fonts/upstream/Tajawal-Regular.ttf`, 446 glyphs).
- **Target Codepoints:** All Presentation Forms-B glyphs required for standard MSA are present.
- **Fallback Resolution:** Canonical isolated letters missing in TTF `cmap` (`0xFE8D` Alef, `0xFEAD` Reh, `0xFEED` Waw, `0xFE80` Hamza) are safely resolved to base codepoints via `cr_phase1_build.py`.
- **Ligature Extension:** Specialized PUA codepoints (`0xE110..0xE115`) provide seamless ligatures for tight UI spaces (`الفصائل`, `الشرقية`).

---

## 4. Screenshot Evidence & Defect Analysis

| Defect Observed | Screenshot Evidence | Mechanism | Impact |
| :--- | :--- | :--- | :--- |
| **Swapped Leader & Religion Layout** | `scratch/crop_leader_religion.png` | Manual layout X-coordinate shift inverted relative positions without anchoring. | Leader label and value appear reversed; colons render on wrong end. |
| **Religion Icon Sandwiched** | `scratch/crop_leader_religion.png` | Icon X offset (-28 px) sits between shifted label (X=280) and value (X=65). | Visual sequence is: `[Value] [ICON] [Label:]` rather than `[ICON] [Label:] [Value]`. |
| **Button Text Clipping** | `scratch/crop_sand_button.png` | Campaign selection button has fixed width; 2-line Arabic wrap clips right boundary. | `الهجرة الكبرى` truncated on the right margin. |
| **Description Left-Alignment** | In-game lore boxes | Engine lacks native right-alignment; unflagged descriptions receive no spacers. | Shorter lines appear left-ragged unless padded with PUA spacers. |

---

## 5. Verdict: SALVAGE & ENHANCE

- **Verdict:** **SALVAGE**.
- **Rationale:** The underlying translation catalog (500 strings across all frontend screens) is exceptionally high quality, strictly adhering to formal MSA, with 100% verified key coverage against vanilla Attila tables.
- **Action:** Retain all source translations in `data/translations/`. Fix the layout and BiDi punctuation bugs at the UI component level and shaping compiler level.
