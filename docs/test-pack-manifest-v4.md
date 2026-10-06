# Test Pack Manifest — v4 Connected Vertical Slice (BUILD ONLY)

## Packs Built

### 1. Fonts Pack
- **Path**: `D:\AttilaArabic\release\Attila_Arabic_POC_v4_fonts.pack`
- **Size**: 27,710,396 bytes
- **SHA256**: `0BFE39A7861C72DE69EE231E223EBD8ECEE521964EA02B4E04FECE88649D8CB4`
- **Format**: PFH4, type `mod (3)`, 31 files, 0 dependencies.
- **Coverage**: 31 merged CUF fonts (`la_gioconda_{10..38}`, `la_gioconda_uppercase_{10..38}`, `georgia_italic_{10..18}`).
- **Glyphs**: Full Arabic set (684 codepoints: U+0621–064A, tatweel U+0640, harakat U+064B–0652, superscript alef U+0670, Arabic punctuation, Arabic-Indic digits U+0660–0669, Presentation Forms-A U+FB50–FDFF, Presentation Forms-B U+FE70–FEFF).
- **Check Status**: `v3_check.py` reports **ALL FONTS PASS** (0 missing, Latin byte-identical, kerning tails identical, original magic `CUF0` kept).

### 2. Localization Pack
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
Copy the two packs from `release\` into the game's `data\` folder:
1. `Attila_Arabic_POC_v4_fonts.pack` -> `D:\SteamLibrary\steamapps\common\Total War Attila\data\`
2. `Attila_Arabic_POC_v4.pack` -> `D:\SteamLibrary\steamapps\common\Total War Attila\data\`

> [!CAUTION]
> Ensure only **ONE font pack** is active in the game folder at any time (remove older font packs like `Attila_Arabic_POC_v3b_big.pack` from `data\`).

### Step 2: Mod Manager Activation
1. Launch Total War: ATTILA launcher / Mod Manager.
2. Enable Out-of-date Mods if prompted.
3. Tick the checkbox for:
   - `Attila_Arabic_POC_v4_fonts`
   - `Attila_Arabic_POC_v4`

---

## Screens to Visit & Exact Verification Points

### 1. Main Menu -> Campaigns Menu
- **Buttons to inspect**:
  - "الحملة الكبرى" (Grand Campaign)
  - "المقدمة التعليمية" (Prologue)
  - "حملة جديدة" (New Campaign)
  - "متابعة الحملة" (Continue Campaign)
- **Check**: Clean Arabic rendering, proper baseline alignment, no clipping.

### 2. Main Menu -> Battles Menu
- **Buttons to inspect**:
  - "المعارك التاريخية" (Historical Battles)
  - "معركة مخصصة" (Custom Battle)
  - "معركة سريعة" (Quick Battle)
  - "رجوع" (Back) / "القائمة الرئيسية" (Main Menu)

### 3. Custom Battle Screen
- **Header**: "معركة مخصصة"
- **Buttons**: "بدء المعركة" (Start Battle), "اختيار الجيوش" (Unit Selection), "إعدادات المعركة" (Battle Settings), "إعادة التعيين" (Reset)
- **Sides**: "الجيش المهاجم" (Attacking Army), "الجيش المدافع" (Defending Army)
- **Unit Card Stats**: Select a unit and inspect Unit Info stats:
  - "هجوم الاشتباك" (Melee Attack), "دفاع الاشتباك" (Melee Defence), "الدرع" (Armour), "الصحة" (Health), "المعنويات" (Morale), "السرعة" (Speed).

### 4. Grand Campaign Faction Select Screen
- **Header**: "اختر الفصيل" (Select Faction), "السمات الثقافية" (Cultural Traits), "تفاصيل الفصيل" (Faction Details)
- **Group Tabs**:
  - "الإمبراطوريات الرومانية", "الممالك الشرقية", "القبائل البدوية", "الممالك البربرية", "القبائل المهاجرة", "ممالك الصحراء"
- **Labels**: "السنة" (Year), "395 م", "التحدي المبدئي:" (Initial Challenge:), "صعوبة الحملة" (Campaign Difficulty), "قائد الفصيل" (Faction Leader)
- **Difficulty Descriptions**: Hover or toggle difficulty levels (Easy through Legendary) to inspect the 5 full descriptive sentences.
- **Closed Faction Dropdown**:
  - Inspect the closed dropdown box: ERE is formatted with 135 px truncation ending with "…" (`الإمبراطورية…`). Verify that the start of the word is intact and does not clip.
- **Faction Description Parchment (Newlines Test)**:
  - **Western Roman Empire (WRE)**: Reads text pre-wrapped with LF (`\n`). Verify if line breaks render correctly.
  - **Eastern Roman Empire (ERE)**: Reads text pre-wrapped with CRLF (`\r\n`). Compare line breaks with WRE to determine if the engine honors LF vs CRLF.
