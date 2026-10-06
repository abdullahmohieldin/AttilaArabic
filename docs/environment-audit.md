# Environment Audit — Attila Arabic POC

Date: 2026-10-06. All entries verified on this machine unless labeled otherwise.

## Game install (READ-ONLY)

| Item | Value | Label |
|------|-------|-------|
| Path | `D:\SteamLibrary\steamapps\common\Total War Attila` | VERIFIED (exists, listed) |
| `data\local_en.pack` | 211,301,042 bytes, PFH4, 214 files, type `release (1)` | VERIFIED (packfile.py info + header bytes) |
| SHA256 before testing | `45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D` | VERIFIED (Get-FileHash) |
| SHA256 after Phase 0/1 + CUF extraction | identical to above | VERIFIED (re-hashed 2026-10-06) |
| `data\language.txt` | `EN` | VERIFIED |
| `languages\` | empty directory | VERIFIED |
| `data\text\` | only `credits.xml`, `default_keys.xml`, `default_keys_osx.xml` | VERIFIED |
| `data\MyMods\` | empty | VERIFIED |
| `ModManager.exe` | present | VERIFIED |
| `user.script.txt` | not present (created on first mod use); `preferences.script.txt` present | VERIFIED |
| Assembly Kit | absent under `D:\SteamLibrary\steamapps\common` | VERIFIED |

## CUF inventory inside `local_en.pack` (from working COPY)

38 fonts, VERIFIED via pack table listing:

| Family | Sizes | Notes |
|--------|-------|-------|
| `arialunicode` | 10, 12, 14, 16, 18, 20, 22 (9–42 MB each) | body/UI font; magic `CUF1` |
| `georgia_italic` | 10–18 (~340–500 KB) | magic unchecked (assumed CUF, UNVERIFIED) |
| `la_gioconda` | 10–38, 13 sizes (~280–650 KB) | magic `CUF0` (10 checked) |
| `la_gioconda_uppercase` | 10–38, 13 sizes | magic unchecked (UNVERIFIED) |

Per your change #1 (merge, don't subset): every size that the UI uses needs
its own merged CUF. Which sizes the UI actually references is still
UNVERIFIED — to be determined from UI/layout files in Phase 2/3.

## Tools

| Tool | Version | Path | Label |
|------|---------|------|-------|
| Python | 3.13.7 | `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` | VERIFIED |
| Git | 2.51.0.windows.1 | `C:\Program Files\Git\cmd\git.exe` | VERIFIED |
| 7-Zip | 26.00 (x64) | `C:\Program Files\7-Zip\7z.exe` (NOT on PATH) | VERIFIED |
| VS Code | — | not installed (both standard paths + registry negative) | VERIFIED ABSENT |
| Java | — | absent (`java` not on PATH) | VERIFIED ABSENT — blocks Tellos CUF tool |
| Ruby / cargo / rustc | — | all absent | VERIFIED ABSENT — blocks etwng (Ruby) and Rust builds |
| Legacy PackFileManager | old PFM 5.x era (config only) | `%LOCALAPPDATA%\PackFileManager\` | VERIFIED (exe not located) |
| RPFM | **5.1.1 portable** | `D:\AttilaArabic\tools\rpfm-v5.1.1\` (`rpfm_ui.exe` FileVersion 5.1.1) | VERIFIED |
| RPFM zip | 293,600,799 bytes | `D:\AttilaArabic\tools\rpfm-v5.1.1-x86_64-pc-windows-msvc.zip` | VERIFIED |
| RPFM CLI | — | v5.x ships NO `rpfm_cli.exe`; only `rpfm_ui.exe` + `rpfm_server.exe` (WebSocket/MCP server) | VERIFIED |

## Python venv (`D:\AttilaArabic\tools\venv`)

`pip freeze` (VERIFIED, `logs\pip-freeze.txt`):

```text
arabic-reshaper==3.0.1
fonttools==4.66.1
pillow==12.3.0
python-bidi==0.6.11
```

pip 26.2.1 (upgraded from 25.2). System site-packages additionally has
`fonttools 4.66.1` + `pillow 12.2.0` (VERIFIED, pre-existing).

## Workspace (`D:\AttilaArabic\`)

Created 2026-10-06 with `docs source extracted tools fonts localization
tests build release screenshots logs` (VERIFIED). Key files so far:

- `docs\SAFETY.md` — read-only rules
- `logs\baseline.txt` — pack hashes (before/after identical)
- `logs\pip-freeze.txt` — venv pins
- `tools\packfile.py` — `ntw_pack_esf_tools` PFH0/4/5 reader/writer
  (MIT-licensed community tool; lists/extracts Attila PFH4 correctly)
- `tools\etwng\` — `taw/etwng` git clone (depth 1) for CUF reference
- `source\cuf.py` — project CUF1 codec (decode + encode + coverage)
- `extracted\local_en.copy.pack` — working copy, SHA256 == original
- `extracted\fonts\arialunicode_10.cuf` (9,151,760 B), `la_gioconda_10.cuf`
- `build\*.rt.cuf`, `build\la_gioconda_10.plus2.cuf` — round-trip/add tests
