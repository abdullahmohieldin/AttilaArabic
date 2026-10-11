# Total War: Attila - Part 1 In-Game Verification Checklist

This checklist defines the visual and functional acceptance criteria for **Part 1 (Pre-Campaign & Faction Selection)** of the Arabic localization fan mod.

---

## 1. Main Menu & Navigation
Verify that top-level UI components are localized and fit neatly within button boundaries:
- [ ] **Grand Campaign Button:** Localized as `الحملة الكبرى`. Text is centered, not clipped.
- [ ] **Custom Battle / Historical Battles:** Labels are legible in Arabic.
- [ ] **Options / Exit Game:** Standard UI control buttons correctly styled.
- [ ] **Campaign Select Screen:** Campaign titles (`الحملة الكبرى`, `آخر الرومان`, `عصر شارلمان`) correctly rendered.

---

## 2. Faction Selection Screen - Layout & Typography Tests

### A. Faction Leader & Religion Layout (Gate G2 Fix Verification)
Navigate to the Faction Selection screen and inspect the top-right header block:
- [ ] **Faction Leader Label & Name:**
  - Label `قائد الفصيل:` has the colon positioned logically on the left (in visual RTL reading order).
  - Leader name (e.g. `الإمبراطور فلافيوس أركاديوس`) is positioned clearly to the left of the label.
  - No text overlap between label and name.
- [ ] **Religion Icon & Label:**
  - Religion icon is positioned to the right of the religion label (`المسيحية الأرثوذكسية`, `المسيحية الخلقيدونية`, `الوثنية الجرمانية`, etc.).
  - The religion icon **does NOT** sit between the leader name and leader label.
- [ ] **Difficulty Slider:**
  - Difficulty labels (`سهل`, `متوسط`, `صعب`, `صعب جداً`, `أسطوري`) display cleanly.

---

## 3. Cultural Group & Faction Coverage

Test each of the following playable factions across different cultural categories:

### Group 1: The Roman Empire (الإمبراطورية الرومانية)
- [ ] **Eastern Roman Empire (الإمبراطورية الرومانية الشرقية):**
  - Leader: `الإمبراطور فلافيوس أركاديوس`
  - Cultural Trait: `الإرث الإمبراطوري`
  - Faction Trait: `خزينة القسطنطينية`
  - Starting position summary and description are properly formatted.
- [ ] **Western Roman Empire (الإمبراطورية الرومانية الغربية):**
  - Leader: `الإمبراطور هونوريوس`
  - Faction traits, cultural traits, and starting difficulty (`أسطوري` / Legendary).

### Group 2: The Great Migrators (المهاجرون العظام)
- [ ] **Visigoths (القوط الغربيون):**
  - Leader: `ألاريك الأول`
  - Faction Trait: `غزاة روما`
  - Migration status bullet points correctly displayed.
- [ ] **Ostrogoths (القوط الشرقيون):**
  - Leader: `فيتيغيرن`
- [ ] **Vandals (الوندال):**
  - Leader: `غايسريك`
- [ ] **Alans (الألان):**
  - Leader: `ريسبينديك`
- [ ] **Suebi (السويبيون):**
  - Leader: `إرمينريك`

### Group 3: The Barbarian Kingdoms (الممالك البربرية)
- [ ] **Franks (الفرنجة):**
  - Leader: `فاراموند`
  - Cultural Trait: `المحاربون الشماليون`
- [ ] **Saxons (السكسون):**
  - Leader: `هادوجات`

### Group 4: The Nomadic Tribes (القبائل البدوية)
- [ ] **Huns (الهون):**
  - Leader: `أودين` / `أتيلا`
  - Unique horde mechanics and cavalry bullet points formatted cleanly.

### Group 5: Eastern Empires (إمبراطوريات الشرق)
- [ ] **Sassanid Empire (الإمبراطورية الساسانية):**
  - Leader: `شاهنشاه يزدجرد الأول`
  - Religion: `الزرادشتية`
  - Satrapy relations and silk road traits verified.

---

## 4. Multi-Line Historical Narrative Descriptions
Inspect the scrollable historical background lore on the left side of the screen:
- [ ] **Right Alignment:** Text appears aligned to the right margin of the parchment scroll.
- [ ] **Line Spacing & Blank Spacers:** Font spacers (`0xE010..0xE015`) pad lines properly without blank line jumps or overlapping ascenders/descenders.
- [ ] **Readability:** Paragraphs flow naturally from right to left without reversed words or isolated unjoined letters.

---

## 5. Visual Defect Reference Guide

| Symptom | Cause | Target Fix |
| :--- | :--- | :--- |
| **Isolated glyphs (ا ل إ م ب ر ا ط و ر)** | Text was fed as raw Unicode instead of Presentation Forms-B | Check shaping pipeline in `scripts/shape_pipeline.py` |
| **Reversed characters (ةيروطاربمإلا)** | Double BiDi reversal | Ensure logical string order in translation tables |
| **Colon on wrong side (`:قائد الفصيل`)** | BiDi flip of neutral punctuation character | Keep trailing colon attached with correct RTL marker |
| **Question marks or square boxes (`???`, `□`)** | Missing glyph in `.cuf` font | Check `out_shaped/GLYPH_COVERAGE_REPORT.md` |
| **Text cut off / clipped horizontally** | UI component box width smaller than Arabic string | Adjust UI container width or shorten phrasing |
| **Overlap with icons** | Relative coordinate offset issue | Adjust X offset in `ui/frontend ui/sp_grand_campaign` |

---

## 6. Feedback Protocol
If you identify any visual defects while following this checklist:
1. Capture a screenshot (`F12` via Steam or `Win + Shift + S`).
2. Save it into `tw_attila_ar/screenshots/`.
3. Follow the reporting format detailed in [`tw_attila_ar/ITERATIONS.md`](file:///D:/AttilaArabic/tw_attila_ar/ITERATIONS.md).
