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

Batch: 06:52 screenshots (5 files, C1 installed). Tools: `source/cr_lines.py`
(line finder), `source/cr_seams.py` (baseline-strip seams), `source/cr_glyphs.py`
(connected components), `source/cr_desc.py` (parchment-panel text mask),
`source/cr_pitch.py`, `source/cr_pairs.py`, `source/cr_fit_loc.py`.
Raw output: `logs/cr_c1_*.txt`. Crops: `logs/crops/C1/`.

**Prediction 1 CONFIRMED**: real Arabic on every surface, no placeholder boxes:
faction title bar, faction group labels + faction names in the panel, both
description boxes, difficulty box, campaign menu buttons, battle menu buttons,
choose-faction header, unit-info stat labels, unit dropdown, unit name
("COMES"), unit bullet points.

**Prediction 3 CONFIRMED**: no vertical clipping; Shyizer `v_size` matches.

#### Big finding 1 — DRAWN DIRECTION IS NOT RESOLVED (retracted claim)

I first wrote here that the engine mirrors our stored strings, from the fact
that the custom-battle button key stores
`FE94 FEBC FEBC FEA8 FEE3 0020 FE94 FEDB FEAE FECC FEE3` while the reader sees
`معركة مخصصة`. **That claim is retracted**: later measurements contradict it and
I could not settle it from the C1 pixels. Evidence for both sides:

* FOR mirroring: the stored byte order of the faction titles is the *reverse*
  of reading order (`factions_screen_name_att_fact_eastern_roman_empire` stores
  U+FE94 U+FEF4 U+FED7 U+FEAE U+FEB8 U+FEDF U+FE8D U+0020 U+FE8E U+FEE3 U+FEED
  U+FEAD, which reads as `روما الشرقية` only when reversed). The stored values
  are RTL visual order; the reader sees logical order.
* AGAINST mirroring: rendering the *stored* bytes left-to-right and overlaying
  them on the measured title strokes gives a converging fit
  (`logs/crops/C4_order/`, IoU 0.579 with the stored order at bitmap scale 1.6),
  i.e. as-drawn order == stored order.
* The CUF bitmaps themselves are NOT mirrored (verified directly: U+FE92 has its
  two dots below the baseline, U+FE94 its two dots above, U+FE8D no dots), so
  the font cannot explain the contradiction.

Cause of the disagreement: the C1 screenshots do not pin down which loc key
belongs to which on-screen element, nor the surface's font identity or scale.
Whole-line stored-vs-reversed comparisons split 3/3 fonts in one test and 1/6 in
another, and my first reversed-order harness dropped every glyph silently
(baseline 19 px < bitmap height 23 px, so the placement clip discarded them) —
the early "reversed" numbers were therefore meaningless, and the claim was
built on them.

**Status: unresolved. Do not author anything on either reading yet.** A loc
value only needs mirror compensation if the engine mirrors, and C1 cannot say.
The dedicated test that settles it is in "Next test" below.

#### Big finding 2 — pitch is NOT `aw` and NOT `w`

On-screen cell pitch, measured from repeated letterforms (distance between two
occurrences of the same codepoint on one line, divided by the sum of that font's
advances between them):

| surface | measured span | sum of Shyizer advances | implied scale |
|---|---|---|---|
| custom battle button `معركة مخصصة`, FE94→FE94 (ink starts x162 → x239) | 77 px | georgia_italic_16 79, georgia_italic_14 76, la_gioconda_16 78, la_gioconda_12 64 | ≈1.0 at 16 px |
| campaign-menu button `الحملة الكبرى`, FE8D→FE8D (run x240 → x264) | 24 px | georgia_italic_16 32, la_gioconda_16 31, georgia_italic_24 49, la_gioconda_12 25 | 0.75 (16 px) |
| battle-menu button `معركة تاريخية`, FE94→FE94 | 12.5 px for 3 glyphs | — | ≈4.3 px per glyph |
| ERE description line 0, FE92→FE92 (`الرومانية`) dot cluster x524.5 → x556.5 | 32.5 px | georgia_italic_16 22, la_gioconda_16 22, georgia_italic_24 32, la_gioconda_20 30 | **1.48** |

So the same font family is used at *different* scales on different surfaces and
the ratio is not 1.0, which is exactly why the `aw`-and-`w` fit never converged
(best fits came out at scale 0.40-1.7 depending on surface, i.e. unconstrained).
`FEF2` could not be isolated: the codepoints our loc uses around it differ per
string, and the two occurrences in a string are always separated by many
non-repeat codepoints, so its advance is not separately identifiable in C1.

#### Join gap (seams), baseline strip (`cr_seams.py`, threshold 180)

Seam = blank columns between two ink runs **inside one word** along the bottom
3-7 rows (the Arabic connecting stroke). Word gaps (>=6 px) are excluded.

| string | seams (px) | verdict |
|---|---|---|
| `اختر الفصيل` (title bar) | 1,1,1,1,1,1 | zero gaps; letters joined, 1 px hairline only |
| `اختر الفصيل` (custom-battle header) | 1,1,1,1,1,3,1,1 | one 3 px seam |
| `معركة مخصصة` (main menu) | 2,3,3,1,1,4,4,1,3,1 | 4 px seams = the visible breaks |
| `إعدادات المعركة` (campaign menu) | 1,1,1,1,1,4,3,3,1,1,1,1,1,1 | 3-4 px seams |
| `معركة تاريخية` (battle menu) | 1,1,1,1,1,3,2,3,1,1,1,1,1,1 | 2-3 px seams |

So 1 px seams dominate (rendering hairline) and the eye-visible breaks are the
3-4 px ones, which fall at *word* boundaries and before `م`/`خ`/`ة`. The 1 px
seams are the draw-window artefact measured in v13 (ink = min(w,pitch)-1), not
an advance problem: at 16 px the seam is 1 px, i.e. one background column
between cells.

#### Other measurements

- Description box: line baselines y621, y639, y657, y675 → **line pitch 18 px**;
  text block x396-711 (315 px). 10 authored lines are drawn; the 11th is clipped
  at the box bottom (half-height row at y~690), so C1's description is 1 line
  too long — the same overflow C0 had.
- Difficulty box (right panel, x1170-1580): Arabic description lines y417-431
  and y436-449 → pitch **19 px**, text x1261-1519 (line 1 258 px, line 2
  175 px), label y391-405.
- Word gap in the menu buttons is 8-9 px (the 12 px fonts give U+0020 advance
  4-5 px), i.e. the engine adds space width on top of the space advance.

### Next test — C4 as designed (settles direction, wrap and alignment in one launch)

Because C1 cannot settle the drawn direction, the next pack must settle it by
construction instead of by inference. One pack, three declared changes, each
readable from one screenshot:

1. **Direction ruler.** U+FD3E/FD3F are unusable (0/37 fonts carry ink). Use two
   clone glyphs instead, in the style of C3: append two glyph records per font
   whose bitmap is a column-clipped copy of that font's own U+FE92, one 6 px
   wide, one 13 px wide, both with `aw == w`. Remap two unused codepoints to
   them (U+FEC7 = 6 px, U+FE9A = 13 px). Then one line of 20 x U+FEC7 followed
   by 20 x U+FE9A, and the mirror line 20 x U+FE9A then 20 x U+FEC7. The two
   halves are visually unmistakable (thin stems vs broad stems), so the
   on-screen arrangement reads the drawn direction directly, with no font or
   scale assumption and nothing to do with Arabic orthography.
2. **Same-line stress**: the two rulers on the faction title bar, the ERE
   description box and the difficulty box (3 surfaces, 2 lines each).
3. **NBSP pad test**: the difficulty description gets, line by line, a leading
   pad of 9 / 0 NBSPs (variant A = none for the other key), so left- vs
   right-alignment shows as which edge the text hugs.

Predicted: if the engine draws as-stored, the FD3E line shows the left-parens on
the LEFT; if it mirrors, they appear on the RIGHT. No other measurement is
needed. Packs `Attila_Arabic_CR_C4.pack` + `_C4_fonts.pack` once rebuilt on this
design (the pack currently in `release/` was built on the retracted mirror
hypothesis and must not be installed).

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

## C3 — advance-width sweep (aw vs w), all 37 fonts — SUPERSEDED BY C5

Status: built (`Attila_Arabic_CR_C3.pack` 1814120 B + `_fonts.pack` 33042160 B)
but **never launched**; C5 carries the same idea plus the direction ruler and is
the pack to install. The C3 build as shipped used codepoints `U+FEC7`, `U+FE9A`,
`U+FEF5`, `U+FE8E` with `aw = w - 2` in all four rows; the reasoning below was
written for that build and is kept only as history. See the C5 section for the
design actually under test.

Declared change, one variable only: four Arabic codepoints our loc does not use
(`U+FEC7`, `U+FE9A`, `U+FEF5`, `U+FE8E`) get **one new glyph record each** in
**every one of the 37 fonts**. The bitmap of each new record is a column-clipped
copy of that font's own `U+FE92` bitmap; `aw` is set to `w - 2` in all four
records. Nothing else is touched (asserted at build time: original dims,
bitmaps, header props and kerning tail byte-identical, and only those 4 table
entries differ per font).

Per font: `FE92.w = W`. The bitmap of each new record is a column-clipped copy
of that font's own FE92 bitmap, and its `aw` is set to the *bitmap width of its
own row*, so each row's `aw` differs from its bitmap `w` by a constant offset:

| line | codepoint | bitmap width w | declared advance aw | relation |
|---|---|---|---|---|
| 1 | U+FEC7 | W-2 | W-2 | aw == w |
| 2 | U+FE9A | W-1 | W-2 | aw == w-1 |
| 3 | U+FEF5 | W   | W-2 | aw == w-2 |
| 4 | U+FE8E | W+1 | W-2 | aw == w-3 |

(`logs/cr_C3_build.txt` prints the full aw/w pair set for all 37 fonts.)

If the pitch follows `aw`: all four rows have the **same pitch** (aw = W-2 in
every row) and the row ink widths **shrink** by ~1 px per row only because the
bitmap is narrower. If the pitch follows the bitmap `w`: the rows differ by
exactly 1 px of pitch each, 20 cells apart, so the 20-copy row width **grows**
by ~19 px per row from line 1 to line 4 (rows 2-4 then also show 1-3 blank
columns of slack after each cell because aw < w).

Loc: each of ERE description, WRE description, difficulty description and the
campaign-menu "battle settings" button gets, prepended, 4 lines of 20 copies of
one codepoint each (20 x 4 = 80 glyphs). Packs:
`Attila_Arabic_CR_C3.pack` + `Attila_Arabic_CR_C3_fonts.pack` (test only).

### Predicted on screen

1. Four rows of identical shape (all are the FE92 beh stem) on each of the four
   surfaces. Row 1 has the narrowest ink cell, row 4 the widest.
2. `aw`-model prediction: **all four rows show the same pitch** = the pitch of
   the surface (whatever it is), 20 copies spanning 20 * P px, and the ink of
   rows 2-4 leaves 1-3 extra blank columns at the right of each cell. Row width
   order = 1 < 2 < 3 < 4 only because the bitmap is wider, not the pitch.
3. `w`-model prediction: row pitches P1 < P2 < P3 < P4 with P4 - P1 ≈ 3 px, so
   the 20-copy row width grows ~57-60 px from row 1 to row 4.
4. Scalars to read: row ink span (first to last ink column) / 19 = pitch of that
   row. On the difficulty box (19 px line pitch) and on the descriptions
   (18 px line pitch) 4 extra lines fit; the button shows only its own line.
5. Kerning hypothesis (same pack, no extra change): the 350/33 matrix covers
   codes 33..382 only, so **no Arabic Presentation-Form Code is inside it**
   (`logs/cr_C3_kerning.txt`) — FE92 (code 683) and every joining form we use
   are outside. The matrix cannot affect Arabic pitch; its only negative deltas
   are for Latin `A`-like codes. So no pair-width change was shipped for C3.
6. Falsifier: rows with a pitch *smaller* than the bitmap width (that would mean
   the engine clips the advance to `w`) or a row whose ink span does not scale
   linearly in the number of copies.

### Measured

_(to be filled from the screenshots)_

---

## C5 — aw sweep + direction ruler in one pack (supersedes C3)

Declared change on top of C1, in one font pack and one loc pack. Per font, six
new glyph records are appended (nothing existing is modified — asserted per font:
original dims, bitmaps, header props and kerning tail byte-identical; exactly
those six table entries differ). Every record's bitmap is a horizontal resample
of that font's own U+FE92 artwork (its own W x H), so the rows differ only in
the two numbers under test.

Let `W = FE92.w = FE92.aw` in the font being drawn, and let `P` be whatever pitch
that surface actually uses. The probe block (six lines, in this stored order) is
prepended to four keys: ERE description, WRE description, difficulty
description, campaign-menu battle-settings button.

| row | content | bitmap w | declared aw | copies |
|---|---|---|---|---|
| 1 | U+FEF5 | W-2 | W-2 | 14 |
| 2 | U+FE71 | W+2 | W-2 | 12 |
| 3 | U+FE79 | W+2 | W+1 | 12 |
| 4 | U+FE86 | W+2 | W+2 | 10 |
| 5 | U+FEC7 x16 then U+FE9A x11 | 5-6 / 12 | = w | 27 |
| 6 | U+FE9A x11 then U+FEC7 x16 | 12 / 5-6 | = w | 27 |

Rows 2-4 carry an **identical bitmap** and differ only in `aw`, so the two
hypotheses are ~19 px apart per row and cannot be confused with an ink
difference. Row 1 is the control (bitmap and aw both from FE92 itself).

Row widths were checked before building (`logs/cr_C5_build.txt`), worst case
over all 37 fonts at the calibrated ≈1 px per advance unit: 224 / 192 / 228 /
200 / 212 / 247 px against a 300 px budget and the 345 px widest line the engine
has demonstrably drawn in this panel. **No probe row should wrap.**

### Predicted on screen

**1. Pitch (the aw question).** Rows 2 and 3 are the decisive pair: they draw
the **same bitmap** (W+2) yet declare advances 3 apart (W-2 vs W+1). Worked
through for `georgia_italic_12` (W=5, so bitmap W+2 = 7 px, advances 3 / 6 / 7):

| row | bitmap w | aw | copies | row width if `aw` controls | row width if `w` controls | if a fixed pitch P |
|---|---|---|---|---|---|---|
| 1 U+FEF5 | 3 | 3 | 14 | 42 | 42 | 14 P |
| 2 U+FE71 | 7 | 3 | 12 | 36 | 84 | 12 P |
| 3 U+FE79 | 7 | 6 | 12 | 72 | 84 | 12 P |
| 4 U+FE86 | 7 | 7 | 10 | 70 | 70 | 10 P |

* **`aw` controls the pitch** → row 2 = 36 px and row 3 = 72 px (a 36 px
  difference, 3 px per cell) even though both draw the same 7 px bitmap; row 2's
  ink sits in a 3 px cell so cells 4-7 of its bitmap are clipped and the ink-to-
  ink pitch is 3 px.
* **`w` controls the pitch** → rows 2 and 3 are **identical** (84 px, pitch
  7 px); the difference between row 2 (36) and row 2-as-drawn is the giveaway.
* **fixed font-independent pitch P** (the v13 conclusion) → all four rows share
  one P, so row2 == row3 exactly and row1/row2 = 14/12 = 1.167, row2/row4 =
  12/10 = 1.2.
* The same logic at `la_gioconda_12` (W=6): aw-controlled gives 48 / 48 / 84 /
  80; w-controlled gives 84 / 84 / 84 / 80 — again rows 2 and 3 are the pair to
  read.
* Falsifier for all three: a row width that is not a whole multiple of its copy
  count (per-cell kerning or justification in play).

**2. Direction ruler (the reading-order question).** U+FEC7 is drawn as a
resampled FE92 stem 5 px wide, U+FE9A as the same stem 12 px wide; both have
`aw == w` (5 and 12 in every font), so pitch and ink agree and each block's
extent is unambiguous. Row 5 stores thin-then-broad, row 6 stores
broad-then-thin.

* If the engine **draws the stored order**: row 5 shows the thin block at the
  **left** end of its line and the broad block at the right; row 6 shows broad
  left, thin right.
* If the engine **mirrors** the value before drawing: row 5 shows the broad
  block at the left and the thin at the right — i.e. rows 5 and 6 appear swapped
  relative to the above.
* **If the engine draws stored order but places a prepended block at the END of
  the value**: both rows still appear as two blocks, but the whole probe block
  lands at the *bottom* of the box instead of the top. That does not change
  which block is left/right inside a row, so the direction reading is unaffected
  — it only changes where the six rows sit. This is the case C3 alone could not
  distinguish, and it is why the ruler rows exist.
* No bidi reordering of the two blocks is expected (no neutral or Latin
  characters inside a row), so any reversal is the engine's own.
* Falsifier: more than two blocks in a row, or a row whose two blocks are
  separated by more than a few px (a word gap would mean a space crept in).

### Measured

_(to be filled from the screenshots)_

---

## After C0-C2

Only when all three are analysed: propose the next single change. No combining.
