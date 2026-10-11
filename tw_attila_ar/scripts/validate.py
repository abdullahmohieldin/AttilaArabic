#!/usr/bin/env python3
"""Batch Translation Validator for Total War: Attila Arabic Localization

Validates translation batches against spec rules:
- 1:1 format placeholder parity (%s, %d, {0})
- No stray Latin characters outside allowlist (e.g. [[col:...]], [[url:...]], [[rgba:...]], <P1>..)
- No Presentation Forms-B or pre-shaped/reversed text in translation layer (logical Arabic only)
- Length ratio verification and warning flags
- Valid JSON / JSONL structure
"""
import re
import sys
import json
from typing import Tuple, List, Dict, Any

PLACEHOLDER_RE = re.compile(r"(\%[0-9]*[sdif]|(?:\{[0-9]+\}))")
TAG_RE = re.compile(r"\[\[[^\]]+\]\]|<P\d+>")
LATIN_RE = re.compile(r"[a-zA-Z]{2,}")
ALLOWLIST_LATIN = {
    "col", "url", "rgba", "br", "font", "b", "i", "u",
    "true", "false", "null", "none", "att", "ad", "bc", "p"
}


def validate_entry(entry: Dict[str, Any]) -> Tuple[bool, str]:
    eid = entry.get("id") or entry.get("key")
    if not eid:
        return False, "Missing entry ID or key"

    en = entry.get("en", "")
    ar = entry.get("ar", "")

    if not ar.strip() and en.strip():
        return False, f"Empty Arabic translation for key '{eid}'"

    # 1. Reject Presentation Forms-B in translation layer
    forms_b_chars = [c for c in ar if 0xFE70 <= ord(c) <= 0xFEFF]
    if forms_b_chars:
        return False, f"Presentation Forms-B detected in translation layer ({len(forms_b_chars)} characters: {[hex(ord(c)) for c in forms_b_chars[:5]]})"

    # 2. Placeholder parity check
    en_phs = PLACEHOLDER_RE.findall(en)
    ar_phs = PLACEHOLDER_RE.findall(ar)
    if sorted(en_phs) != sorted(ar_phs):
        return False, f"Placeholder mismatch: EN={en_phs} vs AR={ar_phs}"

    # 3. Stray Latin check outside allowlist
    # Strip known tags first
    cleaned_ar = TAG_RE.sub(" ", ar)
    latin_words = LATIN_RE.findall(cleaned_ar)
    stray_latins = [w for w in latin_words if w.lower() not in ALLOWLIST_LATIN]
    if stray_latins:
        return False, f"Latin leftover detected outside allowlist: {stray_latins}"

    # 4. Length-ratio anomaly flag (warning/check)
    if len(en) > 20 and len(ar) < len(en) * 0.15:
        return False, f"Length ratio anomaly: AR length {len(ar)} is <15% of EN length {len(en)}"

    return True, "Valid"


def validate_batch(entries: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    errors = []
    seen_ids = set()

    for idx, e in enumerate(entries):
        eid = e.get("id") or e.get("key")
        if eid in seen_ids:
            errors.append(f"Row {idx}: Duplicate ID '{eid}'")
        seen_ids.add(eid)

        valid, msg = validate_entry(e)
        if not valid:
            errors.append(f"Row {idx} ({eid}): {msg}")

    return len(errors) == 0, errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py <batch.jsonl>")
        sys.exit(1)

    fpath = sys.argv[1]
    entries = []
    with open(fpath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    ok, errs = validate_batch(entries)
    if ok:
        print(f"PASS: {len(entries)} entries validated successfully.")
        sys.exit(0)
    else:
        print(f"FAIL: {len(errs)} validation errors found:")
        for err in errs[:10]:
            print(f"  - {err}")
        sys.exit(1)
