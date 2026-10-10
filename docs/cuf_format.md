# Creative Assembly CUF Binary Font Format Specification

> **Document Classification:** Reverse-Engineered Binary File Format Specification  
> **Target Engine:** Creative Assembly Warscape Engine (Total War: ATTILA / Rome II)  
> **Status:** FULLY REVERSE-ENGINEERED & VERIFIED BY CODEC

---

## 1. Overview

The `.cuf` (Creative Assembly Universal Font) format is a proprietary binary bitmap font container utilized across Total War titles from the Warscape engine era (*Empire*, *Napoleon*, *Shogun 2*, *Rome II*, and *Attila*).

While early iterations (*Empire / Napoleon*) utilized sparse pair-lists for character mapping, **Total War: ATTILA** utilizes a flat 64K lookup table with monolithic bitmap packing.

---

## 2. Binary File Layout

A standard Attila `.cuf` file contains five sequential sections:

```text
+-------------------------------------------------------+
| Header (26 bytes): Magic (4B) + 11 x uint16 Properties|
+-------------------------------------------------------+
| Glyph Dimensions Table: N x 4 bytes (alloc_h, aw, w, h)|
+-------------------------------------------------------+
| Character Mapping Table: 65,536 x uint16 (128 KB)    |
+-------------------------------------------------------+
| Bitmap Data Section: Sum(w * h) bytes (8-bit grayscale)|
+-------------------------------------------------------+
| Kerning Tail: uint16 size + uint16 skip + Matrix     |
+-------------------------------------------------------+
```

---

## 3. Detailed Structural Specification

### 3.1 Header (26 Bytes)

| Offset | Type | Field Name | Description |
| :---: | :---: | :--- | :--- |
| `0x00` | `char[4]` | `magic` | File signature: ASCII `'CUF0'` or `'CUF1'`. |
| `0x04` | `uint16` | `first_prop` | Type/rendering flags. |
| `0x06` | `uint16` | `second_prop` | Font style or weight flag. |
| `0x08` | `uint16` | `line_height` | Base vertical line spacing in pixels. |
| `0x0A` | `uint16` | `fourth_prop` | Ascender metric or internal flag. |
| `0x0C` | `uint16` | `fifth_prop` | Descender metric or internal flag. |
| `0x0E` | `uint16` | `baseline` | Distance from cell top to the baseline in pixels. |
| `0x10` | `uint16` | `layout_y_offset` | Global vertical offset applied when rasterizing cells. |
| `0x12` | `uint16` | `space_justify` | Space character width used for justification. |
| `0x14` | `uint16` | `layout_x_offset` | Global horizontal draw offset inside the cell. |
| `0x16` | `uint16` | `h_size` | Maximum glyph bounding box width. Larger glyphs clip. |
| `0x18` | `uint16` | `v_size` | Maximum glyph bounding box height. |

---

### 3.2 Glyph Dimensions Table (`dims`)

Following the header is an array of $N$ glyph records, ordered by internal glyph code:

| Size | Type | Field Name | Semantics |
| :---: | :---: | :--- | :--- |
| 1 byte | `int8` | `alloc_height` | Vertical quad placement metric ($Y_{\text{top}} = Y_{\text{baseline}} - ah$). |
| 1 byte | `uint8` | `alloc_width` | Declared advance width in Empire; ignored in Attila. |
| 1 byte | `uint8` | `width` | Width of the glyph's bitmap data in pixels ($w$). |
| 1 byte | `uint8` | `height` | Height of the glyph's bitmap data in pixels ($h$). |

---

### 3.3 Character Mapping Table (`char_table`)

Attila uses a flat array of **65,536 `uint16` values** (131,072 bytes total):
* Each index represents a Unicode Basic Multilingual Plane (BMP) codepoint (`0x0000` to `0xFFFF`).
* The value at `char_table[cp]` stores the internal glyph index ($0 \dots N-1$).
* Unmapped characters point to a fallback glyph index (or `0xFFFF` for `U+0000`).

> [!NOTE]
> Community tools like RPFM and the Europa Barbarorum CUF tool reject Attila `.cuf` files because they expect the legacy Empire-era `(code, character)` pair list rather than this flat 64K lookup table. Our standalone codec (`source/cuf.py`) natively supports the Attila layout.

---

### 3.4 Bitmap Data Section

The bitmap section contains raw, uncompressed 8-bit grayscale pixel bytes concatenated in glyph order:
* Each glyph consumes exactly $w \times h$ bytes.
* Pixel values range from `0` (transparent/background) to `255` (fully opaque ink).
* Total byte length matches $\sum_{i=0}^{N-1} (w_i \times h_i)$.

---

### 3.5 Kerning Section (Tail)

The file terminates with an optional kerning adjustment table:
* `uint16 kerning_size`: Number of kerned glyph entries.
* `uint16 kerning_skip`: First glyph code indexed in the table (typically 33 for ASCII `'!'`).
* `uint8[kerning_size * kerning_size]`: Row-major kerning matrix.
  * Entry `[A][B]` indicates the modified spacing when glyph `A` is followed by glyph `B`.
  * For standard Latin fonts in Attila, `kerning_size = 350`, covering codes $33 \dots 382$. High Unicode codepoints (including Arabic Presentation Forms) sit outside this matrix.
