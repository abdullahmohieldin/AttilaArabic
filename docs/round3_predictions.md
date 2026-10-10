# Phase 1 — Round 3 Predictions & Real-Text Acceptance Specification

**Document Version:** 3.0  
**Phase:** 1 (Clean-Slate Rendering Proof)  
**Round:** 3 (Real-Text Acceptance Round)  
**Date:** 2026-10-10  
**Status:** DRAFTED PRIOR TO REBUILD (Pre-Commitment)

---

## 1. Executive Summary & Ground-Truth Baseline

Rounds 1 and 2 established five verified rendering laws for Total War: ATTILA (Warscape engine):
1. **Direction (VERIFIED):** Warscape renders text strictly Left-to-Right without internal Bidi reversal. Arabic text must be reshaped into Presentation Forms-B and reversed visually.
2. **Advance Width (VERIFIED):** Glyphs advance strictly by $\text{pitch} = w + 1\text{ px}$. Declared advance width $aw$ is completely ignored.
3. **Vertical Placement & Quad Semantics (VERIFIED):**
   - The engine positions the glyph quad top at $Y_{\text{top}} = Y_{\text{baseline}} - ah$.
   - In all 38 vanilla CUF fonts, visible glyphs have full-cell height $h = v\_size$ and $ah = v\_size$.
   - Round 2 proved that when $ah$ was computed as $baseline\_H - (ih - y\_offset)$, the quad was placed only $4\text{–}5\text{ px}$ above baseline instead of $15\text{–}16\text{ px}$, causing the entire Arabic line to drop by $+10\text{ to }+12\text{ px}$.
   - Scissor-clip on `[FT]` was refuted; Latin `[FT]` is intact while Arabic was displaced downwards.
4. **Joining Seams (VERIFIED):** Widening connecting glyphs by $+1\text{ px}$ ink bleed on the right edge completely closes the $1\text{ px}$ advance gap, producing seamless $0.0\text{ px}$ joins.
5. **Right-Alignment (VERIFIED):** Leading plain spaces (`0x20`) are stripped by the engine. Blank spacer glyphs in the Private Use Area advance by $w + 1$ without trimming and can right-align text.

Round 3 removes all synthetic probe rows and delivers **real, human-readable Arabic text** across ~10 verified live surfaces.

---

## 2. Target Surfaces & Localisation Overrides

Every target key uses real Arabic translations. Each surface retains a small, discreet 1-letter disambiguation prefix (e.g. `[T]`, `[C]`, `[B]`) to provide undeniable proof that our pack overrides are live in game:

| Surface Role | Localisation File | Database Key | Marker | Arabic Text | English Meaning |
|---|---|---|---|---|---|
| **Faction Screen Title** | `factions.loc` | `factions_screen_name_att_fact_eastern_roman_empire` | `[T]` | `الإمبراطورية الرومانية الشرقية` | Eastern Roman Empire |
| **Cultural Trait Header** | `uied_component_texts.loc` | `uied_component_texts_localised_string_header_cultural_NewState_Text_5e0000` | `[C]` | `السمة الثقافية` | Cultural Trait |
| **Start Campaign Button** | `campaign_localised_strings.loc` | `campaign_localised_strings_string_start_campaign` | `[B]` | `بدء الحملة` | Start Campaign |
| **Factions Tab Header** | `uied_component_texts.loc` | `uied_component_texts_localised_string_selection_txt_NewState_Text_90022` | `[F]` | `الفصائل` | Factions |
| **Difficulty Level Label** | `random_localisation_strings.loc` | `random_localisation_strings_string_difficulty_level_3` | `[H]` | `صعب` | Hard |
| **Difficulty Description** | `random_localisation_strings.loc` | `random_localisation_strings_string_campaign_difficulty_description_2` | `[D]` | `للاعبين المتمرسين في توتال وور.` | For players familiar with Total War. |
| **Difficulty Slider Tooltip** | `uied_component_texts.loc` | `uied_component_texts_localised_string_cmp_diff_slider_Tooltip_7000b` | `[S]` | `مؤشر الصعوبة` | Difficulty Slider |
| **Legendary Difficulty Body** | `random_localisation_strings.loc` | `random_localisation_strings_string_campaign_difficulty_slider_legendary` | `[L]` | `الحفظ اليدوي غير متاح في الحملة. لا يمكن إصدار الأوامر أثناء إيقاف المعركة مؤقتاً.` | Manual saves not allowed. Orders cannot be issued when paused. |
| **Faction Description Box** | `start_pos_factions.loc` | `start_pos_factions_description_2120156326` | — | Multi-line narrative (9 right-aligned lines) | Historical narrative of ERE |
| **Faction Long Description** | `start_pos_factions.loc` | `start_pos_factions_long_description_2120156326` | — | Multi-line narrative (9 right-aligned lines) | Identical historical narrative |

---

## 3. Description Box Narrative & Right-Alignment Specification

### 3.1 Historical Narrative Text
The Eastern Roman Empire description in 395 AD is translated into 9 concise sentences, formatted to stay strictly within the visible panel width ($\le 310\text{ px}$ text width vs $335\text{ px}$ safe panel width):

1. **Line 1:** `أطلق تقسيم الإمبراطورية الرومانية عنان الشرق،` (Text width: $279\text{ px}$, Indent: $46\text{ px}$)
2. **Line 2:** `مما مكنه من بسط نفوذه على العالم القديم.` (Text width: $285\text{ px}$, Indent: $40\text{ px}$)
3. **Line 3:** `أتاح المركز الإداري الجديد في القسطنطينية` (Text width: $305\text{ px}$, Indent: $20\text{ px}$)
4. **Line 4:** `استبدال النظم العتيقة وملء خزائن الدولة بالأموال.` (Text width: $305\text{ px}$, Indent: $20\text{ px}$)
5. **Line 5:** `نجح الشرق في تحويل مسار هجرات البرابرة نحو الغرب،` (Text width: $278\text{ px}$, Indent: $47\text{ px}$)
6. **Line 6:** `لكن الإمبراطور الشاب أركاديوس سيواجه تحديات جسيمة،` (Text width: $290\text{ px}$, Indent: $35\text{ px}$)
7. **Line 7:** `بين مؤامرات البلاط وخطر الساسانيين المستمر،` (Text width: $292\text{ px}$, Indent: $33\text{ px}$)
8. **Line 8:** `لضمان بقاء شعلة روما الأخيرة متقدة.` (Text width: $275\text{ px}$, Indent: $50\text{ px}$)

### 3.2 Binary Blank Spacer Glyphs
To push each line to the exact right margin ($325\text{ px}$), the following blank glyphs are allocated in the Unicode Private Use Area:
- `U+E010`: $w = 31 \implies \text{advance } 32\text{ px}$
- `U+E011`: $w = 15 \implies \text{advance } 16\text{ px}$
- `U+E012`: $w = 7 \implies \text{advance } 8\text{ px}$
- `U+E013`: $w = 3 \implies \text{advance } 4\text{ px}$
- `U+E014`: $w = 1 \implies \text{advance } 2\text{ px}$
- `U+E015`: $w = 0 \implies \text{advance } 1\text{ px}$

Each line is prefixed with the exact combination of binary blank spacers matching its required indentation.

---

## 4. Technical Engine Fixes

### 4.1 Vertical Baseline Alignment (100% Vanilla Parity)
- Every Arabic glyph bitmap is padded vertically to the font's full cell height:
  $$h = v\_size, \quad ah = v\_size$$
- The FreeType rasterized Arabic glyph is positioned inside the $v\_size$-tall bitmap so that its FreeType baseline aligns exactly on row `baseline_H`.
- **Predicted In-Game Metric:**
  $$\Delta Y = \text{Baseline}_{\text{Arabic}} - \text{Baseline}_{\text{Latin}} = \mathbf{0\text{ px}} \quad (\text{Tolerance: } \pm 1\text{ px})$$

### 4.2 Universal Connecting Bleed
- Every Arabic glyph with ink touching the right edge has its rightmost column duplicated ($+1\text{ px}$ width).
- **Predicted In-Game Metric:**
  $$\text{Inter-glyph Seam} = \mathbf{0\text{ px}} \quad (\text{Tolerance: } \le 1\text{ px})$$

---

## 5. Numeric Pass/Fail Acceptance Criteria

| Criterion | Target Metric | Fail Threshold | Verification Method |
|---|---|---|---|
| **Baseline Alignment** | $\Delta Y = 0\text{ px}$ | $|\Delta Y| > 1\text{ px}$ | Measured on 4x crops of `[T]`, `[C]`, `[B]`, `[F]`, `[H]`, `[D]` |
| **Joining Seams** | $0.0\text{ px}$ seam | Seam $> 1.0\text{ px}$ | Measured on connected letters across all words |
| **Clipping** | $0$ clipped glyphs | Any clipped glyph | Visual & 4x measurement of top and bottom margins |
| **Right-Alignment** | Lines aligned flush right within $\pm 3\text{ px}$ | Indent drift $> 8\text{ px}$ | Rightmost ink column measurement per line in description box |
| **Readability** | 100% shaped Arabic, natural right-to-left visual flow | Disconnected letters or left-aligned drift | Native reader visual evaluation |
