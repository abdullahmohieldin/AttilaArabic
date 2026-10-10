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
| **Intra-Cell Stroke Joining** | ✅ **VERIFIED** | Connecting baseline strokes extended edge-to-edge ($0$ to $w-1$) across all glyph cells, closing gaps down to the engine's hardcoded minimum. |
| **RTL Paragraph Balancing** | ✅ **VERIFIED** | Pre-segmented 13-line narrative with binary PUA blank padding (`U+E001`–`U+E006`) aligns campaign description text flush-right without mid-line flipping. |
| **Automated Test Suite** | ✅ **VERIFIED** | `tests/test_phase1_packs.py` asserts font integrity, loc format, and vanilla file hashes on every build (3/3 passing). |

---

## 3. Verified Engine Constraints & Precedents

### The 1-Pixel Hairline Tile Seam
- **Observed Behavior:** Between connected cursive letters, an exact 1-pixel gap exists along the connecting baseline.
- **Engine Mechanics:** The Warscape text renderer draws characters on individual 2D rectangular quads and advances each quad by $\text{advance} = w + 1\text{ px}$. The $+1\text{ px}$ margin is an engine-level rule designed to keep Latin characters from smudging.
- **Community Precedents:**
  - *Total War: ROME II* ("Shyizer Arabic - تعريب شيزر"): Mod uses identical Tajawal Presentation Forms-B and exhibits the exact same 1-pixel hairline seam.
  - *Total War: THREE KINGDOMS* ("Three Kingdoms Arabic" by Hussain / AlmightyJack): Mod uses identical CUF bitmap fonts and shares the same engine quad advance constraint.
- **Conclusion:** The 1-pixel seam is the physical limit of the Warscape text renderer without binary code injection into the game executable.

---

## 4. Current Build Hashes

- **`Attila_Arabic_Phase1.pack`**: `D0AA87151CF05C3610B1E59E1B239B02BF7521563ECB96479ABA350495A49AA2`
- **`Attila_Arabic_Phase1_fonts.pack`**: `C96F922C55C643D3591EC1D3AFEBC66B51F0374D2280829CE238D3B3641ADF58`
