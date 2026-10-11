# Total War: Attila - Arabic Localization (Part 1)
## Installation & Activation Guide

This document provides instructions for installing and activating the standalone Arabic Localization mod pack (`Attila_Arabic_Part1.pack`).

---

### Prerequisites
- Total War: Attila installed via Steam.
- Mod pack file generated at:
  `d:\AttilaArabic\tw_attila_ar\out\Attila_Arabic_Part1.pack`

---

### Step 1: Manual Installation
Because the game directory is strictly protected and read-only during development, you must copy the `.pack` file manually into the game's `data` directory.

1. Navigate to your Total War: Attila `data` folder:
   - Typical path: `D:\SteamLibrary\steamapps\common\Total War Attila\data`
   - Alternative default: `C:\Program Files (x86)\Steam\steamapps\common\Total War Attila\data`
2. Copy `Attila_Arabic_Part1.pack` from:
   `d:\AttilaArabic\tw_attila_ar\out\Attila_Arabic_Part1.pack`
   into the game's `data\` folder.

---

### Step 2: Activation

You can activate the mod using either the **Total War Mod Manager** (Launcher) or the **`user.script.txt`** configuration file.

#### Option A: Official Launcher / Mod Manager (Recommended)
1. Start Total War: Attila through Steam.
2. In the Total War Launcher, click on **Mod Manager**.
3. Enable **Enable out-of-date mods** if prompted.
4. Locate **Attila_Arabic_Part1** in the list and toggle the switch/checkbox to **ON**.
5. Launch the game.

#### Option B: Direct `user.script.txt` (Instant / No Launcher Needed)
1. Open Windows Run (`Win + R`) and paste:
   ```cmd
   %APPDATA%\The Creative Assembly\Attila\scripts
   ```
2. Open or create the file named `user.script.txt` (encoded in UTF-16 LE or UTF-8).
3. Add the following line at the top of the file:
   ```text
   mod "Attila_Arabic_Part1.pack";
   ```
4. Save and close the file. Launch the game normally.

---

### Step 3: Verifying Active Mod in Game
1. When the game loads, verify the **Main Menu**:
   - Menu buttons (Grand Campaign / الحملة الكبرى, Options / الخيارات, etc.) should appear in localized Arabic script.
2. Click on **Grand Campaign (الحملة الكبرى)**:
   - Faction selection cards, faction names, leader names, and traits should display in clean Arabic calligraphy with correct Right-to-Left formatting.

---

### Uninstallation / Disabling
To disable the mod:
- **Launcher:** Uncheck `Attila_Arabic_Part1` in the Mod Manager.
- **user.script.txt:** Remove the line `mod "Attila_Arabic_Part1.pack";`.
- **Permanent Removal:** Delete `Attila_Arabic_Part1.pack` from `Total War Attila\data\`.
Your original vanilla files are completely untouched and unaffected.
