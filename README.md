# Total War: ATTILA — Arabic Localization & RTL Toolchain (POC)

Proof of concept for adding full Arabic text rendering and RTL support to Total War: ATTILA without engine modifications.

> [!IMPORTANT]
> **NO GAME FILES IN THIS REPOSITORY**:
> This repository contains only custom Python toolchain scripts, documentation, and open-source upstream font assets (Tajawal under SIL OFL). No copyrighted game data, vanilla `.pack` archives, vanilla `.loc` files, or extracted CA `.cuf` fonts are stored or distributed in this repository.

---

## Project Goal & Current Status

Total War: ATTILA's UI engine performs **no contextual shaping** and **no bidirectional (BiDi) reordering**; it renders strings strictly left-to-right (LTR) using bitmap/vector CUF fonts.

### Verified Findings & Architecture
- **Shaping & BiDi**: Pre-shaping strings into Arabic Presentation Forms-B and applying visual reordering allows proper joining, reading order, and mixed Latin/numeral rendering.
- **CUF Fonts**: The game UI relies primarily on `la_gioconda`, `la_gioconda_uppercase`, and `georgia_italic` (all CUF0 format, lacking Arabic glyphs in vanilla).
- **Font Merging (`v3b_big`)**: We merge Arabic glyphs from Tajawal-Regular into the vanilla CUFs. The `v3b_big` configuration (cap-matched px sizing, cell bounds up to +2px) prevents Arabic vertical clipping while keeping all original Latin glyphs and kerning 100% byte-identical. Missing glyphs render as blank.
- **Text Wrapping**: Engine text-wrapping reverses line order on LTR-rendered RTL strings. To fix this, logical text must be wrapped using exact CUF font widths and then BiDi-reordered per line in top-to-bottom order.
- **Faction Selection UI**: The faction panel reads `start_pos_factions_description_<id>`. Closed dropdown is ~135 px wide and clips the visual start; logical ends must be truncated with ellipsis ("…").

---

## Safety Rules (Binding)

1. **Game Installation is Read-Only**: The game directory (e.g. `D:\SteamLibrary\steamapps\common\Total War Attila`) must never be modified by automated scripts.
2. **Vanilla Integrity Check**: `local_en.pack` SHA256 must strictly remain `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D`. Verified before and after every build.
3. **Manual Pack Testing**: Generated test packs in `release/` are manually copied to the game's `data\` directory by the user.
4. **Single Font Pack**: Only test one font pack at a time in the game to avoid collision.

---

## How to Rebuild (Requires Own Copy of Total War: ATTILA)

### Prerequisites
- Python 3.13+
- Install dependencies:
  ```powershell
  tools\venv\Scripts\pip install -r requirements.txt
  ```

### Rebuilding Packs
1. Extract required vanilla fonts and target `.loc` tables from your own licensed `data\local_en.pack` using `tools\packfile.py` into `extracted\`.
2. Generate merged fonts and localized test packs using scripts in `source/`:
   ```powershell
   tools\venv\Scripts\python source\build_v3.py   # v3 / v3b / v3b_big builds
   ```
3. Test packs will be output to `release/` and manifests logged to `docs/` and `logs/`.

---

## License

No license has been set yet. A license file will be added upon maintainer specification.
