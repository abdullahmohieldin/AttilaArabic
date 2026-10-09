# Phase 1 — Round 2 Predictions & Experiment Specification

**Document Version:** 2.0  
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
  - **Verdict on Cut:** This is a **hard scissor clip by the UI layout component's bounding box** (the `clip_to_bounds` scissor rect of `tx_faction_name`). The UI layout frame top boundary is at Full $Y = 525$.
  - The upper $\sim 12\text{–}18\text{ px}$ of the ascenders are discarded by the GPU scissor test because the UI element bounding box is too short for Tajawal Arabic ascenders at this size. Only the bottom $5\text{–}6\text{ px}$ (baseline connection and lower loops) fall inside the scissor window.
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

To guarantee 100% of probe lines remain visible simultaneously without scrolling, the H8 long narrative lines and legacy rulers are omitted. The suite contains exactly **8 compact lines**:

### Line 1: H3 Joining & Bleed Comparison (Word "مصر")
$$\text{Line 1} = \text{"[H3] "} + \text{Plain Forms-B} + \text{"   "} + \text{Bleed Forms-B} + \text{"   "} + \text{Pre-rendered Chunk}$$
- **Plain Forms-B:** `U+FEAE` (Reh) + `U+FEBC` (Sad medial) + `U+FEE3` (Meem initial). Tight bounding box.
- **Bleed Forms-B:** `CP_BLEED_REH` (0xFE81) + `CP_BLEED_SAD` (0xFE82) + `CP_BLEED_MEEM` (0xFE83). Widened by 1 ink column on connecting side.
- **Pre-rendered Chunk:** `CP_CHUNK_MISR` (0xFE80). Single 3-letter pre-rasterized glyph.

### Line 2: H4 Kerning Delta Probe
$$\text{Line 2} = \text{"[H4] "} + (\text{CP\_KERN\_A} + \text{CP\_KERN\_B}) + \text{"   "} + (\text{CP\_KERN\_A} + \text{CP\_KERN\_B})$$
- Uses codepoints `0xFE84` and `0xFE85`.

### Line 3: H5 Ink Thresholding & Diacritics
$$\text{Line 3} = \text{"[H5] "} + (\text{Solid Yeh} \times 4) + \text{" "} + (\text{Gray Yeh} \times 4) + \text{" "} + \text{shape("شَدَّة كَسْرَة")}$$
- Uses `0xFE7D` (Solid) and `0xFE7E` (Gray), plus real Arabic Shaddah and Kasrah diacritics.

### Line 4: H6 Vertical Boundary Probes
$$\text{Line 4} = \text{"[H6] "} + (\text{Tall Alef } +3\text{px} \times 4) + \text{" "} + (\text{Deep Descender Yeh } -3\text{px} \times 4)$$
- Uses `CP_TALL_ALEF` (0xFEFD) and `CP_DEEP_YEH` (0xFEFC).

### Line 5: H7a Leading Plain Spaces Test
$$\text{Line 5} = \text{"        [H7A] "} + \text{shape("مسافات")}$$
- Starts with **8 plain spaces** (`0x20`). Tests whether the engine strips leading whitespace or advances by $8 \times (w_{\text{space}} + 1)$.

### Line 6: H7b Leading Blank 40px Glyph Test
$$\text{Line 6} = \text{CP\_BLANK\_40} + \text{"[H7B] "} + \text{shape("فراغ")}$$
- Starts with one blank glyph of width $w = 40\text{ px}$ (`CP_BLANK_40` = 0xFE86, empty bitmap). Expected advance = $40 + 1 = \mathbf{41\text{ px}}$.

### Line 7: H7c Inline Blank 40px Glyph Test
$$\text{Line 7} = \text{"[H7C] "} + \text{shape("بداية")} + \text{CP\_BLANK\_40} + \text{shape("نهاية")}$$
- Places the $40\text{ px}$ blank glyph mid-line between two words to directly measure inline advance without leading-whitespace trimming interference.

### Line 8: H9 UI Formatting Tags & Placeholders
$$\text{Line 8} = \text{"[H9] [[col:yellow]]"} + \text{shape("أصفر")} + \text{"[[/col]] "} + \text{shape("نص")} + \text{" %s"}$$
- Validates CA color tags and variable tokens inside the description box.

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
