# Total War: ATTILA — Safety & Game Integrity Specification

> **Document Classification:** Binding Operational Specification  
> **Target Application:** Total War: ATTILA (`Attila.exe`)  
> **Status:** ACTIVE & ENFORCED

---

## 1. Executive Summary & Core Mandate

The primary invariant of this project is **zero modification to the user's licensed game installation**. All toolchain activities operate strictly within a clean-room development workspace, generating independent, modular `.pack` files. 

Under no circumstances may automated tools, scripts, or manual operations alter, patch, or overwrite any original game executable or vanilla archive.

---

## 2. Directory Boundaries & Access Control

| Environment | Path | Access Rights | Scope & Usage |
| :--- | :--- | :---: | :--- |
| **Clean-Room Workspace** | `D:\AttilaArabic\` | **READ / WRITE** | Repository root. Contains toolchains, configs, tests, build outputs, and logs. |
| **Game Installation** | `D:\SteamLibrary\steamapps\common\Total War Attila\` | **READ-ONLY** | Original Steam installation directory. Source for extraction and verification only. |
| **Game Mod Target** | `D:\SteamLibrary\steamapps\common\Total War Attila\data\` | **ISOLATED DROP** | Receives ONLY project `.pack` outputs (`Attila_Arabic_Phase1*.pack`). |

---

## 3. Binding Operational Rules

1. **Vanilla Pack Protection**:
   * Never overwrite, edit, delete, or rename any file inside the game installation.
   * Never modify vanilla `.pack` archives (such as `local_en.pack`, `data.pack`, `models.pack`) in place.
   * All extraction processes must write exclusively to `extracted\` within the project workspace.

2. **Executable Integrity**:
   * Never patch, binary-edit, or hook `Attila.exe`.
   * Never inject external DLLs, memory hooks, or debugging detours into the game runtime.

3. **Mod Configuration Safety**:
   * Never automatically modify `%APPDATA%\The Creative Assembly\Attila\scripts\preferences.script.txt` or `user.script.txt`.
   * Mod activation is handled strictly via standalone `.pack` files loaded as type 3 (`mod`) or user-controlled launcher settings.

4. **Self-Contained Mod Architecture**:
   * Mod assets are delivered exclusively via two isolated archives:
     * `Attila_Arabic_Phase1.pack` (Localization table overrides)
     * `Attila_Arabic_Phase1_fonts.pack` (Custom merged CUF fonts)
   * Deleting these two files instantly and completely restores the pristine vanilla state.

---

## 4. Cryptographic Integrity Benchmarks

The automated test suite (`tests/test_phase1_packs.py`) computes and verifies SHA-256 hashes against vanilla game binaries before and after every operation:

```text
Target Binary:     D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack
Expected SHA-256:  45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D

Target Binary:     D:\SteamLibrary\steamapps\common\Total War Attila\Attila.exe
Expected SHA-256:  51B833D5B8FD8505A7CD035FD92F68CACE681D62EA74D9AD8FBAE26326635BF5
```

> [!CAUTION]
> If any test or build script detects a mismatch against the above SHA-256 hashes, execution immediately halts, logs a fatal error, and aborts deployment.
