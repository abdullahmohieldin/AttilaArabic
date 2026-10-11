# Quarantine Restoration Guide

**Document:** `<WORKDIR>/RESTORE.md`  
**Location:** `tw_attila_ar/RESTORE.md`  

---

## 1. Quick Restoration of All Quarantined Items

All quarantined files are preserved with their exact relative paths inside `<WORKDIR>/quarantine/`.
To restore everything back to the working tree, run this PowerShell script from the project root (`D:\AttilaArabic`):

```powershell
# Restore all quarantined files back to the project root
$quarantine = "D:\AttilaArabic\tw_attila_ar\quarantine"
$root = "D:\AttilaArabic"

Get-ChildItem -Path $quarantine -Recurse -File | ForEach-Object {
    if ($_.Name -ne "MANIFEST.tsv") {
        $rel = [System.IO.Path]::GetRelativePath($quarantine, $_.FullName)
        $target = Join-Path $root $rel
        $parent = Split-Path -Path $target -Parent
        if (-not (Test-Path $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Move-Item -Path $_.FullName -Destination $target -Force
        Write-Host "Restored: $rel"
    }
}
```

---

## 2. Restoring Individual Categories

### A. Restore Experimental Calibration Scripts (`source/cr_*.py`)
```powershell
Copy-Item "D:\AttilaArabic\tw_attila_ar\quarantine\source\cr_*.py" "D:\AttilaArabic\source\" -Force
```

### B. Restore Scratch Analysis Scripts & Crops (`scratch/`)
```powershell
Copy-Item -Recurse "D:\AttilaArabic\tw_attila_ar\quarantine\scratch" "D:\AttilaArabic\" -Force
```

### C. Restore Historical Release Packs (`release/`)
```powershell
Copy-Item "D:\AttilaArabic\tw_attila_ar\quarantine\release\*.pack" "D:\AttilaArabic\release\" -Force
```

---

## 3. Git Snapshot Restoration
If you ever want to completely return the git repository to the exact commit prior to cleanup:
```bash
git checkout pre-cleanup-snapshot
```
Or reset branch `cleanup`:
```bash
git reset --hard pre-cleanup-20261010_143319
```
