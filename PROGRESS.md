# Total War: ATTILA Arabic Localization — Progress Tracker

## Project Status: Phase 1 Production Release (In-Game Verified)

---

## 1. Ground Truth Ledger & Core Invariants

### Environment & Safety Integrity
- **Game Directory:** `D:\SteamLibrary\steamapps\common\Total War Attila` (Strictly READ-ONLY).
- **Vanilla `local_en.pack` SHA-256:** `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` (100% byte-identical, verified).
- **Vanilla `Attila.exe` SHA-256:** `51B833D5B8FD8505A7CD035FD92F68CACE681D62EA74D9AD8FBAE26326635BF5` (100% byte-identical, verified).
- **Active Installed Packs:**
  - `Attila_Arabic_Phase1.pack` (Loc table overrides)
  - `Attila_Arabic_Phase1_fonts.pack` (31 merged CUF fonts)

---

## 2. Milestone Status & Verified Findings

| Milestone | Status | Description |
| :--- | :---: | :--- |
| **Clean-Room Codec** | ✅ **VERIFIED** | Bit-accurate decode/encode of CUF0 and CUF1 binary font structures. Latin glyphs and kerning remain 100% byte-identical. |
| **Arabic Shaping (BiDi)** | ✅ **VERIFIED** | Logical-to-visual conversion into Arabic Presentation Forms-B correctly renders cursive letters in right-to-left order. |
| **Zero-Box Guarantee** | ✅ **VERIFIED** | Missing `.notdef` tofu boxes completely eliminated by mapping isolated Presentation Forms-B and canonical base codepoints directly to true Tajawal glyphs. |
| **Baseline Alignment** | ✅ **VERIFIED** | Automatic calibration using Latin capital 'H' bounds anchors Arabic baselines to match Latin typography without vertical clipping or floating text. |
| **Intra-Cell Stroke Joining** | ✅ **VERIFIED** | Connecting baseline strokes extended edge-to-edge ($0$ to $w-1$) across all glyph cells, and allocated advance shortened (`alloc_w = max(1, w - 1)`) for connecting forms, completely neutralizing the Warscape engine's $+1\text{ px}$ advance and eliminating seams across all connected words. |
| **RTL Paragraph Balancing** | ✅ **VERIFIED** | Pre-segmented 13-line narrative with binary PUA blank padding (`U+E010`–`U+E015`) aligns campaign description text flush-right without mid-line flipping. |
| **Data-Driven Loc Architecture** | ✅ **VERIFIED** | Universal compiler (`source/loc_compiler.py`) auto-compiles modular translation JSON files (`data/translations/`) across 11 tables with 194 strings covering Main Menu, Custom Battles, Unit Stats, Settings, Campaigns, Factions, Cultural Groups, Traits, and UI. |
| **Automated Test Suite** | ✅ **VERIFIED** | `tests/` asserts font integrity, loc format, clean-room safety, baseline fit, and key mappings (10/10 passing). |

---

## 3. Verified Engine Invariants & Solutions

### The 1-Pixel Advance Compensation
- **Engine Mechanics:** The Warscape text renderer draws characters on individual 2D rectangular quads and advances each quad by $\text{advance} = \text{alloc\_w} + 1\text{ px}$.
- **Resolution:** By setting $\text{alloc\_w} = \max(1, w - 1)$ for all connecting forms (`FINAL`, `MEDIAL`, Tatweel), the engine advance becomes $(w - 1) + 1 = w\text{ px}$. This achieves 100% seamless glyph-to-glyph connection across all fonts and screens with 0-pixel gap.

---

## 4. Current Build Hashes

- **`Attila_Arabic_Phase1.pack`**: `352D42D804837F0B42740D8E91784395D1C072426C13CC35D7941D61106611AD`
- **`Attila_Arabic_Phase1_fonts.pack`**: `6018B5F37772D2321E551C5CA25AE264727998B1F02CA3413424071714D8C4FF`
