#!/usr/bin/env python3
"""Screenshot helpers for the clean-room analysis.

  cr_shots.py overview <outdir> <shot>...      downscale whole screenshots
  cr_shots.py crop <out> <shot> X0 Y0 X1 Y1 [zoom]
"""
import os
import sys

from PIL import Image

BASE = r"D:\AttilaArabic"
SHOTS = os.path.join(BASE, "screenshots")


def newest(n=5):
    fs = [os.path.join(SHOTS, f) for f in os.listdir(SHOTS)
          if f.lower().endswith(".png")]
    fs.sort(key=os.path.getmtime)
    return fs[-n:]


def main():
    cmd = sys.argv[1]
    if cmd == "overview":
        outdir = sys.argv[2]
        os.makedirs(outdir, exist_ok=True)
        shots = sys.argv[3:] or newest(5)
        for p in shots:
            im = Image.open(p).convert("RGB")
            w, h = im.size
            s = 1400 / w
            im2 = im.resize((1400, int(h * s)), Image.LANCZOS)
            tag = os.path.basename(p).split(" - ")[-1].replace(".png", "")
            out = os.path.join(outdir, f"ov_{tag}.png")
            im2.save(out)
            print(f"{out}  ({w}x{h} -> {im2.size[0]}x{im2.size[1]})")
    elif cmd == "crop":
        out = sys.argv[2]
        p = sys.argv[3]
        x0, y0, x1, y1 = (int(v) for v in sys.argv[4:8])
        zoom = int(sys.argv[8]) if len(sys.argv) > 8 else 4
        im = Image.open(p).convert("RGB")
        sub = im.crop((x0, y0, x1, y1))
        sub = sub.resize((sub.width * zoom, sub.height * zoom), Image.NEAREST)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sub.save(out)
        print(f"{out}  src=({x0},{y0})-({x1},{y1}) zoom={zoom} "
              f"size={sub.size[0]}x{sub.size[1]}")


if __name__ == "__main__":
    main()
