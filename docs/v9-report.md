# v9 diagnostics report — ruler + pad probe (v8r)

Round goal: find the real engine advance (join-gap cause), test right-align
padding, and isolate the final-yeh dots question. One diagnostics pack
(`v8r`) built on top of the unchanged `v8_fonts`. No verdict in this report —
the ruler spans and pad indents stay UNVERIFIED until the in-game screenshots.

Labels: VERIFIED = own decode of the packs or pixel measurement on the
2026-10-07 screenshots. INFERENCE = conclusion drawn from those facts, still
needing the screen. The screen wins over any model or offline test.

---

## Step 1 answers

### 1. Ruler pack post-mortem — VERIFIED

`v8_ruler.pack` loaded fine; it simply contains **vanilla English text** for
both keys:

| key | v8.pack value | v8_ruler.pack value |
|---|---|---|
| `start_pos_factions_description_2120156326` | Arabic, 476 chars | English, 712 chars ("The division of the Roman Empire has uns…") |
| `random_localisation_strings_string_campaign_difficulty_description_2` | Arabic, 53 chars | English, 36 chars ("For players familiar with Total War.") |

Header type and file list are identical in both packs (PFH4, type 3, same 8
files), so the container was never the problem.

Root cause in `source/build_v8.py` (ruler section):

```python
711:    ruler_want = {}
712:    for k, variants in ruler_strings.items():
713:        for tag, txt in variants.items():
714:            ruler_want[f"{k}_{tag}"] = txt
...
726:            if k in ruler_want and _owner(k) == internal:
727:                val = ruler_want[k]
```

Line 714 builds keys like `start_pos_factions_description_2120156326_ruler_beh20`.
Line 726 then tests the *real* row key against that dict — no row key ever has
a `_ruler_*` suffix, so `val = ruler_want[k]` never executed and every .loc was
re-encoded vanilla. Design flaw on top: 3 variants cannot share one .loc key —
a key maps to exactly one value. The variants must be LF-separated lines
inside one value, which is what `v8r` stores.

### 2. Description lines — VERIFIED

Measured on `…04.56.04.56.png`, text area x 368–692, borders/ornaments
excluded. All 10 full text lines start at exactly **x = 368**:

| line | y | min-x | max-x | width | stored leading spaces (U+0020) |
|---|---|---|---|---|---|
| 1 | 612–628 | 368 | 651 | 284 | 4 |
| 2 | 630–646 | 368 | 691 | 324 | 0 |
| 3 | 651–663 | 368 | 569 | 202 | 23 |
| 4 | 667–681 | 368 | 655 | 288 | 4 |
| 5 | 686–699 | 368 | 623 | 256 | 9 |
| 6 | 705–718 | 368 | 674 | 307 | 0 |
| 7 | 723–735 | 368 | 657 | 290 | 4 |
| 8 | 740–753 | 368 | 652 | 285 | 3 |
| 9 | 758–772 | 368 | 638 | 271 | 7 |
| 10 | 774–790 | 368 | 691 | 324 | 16 |

The v8 pack really stores leading spaces on ERE lines 1,3,4,5,7,8,9,10,11
(3–27 spaces) and on all 11 WRE lines (1–14 spaces) — decoded from the pack.
The screen ignores every one of them: **the engine trims leading whitespace**.
Independently, the vanilla English description in the ruler-test screenshot
(05.08.56) is also flush-left ragged-right, so the description component is
**left-aligned by design**; right-aligned Arabic needs either surviving pad
glyphs (probed in v8r) or the UI-layout alignment field (deferred research).

### 3. Width on screen — VERIFIED measurement, INFERENCE model update

47 description words aligned by rank (screen word k ↔ stored token k,
10/10 lines matched). Per word: predicted ink = Σ(aw) − left bearing of first
glyph − right gap of last glyph, **no R\* tax**.

Result: mean extra **+2.82 px/glyph** (stdev 0.37, range +1.5…+3.6; no trend
with word length → constant per-glyph tax is the right family).
R\* update: geo12 **2.48 → 2.82** (INFERENCE — refine again after the ruler).

Words alone cannot separate "engine advance = aw + c" from "= w + c′";
the ruler lines do. Predictions (S = 19·advance + last ink width):

| hypothesis | L1 (20×FE92) | L2 (20×FE8D) | L1−L2 |
|---|---|---|---|
| advance = aw + c (c≈2.82) | ≈155 px | ≈114 px | 41 |
| advance = w + c′ (c′≈1.82) | ≈155 px | ≈95 px | 60 |

S1−S2 = 41 vs 60 decides the family independent of the constant; S2 then
calibrates the constant. If beh and alef need different constants, that is
reported instead of forcing one fit.

### 4. Join test on screen pixels — VERIFIED

Full-height detector (a): a column with no ink (<250) across the whole word
height. Five long geo12 description words, aligned to stored tokens:

| word (line) | glyphs | expected breaks | gap runs found |
|---|---|---|---|
| L1 (11 gl) | 11 | 3 | 10 runs, 2–4 px, all "soft" |
| L4 (11 gl) | 11 | 2 | 10 runs, 2–3 px |
| L7 (11 gl) | 11 | 3 | 10 runs, 2–4 px |
| L8 (8 gl) | 8 | 3 | 7 runs, 2–4 px |
| L2 (6 gl) | 6 | 1 | 5 runs, 2–4 px |

("soft" = no pixel darker than 180 — faint AA remnants only.) Every join is
open by roughly **2–4 px**; the count of gap runs ≈ glyphs−1, far above the
expected real breaks. Detector (b) (connector rows) was weak: the bitmap edge
columns share ≤1 ink row (edge AA), so it could not add signal — the bitmaps
themselves barely touch even before the engine adds its tax.

Consistent explanation (INFERENCE): engine advance ≈ aw + 2.8, i.e. ~1.8 px
past the ink of a connecting glyph (v8_fonts wrote aw = ink−1), leaving the
observed 2–4 px gaps. The −1 overlap hack cannot close a 2.8 px tax.

Tab word الإمبراطوريات: stored correctly (12 glyphs incl. lam-alef-hamza
ligature U+FEF9 — all 8 ligature forms FEF5–FEFC VERIFIED present in
georgia_italic_12). On-screen join check for the tab word: UNVERIFIED — the
tab label box is contaminated by frame art in the screenshot; the description
evidence stands on its own.

### 5. Yeh / alef maksura audit — VERIFIED

Counts of shaped forms across all v8 values (full table in the build log):
ERE description: FEF0=1, FEF2=1, FEF3=5, FEF4=12. WRE description: FEF0=3,
FEF2=4, FEF3=9, FEF4=11. 31 words across the pack end logically in a yeh-form
(visual-first glyph FEF1/FEF2) or alef-maksura form (FEF0/FEEF).

Raw source spellings (from `build_v8.py` literals, U+XXXX):

| word | raw source | final letter | MSA spelling |
|---|---|---|---|
| الروماني | 0627 0644 0631 0648 0645 0627 0646 **064A** | ي | same |
| الداخلي (WRE src) | …062E 0644 **064A** | ي | same |
| في | 0641 **064A** | ي | same |
| التحدي / المبدئي | …062F **064A** | ي | same |
| على | 0639 0644 **0649** | ى | same (ى is correct) |
| كبرى | …0628 **0649** | ى | same |
| الرومانى (with ى) | **not present anywhere** | — | — |

Correction to the handoff: the sources do **not** use ى for the yeh words —
they use MSA ي (only على/كبرى/المدى are genuine alef-maksura words). So the
on-screen dotless words الروماني/الداخلي/في/التحدي/المبدئي/السياسي/المتداعي/
استراتيجي are **real dotted-yeh words losing their dots**; على/كبرى are
dotless by design and correct. Resolving the earlier contradiction: "zero
U+0649" (raw letters) and "strings end in FEF0" (shaped forms) were both
true — the reshaper converts 0649→FEF0/064A→FEF1/FEF2; the .loc stores only
presentation forms.

Additional defect found during the audit (VERIFIED, unfixed in v8r by the
byte-identical rule): `land_units_onscreen_name_att_rom_legio` is stored in
**logical order** (`FED3 FEF4 FEE0 FED6 0020 FEAD FEED FEE3 FE8E FEE7 FEF2`),
not visual order — a live `shape("فيلق روماني")` returns the reversed string
and does not match. It would display reversed on screen. It was not visible in
any tested screenshot (unit names were not on those screens). Fix in the next
font/loc round; the double-shaping or missing-bidi path in the builder that
produced it should be found then.

### 6. Vertical anchor and dots — VERIFIED bitmaps, INFERENCE clipping

Props: georgia_italic_12 `baseline=15, v_size=18, layout_y_offset=3`;
la_gioconda_12 `baseline=15, v_size=19, layout_y_offset=4`.

Vanilla glyphs in the same CUFs are full line-box bitmaps — 'g','y','p','j',
comma all h=18 (geo12) with descender ink inside rows 15–17, i.e. vanilla
keeps descenders **inside** the box (baseline row 15, ≤3 rows below).

Our over-box glyphs (VERIFIED): geo12 has 138 glyphs with h>18 — including
FEF1 (isolated yeh) h=20, FEF2 h=20, FE9E h=20; lgi12 FEF1/FEF2/FE9E h=21
(+2 over its 19-row box). FEF0 h=18 and FEF4 h=18 (geo12) fit the box.

FEF2 dots sit in rows 18–19 (geo12, alpha 54–177 after the 1.6 boost) and
rows 19–20 (lgi12, alpha 182–240) — exactly the rows beyond v_size.

Hypothesis (INFERENCE): the engine draws bitmaps anchored to the font baseline
prop and clips at v_size rows; any bitmap taller than the box loses its bottom
rows. This explains every observation: FEF4 (in-box) dots render; FEF1/FEF2
dots vanish in **both** fonts regardless of alpha; FEF0 is dotless by design.

Screen checks: no dot remnants at الروماني (8× and threshold-boosted crops —
nothing above noise). Final jeem: **no word in any v8 value ends in jeem**
(0 hits), so the "jeem bowl cut" check is UNVERIFIED — nothing to look at;
the v8r L3 line (20×FEF2) is the decisive in-isolation test in both fonts.

Fix direction for the next font round (not this one): rasterize every glyph
into the vanilla-style line box (scale/compress the outline to fit, like
vanilla 'g'), instead of extending the bitmap below v_size.

### 7. Pad glyphs — VERIFIED

| glyph | geo12 dims | geo12 ink | lgi12 dims | lgi12 ink |
|---|---|---|---|---|
| U+0020 space | (−128, 4, 0, 0) | none | (−128, 5, 0, 0) | none |
| U+00A0 NBSP | (−128, 4, 0, 0) | none — clean blank | (−128, 5, 0, 0) | none |
| U+2003 EM SPACE | (18, 10, 10, 18) | 9/180 px stray dash | (19, 5, 5, 19) | 5/95 px |
| U+E000 PUA | (18, 9, 9, 18) | 58/162 px — real ink | (19, 13, 13, 19) | 105/247 px |

Confirms and corrects the plan: NBSP is a true blank; U+2003 has a stray dash;
U+E000 is **not** a 1px transparent blank — it is a small visible glyph. The
probe is still valid (three distinct advances: 4/10/9 in geo12) and the two
visible pads double as unambiguous position markers.

---

## Step 2 build log

- `source/build_v8r.py` (new): decodes v8.pack, replaces exactly 3 values,
  re-encodes only `start_pos_factions.loc` and
  `random_localisation_strings.loc`; the other 6 files are raw byte copies.
- Ruler lines stored verbatim (no reshaper/bidi). WRE phrase `روما الغربية`
  shaped first, pads concatenated after (pads at stored positions 0–9 —
  verified in the dumps below).
- Self-checks: v8r header PFH4 type 3 ✓; file list == v8 ✓; untouched 6 files
  byte-identical ✓; untouched rows of the 2 edited files identical ✓; vanilla
  `local_en.pack` SHA256 before and after
  `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` ✓ (unchanged).
- Unit tests: test_key_mapping 4/4 OK, test_join_continuity 2/2 OK,
  test_baseline_regression 1/1 OK (7/7).

Stored values (U+XXXX):

```
start_pos_factions_description_2120156326
  L1: FE92 x20
  L2: FE8D x20
  L3: FEF2 x20
  L4: FE8D 0020x20 FE8D
random_localisation_strings_string_campaign_difficulty_description_2
  same 4 lines
start_pos_factions_description_2120156339
  L1-2: 00A0 x10 + FE94 FEF4 FE91 FEAE FED0 FEDF FE8D 0020 FE8E FEE3 FEED FEAD
  L3-4: 2003 x10 + (same phrase)
  L5-6: E000 x10 + (same phrase)
```

- **release/Attila_Arabic_POC_v8r.pack — SHA256
  `668604BF3567D0CDC31BA104C7276E199A7F90AF9639E16BF5033DC0C6C308F5`,
  1,812,828 bytes.**
- v8_fonts stays untouched (SHA unchanged from v8 round).

## Test instructions (DeBo)

1. Delete `Attila_Arabic_POC_v8.pack` and `Attila_Arabic_POC_v8_ruler.pack`
   from `data\`. Keep `Attila_Arabic_POC_v8_fonts.pack`.
2. Copy `release\Attila_Arabic_POC_v8r.pack` into `data\`.
3. Launcher → Mod Manager: tick **only** `Attila_Arabic_POC_v8_fonts` and
   `Attila_Arabic_POC_v8r`.
4. Screenshots (1920×1080, no UI scaling changes):
   a. Faction select → **Eastern Roman Empire** selected (ruler lines in
      georgia_italic_12).
   b. Faction select → **Western Roman Empire** selected (pad-probe lines).
   c. Difficulty slider on **Hard** (same ruler lines in la_gioconda_12,
      centered).
   d. One sanity shot (main menu or custom battle) — everything else should
      look exactly like the v8 round.
5. Expected: the ERE description shows four gibberish ruler lines instead of
   Arabic — that is intended. What matters:
   - L1 vs L2 span difference (41 vs 60 px class) and absolute spans
     (≈114/95 px) → which advance field the engine uses.
   - L3: do the 20 final-yehs show dots? (both fonts via ERE vs Hard).
   - L4: distance between the two alefs → space advance.
   - WRE: which pad type (NBSP / EM-space / E000) indents the lines, and by
     how many px.
