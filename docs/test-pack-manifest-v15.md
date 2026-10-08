# v15 probe manifest — what controls letter pitch?

Round goal: settle the two unknowns that blocked v11-v14, in ONE launch.
Base packs: v14 (bitmaps/loc), with in-place edits below. Vanilla
local_en.pack SHA256 verified before+after (unchanged).

## Measured ground truth (my own pixel measurements, v13 screenshot
2026.10.08-02.19.08.05, ERE box, georgia_italic_12)

| cp | v10 w | v13 w | v14 w | aw (all rounds) | pitch on screen | drawn ink | gap |
|----|-------|-------|-------|-----------------|-----------------|-----------|-----|
| FE92 | 6 | 8 | 9 | 5 | 8 (±1) | 7 | 1 |
| FE98 | 6 | 8 | 7 | 5 | 8 (±1) | 7 | 1 |
| FE9C | 6 | 8 | 7 | 5 | 8 | 3-4 (dot band) | - |
| FEF4 | 6 | 7 | 7 | 5 | 8 | 7 | 1 |
| FE8D | 3 | 5 | 5 | 3 | 5 (4-5) | 2 | 3 |
| FE8E | 4 | 4 | 5 | 3 | 6 | 4 | 2 |
| FEF2 | 9 | 9 | 10 | 8 | 12 | - | - |

Pitch did NOT move when w moved (v10→v13), and is identical in gio12 whose
aw differs → pitch is not our w, and aw has never been varied on a real
codepoint (v10's "aw ignored" used PUA codepoints that render as
placeholder → invalid). v12 solid blocks render at full bitmap size
(FE8D 5×18 block → ~5×18 bar), so bitmaps ARE drawn at true scale.
Model that fits every round: cell pitch P per codepoint (source unknown),
bitmap drawn at cell+1 (geo12 layout_x_offset=1) and clipped near P, so
drawn ink = min(w,P)-1 and a ~1px column between cells stays empty.
System-font advances (Segoe/Tahoma/Arial @12px) do NOT match P → not a
Uniscribe/system-font metric leak.

## v15 edits (in place, v14 bitmaps otherwise byte-identical)

georgia_italic_12: FE92 aw 5→2; FE98 aw 5→12; FEF4 bitmap = solid cols
0-3 only, w=8; FE8D bitmap = solid cols 4-9 only, w=10; FE9C, FE8E untouched.
la_gioconda_12: FE92 aw 6→12; FE98 aw 6→2 (font-independence cross-check).

## Lines on screen

ERE description (geo12), L1-L6: 20× FE92 / FE98 / FE9C / FEF4 / FE8D / FE8E.
WRE description (geo12), L1: 10×FE9C + phrase; L2: 10×FE98(aw12) + phrase.
Hard difficulty (gio12), L1-L3: 20× FE92 / FE98 / FE9C.

## Predictions

H_aw (pitch = aw + c, c≈+3):
  ERE pitches ≈ 5 / 15 / 8 / 8 / 6 / 6; Hard ≈ 15 / 5 / 8;
  WRE phrase on L2 starts ≈ +70px right of L1 phrase.
H_noaw (pitch engine-internal per codepoint):
  ERE pitches 8 / 8 / 8 / 8 / ? / 6; Hard 8 / 8 / 8; WRE phrases flush.
Window probe (independent of H_aw/H_noaw):
  L4 ticks: ink 3 wide (cols 1-3) → +1 draw offset confirmed; ink 4 starting
    at cell+0 → no offset.
  L5 ticks: ink 6 (cols 4-9 drawn) → no clip at P, w>P drawable → overlap
    fix possible; ink 4 (cols 4-7) → clip at P-1, inter-cell column never
    drawable → 1px gap is engine-intrinsic, fallback = hairline acceptance.
  L5 pitch: 5 → pitch fixed; 10-12 → pitch follows w when w>P.

## Measure after screenshots

`tools\venv\Scripts\python source\measure_ruler.py <ERE shot>` (bands map
L1-L6 in order); same script on Hard shot (3 bands); WRE: x of phrase ink
start on L1 vs L2.
