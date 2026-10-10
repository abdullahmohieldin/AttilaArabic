#!/usr/bin/env python3
"""Run the surface fit (cr_fit_surface) with a shortlist of fonts."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cr_fit_surface as F   # noqa: E402

SHORT = ["arialunicode_12.cuf",
         "georgia_italic_12.cuf", "georgia_italic_14.cuf", "georgia_italic_16.cuf",
         "la_gioconda_12.cuf", "la_gioconda_14.cuf", "la_gioconda_16.cuf",
         "la_gioconda_uppercase_12.cuf", "la_gioconda_uppercase_14.cuf",
         "la_gioconda_uppercase_16.cuf"]

if __name__ == "__main__":
    names = sys.argv[1:] or list(F.LINES)
    for n in names:
        F.run_line(n, SHORT, F.SCALES, taxes=(0, 1, 2), top=6)
