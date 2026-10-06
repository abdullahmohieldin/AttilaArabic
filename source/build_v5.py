#!/usr/bin/env python3
"""Build v5 POC: full Arabic font merge with exact baseline-aligned glyph placement.

Fixes the vertical baseline jitter bug:
Each glyph's ink is placed so that its font baseline stroke aligns with the
vanilla font's common baseline row (vm["bottom"]), ensuring tall letters
(alef, lam), short letters (dal, seen), and descenders (reh, jeem, waw)
retain their exact natural vertical offsets on a single flat baseline.

Outputs:
  - build/v5fonts/*.cuf (31 merged fonts)
  - release/Attila_Arabic_POC_v5_fonts.pack
  - docs/test-pack-manifest-v5.md
  - logs/v5_build.txt
"""
import hashlib
import os
import subprocess
import sys
import unicodedata
from fontTools.ttLib import TTFont
from PIL import ImageFont

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cuf import CUF  # noqa: E402

VENV_PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
PACK_PY = os.path.join(BASE, "tools", "packfile.py")
VANILLA_PACK = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"
TAJAWAL = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")

FONTS_BUILD = os.path.join(BASE, "build", "v5fonts")
FONTS_PACK = os.path.join(BASE, "release", "Attila_Arabic_POC_v5_fonts.pack")

SIZES_GIOC = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38]
SIZES_GEORG = [10, 12, 14, 16, 18]
TARGETS = ([f"la_gioconda_{s}" for s in SIZES_GIOC]
           + [f"la_gioconda_uppercase_{s}" for s in SIZES_GIOC]
           + [f"georgia_italic_{s}" for s in SIZES_GEORG])

OVER = 2  # v3b_big cell headroom


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{args}\n{r.stderr[-2000:]}")
    return r.stdout


def base_letter(cp):
    try:
        decomp = unicodedata.decomposition(chr(cp))
    except Exception:
        return None
    parts = decomp.split()
    if len(parts) >= 2 and parts[0].startswith("<"):
        try:
            return int(parts[1], 16)
        except ValueError:
            return None
    return None


def vanilla_metrics(c):
    code = c.table[0x48]
    ah, aw, w, h = c.dims[code]
    d = c.bitmaps[code]
    rows = [y for y in range(h) if any(d[y * w + x] > 20 for x in range(w))]
    top, bottom = min(rows), max(rows)
    return {
        "cap": bottom - top + 1,
        "top": top,
        "bottom": bottom,
        "cell_h": h,
        "vsize": c.props["v_size"],
    }


def calibrate(vanilla_h_cap, lo=8, hi=64):
    best, bestpx = None, None
    for px in range(lo, hi + 1):
        f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        h = f.getbbox("H")[3] - f.getbbox("H")[1]
        if best is None or abs(h - vanilla_h_cap) < best:
            best, bestpx = abs(h - vanilla_h_cap), px
    return bestpx


def build_fonts(log):
    os.makedirs(FONTS_BUILD, exist_ok=True)
    cmap = TTFont(TAJAWAL).getBestCmap()

    # Full target Arabic set
    target_cps = set()
    target_cps.update(range(0x0621, 0x064B))  # Basic letters
    target_cps.add(0x0640)  # Tatweel
    target_cps.update(range(0x064B, 0x0653))  # Harakat
    target_cps.add(0x0670)  # Superscript alef
    target_cps.update([0x060C, 0x061B, 0x061F, 0x066A, 0x066B, 0x066C, 0x06D4])  # Punctuation
    target_cps.update(range(0x0660, 0x066A))  # Digits 0-9
    target_cps.update(range(0xFB50, 0xFE00))  # Forms-A
    target_cps.update(range(0xFE70, 0xFF00))  # Forms-B

    decomp_harakat = {
        0xFE70: 0x064B, 0xFE72: 0x064C, 0xFE74: 0x064D, 0xFE76: 0x064E,
        0xFE78: 0x064F, 0xFE7A: 0x0650, 0xFE7C: 0x0651, 0xFE7E: 0x0652,
    }

    src_of = {}
    missing = []
    for cp in sorted(target_cps):
        if cp in decomp_harakat:
            src_of[cp] = chr(decomp_harakat[cp])
        elif cp in cmap:
            src_of[cp] = chr(cp)
        else:
            b = base_letter(cp)
            if b is not None and b in cmap:
                src_of[cp] = chr(b)
            else:
                missing.append(cp)

    log.append(f"Tajawal-Regular.ttf FULL Arabic set: {len(src_of)} sourceable codepoints")
    log.append(f"Unmapped / non-standard in range: {len(missing)} codepoints")

    for name in TARGETS:
        src = os.path.join(BASE, "extracted", "fonts", name + ".cuf")
        c = CUF.decode(open(src, "rb").read())
        assert c.bitmap_total() == c.size, name
        vm = vanilla_metrics(c)
        V = vm["cell_h"]
        baseline_row = vm["bottom"]  # Common baseline row for all glyphs
        px_cap = calibrate(vm["cap"])

        # Choose px (start at cap-match, reduce if necessary to fit cell + OVER)
        chosen = None
        for px in range(px_cap, 7, -1):
            f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
            ascent, _ = f.getmetrics()
            ok = True
            for cp, ch in src_of.items():
                bbox = f.getbbox(ch)
                if not bbox:
                    continue
                bx0, by0, bx1, by1 = bbox
                top = baseline_row + by0 - ascent + 1
                bot = baseline_row + by1 - ascent + 1
                if top < -OVER or bot > V + OVER:
                    ok = False
                    break
            if ok:
                chosen = px
                break

        assert chosen is not None, f"{name}: no fitting px"
        px = chosen

        f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
        ascent, descent = f.getmetrics()

        dangling = sorted({v for v in c.table if v != 0xFFFF and v >= len(c.dims)})
        new_dims = list(c.dims)
        new_maps = list(c.bitmaps)
        for dcode in dangling:
            while len(new_dims) < dcode:
                raise AssertionError((name, dcode))
            new_dims.append((-128, 0, 0, 0))
            new_maps.append(b"")

        added = {}
        for cp in sorted(src_of.keys()):
            ch = src_of[cp]
            mask = f.getmask(ch, mode="L")
            mw, mh = mask.size
            data = bytes(mask)
            adv = int(round(f.getlength(ch)))
            bbox = f.getbbox(ch)

            if not bbox or not any(data):
                adv_out = max(adv, 4)
                new_dims.append((V, adv_out, adv_out, V))
                new_maps.append(bytes(V * adv_out))
                added[cp] = len(new_dims) - 1
                continue

            bx0, by0, bx1, by1 = bbox

            # Rule: place glyph ink aligning its baseline to baseline_row
            top = baseline_row + by0 - ascent + 1
            bot = top + mh
            ctop = min(top, 0)
            cbot = max(bot, V)
            chh = cbot - ctop
            left = bx0 if bx0 >= 0 else 0
            adv_out = max(adv, left + mw)
            cw = adv_out

            cell = bytearray(chh * cw)
            for y in range(mh):
                cy = top - ctop + y
                if 0 <= cy < chh:
                    cell[cy * cw + left : cy * cw + left + mw] = data[y * mw : (y + 1) * mw]

            code = len(new_dims)
            # alloc_h = chh == h (matches vanilla CUF rule across all fonts)
            new_dims.append((chh if chh < 128 else 127, adv_out, cw, chh))
            new_maps.append(bytes(cell))
            added[cp] = code

        table = list(c.table)
        for cp, code in added.items():
            table[cp] = code
        c.table = table
        c.dims = new_dims
        c.bitmaps = new_maps

        out = c.encode()
        c2 = CUF.decode(out)
        assert c2.encode() == out, f"{name} unstable"
        out_path = os.path.join(FONTS_BUILD, name + ".cuf")
        with open(out_path, "wb") as f:
            f.write(out)

        maxh = max(h for (_, _, _, h) in new_dims[len(new_dims) - len(added):])
        log.append(
            f"{name}: px={px} cell={V} maxcell={maxh} baseline_row={baseline_row} "
            f"vanilla_codes={len(c.dims) - len(added) - len(dangling)} "
            f"+blanks={len(dangling)} +arabic={len(added)} size={len(out)}B"
        )

    # Package into v5 fonts pack
    tmp_pack = os.path.join(BASE, "build", "v5_fonts_tmp.pack")
    run(VENV_PY, PACK_PY, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in TARGETS:
        run(VENV_PY, PACK_PY, "add", tmp_pack, f"font\\{name}.cuf", os.path.join(FONTS_BUILD, f"{name}.cuf"))
    run(VENV_PY, PACK_PY, "set-type", tmp_pack, "3", "--output", FONTS_PACK)
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    log.append(f"Wrote fonts pack: {FONTS_PACK} ({os.path.getsize(FONTS_PACK)} B, SHA256={sha256_file(FONTS_PACK)})")


def main():
    log = []
    # Rule: Hash vanilla BEFORE build
    sha_before = sha256_file(VANILLA_PACK)
    assert sha_before == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch before build: {sha_before}"
    log.append(f"Vanilla local_en.pack SHA256 verified BEFORE build: {sha_before}")

    print("Building v5 full Arabic fonts with exact baseline alignment...")
    build_fonts(log)

    # Rule: Hash vanilla AFTER build
    sha_after = sha256_file(VANILLA_PACK)
    assert sha_after == EXPECTED_VANILLA_SHA, f"Vanilla hash mismatch after build: {sha_after}"
    log.append(f"Vanilla local_en.pack SHA256 verified AFTER build: {sha_after}")

    # Check v5 fonts with v3_check
    print("Running v3_check on v5 fonts...")
    check_out = run(
        VENV_PY,
        os.path.join(BASE, "source", "v3_check.py"),
        FONTS_BUILD,
        os.path.join(BASE, "localization", "corpus_v4.txt"),
    )
    log.append("=== v3_check output ===")
    log.append(check_out)

    log_path = os.path.join(BASE, "logs", "v5_build.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print(f"Build complete. Log written to {log_path}")


if __name__ == "__main__":
    main()
