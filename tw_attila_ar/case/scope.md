# Reverse Engineering Scope & Authorization Contract

**Case ID:** TW-ATTILA-AR-PART1  
**Project:** Total War: Attila Arabic Localization Fan Mod  
**Date:** 2026-10-10  
**Authorization Statement:**  
authorized: my own fan mod; local files only; offline; no exe patching, no memory hooks, no network targets.

---

## 1. Scope Boundaries
- **Target Files:** Legally owned local installation of Total War: Attila (`D:\SteamLibrary\steamapps\common\Total War Attila`).
- **Access Level:** Strictly READ-ONLY on game installation directory.
- **Mod Delivery:** Clean-room standalone `.pack` files loaded via the standard game mod engine.
- **Prohibited Actions:**
  - No executable binary patching (`Attila.exe`).
  - No dynamic process memory injection, hooking, or debugging of the running game process.
  - No network interception, traffic capture, or remote API endpoints.
  - No redistribution of original vanilla assets or game text outside `<WORKDIR>`.

---

## 2. Tooling & Execution Rules
- **Tool Isolation:** All third-party analytical tools, schemas, and clones must be placed inside `<WORKDIR>/vendor`.
- **No Autonomous Installs:** Tools must not be silently or automatically installed without explicit disclosure. Pin versions and report all tool invocations.
- **Case Knowledge Base:** All case notes, disassembly/format analysis, and artifacts are strictly confined to `<WORKDIR>`.
