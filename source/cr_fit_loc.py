#!/usr/bin/env python3
"""Definitive per-surface pitch fit using the exact loc strings.

For each measured surface the script reads the real loc value out of the v14
pack, reverses it (the engine reverses our visual-order string back to logical
for display, which mirrors each rendered line), fits font/scale/model, and then
fits the advance of U+FE92 / U+FEF2 by 0.5 px search.
"""
import os
import sys

import numpy as np

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R      # noqa: E402
import cr_fit as F         # noqa: E402
from loc import decode     # noqa: E402
from packfile import PackFile  # noqa: E402

PF = R.PackFile(R.SHY)
R._cache = {}


def font(leaf):
    if leaf not in R._cache:
        name = next(n for n in PF.files if n.endswith(leaf))
        R._cache[leaf] = R.CUF.decode(PF.get_file(name))
    return R._cache[leaf]


R.font = font
ALL_FONTS = sorted(n.split("\\")[-1] for n in PF.files if n.endswith(".cuf"))
V14 = PackFile(os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack"))
LOC = {}
for internal in (r"text\db\uied_component_texts.loc",
                 r"text\db\factions.loc",
                 r"text\db\start_pos_factions.loc",
                 r"text\db\random_localisation_strings.loc",
                 r"text\db\land_units.loc",
                 r"text\db\ui_unit_stats.loc"):
    rows = decode(V14.get_file(internal))[0]
    LOC.update({k: t for k, t, _ in rows})


def visual(key, line=None):
    """stored value -> the string the engine will draw for that line.

    The engine draws our visual-order value mirrored back to logical order,
    i.e. reversed; so the visual string for our renderer is reverse(stored).
    """
    t = LOC[key]
    if line is not None:
        return t.split("\n")[line][::-1]
    return t[::-1]


SURFACES = [
    ("ERE faction title", "06.52.20.33", (872, 95, 1045, 128), "light", 180,
     lambda: visual("factions_screen_name_att_fact_eastern_roman_empire")),
    ("WRE faction title", "06.52.22.90", (872, 95, 1045, 128), "light", 180,
     lambda: visual("factions_screen_name_att_fact_western_roman_empire")),
    ("choose-faction TITLE", "06.52.20.33", (872, 95, 1045, 130), "light", 180,
     "\uFEE7\uFEDB\uFE8D \uFEDF\uFEF4\uFEBC\uFEE0\uFE8E"),
    ("choose-faction BUTTON", "06.52.36.59", (880, 88, 1110, 130), "light", 180,
     lambda: visual("uied_component_texts_localised_string_tx_header_NewState_Text_530011")),
    ("custom battle btn", "06.52.27.49", (155, 606, 296, 634), "light", 180,
     lambda: visual("uied_component_texts_localised_string_button_txt_NewState_Text_36000f")),
    ("custom battle hdr", "06.52.36.59", (885, 92, 1100, 127), "light", 180,
     lambda: visual("uied_component_texts_localised_string_tx_header_NewState_Text_530011")),
    ("campaign menu btn", "06.52.25.78", (128, 686, 330, 712), "light", 180,
     lambda: visual("uied_component_texts_localised_string_button_txt_NewState_Text_530011h")),
    ("diff box line0", "06.52.20.33", (1275, 300, 1560, 330), "light", 180,
     lambda: visual("random_localisation_strings_string_campaign_difficulty_description_2", 0)),
    ("diff box line1", "06.52.20.33", (1275, 330, 1560, 360), "light", 180,
     lambda: visual("random_localisation_strings_string_campaign_difficulty_description_2", 1)),
    ("ERE desc L0", "06.52.20.33", (390, 630, 715, 660), "dark", 120,
     lambda: visual("start_pos_factions_description_2120156326", 0)),
    ("ERE desc L1", "06.52.20.33", (390, 660, 715, 690), "dark", 120,
     lambda: visual("start_pos_factions_description_2120156326", 1)),
]

INTEREST = (0xFE92, 0xFEF2)


def fit_surface(name, ts, box, mode, thr, text, fonts, scales):
    me = F.measured_mask(ts, *box, mode=mode, thr=thr)
    res = []
    for leaf in fonts:
        c = font(leaf)
        for model in ("aw", "w"):
            for s in scales:
                for tax in (0, 1, 2):
                    for yo in (1, 3, 5):
                        canvas, _pens, total = F.render(c, text, s, tax, model,
                                                        yo)
                        r = F.fit(me, canvas)
                        if r is None:
                            continue
                        res.append((r[0], leaf, model, s, tax, yo, total))
    res.sort(key=lambda r: r[0])
    print(f"\n=== {name} {ts} box={box} ink={int(me.sum())} text={text!r}")
    print(f"  {'err':>6} {'font':30s} {'model':4s} {'scale':5s} {'tax':3s} "
          f"{'yoff':4s} width")
    for r in res[:6]:
        print(f"  {r[0]:6d} {r[1]:30s} {r[2]:4s} {r[3]:5.2f} {r[4]:3d} "
              f"{r[5]:4d} {r[6]:6.1f}")
    if not res:
        return None
    err, leaf, model, s, tax, yo, total = res[0]
    c = font(leaf)
    out = {"name": name, "font": leaf, "model": model, "scale": s, "tax": tax,
           "yoff": yo, "err": err, "width": total, "ink": int(me.sum())}
    for cp in INTEREST:
        idx = None
        for k, ch in enumerate(text):
            if ord(ch) == cp:
                idx = k
                break
        i = c.table[cp]
        ah, aw, w, h = c.dims[i]
        if idx is None:
            out[f"cp{cp:X}"] = None
            print(f"    U+{cp:04X}: aw={aw} w={w} (not in this string)")
            continue
        best = None
        for a in np.arange(max(0.5, (aw * s) - 6), (aw * s) + 7, 0.5):
            canvas, _p, _t = F.render(c, text, s, tax, model, yo,
                                      adv_override={idx: float(a)})
            r = F.fit(me, canvas)
            if r and (best is None or r[0] < best[0]):
                best = (r[0], float(a))
        if best:
            out[f"cp{cp:X}"] = best[1]
            print(f"    U+{cp:04X}: aw={aw} w={w} aw*scale={aw * s:.1f} "
                  f"-> fitted advance {best[1]:.1f} px (err {best[0]})")
    return out


if __name__ == "__main__":
    scales = [round(0.40 + 0.02 * i, 2) for i in range(81)]
    fonts = sys.argv[1:] or ALL_FONTS
    rows = []
    for name, ts, box, mode, thr, getter in SURFACES:
        try:
            if isinstance(getter, str):
                text = getter
            else:
                text = getter()
        except KeyError as e:
            print(f"{name}: missing key {e}")
            continue
        rows.append(fit_surface(name, ts, box, mode, thr, text, fonts, scales))
    print("\n=== summary")
    for r in rows:
        if r:
            print(f"  {r['name']:20s} font={r['font']:28s} {r['model']} "
                  f"scale={r['scale']:.2f} tax={r['tax']} err={r['err']} "
                  f"FE92={r.get('cpFE92')} FEF2={r.get('cpFEF2')}")
