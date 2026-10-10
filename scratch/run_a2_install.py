import os
import sys
import glob
import shutil
import hashlib
import datetime

GAME_DIR = r"D:\SteamLibrary\steamapps\common\Total War Attila"
DATA_DIR = os.path.join(GAME_DIR, "data")
LOCAL_EN = os.path.join(DATA_DIR, "local_en.pack")
ATTILA_EXE = os.path.join(GAME_DIR, "Attila.exe")

RELEASE_DIR = r"D:\AttilaArabic\release"
RELEASE_LOC = os.path.join(RELEASE_DIR, "Attila_Arabic_Phase1.pack")
RELEASE_FONTS = os.path.join(RELEASE_DIR, "Attila_Arabic_Phase1_fonts.pack")

EXPECTED_LOCAL_EN_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"
EXPECTED_ATTILA_EXE_SHA = "51B833D5B8FD8505A7CD035FD92F68CACE681D62EA74D9AD8FBAE26326635BF5"

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def check_file_locked(path: str, mode="r+b") -> bool:
    if not os.path.exists(path):
        return False
    try:
        with open(path, mode):
            pass
        return False
    except (IOError, PermissionError):
        return True

def main():
    print("=== A2 INSTALL PROCEDURE: ROUND 3 ===")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Timestamp: {now}")

    # 1. Close-check & lock check
    print("\n--- 1. Close & Lock Check ---")
    old_packs = glob.glob(os.path.join(DATA_DIR, "Attila_Arabic*.pack"))
    for p in old_packs:
        if check_file_locked(p, "a+b"):
            print(f"FATAL: File locked: {p}")
            sys.exit(1)
        print(f"  Lock check passed: {os.path.basename(p)} is not locked.")

    if check_file_locked(LOCAL_EN, "rb"):
        print(f"FATAL: local_en.pack is locked!")
        sys.exit(1)
    print("  Lock check passed: local_en.pack is not locked.")

    if check_file_locked(ATTILA_EXE, "rb"):
        print(f"FATAL: Attila.exe is locked!")
        sys.exit(1)
    print("  Lock check passed: Attila.exe is not locked.")

    # 2. SHA-256 BEFORE
    print("\n--- 2. Pre-Install Hash Check ---")
    local_en_sha_before = sha256_file(LOCAL_EN)
    attila_exe_sha_before = sha256_file(ATTILA_EXE)
    print(f"  local_en.pack SHA-256 (BEFORE): {local_en_sha_before}")
    print(f"  Attila.exe   SHA-256 (BEFORE): {attila_exe_sha_before}")
    assert local_en_sha_before == EXPECTED_LOCAL_EN_SHA, f"local_en.pack hash mismatch BEFORE install: {local_en_sha_before}"
    assert attila_exe_sha_before == EXPECTED_ATTILA_EXE_SHA, f"Attila.exe hash mismatch BEFORE install: {attila_exe_sha_before}"
    print("  Vanilla file integrity: VERIFIED byte-identical.")

    # 3. Print list of old Attila_Arabic*.pack in data\ before deleting
    print("\n--- 3. Old Attila_Arabic*.pack in data\\ (Pre-Deletion) ---")
    old_records = []
    for p in sorted(old_packs):
        st = os.stat(p)
        h = sha256_file(p)
        mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        rec = {
            "name": os.path.basename(p),
            "size": st.st_size,
            "mtime": mtime,
            "sha256": h,
        }
        old_records.append(rec)
        print(f"  File: {rec['name']}")
        print(f"    Size: {rec['size']} bytes")
        print(f"    LastWriteTime: {rec['mtime']}")
        print(f"    SHA-256: {rec['sha256']}")

    # 4. Delete old Attila_Arabic*.pack
    print("\n--- 4. Deleting Old Packs from data\\ ---")
    for p in old_packs:
        os.remove(p)
        print(f"  Deleted: {os.path.basename(p)}")

    # 5. Copy packs from release\ into data\
    print("\n--- 5. Copying Release Packs into data\\ ---")
    rel_loc_sha = sha256_file(RELEASE_LOC)
    rel_fonts_sha = sha256_file(RELEASE_FONTS)
    print(f"  Source release\\Attila_Arabic_Phase1.pack       SHA-256: {rel_loc_sha}")
    print(f"  Source release\\Attila_Arabic_Phase1_fonts.pack SHA-256: {rel_fonts_sha}")

    dst_loc = os.path.join(DATA_DIR, "Attila_Arabic_Phase1.pack")
    dst_fonts = os.path.join(DATA_DIR, "Attila_Arabic_Phase1_fonts.pack")

    shutil.copy2(RELEASE_LOC, dst_loc)
    shutil.copy2(RELEASE_FONTS, dst_fonts)
    print(f"  Copied to: {dst_loc}")
    print(f"  Copied to: {dst_fonts}")

    # 6. Verify SHA-256 of each copy in data\ against release\
    print("\n--- 6. Verifying Copies in data\\ ---")
    dst_loc_sha = sha256_file(dst_loc)
    dst_fonts_sha = sha256_file(dst_fonts)
    print(f"  data\\Attila_Arabic_Phase1.pack       SHA-256: {dst_loc_sha}")
    print(f"  data\\Attila_Arabic_Phase1_fonts.pack SHA-256: {dst_fonts_sha}")

    assert dst_loc_sha == rel_loc_sha, "Copied loc pack SHA-256 does not match release pack!"
    assert dst_fonts_sha == rel_fonts_sha, "Copied fonts pack SHA-256 does not match release pack!"
    print("  Copy verification: VERIFIED byte-identical.")

    # 7. Print SHA-256 AFTER
    print("\n--- 7. Post-Install Hash Check ---")
    local_en_sha_after = sha256_file(LOCAL_EN)
    attila_exe_sha_after = sha256_file(ATTILA_EXE)
    print(f"  local_en.pack SHA-256 (AFTER): {local_en_sha_after}")
    print(f"  Attila.exe   SHA-256 (AFTER): {attila_exe_sha_after}")

    assert local_en_sha_after == EXPECTED_LOCAL_EN_SHA, f"local_en.pack modified! {local_en_sha_after}"
    assert attila_exe_sha_after == EXPECTED_ATTILA_EXE_SHA, f"Attila.exe modified! {attila_exe_sha_after}"
    assert local_en_sha_after == local_en_sha_before, "local_en.pack changed during install!"
    assert attila_exe_sha_after == attila_exe_sha_before, "Attila.exe changed during install!"
    print("  Vanilla file integrity: VERIFIED byte-identical before and after install.")

    # 8. Write docs/install_log.md
    log_path = r"D:\AttilaArabic\docs\install_log.md"
    log_content = f"""# Installation Log

## Round 3 Deployment Log

- **Timestamp:** {now}
- **Target Folder:** `{DATA_DIR}`
- **Deployment Status:** SUCCESS (Verified)

### Vanilla Integrity Audit
| File | SHA-256 (Before) | SHA-256 (After) | Status |
|---|---|---|---|
| `data\\local_en.pack` | `{local_en_sha_before}` | `{local_en_sha_after}` | **UNCHANGED (BYTE-IDENTICAL)** |
| `Attila.exe` | `{attila_exe_sha_before}` | `{attila_exe_sha_after}` | **UNCHANGED (BYTE-IDENTICAL)** |

### Removed Old Packs from `data\\`
| Pack Filename | File Size | LastWriteTime | SHA-256 |
|---|---|---|---|
"""
    for r in old_records:
        log_content += f"| `{r['name']}` | {r['size']} bytes | {r['mtime']} | `{r['sha256']}` |\n"

    log_content += f"""
### Installed New Packs into `data\\`
| Pack Filename | Pack Type | File Size | Release SHA-256 | Installed SHA-256 | Status |
|---|---|---|---|---|---|
| `Attila_Arabic_Phase1.pack` | PFH4 (Type 3 Mod) | {os.path.getsize(dst_loc)} bytes | `{rel_loc_sha}` | `{dst_loc_sha}` | **VERIFIED MATCH** |
| `Attila_Arabic_Phase1_fonts.pack` | PFH4 (Type 3 Mod) | {os.path.getsize(dst_fonts)} bytes | `{rel_fonts_sha}` | `{dst_fonts_sha}` | **VERIFIED MATCH** |

### Launcher Mod Manager Configuration
The following exact packs must be ticked in the Total War: ATTILA Launcher Mod Manager:
1. `Attila_Arabic_Phase1.pack`
2. `Attila_Arabic_Phase1_fonts.pack`

*(Note: `used_mods.txt` was NOT modified by the installer).*
"""
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_content.strip() + "\n")
    print(f"\nWritten installation log to: {log_path}")

if __name__ == "__main__":
    main()
