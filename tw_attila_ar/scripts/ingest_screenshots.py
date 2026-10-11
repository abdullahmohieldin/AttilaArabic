#!/usr/bin/env python3
"""
Ingest, rename, and deduplicate Total War: Attila in-game screenshots.
Transfers or syncs screenshots from NVIDIA capture folder into tw_attila_ar/screenshots/,
renames them according to the test checklist, and deletes duplicates in NVIDIA folder.
"""
import os
import shutil
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
NVIDIA_DIR = Path(r"C:\Users\egbin\Videos\NVIDIA\Total War  Attila")


def get_file_hash(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def sync_and_cleanup():
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not NVIDIA_DIR.exists():
        print(f"NVIDIA directory not found: {NVIDIA_DIR}")
        return

    nvidia_files = sorted(list(NVIDIA_DIR.glob("*.png")) + list(NVIDIA_DIR.glob("*.jpg")) + list(NVIDIA_DIR.glob("*.jxr")))
    project_files = sorted([f for f in SCREENSHOTS_DIR.glob("*") if f.is_file() and f.name != ".gitkeep"])

    project_hashes = {get_file_hash(f): f for f in project_files}

    print(f"Project screenshots count: {len(project_files)}")
    print(f"NVIDIA captured count: {len(nvidia_files)}")

    for n_file in nvidia_files:
        n_hash = get_file_hash(n_file)
        if n_hash in project_hashes:
            print(f"Duplicate detected in NVIDIA folder: {n_file.name} matches project {project_hashes[n_hash].name}")
            print(f"Deleting duplicate from NVIDIA folder: {n_file}")
            n_file.unlink()
        else:
            dest = SCREENSHOTS_DIR / n_file.name
            print(f"Copying new screenshot {n_file.name} -> {dest}")
            shutil.copy2(n_file, dest)
            project_hashes[n_hash] = dest
            # Delete original from NVIDIA as user requested
            n_file.unlink()
            print(f"Removed from NVIDIA folder: {n_file.name}")


if __name__ == "__main__":
    sync_and_cleanup()
