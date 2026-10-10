# Phase 1 Predictions & Test Plan — Total War: ATTILA Arabic Localization

**Document:** `docs/phase1_predictions.md`  
**Date:** 2026-10-09  
**Status:** Pre-Test Registered Predictions (Written BEFORE Build)  
**Methodology:** Clean-slate testing. No assumptions carried from earlier branches or unverified notes.

---

## 1. Target Surfaces & Vanilla Key Inventory

Every target key is verified in vanilla `extracted/local_en.copy.pack` and extracted `.loc` files before building:

| Target Surface | Control Type | Vanilla Loc File | Target Key | Vanilla English Value |
|---|---|---|---|---|
| **Main Menu Campaign Button** | Primary Menu Button | `text\db\uied_component_texts.loc` | `uied_component_texts_localised_string_button_txt_NewState_Text_160028` | `"Campaign"` |
| **Battle Settings Button** | Settings / Options Button | `text\db\uied_component_texts.loc` | `uied_component_texts_localised_string_tx_battle_options_NewState_Text_590076` | `"Battle Settings"` |
| **Faction Select Title** | Selection / Header Title | `text\db\factions.loc` | `factions_screen_name_att_fact_eastern_roman_empire` | `"Eastern Roman Empire"` |
| **Difficulty Tooltip** | Hover Tooltip | `text\db\uied_component_texts.loc` | `uied_component_texts_localised_string_medal1_default_Tooltip_5003a` | `"Hard"` |
| **ERE Multi-line Description** | Multi-line Parchment Panel | `text\db\start_pos_factions.loc` | `start_pos_factions_description_2120156326` | `"The division of the Roman Empire has unseated its ancient pre-eminence..."` |

*Build Assertion:* The build script must parse each target file directly from `extracted/local_en.copy.pack`, assert the key exists, and halt immediately if any key is missing.

---

## 2. Target Font Inventory & Merge Rules

Vanilla UI surfaces do not reference `arialunicode_*`. They draw from `la_gioconda`, `la_gioconda_uppercase`, and `georgia_italic`.

### Fonts Merged for Phase 1:
- `georgia_italic`: sizes 10, 12, 14, 16, 18 (used for tooltips, body copy, descriptions)
- `la_gioconda`: sizes 10, 12, 14, 16, 18, 20, 22 (used for UI panels, body text, buttons)
- `la_gioconda_uppercase`: sizes 10, 12, 14, 16, 18, 20, 22 (used for menu buttons, headers, faction titles)

### Strict Merge Assertions:
1. **Existing Latin Glyphs:** Original glyph count $N$ glyph records, dimension bytes, and bitmap bytes remain **100% byte-identical**.
2. **Header Properties:** All 11 `u16` header properties (`line_height`, `baseline`, `v_size`, `h_size`, etc.) remain **byte-identical**.
3. **Kerning Matrix:** The tail kerning section remains **byte-identical**.
4. **Appended Records:** Injected Arabic glyph records and probe records are appended strictly at index $\ge N$, and only unused character table entries (or mapped Presentation Forms-B) point to them.

---

## 3. Hypotheses, Probes, Predictions & Gating Criteria

### H1: Direction (Drawn Reading Order)
- **Question:** Does the engine render stored strings strictly Left-to-Right without internal mirroring or automatic shaping?
- **Probe Design:** Asymmetric dual-block ruler lines injected into the test text:
  - Block A: Thin vertical stem (width = 5 px, declared $aw = 5$, 12 copies).
  - Block B: Broad block (width = 12 px, declared $aw = 12$, 8 copies).
  - Line 1 stores: `AAAAAAAAAAAA BBBBBBBB` (Thin run followed by Thick run).
  - Line 2 stores: `BBBBBBBB AAAAAAAAAAAA` (Thick run followed by Thin run).
- **Prediction:**
  - *If engine is strictly LTR:* Line 1 displays Thin on LEFT, Thick on RIGHT. Line 2 displays Thick on LEFT, Thin on RIGHT.
  - *If engine mirrors:* Line 1 displays Thick on LEFT, Thin on RIGHT.
- **Numeric Pass/Fail Criteria:**
  - PASS: Orientation matches strictly LTR storage order (Thin-then-Thick on Line 1).
  - FAIL: Mirroring or arbitrary reordering observed.
- **Verdict Impact:**
  - LTR confirms clean-room pre-shaping and visual bidi reordering are required and stable. (Supports GO).
  - Engine mirroring would require inverse-order authoring. (CONDITIONAL).

---

### H2: Pitch (Horizontal Advance Mechanics)
- **Question:** What controls on-screen horizontal cell pitch? Candidates: declared advance width $aw$, bitmap ink width $w$, $w + \text{constant } C$, or a fixed surface pitch $P$.
- **Probe Design:** Advance width sweep with controlled parameters (8 copies per block):
  - Probe H2a: $w = 8$, $aw = 6$ ($aw < w$).
  - Probe H2b: $w = 8$, $aw = 8$ ($aw == w$).
  - Probe H2c: $w = 8$, $aw = 10$ ($aw > w$).
  - Probe H2d (Control): $w = 6$, $aw = 8$ ($w < aw$, tests whether ink width or advance sets pitch).
- **Distinguishable Prediction Signatures (8 copies):**

| Model | Probe H2a ($w8, aw6$) | Probe H2b ($w8, aw8$) | Probe H2c ($w8, aw10$) | Probe H2d ($w6, aw8$) | Distinctive Signature |
|---|---|---|---|---|---|
| **$pitch = aw$** | 48 px | 64 px | 80 px | **64 px** | H2a (48) < H2b (64) == H2d (64) < H2c (80). Varying $aw$ changes width; varying $w$ at fixed $aw$ does not. |
| **$pitch = w$** | 64 px | 64 px | 64 px | **48 px** | H2d (48) < H2a (64) == H2b (64) == H2c (64). Varying $aw$ produces 0 px change; varying $w$ changes width. |
| **$pitch = w + C$ ($C=2$)** | 80 px | 80 px | 80 px | **64 px** | H2d (64) < H2a (80) == H2b (80) == H2c (80). H2a/b/c identical, width expands beyond $w$ by $8 \times C$. |
| **Fixed Pitch $P$** | $8P$ | $8P$ | $8P$ | **$8P$** | All four probe rows measure identical total pixel width regardless of $w$ or $aw$. |

- **Numeric Pass/Fail Criteria:**
  - PASS: Measured row widths match exactly one model signature above within $\pm 1$ px measurement tolerance.
  - Joining candidate verification: If $aw == w$ achieves exact glyph abutment without inter-cell gaps, $aw$ model is validated for production.
- **Verdict Impact:**
  - If $aw$ controls pitch: Direct mathematical control over letter spacing. (GO).
  - If $w$ or $w + C$: Requires glyph dilation/overhangs to close gaps. (CONDITIONAL).
  - If fixed pitch $P$: (CONDITIONAL / NO-GO if gap cannot be closed).

---

### H3: Joining (Forms-B Letters vs Pre-rasterized Chunk Glyphs)
- **Question:** Can individual Presentation Forms-B glyphs join seamlessly, or does cell gap require pre-composed multi-letter word/syllable chunks?
- **Probe Design:**
  - Probe H3a (Individual Forms): Standard connected Arabic words (`القاهرة`, `معركة`, `الإمبراطورية`) using individual Forms-B codepoints with $aw == w$.
  - Probe H3b (Pre-rendered Chunk): A 2-letter chunk (`ـمتـ` / `ـتر`) pre-rasterized as a single glyph assigned to an unused codepoint (e.g. `U+06FD`).
- **Prediction:**
  - H3a with $aw == w$ will produce continuous connecting baseline with seam $\le 1$ px.
  - H3b will have strictly 0 px seam internally.
- **Numeric Pass/Fail Criteria:**
  - PASS: Baseline seam across joining letters $\le 1$ px (hairline anti-aliasing only; no visible 2-4 px gaps).
  - Feasibility Limit: Injected glyph count $< 2048$, total CUF bitmap size increase $< 500$ KB per font.
- **Verdict Impact:**
  - Seam $\le 1$ px with Forms-B: Full vocabulary localization feasible without combinatorial chunk explosion. (GO).
  - Seams $> 2$ px persistent: Requires multi-letter chunking or negative spacing table. (CONDITIONAL).

---

### H4: Kerning (CUF Kerning Matrix Influence)
- **Question:** Does the engine apply the CUF kerning matrix to injected glyph codes, or does it only affect vanilla Latin codes?
- **Probe Design:**
  - Test pair: Two specific probe codes $C_1, C_2$.
  - Kerning Row A: Delta between $C_1$ and $C_2$ set to $-5$ px in the kerning matrix tail.
  - Kerning Row B: Delta set to $0$ px (control).
- **Prediction:**
  - *If kerning is active for high codes:* The distance between $C_1$ and $C_2$ in Row A is 5 px shorter than in Row B.
  - *If kerning is inactive for high codes:* Row A and Row B measure identical pixel distance.
- **Numeric Pass/Fail Criteria:**
  - PASS: Measurable $\Delta \text{distance} \approx -5$ px between pairs.
  - NEGATIVE: $0$ px change (kerning matrix ignored for extended codes).
- **Verdict Impact:**
  - Kerning active: Provides an extra fine-tuning mechanism for complex ligatures. (GO).
  - Kerning inactive: Informative negative result; all spacing must be controlled via glyph $aw$. (GO / CONDITIONAL).

---

### H5: Weight & Ink Thresholding
- **Question:** Does the engine drop faint anti-aliased pixels? Does binarized/solid-255 rasterization preserve small diacritics and dots?
- **Probe Design:**
  - Compare three rendering treatments of `ي` (two dots below) and `ش` (three dots above):
    - Treatment 1: Standard continuous grayscale anti-aliasing (alpha 20..255).
    - Treatment 2: Binarized / thresholded ink (alpha $> 80 \to 255$).
    - Treatment 3: Dilated dot cluster (+1 px solid footprint).
- **Prediction:**
  - Treatment 1 may exhibit faint or dropped dots at sizes $\le 12$ px.
  - Treatments 2 and 3 will render solid, visible dots on 1080p screen.
- **Numeric Pass/Fail Criteria:**
  - PASS: Diacritic dots (below Beh/Yeh, above Teh/Noon/Sheen) visible with $\ge 2\times 2$ solid pixels on screen.
- **Verdict Impact:**
  - Legible dots verified: (GO).
  - Dropped dots requiring manual font pathology: (CONDITIONAL).

---

### H6: Glyph Box Clipping (Vertical Clearance)
- **Question:** Do high hamzas (e.g. `أ`, `آ`) or low descenders (e.g. `ي`, `ج`, `ر`) clip against vanilla cell bounds or $v\_size$?
- **Probe Design:**
  - Probe glyphs with:
    - Normal cap height matching vanilla `'H'`.
    - Extended ascender height ($+3$ px above vanilla cap).
    - Extended descender height ($+3$ px below vanilla baseline).
- **Prediction:**
  - If glyph dimensions remain within $v\_size$, no vertical clipping occurs.
  - If glyph dimensions exceed $v\_size$, top or bottom rows clip sharply.
- **Numeric Pass/Fail Criteria:**
  - PASS: Zero row clipping on hamza above Alef and tail loop below baseline.
- **Verdict Impact:**
  - Full glyph height visible: (GO).
  - Vertical clipping observed: Requires scaling Tajawal cap down by 1-2 px to fit envelope. (CONDITIONAL).

---

### H7: Right Alignment & Whitespace
- **Question:** Can lines inside LTR-oriented text controls be right-aligned using whitespace padding, and does the engine trim leading whitespace?
- **Probe Design:**
  - In a fixed-width panel (ERE description / difficulty box):
    - Line 1: No padding (`"كلمة"`).
    - Line 2: 12 standard ASCII spaces (`"            كلمة"`).
    - Line 3: 12 Non-Breaking Spaces (`"\u00A0..."`).
    - Line 4: Explicit right-pad calculation (total width - text width).
- **Prediction:**
  - Standard ASCII spaces may be collapsed or trimmed by the layout parser.
  - Non-Breaking Spaces (`U+00A0`) will not be trimmed and will push text rightward.
- **Numeric Pass/Fail Criteria:**
  - PASS: Line with NBSP padding shifts rightward by $\ge 40$ px relative to unpadded line.
- **Verdict Impact:**
  - NBSP padding functions: Right-alignment achievable in vanilla LTR containers. (GO).
  - All whitespace trimmed: Text remains left-aligned inside LTR containers. (CONDITIONAL).

---

### H8: Line Wrapping & Break Tokens
- **Question:** How does multi-line text behave under engine auto-wrap vs hard breaks, and what is the panel capacity before vertical clipping?
- **Probe Design (Injected into ERE Description):**
  - **Case (a) Unwrapped Reordered Paragraph:** A continuous 120-character RTL sentence with no embedded newlines.
  - **Case (b) Hard-Broken Paragraph:** Three lines broken explicitly with `\n`, pre-formatted in visual top-to-bottom order.
  - **Case (c) Overflow String:** A 12th probe line at the very bottom intended to test vertical boundary capacity.
- **Predictions per Sub-Case:**
  - **Case (a) Unwrapped:** The engine will auto-wrap words when line width exceeds panel capacity (approx. 320–350 px). Because words are in visual RTL order, auto-wrapping stacks lines in reverse reading order (the logical end of the sentence appears on Line 1).
  - **Case (b) Hard-Broken:** The engine respects `\n` as an authoritative line break; lines stack top-to-bottom in correct author order (Line 1 at $y \approx 620$, Line 2 at $y \approx 638$, Line 3 at $y \approx 656$).
  - **Case (c) Overflow:** If line count exceeds the panel's vertical capacity (approx. 10 lines at 18px pitch), line 11+ will either clip against the bottom boundary or overflow into the lower frame.
- **Numeric Pass/Fail Criteria:**
  - PASS: Hard `\n` line breaks are parsed cleanly with line pitch $\approx 18\pm 2$ px; top-to-bottom reading order preserved for Case (b).
  - Auto-wrap boundary measured within $\pm 5$ px for Case (a).
  - Vertical capacity measured in exact visible line count for Case (c).
- **Verdict Impact:**
  - Pre-wrap with `\n` functions: Multi-line narrative lore text is 100% solvable via pre-wrap offline pipeline. (GO).
  - Newlines ignored: Multi-line layout blocked without engine hooks. (NO-GO).

---

### H9: Formatting Markup Tags & Variable Tokens
- **Question:** How do inline color markup tags (`[[col:yellow]]...[[/col]]`) and variable tokens (`%s`, `{n}`) interact with visual BiDi reordering?
- **Probe Design:**
  - Test String 1: Color tag surrounding Arabic word:
    - Syntactic preservation: `[[col:yellow]]` + reordered word + `[[/col]]`.
  - Test String 2: Variable token with mixed text:
    - `1200 %s روما` (testing whether `%s` is preserved verbatim without token scrambling).
- **Prediction:**
  - If tags are tokenized and protected prior to BiDi reordering, the engine parses `[[col:...]]` correctly and applies the color tint to the Arabic glyphs.
  - If tags are naively reordered, tag syntax breaks (`[[/col]]` before `[[col:...]]`) and literal tags appear as ink.
- **Numeric Pass/Fail Criteria:**
  - PASS: Color tint successfully applied to the tagged word; zero literal tag text displayed on screen; `%s` placeholder intact.
- **Verdict Impact:**
  - Tags work with protected BiDi: Complete UI styling compatibility. (GO).
  - Tags broken by engine: Markup must be stripped or refactored. (CONDITIONAL).

---

## 4. Overall Phase 1 Verdict Framework

The final report at the end of Phase 1 will issue exactly one verdict based on the screenshots:

1. **GO:**
   - H1 confirms deterministic LTR draw order.
   - H2 & H3 achieve baseline join seam $\le 1$ px with $aw == w$.
   - H5 & H6 verify legible dots without box clipping.
   - H8 confirms `\n` hard wrapping stacks top-to-bottom.
   - H9 confirms tags and formatting intact.
2. **CONDITIONAL:**
   - Core glyph rendering succeeds, but specific surfaces require targeted compensation (e.g. padding tables for right-alignment, minor cap scaling for ascender headroom, or per-surface line-width wrap calibrations).
3. **NO-GO:**
   - Unresolvable engine-level barrier (e.g. hard crashes on non-ASCII characters, fixed unalterable character pitch that splits words, or inability to display injected glyphs).
