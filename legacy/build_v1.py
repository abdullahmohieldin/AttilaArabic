#!/usr/bin/env python3
"""Build v1 loc-only test pack (no CUF): full-file copies of 3 vanilla .loc
files with 4 rows replaced by pre-shaped Arabic. Reproducible.

Usage: build_v1.py
Reads : extracted/local_en.copy.pack (via packfile.py + source/loc.py)
Writes: build/v1/*.loc, release/Attila_Arabic_POC_v1.pack,
        docs/test-pack-manifest-v1.md
"""
import os
import subprocess
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from loc import decode, encode  # noqa: E402
from shape import shape  # noqa: E402

VENV_PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
PACK_PY = os.path.join(BASE, "tools", "packfile.py")
COPY_PACK = os.path.join(BASE, "extracted", "local_en.copy.pack")
BUILD = os.path.join(BASE, "build", "v1")
REL = os.path.join(BASE, "release", "Attila_Arabic_POC_v1.pack")

# logical (typed-order) Arabic test strings
STRINGS = {
    "uied_component_texts_localised_string_string_NewState_Text_1c0025":
        "القاهرة",
    "uied_component_texts_localised_string_mp_tx_NewState_Text_75002f":
        "Rome 1200 — روما",
    "factions_screen_name_att_fact_western_roman_empire":
        "الجيش الأول: 1200 جندي",
    "start_pos_factions_long_description_2120156339":
        "الإمبراطورية الرومانية الغربية على حافة الانهيار. الإمبراطور يرقص "
        "على أنغام قائدٍ من الوندال، ومجلس الشيوخ عاجزٌ في ضياعٍ واسعة. "
        "روما — أم الإمبراطورية — أُهملت لصالح عاصمةٍ عملية في ميديولانوم. "
        "منذ انقسام الإمبراطورية (395م) تفاقمت العيوب بسرعة: التجارة 1200 "
        "قطعة ذهبية والضرائب أعلى بنسبة 25%.",
}

FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
]


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args}\n{r.stderr[-2000:]}")
    return r.stdout


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.makedirs(BUILD, exist_ok=True)
    changed = {}
    for internal in FILES:
        tmp = os.path.join(BUILD, "vanilla_" + internal.split("\\")[-1])
        run(VENV_PY, PACK_PY, "extract", COPY_PACK, internal, "--output", tmp)
        rows, pos, total = decode(open(tmp, "rb").read())
        assert pos == total, f"slack in {internal}"
        n0 = len(rows)
        out = []
        for k, t, tip in rows:
            if k in STRINGS:
                v = shape(STRINGS[k])
                changed[k] = (t, v)
                out.append((k, v, tip))
            else:
                out.append((k, t, tip))
        assert any(k in STRINGS for k, _, _ in rows), internal
        data = encode(out)
        # self-check: re-decode
        rows2, pos2, _ = decode(data)
        assert pos2 == len(data) and len(rows2) == n0
        open(os.path.join(BUILD, internal.split("\\")[-1]), "wb").write(data)
    print(f"edited {len(changed)} keys:")
    for k, (old, new) in changed.items():
        print(f"  {k}\n    was: {old[:60]!r}\n    now(logical): {STRINGS[k][:60]!r}")
    run(VENV_PY, PACK_PY, "create", os.path.join(BUILD, "v1.pack"),
        "--type", "3", "--version", "PFH4")
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        run(VENV_PY, PACK_PY, "add", os.path.join(BUILD, "v1.pack"),
            internal, os.path.join(BUILD, leaf))
    run(VENV_PY, PACK_PY, "set-type", os.path.join(BUILD, "v1.pack"),
        "3", "--output", REL)
    print(run(VENV_PY, PACK_PY, "info", REL))
    print(run(VENV_PY, PACK_PY, "list", REL))
    print("wrote", REL)


if __name__ == "__main__":
    main()
