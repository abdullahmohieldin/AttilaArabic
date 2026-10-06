# Fonts — sources and license

## Tajawal Regular (v3 test source)

- File: `fonts\upstream\Tajawal-Regular.ttf` (60,360 B)
- SHA256: `6882892DA3E03527d5db2bbab3b48bde6ef2e878a43f522d1a4eebda90010a19`
- Source: `https://raw.githubusercontent.com/google/fonts/main/ofl/tajawal/Tajawal-Regular.ttf`
  (upstream: `github.com/googlefonts/tajawal`)
- Designer: Boutros Fonts, Mourad Boutros, Soulaf Khalifeh — VERIFIED (Google Fonts)
- License: `fonts\upstream\OFL.txt`, SIL Open Font License 1.1 — VERIFIED
- **Reserved Font Name: NONE** — VERIFIED. The copyright line reads
  `Copyright 2018 Boutros International. (http://www.boutrosfonts.com)`
  with no "with Reserved Font Name(s)" declaration, so no name is reserved
  under OFL §1. Modification, embedding of derived bitmaps, and
  redistribution are permitted provided the license + copyright notice ship
  with any distribution (OFL §§2,5).
- Coverage note (VERIFIED via fontTools cmap, 446 glyphs): lacks 13 isolated
  Presentation Forms used by the corpus (FE83, FE8D, FE8F, FE93, FEA5, FEA9,
  FEAB, FEAD, FEC9, FEDD, FEE1, FEED, FEF1); v3 renders those from their
  Unicode base letters (compatibility decomposition). Everything else in the
  69-codepoint corpus, incl. U+2014, is in Tajawal's cmap.

## Vanilla fonts (reference only, never modified)

- Working copies under `extracted\fonts\` (from `local_en.copy.pack`).
- Merged outputs under `build\v3fonts\` (31 files).
