# CUF Investigation — fail-fast result: PASS (write path proven on copies)

Date: 2026-10-06. All work on COPIES under `extracted\` / `build\`.
Vanilla `local_en.pack` SHA256 before == after (see `logs\baseline.txt`).

## Verdict

**CUF decode AND encode work.** No blocker. Proceed to Phases 4–6.
(Tellos/etwng were NOT needed and not used; RPFM font support is
documented below for the record.)

## 1. Which fonts, where, what magic — VERIFIED

- 38 `font\*.cuf` in `local_en.pack` (table listing of working copy).
- `arialunicode_10.cuf`: magic **`CUF1`**, 9,151,760 B, 38,948 glyphs.
- `la_gioconda_10.cuf`: magic **`CUF0`**, 281,073 B, 285 glyphs.
- Both magics occur in Attila's pack (DOCUMENTED assumption "CUF0 everywhere"
  is false).

## 2. Tool support matrix

| Tool | Decode Attila CUF | Write Attila CUF | Label |
|------|-------------------|------------------|-------|
| RPFM 5.1.1 (`rpfm_lib::files::font`) | NO — rejects `CUF1` at signature gate (`DecodingFontUnsupportedSignature`); Attila `CUF0` also fails (dims overread, Empire layout assumed) | Empire-layout `CUF0` only (has `Encodeable` + round-trip test) | VERIFIED (master source read: `font/mod.rs` decode+encode; empirical overread on vanilla files) |
| Tellos CUF tool | not attempted — needs Java, Java is VERIFIED ABSENT; Empire-era, Attilacompat UNVERIFIED | same | — |
| etwng `cuf/cuf_unpack` | NO — Ruby unpack-only, expects `CUF0` Empire layout; Ruby VERIFIED ABSENT | cannot (unpack-only by design) | VERIFIED (source read, 92 lines) |
| Project codec `source\cuf.py` (new) | **YES** — both magics, exact parse (see §3) | **YES** — byte-identical round-trip + glyph-add test (see §4) | VERIFIED (hashes below) |

RPFM strings in `rpfm_server.exe`/`rpfm_ui.exe` do contain `CUFProperties`,
`Glyph`, `supports_kerning`, `kerning_blocks`, `line_height`, etc.
(VERIFIED) — the decoder exists, it just targets Empire's variant.

## 3. Attila CUF layout (empirically derived) — VERIFIED by exact byte-fit

```text
magic CUF0|CUF1
11x u16 props (line_height=10 for both size-10 fonts ✓)
u16 count N | u32 bitmap_bytes
65536x u16 char->code table
N x 4B dims (i8 alloc_h, u8 alloc_w, u8 w, u8 h) in CODE order 0..N-1
N x u32 bitmap offsets (cumulative running offset for ALL glyphs,
    including empty ones — differs from RPFM's 0-for-empty convention)
concatenated 8-bit grayscale bitmaps, sum(w*h) == bitmap_bytes
tail: kerning (u16 ksize, u16 skip, ksize*ksize bytes) or near-empty
```

Key difference vs Empire: the table has (almost) no `0xFFFF` entries —
unmapped chars ALIAS a default glyph code. Only char `0x0` uses `0xFFFF`,
plus 1 dangling code == N (PUA icons `U+F003+` in gioconda, `U+FFFE/F`
in arialunicode) that points past the dims section (engine tolerates it;
INFERENCE).

Fit check (VERIFIED): `32 + 131072 + N*8 + bitmap_bytes + tail == file size`
EXACTLY for both fonts; gioconda tail = `350, skip=33, 350*350` kerning
EXACT; arial tail = 6 bytes (`ksize=0, skip=0` + `0x0021`, meaning of last
2 bytes UNVERIFIED, preserved verbatim).

Props are human-sensible (VERIFIED): `line_height=10`, gioconda
`h_size=23 v_size=15`, arial `h_size=31 v_size=18`.

## 4. Write-path proof (on copies) — VERIFIED

- Round-trip `decode → encode`: **byte-identical** for both fonts
  (`build\la_gioconda_10.rt.cuf` 281,073 B; `build\arialunicode_10.rt.cuf`
  9,151,760 B).
- Glyph ADD: `la_gioconda` copy + 2 Arabic mappings (`U+0627/U+0628` →
  new code 285, bitmap copied from `A`): re-decodes with 286 glyphs,
  correct mappings, intact bitmap; re-encode is stable (identical bytes,
  `build\la_gioconda_10.plus2.cuf` 281,216 B).
- Therefore the merge strategy from change #1 (Arabic glyphs into a COPY
  of each vanilla `arialunicode_*` size) is implementable with `source\cuf.py`.

## 5. Arabic coverage in vanilla `arialunicode_*` — VERIFIED REAL (2026-10-06 addendum)

Method (`source\cuf_cluster.py`): bitmap-identity clustering. A mapping is
REAL iff its bitmap is non-empty AND not shared with known-unassigned probes
(`U+0378→0x2CE`, `U+2E9F→0x1207`) or any >40-codepoint fallback cluster.
Fallback defaults identified per font (e.g. size 10: most-common table value
`0x1551`, 6658 users, 13×18 bitmap with ink — the tofu box).

| Size | Codes | 0600–06FF real/aliased/empty | FB50–FDFF | FE70–FEFF |
|------|-------|------------------------------|-----------|-----------|
| 10 | 38948 | 252 / 0 / 4 | 688 / 0 / 0 | 144 / 0 / 0 |
| 12 | 38948 | 252 / 0 / 4 | 688 / 0 / 0 | 144 / 0 / 0 |
| 14 | 38948 | 252 / 0 / 4 | 688 / 0 / 0 | 144 / 0 / 0 |
| 16 | 38948 | 252 / 0 / 4 | 688 / 0 / 0 | 144 / 0 / 0 |
| 18 | 38948 | 252 / 0 / 4 | 688 / 0 / 0 | 144 / 0 / 0 |
| 20 | 38948 | 252 / 0 / 4 | 688 / 0 / 0 | 144 / 0 / 0 |
| 22 | 38948 | 252 / 0 / 4 | 688 / 0 / 0 | 144 / 0 / 0 |

Tables are identical across sizes (same probe mappings, same user counts);
only raster sizes differ. The 4 EMPTY codepoints in 0600–06FF (all sizes):
`U+0674, U+06DD, U+06E5, U+06E6` (zero-size bitmaps — genuinely missing
glyphs, not aliases; none needed for the v1 corpus).

Visual proof: `docs\arabic-glyphs-arialunicode_10.png` — contact sheet of
all 28 base letters × isolated/initial/medial/final (Forms-B) rendered from
the vanilla bitmaps (`source\cuf_sheet.py`). All cells green/real, shapes
visually confirmed as correct Arabic contextual forms (e.g. بـ ـبـ ـب,
س scintilla variants); top row shows the red fallback boxes for contrast.

Whether the engine selects these presentation forms for pre-shaped input
(and how it wraps them) is UNVERIFIED — decided by the v1 in-game test
(Phase 8). If vanilla renders correctly, NO Tajawal merge is needed.

## 6. Open items / risks (UNVERIFIED until later phases)

- Kerning indexing (per-char vs per-code) when ADDING glyphs; tail
  preserved verbatim for now — must re-examine before the real merge.
- Which `arialunicode` sizes the UI actually uses (10/12/14/16/18/20/22?).
- Whether the engine prefers CUF0 vs CUF1 on load (both ship vanilla, so
  both parse — INFERENCE: safe to keep each file's original magic).
- Pack type for the standalone mod (`release (1)` vanilla vs `mod (3)` /
  `movie (4)` per packfile.py) — Phase 2/7 experiment.
- RPFM still used for `.loc` + pack assembly; fonts handled by `source\cuf.py`.
