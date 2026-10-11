# Phase 0.5 Cleanup Execution Report

**Document:** `<WORKDIR>/CLEANUP_REPORT.md`  
**Execution Timestamp:** 2026-10-10 14:45:00  
**Git Branch:** `cleanup`  
**Pre-Cleanup Baseline:** Commit `b906887` (`pre-cleanup-snapshot`), Tag `pre-cleanup-20261010_143319`  
**Quarantine Location:** `D:\AttilaArabic\tw_attila_ar\quarantine`  
**Manifest:** `D:\AttilaArabic\tw_attila_ar\quarantine\MANIFEST.tsv`  

---

## 1. Summary of Actions Taken

1. **Full Pre-Cleanup Snapshot Archive:**
   - Created `tw_attila_ar/backup/project_20261010_143319.zip` (895.74 MB).
   - Saved full git state in `tw_attila_ar/backup/git_state_20261010_143319.txt`.
   - Committed uncommitted files to `pre-cleanup-snapshot` and created permanent git tag.
2. **Quarantine Movement (Zero Deletion):**
   - Moved 94 items (approx 2.1 GB) into `<WORKDIR>/quarantine/`.
   - Scratch analysis scripts and debug crops (60 files) moved from `scratch/`.
   - Experimental calibration solvers (48 files) moved from `source/`.
   - Redundant RPFM zip (293.6 MB) and PDB debug symbols (841.7 MB) moved from `tools/`.
   - Obsolete Ruby-dependent tool moved from `tools/etwng/`.
   - Historical prototype packs (40 packs, ~670 MB) moved from `release/`.
3. **Restoration of Broken Dependencies:**
   - Initial test run identified that `tests/test_baseline_regression.py`, `tests/test_join_continuity.py`, and `tests/test_key_mapping.py` assert against files in `build/v6fonts` and `build/v6`.
   - Per the approved rule (*"if something breaks, restore it and reclassify as KEEP"*), `build/` was immediately restored and reclassified as `KEEP`.
   - Re-verified test suite: **10 passed in 4.83s**.
4. **Commits on Branch `cleanup`:**
   - `cleanup: quarantine scratch analysis scripts and temporary debug crops` (`3de9905`)
   - `cleanup: quarantine historical calibration solvers and experimental scripts from source/` (`05c6ffe`)

---

## 2. Working Tree Status After Cleanup

The working tree is now lean, focused, and verified:
- `source/`: Down to 6 clean, core scripts (`cuf.py`, `loc.py`, `loc_compiler.py`, `shape.py`, `preview.py`, `cr_phase1_build.py`).
- `release/`: Retains only the active delivery packs (`Attila_Arabic_Phase1.pack`, `Attila_Arabic_Phase1_fonts.pack`).
- `data/translations/`: All 14 translation JSON/TSV tables held intact until Phase 3 audit.
- `tools/`: Retains functional Python venv, portable RPFM UI/server binaries, packfile library, and engine patch configs.
- `tests/`: 10/10 tests passing.

---

## 3. How to Permanently Delete Quarantine (When You Are Ready)

The agent will **never** delete the quarantine directory. Whenever you are confident that you no longer need the quarantined prototypes and debug files, you can permanently delete them yourself by running in PowerShell:

```powershell
# CAUTION: Run only when you are certain you do not need the quarantined files.
Remove-Item -Recurse -Force "D:\AttilaArabic\tw_attila_ar\quarantine"
```
Or delete individual subfolders (e.g. only the large PDB symbols):
```powershell
Remove-Item -Recurse -Force "D:\AttilaArabic\tw_attila_ar\quarantine\tools\rpfm-v5.1.1"
Remove-Item -Force "D:\AttilaArabic\tw_attila_ar\quarantine\tools\rpfm-v5.1.1-*.zip"
```
