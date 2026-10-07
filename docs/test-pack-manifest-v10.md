# Test pack manifest — v10 calibration probe

Two packs, built by `source/build_v10.py`:

- `release/Attila_Arabic_POC_v10_fonts.pack` — SHA256 `BD83458B10D527F45A6721FAA2D60E295EA44B0E7299E85E9F0BA7ECF11C1ADE`, 26,546,845 B.
  v8_fonts with 11 PUA glyphs **added to georgia_italic_12 only**; the other 30 CUFs are byte-identical; no existing glyph touched.
- `release/Attila_Arabic_POC_v10.pack` — SHA256 `660890238F543997C823987E462C452FE4655A5BE121D41A1EE6BD56D326242A`, 1,812,924 B.
  v8.pack with exactly 2 values replaced (ERE + WRE descriptions); the other 7 .loc files byte-identical.

Vanilla `local_en.pack` SHA256 verified unchanged before and after both builds.
Unit tests: 7/7 OK. Records decoded back from the built packs — aw and w are
written as independent fields (table in the build log).

## What v9 established (VERIFIED, see chat / v9 report)

Engine advance per codepoint is **font-independent**: geo12 and gio12 ruler
spans are identical (158 / 97 / 238) despite different (aw, w) records.
Measured advances: FE92→8.0, FE8D→4.95, FEF2→12.05, space→5.0 (alef-to-alef
105 = 5 + 20×5), U+2003→6.0 pitch, U+E000→14.0 pitch, NBSP→~0.9.
v6 vs v8 FE92 differ only in aw (6 vs 5); screen unchanged → aw ignored.
The advance matches neither our aw, nor our w, nor arialunicode_12 records
(beh = alef there but 8 ≠ 5 measured), nor GDI fallbacks tested (Arial/TNR/
Tahoma @ 16/21/24 px em). Source of the advance: UNRESOLVED — the CUF tail
holds a 350-entry per-glyph-like array (identical in vanilla/v6/v8, our
glyphs beyond its range); indexing unresolved.

## ERE description lines (georgia_italic_12)

| line | stored | what it is | what I should see |
|---|---|---|---|
| L1 | 20 × U+E100 | beh clone, (aw,w)=(6,6) | solid 6px-wide block row, 20× |
| L2 | 20 × U+E101 | beh clone, (aw,w)=(5,6) | same ink as L1 |
| L3 | 20 × U+E102 | beh clone, (aw,w)=(6,4) | narrower 4px blocks |
| L4 | 20 × U+E103 | beh clone, (aw,w)=(4,6) | same ink as L1 |
| L5 | 20 × U+E104 | beh clone, (aw,w)=(8,6) | same ink as L1 |
| L6 | 20 × U+E105 | beh clone, (aw,w)=(6,8) | blocks with 2px gap inside |
| L7 | FE8D + 20 × U+E110 + FE8D | blank (4,4) | two alefs far apart |
| L8 | FE8D + 20 × U+E111 + FE8D | blank (8,8) | two alefs far apart |
| L9 | FE8D + 20 × U+E112 + FE8D | blank (8,0) | two alefs, spacing tells |

### Predictions per hypothesis (span in px, alef distance for L7-L9)

Pitch hypothesis → span = 19 × advance + last ink (6 for w≥6 clones, 4 for L3):

| line | H_fallback14 (unknown cp → 14, like E000) | H_w (adv = w+2) | H_aw (adv = aw+2) |
|---|---|---|---|
| L1 (6,6) | 272 | 158 | 158 |
| L2 (5,6) | 272 | 158 | **139** |
| L3 (6,4) | 270 | **118** | 158 |
| L4 (4,6) | 272 | 158 | **120** |
| L5 (8,6) | 272 | 158 | **196** |
| L6 (6,8) | 272 | **196** | 158 |
| L7 blank (4,4) | 285 | 125 | 85 |
| L8 blank (8,8) | 285 | 205 | 165 |
| L9 blank (8,0) | 285 | 45 | 165 |

Discriminating pairs: L2 vs L1 (aw only), L4 vs L5 (aw only), L3 vs L6
(w only). If all six lines render identically (~272), the engine ignores
both fields for unknown codepoints and the fallback is constant — then the
join fix cannot come from record tuning at all.

## WRE description lines (georgia_italic_12)

| line | stored | what it is | what I should see |
|---|---|---|---|
| L1 | 20 × U+FEF2 | original final yeh (control) | 20 bowls, NO dots (replicates v9) |
| L2 | 20 × U+E120 | FEF2 refit into 18 rows, dots inside box | 20 bowls, slightly shorter |
| L3 | 20 × U+E121 | FEF2 shifted up 2 rows, same 20-row record | 20 bowls riding high |
| L4-L5 | 10 × U+E111 + shaped رومة الغربية | blank-(8,8) pad probe | indented phrase |

Predictions:

- Dots: if L2 or L3 shows dots while L1 does not → the over-box clipping
  hypothesis is CONFIRMED (engine clips bitmaps at the font's row box) and
  the fix is to rasterize every glyph into the box like vanilla 'g'.
  If L2/L3 also show no dots → the dots are lost before clipping (rasterizer
  or alpha); next probe targets the raster stage.
- Pitch: L1 should repeat v9's 238 px. L2/L3 are new codepoints — span 275 if
  the unknown-codepoint fallback (14) applies, ~237 if the engine reads the
  CUF record for new codepoints (then record tuning is alive for new glyphs).
- L4/L5 indent: phrase starts at ≈508 (fallback 14), ≈478 (w+2 = 10), or
  ≈448 (aw+2 = 8) after the 10 pads.

## Test steps (DeBo)

1. Delete `Attila_Arabic_POC_v8r.pack` (and v8/v8_ruler if still present) from
   `data\`. Keep `Attila_Arabic_POC_v8_fonts.pack` **only if** you also keep
   v8r for comparison — otherwise remove it: v10 replaces it.
2. Copy `Attila_Arabic_POC_v10_fonts.pack` and `Attila_Arabic_POC_v10.pack`
   into `data\`.
3. Mod Manager: tick **only** `Attila_Arabic_POC_v10_fonts` +
   `Attila_Arabic_POC_v10`.
4. Screenshots (1920×1080):
   a. Faction select → **Eastern Roman Empire** (9 calibration lines).
   b. Faction select → **Western Roman Empire** (3 FEF2 lines + 2 pad lines).
   c. One sanity shot (menus must look exactly like the v8 round).
5. Upload all three; I will measure spans, alef distances, indents, and dots
   per the prediction tables above and call each hypothesis.

## RESULTS (2026-10-07, screenshots 07.37.33.86 / 07.37.36.81 / 07.37.39.37) — measured

| line | predicted (fallback14 / w+2 / aw+2) | measured | verdict |
|---|---|---|---|
| ERE L1-L6 (all 6 clones) | 272/270 or mixed 118..196 | **277 every line, pitch 14.0, 20 runs of 11px** | fallback-14 |
| ERE L7-L9 alef distance | 285 / 125-205 / 85-165 | **285 exactly (alefs at x368 and x653)** | fallback-14 |
| WRE L1 (FEF2 control) | 238 | **238, pitch 12.0, 10px bowls (our bitmap)** | replicates v9 |
| WRE L2-L3 (E120/E121) | 275 or ~237 | **277, 11px placeholder runs** | placeholder |
| WRE L4-L5 phrase indent | 508 / 478 / 448 | **~508** | fallback-14 |

Key findings:

1. **H_fallback14 CONFIRMED.** For codepoints the engine does not know
   (PUA E1xx), both aw and w are ignored; advance is a constant 14 and the
   engine draws its **own placeholder glyph** (11px blob + apostrophe mark,
   pixel dump in logs/crops/zoom/v10_wre_L2_E120_6x.png) — our clone bitmaps
   were never rendered.
2. **Real presentation forms DO use our bitmaps** (WRE L1: 10px Tajawal bowls)
   with the mystery per-codepoint advance (FEF2 = 12).
3. **The dots experiment did not run** — E120/E121 rendered as placeholders,
   so the over-box clipping hypothesis is still untested. The only way to test
   it is to modify a REAL codepoint's bitmap in place in a probe fonts pack.
4. Record tuning (aw/w) is a dead end for the join fix. The remaining lever is
   the bitmap itself: stretch each glyph's ink to (engine_advance − 1) px so
   joins close. Engine advances are measurable per codepoint with 20x ruler
   lines (method proven in v9/v10).
5. Sanity: campaigns/battles menus identical to the v8 round (Arabic OK).

Next probe (v11, one fonts pack + one loc): in-place geo12 changes —
FEF2 refit-18 (dots test), FE92 stretched 6→8px and FE8D 3→5px (join test),
loc lines 20×FEF2 / 20×FE92 / 20×FE8D + one real sentence.
