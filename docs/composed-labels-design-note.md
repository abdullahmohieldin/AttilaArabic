# Design Note: Composed Labels & UI Key Concatenation

## Problem Statement (VERIFIED by Game Tests)

Total War: ATTILA's UI engine composes complex labels at runtime by joining separate localized strings via hardcoded engine formatting strings or simple string concatenation (e.g. `rating + " " + stat_name`).

In earlier test packs, unit stats appeared on screen as:
`"Excellent الدرع"` (or `"Very High <Arabic> U03"`)

This reveals how the game engine handles compound labels:
1. **Engine Concatenation Order (VERIFIED)**:
   - The engine concatenates `[Rating string] [Stat string]` from left to right.
2. **Visual RTL Reversal (INFERENCE)**:
   - In English LTR reading: the left string is read first, then the right string (`[Rating: Excellent] [Stat: Armour]`).
   - When Arabic is pre-shaped into visual order and rendered by the engine's LTR layout, the engine places `[Rating: ممتاز]` on the left and `[Stat: الدرع]` on the right.
   - An Arabic reader reading RTL reads the right element first and the left element second: `[الدرع] [ممتاز]` ("Armour: Excellent"), which naturally matches Arabic adjective-after-noun syntax.

---

## Screen-Verified Key Analysis

### 1. Unit Info Bullet Point Ratings & Stats (VERIFIED)
- **Qualitative Rating Keys** (`text\db\ui_unit_bullet_point_enums.loc`):
  - Real keys verified from database:
    - `ui_unit_bullet_point_enums_onscreen_name_att_excellent` ("Excellent") -> `ممتاز`
    - `ui_unit_bullet_point_enums_onscreen_name_att_good` ("Good") -> `جيد`
    - `ui_unit_bullet_point_enums_onscreen_name_att_average_positive` ("Average") -> `متوسط`
    - `ui_unit_bullet_point_enums_onscreen_name_att_average_negative` ("Average") -> `متوسط`
    - `ui_unit_bullet_point_enums_onscreen_name_att_poor` ("Poor") -> `ضعيف`
    - `ui_unit_bullet_point_enums_onscreen_name_att_very_poor` ("Very Poor") -> `ضعيف جداً`
    - `ui_unit_bullet_point_enums_onscreen_name_att_high` ("High") -> `مرتفع`
    - `ui_unit_bullet_point_enums_onscreen_name_att_very_high` ("Very High") -> `مرتفع جداً`
    - `ui_unit_bullet_point_enums_onscreen_name_att_low` ("Low") -> `منخفض`
    - `ui_unit_bullet_point_enums_onscreen_name_att_very_low` ("Very Low") -> `منخفض جداً`
- **Stat Names** (`text\db\ui_unit_stats.loc`):
  - `ui_unit_stats_onscreen_name_stat_armour` ("Armour") -> `الدرع`
  - `ui_unit_stats_onscreen_name_stat_health` ("Health") -> `الصحة`
  - `ui_unit_stats_onscreen_name_stat_morale` ("Morale") -> `المعنويات`
  - `ui_unit_stats_onscreen_name_stat_speed` ("Speed") -> `السرعة`
  - `ui_unit_stats_onscreen_name_stat_melee_attack` ("Melee Attack") -> `هجوم الاشتباك`
  - `ui_unit_stats_onscreen_name_stat_melee_defence` ("Melee Defence") -> `دفاع الاشتباك`

### 2. Disproven Concatenation Claim: Initial Challenge (VERIFIED)
- **Correction**: An earlier draft claimed that `"Initial challenge:"` was concatenated by the engine with the difficulty rating into a single compound label string.
- **Screen Verification**: Examination of screenshots (1920x1080) proves that:
  - `"Initial challenge:"` (`uied_component_texts_localised_string_tx_initial_challenge:_NewState_Text_670040`) is a **separate UI widget** (K50).
  - The difficulty rating text (`"Normal"`, `"Hard"`, etc.) sits in its own dedicated label widget.
  - They are NOT concatenated into one localized string by the game.

---

## Summary of Rules for Localizing Composed Labels

1. **Standalone Localized Keys**: Both rating enums and unit stat labels are pre-shaped as standalone Arabic visual strings.
2. **LTR Layout Inversion**: The engine's LTR layout of `[Rating] [Stat]` renders in visual space with `Rating` at low X and `Stat` at higher X. Because Arabic is read right-to-left, the eye encounters `Stat` first and `Rating` second, naturally preserving Arabic grammar without code injection or layout modification.
