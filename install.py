#!/usr/bin/env python3
"""Install test packs into the game data folder.

Usage: python install.py [v15]   (version tag, default v15)
Deletes every Attila_Arabic_POC_*.pack in the game data dir, copies the
requested loc pack + its fonts pack, prints launch steps.
Never touches vanilla packs.
"""
import glob
import os
import shutil
import sys

BASE = r"D:\AttilaArabic"
DATA = r"D:\SteamLibrary\steamapps\common\Total War Attila\data"

ver = sys.argv[1] if len(sys.argv) > 1 else "v15"
want = [f"Attila_Arabic_POC_{ver}.pack", f"Attila_Arabic_POC_{ver}_fonts.pack"]

assert os.path.isdir(DATA), DATA
for old in glob.glob(os.path.join(DATA, "Attila_Arabic_POC_*.pack")):
    os.remove(old)
    print("removed", os.path.basename(old))
for name in want:
    src = os.path.join(BASE, "release", name)
    assert os.path.exists(src), src
    shutil.copy2(src, os.path.join(DATA, name))
    print("copied ", name)

print("""
Launch steps:
1. Quit the game and Steam launcher fully.
2. Steam -> Attila -> Play -> Mod Manager.
3. Tick ONLY: Attila_Arabic_POC_%s and Attila_Arabic_POC_%s_fonts.
4. Screenshots (1920x1080):
   a. Faction select -> Eastern Roman Empire (ruler L1-L6 geo12 + WRE pad lines)
   b. Faction select -> Western Roman Empire (pad-indent lines)
   c. Difficulty slider -> Hard (gio12 ruler)
""" % (ver, ver))
