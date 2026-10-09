# Phase 1 — Round 2 Predictions & Experiment Specification

**Document Version:** 2.1  
**Phase:** 1 (Clean-Slate Rendering Proof)  
**Round:** 2  
**Date:** 2026-10-10  
**Status:** DRAFTED PRIOR TO REBUILD (Pre-Commitment)

---

## 1. Ground-Truth Analysis of Round 1 Results

All measurements below performed on the 4x nearest-neighbor upscale ([`scratch/Phase1_R1_05_4x.png`](file:///d:/AttilaArabic/scratch/Phase1_R1_05_4x.png)) and full 1080p screenshot [`Phase1_R1_01_faction_select_ere.png`](file:///d:/AttilaArabic/screenshots/Phase1_R1_01_faction_select_ere.png).

### 1.1 Redone Faction Title Analysis (Full-Screen Y≈521–536, Crop Y≈215–230)
- **Observed Surface:** A horizontal strip of dark ink situated immediately above the ornamental divider line at Full $Y = 532$ (crop $Y = 226$) and directly above "Faction Leader: Emperor Arcadius" (Full $Y = 544$, crop $Y = 238$).
- **Visible Span & Height:**
  - Horizontal span: $X = 380\text{ to } 670\text{ px}$ (width $\approx 290\text{ px}$).
  - Vertical ink span: Full $Y = 525\text{ to } 530\text{ px}$ (crop $Y = 219\text{ to } 224\text{ px}$).
  - Visible height: **$5\text{ to } 6\text{ px}$**.
- **Nature of the Cut:**
  - Across all $290\text{ px}$ of width, every vertical stroke is cut completely flat at horizontal line Full $Y = 525$.
  - Above Full $Y = 525$, there is clear parchment space; below Full $Y = 530$, it reaches the horizontal divider frame.
  - **Verdict on Cut:** Hard horizontal cut at Full $Y = 525$. Two competing hypotheses:
    1. **UI Component Scissor Clip (INFERENCE):** The UI layout component (`clip_to_bounds` scissor rect of `tx_faction_name`) bounding box top boundary is at Full $Y = 525$. The upper $\sim 12\text{–}18\text{ px}$ of the ascenders are discarded by the GPU scissor test because the UI element bounding box is too short for Tajawal Arabic ascenders at this size.
    2. **Font Vertical Extent / Placement Mismatch (INFERENCE):** Our Arabic glyphs for this font size are placed too high (insufficient top margin / excess baseline distance) or are taller than the font line cell, causing ascenders to project above the component baseline or cell boundary. (See Section 6 for full vertical extent measurements across all font sizes).
- **Identity of Text:**
  - Width ($290\text{ px}$) matches the calibrated 3-word title "الإمبراطورية الرومانية الشرقية" rendered at 24pt ($283\text{ px}$).
  - Stroke structure shows multiple vertical Alef/Lam stems on the right, medial loops in the center, and final Yeh/Heh curves on the left (matching LTR visual order).
  - **Verdict:** Most likely **`factions_screen_name_att_fact_eastern_roman_empire`** (**INFERENCE**).

---

### 1.2 Description Box Probe Ledger (Corrected Evaluation)

| Hypothesis / Probe | Probe In Round 1 Build | Predicted | Observed Measurement (4x Upscale) | Corrected Finding & Status |
|---|---|---|---|---|
| **H1: Direction** | Rows 1 & 2: Asymmetric ruler (5px vs 12px stems) | LTR if thin stems on left; RTL if on right | In Row 1, thin stems appear on the LEFT, thick on the RIGHT. In Row 2, thick stems appear on the LEFT, thin on the RIGHT. | **VERIFIED**<br>Warscape renders strings strictly LTR without internal Bidi reversal. |
| **H2: Pitch** | Row 3: Sweep of $w=8$ with $aw=6, 8, 10$ and control $w=6, aw=8$ | Advance determined by $aw$ or $w$ | All 3 blocks with $w=8$ rendered with identical **$9.00\text{ px}$ pitch** ($8 + 1$). Control block ($w=6$) rendered with **$7.00\text{ px}$ pitch** ($6 + 1$). | **VERIFIED**<br>Advance width $aw$ is completely ignored. Pitch is strictly $\text{pitch} = w + 1\text{ px}$. |
| **H3: Joining Seams** | Row 4: `shape("القاهرة مصر")` + chunk `تر` | Continuous strokes if $aw$ respected; gap if $w+1$ | Baseline across per-letter Forms-B has a visible **$1.00\text{ px}$ gap** ($4\text{ px}$ in 4x) between adjacent letters. Pre-rendered chunk `تر` has **$0.00\text{ px}$ gap** across all $10\text{ px}$ of baseline stroke. | **VERIFIED**<br>Individual Forms-B glyphs suffer a 1px seam due to $\text{pitch} = w + 1$. Pre-composed chunks join with 0px seam. |
| **H4: Kerning Delta** | `CP_KERN_A` / `CP_KERN_B` assigned in CUF | Detectable distance shift | Codepoints were assigned in the CUF font table but omitted from the loc string. Did not appear in the description box. | **UNVERIFIED (Omitted from Loc)** |
| **H5: Ink Thresholding & Grayscale** | Row 5: 6x `CP_INK_SOLID` vs 6x `CP_INK_GRAY` | Solid ink crisper than grayscale on parchment | Visual inspection on 4x crop: Gray Yeh rendered visibly with intermediate alpha (mean luminance $\sim 82$), confirming the engine blends partial alpha values. Solid Yeh rendered with saturated ink (lum $\sim 43$). Gate 0 claim ("only solid 255 renders") is re-labeled as **INFERENCE** (disproven; engine does render anti-aliasing, but binary ink is substantially crisper). | **VERIFIED (Visual)** |
| **H6: Vertical Clipping** | Row 5: 6x `CP_TALL_ALEF` ($+3\text{ px}$ height, $h=10\text{ px}$) | Clipped if bounding box clamped by line height | Measured vertical span = **$10.00\text{ px}$** intact. Clear parchment space observed above and below. Zero scissor clipping at font cell boundaries. | **VERIFIED**<br>Box line spacing accommodates taller glyphs without line-level clipping. |
| **H7: Right Alignment** | Row 6: 8x NBSP (`\u00A0`, $w=0, aw=5$) + marker word | Right-aligned to margin if spaces push line | NBSP had $w=0$; under $\text{pitch} = w + 1$, each NBSP advanced by only $0 + 1 = 1\text{ px}$. 8 NBSPs produced a $6\text{–}8\text{ px}$ indent. Because $w=0$ confounded advance, testing whether spaces push to right margin was not cleanly tested. | **INCONCLUSIVE** |
| **H8a: Unwrapped Wrapping** | Row 9: 110-character unwrapped sentence | Auto-wrapped at margin | Wrapped into 4 visual lines (widths 188px, 301px, 218px, 280px). Words reordered backwards across visual lines because whole-string Bidi was broken by engine line wrapping. | **VERIFIED** |
| **H8b: Hard-Broken Lines** | Rows 7 & 8: Explicit `\n` breaks | Top-to-bottom sequence | Lines 7 and 8 rendered cleanly on sequential lines. | **VERIFIED** |
| **H8c: Box Overflow** | Row 10: Overflow probe string | Truncated at box bottom | The description box scrolls, and the crop was taken mid-scroll. Truncation at box boundary is not proven. | **UNVERIFIED** |
| **H9: UI Formatting Tags** | Assigned to tooltip | Colors preserved | Tooltip was not captured in Round 1 screenshots. | **UNVERIFIED** |

---

## 2. Round 2 Target Surfaces & Disambiguation Markers

All target surfaces are located on the **Faction Selection Screen** so a single 1920x1080 capture covers every key.

Every duplicate entry is assigned a **unique visible marker prefix** (e.g. `[B1]`, `[B2]`) so the in-game screenshot immediately proves which key is live:

| Surface Role | Localisation File | Database Key | Disambiguation Marker | Vanilla Text | Proposed Replacement Text |
|---|---|---|---|---|---|
| **Start Campaign Button** (Primary) | `uied_component_texts.loc` | `uied_component_texts_localised_string_button_txt_NewState_Text_30006e` | **`[B1]`** | `'Start Campaign'` | `[B1] ` + `shape("بدء الحملة")` |
| **Start Campaign Button** (Fallback) | `uied_component_texts.loc` | `uied_component_texts_localised_string_string_NewState_Text_30006e` | **`[B2]`** | `'Start Campaign'` | `[B2] ` + `shape("بدء الحملة")` |
| **Factions Header** (Text) | `uied_component_texts.loc` | `uied_component_texts_localised_string_tx_factions_NewState_Text_90022` | **`[F1]`** | `'Factions'` | `[F1] ` + `shape("الفصائل")` |
| **Factions Header** (Selection) | `uied_component_texts.loc` | `uied_component_texts_localised_string_selection_txt_NewState_Text_90022` | **`[F2]`** | `'Factions'` | `[F2] ` + `shape("الفصائل")` |
| **Factions Header** (Tooltip) | `uied_component_texts.loc` | `uied_component_texts_localised_string_tab_factions_Tooltip_90022` | **`[F3]`** | `'Factions'` | `[F3] ` + `shape("الفصائل")` |
| **Difficulty Tooltip** (Handle State) | `uied_component_texts.loc` | `uied_component_texts_localised_string_handle_NewState_Tooltip_7000b` | **`[T1]`** | `'Difficulty Slider\|\|Move this...'` | `[T1] ` + `shape("مؤشر الصعوبة")` + `"\|\|"` + `shape("حرك لتغيير الصعوبة")` |
| **Difficulty Tooltip** (Handle Base) | `uied_component_texts.loc` | `uied_component_texts_localised_string_handle_Tooltip_7000b` | **`[T2]`** | `'Difficulty Slider\|\|Move this...'` | `[T2] ` + `shape("مؤشر الصعوبة")` + `"\|\|"` + `shape("حرك لتغيير الصعوبة")` |
| **Difficulty Tooltip** (Slider Comp) | `uied_component_texts.loc` | `uied_component_texts_localised_string_cmp_diff_slider_Tooltip_7000b` | **`[T3]`** | `'Difficulty Slider\|\|Move this...'` | `[T3] ` + `shape("مؤشر الصعوبة")` + `"\|\|"` + `shape("حرك لتغيير الصعوبة")` |
| **Hard Label** (Level 3 Dynamic) | `random_localisation_strings.loc` | `random_localisation_strings_string_difficulty_level_3` | **`[H1]`** | `'Hard'` | `[H1] ` + `shape("صعب")` |
| **Hard Label** (Static Hard) | `random_localisation_strings.loc` | `random_localisation_strings_string_hard` | **`[H2]`** | `'Hard'` | `[H2] ` + `shape("صعب")` |
| **Hard Label** (Legacy Tooltip) | `uied_component_texts.loc` | `uied_component_texts_localised_string_medal1_default_Tooltip_5003a` | **`[H3]`** | `'Hard'` | `[H3] ` + `shape("صعب")` |
| **Difficulty Description** | `random_localisation_strings.loc` | `random_localisation_strings_string_campaign_difficulty_description_2` | **`[D1]`** | `'For players familiar with Total War.'` | `[D1] ` + `shape("للاعبين المتمرسين في توتال وور.")` |
| **Cultural Trait Header** | `uied_component_texts.loc` | `uied_component_texts_localised_string_header_cultural_NewState_Text_5e0000` | **`[C1]`** | `'Cultural Trait'` | `[C1] ` + `shape("السمة الثقافية")` |
| **Faction Screen Title** | `factions.loc` | `factions_screen_name_att_fact_eastern_roman_empire` | **`[FT]`** | `'Eastern Roman Empire'` | `[FT] ` + `shape("الإمبراطورية الرومانية الشرقية")` |
| **Faction Description** | `start_pos_factions.loc` | `start_pos_factions_description_2120156326` | — | Multi-line narrative | Compact 8-line probe suite (fits visible window) |
| **Faction Long Description** | `start_pos_factions.loc` | `start_pos_factions_long_description_2120156326` | — | Multi-line narrative | Identical compact 8-line probe suite |

---

## 3. Description Box: Patched 8-Line Non-Scrolling Probe Suite

Measurement from `Phase1_R1_01` at scroll offset 0 demonstrates that the visible description window spans from Full $Y = 625\text{ to } 810\text{ px}$ ($185\text{ px}$ height). With standard $\sim 18\text{ px}$ line pitch, **exactly 10 lines fit without scrolling**.

To guarantee 100% of probe lines remain visible simultaneously without scrolling, the suite contains exactly **8 compact lines** using **Unicode Private Use Area (PUA) codepoints `U+E000`–`U+E00A`**:

### Line 1: H3 Joining & Bleed Comparison (Word "مصر")
$$\text{Line 1} = \text{"[H3] "} + \text{Plain Forms-B} + \text{"   "} + \text{Bleed Forms-B} + \text{"   "} + \text{Pre-rendered Chunk}$$
- **Plain Forms-B:** `U+FEAE` (Reh) + `U+FEBC` (Sad medial) + `U+FEE3` (Meem initial). Tight bounding box.
- **Bleed Forms-B:** `CP_BLEED_REH` (`0xE001`) + `CP_BLEED_SAD` (`0xE002`) + `CP_BLEED_MEEM` (`0xE003`). Widened by 1 ink column on connecting side.
- **Pre-rendered Chunk:** `CP_CHUNK_MISR` (`0xE000`). Single 3-letter pre-rasterized glyph.

### Line 2: H4 Kerning Delta Probe
$$\text{Line 2} = \text{"[H4] "} + (\text{CP\_KERN\_A} + \text{CP\_KERN\_B}) + \text{"   "} + (\text{CP\_KERN\_A} + \text{CP\_KERN\_B})$$
- Uses codepoints `CP_KERN_A` (`0xE004`) and `CP_KERN_B` (`0xE005`).

### Line 3: H5 Ink Thresholding & Diacritics
$$\text{Line 3} = \text{"[H5] "} + (\text{Solid Yeh} \times 4) + \text{" "} + (\text{Gray Yeh} \times 4) + \text{" "} + \text{shape("شَدَّة كَسْرَة")}$$
- Uses `CP_INK_SOLID` (`0xE007`) and `CP_INK_GRAY` (`0xE008`), plus real Arabic Shaddah and Kasrah diacritics.

### Line 4: H6 Vertical Boundary Probes
$$\text{Line 4} = \text{"[H6] "} + (\text{Tall Alef } +3\text{px} \times 4) + \text{" "} + (\text{Deep Descender Yeh } -3\text{px} \times 4)$$
- Uses `CP_TALL_ALEF` (`0xE00A`) and `CP_DEEP_YEH` (`0xE009`).

### Line 5: H7a Leading Plain Spaces Test
$$\text{Line 5} = \text{"        [H7A] "} + \text{shape("مسافات")}$$
- Starts with **8 plain spaces** (`0x20`). Tests whether the engine strips leading whitespace or advances by $8 \times (w_{\text{space}} + 1)$.

### Line 6: H7b Leading Blank 40px Glyph Test
$$\text{Line 6} = \text{CP\_BLANK\_40} + \text{"[H7B] "} + \text{shape("فراغ")}$$
- Starts with one blank glyph of width $w = 40\text{ px}$ (`CP_BLANK_40` = `0xE006`, empty bitmap). Expected advance = $40 + 1 = \mathbf{41\text{ px}}$.

### Line 7: H7c Inline Blank 40px Glyph Test
$$\text{Line 7} = \text{"[H7C] "} + \text{shape("بداية")} + \text{CP\_BLANK\_40} + \text{shape("نهاية")}$$
- Places the $40\text{ px}$ blank glyph (`0xE006`) mid-line between two words to directly measure inline advance without leading-whitespace trimming interference.

### Line 8: H9 UI Formatting Tags & Placeholders
$$\text{Line 8} = \text{"[H9] [[col:yellow]]"} + \text{shape("أصفر")} + \text{"[[/col]] "} + \text{shape("نص")} + \text{" %s"}$$
- Validates CA color tags and variable tokens inside the description box.

---

### 3.1 Codepoint Collision Audit & Isolation to Unicode Private Use Area (PUA)

Prior to rebuild, a systematic collision audit evaluated every probe codepoint against the real Arabic Presentation Forms-B block (`U+FE70`–`U+FEFF`) and the shaped outputs of `shape()` across all Round 2 UI override strings:

| Probe Identifier | Legacy Codepoint | Unicode Name | In Arabic Block? | Collision with Real Loc Text? | Trivial Pass Risk? | Migrated PUA Codepoint |
|---|---|---|---|---|---|---|
| `CP_CHUNK_MISR` | `U+FE80` | ARABIC LETTER HAMZA ISOLATED FORM | Yes (`FE70..FEFF`) | **COLLISION:** Used in `[B1]`/`[B2]` ("بدء") | **YES** | **`U+E000`** |
| `CP_BLEED_REH` | `U+FE81` | ARABIC LETTER ALEF WITH MADDA ABOVE ISOLATED FORM | Yes (`FE70..FEFF`) | None | No | **`U+E001`** |
| `CP_BLEED_SAD` | `U+FE82` | ARABIC LETTER ALEF WITH MADDA ABOVE FINAL FORM | Yes (`FE70..FEFF`) | None | No | **`U+E002`** |
| `CP_BLEED_MEEM` | `U+FE83` | ARABIC LETTER ALEF WITH HAMZA ABOVE ISOLATED FORM | Yes (`FE70..FEFF`) | **COLLISION:** Used in `[H9]` ("أصفر") | **YES** | **`U+E003`** |
| `CP_KERN_A` | `U+FE84` | ARABIC LETTER ALEF WITH HAMZA ABOVE FINAL FORM | Yes (`FE70..FEFF`) | None | No | **`U+E004`** |
| `CP_KERN_B` | `U+FE85` | ARABIC LETTER WAW WITH HAMZA ABOVE ISOLATED FORM | Yes (`FE70..FEFF`) | None | No | **`U+E005`** |
| `CP_BLANK_40` | `U+FE86` | ARABIC LETTER WAW WITH HAMZA ABOVE FINAL FORM | Yes (`FE70..FEFF`) | **COLLISION:** Used in `[T1]..[T3]` ("مؤشر") | **YES** | **`U+E006`** |
| `CP_INK_SOLID` | `U+FE7D` | ARABIC SHADDA MEDIAL FORM | Yes (`FE70..FEFF`) | None | No | **`U+E007`** |
| `CP_INK_GRAY` | `U+FE7E` | ARABIC SUKUN ISOLATED FORM | Yes (`FE70..FEFF`) | None | No | **`U+E008`** |
| `CP_DEEP_YEH` | `U+FEFC` | ARABIC LIGATURE LAM WITH ALEF FINAL FORM | Yes (`FE70..FEFF`) | **COLLISION:** Used in `[D1]` ("للاعبين") | **YES** | **`U+E009`** |
| `CP_TALL_ALEF` | `U+FEFD` | UNKNOWN / UNASSIGNED IN FORMS-B | Yes (`FE70..FEFF`) | None | No | **`U+E00A`** |

#### Build Assertion Vulnerability & Remediation
- **Trivial Pass Mechanism:** A global check `assert chr(cp) in "".join(overrides.values())` would pass trivially for `U+FE80`, `U+FE83`, `U+FE86`, and `U+FEFC` because those codepoints are present in standard Arabic words ("بدء", "أصفر", "مؤشر", "للاعبين") even if omitted from the probe description line. Furthermore, overriding those codepoints in the CUF table corrupted real words (e.g. rendering a 40px blank space in "مؤشر" or replacing Hamza with "مصر" in "بدء").
- **Remediation:**
  1. All 11 probe glyphs are moved into the **Unicode Private Use Area** (`U+E000`–`U+E00A`), outside any standard Unicode block.
  2. All standard Arabic Presentation Forms-B (`U+FE70`–`U+FEFF`) remain strictly mapped to their authentic, plain font glyphs.
  3. The build assertion is tightened: each probe codepoint is asserted to exist **specifically within its designated probe line** (`line_h3`, `line_h4`, `line_h5`, `line_h6`, `line_h7b`, `line_h7c`), and asserted to be **completely absent from all non-probe override keys**.

---

## 4. Quantitative Predictions & Pass/Fail Criteria

### 4.1 H3 Seam Width Prediction ("Bleed" Experiment)
- **(a) Plain Forms-B:** Predicted seam = **$1.0\text{ px}$ gap** (due to $\text{pitch} = w + 1$).
- **(b) Bleed Forms-B:**
  - If engine advances strictly by $\text{pitch} = w' + 1 = w + 2$, seam remains **$1.0\text{ px}$**.
  - If engine overlaps the widened ink column, seam drops to **$0.0\text{ px}$**.
  - **Prediction:** Tested directly on screen against (a) and (c).
- **(c) Pre-rendered Chunk:** Predicted seam = **$0.0\text{ px}$** (continuous rasterized stroke).

### 4.2 H7 Space Advance Predictions
- **Line 5 (Leading spaces):**
  - If trimmed: $X_{\text{start}} = X_{\text{margin}}$.
  - If preserved: $X_{\text{start}} = X_{\text{margin}} + 8 \times 6 = X_{\text{margin}} + 48\text{ px}$.
- **Line 6 (Leading 40px blank):** Expected advance = **$41\text{ px}$** ($40 + 1$).
- **Line 7 (Inline 40px blank):** Expected gap between words = **$41\text{ px}$**.

---

## 5. CUF Font Family and Size Mapping (Evidence from On-Screen Latin)

All font inferences are derived strictly by comparing measured on-screen Latin glyph cap heights with vanilla CUF metrics in `local_en.copy.pack`:

| UI Surface | On-Screen Latin Cap Height | Vanilla CUF Metric Match | Inferred Font & Size | Status |
|---|---|---|---|---|
| **Faction Description Box** | $11\text{ px}$ (measured from Latin labels in same panel) | `la_gioconda_12.cuf` ($H$ cap = $11\text{ px}$, baseline = 15) | `la_gioconda_12.cuf` (12pt) | **INFERENCE** |
| **Faction Selection Header** | $15\text{–}16\text{ px}$ (measured from on-screen "FACTIONS") | `la_gioconda_uppercase_18.cuf` ($H$ cap = $16\text{ px}$, baseline = 22) | `la_gioconda_uppercase_18.cuf` (18pt) | **INFERENCE** |
| **Start Campaign Button** | Not measured on isolated Latin | Uppercase button style (typically 18–22pt) | `la_gioconda_uppercase_20.cuf` | **UNVERIFIED** |
| **Difficulty Tooltip** | Not measured on isolated Latin | Standard tooltip style (typically 10–12pt) | `la_gioconda_10.cuf` / `12.cuf` | **UNVERIFIED** |
| **Difficulty Level Label** | Not measured on isolated Latin | Slider sub-header (typically 12–14pt) | `la_gioconda_14.cuf` | **UNVERIFIED** |
| **Cultural Trait Header** | Not measured on isolated Latin | Small section header | `la_gioconda_uppercase_14.cuf` | **UNVERIFIED** |

---

## 6. Merged Font Vertical Extents & Faction Title [FT] Prediction

### 6.1 Font Metric Audit (All 27 Merged Font Sizes)

Every merged CUF font was evaluated for:
- `line_height` ($lh$) and `baseline` ($base$).
- Cell height / bitmap height: `v_size` ($cell$).
- Latin ascender top ('l', 'd') and descender bottom ('g', 'p') ink extents relative to cell top (row 0).
- Standard Arabic glyphs' tallest top ($ah$) and lowest bottom ($ah + h$).
- All Arabic glyphs (including probes, e.g. `CP_DEEP_YEH` with $ah = -3$).

| Font Family & Size | Line Height | Baseline | Cell Height (`v_size`) | Latin Extents [`asc`..`desc`] | Std Arabic Extents [`top`..`bot`] | All Arabic [`top`..`bot`] | Exceeds Latin Extents? | Exceeds Font Cell? |
|---|---|---|---|---|---|---|---|---|
| `la_gioconda_uppercase_18` | 18 | 22 | 28 | [10..21] | [5..30] | [-3..30] | **YES:** Top ($5 < 10$), Bot ($30 > 21$) | **YES:** Bot ($30 > 28$) |
| `la_gioconda_uppercase_20` | 20 | 25 | 31 | [12..24] | [6..35] | [-3..35] | **YES:** Top ($6 < 12$), Bot ($35 > 24$) | **YES:** Bot ($35 > 31$) |
| `la_gioconda_uppercase_22` | 22 | 27 | 34 | [13..26] | [6..38] | [-3..38] | **YES:** Top ($6 < 13$), Bot ($38 > 26$) | **YES:** Bot ($38 > 34$) |
| `la_gioconda_uppercase_24` | 24 | 29 | 37 | [14..28] | [6..41] | [-3..41] | **YES:** Top ($6 < 14$), Bot ($41 > 28$) | **YES:** Bot ($41 > 37$) |
| `la_gioconda_uppercase_26` | 26 | 32 | 40 | [15..31] | [7..45] | [-3..45] | **YES:** Top ($7 < 15$), Bot ($45 > 31$) | **YES:** Bot ($45 > 40$) |
| `la_gioconda_uppercase_28` | 28 | 34 | 43 | [16..33] | [8..48] | [-3..48] | **YES:** Top ($8 < 16$), Bot ($48 > 33$) | **YES:** Bot ($48 > 43$) |
| `la_gioconda_uppercase_30` | 30 | 37 | 46 | [18..36] | [9..52] | [-3..52] | **YES:** Top ($9 < 18$), Bot ($52 > 36$) | **YES:** Bot ($52 > 46$) |
| `la_gioconda_uppercase_32` | 32 | 39 | 49 | [18..38] | [9..55] | [-3..55] | **YES:** Top ($9 < 18$), Bot ($55 > 38$) | **YES:** Bot ($55 > 49$) |
| `la_gioconda_uppercase_38` | 38 | 47 | 59 | [22..46] | [15..64] | [-3..64] | **YES:** Top ($15 < 22$), Bot ($64 > 46$) | **YES:** Bot ($64 > 59$) |
| `la_gioconda_10` | 10 | 12 | 15 | [3..14] | [2..16] | [-3..16] | **YES:** Top ($2 < 3$), Bot ($16 > 14$) | **YES:** Bot ($16 > 15$) |
| `la_gioconda_12` | 12 | 15 | 19 | [3..18] | [3..20] | [-3..20] | **YES:** Bot ($20 > 18$) | **YES:** Bot ($20 > 19$) |
| `la_gioconda_14` | 14 | 17 | 22 | [3..21] | [3..24] | [-3..24] | **YES:** Bot ($24 > 21$) | **YES:** Bot ($24 > 22$) |
| `la_gioconda_16` | 16 | 19 | 24 | [4..23] | [4..26] | [-3..26] | **YES:** Bot ($26 > 23$) | **YES:** Bot ($26 > 24$) |
| `la_gioconda_18` | 18 | 22 | 28 | [4..27] | [5..30] | [-3..30] | **YES:** Bot ($30 > 27$) | **YES:** Bot ($30 > 28$) |
| `la_gioconda_20` | 20 | 25 | 32 | [5..30] | [6..35] | [-3..35] | **YES:** Bot ($35 > 30$) | **YES:** Bot ($35 > 32$) |
| `la_gioconda_22` | 22 | 27 | 34 | [6..33] | [6..38] | [-3..38] | **YES:** Bot ($38 > 33$) | **YES:** Bot ($38 > 34$) |
| `la_gioconda_24` | 24 | 29 | 37 | [6..36] | [6..41] | [-3..41] | **YES:** Bot ($41 > 36$) | **YES:** Bot ($41 > 37$) |
| `la_gioconda_26` | 26 | 32 | 41 | [6..39] | [7..45] | [-3..45] | **YES:** Bot ($45 > 39$) | **YES:** Bot ($45 > 41$) |
| `la_gioconda_28` | 28 | 34 | 43 | [7..42] | [8..48] | [-3..48] | **YES:** Bot ($48 > 42$) | **YES:** Bot ($48 > 43$) |
| `la_gioconda_30` | 30 | 37 | 47 | [8..46] | [9..52] | [-3..52] | **YES:** Bot ($52 > 46$) | **YES:** Bot ($52 > 47$) |
| `la_gioconda_32` | 32 | 39 | 50 | [8..48] | [9..55] | [-3..55] | **YES:** Bot ($55 > 48$) | **YES:** Bot ($55 > 50$) |
| `la_gioconda_38` | 38 | 47 | 60 | [10..58] | [15..64] | [-3..64] | **YES:** Bot ($64 > 58$) | **YES:** Bot ($64 > 60$) |
| `georgia_italic_10` | 10 | 13 | 16 | [2..15] | [2..18] | [-3..18] | **YES:** Bot ($18 > 15$) | **YES:** Bot ($18 > 16$) |
| `georgia_italic_12` | 12 | 15 | 18 | [3..17] | [3..20] | [-3..20] | **YES:** Bot ($20 > 17$) | **YES:** Bot ($20 > 18$) |
| `georgia_italic_14` | 14 | 19 | 23 | [5..22] | [5..26] | [-3..26] | **YES:** Bot ($26 > 22$) | **YES:** Bot ($26 > 23$) |
| `georgia_italic_16` | 16 | 20 | 25 | [4..24] | [4..28] | [-3..28] | **YES:** Bot ($28 > 24$) | **YES:** Bot ($28 > 25$) |
| `georgia_italic_18` | 18 | 23 | 29 | [5..27] | [5..32] | [-3..32] | **YES:** Bot ($32 > 27$) | **YES:** Bot ($32 > 29$) |

### 6.2 Key Extent Findings
1. **Descender / Bottom Overflow:** Across **all 27 merged font sizes**, standard Arabic glyphs extend $2\text{–}6\text{ px}$ below the lowest Latin descender ('g', 'p', 'y') and $1\text{–}5\text{ px}$ below the font cell bitmap boundary (`v_size`).
2. **Ascender / Top Placement in Uppercase Fonts:** Across all 9 sizes of `la_gioconda_uppercase`, standard Arabic glyphs reach significantly higher towards row 0 ($top = 5\text{–}15\text{ px}$) than Latin uppercase caps ($asc = 10\text{–}22\text{ px}$), protruding $5\text{–}8\text{ px}$ higher than Latin glyphs.
3. **Probe Glyph Boundary Exceedance:** In all fonts, `CP_DEEP_YEH` ($ah = -3$) reaches 3 pixels above the top cell boundary ($top = -3 < 0$).

### 6.3 Testable Prediction for Faction Title `[FT]` (`factions_screen_name_att_fact_eastern_roman_empire`)
- **Observed in Round 1:** The title text was clipped flat at Full $Y = 525$, with only the bottom $5\text{–}6\text{ px}$ of letters visible above the divider frame ($Y = 532$).
- **Competing Predictions for Round 2:**
  - **Hypothesis A (UI Scissor Clip):** If clipping is enforced by the UI component's fixed bounding box (`tx_faction_name` has a fixed height of $\sim 10\text{–}15\text{ px}$), the text will display the marker `[FT]` at the left, but `[FT]` and the Arabic letters will STILL have their upper halves clipped at Full $Y = 525$.
  - **Hypothesis B (Font Vertical Extent / Placement Clipping):** If clipping is caused by the font cell boundary or glyph placement, the Latin marker `[FT]` (which uses vanilla Latin glyphs with normal $ah$) will render **completely intact**, while the Arabic glyphs immediately adjacent to it will be clipped at the top.
- **Verification Criterion:**
  In Round 2 capture:
  - If `[FT]` is clipped flat at $Y = 525$ along with the Arabic letters $\rightarrow$ **CONFIRMED UI SCISSOR CLIP**.
  - If `[FT]` Latin letters 'F' and 'T' are fully visible while Arabic ascenders are clipped $\rightarrow$ **CONFIRMED GLYPH TOP / PLACEMENT OVERFLOW**.
