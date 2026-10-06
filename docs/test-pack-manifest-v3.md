# Test Pack Manifest — v3 font test (BUILD ONLY, do NOT test yet)

Pack: `D:\AttilaArabic\release\Attila_Arabic_POC_v3_fonttest.pack`
SHA256: `861326EFBB43716179020C38F890409F19D4DF0C58174920ED1C9BE02432E721`
Format: PFH4, type `mod (3)`, 31 files, 0 dependencies.
Built by: `source\build_v3.py`. Status: built + self-checked, never loaded
in-game. Awaiting explicit test go-ahead (separate step).

## Contents

All 31 files at vanilla internal paths `font\<name>.cuf`:

- `la_gioconda_{10,12,14,16,18,20,22,24,26,28,30,32,38}` (13)
- `la_gioconda_uppercase_{…same 13…}`
- `georgia_italic_{10,12,14,16,18}` (5)

Per file (VERIFIED by `source\v3_check.py`, `logs\v3_build.txt`):

- original magic kept (`CUF0` on all 31 — VERIFIED; no CUF1 in this set)
- vanilla Latin glyphs byte-identical (spot range U+0020–U+007E) — VERIFIED
- kerning tail byte-identical (incl. 350×350 blocks where present) — VERIFIED
- +69 corpus Arabic glyphs appended (codes after vanilla range) + 1 blank
  placeholder preserving the dangling PUA reference — VERIFIED
- `source\v3_check.py`: **ALL FONTS PASS, 0 missing** of 69 corpus codepoints

## Method (INFERENCE where engine behavior is concerned)

- Source: `fonts\upstream\Tajawal-Regular.ttf` (OFL 1.1, no Reserved Font
  Name — VERIFIED, see `docs\fonts.md`), rasterized natively per size with
  Pillow BASIC layout (no shaper; presentation forms = single glyphs).
- 13 corpus codepoints absent from Tajawal's cmap (isolated Forms-B) were
  rendered from their Unicode base letters (compatibility decomposition),
  which Pillow draws in isolated shape — VERIFIED visually on contact sheet.
- Calibration per file: pixel size chosen so Tajawal cap-height matches the
  vanilla `H` cap, then reduced until all 69 glyphs fit the vanilla cell
  height with baselines aligned (vanilla `H` bottom = baseline). Advances
  from Tajawal metrics; cells keep full ink incl. bearings; `alloc_h` = cell
  height like vanilla Latin. No bitmap was scaled from another size.
- Known limits (UNVERIFIED in-game): Arabic renders smaller than the
  cap-matched size (fit reduction); `U+2014` was already present in vanilla
  fonts (VERIFIED `0xF8` in gioconda_10) so it was not added; mark
  codepoints (e.g. tanween) included as spacing glyphs — shaping quality
  TBD by screenshots.

## Visual QA

`docs\arabic-glyphs-merged_gioconda_10.png`: added forms green/correct
orientation + polarity; non-corpus forms still fallback (red) as designed.
