# Test Pack Manifest — v1 (loc-only, NO CUF)

Pack: `D:\AttilaArabic\release\Attila_Arabic_POC_v1.pack`
SHA256: `1967C08D2C72495F5065A975ADB4DD04EC47C0C440A0D16DB9A3D644AB8CA5B1`
Format: PFH4, type `mod (3)`, 3 files, 0 dependencies.
Built by: `source\build_v1.py` (reproducible; inputs = working copy of
vanilla `local_en.pack` + `source\shape.py` with arabic-reshaper 3.0.1 /
python-bidi 0.6.11).
Vanilla files changed: NONE (full-file copies with 4 edited rows; entry
counts and tooltip flags identical to vanilla — verified by re-extract).

## Overridden resources

| # | Internal path | Key | Vanilla (logical) | Override (logical Arabic) | Where to see it |
|---|---------------|-----|-------------------|---------------------------|-----------------|
| 1 | `text\db\uied_component_texts.loc` | `…_string_NewState_Text_1c0025` | `Prologue` | القاهرة | Main menu item |
| 2 | `text\db\uied_component_texts.loc` | `…_mp_tx_NewState_Text_75002f` | `Multiplayer` | Rome 1200 — روما | Main menu item (AR+EN) |
| 3 | `text\db\factions.loc` | `factions_screen_name_att_fact_western_roman_empire` | `Western Roman Empire` | الجيش الأول: 1200 جندي | Grand-campaign faction list, WRE entry (AR+numbers) |
| 4 | `text\db\start_pos_factions.loc` | `start_pos_factions_long_description_2120156339` | 945-char WRE English text | 284-char Arabic paragraph (parens (395م), em-dash, 1200, 25%) | Faction-select description panel for WRE (long wrap test) |

Stored text is pre-shaped visual order (Presentation Forms + bidi);
no font files in this pack — vanilla `arialunicode_*` renders it.

## What to report from the game test

Joining / RTL order / AR+EN / AR+numbers / punctuation-parens /
multiline wrap + line order / clipping / tofu / alignment.
Screenshots go in `D:\AttilaArabic\screenshots\`.
