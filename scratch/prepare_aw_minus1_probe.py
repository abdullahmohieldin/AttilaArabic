#!/usr/bin/env python3
"""Create and run a non-destructive CUF alloc_width = width - 1 probe.

Run from the AttilaArabic repository root, for example:
    cd /d D:\\AttilaArabic
    tools\\venv\\Scripts\\python scratch\\prepare_aw_minus1_probe.py

This writes source/cr_phase1_build_v16_awminus1.py (a derived test builder),
then runs it. The original production builder is not edited. Only a uniquely
named fonts pack is built; the localization pack is not rebuilt. Because the
project pre-shapes text into visual order, the probe shortens advances for
FINAL/MEDIAL/tatweel forms whose right edge joins the next rendered glyph; it
does not shorten INITIAL-form advances at the ends of visual-order runs.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one occurrence for {label}; found {count}. No test builder was written.")
    return source.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="AttilaArabic repository root (default: current directory)")
    parser.add_argument("--no-build", action="store_true", help="Generate the test builder but do not execute it")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    original_path = root / "source" / "cr_phase1_build.py"
    test_path = root / "source" / "cr_phase1_build_v16_awminus1.py"

    if not original_path.is_file():
        print(f"ERROR: cannot find {original_path}", file=sys.stderr)
        print("Run this from the AttilaArabic repo root or pass --repo-root.", file=sys.stderr)
        return 2
    if test_path.exists():
        # Remove old test builder if regenerating
        test_path.unlink()

    src = original_path.read_text(encoding="utf-8")

    # Count all generated joining forms for each font, for repeatable build logs.
    src = replace_once(
        src,
        "        for cp in sorted(set(arabic_cps)):\n",
        "        advance_probe_count = 0\n        for cp in sorted(set(arabic_cps)):\n",
        "Arabic glyph loop counter",
    )
    src = replace_once(
        src,
        '            is_conn_right = ("FINAL" in form_name or "MEDIAL" in form_name or cp == 0x0640)\n',
        '            is_conn_right = ("FINAL" in form_name or "MEDIAL" in form_name or cp == 0x0640)\n'
        "            # Pre-shaped text is in visual order; only the right edge joins the next rendered glyph.\n"
        "            is_connecting_form = is_conn_right\n",
        "visual-order joining-form classification",
    )
    src = replace_once(
        src,
        "            glyph_idx = len(new_dims)\n"
        "            new_dims.append((cell_ah, w, w, cell_h))\n"
        "            new_bitmaps.append(bytes(cell_bm))\n"
        "            new_table[cp] = glyph_idx\n",
        "            # V16 probe: shorten only the allocated advance; preserve bitmap width.\n"
        "            alloc_w = max(1, w - 1) if is_connecting_form else w\n"
        "            if is_connecting_form:\n"
        "                advance_probe_count += 1\n"
        "            glyph_idx = len(new_dims)\n"
        "            new_dims.append((cell_ah, alloc_w, w, cell_h))\n"
        "            new_bitmaps.append(bytes(cell_bm))\n"
        "            new_table[cp] = glyph_idx\n",
        "Arabic glyph advance assignment",
    )
    src = replace_once(
        src,
        "        # 2. Append Round 3 Binary Blank Spacer Glyphs\n",
        '        print(f"  {fname}: alloc_width reduced for {advance_probe_count} right-joining glyphs")\n\n'
        "        # 2. Append Round 3 Binary Blank Spacer Glyphs\n",
        "per-font diagnostics",
    )
    src = replace_once(
        src,
        '    out_font_pack = os.path.join(OUT_DIR, "Attila_Arabic_Phase1_fonts.pack")\n',
        '    out_font_pack = os.path.join(OUT_DIR, "Attila_Arabic_Phase1_fonts_v16_awminus1.pack")\n',
        "unique output pack name",
    )

    # Avoid touching/rebuilding the localization pack; this test concerns fonts only.
    main_start = src.rfind("def main():")
    entry_start = src.rfind('if __name__ == "__main__":')
    if main_start < 0 or entry_start < 0 or main_start >= entry_start:
        raise RuntimeError("Could not safely locate main() entry point; no test builder was written.")
    test_main = '''def main():
    print("==================================================")
    print("TOTAL WAR: ATTILA — ARABIC LOCALIZATION")
    print("V16 MICRO-TEST — alloc_width = width - 1 for right-joining forms")
    print("==================================================")
    f_pack, f_hash = build_fonts()
    print("\\n--- V16 Advance-Overhang Probe ---")
    print(f"Test fonts pack: {f_pack}")
    print(f"SHA-256: {f_hash}")
    print("Localization pack was not rebuilt.")


'''
    src = src[:main_start] + test_main + src[entry_start:]

    test_path.write_text(src, encoding="utf-8")
    print(f"Created test-only builder: {test_path}")
    print("Original source/cr_phase1_build.py was not modified.")

    if args.no_build:
        print("--no-build specified; test builder was generated but not run.")
        return 0

    print("Running font-only probe build...")
    subprocess.run([sys.executable, str(test_path)], cwd=str(root), check=True)
    print("\nProbe pack generated. Do not deploy it alongside another pack overriding the same font paths.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: probe build failed with exit code {exc.returncode}.", file=sys.stderr)
        raise SystemExit(exc.returncode)
