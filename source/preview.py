#!/usr/bin/env python3
"""preview.py — offline CUF text rendering and baseline verification tool.

Draws each glyph from a CUF font at its advance on a baseline line,
drawing the baseline in red (255, 0, 0).

Usage:
  python source/preview.py --font <font.cuf> --text '<text>' --output docs/<name>.png
"""
import argparse
import os
import sys
from PIL import Image, ImageDraw

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = r"D:\AttilaArabic"
sys.path.insert(0, os.path.join(BASE, "source"))
from cuf import CUF  # noqa: E402
from shape import shape  # noqa: E402


def render_cuf_preview(font_path, text, output_path, scale=4, cell_borders=False):
    c = CUF.decode(open(font_path, "rb").read())
    base_row = c.props["baseline"] - 1
    v_size = c.props["v_size"]

    # Pre-shape text into visual RTL order
    visual = shape(text)

    # Collect glyphs and calculate dimensions
    glyphs = []
    total_w = 0
    for ch in visual:
        cp = ord(ch)
        code = c.table[cp]
        if code >= len(c.dims) or c.dims[code][0] == -128:
            # fallback to space
            sp_code = c.table[0x20]
            adv = c.dims[sp_code][1] if sp_code < len(c.dims) else 6
            glyphs.append((None, adv, 0, 0, b""))
            total_w += adv
            continue
        ah, aw, w, h = c.dims[code]
        bm = c.bitmaps[code]
        glyphs.append((code, aw, w, h, bm))
        total_w += aw

    margin_x = 12
    margin_y = 12
    canvas_w = total_w + margin_x * 2
    canvas_h = v_size + margin_y * 2

    # Dark background for high contrast
    img = Image.new("RGB", (canvas_w, canvas_h), (25, 25, 28))
    draw = ImageDraw.Draw(img)

    base_y = margin_y + base_row

    # Draw cell borders if requested
    if cell_borders:
        cx = margin_x
        for code, aw, w, h, bm in glyphs:
            draw.rectangle(
                [(cx, margin_y), (cx + aw - 1, margin_y + v_size - 1)],
                outline=(50, 70, 90),
                width=1,
            )
            cx += aw

    # Draw red baseline line
    draw.line([(0, base_y), (canvas_w, base_y)], fill=(255, 50, 50), width=1)

    cur_x = margin_x
    for code, aw, w, h, bm in glyphs:
        if code is None:
            cur_x += aw
            continue

        glyph_base_row = base_row + (h - v_size)
        top_y = base_y - glyph_base_row

        for y in range(h):
            row_offset = y * w
            for x in range(w):
                alpha = bm[row_offset + x]
                if alpha > 0:
                    px_x = cur_x + x
                    px_y = top_y + y
                    if 0 <= px_x < canvas_w and 0 <= px_y < canvas_h:
                        orig = img.getpixel((px_x, px_y))
                        # Alpha blend white glyph over canvas
                        blended = (
                            min(255, orig[0] + alpha),
                            min(255, orig[1] + alpha),
                            min(255, orig[2] + alpha),
                        )
                        img.putpixel((px_x, px_y), blended)
        cur_x += aw

    # Scale up with nearest-neighbor to allow crisp pixel inspection
    scaled = img.resize((canvas_w * scale, canvas_h * scale), Image.Resampling.NEAREST)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scaled.save(output_path)
    print(f"Rendered '{text}' -> {output_path} ({scaled.width}x{scaled.height}px, base_y={base_y*scale}px)")


def main():
    parser = argparse.ArgumentParser(description="Render text preview from CUF font with baseline")
    parser.add_argument("--font", required=True, help="Path to CUF font")
    parser.add_argument("--text", required=True, help="Logical Arabic text to render")
    parser.add_argument("--output", required=True, help="Output PNG file path")
    parser.add_argument("--scale", type=int, default=4, help="Upscale factor (default 4)")
    parser.add_argument("--cell-borders", action="store_true", help="Draw cell borders around glyphs")
    args = parser.parse_args()

    render_cuf_preview(args.font, args.text, args.output, scale=args.scale, cell_borders=args.cell_borders)


if __name__ == "__main__":
    main()
