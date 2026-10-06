#!/usr/bin/env python3
"""Minimal .loc codec (Attila/English), layout per rpfm_lib::files::loc.

Header (14 bytes): u16 BOM 0xFEFF-as-read-LE? -> bytes FF FE (VERIFIED),
  b'LOC', u8 0, i32 version=1, u32 count.
Per entry: u16 char-count + UTF-16LE key, u16 char-count + UTF-16LE text,
  u8 tooltip flag.

Usage: loc.py info|roundtrip|tsv-export|tsv-import ...
"""
import csv
import struct
import sys


def decode(data: bytes):
    assert data[0:2] == b"\xff\xfe", data[0:4]
    assert data[2:5] == b"LOC", data[2:6]
    assert data[5] == 0
    ver, = struct.unpack_from("<i", data, 6)
    assert ver == 1, ver
    n, = struct.unpack_from("<I", data, 10)
    pos, rows = 14, []
    for _ in range(n):
        lk, = struct.unpack_from("<H", data, pos)
        pos += 2
        key = data[pos:pos + 2 * lk].decode("utf-16-le")
        pos += 2 * lk
        lt, = struct.unpack_from("<H", data, pos)
        pos += 2
        text = data[pos:pos + 2 * lt].decode("utf-16-le")
        pos += 2 * lt
        tip = data[pos]
        pos += 1
        rows.append((key, text, tip))
    return rows, pos, len(data)


def encode(rows) -> bytes:
    out = bytearray(b"\xff\xfeLOC\x00")
    out += struct.pack("<iI", 1, len(rows))
    for key, text, tip in rows:
        kb, tb = key.encode("utf-16-le"), text.encode("utf-16-le")
        assert len(kb) // 2 == len(key) and len(tb) // 2 == len(text), \
            "surrogate pair in key/text (unhandled)"
        out += struct.pack("<H", len(key)) + kb
        out += struct.pack("<H", len(text)) + tb
        out += struct.pack("<B", tip)
    return bytes(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "info":
        raw = open(sys.argv[2], "rb").read()
        rows, pos, total = decode(raw)
        print(f"entries={len(rows)} consumed={pos}/{total} exact={pos == total}")
        for k, t, tip in rows[:5]:
            print(f"  [{tip}] {k} = {t[:80]!r}")
    elif cmd == "roundtrip":
        raw = open(sys.argv[2], "rb").read()
        enc = encode(decode(raw)[0])
        open(sys.argv[3], "wb").write(enc)
        print(f"src={len(raw)} enc={len(enc)} identical={enc == raw}")
    elif cmd == "tsv-export":
        rows, _, _ = decode(open(sys.argv[2], "rb").read())
        with open(sys.argv[3], "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t")
            w.writerow(["key", "text", "tooltip"])
            w.writerows(rows)
        print(f"exported {len(rows)} rows")
