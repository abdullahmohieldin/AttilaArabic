#!/usr/bin/env python3
"""CUF codec v2 for the Attila Arabic POC (fail-fast experiment).

Attila variant layout (empirically derived, VERIFIED by exact byte-fit on
two vanilla fonts — see docs/cuf-investigation notes):
  magic CUF0|CUF1 (both occur in Attila's local_en.pack)
  11x u16 props | u16 count N | u32 bitmap_bytes
  65536x u16 char->code table (0xFFFF = unused; unmapped chars ALIAS a
    default glyph code instead of using a sentinel; 1-2 dangling codes
    equal to N exist for PUA/noncharacter chars)
  N x 4B dims (i8 alloc_h, u8 alloc_w, u8 w, u8 h) in code order
  N x u32 bitmap offsets (cumulative)
  bitmap bytes (sum(w*h) == bitmap_bytes)
  tail: kerning (u16 ksize, u16 skip, ksize*ksize bytes) or empty

Differs from RPFM/Empire layout ONLY in that the table has (almost) no
0xFFFF entries — RPFM reads dims per *mapped char* and therefore overreads
on Attila files. RPFM also gate-keeps magic == CUF0.

Usage: cuf.py info|coverage|roundtrip|addglyph ...
"""
import struct
import sys

PROP_NAMES = [
    "first_prop", "second_prop", "line_height", "fourth_prop", "fifth_prop",
    "baseline", "layout_y_offset", "space_justify", "layout_x_offset",
    "h_size", "v_size",
]

ARABIC_RANGES = {
    "Arabic U+0600-U+06FF": (0x0600, 0x06FF),
    "Arabic Supplement U+0750-U+077F": (0x0750, 0x077F),
    "Arabic Ext-A U+08A0-U+08FF": (0x08A0, 0x08FF),
    "Pres Forms-A U+FB50-U+FDFF": (0xFB50, 0xFDFF),
    "Pres Forms-B U+FE70-U+FEFF": (0xFE70, 0xFEFF),
}


class CUF:
    def __init__(self):
        self.magic = b"CUF1"
        self.props = {}
        self.count = 0
        self.size = 0
        self.table = []
        self.dims = []     # list per code 0..N-1 of (ah, aw, w, h)
        self.bitmaps = []  # list per code of bytes
        self.tail = b""

    @classmethod
    def decode(cls, data: bytes):
        if data[0:4] not in (b"CUF0", b"CUF1"):
            raise ValueError(f"bad magic: {data[0:4]!r}")
        c = cls()
        c.magic = data[0:4]
        c.props = dict(zip(PROP_NAMES, struct.unpack_from("<11H", data, 4)))
        c.count, = struct.unpack_from("<H", data, 26)
        c.size, = struct.unpack_from("<I", data, 28)
        c.table = list(struct.unpack_from("<65536H", data, 32))
        pos = 32 + 131072
        c.dims = []
        for _ in range(c.count):
            ah, aw, w, h = struct.unpack_from("<b3B", data, pos)
            pos += 4
            c.dims.append((ah, aw, w, h))
        c.offsets = []
        for _ in range(c.count):
            o, = struct.unpack_from("<I", data, pos)
            pos += 4
            c.offsets.append(o)
        c.bitmaps = []
        for (ah, aw, w, h) in c.dims:
            n = w * h
            c.bitmaps.append(data[pos:pos + n])
            pos += n
        c.bitmap_end = pos
        c.tail = data[pos:]
        c.total = len(data)
        return c

    def bitmap_total(self):
        return sum(w * h for (_, _, w, h) in self.dims)

    def parse_tail(self):
        if not self.tail:
            return ("empty",)
        ks, skip = struct.unpack_from("<HH", self.tail, 0)
        expect = 4 + ks * ks
        return (f"ksize={ks} skip={skip} tail_len={len(self.tail)} "
                f"expect={expect} match={expect == len(self.tail)}")

    def encode(self) -> bytes:
        out = bytearray()
        out += self.magic
        out += struct.pack("<11H", *[self.props[n] for n in PROP_NAMES])
        out += struct.pack("<H", len(self.dims))
        out += struct.pack("<I", sum(len(b) for b in self.bitmaps))
        out += struct.pack("<65536H", *self.table)
        for (ah, aw, w, h) in self.dims:
            out += struct.pack("<b3B", ah, aw, w, h)
        off = 0
        for b in self.bitmaps:
            # VERIFIED vanilla convention: cumulative running offset for ALL
            # glyphs (empty glyphs point at the next glyph's start).
            # (Differs from RPFM's Empire convention of 0 for fully-empty.)
            out += struct.pack("<I", off)
            off += len(b)
        for b in self.bitmaps:
            out += b
        out += self.tail
        return bytes(out)


def cmd_info(path):
    data = open(path, "rb").read()
    c = CUF.decode(data)
    print(f"file: {path} size={len(data)} magic={c.magic!r}")
    print("props:", " ".join(f"{k}={v}" for k, v in c.props.items()))
    print(f"count={c.count} declared_size={c.size} "
          f"sum(w*h)={c.bitmap_total()} match={c.bitmap_total() == c.size}")
    print(f"bitmap_end={c.bitmap_end} total={c.total} tail_extra={c.total - c.bitmap_end}")
    print("tail:", c.parse_tail())
    # offsets canonical?
    canon, off = True, 0
    for i, b in enumerate(c.bitmaps):
        if len(b) == 0:
            if c.offsets[i] != 0:
                canon = False
        elif c.offsets[i] != off:
            canon = False
        off += len(b)
    print(f"offsets canonical (RPFM convention): {canon}")


def cmd_roundtrip(src, dst):
    data = open(src, "rb").read()
    enc = CUF.decode(data).encode()
    open(dst, "wb").write(enc)
    print(f"src={len(data)} enc={len(enc)} identical={enc == data}")


def cmd_coverage(path):
    data = open(path, "rb").read()
    c = CUF.decode(data)
    print(f"codes: {c.count}, mapped table entries: "
          f"{sum(1 for v in c.table if v != 0xFFFF)}")
    for name, (lo, hi) in ARABIC_RANGES.items():
        codes = {c.table[i] for i in range(lo, hi + 1)} - {0xFFFF}
        n_real = sum(1 for i in range(lo, hi + 1)
                     if c.table[i] != 0xFFFF and c.table[i] < c.count)
        print(f"  {name}: distinct codes referenced={len(codes)} "
              f"in-range={n_real}/{hi - lo + 1}")


if __name__ == "__main__":
    if sys.argv[1] == "info":
        cmd_info(sys.argv[2])
    elif sys.argv[1] == "coverage":
        cmd_coverage(sys.argv[2])
    elif sys.argv[1] == "roundtrip":
        cmd_roundtrip(sys.argv[2], sys.argv[3])
