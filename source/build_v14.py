#!/usr/bin/env python3
"""Build v14 (round 14): universal join fix + tatweel pads + offline QA.

Base: v11 packs (NOT v13; v13 probe bitmaps rebuilt via the universal rule).
Vanilla local_en.pack verified SHA256 before AND after (never modified).

FONTS (v14_fonts): ALL 31 CUFs. For every REAL Arabic presentation-form
glyph (FB50-FDFF, FE70-FEFF minus FE70-FE7F harakat) with ink:
  MEDIAL -> join rows solid 255 across 0..new_w-1 (both sides join)
  INITIAL -> join rows solid from x=0 to row ink end (joins screen-left only)
  FINAL   -> join rows solid from row ink start to new_w-1 (joins screen-right)
  new_w = w+1 (w<=10) else w+2; other glyphs byte-identical.
  Join rows = rows touching the join side AND width >= max_row_width-1
  (dots excluded; verified offline). All other pixels (dots/stems/AA) kept.
  U+0640 TATWEEL -> blank bitmap in all 31 CUFs (right-align spacer).
  v11 FE92/FE8D/FEF2 tweaks are absorbed/replaced by the rule above.

LOC (v14): ERE/WRE description_ = REAL texts (v7 logicals), wrapped with
ENGINE advances to 350px (box=359 per layout Text record, screenshot-confirmed
~365), shaped per line, tatweel-padded (A_TAT=16 HYPOTHESIS, conservative to
avoid clipping; residuals calibrate v15). long_ = real texts, NO pads.
Difficulties _0.._4 restored to v11 (probes concluded). Rest v11-identical.

OFFLINE QA (pre-pack gate, non-fatal): compose 11 Arabic strings LTR from the
NEW CUF bitmaps at engine advances; seam-ink metric per joining boundary vs
ideal-butted Tajawal reference; zoomed PNGs to logs/crops/v14/. Numbers logged.
"""
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import unicodedata

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))

from cuf import CUF        # noqa: E402
from loc import decode, encode  # noqa: E402
from packfile import PackFile  # noqa: E402
from shape import shape    # noqa: E402

V11_FONTS = os.path.join(BASE, "release", "Attila_Arabic_POC_v11_fonts.pack")
V11_PACK  = os.path.join(BASE, "release", "Attila_Arabic_POC_v11.pack")
FONTS_OUT = os.path.join(BASE, "release", "Attila_Arabic_POC_v14_fonts.pack")
LOC_OUT   = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")
VANILLA   = r"D:\SteamLibrary\steamapps\common\Total War Attila\data\local_en.pack"
EXPECTED_VANILLA_SHA = "45E0F0877B3A644F8C63352A6824416EEDBDC0B85A000E1189A2B05860A7F70D"
TAJAWAL   = os.path.join(BASE, "fonts", "upstream", "Tajawal-Regular.ttf")

INK_THRESH = 20
TAT = "\u0640"

# Measured engine advances (VERIFIED v9/v10/v13 screenshots). Everything else:
# ink_width + 3 (ink<=3 or ink>=9) else + 2 (fits all 4 calibrations).
MEASURED_ADV = {0xFE92: 8, 0xFE98: 8, 0xFE9C: 8, 0xFEF4: 8, 0xFE8D: 5,
                0xFE8E: 6, 0xFEF2: 12, 0x20: 5, 0xA0: 0.9, 0x2003: 6}
BOX_W, PAD_TARGET, A_TAT = 359, 350, 16.0  # layout+screenshot; HYPOTHESIS 16

KEY_ERE = "start_pos_factions_description_2120156326"
KEY_ERE_L = "start_pos_factions_long_description_2120156326"
KEY_WRE = "start_pos_factions_description_2120156339"
KEY_WRE_L = "start_pos_factions_long_description_2120156339"
DIFF = "random_localisation_strings_string_campaign_difficulty_description_"

WRE_LOGICAL = (
    "تقف الإمبراطورية الرومانية الغربية على شفا الانهيار والضياع. "
    "تنهش الحدود هجمات البرابرة المتواصلة، بينما ينخر الفساد السياسي والتمرد الداخلي في قلب الدولة. "
    "روما العظيمة لم تعد العاصمة، بل انتقل الحكم إلى ميديولانوم ورافينّا تحت وطأة التهديد. "
    "إن بقاء الإمبراطورية يتطلب قائداً حازماً يعيد الانضباط إلى الفيالق، ويثبت أركان الاقتصاد المتداعي، "
    "ويصد جحافل الغزاة قبل فوات الأوان."
)
ERE_LOGICAL = (
    "انقسام الإمبراطورية الرومانية أطلق العنان للشرق، وأتاح له الإمساك بزمام العالم الروماني. "
    "عاصمتها القسطنطينية مهيبة الأسوار وعقدة التجارة العالمية، وخزائنها عامرة بالذهب. "
    "ومع ذلك، فإن الخطر يحيط بها من كل جانب؛ فالساسانيون يتربصون بالحدود الشرقية، "
    "والقبائل المهاجرة تهدد مقاطعات البلقان. "
    "إن الحفاظ على هذا الإرث العظيم يتطلب دبلوماسية بارعة، وحملات عسكرية حاسمة، وجيوشاً لا تلين."
)

FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
    r"text\db\land_units.loc",
    r"text\db\faction_groups.loc",
    r"text\db\random_localisation_strings.loc",
    r"text\db\ui_unit_stats.loc",
    r"text\db\ui_unit_bullet_point_enums.loc",
]

QA_STRINGS = ["روما الغربية", "روما الشرقية", "الساسانيون", "اختر الفصيل",
              "معركة مخصصة", "هجوم الاشتباك", "الدرع", "صد المقذوفات",
              "مكافأة ضد الفرسان", "صعب: يتطلب تخطيطا",
              "الشرق يمسك بزمام العالم الروماني",
              "البحر الذين حبل موسى القاضي وجه"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def run(*args):
    subprocess.run(args, check=True)


def ink_bbox(bm, w, h):
    xs = [x for y in range(h) for x in range(w) if bm[y * w + x] > INK_THRESH]
    if not xs:
        return None
    return min(xs), max(xs)


def adv_model(cuf, ink_cache, cp):
    if cp in MEASURED_ADV:
        return MEASURED_ADV[cp]
    code = cuf.table[cp] if cp < 65536 else 0xFFFF
    if code == 0xFFFF or code >= len(cuf.dims):
        return 5.0
    ink = ink_cache.get(code, 0)
    if ink == 0:
        return 5.0
    return float(ink + (3 if (ink <= 3 or ink >= 9) else 2))


def classify(cp, bm, w, h):
    """-> kind in medial/initial/final/skip/tatweel (+reason)."""
    if cp == 0x0640:
        return "tatweel", ""
    if not (0xFB50 <= cp <= 0xFDFF or 0xFE70 <= cp <= 0xFEFF):
        return "skip", "out-of-range"
    if 0xFE70 <= cp <= 0xFE7F:
        return "skip", "harakat"
    if not any(b > INK_THRESH for b in bm):
        return "skip", "empty"
    nm = unicodedata.name(chr(cp), "")
    if "MEDIAL" in nm:
        return "medial", ""
    if "INITIAL" in nm:
        return "initial", ""
    if "FINAL" in nm:
        return "final", ""
    return "skip", nm.split(" ", 3)[-1] if nm else "noname"


def treat_glyph(dims, bm, kind):
    """Returns (new_dims, new_bitmap, info) or None when no join rows."""
    ah, aw, w, h = dims
    rows = [list(bm[y * w:(y + 1) * w]) for y in range(h)]
    bb = ink_bbox(bm, w, h)
    x0, x1 = bb
    widths = [sum(1 for v in r if v > INK_THRESH) for r in rows]
    maxw = max(widths)
    if kind == "medial":
        is_join = [(r[x0] > INK_THRESH and r[x1] > INK_THRESH) for r in rows]
        new_w = w + (1 if w <= 10 else 2)
        fill = (0, new_w)
    elif kind == "initial":
        is_join = [(r[x0] > INK_THRESH and widths[y] >= max(maxw - 1, 3)) for y, r in enumerate(rows)]
        new_w = w
        fill = None  # per-row 0..x1r
    else:  # final: join rows touch x1, mid-cell band (dots live top/bottom)
        is_join = [(r[x1] > INK_THRESH and widths[y] >= 2
                    and 0.15 * h <= y <= 0.85 * h) for y, r in enumerate(rows)]
        new_w = w + (1 if w <= 10 else 2)
        fill = None
    if not any(is_join):
        return None
    out = bytearray(new_w * h)
    for y in range(h):
        old = rows[y]
        for j in range(new_w):
            src = x0 + j
            out[y * new_w + j] = old[src] if src < w else 0
        if is_join[y]:
            if fill is not None:
                for j in range(fill[0], fill[1]):
                    out[y * new_w + j] = 255
            else:
                xs = [x for x in range(w) if old[x] > INK_THRESH]
                lo, hi = min(xs) - x0, max(xs) - x0
                if kind == "initial":
                    for j in range(0, hi + 1):
                        out[y * new_w + j] = 255
                else:
                    for j in range(lo, new_w):
                        out[y * new_w + j] = 255
    info = f"x0={x0} x1={x1} w={w}->{new_w} join={sum(is_join)}/{h}"
    return (ah, aw, new_w, h), bytes(out), info


def visual_width(visual, cuf, ink_cache):
    return sum(adv_model(cuf, ink_cache, ord(c)) for c in visual)


def wrap_engine(logical, cuf, ink_cache, width):
    lines, cur = [], []
    for word in logical.split(" "):
        cand = " ".join(cur + [word]) if cur else word
        if visual_width(shape(cand), cuf, ink_cache) <= width or not cur:
            cur.append(word)
        else:
            lines.append(shape(" ".join(cur)))
            cur = [word]
    if cur:
        lines.append(shape(" ".join(cur)))
    return lines


def main():
    log = []
    assert sha256_file(VANILLA) == EXPECTED_VANILLA_SHA
    log.append("vanilla SHA256 before: OK")

    # ---------------- fonts ----------------
    v11f = PackFile(V11_FONTS)
    assert len(v11f.files) == 31
    totals = {"medial": 0, "initial": 0, "final": 0, "tatweel": 0, "skip": 0}
    shifted, widened2, glyphs_changed = 0, 0, 0
    new_files = {}
    base_ink = {}  # font -> {code: v11 ink width} for the advance model
    for name in sorted(v11f.files):
        c = CUF.decode(v11f.get_file(name))
        old_bitmaps = list(c.bitmaps)
        old_dims = list(c.dims)
        ink_of = {}
        for i, bm in enumerate(c.bitmaps):
            ah, aw, w, h = c.dims[i]
            bb = ink_bbox(bm, w, h) if w and h else None
            ink_of[i] = (bb[1] - bb[0] + 1) if bb else 0
        base_ink[name] = ink_of
        changed = set()
        for cp in list(range(0xFB50, 0xFF00)) + [0x0640]:
            i = c.table[cp]
            if i >= len(c.dims):
                continue
            ah, aw, w, h = c.dims[i]
            if cp == 0x0640:
                assert w and h and any(b > INK_THRESH for b in c.bitmaps[i]), f"{name} tatweel empty"
                c.bitmaps[i] = bytes(w * h)
                changed.add(i)
                totals["tatweel"] += 1
                continue
            kind, why = classify(cp, c.bitmaps[i], w, h)
            if kind == "skip":
                totals["skip"] += 1
                continue
            res = treat_glyph(c.dims[i], c.bitmaps[i], kind)
            if res is None:
                log.append(f"  nojoin {name.split(chr(92))[-1]} U+{cp:04X}")
                totals["skip"] += 1
                continue
            nd, nb, info = res
            c.dims[i] = nd
            c.bitmaps[i] = nb
            changed.add(i)
            totals[kind] += 1
            if nd[2] == w + 2:
                widened2 += 1
            bb = ink_bbox(old_bitmaps[i], w, h)
            if bb and bb[0] > 2:
                shifted += 1
                log.append(f"  shift {name.split(chr(92))[-1]} U+{cp:04X} x0={bb[0]} {info}")
        for i in range(len(c.dims)):
            if i not in changed:
                assert c.dims[i] == old_dims[i] and c.bitmaps[i] == old_bitmaps[i], f"{name} glyph {i} drifted"
        glyphs_changed += len(changed)
        data = c.encode()
        assert CUF.decode(data).encode() == data, f"{name} unstable"
        new_files[name] = data
    log.append(f"surgery: medial={totals['medial']} initial={totals['initial']} "
               f"final={totals['final']} tatweel_blank={totals['tatweel']} skipped={totals['skip']}")
    assert totals["medial"] >= 300 and totals["initial"] >= 200 and totals["final"] >= 200, totals
    assert totals["tatweel"] == 31, totals
    log.append(f"surgery: {glyphs_changed} glyphs changed, {shifted} shifted-x0>2, {widened2} widened+2")

    tmpdir = os.path.join(BASE, "build", "v14_fonts")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir)
    for name in sorted(new_files):
        with open(os.path.join(tmpdir, name.split("\\")[-1]), "wb") as f:
            f.write(new_files[name])
    PY = os.path.join(BASE, "tools", "venv", "Scripts", "python.exe")
    PACK = os.path.join(BASE, "tools", "packfile.py")
    tmp_pack = os.path.join(BASE, "build", "v14f_tmp.pack")
    if os.path.exists(tmp_pack):
        os.remove(tmp_pack)
    run(PY, PACK, "create", tmp_pack, "--type", "3", "--version", "PFH4")
    for name in sorted(new_files):
        run(PY, PACK, "add", tmp_pack, name, os.path.join(tmpdir, name.split("\\")[-1]))
    run(PY, PACK, "set-type", tmp_pack, "3", "--output", FONTS_OUT)
    os.remove(tmp_pack)
    v14f = PackFile(FONTS_OUT)
    assert v14f.header.version == b"PFH4" and v14f.header.pack_type == 3
    log.append(f"v14_fonts SHA256: {sha256_file(FONTS_OUT)} ({os.path.getsize(FONTS_OUT)} B)")

    # ---------------- loc ----------------
    v11 = PackFile(V11_PACK)
    geo = CUF.decode(v14f.get_file("font\\georgia_italic_12.cuf"))
    ink_cache = dict(base_ink["font\\georgia_italic_12.cuf"])
    elines = wrap_engine(ERE_LOGICAL, geo, ink_cache, PAD_TARGET)
    wlines = wrap_engine(WRE_LOGICAL, geo, ink_cache, PAD_TARGET)
    log.append(f"wrap ERE: {len(elines)} lines " + ", ".join(f"{visual_width(l, geo, ink_cache):.0f}" for l in elines) + f"/{PAD_TARGET}")
    log.append(f"wrap WRE: {len(wlines)} lines " + ", ".join(f"{visual_width(l, geo, ink_cache):.0f}" for l in wlines) + f"/{PAD_TARGET}")

    def pad(lines, tag):
        out = []
        for i, ln in enumerate(lines):
            wpx = visual_width(ln, geo, ink_cache)
            n = max(0, int((PAD_TARGET - wpx) // A_TAT))
            n = min(n, 40)
            assert wpx + n * A_TAT <= PAD_TARGET + 1, f"{tag}_L{i} overflow"
            if wpx > PAD_TARGET:
                log.append(f"WARN {tag}_L{i}: width {wpx:.0f} > {PAD_TARGET} (no pad)")
            out.append(TAT * n + ln)
            log.append(f"PAD {tag}_L{i}: w={wpx:.0f} n={n}")
        return "\n".join(out)

    repl_spf = {KEY_ERE: pad(elines, "ERE"), KEY_WRE: pad(wlines, "WRE"),
                KEY_ERE_L: "\n".join(elines), KEY_WRE_L: "\n".join(wlines)}
    rows_r, p2, t2 = decode(v11.get_file(r"text\db\random_localisation_strings.loc"))
    assert p2 == t2
    d_r11 = {k: t for k, t, _ in rows_r}
    repl_r = {k: d_r11[k] for k in d_r11 if k.startswith(DIFF)}

    tmpdir2 = os.path.join(BASE, "build", "v14_loc")
    shutil.rmtree(tmpdir2, ignore_errors=True)
    os.makedirs(tmpdir2)
    for internal in FILES:
        raw = v11.get_file(internal)
        if internal == r"text\db\start_pos_factions.loc":
            rows, p, t = decode(raw)
            assert p == t
            open(os.path.join(tmpdir2, "start_pos_factions.loc"), "wb").write(encode(
                [(k, repl_spf.get(k, x), tip) for k, x, tip in rows]))
        elif internal == r"text\db\random_localisation_strings.loc":
            rows, p, t = decode(raw)
            assert p == t
            open(os.path.join(tmpdir2, "random_localisation_strings.loc"), "wb").write(encode(
                [(k, repl_r.get(k, x), tip) for k, x, tip in rows]))
        else:
            open(os.path.join(tmpdir2, internal.split("\\")[-1] + ".raw"), "wb").write(raw)
    tmp2 = os.path.join(BASE, "build", "v14l_tmp.pack")
    if os.path.exists(tmp2):
        os.remove(tmp2)
    run(PY, PACK, "create", tmp2, "--type", "3", "--version", "PFH4")
    for internal in FILES:
        leaf = internal.split("\\")[-1]
        src = os.path.join(tmpdir2, leaf + ".raw")
        if not os.path.exists(src):
            src = os.path.join(tmpdir2, leaf)
        run(PY, PACK, "add", tmp2, internal, src)
    run(PY, PACK, "set-type", tmp2, "3", "--output", LOC_OUT)
    os.remove(tmp2)

    v14 = PackFile(LOC_OUT)
    assert v14.header.version == b"PFH4" and v14.header.pack_type == 3
    for internal in FILES:
        if internal in (r"text\db\start_pos_factions.loc",
                        r"text\db\random_localisation_strings.loc"):
            continue
        assert v14.get_file(internal) == v11.get_file(internal), internal
    r13, p, t = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    assert p == t
    d13 = {k: x for k, x, _ in r13}
    for k, v in repl_spf.items():
        assert d13[k] == v, k
    # no rulers / placeholders left in descriptions
    for k in (KEY_ERE, KEY_WRE, KEY_ERE_L, KEY_WRE_L):
        assert "\uE100" not in d13[k] and "\uE120" not in d13[k], k
    rr, p, t = decode(v14.get_file(r"text\db\random_localisation_strings.loc"))
    assert p == t
    dd = {k: x for k, x, _ in rr}
    for k, v in repl_r.items():
        assert dd[k] == v, k
    log.append("v14 loc: ERE/WRE desc+long replaced (real, desc padded); difficulties = v11")
    log.append(f"v14 loc SHA256: {sha256_file(LOC_OUT)} ({os.path.getsize(LOC_OUT)} B)")
    assert sha256_file(VANILLA) == EXPECTED_VANILLA_SHA
    log.append("vanilla SHA256 after: OK")

    # ---------------- offline QA ----------------
    qa_log = qa_offline(v14f, base_ink)
    log.extend(qa_log)

    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    with open(os.path.join(BASE, "logs", "v14_build.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


def form_kind(cp):
    nm = unicodedata.name(chr(cp), "")
    if "MEDIAL" in nm:
        return "M"
    if "INITIAL" in nm:
        return "I"
    if "FINAL" in nm:
        return "F"
    if "ISOLATED" in nm:
        return "O"
    if cp == 0x0640:
        return "T"
    return "?"


def qa_offline(v14f, base_ink):
    """Compose QA strings LTR from NEW CUF bitmaps at engine advances;
    seam metric per joining boundary vs ideal-butted Tajawal. Non-fatal."""
    from PIL import Image, ImageFont
    out = ["== offline QA (engine-advance compose, seam>=200 pass, <128 FAIL) =="]
    from fontTools.ttLib import TTFont
    cmap = TTFont(TAJAWAL).getBestCmap()

    def taj_mask(ch, px):
        try:
            f = ImageFont.truetype(TAJAWAL, px, layout_engine=ImageFont.Layout.BASIC)
            m = f.getmask(ch, mode="L")
            return bytes(m), m.size
        except Exception:
            return b"", (0, 0)

    def taj_src(cp):
        if cp in cmap:
            return chr(cp)
        try:
            parts = unicodedata.decomposition(chr(cp)).split()
            if len(parts) >= 2 and parts[0].startswith("<"):
                return chr(int(parts[1], 16))
        except Exception:
            pass
        return None

    # calibrate Tajawal px per CUF via cap height of 'H'
    def vanilla_cap(c):
        i = c.table[0x48]
        ah, aw, w, h = c.dims[i]
        d = c.bitmaps[i]
        rows = [y for y in range(h) if any(d[y * w + x] > INK_THRESH for x in range(w))]
        return min(rows), max(rows)

    cropdir = os.path.join(BASE, "logs", "crops", "v14")
    os.makedirs(cropdir, exist_ok=True)
    total_fail, total_conn = 0, 0

    def maxrow(bm, w, h):
        best, bw = 0, -1
        for y in range(h):
            ink = sum(1 for v in bm[y * w:(y + 1) * w] if v > INK_THRESH)
            if ink > bw:
                best, bw = y, ink
        return best
    for fname, tag in (("font\\georgia_italic_12.cuf", "geo12"),
                       ("font\\la_gioconda_12.cuf", "gio12")):
        c = CUF.decode(v14f.get_file(fname))
        ink_cache = dict(base_ink[fname])
        top, bottom = vanilla_cap(c)
        cap = bottom - top + 1
        px = cap + 6
        for s in QA_STRINGS:
            vis = shape(s)
            # ours
            cells = []
            for ch in vis:
                cp = ord(ch)
                if unicodedata.category(ch) == "Mn":
                    continue
                i = c.table[cp]
                ah, aw, w, h = c.dims[i]
                cells.append((cp, c.bitmaps[i], w, h))
            adv = [adv_model(c, ink_cache, cp) for cp, _, _, _ in cells]
            # join row per cell: most-solid row (treated bars), else widest row
            def jrow(bm, w, h):
                best, bs, bi = 0, -1, -1
                for y in range(h):
                    row = bm[y * w:(y + 1) * w]
                    solid = sum(1 for v in row if v > 200)
                    ink = sum(1 for v in row if v > INK_THRESH)
                    if (solid, ink) > (bs, bi):
                        best, bs, bi = y, solid, ink
                return best
            jr = [jrow(bm, w, h) for _, bm, w, h in cells]
            refj = max(set(jr), key=jr.count)
            H = max(h for _, _, _, h in cells) + 8
            W = int(sum(adv)) + 8
            img = Image.new("L", (W, H), 255)
            cur = 0.0
            pos = []
            for (cp, bm, w, h), a, j in zip(cells, adv, jr):
                x0 = int(round(cur))
                for y in range(h):
                    for x in range(w):
                        v = bm[y * w + x]
                        if v > 10:
                            yy = y + (refj - j) + 4
                            if 0 <= yy < H and 0 <= x0 + x < W:
                                old = img.load()[x0 + x, yy]
                                img.load()[x0 + x, yy] = min(old, 255 - v)
                pos.append((cur, a))
                cur += a
            # reference: Tajawal butted with 1px overlap, max-row aligned
            rb = []
            for ch in vis:
                cp = ord(ch)
                if unicodedata.category(ch) == "Mn":
                    continue
                src = taj_src(cp)
                if src is None:
                    continue
                bm, (mw, mh) = taj_mask(src, px)
                rb.append((cp, bm, mw, mh))
            rX = []
            cur = 0
            for cp, bm, mw, mh in rb:
                xs = [x for y in range(mh) for x in range(mw) if bm[y * mw + x] > INK_THRESH] if mw and mh else []
                iw = (max(xs) - min(xs) + 1) if xs else mw
                rX.append((cur, iw, bm, mw, mh, maxrow(bm, mw, mh) if mw and mh else 0))
                cur += max(iw - 1, 1)
            # seam metric on ours
            fails, seams, nconn = [], [], 0
            cps = [cp for cp, _, _, _ in cells]
            kinds = [form_kind(cp) for cp in cps]
            for i in range(len(cells) - 1):
                lk, rk = kinds[i], kinds[i + 1]
                joining = (lk in ("M", "F") and rk in ("I", "M")) or \
                          (lk == "T" or rk == "T")
                xb = int(round(pos[i + 1][0]))
                col = [img.load()[x, y] for x in (xb - 1, xb)
                       for y in range(H) if 0 <= x < W]
                seam = 255 - min(col) if col else 255
                if joining:
                    nconn += 1
                    seams.append(seam)
                    if seam < 128:
                        fails.append((f"U+{cps[i]:04X}", f"U+{cps[i + 1]:04X}", seam))
            # seam metric on ref (same columns logic on rimg)
            rimg = None
            rseams, rfail, rnconn = [], [], 0
            if rX:
                rref = max(set(r[5] for r in rX), key=[r[5] for r in rX].count)
                rh0 = max(mh for _, _, _, _, mh, _ in rX) + 8
                rimg = Image.new("L", (cur + 8, rh0), 255)
                for cx, iw, bm, mw, mh, mr in rX:
                    for y in range(mh):
                        for x in range(mw):
                            v = bm[y * mw + x]
                            yy = y + (rref - mr) + 4
                            if v > 10 and 0 <= cx + x < cur + 8 and 0 <= yy < rh0:
                                o = rimg.load()[cx + x, yy]
                                rimg.load()[cx + x, yy] = min(o, 255 - v)
                rpos = [r[0] for r in rX]
                rr_kinds = [form_kind(cp) for cp, _, _, _ in rb]
                for i in range(len(rX) - 1):
                    lk, rk = rr_kinds[i], rr_kinds[i + 1]
                    joining = lk in ("M", "F") and rk in ("I", "M")
                    xb = rpos[i + 1]
                    col = [rimg.load()[x, y] for x in (xb - 1, xb)
                           for y in range(rh0) if 0 <= x < cur + 8]
                    seam = 255 - min(col) if col else 255
                    if joining:
                        rnconn += 1
                        rseams.append(seam)
                        if seam < 128:
                            rfail.append(i)
            total_fail += len(fails)
            total_conn += nconn
            mn = min(seams) if seams else -1
            avg = sum(seams) / len(seams) if seams else -1
            rmn = min(rseams) if rseams else -1
            ravg = sum(rseams) / len(rseams) if rseams else -1
            out.append(f"  [{tag}] {s}: conn={nconn} min_seam={mn} avg={avg:.0f} "
                       f"FAIL={fails if fails else '-'} | "
                       f"ref conn={rnconn} min={rmn} avg={ravg:.0f} reffail={len(rfail)}")
            # png: ours over ref
            rh = max(([rimg.size[1]] if rimg is not None else [H]) + [H]) + 8
            rw = max(W, (rimg.size[0] if rimg is not None else W)) + 8
            canvas = Image.new("L", (rw * 2, rh), 200)
            canvas.paste(img.crop((0, 0, W, H)), (0, 0))
            if rimg is not None:
                canvas.paste(rimg.crop((0, 0, rimg.size[0], rimg.size[1])), (rw, 0))
            canvas = canvas.resize((canvas.width * 2, canvas.height * 2), Image.NEAREST)
            safe = "".join(f"{ord(ch):04X}_" for ch in vis[:6])
            canvas.save(os.path.join(cropdir, f"{tag}_{safe}.png"))
    out.append(f"QA TOTAL: connecting={total_conn} failed={total_fail}")
    return out


if __name__ == "__main__":
    main()
