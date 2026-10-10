#!/usr/bin/env python3
"""Dump the loc text of the keys used by the C1 measurement, plus Shyizer's
per-font (aw,w) for the codepoints of interest."""
import os
import sys

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF               # noqa: E402
from loc import decode            # noqa: E402
from packfile import PackFile     # noqa: E402

V14 = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")
SHY = os.path.join(BASE, "reference", "shyizer", "data", "Shyizer Arabic.pack")

KEYS = {
    r"text\db\start_pos_factions.loc": [
        "start_pos_factions_description_2120156326",
        "start_pos_factions_description_2120156339"],
    r"text\db\random_localisation_strings.loc": [
        "random_localisation_strings_string_campaign_difficulty_description_2"],
    r"text\db\uied_component_texts.loc": [
        "uied_component_texts_localised_string_tx_header_NewState_Text_530011",
        "uied_component_texts_localised_string_button_txt_NewState_Text_36000f",
        "uied_component_texts_localised_string_button_txt_NewState_Text_530011h"],
    r"text\db\factions.loc": [
        "factions_screen_name_att_fact_eastern_roman_empire",
        "factions_screen_name_att_fact_western_roman_empire"],
}


def show_text():
    pf = PackFile(V14)
    for internal, keys in KEYS.items():
        rows = decode(pf.get_file(internal))[0]
        d = {k: t for k, t, _ in rows}
        for k in keys:
            t = d[k]
            print(f"--- {k}")
            for i, line in enumerate(t.split("\n")):
                cps = " ".join(f"{ord(c):04X}" for c in line)
                print(f"  L{i:02d} len={len(line):3d} {line!r}")
                print(f"       {cps}")


def shyizer_metrics():
    src = PackFile(SHY)
    names = sorted(n for n in src.files if n.endswith(".cuf"))
    cps = [0xFE92, 0xFE8D, 0xFE8E, 0xFEF2, 0xFE98, 0xFE9C, 0xFEF4, 0xFEE7,
           0x0020]
    print("\nfont aw/w/h (ah) per codepoint   [Shyizer]")
    hdr = "  {:38s}".format("font") + "".join(f"{c:>14X}" for c in cps)
    print(hdr)
    for n in names:
        c = CUF.decode(src.get_file(n))
        row = "  {:38s}".format(n.split("\\")[-1])
        for cp in cps:
            i = c.table[cp]
            if i == 0xFFFF or i >= c.count:
                row += f"{'--':>14s}"
            else:
                ah, aw, w, h = c.dims[i]
                row += f"{f'{aw}/{w}/{h}':>14s}"
        print(row)
    print("  (aw/w/h; h=bitmap height, ah=alloc_height)")
    print("\nkerning tails:")
    for n in names:
        c = CUF.decode(src.get_file(n))
        print(f"  {n.split(chr(92))[-1]:38s} {c.parse_tail()}")


if __name__ == "__main__":
    show_text()
    if "--fonts" in sys.argv:
        shyizer_metrics()
