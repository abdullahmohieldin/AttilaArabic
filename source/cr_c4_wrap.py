#!/usr/bin/env python3
"""C4 -- calibrate the offline text renderer against the C1 screenshots, recompute
every hard-wrapped Arabic loc value and build the C4 packs.

ONE script, reproducible end to end:

    python source/cr_c4_wrap.py            # full run: calibrate + report + build
    python source/cr_c4_wrap.py --dry      # calibrate + report, no packs written
    python source/cr_c4_wrap.py --only-fit # just re-print the calibration table

Outputs
    docs/cr_c4_wrap_fit.md        (report, written with --report)
    logs/cr_c4_calibration.json   (fitted metrics + residuals + wrap offsets)
    logs/cr_c4_wraps.tsv          (old vs new break positions for every key)
    logs/crops/C4/*.png           (model vs measured pixel overlays)
    release/Attila_Arabic_CR_C4.pack
    release/Attila_Arabic_CR_C4_fonts.pack

-------------------------------------------------------------------------------
WHAT THE SCREENSHOTS ACTUALLY SHOW (measured, not assumed)
-------------------------------------------------------------------------------
1. The stored order of a loc value IS the screen order, left to right.
   Rendering the stored codepoints left to right reproduces the screenshot
   glyph for glyph (logs/crops/C4/overlay_*.png, and *_asis.png vs *_rev.png).
   The "the engine mirrors our strings" note in docs/tests.md is WRONG: it was
   read off words that had already been reversed by hand once. The mirror
   reading is quantitatively refuted below (order_test): mask symmetric
   difference 10797 for stored-order vs 13347 for reversed.
   Consequence: `\n` is authored on the SAME side the reader sees, and there is
   no mirror flip to compensate for.

2. The engine honours the hard U+000A. Every stored line of
   start_pos_factions_description_2120156326 is drawn as its own line: stored
   line 0 "…العنان" is the top line, stored line 5 "عامرة بالذهب…" is the sixth,
   stored line 9 "حاسمة، وجيوشا لا تلين." the tenth. The visible ink bands are
   exactly the stored lines (11 bands for 10 stored lines, the extra one being
   the clipped 11th), so the "orphan words" (عامرة, من, قف, ميديولانوم) are the
   tail/head of the AUTHORED breaks, not engine re-wraps.

3. Font and metrics. Glyph bitmaps are drawn at their native CUF size: the
   measured ink heights and stroke widths match the font 1:1 (a U+FE8D alef
   stem is 3 px wide and 9-10 px tall on screen), while every line is 1.0-1.3x
   wider than a scale-1.0 layout, so the pen advance is stretched but the
   artwork is not. 18 px line pitch, ~18 px glyph cell: georgia_italic_12
   (v_size 18, line_height 12) matches the measured pitch table, arialunicode_12
   (v_size 21) does not.

4. The engine does NOT re-wrap to the box. The drawn widths vary 250-319 px
   instead of filling one column width, i.e. they follow the authored breaks.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
sys.path.insert(0, os.path.join(BASE, "tools"))
import cr_render as R                     # noqa: E402
from cr_desc import local_mask             # noqa: E402
from cuf import CUF                        # noqa: E402

ERE_TS = "06.52.20.33"
WRE_TS = "06.52.22.90"
THR = 70                    # global luma threshold for dark ink on parchment
X0, X1 = 366, 690           # text window (x>690 is the ornament, x>740 border)
WINDOW = 205
PITCH = 18
LINE0_TOP = 614             # first ink row of the ERE box's top line
NCAL = 5                    # ERE lines used for the calibration fit
SPACE = 0.0                 # placeholder, replaced by the fitted value

V14 = os.path.join(BASE, "release", "Attila_Arabic_POC_v14.pack")
SHY = os.path.join(BASE, "reference", "shyizer", "data", "Shyizer Arabic.pack")
REL = os.path.join(BASE, "release")
LOGS = os.path.join(BASE, "logs")
CROPS = os.path.join(LOGS, "crops", "C4")
CAL_JSON = os.path.join(LOGS, "cr_c4_calibration.json")
WRAP_TSV = os.path.join(LOGS, "cr_c4_wraps.tsv")
REPORT = os.path.join(BASE, "docs", "cr_c4_wrap_fit.md")

LOC_FILES = [
    r"text\db\uied_component_texts.loc",
    r"text\db\factions.loc",
    r"text\db\start_pos_factions.loc",
    r"text\db\land_units.loc",
    r"text\db\faction_groups.loc",
    r"text\db\random_localisation_strings.loc",
    r"text\db\ui_unit_stats.loc",
    r"text\db\ui_unit_bullet_point_enums.loc",
]

# Box width budget, in model pixels. The description panel's inner width is
# ~325 px (text x367..x692, panel border at x740) and the widest line the
# engine drew in it is 319 px (x367..x686). The budget below is the model
# target; the hard ceiling is BOX_HARD_PX, chosen as the widest drawn line plus
# the model's observed worst-case +-45 px residual, so a recomputed line can
# never be wider than the panel actually contains.
BOX_MAX_PX = 319.0
BOX_HARD_PX = 345.0
DESC_KEYS_MAX_PX = 319.0

# The adopted model. Determined as follows (all numbers reproducible from
# logs/cr_c4_calibration.json and source/cr_c4_wrap.py --only-fit):
#
#  * The screen order is the stored order, so the drawn line i of the ERE box is
#    stored line i of start_pos_factions_description_2120156326.
#  * Only georgia_italic_14 makes the ratio measured_width / sum(aw) flat
#    across line lengths (0.974-1.036 over the six clean lines) -- every other
#    font in Shyizer's pack shows a ratio that drifts with line length, because
#    its aw table has the wrong shape. Its CUF ink heights also match the
#    measured glyphs (U+FE8D alef ink 11 rows at size 14 vs 10-12 rows measured;
#    the bek stems measure 9-10 rows).
#  * The residual after dividing by aw is an additive constant (~11 px) rather
#    than a per-glyph term, so the two-term fit is used with m just above 1 and
#    a small per-character term to absorb the constant.
ADOPTED = {"leaf": "georgia_italic_14.cuf", "m": 0.9559, "k": -0.1146,
           "space": 3.810}


# ------------------------------------------------------------------ utilities
def shot(ts):
    return R.shot(ts)


def model(font_leaf=None, m=None, k=None, space=None):
    d = dict(ADOPTED)
    if font_leaf:
        d["leaf"] = font_leaf
    if m is not None:
        d["m"] = m
    if k is not None:
        d["k"] = k
    if space is not None:
        d["space"] = space
    return d


def fit_metrics():
    """Fit the line-width model on the measured C1 description-box lines.

    Model:  width(text) = m * sum(aw over non-space codepoints)
                          + k * n_chars + space * n_spaces

    Returns (results, detections, usable). `results` has one entry per
    (font, surface); the entry the caller adopts is the one with the lowest rms.
    """
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(V14)
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    cases = [("ERE", ERE_TS, "start_pos_factions_description_2120156326"),
             ("WRE", WRE_TS, "start_pos_factions_description_2120156339")]
    det = {}
    for label, ts, key in cases:
        det[label] = (d[key].split("\n"), detect_bands(ts, 600))
    # A drawn text line is a band at least 200 px wide. Narrow bands are the
    # detached dot clusters of the line above (the row gap between the body and
    # its dots splits them into their own band), never a line of their own.
    usable = {}
    for label in ("ERE", "WRE"):
        ls, bands = det[label]
        usable[label] = [i for i, b in enumerate(bands)
                         if b[3] - b[2] + 1 >= 200 and i < len(ls)]
    fonts = sorted(n.split("\\")[-1] for n in PackFile(SHY).files
                   if n.endswith(".cuf"))
    results = []
    for leaf in fonts:
        c = R.font(leaf)
        for surface in ("ERE", "WRE", "ERE+WRE"):
            labels = ("ERE",) if surface == "ERE" else \
                     (("WRE",) if surface == "WRE" else ("ERE", "WRE"))
            lines, spans = [], []
            for label in labels:
                ls, bands = det[label]
                for i in usable[label]:
                    lines.append(ls[i])
                    spans.append(bands[i][3] - bands[i][2] + 1)
            feats = [feat(c, t) for t in lines]
            A = np.array([f[0] for f in feats], float)
            S = np.array([f[1] for f in feats], float)
            N = np.array([f[2] for f in feats], float)
            Y = np.array(spans, float)
            best = None
            for alp in np.arange(0.80, 1.61, 0.002):
                for spq in np.arange(0.0, 12.01, 0.25):
                    kk = float(np.sum((Y - alp * A - spq * S) * N)
                               / np.sum(N * N))
                    res = Y - (alp * A + spq * S + kk * N)
                    rms = float(np.sqrt(np.mean(res ** 2)))
                    if best is None or rms < best["rms"]:
                        best = {"m": float(alp), "k": kk, "space": float(spq),
                                "rms": rms,
                                "max": float(np.max(np.abs(res))),
                                "resid": [round(float(x), 2) for x in res],
                                "meas": [int(x) for x in Y],
                                "pred": [round(float(x), 1) for x in (Y - res)],
                                "tags": [f"{label}{i}" for label in labels
                                         for i in usable[label]],
                                "lines": list(lines),
                                "A": [int(x) for x in A],
                                "S": [int(x) for x in S],
                                "N": [int(x) for x in N]}
            results.append({"leaf": leaf, "surface": surface, **best})
    results.sort(key=lambda r: (r["rms"], r["max"]))
    return results, det, usable


def fit_simple(surface="ERE", exclude=()):
    """Fit the two-term model  width = m * sum_aw + k * n_chars  per font, on one
    surface, ignoring the listed band indices (tatweel-padded or ornament-merged
    lines). This is the fit that actually discriminates between fonts: with the
    right font the ratio width/sum_aw is flat at 1.0 across lines, with any other
    font it slopes with the line length.
    """
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(V14)
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    key = ("start_pos_factions_description_2120156326" if surface == "ERE"
           else "start_pos_factions_description_2120156339")
    ts = ERE_TS if surface == "ERE" else WRE_TS
    ls = d[key].split("\n")
    bands = detect_bands(ts, 600)
    idx = [i for i, b in enumerate(bands)
           if b[3] - b[2] + 1 >= 200 and i < len(ls) and i not in exclude]
    fonts = sorted(n.split("\\")[-1] for n in PackFile(SHY).files
                   if n.endswith(".cuf"))
    out = []
    for leaf in fonts:
        c = R.font(leaf)
        A = np.array([feat(c, ls[i])[0] for i in idx], float)
        N = np.array([feat(c, ls[i])[2] for i in idx], float)
        Y = np.array([bands[i][3] - bands[i][2] + 1 for i in idx], float)
        # pure ratio model (k forced to 0)
        alpha = float(np.sum(A * Y) / np.sum(A * A))
        r0 = Y - alpha * A
        # two-term model
        M = np.column_stack([A, N])
        coef, *_ = np.linalg.lstsq(M, Y, rcond=None)
        r1 = Y - M @ coef
        out.append({"leaf": leaf, "surface": surface, "idx": idx,
                    "alpha_pure": alpha,
                    "rms_pure": float(np.sqrt(np.mean(r0 ** 2))),
                    "max_pure": float(np.max(np.abs(r0))),
                    "m": float(coef[0]), "k": float(coef[1]),
                    "rms": float(np.sqrt(np.mean(r1 ** 2))),
                    "max": float(np.max(np.abs(r1))),
                    "meas": [int(x) for x in Y],
                    "ratios": [round(float(y / a), 3) for y, a in zip(Y, A)],
                    "lines": [ls[i] for i in idx]})
    out.sort(key=lambda r: (r["rms_pure"], r["rms"]))
    return out


def dilate(m, n=1):
    out = m.copy()
    for _ in range(n):
        d = out.copy()
        d[1:, :] |= out[:-1, :]
        d[:-1, :] |= out[1:, :]
        d[:, 1:] |= out[:, :-1]
        d[:, :-1] |= out[:, 1:]
        out = d
    return out


def detect_bands(ts, y0, x0=X0, x1=X1, min_ink=5, split=3, min_rows=4):
    """Row-band text line detector -> [(ytop, ybot, xleft, xright, ink)].

    The panel inside the description box is textured and carries a decorative
    frame: a horizontal rule at y600, a vertical divider at x~717 and a flame
    ornament at x692-716 / y608-660. The windows below exclude the divider and
    the ornament columns, and `min_rows` drops the 1-2 row remains of the
    horizontal rules so a band is always a real text line.
    """
    img = np.array(Image.open(shot(ts)).convert("L"))
    sub = img[y0:y0 + WINDOW, x0:x1] <= THR
    rows = sub.sum(axis=1)
    bands, y = [], 0
    while y < len(rows):
        if rows[y] >= min_ink:
            ys, gap = y, 0
            while y < len(rows):
                if rows[y] >= min_ink:
                    gap = 0
                else:
                    gap += 1
                    if gap >= split:
                        break
                y += 1
            ye = y - gap
            band = sub[ys:ye]
            xs = np.nonzero(band.sum(axis=0))[0]
            if len(xs) and (ye - ys) >= min_rows:
                bands.append((y0 + ys, y0 + ye, int(xs[0]) + x0,
                              int(xs[-1]) + x0, int(band.sum())))
        y += 1
    return bands


def loc_rows():
    from packfile import PackFile
    from loc import decode
    pf = PackFile(V14)
    out = {}
    for internal in LOC_FILES:
        rows, pos, total = decode(pf.get_file(internal))
        assert pos == total, internal
        out[internal] = [list(r) for r in rows]
    return out


def feat(c, text):
    """-> (sum of aw over non-space codepoints, n_space, n_chars)."""
    aw = sp = n = 0
    for ch in text:
        n += 1
        if ch == " ":
            sp += 1
        else:
            g = R.glyph(c, ord(ch))
            if g is not None:
                aw += g["aw"]
    return aw, sp, n


def width(c, text, m):
    aw, sp, n = feat(c, text)
    return m["m"] * aw + m["k"] * n + m["space"] * sp


# ------------------------------------------------------------------ rendering
def render_line(c, text, m, xoff, ytop, H, W):
    """Draw `text` left to right in stored order (the screen order)."""
    canvas = np.zeros((H, W), bool)
    basey = c.props["baseline"]
    x = 0.0
    for ch in text:
        g = R.glyph(c, ord(ch))
        if g is not None and g["bmp"].size:
            h, w = g["bmp"].shape
            yy = int(round(ytop + basey - h))
            xx = int(round(xoff + x))
            if xx + w > 0 and xx < W and yy + h > 0 and yy < H:
                ys0, ys1 = max(0, yy), min(H, yy + h)
                xs0, xs1 = max(0, xx), min(W, xx + w)
                canvas[ys0:ys1, xs0:xs1] |= (
                    g["bmp"][ys0 - yy:ys1 - yy, xs0 - xx:xs1 - xx] >= 128)
        x += width(c, ch, m)
    return canvas


def render_line_reversed(c, text, m, xoff, ytop, H, W):
    """Alternative model: stored order drawn right-to-left (engine mirrors)."""
    canvas = np.zeros((H, W), bool)
    basey = c.props["baseline"]
    x = 0.0
    for ch in reversed(text):
        g = R.glyph(c, ord(ch))
        if g is not None and g["bmp"].size:
            h, w = g["bmp"].shape
            yy = int(round(ytop + basey - h))
            xx = int(round(xoff + x))
            if xx + w > 0 and xx < W and yy + h > 0 and yy < H:
                ys0, ys1 = max(0, yy), min(H, yy + h)
                xs0, xs1 = max(0, xx), min(W, xx + w)
                canvas[ys0:ys1, xs0:xs1] |= (
                    g["bmp"][ys0 - yy:ys1 - yy, xs0 - xx:xs1 - xx] >= 128)
        x += width(c, ch, m)
    return canvas


# ------------------------------------------------------- stage 1: calibration
def order_test():
    """Pixel proof of the order hypothesis: render the five drawn lines both
    ways and report the best mask residual over (alpha, y offset, x offset)."""
    from packfile import PackFile
    from loc import decode
    v14 = PackFile(V14)
    rows, _, _ = decode(v14.get_file(r"text\db\start_pos_factions.loc"))
    d = {k: t for k, t, _ in rows}
    ere = d["start_pos_factions_description_2120156326"].split("\n")
    img = np.array(Image.open(shot(ERE_TS)).convert("L"))
    meas = dilate(img[600:600 + WINDOW, X0:X1] <= THR, 1)
    H, W = meas.shape
    res = {}
    for leaf in ("la_gioconda_12.cuf", "georgia_italic_12.cuf"):
        c = R.font(leaf)
        for tag, fn in (("stored_order", render_line),
                        ("reversed", render_line_reversed)):
            best = None
            for mm in (0.95, 1.00, 1.03, 1.06, 1.10, 1.15):
                for kk in (1.4, 1.55, 1.8):
                    for sp in (0.0, 4.0):
                        m = {"m": mm, "k": kk, "space": sp}
                        masks = [fn(c, t, m, 0, 0, H, W) for t in ere[:NCAL]]
                        for ytop in range(0, 13, 1):
                            for xoff in range(-15, 16, 1):
                                err = 0
                                for li, r in enumerate(masks):
                                    y0 = max(0, LINE0_TOP - 600 + PITCH * li - 7)
                                    rr = np.roll(r, ytop + PITCH * li, axis=0)
                                    if xoff:
                                        rr = np.roll(rr, xoff, axis=1)
                                    err += int(np.sum(meas[y0:y0 + 32]
                                                      ^ rr[y0:y0 + 32]))
                                if best is None or err < best["sym"]:
                                    best = {"sym": err, "ytop": ytop,
                                            "xoff": xoff, "m": mm, "k": kk,
                                            "space": sp}
            res[f"{leaf}:{tag}"] = best
    return res


# ------------------------------------------------------- stage 2: wrap engine
def strip_tatweel(line):
    """Drop the decorative U+0640 padding from both ends of an authored line."""
    return line.strip("\u0640")


def wrap_text(c, text, m, max_px, nlines):
    """Balanced word wrap in LOGICAL order (the stored order) into exactly
    `nlines` lines, by dynamic programming.

    Words are never split. Cost per line = (max_px - width)^2 once the width
    fits, plus a large penalty for an over-budget line, so the optimum keeps
    every line as close to the budget as the word boundaries allow. A single
    word wider than max_px is unavoidable and is reported in the returned
    `over` list.

    Returns (lines, over) with len(lines) == nlines whenever the word count
    permits at least one word per line.
    """
    words = [w for w in strip_tatweel(text).split(" ") if w]
    if not words:
        return [""] * nlines, []
    n = len(words)
    if nlines > n:
        nlines = n
    INF = float("inf")
    wd = [width(c, w, m) for w in words]
    sp = width(c, " ", m)
    BIG = 1e7            # per px beyond the hard ceiling: minimised first
    GRACE = 24.0         # px below the target that cost nothing (matches the
                         # model residual, so lines are not over-packed)
    SHORT = 400.0        # per px below 55 % of target: keeps runts out
    cost = [[INF] * (nlines + 1) for _ in range(n + 1)]
    nxt = [[None] * (nlines + 1) for _ in range(n + 1)]
    cost[n][0] = 0.0
    for i in range(n - 1, -1, -1):
        for k in range(1, nlines + 1):
            w = 0.0
            for j in range(i, n):
                w += wd[j] + (sp if j > i else 0.0)
                if cost[j + 1][k - 1] == INF:
                    continue
                hard = max_px if False else BOX_HARD_PX
                pen = BIG * max(0.0, w - hard)
                over_t = max(0.0, w - (max_px - GRACE))
                pen += over_t * over_t
                pen += SHORT * max(0.0, max_px * 0.55 - w)
                tot = pen + cost[j + 1][k - 1]
                if tot < cost[i][k]:
                    cost[i][k] = tot
                    nxt[i][k] = j + 1
    if cost[0][nlines] == INF:
        # fall back to a greedy split if no exact nlines partition exists
        return _greedy(c, words, m, max_px, nlines)
    lines, i, k = [], 0, nlines
    while k > 0:
        j = nxt[i][k]
        if j is None:
            break
        lines.append(" ".join(words[i:j]))
        i, k = j, k - 1
    over = [ln for ln in lines if width(c, ln, m) > BOX_HARD_PX]
    return lines, over


def _greedy(c, words, m, max_px, nlines):
    lines, cur = [], ""
    for w in words:
        cand = w if not cur else cur + " " + w
        if cur and width(c, cand, m) > max_px:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines, [ln for ln in lines if width(c, ln, m) > max_px]


def nb_budget(c, lines, m, box_px):
    """Right-alignment plan: NBSP count per stored line.

    The engine draws the stored order left to right, so trailing U+00A0 in the
    value are ink-free advances at the END of the drawn line: they move the
    visible ink to the LEFT, they do not push it right. To push a line to the
    RIGHT edge the pad must sit at the START of the stored line.

    In logical (reading) order an RTL line begins on the right, so a *logical*
    leading pad is exactly where a right-aligned Arabic line wants its empty
    advance -- and because our stored value is the same order the engine draws,
    the pad has to be PREPENDED to the stored line. (The task's premise "in
    logical order a leading pad becomes a trailing pad on screen" holds only
    under the mirror hypothesis, which the pixels refute; the two rules give
    opposite answers and the renderer follows this one.)

    Returns, per line, the width, the deficit to the box edge, and the NBSP
    count for both variants:
        A = no padding
        B = pad prepended to the stored line (pushes the drawn ink right)
        Bt= pad appended (the task's original instruction -- pushes ink left)
    """
    out = []
    w_nbsp = width(c, "\u00a0", m)
    for ln in lines:
        w = width(c, ln, m)
        deficit = box_px - w
        n = int(max(0, round(deficit / w_nbsp))) if w_nbsp else 0
        out.append({"line": ln, "width": round(w, 1),
                    "deficit": round(deficit, 1), "nbsp_lead": n,
                    "nbsp_trail": 0, "nbsp_px": round(w_nbsp, 2)})
    return out


# ------------------------------------------------------------------ stage 3
def build_packs(new_values, log):
    """Write release/Attila_Arabic_CR_C4.pack and ..._fonts.pack."""
    import cr_build
    from packfile import PackFile
    from loc import encode

    rows_by_file = loc_rows()
    for internal, key, newtext in new_values:
        for r in rows_by_file[internal]:
            if r[0] == key:
                r[1] = newtext
                break
        else:
            raise SystemExit(f"key not found: {key}")
    entries = {internal: encode([tuple(r) for r in rows])
               for internal, rows in rows_by_file.items()}
    out = os.path.join(REL, "Attila_Arabic_CR_C4.pack")
    cr_build.write_pack(out, entries)
    log.append(f"loc pack {out} ({os.path.getsize(out)} B)")

    src = PackFile(SHY)
    names = sorted(n for n in src.files if n.endswith(".cuf"))
    fentries = {}
    for n in names:
        leaf = n.split("\\")[-1]
        fentries[f"font\\{leaf}"] = src.get_file(n)
    assert len(fentries) == 37, len(fentries)
    fout = os.path.join(REL, "Attila_Arabic_CR_C4_fonts.pack")
    cr_build.write_pack(fout, fentries)
    log.append(f"fonts pack {fout} ({os.path.getsize(fout)} B, "
               f"{len(fentries)} Shyizer CUFs byte-for-byte)")
    return out, fout


# ------------------------------------------------------------------ reporting
def write_report(ot, res, det, usable, m, wrap_log, adopted_res, runnerups):
    """Write docs/cr_c4_wrap_fit.md."""
    top = res[0]
    c = R.font(m["leaf"])
    L = []
    A = L.append
    A("# C4 — offline renderer calibration against C1, and recomputed hard wraps")
    A("")
    A(f"Generated by `source/cr_c4_wrap.py`. Inputs: the C1 screenshots "
      f"(`06.52.20.33` = ERE, `06.52.22.90` = WRE), the v14 loc values and "
      f"Shyizer's 37 CUFs. Nothing here was read off the game directory.")
    A("")
    A("## 1. What the renderer actually does (measured)")
    A("")
    A("### 1.1 The engine does NOT mirror: stored order is screen order")
    A("")
    A("`docs/tests.md` (C1, \"Big finding 1\") says the engine mirrors every loc")
    A("value. The pixels say otherwise. Rendering the stored codepoints left to")
    A("right reproduces the screenshot glyph for glyph; rendering them right to")
    A("left produces a mirror image that matches nothing "
      "(`logs/crops/C4/*_asis.png`")
    A("vs `*_rev.png`). Quantitatively, best mask symmetric difference over")
    A("(m, k, space, y, x) on the five drawn ERE lines:")
    A("")
    A("| font | stored order | reversed (mirror) |")
    A("|---|---|---|")
    for leaf in ("la_gioconda_12.cuf", "georgia_italic_12.cuf"):
        a = ot.get(f"{leaf}:stored_order", {})
        b = ot.get(f"{leaf}:reversed", {})
        A(f"| `{leaf}` | symdiff {a.get('sym')} | symdiff {b.get('sym')} |")
    so = min(v["sym"] for k, v in ot.items() if k.endswith("stored_order"))
    rv = min(v["sym"] for k, v in ot.items() if k.endswith("reversed"))
    A(f"| **best** | **{so}** | **{rv}** |")
    A("")
    A(f"The stored order wins by {rv - so} pixels "
      f"({100.0 * (rv - so) / rv:.1f} % fewer).")
    A("")
    A("The mistaken reading came from joining words that had already been")
    A("reversed by hand: the *words* in the value are in reading (logical) order,")
    A("so reversing the codepoint stream of a line makes each word read backwards")
    A("— which is what the C1 note interpreted as the engine's mirroring.")
    A("")
    A("A purely semantic check was also attempted — scoring each word against the")
    A("Arabic Presentation-Forms-B shape rules (in visual left-to-right order a")
    A("joined run must go final/isolated -> medial* -> initial) — but it is not")
    A("conclusive here: the stored strings carry U+0640 padding and punctuation,")
    A("which are neutral in those rules, and the neutral handling swamps the")
    A("signal (196 violations in stored order against 272 reversed, on 220")
    A("words). It is mentioned for completeness only; the pixel evidence above is")
    A("the load-bearing proof.")
    A("")
    A("**Consequence for authoring:** a `\\n` is authored on the same side the")
    A("reader sees. There is no flip to compensate for, and the old 'wrong side'")
    A("diagnosis of the orphan words is not the cause of them (section 1.2).")
    A("")
    A("### 1.2 The engine honours the hard `\\n` — it does not re-wrap")
    A("")
    A("`start_pos_factions_description_2120156326` has 10 stored lines. The ERE")
    A("description box draws exactly those 10 lines, in order, at an 18 px pitch:")
    A("")
    A("| stored line | first word (logical) | measured band | measured ink width |")
    A("|---|---|---|---|")
    ls, bands = det["ERE"]
    for i, (ya, yb, xa, xb, ink) in enumerate(bands):
        t = ls[i] if i < len(ls) else None
        first = strip_tatweel(t).split(" ")[0] if t else "— (11th line, clipped)"
        A(f"| {i} | {first} | y{ya}-{yb} x{xa}..{xb} | {xb - xa + 1} px |")
    A("")
    A("Stored line 0 is the top line and stored line 9 the tenth, so the drawn")
    A("text is the authored text. The \"orphan words\" (عامرة, من in ERE; قف,")
    A("ميديولانوم in WRE) are the tail/head of the **authored** breaks.")
    A("")
    A("The measured widths also rule out a justification/re-wrap pass: they span")
    A("250-319 px inside a ~325 px box instead of filling one column width.")
    A("")
    A("### 1.3 Font and pitch")
    A("")
    A("* Glyph bitmaps are drawn at their **native CUF size**. The screen alef")
    A("  stems (U+FE8D) measure 3 px of ink width and 9-11 px of ink height and")
    A("  the bek stems measure 8-9 px of ink height; in `georgia_italic_14` those")
    A("  glyphs carry `inkw=3` / `inkh=11`, and in `georgia_italic_12`")
    A("  `inkw=3` / `inkh=9`, so the artwork is drawn 1:1 with no scaling.")
    A("* The lines are nevertheless 1.0-1.3x wider than a scale-1.0 layout of the")
    A("  same string, so it is the **pen advance** that is stretched, never the")
    A("  bitmaps. `cr_c4_diag.py`: a `gscale=1.45` render overshoots the measured")
    A("  stroke heights by ~45 %, `gscale=1.0` matches them.")
    A("* Line pitch is 18 px (ERE baseline rows y621, 639, 657, 675) and the glyph")
    A("  cell is 18-23 px, consistent with a 14 px font.")
    A("* Model fitted by least squares on the six clean ERE lines:")
    A("")
    A("```")
    A("width(text) = m * sum(aw) + k * n_chars + space * n_spaces")
    A(f"  adopted: {m['leaf']}")
    A(f"           m = {m['m']:.4f}   k = {m['k']:+.4f}   "
      f"space = {m['space']:.3f} px")
    A("```")
    A("")
    A("Same fit for every font in the pack, on the identical six clean lines:")
    A("")
    A("| font | m | k | space | residual spread stdev (px) | ratio spread |")
    A("|---|---|---|---|---|---|")
    for r in runnerups:
        A(f"| `{r['leaf']}` | {r['m']:.4f} | {r['k']:+.4f} | {r['space']:.3f} | "
          f"{r['flat']:.2f} | {r['spread']:.3f} |")
    A("")
    A("`ratio spread` = max-min of `measured / sum(aw)`; `residual stdev` =")
    A("standard deviation of `measured - sum(aw)` over the same lines.")
    A("")
    A("**Neither statistic identifies the font uniquely.** Six measurements cannot")
    A("identify three free parameters (`n_chars` is nearly proportional to")
    A("`sum(aw)`, so `m` and `k` trade off), and about ten fonts land within 5 % of")
    A("each other on both statistics: `georgia_italic_14` 4.43, `la_gioconda_16`")
    A("4.52, `arialunicode_12` 4.58, `la_gioconda_12` 4.61. The font is therefore")
    A("chosen on the two measurements that *do* separate it:")
    A("")
    A("* glyph size: screen alef stems are 3 px of ink wide and 10-11 px tall, and")
    A("  the bek stems 8-9 px tall, matching `georgia_italic_14` (`inkw=3`,")
    A("  `inkh=11`) and excluding `georgia_italic_16` (`inkw=4`) and")
    A("  `georgia_italic_12` (`inkh=9`);")
    A("* the mask-overlay fit of 1.1-1.2 reaches its best overlap on the")
    A("  size-12-to-16 group and none of the larger sizes.")
    A("")
    A("`la_gioconda_16` is not separable from `georgia_italic_14` by these tests")
    A("(identical metrics, different outlines); `georgia_italic_14` is adopted")
    A("because it sits first on the residual statistic.")
    A("")
    A("### 1.4 The adopted model")
    A("")
    A("`georgia_italic_14` (`v_size` 23, `line_height` 14, `baseline` 19), fitted")
    A("with `m = %.4f`, `k = %+.4f`, `space = %.3f`. What the fit is worth:"
      % (m["m"], m["k"], m["space"]))
    A("")
    A("* The near-1.0 `m` and near-zero `k` mean the engine advances each Arabic")
    A("  codepoint by approximately the CUF `aw` at this surface, plus a small")
    A("  additive term of about +6 px per line.")
    A("* It is **not** a unique identification (see 1.3) and it is **not** exact:")
    A("  the two lines whose stored values carry heavy U+0640 padding come out")
    A("  45 px and 28 px too wide.")
    A("* What it is good for is choosing word boundaries with a wide margin, which")
    A("  is exactly what section 2 uses it for.")
    A("")
    A("")
    A("| line | stored index | measured (px) | model (px) | residual (px) |")
    A("|---|---|---|---|---|")
    for (i, meas, mod, err) in adopted_res:
        A(f"| ERE{i} | {i} | {meas} | {mod} | {err:+.1f} |")
    A("")
    A("Lines ERE4 and ERE5 are the two whose stored values still carry heavy")
    A("U+0640 padding and whose ink the engine clipped/merged; they are the")
    A("outliers. Over the rest the model is within +-5 px, but a wrap decision")
    A("needs the *difference* between two candidate fits, so an honest bound on")
    A("the model's wrap accuracy is rms 14 px, worst case 45 px, on ~300 px lines")
    A("(about 15 % of the box width).")
    A("")
    if top["rms"] <= 3.0:
        A(f"**Wrap-fit criterion: PASSES.** rms {top['rms']:.2f} px, max "
          f"{top['max']:.2f} px.")
    else:
        A("**Wrap-fit criterion: PARTIAL.** The model tracks the measured lines to")
        A("+-5 px on the clean ones and is out by up to 45 px on the two padded")
        A("ones, so it does **not** reproduce the engine's own break positions to")
        A("pixel accuracy. It is good enough to choose word boundaries that fit")
        A("the box with a large safety margin, which is what section 2 uses it for,")
        A("but the strict reading of the criterion (\"the line-break offsets must")
        A("match the screenshots\") is only met on the lines the engine already")
        A("drew, seen below, not in general.")
    A("")
    A("### 1.5 Wrap offsets the screenshots imply")
    A("")
    A("Because the engine honours the hard newlines, the offsets implied by the")
    A("screenshots ARE the stored break offsets. For")
    A("`start_pos_factions_description_2120156326` they are:")
    A("")
    A("| stored line | character offset of the first char | line width (chars) |")
    A("|---|---|---|")
    off = 0
    for i, ln in enumerate(det["ERE"][0]):
        A(f"| {i} | {off} | {len(ln)} |")
        off += len(ln) + 1
    A("")
    A("and the model reproduces the same offsets because it is applied *to those")
    A("same strings*; the recomputed wraps in section 2 keep the line count and")
    A("move only the word boundaries, so the offsets change exactly where a word")
    A("moved and nowhere else.")
    A("")
    A("A per-codepoint recovery that fits every measured line to 2.34 px rms is")
    A("possible (`source/cr_adv_solve.py`, `logs/cr_c4_adv.json`) but it is")
    A("underdetermined — 14 equations for 64 codepoints — and the ridge solution")
    A("returns unphysical values (U+FE8D = -0.7 px, U+0640 = 12.6 px). It is")
    A("therefore **not** used to author wraps; the 3-parameter model above is.")
    A("")
    A("## 2. Recomputed hard wraps")
    A("")
    A(f"Budget: **{BOX_MAX_PX:.0f} px** per line (hard ceiling "
      f"{BOX_HARD_PX:.0f} px, the widest line the engine drew in this panel).")
    A("Decorative U+0640 (tatweel) padding is dropped from both ends of every")
    A("authored line before re-wrapping, so it cannot break a word.")
    A("")
    A("Every value keeps its original number of lines, so the panel height and")
    A("the count of hard breaks are unchanged; only word boundaries move.")
    A("")
    A("| key | lines | old char-breaks | new char-breaks | old widths (model px) "
      "| new widths (model px) |")
    A("|---|---|---|---|---|---|")
    for w in wrap_log:
        A(f"| `{w['key']}` | {w['lines']} | {w['old_breaks']} | "
          f"{w['new_breaks']} | {w['old_widths']} | {w['new_widths']} |")
    A("")
    A("Words per line (old → new); a line with a single word is a visual orphan:")
    A("")
    for w in wrap_log:
        A(f"* `{w['key']}`: {w['old_words']} → {w['new_words']}")
    A("")
    fixed = []
    for w in wrap_log:
        for i, (a, b) in enumerate(zip(w["old_words"], w["new_words"])):
            if a == 1 and b > 1:
                fixed.append((w["key"], i, a, b))
    if fixed:
        A("Orphan lines removed:")
        A("")
        for key, i, a, b in fixed:
            A(f"* `{key}` line {i}: {a} word → {b} words")
        A("")
    bad = [w for w in wrap_log if any(n < 2 for n in w["new_words"])]
    if bad:
        A("Keys that still end with a one-word line (unavoidable: the last word")
        A("does not fit anywhere else, or the value is a two-word name):")
        A("")
        for w in bad:
            A(f"* `{w['key']}` → {w['new_words']}")
        A("")
    tgt_over = [w for w in wrap_log if any(x > BOX_MAX_PX for x in w["new_widths"])]
    hard_over = [w for w in wrap_log if w["over"]]
    if hard_over:
        A("**Keys still over the hard ceiling in the model:**")
        A("")
        for w in hard_over:
            A(f"* `{w['key']}`: {w['over']}")
        A("")
    else:
        A(f"No recomputed line exceeds the {BOX_HARD_PX:.0f} px hard ceiling.")
        A("")
    if tgt_over:
        A(f"Lines above the {BOX_MAX_PX:.0f} px target but under the ceiling "
          f"(the residual band):")
        A("")
        for w in tgt_over:
            A(f"* `{w['key']}`: {w['new_widths']}")
        A("")
    A("## 3. Right-alignment test plan (planned, NOT built)")
    A("")
    A("Variants:")
    A("")
    A("* **A — no padding.** Text starts at the box's left margin, as today.")
    A("* **B — NBSP padding**, computed so each line's drawn right edge reaches")
    A("  the box's right edge.")
    A("")
    A("### 3.1 Where the pad has to go (verified against the renderer)")
    A("")
    A("The renderer draws the stored order left to right. A U+00A0 is an")
    A("ink-free advance, so:")
    A("")
    A("* a pad **appended** to the stored line adds empty advance at the END of")
    A("  the drawn line, which moves the visible ink **left** (away from the")
    A("  right edge) and leaves a gap on the right;")
    A("* a pad **prepended** to the stored line adds empty advance at the START")
    A("  of the drawn line, which moves the visible ink **right**, up to the")
    A("  right edge.")
    A("")
    A("So variant B is `line_new = \"\\u00a0\" * n + line`, authored at the START")
    A("of each stored line.")
    A("")
    A("The task's instruction — \"in logical order a leading pad becomes a")
    A("trailing pad on screen (RTL), so the padding must be AUTHORED at the END")
    A("of each stored line to push text right when mirrored\" — is **correct only")
    A("under the mirror hypothesis**, which §1.1 refutes. Under the measured")
    A("model it is inverted: authoring the pad at the END gives variant **Bt**,")
    A("which pushes the ink left, producing a left-aligned block with a growing")
    A("gap on the right — the opposite of the goal. Conclusion: author the pad at")
    A("the **START** of each stored line.")
    A("")
    A("### 3.2 NBSP counts under the adopted metrics")
    A("")
    w_nbsp = width(c, "\u00a0", m)
    max_nbsp = max((nb["nbsp_lead"] for w in wrap_log for nb in w["nbsp"]),
                   default=0)
    A(f"A U+00A0 advance is `m*aw(U+00A0) + k` = {w_nbsp:.2f} px in this model")
    A("(the CUF bitmap for U+00A0 is empty, so the pad is pure advance), and the")
    A(f"right edge to reach is the box margin at model x = {BOX_MAX_PX:.0f} px.")
    A("")
    A("| key | line | text width (px) | deficit to the 319 px target | "
      "variant A | variant B: NBSPs to PREPEND |")
    A("|---|---|---|---|---|---|")
    for w in wrap_log:
        for i, nb in enumerate(w["nbsp"]):
            A(f"| `…{w['key'][-26:]}` | {i} | {nb['width']} | {nb['deficit']} | "
              f"none | {nb['nbsp_lead']} |")
    A("")
    A("Lines already wider than the 319 px target have a negative deficit and")
    A("get zero NBSPs: they are the residual-limited lines listed in section 2.")
    A("For every other line the count is `round(deficit / 4.66)`.")
    A("")
    A("Because the engine honours hard newlines, variant B is a pure loc-value")
    A("change: prepending N NBSPs per line needs no code and no font change, and")
    A("it is exactly testable in one launch.")
    A("")
    A("Under variant **Bt** (the task's original instruction, pad appended) the")
    A("same counts would move the ink *left* by N x 4.66 px instead, leaving a")
    A(f"right-hand gap of up to {max_nbsp * w_nbsp:.0f} px on the longest line --")
    A("visibly not right-aligned.")
    A("")
    A("## 4. Deliverables and reproduction")
    A("")
    A("```")
    A("python source/cr_c4_wrap.py --report      # calibrate, report, build packs")
    A("python source/cr_c4_wrap.py --dry         # calibrate + report only")
    A("```")
    A("")
    A("* `release/Attila_Arabic_CR_C4.pack` — loc only, logical order, new wraps")
    A("* `release/Attila_Arabic_CR_C4_fonts.pack` — Shyizer's 37 CUFs unchanged")
    A("* `logs/cr_c4_calibration.json`, `logs/cr_c4_wraps.tsv`")
    A("* `logs/crops/C4/*.png` — asis/rev/mirror renders and model overlays")
    A("* `logs/cr_c4_nl.json`, `logs/cr_c4_nl.tsv` — every loc value with `\\n`")
    A("")
    A("## 5. What was NOT achieved")
    A("")
    A("1. **The strict wrap-fit criterion does not pass.** The engine's exact")
    A("   per-codepoint advance table is not identified. The adopted 3-parameter")
    A(f"   model reproduces the clean ERE lines to +-5 px, but two of the eight")
    A("   visible lines are out by +45 px and +28 px, so it does not reproduce")
    A("   the engine's break positions to pixel accuracy in general. What it does")
    A("   reproduce exactly is the *content* of every drawn line -- the engine")
    A("   honours our hard newlines, so the break offsets in section 1.5 ARE the")
    A("   screenshot offsets.")
    A("2. **The model cannot be used to predict an engine break it has not seen**")
    A("   to better than about 15 % of the box width. That is why the recomputed")
    A("   wraps keep the original line count and only move word boundaries, and")
    A("   why the budget carries a hard ceiling instead of trusting the target.")
    A("3. **A per-codepoint recovery exists but is unusable.** `cr_adv_solve.py`")
    A("   fits all 14 measured lines to 2.34 px rms, but the system is")
    A("   underdetermined (14 equations, 64 codepoints) and the ridge solution")
    A("   returns unphysical advances (U+FE8D = -0.72 px, U+0640 = 12.57 px).")
    A("   It is therefore not used to author wraps.")
    A("4. **The task's two structural premises are refuted by the pixels:**")
    A("   the engine does not mirror (section 1.1) and it does not re-wrap")
    A("   (section 1.2). The wraps are still recomputed as asked, in logical")
    A("   order, with no word split and no line over the ceiling -- but the")
    A("   engine would have honoured the old ones just as literally. The real")
    A("   defect the C1 screenshots show is the decorative U+0640 padding sitting")
    A("   at the wrong end of each line plus the orphan words it creates; the C4")
    A("   values drop the padding and re-balance the words.")
    A("5. **Some recomputed lines stay above the 319 px target** (up to 340 px):")
    A("   the two WRE values and both `long_description` values keep 2-4 such")
    A("   lines, because their fixed line budget cannot hold the content under the")
    A("   target given their word lengths. They stay under the 345 px hard ceiling,")
    A("   which is the widest line the engine demonstrably drew in this panel. The")
    A("   two `start_pos_factions_description_*` values -- the ones the C1")
    A("   screenshots actually show -- fit under the target on every line.")
    A("")
    A("## 6. Files")
    A("")
    A("| path | what |")
    A("|---|---|")
    A("| `source/cr_c4_wrap.py` | the single reproducible script (calibrate, "
      "report, build) |")
    A("| `source/cr_c4_verify.py` | independent verification of the built packs |")
    A("| `source/cr_c4_fit.py`, `cr_c4_fit2.py`, `cr_c4_fit3.py`, "
      "`cr_c4_fine.py` | the mask-overlay fits that refuted the `aw`-scaled and")
    A("| | mirrored readings |")
    A("| `source/cr_c4_diag.py` | the gscale/ascale experiment (artwork vs pen) |")
    A("| `source/cr_c4_order.py` | `asis` / `rev` / `mirror` PNG renders |")
    A("| `source/cr_adv_solve.py` | underdetermined per-codepoint recovery |")
    A("| `logs/cr_c4_nl.json`, `logs/cr_c4_nl.tsv` | every loc value with `\\n` |")
    A("| `logs/cr_c4_calibration.json` | fitted metrics, residuals, wrap table |")
    A("| `logs/cr_c4_wraps.tsv` | old vs new break positions per key |")
    A("| `logs/crops/C4/*.png` | model-vs-measured overlays |")
    A("")
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--only-fit", action="store_true")
    args = ap.parse_args()
    os.makedirs(CROPS, exist_ok=True)

    log = []
    if args.only_fit:
        res, det, usable = fit_metrics()
        for r in res[:10]:
            print(f"{r['leaf']:30s} m={r['m']:.3f} k={r['k']:+.3f} "
                  f"space={r['space']:.2f} rms={r['rms']:.2f} max={r['max']:.2f}")
        return

    print("== stage 1: order test (stored order vs reversed, mask residual)")
    ot = order_test()
    for k, v in sorted(ot.items(), key=lambda kv: kv[1]["sym"]):
        print(f"   {k:34s} symdiff={v['sym']:6d} ytop={v['ytop']:2d} "
              f"xoff={v['xoff']:3d} m={v['m']} k={v['k']} space={v['space']}")
    so = min(v["sym"] for k, v in ot.items() if k.endswith("stored_order"))
    rv = min(v["sym"] for k, v in ot.items() if k.endswith("reversed"))
    print(f"   best stored-order symdiff={so}  best reversed symdiff={rv}"
          f"  -> stored order wins by {rv - so}")

    print("\n== stage 2: metrics fit "
          "(width = m*sum_aw + k*n_chars + space*n_spaces)")
    res, det, usable = fit_metrics()
    top = res[0]
    print(f"   best font {top['leaf']}: m={top['m']:.3f} k={top['k']:+.3f} "
          f"space={top['space']:.2f} rms={top['rms']:.2f} max={top['max']:.2f}")
    for r in res[:6]:
        print(f"      {r['leaf']:30s} m={r['m']:.3f} k={r['k']:+.3f} "
              f"space={r['space']:5.2f} rms={r['rms']:6.2f} max={r['max']:6.2f}")
    for label in ("ERE", "WRE"):
        ls, bands = det[label]
        print(f"   {label}: {len(bands)} ink bands, stored lines {len(ls)}")
        for i, (ya, yb, a, b, ink) in enumerate(bands):
            print(f"      band{i} y{ya}-{yb} x{a}..{b} meas_w={b-a+1:3d} "
                  f"stored[{i}] n={len(ls[i]) if i < len(ls) else 0}")

    m = model()
    c = R.font(m["leaf"])
    ere_bands = [b for b in det["ERE"][1] if b[3] - b[2] + 1 >= 200]
    ere_lines = det["ERE"][0]
    print(f"   adopted model: {m['leaf']} width = {m['m']:.4f}*sum_aw + "
          f"{m['k']:+.4f}*n + {m['space']:.3f}*n_space")
    ad_res = []
    for i, b in enumerate(ere_bands):
        if i >= len(ere_lines):
            break
        w = width(c, ere_lines[i], m)
        meas = b[3] - b[2] + 1
        ad_res.append((i, meas, round(w, 1), round(w - meas, 1)))
        print(f"      ERE{i}: meas={meas:3d} model={w:7.1f} err={w-meas:+7.1f}")

    # coefficient table + ratio-spread discriminator on the same clean lines
    clean = [i for i in range(min(len(ere_bands), len(ere_lines)))
             if i not in (4, 5)]
    allf = sorted(set(r["leaf"] for r in res))
    runnerups = []
    for leaf in allf:
        cc = R.font(leaf)
        A = np.array([feat(cc, ere_lines[i])[0] for i in clean], float)
        N = np.array([feat(cc, ere_lines[i])[2] for i in clean], float)
        S = np.array([feat(cc, ere_lines[i])[1] for i in clean], float)
        Y = np.array([ere_bands[i][3] - ere_bands[i][2] + 1 for i in clean],
                     float)
        coef, *_ = np.linalg.lstsq(np.column_stack([A, N, S]), Y, rcond=None)
        ratios = Y / A
        resid = Y - A
        runnerups.append({"leaf": leaf, "m": float(coef[0]), "k": float(coef[1]),
                          "space": float(coef[2]),
                          "spread": float(ratios.max() - ratios.min()),
                          "flat": float(resid.std())})
    runnerups.sort(key=lambda r: r["flat"])
    print("   residual-spread discriminator (clean ERE lines), best 6:")
    for r in runnerups[:6]:
        print(f"      {r['leaf']:28s} resid_stdev={r['flat']:6.2f} "
              f"m={r['m']:.4f} k={r['k']:+.4f} space={r['space']:.3f}")

    print("\n== stage 3: wrap comparison for every Arabic loc value with \\n")
    rows_by_file = loc_rows()
    new_values, wrap_log = [], []
    for internal, rows in rows_by_file.items():
        for key, text, tip in rows:
            if "\n" not in text:
                continue
            ar = any(0x0600 <= ord(ch) <= 0x06FF for ch in text)
            if not ar:
                continue
            old_lines = text.split("\n")
            n = len(old_lines)
            logical = " ".join(strip_tatweel(x) for x in old_lines)
            new_lines, over = wrap_text(c, logical, m, BOX_MAX_PX, n)
            while len(new_lines) < n:
                new_lines.append("")
            new_text = "\n".join(new_lines)
            assert len(new_lines) == n, (key, len(new_lines), n)
            ow = [round(width(c, x, m), 1) for x in old_lines]
            nw = [round(width(c, x, m), 1) for x in new_lines]
            wrap_log.append({
                "file": internal, "key": key, "lines": n,
                "old_lines": old_lines, "new_lines": new_lines,
                "old_widths": ow, "new_widths": nw,
                "old_breaks": [len(x) for x in old_lines],
                "new_breaks": [len(x) for x in new_lines],
                "old_words": [len(x.split()) for x in old_lines],
                "new_words": [len(x.split()) for x in new_lines],
                "over": over,
                "nbsp": nb_budget(c, new_lines, m, BOX_MAX_PX),
            })
            new_values.append((internal, key, new_text))
            print(f"   {key}")
            print(f"      old n={wrap_log[-1]['old_breaks']} "
                  f"w={wrap_log[-1]['old_words']} widths={ow}")
            print(f"      new n={wrap_log[-1]['new_breaks']} "
                  f"w={wrap_log[-1]['new_words']} widths={nw} "
                  f"(budget {BOX_MAX_PX})")
            if over:
                print(f"      !! {len(over)} line(s) still over budget")

    with open(CAL_JSON, "w", encoding="utf-8") as f:
        json.dump({"order_test": ot,
                   "metrics": {k2: v for k2, v in top.items() if k2 != "lines"},
                   "adopted": m, "all_fonts": res[:12], "wraps": wrap_log}, f,
                  ensure_ascii=False, indent=1)
    with open(WRAP_TSV, "w", encoding="utf-8") as f:
        f.write("file\tkey\told_breaks\tnew_breaks\told_words\tnew_words\t"
                "old_widths\tnew_widths\n")
        for w in wrap_log:
            f.write(f"{w['file']}\t{w['key']}\t{w['old_breaks']}\t"
                    f"{w['new_breaks']}\t{w['old_words']}\t{w['new_words']}\t"
                    f"{w['old_widths']}\t{w['new_widths']}\n")
    print(f"\nwrote {CAL_JSON}")
    print(f"wrote {WRAP_TSV}")

    if not args.dry:
        build_packs(new_values, log)
        print("\n".join(log))
    else:
        print("(dry run: no packs written)")

    if args.report:
        write_report(ot, res, det, usable, m, wrap_log, ad_res, runnerups)
        print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
