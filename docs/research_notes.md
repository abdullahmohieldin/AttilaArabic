# Research notes (persistent across chats)

## CUF format facts

- CUF glyph record: alloc_height (i8), alloc_width (u8, the advance),
  width (u8), height (u8). HSize/VSize in the header are max render
  bounds; bigger glyphs are clipped.
- Empire-style CUFs end with a kerning section: u16 size, u16 skip, then a
  size x size byte matrix; entry = width of glyph A when followed by
  glyph B. A value below A's normal advance would act as negative spacing.
  NOT proven that Attila reads it.
- Attila char map = 65536 x u16 char->code table (Empire uses per-glyph
  code/character pairs); RPFM and the EB CUF tool only understand the
  Empire layout. Details in docs/cuf_format.md.

## Measured in game (Attila)

- Pitch per codepoint (8/8/8/8/5/6 for FE92/FE98/FE9C/FEF4/FE8D/FE8E,
  FEF2=12, space=5) did not change when the bitmap width changed
  (v10 w=6 -> v13 w=8, same pitches), and did not change when aw was set
  to 2 and 12 in v15 (the ruler lines ended at the same x). Only solid
  255 pixels render; faint edges get dropped.
- Drawn ink per cell = min(w, pitch) - ~1 column; geo12 layout_x_offset=1
  is consistent with a +1 draw offset, leaving ~1 empty column between
  cells (v13: w8@P8 drew 7 cols, gap 1; v10: w6@P8 drew ~5, gap 2-4).
- v15 OPEN ANOMALY (2026-10-08): the half-block probes (FEF4 = solid cols
  0-3, FE8D = solid cols 4-9 in georgia_italic_12) did NOT appear as
  blocks in the faction description box; the box showed normal shaped
  ticks instead. Suspect the description box draws from a CUF we did not
  edit (another size, or vanilla arialunicode which has real Arabic and is
  NOT in our fonts pack). v12's solid blocks were seen in unit-info /
  dropdown surfaces, not verified in this box. Next probe must identify
  the description box's actual font before any join fix is built.
- System-font advances (Segoe/Tahoma/Arial @12px) and vanilla
  arialunicode aw values do NOT match the pitch table -> pitch source
  still unknown; it is per-codepoint, font-independent, aw-independent,
  w-independent.

## Build lineage

- v14 is the last real build; v15 is a probe, not a release.
- v14 fonts = solid-255 join bars + 1px overlap on all connecting forms
  (166/166 seamless in the offline renderer) but gaps remained in game.
- The offline renderer's placement model is wrong somewhere; calibrate
  against real screenshots before trusting it (it passed 166/166 while
  the screen disagreed).

## Other mods / tools

- Connected-Tajawal Arabic mods exist for Rome II (Shyizer), Warhammer III
  and Three Kingdoms; their method is undocumented.
- Shyizer Arabic Rome II V1.0 (reference/shyizer/): one pack
  ("Shyizer Arabic.pack", PFH4 type 3) with 37 CUFs (arialunicode_12,
  georgia_italic_10-24, la_gioconda_10-38, la_gioconda_uppercase_8-38) +
  text\db loc files. Its Arabic glyph records have aw == w (tight, e.g.
  FE92 aw5/w5, FEF2 aw9/w9, h=18 in-box) and its kerning tails are the
  unchanged vanilla 350/33 matrix. Rome II engine generation = Empire-era;
  aw==w there may be why it connects without tricks. Not copied into our
  packs (study only).
- ThreeKingdomsArabic-Release (reference/threekingdoms/): repo ships ONLY
  docs (README/CHANGELOG/LICENSE/THIRD_PARTY_NOTICES/SHA256SUMS); the mod
  itself is a Windows installer exe in GitHub Releases (v1.5.2). No fonts
  or scripts in the repo to study.
- Europa Barbarorum CUF tool (reference/cuf-tool/): Java binary CUF.jar +
  javadoc + PDF manual; converts TrueType/Type1 to Empire CUF. No source.
- RPFM font source: reference/rpfm/mod.rs.

## Environment

- Attila install: D:\SteamLibrary\steamapps\common\Total War Attila
  (data\ holds our mod packs + vanilla packs; vanilla local_en.pack
  SHA256 45E0F087...970D must never change).
- Steam screenshots do NOT go to a Steam userdata folder for this game;
  the user copies them to D:\AttilaArabic\screenshots\ (names
  "Total War  Attila Screenshot ...png").
- reference/ is gitignored: other people's work, never commit.

## Clean-room findings (2026-10-08, offline, vanilla files only)

- VANILLA FONTS CARRY NO ARABIC OUTSIDE arialunicode. Reading the 65536-entry
  char table of all 38 vanilla CUFs (logs/cr_map_scan.txt): arialunicode_10-22
  (N=38948) map 100/100 of the Arabic codepoints our loc uses to real glyphs
  with ink; georgia_italic_10-18 (N=626) and la_gioconda_10-38 +
  la_gioconda_uppercase_10-38 (N=285) map 97/100 to a DANGLING entry
  (table[cp] == N, past the end of the glyph array). Only U+060C, U+061B and
  U+0640 are in range in those fonts. Dangling counts: arialunicode 3,
  georgia_italic 1278, gioconda/uppercase 4094.
- Therefore v8-v15 (31 CUFs = georgia_italic + la_gioconda + uppercase, no
  arialunicode) could only ever affect a surface if that surface draws from one
  of those fonts, and only via the v8 trick of appending glyphs and remapping
  the table. Any surface drawing from arialunicode_* was untouched by all of
  v8-v15 - the v15 faction-description anomaly (our georgia_italic_12
  half-blocks never appeared there) is exactly that.
- Appending glyphs + remapping table entries is proven to reach the screen
  (v8 onwards drew Arabic from gio/geo this way). It touches no existing glyph.
- The measured pitch table (FE92/FE98/FE9C/FEF4=8, FE8D=5, FE8E=6, FEF2=12,
  space=5) matches NO vanilla font's aw or w at any size (arialunicode_12 aw =
  4/4/4/4/4/4/13/4; _14 = 5x6/15/5; _16 = 5,5,5,5,5,6,17,6). It also matches
  neither our v14 nor v15 gio12/geo12 dims. The pitch source is still unknown;
  C1 (Shyizer, aw==w, per-font values differ) and C2 (font identity per
  surface) are designed to settle it.
- Shyizer coverage of our loc: 0 missing codepoints in all 37 CUFs; only
  U+000A/U+0020/U+00A0 are blank (logs/cr_C1_coverage.txt). Its v_size values
  equal Attila's vanilla ones for the same file names, so no clipping expected.
- Round-trip gate: all 38 vanilla CUFs decode->encode byte-identical
  (logs/cr_gate.txt), so the codec is trusted for clean-room builds.
