# Part 1 Implementation Plan: Pre-Campaign Frontend & Faction Selection Screen

**Project:** Total War: Attila Arabic Localization (Part 1 Only)  
**Deliverable:** Standalone override `.pack` (Mod type) for all screens prior to entering a campaign, beginning with the Faction Selection screen.  
**Approved Spec:** User prompt dated 2026-10-10.

---

## 1. Discovered Inputs & Environment
- **Attila Install Path:** `D:\SteamLibrary\steamapps\common\Total War Attila` (Data folder: `D:\SteamLibrary\steamapps\common\Total War Attila\data`) — STRICTLY READ-ONLY.
- **Existing Arabic Localization / Mod Project:** `D:\AttilaArabic` (Git repository on branch `clean-room`, origin `https://github.com/debo002/AttilaArabic.git`).
- **Font Work / Glyph Tooling:** `D:\AttilaArabic\fonts` (Upstream: `Tajawal-Regular.ttf`), `source/cuf.py`, `source/cr_phase1_build.py`, `reference/cuf-tool`. Separate track — strictly reporting only, no modification.
- **Screenshots:** Visual crops available in `D:\AttilaArabic\scratch/` (`crop_leader_religion.png`, `crop_sand_button.png`); `docs/screenshot_log.md` documents prior capture logs; `screenshots/` directory has `desktop.ini` only.
- **WORKDIR:** `D:\AttilaArabic\tw_attila_ar` (`./tw_attila_ar`).

---

## 2. Hard Constraints & Operating Rules
1. **Attila Install is strictly READ-ONLY:** Never write, modify, or delete files in `D:\SteamLibrary\...`.
2. **Quarantine Over Deletion:** Project cleaning moves files into `<WORKDIR>/quarantine/` with `MANIFEST.tsv`. No hard deletes.
3. **Git History Preservation:** Never rewrite history, never force-push, never delete branches/tags/stashes. Never push without explicit instruction.
4. **Clean-Room Overrides:** Clean-room pack overrides only. No exe patching, no memory hooking, no redistribution of raw vanilla assets outside `<WORKDIR>`.
5. **Reverse Engineering Scope:** Authorized offline fan mod on legally owned copy only. Case scope recorded in `<WORKDIR>/case/scope.md`.
6. **Tooling & Dependency Policy:** Ponytail principle (prefer existing tools, Python stdlib over bloat); pin versions in `<WORKDIR>/vendor`.

---

## 3. Execution Phases & Gates

### Phase 0: Audit Prompt Against Reality
- Audit each prompt assumption against real files and engine behavior:
  - Pack names (`local_en.pack` vs `local_en_shared_rome2.pack`, DLCs, absence of patch packs).
  - File paths (`text/db/*.loc`).
  - Loc columns (`key`, `text`, `tooltip` u8 flag).
  - RPFM game key (`attila` confirmed in `rpfm_lib`).
  - RPFM CLI availability (flagged: v5.x ships no `rpfm_cli.exe`; Python packfile/loc tools serve as verified equivalent).
  - Markup patterns (`[[col:...]]`, `[[url:...]]`, `%s`, `%d`).
  - Load-order & override behavior (mod pack priority, key-level localization dictionary merge).
  - Faction select UI layout location (`ui/frontend ui/sp_grand_campaign` in `data.pack`).
  - Project layout structure.
- Deliverable: `<WORKDIR>/AUDIT_PROMPT.md`.

### Phase 0.5: Clean the Project and Repo
- **A. Snapshot:**
  - Create zip backup of project to `<WORKDIR>/backup/project_<timestamp>.zip`.
  - Record git status, stash, branches, and remotes.
  - Commit uncommitted changes to a dedicated branch `pre-cleanup-snapshot` and create tag `pre-cleanup-<timestamp>`.
- **B. Classification:**
  - Audit every file and folder by size, mtime, and git status.
  - Categorize into `KEEP`, `JUNK`, `DEAD`, `BROKEN`, `LEGACY-LOCALIZATION`, `UNSURE`.
  - Document evidence and rationale in `<WORKDIR>/CLEANUP_PLAN.md`.
- **C. Repo Hygiene:**
  - Review `.gitignore` and `.gitattributes`.
  - Identify untracked binaries, game-extracted data, absolute paths, and secrets.
- **>>> GATE G1 (STOP):** Present `CLEANUP_PLAN.md` to user and wait for explicit confirmation.
- **D. Execution (Post-G1):**
  - Move classified items to `<WORKDIR>/quarantine/<original path>` with `MANIFEST.tsv`.
  - Commit removals as small, focused commits on branch `cleanup`.
  - Verify surviving test suite passes; write `RESTORE.md` and `CLEANUP_REPORT.md`.

### Phase 1: Tooling
- Clone `Frodo45127/rpfm` and `Frodo45127/rpfm-schemas` into `<WORKDIR>/vendor` for reference.
- Verify schema definition for Attila (`schema_att.ron`).
- Document verified tool invocations and CLI/Python tools in `<WORKDIR>/TOOLING.md`.

### Phase 2: Extraction & Master Localization Table
- Inspect all packs in Attila `data/` folder and extract all 171 `text/db/*.loc` files from `local_en.pack`.
- Determine load order and key override semantics.
- Compile `master/master.tsv` with schema: `key | text_en | tooltip | source_pack | source_file | load_rank`.
- Report translatable text appearing in Part 1 screens (DB tables, UI layout strings).

### Phase 3: Audit Existing Localization
- Audit current Arabic JSON translation catalogs against master keys.
- Check placeholder matching (`%s`, `%d`), Latin leftovers, tooltip flags, encoding.
- Analyze shaping pipeline (`source/shape.py`, Arabic Reshaper, python-bidi, Presentation Forms-B).
- Produce `AUDIT_EXISTING.md` with concrete coverage and quality metrics.
- Quarantine deprecated legacy translations to `<WORKDIR>/quarantine/legacy/`.

### Phase 4: Map Faction Selection Screen & Root-Cause RTL Bugs
- Dissect `ui/frontend ui/sp_grand_campaign` layout component tree.
- Map every visual element to its UI component, loc key, DB source, and English text in `FACTION_SCREEN_MAP.md`.
- Root-cause observed issues (leader/religion swapped, icon placement, description alignment, button text clipping).
- Propose and rank candidate fixes (loc string formatting vs UI component layout overrides).
- **>>> GATE G2 (STOP):** Present screen map, root causes, and fix proposals to user and wait for confirmation.

### Phase 5: Translate Part 1
- **Scope 1A:** Faction selection (factions, cultures, religions, leaders, traits, descriptions, buttons, start dates).
- **Scope 1B:** Rest of pre-campaign frontend (main menu, options, loading screens, custom battle menus).
- Token protection with `<P1>`.. placeholders; locked terminology in `glossary.csv`.
- Logical-order MSA Arabic in translation source layers.
- Process in batches (~100-150 entries in JSONL) with automated TDD test validation (`validate.py`).

### Phase 6: Implement RTL Fixes
- Apply approved G2 layout/text fixes.
- Keep logical text separated from visual shaping output (`out_shaped/`).
- Calibrate layout ordering and line alignment.
- Report Presentation Forms-B glyph usage for font verification.

### Phase 7: Build & Verify
- Compile verified loc tables to binary `.loc` format.
- Assemble standalone Mod `.pack` in `<WORKDIR>/out/` using clean-room pack builder.
- Validate pack structure with round-trip extraction and diff verification.
- Provide manual installation guide (`INSTALL.md`) and in-game verification checklist (`TEST_CHECKLIST.md`).

### Phase 8: Iteration Loop
- Ingest new in-game verification screenshots from user.
- Compare with expected checklist, diagnose anomalies, apply iterative corrections, and record in `ITERATIONS.md`.
