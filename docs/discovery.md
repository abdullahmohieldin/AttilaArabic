# Phase 0 Discovery Report — Total War: ATTILA Arabic Localization

**Date:** 2026-10-09  
**Status:** COMPLETE (Gate 0)  
**Standard:** Every claim labeled `VERIFIED` / `DOCUMENTED` / `INFERENCE` / `UNVERIFIED`.

---

## 1. Access Verification & Environment

| Item | Value / Finding | Label |
|---|---|---|
| **Game Folder** | `D:\SteamLibrary\steamapps\common\Total War Attila` | `VERIFIED` (exists, treated strictly as READ-ONLY) |
| **Workspace** | `D:\AttilaArabic` | `VERIFIED` (writable, local git repository on branch `clean-room`) |
| **Direct Game Execution** | Agent cannot launch game (`NO`) — User performs all test installations and runs | `VERIFIED` |
| **Game Executable** | `Attila.exe`, FileVersion `1.6.0.0`, ProductVersion `3.2.1.0` | `VERIFIED` (via PE VersionInfo) |
| **Architecture / Platform** | 32-bit PE (`x86`) running on 64-bit Windows host | `VERIFIED` (PE machine type, `clockwork.Release.x86.dll`, `EOSSDK-Win32-Shipping.dll`) |
| **Core Libraries** | `empire.retail.dll` (32.2 MB), `icudt42.dll` (ICU data v4.2, 10.9 MB), `icudt.dll` (9.9 MB), `ModManager.exe` (2.1 MB) | `VERIFIED` |
| **Active Language Slot** | `data\language.txt` contains `EN` | `VERIFIED` (read directly) |
| **Languages Directory** | `languages\` at game root is empty | `VERIFIED` |
| **Vanilla Mod State** | `data\text\` contains only `credits.xml`, `default_keys.xml`, `default_keys_osx.xml` (no loose `.loc`) | `VERIFIED` |
| **User Mod State** | `used_mods.txt` at game root records active mod list; `preferences.script.txt` present in `%APPDATA%\The Creative Assembly\Attila\scripts` | `VERIFIED` |

---

## 2. Pack File & Loading Architecture

| Concept | Description | Label |
|---|---|---|
| **Pack Header Format** | PFH4 (Pack File Header v4, magic `PFH4`). Header specifies pack type, index count/size, file count, and file index size. | `VERIFIED` (via `packfile.py` and binary inspection) |
| **Pack Types** | `0=boot, 1=release, 2=patch, 3=mod, 4=movie` | `DOCUMENTED` (community tooling standard) |
| **Vanilla Packs** | `data\local_en.pack` is type `1 (release)`. Base assets are in `data.pack`, `models.pack`, etc. | `VERIFIED` |
| **Mod Pack Overrides** | Packs configured as type `3 (mod)` are placed in `data\` and enabled via the official launcher Mod Manager. The launcher writes active mods into `used_mods.txt` (e.g. `mod "pack_name.pack";`). | `VERIFIED` |
| **Load Priority** | Mod packs (type 3) listed in `used_mods.txt` override same-path resources from release packs (type 1). Movie packs (type 4) autoload without manager activation. | `DOCUMENTED` |
| **Target Packaging** | Localized data delivered as standalone type `3 (mod)` `.pack` files. Zero modification of vanilla `.pack` files or `Attila.exe`. | `VERIFIED` |

---

## 3. Localization Table Architecture

| Item | Details | Label |
|---|---|---|
| **Vanilla Loc Storage** | Located inside `data\local_en.pack` under `text\db\*.loc` (174 tables + `credits.xml`). | `VERIFIED` |
| **Binary `.loc` Format** | Header: `0xFF 0xFE` (BOM) + ASCII `'LOC\0'` + `i32 version (1)` + `u32 entry_count`. Entries: `u16 key_len` + UTF-16LE key + `u16 text_len` + UTF-16LE text + `u8 tooltip_flag` (0 or 1). | `VERIFIED` (codec round-trip byte-identical in `source/loc.py`) |
| **Key Merging vs File Override** | Attila replaces localization files on a whole-file basis or merges table keys across same-path `.loc` tables. Supplying full-file tables guarantees correct behavior under both semantics. | `DOCUMENTED` / `INFERENCE` |
| **Formatting Tags** | Vanilla texts contain markup tags: `[[url:…]]…[[/url]]`, `[[col:…]]…[[/col]]`, format tokens `%s`, `%d`, `{n}`. | `VERIFIED` |

---

## 4. Font Architecture & Formats

| Feature | Details | Label |
|---|---|---|
| **Font Format** | Proprietary Creative Assembly CUF bitmap format (`CUF0` and `CUF1`). | `VERIFIED` |
| **CUF Header** | Magic `CUF0` or `CUF1` followed by 11 `u16` properties: `first_prop`, `second_prop`, `line_height`, `fourth_prop`, `fifth_prop`, `baseline`, `layout_y_offset`, `space_justify`, `layout_x_offset`, `h_size`, `v_size`. `h_size`/`v_size` define max render bounds. | `VERIFIED` (matches RPFM specification and byte layouts) |
| **Glyph Dimensions** | Array of records in glyph code order: `i8 alloc_height, u8 alloc_width, u8 width, u8 height`. | `VERIFIED` |
| **Attila Char Mapping** | Flat array of 65,536 `u16` entries mapping Unicode codepoint `0..0xFFFF` directly to glyph index. Differs from Empire-era pair-lists. | `VERIFIED` (RPFM and EB tool fail on Attila tables; custom codec `source/cuf.py` decodes/encodes byte-identically) |
| **Bitmaps** | Concatenated 8-bit uncompressed grayscale bitmaps. Only solid ink (`255`) reliably renders; antialiased edges drop below threshold. | `VERIFIED` |
| **Kerning Matrix** | Tail section with `u16 size`, `u16 skip`, and a `size x size` byte matrix (e.g. 350x350 for `la_gioconda`). Arabic Presentation Forms codes reside outside this matrix. | `VERIFIED` |

---

## 5. Vanilla Font Inventory & Arabic Availability

Audit of all 38 CUF fonts extracted from `local_en.pack` (`logs/cr_map_scan.txt`):

| Font Family | Font Files | Glyph Count | Arabic Presentation Forms-B (FE70..FEFF) Status | UI Surface Role | Label |
|---|---|---|---|---|---|
| `arialunicode` | 7 sizes (10, 12, 14, 16, 18, 20, 22) | 38,948 glyphs | **Present with real ink** (100/100 test codepoints valid) | NOT used by primary UI surfaces | `VERIFIED` |
| `georgia_italic` | 5 sizes (10, 12, 14, 16, 18) | 626 glyphs | **Dangling indices** (`table[cp] >= N`) except U+060C, U+061B, U+0640 | Active UI font | `VERIFIED` |
| `la_gioconda` | 13 sizes (10 to 38) | 285 glyphs | **Dangling indices** (`table[cp] >= N`) except U+060C, U+061B, U+0640 | Active UI font | `VERIFIED` |
| `la_gioconda_uppercase` | 13 sizes (10 to 38) | 285 glyphs | **Dangling indices** (`table[cp] >= N`) except U+060C, U+061B, U+0640 | Active UI font | `VERIFIED` |

### Critical Engine Behavior:
- When a codepoint points to a dangling table index (`>= N`) in `la_gioconda` or `georgia_italic`, the Attila engine draws **BLANK with advance** (zero ink, not a placeholder box).
- In test C0 (vanilla fonts with pre-shaped Arabic loc), **every Arabic surface drew completely blank**, confirming that in-game UI elements (faction selection, buttons, description panels, unit cards) draw from `la_gioconda` / `georgia_italic` / `uppercase`, never from `arialunicode`.
- Therefore, custom Arabic glyphs **must be injected/merged into the active UI CUF fonts**.

---

## 6. Dependent File Hashes (SHA-256)

All dependent game files, tooling, and source assets verified on this machine:

| File Path | Description | SHA-256 | Label |
|---|---|---|---|
| `D:\SteamLibrary\steamapps\common\Total War Attila\Attila.exe` | Vanilla Game Executable (v1.6.0.0) | `51B833D5B8FD8505A7CD035FD92F68CACE681D62EA74D9AD8FBAE26326635BF5` | `VERIFIED` |
| `D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack` | Vanilla English Loc Pack (211,301,042 B) | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` | `VERIFIED` |
| `D:\SteamLibrary\steamapps\common\Total War Attila\data\language.txt` | Game Language Setting (`EN`) | `69374B09B1681162BA2D6BBA92D6A167EA5CA5921EB172EB173E999E3BE5D8BA` | `VERIFIED` |
| `D:\AttilaArabic\extracted\local_en.copy.pack` | Working Copy of Vanilla Loc Pack | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` | `VERIFIED` |
| `D:\AttilaArabic\fonts\upstream\Tajawal-Regular.ttf` | Candidate Arabic Font (Google Fonts OFL) | `6882892DA3E03527D5DB2BBAB3B48BDE6EF2E878A43F522D1A4EEBDA90010A19` | `VERIFIED` |
| `D:\AttilaArabic\fonts\upstream\OFL.txt` | SIL Open Font License 1.1 for Tajawal | `9B584984F9DB0EE30347391A76EFF9C0A6B03DC450C3C6AFE3757A2CB3A4DB87` | `VERIFIED` |
| `D:\AttilaArabic\fonts\upstream\ATTRIBUTION.txt` | Boutros International Attribution Notice | `2B9685BD8467EC846CB2840C54EFC0646E511FEAE1180D789D91E1462FA7CCA5` | `VERIFIED` |
| `D:\AttilaArabic\tools\packfile.py` | PFH4 Pack Builder / Extractor | `78E32367C99A073401C48809C7D9D0640B8878342C35278EAD96D65693152A1F` | `VERIFIED` |
| `D:\AttilaArabic\source\cuf.py` | CUF0/CUF1 Codec & Atlas Generator | `16FF864404A4F31538D6893BB5F6E95C37D1A05F502ADF90498A92F235DD1693` | `VERIFIED` |
| `D:\AttilaArabic\source\loc.py` | Binary `.loc` Codec & TSV Tool | `5850E7E06B46B87521DF1E6488CEEB23ED604D64BB8D0FFC4A28DA164031F516` | `VERIFIED` |
| `D:\AttilaArabic\source\shape.py` | Arabic Shaping & BiDi Reorder Engine | `FBAA369B630BC418202C3F06271872DB4BCDF0C4BA0465CFDA2F2620381CB3A3` | `VERIFIED` |

---

## 7. Third-Party Tools, Mods & Licenses

| Tool / Resource | Origin / Repository | License / Metadata String | Redistribution Permission | Role in Project | Label |
|---|---|---|---|---|---|
| **RPFM (v5.1.1)** | Frodo45127 (`tools\rpfm-v5.1.1\LICENSE`) | `MIT License` (Copyright (c) 2017-2026 Ismael Gutiérrez González) | Permitted with notice | Pack inspection reference; UI pack validation | `VERIFIED` |
| **packfile.py** | Community (`ntw_pack_esf_tools`) | `MIT License` | Permitted | Autonomous pack build/extraction pipeline | `VERIFIED` |
| **etwng** | Tomasz Wegrzanowski (`tools\etwng\LICENSE`) | `MIT License` (Copyright (c) 2010-2025 Tomasz Wegrzanowski) | Permitted | Empire CUF research reference | `VERIFIED` |
| **Europa Barbarorum CUF Tool** | The Europa Barbarorum Team (`reference\cuf-tool\bin\COPYRIGHT`) | `BSD-3-Clause` (Copyright (c) 2010, 2011, 2012, The Europa Barbarorum Team) | Permitted with notice | Historical reference only; incompatible with Attila 65k char tables | `VERIFIED` |
| **arabic-reshaper (3.0.1)** | Abdullah Diab `<mpcabd@gmail.com>` | Metadata `License: MIT` | Permitted | Contextual glyph shaping (Forms-B conversion) | `VERIFIED` |
| **python-bidi (0.6.11)** | Meir Kriheli `<mkriheli@gmail.com>` | Metadata Classifier: `License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)` | Permitted dynamically linked | Unicode Bidirectional algorithm (visual order) | `VERIFIED` |
| **fonttools (4.66.1)** | Just van Rossum `<just@letterror.com>`, Maintainer: Behdad Esfahbod | Metadata `License: MIT` | Permitted | TrueType table parsing & glyph extraction | `VERIFIED` |
| **Pillow (12.3.0)** | Jeffrey 'Alex' Clark `<aclark@aclark.net>` | Metadata `License-Expression: MIT-CMU` | Permitted | Glyph rasterization & font atlas processing | `VERIFIED` |
| **Shyizer Arabic Rome II V1.0** | Shyizer (`reference\shyizer\`) | No license file present in archive / `UNVERIFIED` | **NO REDISTRIBUTION** | Structural inspection only | `VERIFIED` |
| **Three Kingdoms Arabic** | Hussain (`reference\threekingdoms\`) | `Proprietary / All Rights Reserved` (Installer redistribution only per README) | **NO REDISTRIBUTION** | Prior art documentation only | `VERIFIED` |

### Prior Art Contamination Audit
- **Inspection Summary:**
  - `reference/shyizer`: Rome II community mod containing 37 CUF files. Inspected solely to observe that Rome II fonts had `aw == w` on Presentation Forms-B glyphs and standard 350x33 kerning tails.
  - `reference/threekingdoms`: Documentation-only clone containing release notes for an external `.exe` installer. No code, assets, or font data exist in the repository.
- **Contamination Rules & Compliance:**
  - Neither mod is tracked in git (`reference/` is gitignored).
  - **Zero bytes**, glyph bitmaps, metric values, or text strings from Shyizer or Three Kingdoms may be committed, packaged into test packs, or used as test inputs in Phase 1.
  - Phase 1 relies strictly and exclusively on clean-room inputs: upstream `Tajawal-Regular.ttf` (SIL OFL 1.1) and our own standalone codecs (`source/cuf.py`, `source/loc.py`, `source/shape.py`).


---

## 8. Candidate Font Audit (Tajawal-Regular.ttf)

- **Source:** Google Fonts upstream (`github.com/googlefonts/tajawal`).
- **Copyright:** `Copyright 2018 Boutros International (http://www.boutrosfonts.com)`.
- **License:** SIL Open Font License 1.1 (`OFL.txt`). `VERIFIED`.
- **Reserved Font Name:** **NONE** declared. Modification, rasterization into bitmap atlases, and redistribution under OFL terms are fully permitted. `VERIFIED`.
- **Glyph Audit & Coverage Analysis:**
  - Total CMAP entries: 446 glyphs.
  - Basic Arabic (`U+0621..U+064A`): 100% complete (37/37 letters covered). `VERIFIED`.
  - Hamza forms: ء (`U+0621`), آ (`U+0622`), أ (`U+0623`), ؤ (`U+0624`), إ (`U+0625`), ئ (`U+0626`) all present in CMAP. `VERIFIED`.
  - Lam-Alef ligatures: All 8 Presentation Forms-B variants (`U+FEF5..U+FEFC`) present directly in CMAP. `VERIFIED`.
  - Punctuation: Arabic comma (`U+060C`), semicolon (`U+061B`), question mark (`U+061F`), percent (`U+066A`), tatweel (`U+0640`) all present in CMAP. `VERIFIED`.
  - Digits: Arabic-Indic (`U+0660..U+0669`) and ASCII (`0..9`) all present. `VERIFIED`.
  - Presentation Forms-B (`U+FE70..U+FEFF`): 89 directly present. The 36 missing forms are exclusively `<isolated>` forms which decompose 1:1 to base letters `U+0621..U+064A` present in Tajawal. `VERIFIED`.

---

## 9. Proposed Phase 1 Test Plan: Minimal Rendering Proof

### Core Technical Questions to Answer:
1. **Engine Native Shaping & Direction:** Does the Warscape engine perform native Arabic shaping or BiDi reordering?
   - *Current Evidence:* Screenshots from C0 and C1 demonstrate that the engine performs **no native shaping** and renders characters strictly in memory order.
2. **Reading Direction & Layout Orientation:** Does the engine render stored strings strictly Left-to-Right without mirroring?
   - Test C5 isolates direction using asymmetric ruler probe rows.
3. **Glyph Metrics & Advance Control:** Does cell pitch follow declared advance width `aw`, bitmap width `w`, or an internal fixed pitch?
   - Test C5 tests sweep rows comparing `aw` vs `w`.
4. **Line Wrapping & Right-Alignment:** How do multi-line text boxes behave with hard returns and long strings?

### Minimal Test Pack Specifications:
- **Loc Pack:** `Attila_Arabic_Phase1.pack` (type 3 mod pack).
  - Target keys across diverse UI controls:
    - Button: Main menu and campaign battle settings buttons.
    - Dropdown: Faction select dropdown / unit selection.
    - Tooltip: Difficulty medal or unit stat tooltip.
    - Multi-line description: Eastern Roman Empire description panel (`start_pos_factions_description_att_fact_eastern_roman_empire`).
  - Text contents to test:
    1. Joined Arabic word (`القاهرة`, `معركة`).
    2. Lam-Alef ligature (`الإمبراطورية`, `لا`).
    3. Hamza variations (ء, أ, إ, ؤ, ئ, آ).
    4. Mixed Arabic and Latin numbers / letters (`روما 1200`, `AD 395`).
    5. Formatting tags (`[[col:yellow]]...[[/col]]`) and placeholders.
    6. Right-to-left line wrapping and alignment.
- **Font Pack:** `Attila_Arabic_Phase1_fonts.pack` (type 3 mod pack).
  - Merged Tajawal Arabic glyphs into active UI CUFs (`la_gioconda` and `georgia_italic` active sizes).
  - Original Latin glyphs, header properties, and kerning tails preserved 100% byte-identical.
