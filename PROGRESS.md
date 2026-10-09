# Total War: ATTILA Arabic Localization — Progress Tracker

## Status: Phase 1 Round 2 Build in Progress (Predictions Documented & Committed)

---

## 1. Actual Results & Ground Truth Ledger

### Environment & Safety Integrity
- **Game folder:** `D:\SteamLibrary\steamapps\common\Total War Attila` (READ-ONLY verified).
- **Vanilla `local_en.pack` SHA-256:** `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` (byte-identical before and after build).
- **`Attila.exe` SHA-256:** `51B833D5B8FD8505A7CD035FD92F68CACE681D62EA74D9AD8FBAE26326635BF5` (byte-identical).
- **Deployment Audit (A3):** Verified `data\` contains zero third-party mods, and `used_mods.txt` lists only our two packs in correct priority.

---

### Round 1 Screen Measurements & Hypotheses Evaluation

1. **H1 Direction:** **VERIFIED**. Rulers 1 & 2 confirm Warscape draws text strictly Left-to-Right without internal Bidi reversal.
2. **H2 Pitch:** **VERIFIED**. Pitch sweep proves Warscape advances CUF glyphs strictly by:
   $$\text{pitch} = w + 1\text{ px}$$
   The `aw` field in the glyph table is completely ignored.
3. **H3 Joining Seams:** **VERIFIED**. Individually rasterized Forms-B glyphs suffer an intrinsic $1\text{ px}$ baseline gap due to $\text{pitch} = w + 1$. Pre-rendered multi-letter chunks join with $0\text{ px}$ gap.
4. **H4 Kerning:** **UNVERIFIED (Omitted in R1)**. Probes were assigned in CUF table but omitted from description text in Round 1.
5. **H5 Ink Thresholding & Grayscale:** **VERIFIED (Visual)**. Gray Yeh rendered with intermediate alpha (mean lum $\sim 82$), disproving the Gate 0 assumption that the engine only draws solid 255. Engine performs alpha blending, but saturated/binary ink provides substantially crisper contrast on parchment textures. Gate 0 claim re-labeled as **INFERENCE**.
6. **H6 Vertical Bounds:** **VERIFIED**. Tall Alef ($+3\text{ px}$) rendered with $10\text{ px}$ height completely intact with clear space above and below. Line spacing accommodates taller glyphs without line-level clipping.
7. **H7 Right Alignment:** **INCONCLUSIVE**. Round 1 NBSP had $w=0$, advancing by only $0+1=1\text{ px}$ per character, confounding alignment testing.
8. **H8 Line Order & Wrapping:** **VERIFIED**. Hard breaks (`\n`) render sequentially top-to-bottom. Unwrapped long lines break across visual lines without re-applying Bidi, causing words to appear reversed across lines. Box overflow (H8c) is **UNVERIFIED** because box was captured mid-scroll.
9. **Faction Title Clipping:** **INFERENCE**. Arabic title line above leader at Full $Y = 525\text{ to } 530\text{ px}$ is cut flat across all $290\text{ px}$ of width at $Y = 525$. Proven to be a hard scissor clip by the UI layout component's bounding box (`clip_to_bounds` on `tx_faction_name`).

---

## 2. Round 2 Scope & Plan

- **Single Screen Coverage:** All 16 target keys are on the Faction Selection screen.
- **Disambiguation Markers:** Every duplicate key has a distinct prefix (`[B1]`–`[B2]`, `[F1]`–`[F3]`, `[T1]`–`[T3]`, `[H1]`–`[H3]`, `[D1]`, `[C1]`, `[FT]`).
- **Compact Non-Scrolling Description Box:** 8 compact lines ($< 150\text{ px}$ height, well within the $185\text{ px}$ / 10-line visible capacity measured in `Phase1_R1_01`).
- **Patched Probes:**
  - **H3 Bleed:** Word "مصر" tested across (a) Plain Forms-B, (b) Bleed Forms-B (+1px right ink column), (c) Pre-rendered Chunk.
  - **H4 Kerning:** Injected test pair in description box.
  - **H5 Ink & Diacritics:** Solid vs Gray Yeh + Shaddah / Kasrah diacritics.
  - **H6 Vertical Bounds:** Tall Alef (+3px) + Deep Yeh (-3px).
  - **H7 Space Advances:**
    - Line 5: 8 leading plain spaces (`0x20`)
    - Line 6: Leading $40\text{ px}$ blank glyph (`CP_BLANK_40 = 0xFE86`, expected advance $41\text{ px}$)
    - Line 7: Inline $40\text{ px}$ blank glyph between marker words (expected gap $41\text{ px}$)
  - **H9 Formatting Tags:** `[[col:yellow]]` color markup and `%s` placeholder test.
- **Build Assertion:** Build script strictly asserts that 100% of probe codepoints defined in the font pack appear in at least one loc string.

---

## 3. Next Steps

1. Commit documentation updates to git (`docs/round2_predictions.md`, `PROGRESS.md`).
2. Build Round 2 packs (`Attila_Arabic_Phase1.pack`, `Attila_Arabic_Phase1_fonts.pack`).
3. Run test suite `tests/test_phase1_packs.py` and print SHA-256 hashes.
4. Stop and wait for user's explicit command to execute procedure A2.
