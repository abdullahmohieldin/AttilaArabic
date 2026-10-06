# Test Pack Manifest — v5 Fixed Baseline Arabic Fonts (BUILD ONLY)

## Packs Built

### 1. Fonts Pack (Rebuilt with Unified Baseline Alignment)
- **Path**: `D:\AttilaArabic\release\Attila_Arabic_POC_v5_fonts.pack`
- **Size**: 26,545,551 bytes
- **SHA256**: `A6D9127033B2199307A9E3F7D73F205D5EBDB78C9C09BB4C0BF44DC638F726B8`
- **Format**: PFH4, type `mod (3)`, 31 files, 0 dependencies.
- **Coverage**: 31 merged CUF fonts (`la_gioconda_{10..38}`, `la_gioconda_uppercase_{10..38}`, `georgia_italic_{10..18}`).
- **Glyphs**: Full Arabic set (684 codepoints: U+0621–064A, tatweel U+0640, harakat U+064B–0652, superscript alef U+0670, Arabic punctuation, Arabic-Indic digits U+0660–0669, Presentation Forms-A U+FB50–FDFF, Presentation Forms-B U+FE70–FEFF).
- **Baseline Fix**: True font baseline row alignment (`top = baseline_row + by0 - ascent + 1`). Connecting strokes sit flat on the common baseline row, eliminating wavy/jittery letter connections.
- **Check Status**: `v3_check.py` reports **ALL FONTS PASS** (0 missing, Latin byte-identical, kerning tails identical, original magic `CUF0` kept).

### 2. Localization Pack (Unchanged from v4)
- **Path**: `D:\AttilaArabic\release\Attila_Arabic_POC_v4.pack`
- **Size**: 1,807,749 bytes
- **SHA256**: `A820ACAFA927BC10B06D0DDA9FF4ECA4DB87B063DE38CAE903EFC53DBF4B26D6`
- **Format**: PFH4, type `mod (3)`, 7 full-file loc copies.
- **Strings**: 80 real Arabic strings across Battles menu, Campaigns menu, Custom Battle, Faction Select, and Faction Descriptions. **NO ID prefixes**.

---

## Baseline Integrity Verification (Binding Rule)

| Pack | Status | SHA256 |
|------|--------|--------|
| `D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack` | BEFORE build | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` |
| `D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack` | AFTER build | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` |

---

## Test Setup in Total War: ATTILA

### Step 1: Copy Packs to Game Folder
Copy `Attila_Arabic_POC_v5_fonts.pack` into the game's `data\` folder:
1. Copy `D:\AttilaArabic\release\Attila_Arabic_POC_v5_fonts.pack` -> `D:\SteamLibrary\steamapps\common\Total War Attila\data\`
2. Keep `Attila_Arabic_POC_v4.pack` in `data\` (or copy if not present).

> [!CAUTION]
> Ensure only **ONE font pack** is active in the game folder at any time (remove older font packs `Attila_Arabic_POC_v4_fonts.pack` or `Attila_Arabic_POC_v3b_big.pack` from `data\`).

### Step 2: Mod Manager Activation
1. Launch Total War: ATTILA launcher / Mod Manager.
2. Enable Out-of-date Mods if prompted.
3. Tick the checkbox for:
   - `Attila_Arabic_POC_v5_fonts`
   - `Attila_Arabic_POC_v4`

---

## Screens to Inspect & Verification Points

1. **Main Menu -> Campaigns Menu ("الحملة الكبرى", "المقدمة التعليمية")**:
   - Check that connected letters sit on a single flat baseline without vertical stepping or jitter.
2. **Main Menu -> Battles Menu ("معركة تاريخية", "معركة مخصصة")**:
   - Verify smooth horizontal cursive flow on buttons.
3. **Faction Select & Faction Description (e.g. Sasanian Empire "الإمبراطورية الساسانية")**:
   - Check multi-word paragraphs and titles for clean baseline alignment across varying glyph heights (tall alef/lam vs flat dal/beh vs descender reh/noon).
