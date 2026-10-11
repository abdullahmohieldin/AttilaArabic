# Screenshot Feedback & Visual Iteration Loop (Phase 8)

This guide documents the iteration protocol for reporting and fixing visual layout, typography, and clipping issues identified during in-game testing.

---

## 1. Quick Iteration Workflow

```mermaid
graph LR
    A[Play & Spot Defect] --> B[Capture Screenshot]
    B --> C[Save in screenshots/]
    C --> D[Notify Assistant]
    D --> E[Patch UI / Translation]
    E --> F[Rebuild Pack]
    F --> G[Test In-Game]
```

1. **Capture Screenshot:** Take an in-game screenshot (`F12` or `Win + Shift + S`) showing the defect.
2. **Save Screenshot:** Save the image to:
   ```text
   d:\AttilaArabic\tw_attila_ar\screenshots\issue_01.png
   ```
3. **Notify the Assistant:** Provide the screenshot name and describe the problem in chat (using the template below).
4. **Automated Fix & Rebuild:** The assistant inspects the UI component coordinates or translation key, applies the targeted fix, and rebuilds the pack with:
   ```powershell
   & "d:\AttilaArabic\tools\venv\Scripts\python.exe" "d:\AttilaArabic\tw_attila_ar\scripts\build_pack.py"
   ```
5. **Re-test:** Copy the updated `tw_attila_ar\out\Attila_Arabic_Part1.pack` to your game `data\` folder and verify.

---

## 2. Issue Reporting Template

When reporting visual issues, use this format for rapid resolution:

```markdown
### Visual Issue Report
- **Screenshot:** issue_01.png (in `tw_attila_ar/screenshots/`)
- **Screen:** Grand Campaign Faction Selection / Main Menu / etc.
- **Faction:** Eastern Roman Empire / Huns / etc.
- **Component:** Faction Leader Label / Trait description / Button label
- **Observed Defect:** (e.g. Text clipped on right edge / Colon appears before the label / Icon overlapping name)
- **Expected Result:** (e.g. Needs 20px more width / Colon should be on the left / Icon placed to right of text)
```

---

## 3. Common Fix Mechanisms

Depending on the nature of the reported defect, fixes are categorized into three automated paths:

### Path A: Wording & Brevity Tuning
- **When to use:** Text overflows button containers (e.g. `الهجرة الكبرى` vs `الهجرة`).
- **File modified:** `tw_attila_ar/translated/part1_logical.json` or `tw_attila_ar/batches/*.jsonl`.
- **Pipeline:** Re-run validator -> Re-shape -> Re-build pack.

### Path B: Font Spacer & Line Wrapping Tuning
- **When to use:** Multi-line narrative descriptions have irregular line padding or left-margin gaps.
- **File modified:** Narrative entry in `tw_attila_ar/scripts/shape_pipeline.py`.
- **Pipeline:** Adjust PUA spacer count (`0xE010..0xE015`) to align lines with Warscape UIC scroll boundaries.

### Path C: UIC Layout & Coordinate Adjustments
- **When to use:** Hard-coded UIC components physically collide (e.g. leader name and leader label).
- **File modified:** `tw_attila_ar/ui/frontend ui/sp_grand_campaign`.
- **Pipeline:** Adjust component X/Y position or dimensions -> Re-pack into `Attila_Arabic_Part1.pack`.
