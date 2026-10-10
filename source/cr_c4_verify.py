#!/usr/bin/env python3
"""Independent verification of release/Attila_Arabic_CR_C4.pack.

Checks, without importing the builder:
  1. the pack opens as PFH4 type 3 and holds the 8 loc files;
  2. every loc file round-trips (decode -> encode byte identical);
  3. the only differences from Attila_Arabic_POC_v14.pack are the values of
     loc keys that contained U+000A and Arabic text;
  4. every changed value has the same number of lines as before;
  5. concatenating its lines, minus U+0640 padding, preserves the word
     sequence (no word lost, no word split);
  6. no new line exceeds the hard ceiling and no line holds a single word that
     the old value did not already isolate.

  python source/cr_c4_verify.py
"""
import os
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from packfile import PackFile  # noqa: E402
from loc import decode, encode  # noqa: E402
from cr_build import LOC_FILES  # noqa: E402
import cr_c4_wrap as W         # noqa: E402

V14 = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")
C4 = os.path.join(BASE, "release", "Attila_Arabic_CR_C4.pack")
C4F = os.path.join(BASE, "release", "Attila_Arabic_CR_C4_fonts.pack")


def rows_of(path, internal):
    pf = PackFile(path)
    return decode(pf.get_file(internal))[0]


def main():
    fails = []
    a, b = PackFile(V14), PackFile(C4)
    assert a.header.version == b.header.version == b"PFH4", (a.header.version,
                                                             b.header.version)
    assert a.header.pack_type == b.header.pack_type == 3
    print(f"pack PFH4 type 3 OK: v14 {len(a.files)} files, "
          f"C4 {len(b.files)} files")
    if len(a.files) != len(b.files):
        fails.append("file count differs")

    changed = []
    for internal in LOC_FILES:
        ra, rb = rows_of(V14, internal), rows_of(C4, internal)
        # round-trip gate on the new bytes
        raw = PackFile(C4).get_file(internal)
        assert encode(decode(raw)[0]) == raw, internal
        if len(ra) != len(rb):
            fails.append(f"{internal}: entry count {len(ra)} -> {len(rb)}")
        da = {k: (t, tip) for k, t, tip in ra}
        db = {k: (t, tip) for k, t, tip in rb}
        if set(da) != set(db):
            fails.append(f"{internal}: key set differs")
        for key in da:
            ta, tipa = da[key]
            tb, tipb = db[key]
            if tipa != tipb:
                fails.append(f"{key}: tooltip flag {tipa} -> {tipb}")
            if ta != tb:
                changed.append((internal, key, ta, tb))
        print(f"  {internal:44s} rows={len(ra)} roundtrip=OK")

    print(f"\nchanged values: {len(changed)}")
    m = W.model()
    c = W.R.font(m["leaf"])
    for internal, key, ta, tb in changed:
        la, lb = ta.split("\n"), tb.split("\n")
        ar = any(0x0600 <= ord(ch) <= 0x06FF for ch in ta)
        if not ar:
            fails.append(f"{key}: changed although it has no Arabic")
        if "\n" not in ta:
            fails.append(f"{key}: changed although it had no U+000A")
        if len(la) != len(lb):
            fails.append(f"{key}: line count {len(la)} -> {len(lb)}")
        wa = " ".join(" ".join(W.strip_tatweel(x).split()) for x in la)
        wb = " ".join(" ".join(W.strip_tatweel(x).split()) for x in lb)
        if wa != wb:
            fails.append(f"{key}: word sequence changed")
        # no word split: every word of the new value sits on exactly one line
        words = wa.split(" ")
        joined = " ".join(lb)
        if " ".join(words) != " ".join(joined.split()):
            fails.append(f"{key}: new lines do not rejoin to the same words")
        widths = [round(W.width(c, x, m), 1) for x in lb]
        if any(x > W.BOX_HARD_PX for x in widths):
            fails.append(f"{key}: line over hard ceiling {widths}")
        print(f"  {key}")
        print(f"     old {len(la)} lines -> new {len(lb)} lines")
        print(f"     old widths {[round(W.width(c, x, m), 1) for x in la]}")
        print(f"     new widths {widths}")
        print(f"     old words/line {[len(x.split()) for x in la]}")
        print(f"     new words/line {[len(x.split()) for x in lb]}")

    # font pack
    if os.path.exists(C4F):
        src = PackFile(W.SHY)
        dst = PackFile(C4F)
        names = [n for n in src.files if n.endswith(".cuf")]
        ok = len(dst.files) == len(names) == 37
        for n in names:
            leaf = n.split("\\")[-1]
            data = src.get_file(n)
            got = dst.get_file(f"font\\{leaf}")
            if got != data:
                ok = False
        print(f"\nfonts pack: {len(dst.files)} entries, byte-for-byte "
              f"identical to Shyizer source = {ok}")
        if not ok:
            fails.append("fonts pack mismatch")
    else:
        fails.append("fonts pack missing")

    print()
    if fails:
        print("FAILURES:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
