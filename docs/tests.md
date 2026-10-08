# Clean-room test log

Rule: predictions are written **before** the launch; measured results are written
**after** the screenshot is read. One declared change per test, one launch each.
Builder: `source/cr_build.py <C0|C1|C2>`, configs in `configs/`. Installer:
`python install.py <C0|C1|C2|v14|none>`.

## Structural evidence gathered before C0 (offline, vanilla files only)

From `source/cr_map_scan.py` (logs/cr_map_scan.txt), reading the 65536-entry
char table of all 38 vanilla CUFs extracted from `local_en.pack`:

| font file | glyph count N | our 100 Arabic codepoints in range | dangling table entries |
|---|---|---|---|
| arialunicode_10..22 (7) | 38948 | **100/100, all with real ink** | 3 |
| georgia_italic_10..18 (5) | 626 | **3/100** (only U+060C U+061B U+0640) | 1278 |
| la_gioconda_10..38 (13) | 285 | **3/100** | 4094 |
| la_gioconda_uppercase_10..38 (13) | 285 | **3/100** | 4094 |

"Dangling" = `table[cp] >= N`, i.e. the entry points past the end of the glyph
array. Vanilla `georgia_italic_*`, `la_gioconda_*` and `uppercase_*` therefore
contain **no Arabic glyphs at all**; only `arialunicode_*` does.

Consequence for the legacy line of work: our 31-font pack (v8..v15) shipped
georgia_italic + la_gioconda + uppercase and **never shipped an arialunicode**,
and v8 reached Arabic in those fonts only by appending glyphs and remapping the
table. Any surface that draws from `arialunicode_*` was untouched by all of
v8..v15 — which is exactly the v15 anomaly (the faction description box ignored
our georgia_italic_12 half-blocks and kept showing shaped Arabic).

Shyizer's Rome II set (37 CUFs, reference only): 144 Presentation-Forms-B
codepoints in range in **every** font, 131-136 with ink, `aw == w`. Its
`v_size` values match Attila's vanilla ones for the same file names
(arial12 21, georgia_italic_12 18, la_gioconda_12 19).

---

## C0 — vanilla fonts + our loc (no font pack)

Declared change: the two faction description keys use the tatweel-free
`long_description_*` values. Everything else is v14 loc text verbatim.
Pack: `release/Attila_Arabic_CR_C0.pack` (1813448 B, SHA256 B09302E641204AB2…).

### Predicted on screen

1. Surfaces drawing from an `arialunicode_*` font: **real Arabic glyphs**. Our
   text is already pre-shaped to Presentation Forms-B and those codepoints have
   genuine vanilla bitmaps, so the letter shapes should be correct and joined in
   shape, but cramped: arialunicode_12 advances are aw=4 for FE92/FE8D/FE8E and
   aw=13 for FEF2, i.e. much narrower than the 8/5/6/12 px we measured in v13.
2. Surfaces drawing from georgia_italic / la_gioconda / uppercase: a row of
   identical **placeholder boxes** at ~14 px pitch, except U+060C (،) U+061B (؛)
   U+0640 (ـ) which are in range and will draw.
3. Hard wraps (embedded `\n`) are respected; each line renders in the authored
   visual order. Difficulty box stays centred, faction description left-aligned.
4. **The faction description box shows real Arabic**, not boxes — because v15
   proved our georgia_italic_12 edits never reached it. This is the key C0
   prediction: it says the box's font is an `arialunicode_*` size.
5. The description text is 10 hard-wrapped lines (ERE) whose widths were
   computed with the v14 advance model, which the clean-room scan no longer
   supports. Expect **overflow/clipping** in the box; the number of lines that
   fit is itself a measurement (gives the box's line height and capacity).
6. Falsifier: if the description box shows boxes, its font is gio/geo and the v15
   anomaly has a different cause (then C2 must explain it).

### Measured

Screenshots 2026-10-08 06:40 batch (6 files). **Predictions 1 and 4 FALSIFIED.**

1. No surface shows real Arabic. No placeholder boxes either: every Arabic
   codepoint draws **blank (zero ink) but still consumes advance**. Surviving
   ink is only ASCII `.` `:` and the in-range U+060C/U+061B/U+0640.
2. Blank on every Arabic surface: faction title bar, faction group labels,
   ERE+WRE description boxes, difficulty box, campaign and battle menu buttons,
   choose-army header, unit name, unit stat labels, bullet points. English text
   everywhere unaffected ("Prologue", "Hard", "Very Hard", "Magister Militum",
   stat numbers all render).
3. ERE description box: 9-10 punctuation marks stacked at the LEFT edge
   (x≈380-424, y≈638-782), one per wrapped line → hard wraps respected, RTL
   puts the trailing mark left, ~10 lines fit with no clipping. Line pitch
   ≈18 px (row diffs 14/18/22).
4. Implied line widths: box right edge ≈722, marks at x 380-424 → lines are
   298-342 px wide vs the 350 px v14 wrap target. Blank glyphs advance at
   roughly the v13 pitch table, so the pitch table still describes this surface.
5. Revised conclusion: every Arabic surface draws from a font whose table has
   Arabic dangling = georgia_italic / la_gioconda / uppercase. `arialunicode_*`
   is used by none of them. Dangling entries draw blank, not a box (revises the
   v10 "placeholder drawn" note, which was about in-range glyphs we created).
6. v15 anomaly revised: the description box does draw from a font we shipped,
   but not the one we probed. v13's PUA ruler appeared in this box (so its font
   is one of our 31), while v15's half-block probes sat in georgia_italic_12 and
   the box kept showing v14-surgery ticks → the box's font is a la_gioconda or
   uppercase size, not georgia_italic_12. C2 decodes which.

---

## C1 — Shyizer's 37 CUFs byte-for-byte + C0 loc

Declared change: font pack only. Test pack is generated from `reference/` at
build time and is **never committed**.
Packs: `Attila_Arabic_CR_C1.pack` (identical bytes to C0's loc) +
`Attila_Arabic_CR_C1_fonts.pack` (37 CUFs, verified byte-for-byte vs source).

Offline coverage check (`logs/cr_C1_coverage.txt`): of the 194 codepoints our
loc uses, **0 missing in every one of the 37 fonts**; the only blanks are
U+000A, U+0020, U+00A0 (whitespace, expected).

### Predicted on screen

1. Arabic renders as **connected letters on every surface** — no placeholder
   boxes anywhere, since all 37 fonts carry ink for all 100 Arabic codepoints.
2. Advance question, the point of this test. Shyizer sets `aw == w` and the
   values differ per font for the same codepoint (U+FE92: arialunicode_12 aw=6,
   georgia_italic_12 aw=5, la_gioconda_12 aw=6; U+FEF2: 11 / 9 / 10).
   - If pitch follows `aw`, letters butt exactly and joins close.
   - If the engine adds the +2.82 px/appended-glyph tax measured in v9, letters
     separate by ~2-3 px gaps.
   - If pitch is font-independent (the v15 conclusion), the same codepoint shows
     the same pitch on surfaces using different fonts. Measuring FE92/FEF2 pitch
     on two surfaces with different fonts settles it.
3. No vertical clipping of glyphs: Shyizer's `v_size` equals Attila's for the
   same names. The description box still carries C0's 10 hard-wrapped lines, so
   expect the same box overflow as C0 — but with different per-glyph advances
   the lines will be a different width, which is a direct advance measurement.
4. Falsifier: boxes anywhere → that surface uses a font file Shyizer does not
   ship (e.g. `la_gioconda_uppercase_8/9`, absent from Attila's local_en.pack).

### Measured

_(to be filled from the screenshots)_

---

## C2 — font identity barcodes on vanilla CUFs

Declared change: 3 glyph records appended to each of the 38 vanilla CUFs
(index N = blank, N+1 = solid block, N+2 = blank) and 11 real, non-PUA,
unused-by-our-loc codepoints remapped to an 11-slot barcode carrying the font
id. The same barcode string is placed on 13 keys over 9 surfaces.
Packs: `Attila_Arabic_CR_C2.pack` + `Attila_Arabic_CR_C2_fonts.pack`.

Marker codepoints (all Arabic block, all spacing, none used by our loc, none
used by English text): U+0606 U+0607 U+0608 U+0609 U+060A U+060B U+060D U+060E
U+060F U+0620 U+06FD.

Barcode layout: `BLOCK BLOCK b7 b6 b5 b4 b3 b2 b1 b0 BLOCK`, b* = font id in
binary MSB first. The asymmetric sync (2 blocks at one end, 1 at the other)
reveals whether the engine bidi-reversed the run.

No existing glyph record, bitmap, header prop or kerning tail is modified
(asserted per font at build time); the only table edits are the 11 markers.
Side effect: index N becomes a blank glyph, so chars that were dangling
(unknown/PUA) draw nothing instead of the placeholder box.

### Font → marker table

`logs/cr_C2_markers.txt` (id 0-6 arialunicode_10..22, 7-11 georgia_italic_10..18,
12-24 la_gioconda_10..38, 25-37 la_gioconda_uppercase_10..38).

### Predicted on screen

1. Each marked surface shows 11 slots, ~12-14 px apart, bar height = that
   font's `v_size`, bar width = min(10, pitch) − 1 column.
2. Read left→right, decode the 8 middle slots → font id → table above.
3. Expected from the v15 anomaly: the ERE/WRE **faction description box reports
   an arialunicode id (0-6)**; difficulty box / menu buttons / unit cards report
   la_gioconda or uppercase ids (12-37).
4. A surface showing 11 placeholder boxes instead of a barcode means its font is
   **not one of the 38 vanilla CUFs** — that is itself an identification.
5. Latin UI text unchanged everywhere (no existing glyph was touched).
6. Falsifier: a barcode appearing at a width/height that matches no font's
   v_size, or two different fonts reporting the same id.

### Measured

_(to be filled from the screenshots)_

---

## After C0-C2

Only when all three are analysed: propose the next single change. No combining.
