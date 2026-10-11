#!/usr/bin/env python3
"""Engine Font Advance Patcher for Total War: ATTILA (empire.retail.dll)

Patches the hardcoded 1-pixel font advance gap in empire.retail.dll.
Vanilla engine has hardcoded:
    mov al, [eax+2]   ; load glyph width W
    inc al            ; FE C0 -> advance = W + 1
This causes a 1-pixel transparent gap between every connecting Arabic letter.

This script patches all 16 occurrences of 'FE C0' to '90 90' (NOP NOP),
making character advance equal to exact glyph width W (advance = W).
Spaces (0x20) branch separately to read alloc_w ([eax+1]) and remain unaffected.

Includes automatic vanilla backup (.vanilla_bak) and one-command revert (--revert).
"""

import os
import sys
import shutil
import argparse

DEFAULT_DLL_PATH = r"D:\SteamLibrary\steamapps\common\Total War Attila\empire.retail.dll"

# The 16 verified file offsets of 'fe c0' (inc al) in font layout / measuring routines
TARGET_OFFSETS = [
    0x16bc721,
    0x16bc7c6,
    0x16bc875,
    0x16bc91b,
    0x16bc9fd,
    0x16bcaec,
    0x16bcb92,
    0x16bcc74,
    0x17539c8,
    0x175e3cc,
    0x175e4c8,
    0x17768b2,
    0x1777508,
    0x1777616,
    0x1777704,
    0x178cf12,
]

EXPECTED_ORIGINAL_BYTES = b"\xfe\xc0"
PATCHED_BYTES = b"\x90\x90"


def get_backup_path(dll_path: str) -> str:
    return dll_path + ".vanilla_bak"


def backup_dll(dll_path: str) -> str:
    bak_path = get_backup_path(dll_path)
    if not os.path.exists(bak_path):
        print(f"[BACKUP] Creating pristine backup: {bak_path}")
        shutil.copy2(dll_path, bak_path)
    else:
        print(f"[BACKUP] Pristine backup already exists: {bak_path}")
    return bak_path


def revert_dll(dll_path: str) -> bool:
    bak_path = get_backup_path(dll_path)
    if not os.path.exists(bak_path):
        print(f"[ERROR] Cannot revert: backup file not found at {bak_path}")
        return False
    print(f"[REVERT] Restoring vanilla DLL from: {bak_path}")
    shutil.copy2(bak_path, dll_path)
    print(f"[REVERT] Successfully restored vanilla empire.retail.dll")
    return True


def apply_patch(dll_path: str) -> bool:
    if not os.path.exists(dll_path):
        print(f"[ERROR] Target DLL not found: {dll_path}")
        return False

    # 1. Ensure pristine backup exists
    backup_dll(dll_path)

    # 2. Read DLL content
    with open(dll_path, "rb") as f:
        dll_bytes = bytearray(f.read())

    print(f"[PATCH] Verifying {len(TARGET_OFFSETS)} font advance instructions in {dll_path}...")
    all_clean = True
    already_patched = 0

    for off in TARGET_OFFSETS:
        cur_bytes = bytes(dll_bytes[off : off + 2])
        if cur_bytes == PATCHED_BYTES:
            already_patched += 1
        elif cur_bytes != EXPECTED_ORIGINAL_BYTES:
            print(f"[MISMATCH] Offset 0x{off:x}: expected {EXPECTED_ORIGINAL_BYTES.hex()}, found {cur_bytes.hex()}")
            all_clean = False

    if already_patched == len(TARGET_OFFSETS):
        print("[INFO] DLL is already fully patched (all 16 offsets are NOP NOP).")
        return True

    if not all_clean:
        print("[ERROR] DLL bytes mismatch. Patch aborted for safety.")
        return False

    # 3. Patch all offsets
    for off in TARGET_OFFSETS:
        dll_bytes[off : off + 2] = PATCHED_BYTES

    # 4. Write patched DLL
    with open(dll_path, "wb") as f:
        f.write(dll_bytes)

    # 5. Verify written file
    with open(dll_path, "rb") as f:
        verified_bytes = f.read()

    for off in TARGET_OFFSETS:
        assert verified_bytes[off : off + 2] == PATCHED_BYTES, f"Verification failed at offset 0x{off:x}"

    print(f"[SUCCESS] Successfully patched {len(TARGET_OFFSETS)} font advance instructions!")
    print(f"[SUCCESS] Advance now equals exact glyph width W (zero 1px gap across all game text).")
    return True


def main():
    parser = argparse.ArgumentParser(description="Patch empire.retail.dll font advance hardcode (eliminate 1px gap).")
    parser.add_argument("--dll", default=DEFAULT_DLL_PATH, help="Path to empire.retail.dll")
    parser.add_argument("--revert", action="store_true", help="Revert to vanilla backup")
    args = parser.parse_args()

    if args.revert:
        success = revert_dll(args.dll)
    else:
        success = apply_patch(args.dll)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
