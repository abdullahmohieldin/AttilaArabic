# CUF format — cross-tool reference

Sources: our codec (`source/cuf.py`, byte-fit VERIFIED on Attila CUF0+CUF1),
RPFM `rpfm_lib/src/files/font/mod.rs` (fetched to `reference/rpfm/mod.rs`,
docs.rs source view of latest rpfm_lib), Europa Barbarorum CUF tool
(`reference/cuf-tool/`, binary CUF.jar + javadoc only, no .java sources),
empirical Attila layout in `docs/cuf-investigation.md`.

## Header

magic `CUF0`|`CUF1`; 11 x u16 props: first_prop, second_prop, line_height,
fourth_prop, fifth_prop, baseline, layout_y_offset, space_justify,
layout_x_offset, h_size, v_size (RPFM names identical).
h_size/v_size = max render bounds; glyphs wider/taller appear cut off
(RPFM doc comment; matches our clipping observations).
space_justify = space width for justify/wrap (RPFM doc comment).
layout_x_offset / layout_y_offset = draw offsets of the bitmap inside the
cell (RPFM doc comment; geo12 has layout_x_offset=1, consistent with the
+1px draw offset measured on screen in v13/v15).

## Glyph record (dims section)

Per glyph, in code order: `i8 alloc_height, u8 alloc_width, u8 width,
u8 height`. alloc_width is the advance per RPFM/Empire semantics; in
Attila it demonstrably does NOT control pitch (v15: aw=2 and aw=12 on
FE92/FE98 changed nothing on screen).

## Char map — the Empire/Attila split

- Empire (RPFM, EB tool): per-glyph `(u16 code, u16 character)` pair list;
  RPFM Glyph struct also carries `code`, `character` and a `kerning: u32`
  field; dims are read by iterating characters 0..=u16::MAX.
- Attila: 65536 x u16 char->code table (unmapped chars alias a default
  glyph code; only U+0000 uses 0xFFFF), then N x u32 cumulative bitmap
  offsets including empty glyphs. RPFM rejects Attila files at the
  signature/dims gate; the EB tool is Empire-era and cannot read them.

## Bitmaps

Concatenated 8-bit grayscale, sum(w*h) == bitmap_bytes header field.
Only solid (255) pixels survive to screen; faint AA edges are dropped
(measured v9-v15).

## Kerning section (tail)

Layout (RPFM decode/encode, VERIFIED byte-fit on Attila gioconda tails):
`u16 size, u16 skip, then size x size u8 matrix`, row-major; entry [A][B] =
width of glyph A when followed by glyph B; values below A's normal advance
act as negative spacing. Codes below `skip` have no kerning row/col.
Attila files: la_gioconda_* tails = 350/33 matrix (122504 B); arialunicode
tails = 6 B (ksize 0). Whether the Attila engine READS it: NOT proven.

## EB CUF tool vs RPFM — differences

- Kerning section layout: AGREE (same u16/u16/matrix shape). EB tool
  exposes it as `CUFFont.kerning` + `CUFFont.kerningEnabled` (javadoc);
  RPFM as `supports_kerning`, `kerning_skip`, `kerning_blocks`.
  CUFWriter javadoc shows setters for HSize/VSize/GlyphDataSize but no
  kerning setter -> the EB tool writes kerning only when copying sources.
- Header props and glyph record order: AGREE (11 u16 props; i8/u8/u8/u8).
- Char map: both tools target the Empire pair-list layout; neither reads
  the Attila 65536 table (RPFM verified reject; EB tool Empire-era).
- RPFM additionally documents h_size/v_size clipping and space_justify
  semantics; the EB javadoc does not document prop semantics.
