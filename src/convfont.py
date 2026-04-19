import fontforge
import re

FONT_W = 32
FONT_H = 48
PIXEL = 20  # scale

INPUT_FILE = "BadPixel.h"
OUTPUT_FILE = "BadPixel.ttf"

font = fontforge.font()
# --- FONT IDENTITY (VERY IMPORTANT FOR LINUX + LIBREOFFICE) ---
font.familyname = "BadPixel"
font.fontname = "BadPixel-Regular"
font.fullname = "BadPixel Regular"
font.weight = "Regular"
font.version = "1.2"

font.encoding = "UnicodeFull"

# Metrics (adjust if needed)
font.em = 1000
font.ascent = 40 * PIXEL
font.descent = 8 * PIXEL

with open(INPUT_FILE) as f:
    content = f.read()

glyphs = re.findall(
    r'static const uint8_t BadPixel_([0-9A-F]{4})\[\d+\] = \{([^}]*)\};',
    content,
    re.MULTILINE
)

for hexcode, data in glyphs:
    cp = int(hexcode, 16)

    bytes_list = [int(x.strip(), 16) for x in data.split(",") if x.strip()]
    if len(bytes_list) != (FONT_W // 8) * FONT_H:
        continue

    g = font.createChar(cp)
    pen = g.glyphPen()

    min_x = FONT_W
    max_x = -1

    # --- draw pixels + find bounds ---
    for y in range(FONT_H):
        for byte in range(FONT_W // 8):
            b = bytes_list[y * (FONT_W // 8) + byte]

            for bit in range(8):
                if (b >> (7 - bit)) & 1:
                    x = byte * 8 + bit

                    min_x = min(min_x, x)
                    max_x = max(max_x, x)

    # --- special case: space ---
    if cp == 32 or max_x < min_x:
        g.width = int(FONT_W * PIXEL * 0.5)
        continue

    # --- draw again, shifted to remove left padding ---
    for y in range(FONT_H):
        for byte in range(FONT_W // 8):
            b = bytes_list[y * (FONT_W // 8) + byte]

            for bit in range(8):
                if (b >> (7 - bit)) & 1:
                    x = byte * 8 + bit

                    # shift left by min_x
                    px = (x - min_x) * PIXEL
                    py = (FONT_H - y) * PIXEL

                    pen.moveTo((px, py))
                    pen.lineTo((px + PIXEL, py))
                    pen.lineTo((px + PIXEL, py - PIXEL))
                    pen.lineTo((px, py - PIXEL))
                    pen.closePath()

    # --- set width with padding ---
    glyph_width = (max_x - min_x + 1) * PIXEL
    g.width = glyph_width + PIXEL * 3  # 1.5px padding on each side

    # optional cleanup
    g.removeOverlap()

font.generate(OUTPUT_FILE)
