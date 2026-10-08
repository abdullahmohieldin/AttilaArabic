#!/usr/bin/env python3
"""Install one clean-room test set into the game data folder.

Usage: python install.py C0|C1|C2|v14|none
Deletes every Attila_Arabic_*.pack in the game data dir first, then copies
exactly the packs of the requested test set. Never touches vanilla packs.
  C0  loc only (vanilla fonts)      C1  loc + Shyizer's 37 CUFs
  C2  loc + vanilla font barcodes   v14 restore the shipping build
  none  remove our packs, leave vanilla only
"""
import glob
import os
import shutil
import sys

BASE = r"D:\AttilaArabic"
DATA = r"D:\SteamLibrary\steamapps\common\Total War Attila\data"
REL = os.path.join(BASE, "release")

SETS = {
    "C0": ["Attila_Arabic_CR_C0.pack"],
    "C1": ["Attila_Arabic_CR_C1.pack", "Attila_Arabic_CR_C1_fonts.pack"],
    "C2": ["Attila_Arabic_CR_C2.pack", "Attila_Arabic_CR_C2_fonts.pack"],
    "C3": ["Attila_Arabic_CR_C3.pack", "Attila_Arabic_CR_C3_fonts.pack"],
    "C5": ["Attila_Arabic_CR_C5.pack", "Attila_Arabic_CR_C5_fonts.pack"],
    "v14": ["Attila_Arabic_POC_v14.pack", "Attila_Arabic_POC_v14_fonts.pack"],
    "none": [],
}

SHOTS = {
    "C0": ["faction select -> Eastern Roman Empire (description box)",
           "faction select -> Western Roman Empire",
           "difficulty slider (description box)",
           "main menu (buttons)",
           "custom battle -> choose army -> unit list + one unit card"],
    "C1": ["same five surfaces as C0"],
    "C2": ["faction select -> ERE: description box + faction title + group list",
           "faction select -> WRE",
           "difficulty slider box",
           "main menu buttons",
           "custom battle -> choose army: header, unit name, stat labels",
           "hover the difficulty medal (tooltip)"],
    "C3": ["faction select -> ERE: the 4 sweep rows at the top of the description box",
           "faction select -> WRE: the 4 sweep rows",
           "difficulty box (right panel): the 4 sweep rows",
           "campaign menu: the battle-settings button line (single row)"],
    "C5": ["faction select -> ERE: description box, all 6 probe rows (4 sweep + 2 ruler)",
           "faction select -> WRE: description box, all 6 probe rows",
           "difficulty box (right panel): the 6 probe rows",
           "campaign menu: the battle-settings button (ruler row)",
           "custom battle setup (choose army): the header line + unit stat labels",
           "one menu button with Arabic on it (main menu is fine)"],
}

test = sys.argv[1] if len(sys.argv) > 1 else "C0"
assert test in SETS, f"unknown test set {test!r}; use one of {sorted(SETS)}"
assert os.path.isdir(DATA), DATA

for old in glob.glob(os.path.join(DATA, "Attila_Arabic_*.pack")):
    os.remove(old)
    print("removed", os.path.basename(old))
for name in SETS[test]:
    src = os.path.join(REL, name)
    assert os.path.exists(src), f"missing {src} - run source/cr_build.py {test}"
    shutil.copy2(src, os.path.join(DATA, name))
    print("copied ", name)

print(f"\n{test}: {len(SETS[test])} pack(s) installed")
print("Launch steps:")
print("1. Quit the game and Steam fully.")
print("2. Steam -> Attila -> Play -> Mod Manager.")
tick = " and ".join(os.path.splitext(n)[0] for n in SETS[test])
print(f"3. Tick ONLY: {tick}" if tick else "3. Tick NOTHING (vanilla only).")
print("4. Screenshots (1920x1080) into D:\\AttilaArabic\\screenshots\\:")
for s in SHOTS.get(test, []):
    print("   -", s)
