# Design Note: Composed Labels & UI Key Concatenation

## Problem Statement (VERIFIED by Game Tests)

Total War: ATTILA's UI engine composes complex labels at runtime by joining separate localized strings via hardcoded engine formatting strings or simple string concatenation (e.g. `"{0} {1}"` or `rating + " " + stat_name`).

In earlier test packs, unit stats appeared on screen as:
`"Very High <Arabic> U03"`

This reveals two fundamental conflicts with Arabic localization:

1. **Syntactic Ordering (Adjective vs Noun)**:
   - English syntax puts the qualifying adjective before the noun: `[Adjective: Very High] [Noun: Health]`.
   - Arabic syntax requires the noun to precede the qualifying adjective: `[Noun: الصحة] [Adjective: عالية جداً]`.
   - If keys are translated independently without reordering, the engine's LTR concatenation produces `عالية جداً صحة` (grammatically invalid Arabic).

2. **Bidirectional (BiDi) Boundary Scrambling**:
   - Because the engine performs no internal BiDi reordering, Arabic strings must be pre-shaped into Arabic Presentation Forms and ordered visually LTR.
   - When the engine concatenates an untranslated or LTR Latin string (`"Very High "`) with a pre-shaped visual RTL string, or joins two independently pre-shaped strings with a space, the word order is scrambled visually in game.

---

## Which Keys Are Joined (VERIFIED / DOCUMENTED)

### 1. Unit Stat Qualitative Ratings + Stat Names
- **Stat Names** (`text\db\ui_unit_stats.loc`):
  - `ui_unit_stats_onscreen_name_stat_melee_attack` ("Melee Attack")
  - `ui_unit_stats_onscreen_name_stat_melee_defence` ("Melee Defence")
  - `ui_unit_stats_onscreen_name_stat_armour` ("Armour")
  - `ui_unit_stats_onscreen_name_stat_health` ("Health")
  - `ui_unit_stats_onscreen_name_stat_morale` ("Morale")
  - `ui_unit_stats_onscreen_name_stat_speed` ("Speed")
- **Qualitative Ratings** (`text\db\uied_component_texts.loc`):
  - `uied_component_texts_localised_string_prediction_accuracy_very_high_Text_...` ("Very high")
  - `uied_component_texts_localised_string_prediction_accuracy_very_low_Text_...` ("Very low")
  - Rating levels in UI layouts (`Poor`, `Average`, `Good`, `Very High`).

### 2. Header and Value Concatenations
- **Initial Challenge**:
  - Key: `uied_component_texts_localised_string_tx_initial_challenge:_NewState_Text_670040` (`"Initial challenge: "`)
  - Joined with difficulty rating string (e.g. `"Normal"`, `"Hard"`).
- **Faction Leader Title**:
  - Key: `uied_component_texts_localised_string_heading_tx_NewState_Text_79004a` (`"Faction Leader"`)
  - Joined or paired with character names in `names.loc`.

---

## Solution Strategies

### Approach A: Whole-Phrase Contextual Strings (Recommended for UI Tooltips)
Where a UI element allows a single format template (e.g. `"{0}: {1}"`), customize the template so the entire clause forms a cohesive Arabic sentence.

### Approach B: Colon-Separated Neutral Keys
When two independent database keys are joined at runtime:
1. Translate the rating adjective in a neutral nominal form or translate the stat label with a trailing separator.
2. For stat labels in unit cards, use concise standalone terms (e.g. `الصحة`, `الدرع`, `هجوم الاشتباك`).
3. For composed descriptions, localize the composite UI layout templates rather than individual fragment keys where possible.
