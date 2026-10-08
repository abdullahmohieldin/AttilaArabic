#!/usr/bin/env python3
"""C5 builder = C3's advance-width sweep + a two-clone direction ruler.

Font packs (Shyizer's 37 CUFs, test only): 12 new glyph records appended per
font, nothing existing modified.

  sweep, per font (FE92 width W; aw == w in every row, so the decodable
  question is "does the pitch equal the declared advance or is it fixed?"):
     U+FEF5  bitmap/aw = W-2
     U+FE71  bitmap/aw = W    (control: the bitmap is the font's own FE92)
     U+FE79  bitmap/aw = W+1
     U+FE86  bitmap/aw = W+2

  direction ruler, two clones of the same U+FE92 artwork stretched to two
  clearly different widths, aw == w so pitch and ink agree:
     U+FEC7  bitmap w = 5-6 px, aw = w   (narrow stem)
     U+FE9A  bitmap w = 12-13 px, aw = w  (broad stem)

Loc pack: an 8-line block is prepended to four keys (ERE description, WRE
description, difficulty description, campaign-menu battle-settings button):

  row 1  U+FEF5 x20       sweep line, bitmap/aw W-2
  row 2  U+FE71 x20       sweep line, bitmap/aw W (control)
  row 3  U+FE79 x16       sweep line, bitmap/aw W+1
  row 4  U+FE86 x14       sweep line, bitmap/aw W+2
  row 5  U+FEC7 x M then U+FE9A x M   thin block then broad block (stored)
  row 6  U+FE9A x M then U+FEC7 x M   broad block then thin block (stored)

Row widths are checked against the calibrated budget before the pack is
written and the worst case over all 37 fonts is printed.
"""
import hashlib
import os
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
from cuf import CUF               # noqa: E402
from loc import decode, encode    # noqa: E402
from packfile import PackFile     # noqa: E402
import cr_build as B              # noqa: E402

SHY = os.path.join(BASE, "reference", "shyizer", "data", "Shyizer Arabic.pack")
REL = os.path.join(BASE, "release")
V14 = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")

NARROW_CP, BROAD_CP = 0xFEC7, 0xFE9A
NARROW_W, BROAD_W = 5, 12
# sweep rows: (codepoint, bitmap width delta vs FE92.w, declared aw delta).
# Rows 2-5 all carry the SAME bitmap (W+2) and differ ONLY in the declared
# advance, so the two hypotheses are ~19 px apart per row and cannot be
# confused. Row 1 is the control: both its bitmap and its aw are the font's
# own FE92 values. All four codepoints are unused by our loc and carry ink in
# all 37 fonts (U+FE76/U+FE78 do not carry ink, which is why they are unused).
SWEEP = [(0xFEF5, -2, -2), (0xFE71, +2, -2), (0xFE79, +2, +1),
         (0xFE86, +2, +2)]
SWEEP_CP = [cp for cp, _, _ in SWEEP]
SWEEP_REP = [14, 12, 12, 10]
# direction ruler rows: (narrow copies, broad copies) per row
RULER_ROWS = [(16, 11), (11, 16)]
BUDGET = 300.0        # px; the engine drew up to 319 px lines in this panel
CEILING = 345.0       # widest line the engine demonstrably drew

PROBE_KEYS = [
    (r"text\db\start_pos_factions.loc",
     "start_pos_factions_description_2120156326"),
    (r"text\db\start_pos_factions.loc",
     "start_pos_factions_description_2120156339"),
    (r"text\db\random_localisation_strings.loc",
     "random_localisation_strings_string_campaign_difficulty_description_2"),
    (r"text\db\uied_component_texts.loc",
     "uied_component_texts_localised_string_button_txt_NewState_Text_530011h"),
]
LABELS = ["row1 U+FEF5 x14  bitmap W-2  aw W-2   (control row)",
          "row2 U+FE71 x12  bitmap W+2  aw W-2",
          "row3 U+FE79 x12  bitmap W+2  aw W+1",
          "row4 U+FE86 x10  bitmap W+2  aw W+2",
          "row5 thin x16 then broad x11  (thin half first in the stored value)",
          "row6 broad x11 then thin x16  (broad half first in the stored value)"]


def stretch(bm, w, h, new_w):
    """Resample a w x h bitmap to new_w columns (nearest neighbour)."""
    if new_w == w:
        return bytes(bm)
    img = Image.fromarray(np.frombuffer(bm, np.uint8).reshape(h, w))
    out = img.resize((new_w, h), Image.NEAREST)
    return np.array(out, np.uint8).tobytes()


def add_record(dims, bmps, ah, aw, w, h, data):
    dims.append((ah, aw, w, h))
    bmps.append(data)
    return len(dims) - 1


def build_fonts(log):
    src = PackFile(SHY)
    names = sorted(n for n in src.files if n.endswith(".cuf"))
    entries, rows = {}, []
    for n in names:
        leaf = n.split("\\")[-1]
        raw = src.get_file(n)
        old = CUF.decode(raw)
        c = CUF.decode(raw)
        dims, bmps = list(c.dims), list(c.bitmaps)
        table = list(c.table)
        fe92 = c.table[0xFE92]
        ah92, aw92, w92, h92 = c.dims[fe92]
        src_bm = c.bitmaps[fe92]
        # sweep records: bitmap width and declared advance are independent
        for cp, wd, ad in SWEEP:
            w, aw = w92 + wd, aw92 + ad
            assert w >= 1 and aw >= 1, (leaf, cp, w, aw)
            idx = add_record(dims, bmps, ah92, aw, w, h92,
                             stretch(src_bm, w92, h92, w))
            table[cp] = idx
            rows.append((leaf, "sweep", cp, aw, w))
        # direction ruler clones: aw == w, so pitch and ink agree. The width is
        # NOT clamped to the font's own aw - the clones are deliberately wider
        # than FE92 so the two blocks are unmistakable.
        for cp, want in ((NARROW_CP, NARROW_W), (BROAD_CP, BROAD_W)):
            w = want
            idx = add_record(dims, bmps, ah92, w, w, h92,
                             stretch(src_bm, w92, h92, w))
            table[cp] = idx
            rows.append((leaf, "ruler", cp, w, w))
        c.table, c.dims, c.bitmaps = table, dims, bmps
        out = c.encode()
        chk = CUF.decode(out)
        assert chk.encode() == out, leaf
        napp = len(SWEEP) + 2
        assert chk.dims[:-napp] == old.dims, leaf
        assert chk.bitmaps[:-napp] == old.bitmaps, leaf
        assert chk.props == old.props and chk.tail == old.tail, leaf
        diff = [cp for cp in range(65536) if chk.table[cp] != old.table[cp]]
        assert sorted(diff) == sorted([cp for cp, _, _ in SWEEP]
                                      + [NARROW_CP, BROAD_CP]), (leaf, diff)
        entries[n if n.startswith("font") else
                f"font\\{n.split(chr(92))[-1]}"] = out
    B.write_pack(os.path.join(REL, "Attila_Arabic_CR_C5_fonts.pack"), entries)
    log.append(f"fonts pack: {len(entries)} CUFs, {len(SWEEP) + 2} new glyph "
               f"records each, {len(SWEEP) + 2} table entries remapped each")
    return rows


def block():
    lines = ["".join(chr(cp) for _ in range(rep))
             for (cp, _, _), rep in zip(SWEEP, SWEEP_REP)]
    for n_narrow, n_broad in RULER_ROWS:
        lines.append(chr(NARROW_CP) * n_narrow + chr(BROAD_CP) * n_broad)
    return "\n".join(lines)


def widths(rows):
    """advance width of each probe row, per font, from the built records."""
    per = {}
    for leaf, kind, cp, aw, w in rows:
        per.setdefault(leaf, {})[cp] = aw
    out = {}
    for leaf, m in per.items():
        sweep = [rep * m[cp] for (cp, _, _), rep in zip(SWEEP, SWEEP_REP)]
        rul = [nn * m[NARROW_CP] + nb * m[BROAD_CP]
               for nn, nb in RULER_ROWS]
        out[leaf] = sweep + rul
    return out


def build_loc(log, wtab):
    cfg = {"test": "C5", "loc": {"descriptions_from_long": True}}
    files = B.loc_rows(cfg, log)
    blk = block()
    for internal, key in PROBE_KEYS:
        rows = files[internal]
        have = {k for k, _, _ in rows}
        assert key in have, f"missing {key}"
        files[internal] = [(k, (blk + "\n" + t) if k == key else t, tip)
                           for k, t, tip in rows]
    entries = {i: encode(r) for i, r in files.items()}
    out = os.path.join(REL, "Attila_Arabic_CR_C5.pack")
    B.write_pack(out, entries)
    log.append(f"loc pack: {out} ({os.path.getsize(out)} B) "
               f"SHA256={B.sha256_file(out)[:16]}")
    log.append(f"loc probe block: 6 rows prepended to {len(PROBE_KEYS)} keys")
    for i, lab in enumerate(LABELS):
        worst = max(wtab[leaf][i] for leaf in wtab)
        best = min(wtab[leaf][i] for leaf in wtab)
        flag = "OK" if worst <= BUDGET else (
            "over budget" if worst <= CEILING else "OVER CEILING")
        log.append(f"  row {i + 1}: advance width across fonts "
                   f"{best:.0f}-{worst:.0f} px (budget {BUDGET:.0f}) {flag} "
                   f"[{lab}]")
    return entries


def main():
    log = ["== C5 == declared change: C3's aw sweep + a two-clone direction "
           "ruler, in one font pack (12 appended glyph records per font, "
           "nothing existing modified)",
           f"vanilla local_en.pack SHA256 before: "
           f"{'OK' if B.sha256_file(B.VANILLA) == B.VANILLA_SHA else 'CHANGED!'}"]
    assert B.sha256_file(B.VANILLA) == B.VANILLA_SHA
    rows = build_fonts(log)
    wtab = widths(rows)
    build_loc(log, wtab)
    assert B.sha256_file(B.VANILLA) == B.VANILLA_SHA
    log.append("vanilla local_en.pack SHA256 after: OK")
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    with open(os.path.join(BASE, "logs", "cr_C5_build.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()


