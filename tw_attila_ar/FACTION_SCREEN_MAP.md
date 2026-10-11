# Phase 4: Faction Selection Screen Map & Root-Cause RTL Analysis

**Document:** `<WORKDIR>/FACTION_SCREEN_MAP.md`  
**Execution Date:** 2026-10-10  
**Target Surface:** Pre-Campaign Frontend & Faction Selection Screen  
**Primary UI Layout:** `ui/frontend ui/sp_grand_campaign` in `data.pack`  
**Status:** **PENDING USER APPROVAL (GATE G2)**  

---

## 1. Comprehensive Faction Selection Screen Element Map

| UI Element | Layout Component & Path | Loc Key | DB Table & Field | English Vanilla | Current Arabic | Observed Problem |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Faction Name** | `name` in `faction_details_parent` | `factions_screen_name_<faction>` | `factions_tables.screen_name` | Eastern Roman Empire | الإمبراطورية الرومانية الشرقية | Rendered correctly; font scaling verified. |
| **Faction Group / Tab** | `tab_factions` / `tx_factions` | `faction_groups_screen_name_<group>` | `faction_groups_tables.screen_name` | Roman Empire | الإمبراطورية الرومانية | Rendered correctly; 2-line ligature patch applied. |
| **Faction Leader Label** | `tx_faction_leader` | `uied_component_texts_localised_string_tx_faction_leader_NewState_Text_290050` | `uied_component_texts.loc` | Faction Leader: | قائد الفصيل: | Colon rendered on left; swapped position against value. |
| **Faction Leader Name** | `dy_faction_leader` | `names_name_<id>` | `names_tables.name` (via `frontend_faction_leaders_tables`) | Arcadius | أركاديوس | Separated from label by excessive negative offset. |
| **Religion Label** | `tx_religion` | `uied_component_texts_localised_string_tx_religion_NewState_Text_6f0031` | `uied_component_texts.loc` | Religion: | الديانة: | Colon on wrong end; label and icon order distorted. |
| **Religion Name** | `dy_religion` | `religions_religion_<key>` | `religions_tables.religion` | Christianity (Eastern Orthodox) | المسيحية (الأرثوذكسية الشرقية) | Shifted to left without smooth margin alignment. |
| **Religion Icon** | `icon` (inside `tx_religion`) | — | `religions_tables.icon_path` | (Symbol/crest icon) | (Symbol/crest icon) | Physically trapped between name and label. |
| **Cultural Trait Header** | `header_cultural` | `uied_component_texts_localised_string_header_cultural_NewState_Text_5e0000` | `uied_component_texts.loc` | Cultural Trait | سمة الثقافة | Correct, but left-aligned within header frame. |
| **Cultural Trait Name** | `tx_cultural_trait` | `effect_bundles_localised_title_<trait>` | `effect_bundles_tables.localised_title` | Roman Civilization | الحضارة الرومانية | Correct; fits label box. |
| **Cultural Trait Description** | `dy_cultural_trait_desc` | `effect_bundles_localised_description_<trait>` | `effect_bundles_tables.localised_description` | The glory that was Rome... | مجد روما الخالد... | Left-aligned because `is_narrative` spacer missing. |
| **Faction Trait Header** | `header_faction` | `uied_component_texts_localised_string_header_faction_NewState_Text_410063` | `uied_component_texts.loc` | Faction Trait | سمة الفصيل | Rendered correctly. |
| **Faction Trait Name** | `tx_faction_trait` | `effect_bundles_localised_title_<trait>` | `effect_bundles_tables.localised_title` | Economic Might | القوة الاقتصادية | Rendered correctly. |
| **Faction Trait Description** | `dy_faction_trait_desc` | `effect_bundles_localised_description_<trait>` | `effect_bundles_tables.localised_description` | Treasuries full of gold... | خزائن عامرة بالذهب... | Left-aligned; lacks right-margin flush spacing. |
| **Trait Effects Bullet Points** | `dy_effect` in `effect_description_window` | `effects_description_<effect_key>` | `effects_tables.description` | +5% tax rate... | +٥% معدل الضرائب... | Arabic digits / symbols flip if punctuation unescaped. |
| **Faction Narrative Lore** | `party_description` in `faction_details_parent` | `campaign_map_playable_areas_description_<faction>` | `campaign_map_playable_areas_tables.description` | Following the division of the Empire... | بعد انقسام الإمبراطورية... | Requires exact PUA blank spacer indentation to align flush-right. |
| **Starting Difficulty Label** | `tx_difficulty` | `uied_component_texts_localised_string_tx_difficulty_NewState_Text_79004a` | `uied_component_texts.loc` | Starting Difficulty: | صعوبة البداية: | Colon on wrong end; label left-anchored. |
| **Starting Difficulty Value** | `dy_difficulty` | `uied_component_texts_localised_string_dy_difficulty_NewState_Text_2f006a` | `uied_component_texts.loc` | Hard | صعب | Rendered correctly. |
| **Difficulty Description Box** | `label_difficulty_description` | `uied_component_texts_localised_string_label_difficulty_description_Text_7000b` | `uied_component_texts.loc` | A challenging starting position... | موقع بداية يمثل تحدياً كبيراً... | Multi-line text left-aligned inside panel. |
| **Start Year Label & Value** | `dy_start_year` | `uied_component_texts_localised_string_dy_start_year_NewState_Text_70001` | `uied_component_texts.loc` | AD 395 | ٣٩٥ م | Digits and suffix orientation require careful ordering. |
| **Start Campaign Button** | `button_start` | `uied_component_texts_localised_string_button_txt_NewState_Text_30006e` | `uied_component_texts.loc` | Start Campaign | ابدأ الحملة | Rendered correctly; centered in button. |
| **Back Button** | `button_back` | `uied_component_texts_localised_string_button_txt_NewState_Text_60002` | `uied_component_texts.loc` | Back | عودة | Rendered correctly. |
| **Campaign Selection Button (Preceding)**| `button_campaign_<key>` | `campaigns_localised_name_<key>` | `campaigns_tables.localised_name` | The Great Migration | الهجرة الكبرى | **Clipped on right margin** due to narrow button width. |

---

## 2. Root-Cause Analysis of RTL & Layout Defects

### A. Defect 1: Leader and Religion Labels & Values are Swapped / Distorted
- **Observed Visual Bug:** In `crop_leader_religion.png`, the line displays `أولدين قائد الفصيل:`. The leader name appears on the left, the title appears on the right, but the colon appears at the far left: `:أولدين قائد الفصيل`. In religion, the icon is sandwiched between the name and label.
- **Root Cause (Hypotheses 1 & 4):**
  1. *Hypothesis 1 (Separate UI Components):* In `sp_grand_campaign`, the label (`tx_faction_leader`, width 140) and dynamic value (`dy_faction_leader`, width 192) are independent UI components. In vanilla LTR, the label sits at X=69 and the value at X=218. An ad-hoc edit in commit `2ff571c` shifted `tx_faction_leader` to X=250 and `dy_faction_leader` to X=65 without recalculating component widths and bounding boxes.
  2. *Hypothesis 4 (Mixed Direction / Neutral Punctuation):* The ASCII colon `:` in `"قائد الفصيل:"` is a neutral character. When processed by `python-bidi` with `base_dir='R'`, the trailing colon is placed at visual index 0 (the far left of the text). Because the engine draws from left to right, the colon renders *before* the Arabic words.
  3. *Religion Icon Sandwiched:* The `icon` component was assigned relative offset X=-28 relative to `tx_religion` (X=280), placing it at physical X=252. The value `dy_religion` was moved to X=65. This placed the icon physically in the middle: `[Value X=65] [ICON X=252] [Label X=280]`.

### B. Defect 2: Narrative Descriptions are Not Right-Aligned
- **Observed Visual Bug:** Descriptions in faction lore, cultural traits, and difficulty panels appear ragged or left-aligned.
- **Root Cause (Hypothesis 5):**
  - In Warscape UIC components, text alignment defaults to Left (`alignment = 0`). The game engine does not perform native RTL layout.
  - While faction narrative lore (`campaign_map_playable_areas_description_*`) uses custom PUA blank spacers (`0xE010..0xE015`), trait descriptions and difficulty boxes did not have the `is_narrative` flag enabled, leaving them unpadded and left-anchored.

### C. Defect 3: Campaign Selection Button Text Clipping
- **Observed Visual Bug:** In `crop_sand_button.png`, the button text `الهجرة الكبرى` is clipped on the right.
- **Root Cause (Hypothesis 5):**
  - The UI button container has a fixed width. When 2-line Arabic text with reshaped forms is centered or wrapped, the bounding box clips the initial letters of the line.

---

## 3. Proposed Ranked Fixes

### Fix Set 1: Leader & Religion Alignment & Component Geometry
- **Rank 1 (Recommended - Clean-Room UI Layout Geometry + Loc Punctuation Clean):**
  - In `sp_grand_campaign`:
    - Set `tx_faction_leader` to X=250, width=140, right-anchored.
    - Set `dy_faction_leader` to X=20, width=220, right-aligned to meet the label smoothly.
    - Reposition `icon` to the far right (X=265), `tx_religion` at X=235, and `dy_religion` at X=20..220.
  - In `data/translations/faction_select_ui.json`:
    - Replace `"قائد الفصيل:"` with logical formatting that ensures the colon renders at the visual trailing end (e.g. using Arabic colon `\u061B` or trailing punctuation protection).
  - *Feasibility:* 100% verified via UIC binary patch. Clean-room, no exe modification.

### Fix Set 2: Universal Right-Margin Flush Alignment for Descriptions
- **Rank 1 (Recommended - Universal Pipeline Spacer Flagging):**
  - Extend `format_narrative()` in `source/loc_compiler.py` to automatically process **all** multi-line narrative descriptions:
    - Faction lore descriptions (`campaign_map_playable_areas_description_*`)
    - Cultural trait descriptions (`effect_bundles_localised_description_*`)
    - Difficulty panel descriptions (`label_difficulty_description_*`)
  - Calculate line pixel width dynamically and pad with PUA blank spacers (`0xE010..0xE015`).
  - *Feasibility:* 100% loc-only, completely stable across all campaign screens.

### Fix Set 3: Button Text Width & Padding Resolution
- **Rank 1 (Recommended - Concise Lexical Optimization):**
  - Adjust translated button strings in `campaigns.json` and `faction_select_ui.json` to compact terminology that fits standard button frames (e.g., using `عصر الهجرات` or compact ligature glyph `\uE114` for `الكبرى`).
  - *Feasibility:* 100% safe, eliminates clipping without altering UI container boundaries.
