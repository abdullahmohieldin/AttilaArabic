# Test pack manifest — v11 in-place probes

Built by `source/build_v11.py` on top of the v10 packs:

- `release/Attila_Arabic_POC_v11_fonts.pack` — SHA256 `F8D586E9F5BDAB13ACF3AD1D3B1A28AA84C1F8A781A2E01C3B3DDBDC91687875`, 26,546,899 B.
  v10_fonts with exactly three IN-PLACE changes to `georgia_italic_12`; all other glyphs and all other 30 CUFs byte-identical:

  | glyph | before | after | change |
  |---|---|---|---|
  | FEF2 final yeh | (20,8,9,20), 180 B | (18,8,9,18), 162 B | refit to 18 rows (E120-style resample; dots now inside the box) |
  | FE92 medial beh | (18,5,6,18) | (18,5,8,18) | ink stretched horizontally 6 → 8 px |
  | FE8D alef | (18,3,3,18) | (18,3,5,18) | ink stretched horizontally 3 → 5 px |

- `release/Attila_Arabic_POC_v11.pack` — SHA256 `EF70FA33922A9732849AE4A385488A3E05E036ECC8C4AE945658D38DDCA34433`, 1,813,076 B.
  v10.pack with only the WRE description extended by 3 lines; ERE, the v10 WRE control lines, all other rows and all other .loc files byte-identical.

Vanilla `local_en.pack` SHA256 verified unchanged before/after. Unit tests 7/7 OK.

## WRE description lines to shoot (all georgia_italic_12)

| line | stored | what it is | prediction |
|---|---|---|---|
| L1 | 20 × FEF2 | **refit** final yeh (v10 screenshot = control: span 238, no dots) | span ≈ 237 if advance stays 12.0; dots visible = clipping/refit supported |
| L2 | 20 × E120 | placeholder control (must stay 277) | unchanged |
| L3 | 20 × E121 | placeholder control | unchanged |
| L4-L5 | 10 × E111 + رومة الغربية | pad controls | unchanged |
| L6 | 20 × FE92 | **stretched** medial beh | if advance stays 8.0: span 160, runs ~9 px, gaps 0 (continuous line) |
| L7 | 20 × FE8D | **stretched** alef | if advance stays 5.0: span 100, runs ~6 px, gaps 0 |
| L8 | shaped sentence | اثبات ثبات ثبت ثوب اثبات ثبات ثبت — repeated stretched FE92/FE8D in context | joins should touch; words slightly wider than v8 |

ERE description = v10's 9 clone lines unchanged (controls).

Side effect to expect: every medial beh in the whole UI (menus, tabs, labels)
is now 8 px wide — words render slightly wider and joins should look tighter
everywhere. That is the fix candidate working, not a regression.

## Measurements to make after the game (DeBo shoots, I measure)

1. Span + pitch + run width for L1, L6, L7 (and confirm L2/L3/L4/L5 unchanged).
2. FEF2: dots visible? bowl height vs the v10 control crop
   (`logs/crops/zoom/v10_wre_L1_fef2_6x.png`).
3. FE92/FE8D: do glyphs now visually touch the next glyph (gap gone)?
4. One menu screenshot: overall Arabic unchanged apart from wider beh joins.

## Verdict criteria

- FEF2 changed visually (dots or shorter bowls) → clipping/refit hypothesis
  gains support; next step = refit every over-box glyph (FEF1, FEF2, FE9E, ...).
- FEF2 unchanged/clipped → investigate engine vertical glyph handling.
- FE92/FE8D joins closed at unchanged pitch → fixed-advance hypothesis
  confirmed; proceed to full per-glyph stretched rasterization (each glyph
  stretched to its measured engine advance − 1).
- No join improvement → stop stretching; investigate glyph origin/sidebearing.
