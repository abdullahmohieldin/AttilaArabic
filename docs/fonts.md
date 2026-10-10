# Typography & Font Pipeline Specification

> **Document Classification:** Asset Reference & Font Engineering Specification  
> **Status:** PRODUCTION ACTIVE (Phase 1)  
> **Primary Upstream Typeface:** Tajawal Regular ([Google Fonts](https://fonts.google.com/specimen/Tajawal))

---

## 1. Upstream Typeface Provenance & Licensing

The project utilizes the open-source **Tajawal** typeface, chosen for its clear geometric Kufi-Naskh balance, high legibility on dark and parchment backgrounds, and optimal stroke-width scaling at small user-interface sizes.

| Property | Details |
| :--- | :--- |
| **Font Family** | Tajawal (Arabic & Latin) |
| **Style / Weight** | Regular (400) |
| **File Location** | `fonts\upstream\Tajawal-Regular.ttf` (60,360 bytes) |
| **File SHA-256** | `6882892DA3E03527D5DB2BBAB3B48BDE6EF2E878A43F522D1A4EEBDA90010A19` |
| **Designers** | Boutros Fonts (Mourad Boutros, Soulaf Khalifeh) |
| **Upstream Repository** | [googlefonts/tajawal](https://github.com/googlefonts/tajawal) |
| **License** | [SIL Open Font License (OFL) Version 1.1](http://scripts.sil.org/OFL) (`fonts\upstream\OFL.txt`) |
| **Reserved Font Names** | None declared. Distribution, modification, and bitmap embedding permitted. |

---

## 2. Glyph Coverage & Codepoint Mapping Strategy

Attila's Warscape engine does not support real-time OpenType cursive shaping; all text strings must be pre-shaped into **Unicode Arabic Presentation Forms-B** (`U+FE70`–`U+FEFF`) prior to display.

### 2.1 The Isolated Glyphs Fallback Architecture
The upstream `Tajawal-Regular.ttf` font contains 446 glyphs. In its internal Unicode character map (`cmap`), several isolated Presentation Forms-B characters are intentionally omitted in favor of canonical base Arabic codepoints (`U+0600`–`U+06FF`). 

To prevent missing-glyph boxes (`[]` tofu) when the engine encounters these characters:

| Target Codepoint | Description | Fallback Base Codepoint | Resulting Vector Shape |
| :--- | :--- | :---: | :---: |
| `0xFE8D` | Arabic Letter Alef (Isolated) | `0x0627` | True Alef Isolated Glyph |
| `0xFEAD` | Arabic Letter Reh (Isolated) | `0x0631` | True Reh Isolated Glyph |
| `0xFEED` | Arabic Letter Waw (Isolated) | `0x0648` | True Waw Isolated Glyph |
| `0xFE80` | Arabic Letter Hamza (Isolated) | `0x0621` | True Hamza Glyph |
| `0xFE83` | Arabic Letter Alef with Hamza Above | `0x0623` | True Alef-Hamza Glyph |

Unmapped non-characters are intentionally skipped during font generation, ensuring the `.notdef` box is never bound to any valid Arabic letter code.

---

## 3. Game Font Library (`.cuf`) Integration

The clean-room font builder (`source/cr_phase1_build.py`) merges calibrated Arabic glyphs into all **37 vanilla game CUF fonts** across the three major typeface families used by Total War: ATTILA:

| Font Family | File Prefix | Available Point Sizes | UI Role in Game |
| :--- | :--- | :---: | :--- |
| **Georgia Italic** | `georgia_italic_*.cuf` | 10, 12, 14, 16, 18, 20, 22, 24 | Narrative lore, tooltips, quotes |
| **La Gioconda** | `la_gioconda_*.cuf` | 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38 | Standard headers, faction names, menus |
| **La Gioconda Uppercase** | `la_gioconda_uppercase_*.cuf` | 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38 | Major titles, button labels, tabs |
| **Arial Unicode** | `arialunicode_12.cuf` | 12 | System fallback tables |

### 3.1 Strict Byte-Preservation Invariants
During font injection, the builder strictly preserves:
1. All vanilla Latin glyph records (`U+0020` to `U+007E`) byte-identically.
2. All original header properties (line height, vertical boundaries, layout offsets).
3. All original kerning tails (including 350×350 Latin kerning matrices).
4. Magic header signatures (`CUF0` / `CUF1`).
