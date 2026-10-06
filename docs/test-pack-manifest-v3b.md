# Test Pack Manifest — v3b / v3b_big (BUILD ONLY, test after approval of results)

- v3b: `D:\AttilaArabic\release\Attila_Arabic_POC_v3b_fonttest.pack`
  (31 merged CUFs, current-size rules)
- v3b_big: `D:\AttilaArabic\release\Attila_Arabic_POC_v3b_big.pack`
  (31 merged CUFs, raised px, cells may exceed v_size by ≤2px)
- Both PFH4 type `mod (3)`. Same 70-codepoint corpus
  (`localization\corpus_v2b_full.txt` = v1+v2 Arabic + U+2014 noted).
- `source\v3_check.py` on both sets: **ALL FONTS PASS, 0 missing**;
  Latin U+0020–U+007E byte-identical; kerning tails identical; magic kept.
- Build logs: `logs\v3b_build.txt`, `logs\v3bbig_build.txt`
  (per-font px, cell, counts; `missing_src=0 clipped=0` everywhere).

## Size issue (your task 4)

v3 calibration matched Tajawal cap-height to vanilla `H`, then reduced px
until all 70 glyphs fit the vanilla cell (e.g. gioconda_10: px 13→10).
Consequence: Arabic x-height ~25–30% under Latin caps (INFERENCE from px
ratios) — matches your "smaller" observation. Baseline alignment itself
rendered correctly in your v2+v3 test (your VERIFIED observation).

- v3b: unchanged rules (deterministic rebuild + 1 new codepoint).
- v3b_big: px starts at cap-match (e.g. _10: px 13 vs 10); cells grow upward
  past v_size by ≤2px max (baseline row preserved; e.g. _10 maxcell 16 vs 15).
  Whether the engine clips above v_size is UNVERIFIED — that is exactly what
  the big-pack test decides. If big clips, stay with v3b sizing; if big
  draws, adopt big px as the new baseline.
