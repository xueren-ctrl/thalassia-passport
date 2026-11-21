#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws, fully offline with Pillow (bundled DejaVu fonts, stdlib fallback),
one open passport spread for the invented island Republic of Thalassia:
a data page with a portrait and a machine-readable strip, and a facing
visa page with arrival/departure stamps from neighbouring countries that
tell one consistent travel story (all after the 02 JUN 2024 issue date).

Output: /output/entry.png  (1024 x 1024, well under the 1 MiB cap)
"""
import math
import os
import sys

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
DESK = (58, 47, 40)
DESK_DARK = (44, 36, 31)
PAPER = (247, 242, 230)
PAPER_SHADOW = (210, 198, 172)
INK = (28, 32, 48)
INK_SOFT = (74, 78, 96)
RULE = (150, 138, 112)
GOLD = (176, 138, 62)
TEAL = (36, 96, 92)
TEAL_DARK = (24, 68, 66)
RED_INK = (168, 52, 44)
BLUE_INK = (38, 74, 138)
GREEN_INK = (34, 102, 66)
PURPLE_INK = (104, 64, 128)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAVE_PIL = True
except Exception:  # pragma: no cover - sandbox without Pillow
    HAVE_PIL = False


# ---------------------------------------------------------------- fonts
def _font(name, size):
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, name),
        os.path.join("/usr/share/fonts/truetype/dejavu", name),
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


class Fonts:
    def __init__(self):
        self.serif = lambda s: _font("DejaVuSerif.ttf", s)
        self.serif_b = lambda s: _font("DejaVuSerif-Bold.ttf", s)
        self.sans = lambda s: _font("DejaVuSans.ttf", s)
        self.sans_b = lambda s: _font("DejaVuSans-Bold.ttf", s)


F = Fonts()


def text_w(draw, s, font):
    box = draw.textbbox((0, 0), s, font=font)
    return box[2] - box[0]


def draw_text(draw, xy, s, font, fill=INK, anchor="la"):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor)


def centred(draw, cx, y, s, font, fill=INK):
    draw.text((cx, y), s, font=font, fill=fill, anchor="ma")


def label_value(draw, x, y, label, value, vfont=None, width=210):
    """One small-caps label above a bold value, with a hairline rule."""
    draw_text(draw, (x, y), label, F.sans(11), fill=INK_SOFT)
    draw_text(draw, (x, y + 14), value, vfont or F.sans_b(17), fill=INK)
    draw.line([(x, y + 36), (x + width, y + 36)], fill=RULE, width=1)


# ---------------------------------------------------------------- MRZ
_MRZ_VALUES = {}
for _i, _c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    _MRZ_VALUES[_c] = _i
_MRZ_VALUES["<"] = 0


def mrz_check(s):
    total = 0
    for i, ch in enumerate(s):
        total += _MRZ_VALUES[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    doc = "TH4829167"
    line1 = "P<THAMARLOW<<ELENA<SOFIA<<<<<<<<<<<<<<"
    line1 = line1[:44].ljust(44, "<")
    dob, sex, exp = "920314", "F", "340601"
    optional = "<<<<<<<<<<<<<<"
    head = doc + mrz_check(doc) + "THA" + dob + mrz_check(dob) + sex + exp
    head += mrz_check(exp) + optional
    composite = head[0:10] + head[13:20] + head[21:28] + head[28:42]
    line2 = head + mrz_check(composite) + "<"
    return line1, line2


# ---------------------------------------------------------------- portrait
def draw_portrait(draw, x, y, w, h):
    """Flat-illustration portrait: island marine biologist, teal backdrop."""
    draw.rectangle([x, y, x + w, y + h], fill=(46, 111, 106))
    # sun / sea bands behind the sitter
    draw.ellipse([x + w - 52, y + 12, x + w - 8, y + 56], fill=(233, 196, 106))
    for i, yy in enumerate(range(y + 118, y + h, 16)):
        draw.line([(x, yy), (x + w, yy + 6)], fill=(64, 130, 124), width=3)
    cx = x + w // 2
    # shoulders / jacket
    draw.polygon(
        [(cx - 62, y + h), (cx - 58, y + 158), (cx - 30, y + 138),
         (cx + 30, y + 138), (cx + 58, y + 158), (cx + 62, y + h)],
        fill=(38, 52, 84),
    )
    draw.polygon([(cx - 14, y + 140), (cx, y + 168), (cx + 14, y + 140)],
                 fill=(240, 236, 224))
    # neck and face
    draw.rectangle([cx - 11, y + 118, cx + 11, y + 142], fill=(214, 164, 120))
    draw.ellipse([cx - 34, y + 34, cx + 34, y + 128], fill=(232, 185, 141))
    # hair: dark sweep over the crown and sides
    draw.pieslice([cx - 38, y + 22, cx + 38, y + 96], 180, 360, fill=(52, 36, 28))
    draw.polygon([(cx - 38, y + 62), (cx - 30, y + 30), (cx - 12, y + 48),
                  (cx - 22, y + 74)], fill=(52, 36, 28))
    draw.polygon([(cx + 38, y + 62), (cx + 30, y + 30), (cx + 12, y + 48),
                  (cx + 22, y + 74)], fill=(52, 36, 28))
    # brows, eyes, nose, lips
    draw.line([(cx - 24, y + 76), (cx - 8, y + 74)], fill=(52, 36, 28), width=3)
    draw.line([(cx + 8, y + 74), (cx + 24, y + 76)], fill=(52, 36, 28), width=3)
    draw.ellipse([cx - 21, y + 80, cx - 13, y + 88], fill=(32, 28, 26))
    draw.ellipse([cx + 13, y + 80, cx + 21, y + 88], fill=(32, 28, 26))
    draw.line([(cx, y + 88), (cx - 2, y + 104), (cx + 3, y + 105)],
              fill=(196, 138, 100), width=2)
    draw.arc([cx - 10, y + 110, cx + 10, y + 122], 0, 180, fill=(150, 70, 60),
             width=2)
    # earring + jacket pin (island shell)
    draw.ellipse([cx - 36, y + 96, cx - 31, y + 101], fill=GOLD)
    draw.ellipse([cx - 46, y + 158, cx - 34, y + 170], fill=(233, 196, 106))
    draw.rectangle([x, y, x + w, y + h], outline=(90, 70, 40), width=2)


def stamp(base, box, lines, colour, angle, font_size=15):
    """A rotated rubber stamp on its own layer, stamped onto base."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    ld.rounded_rectangle(box, radius=8, outline=colour + (255,), width=3)
    ld.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=colour + (255,),
                 width=1)
    cy = y0 + 12
    for ln in lines:
        f = F.sans_b(font_size)
        centred(ld, (x0 + x1) // 2, cy, ln, f, fill=colour + (255,))
        cy += font_size + 5
    layer = layer.rotate(angle, resample=Image.BICUBIC, center=((x0 + x1) / 2,
                                                                (y0 + y1) / 2))
    # fade the stamp slightly, like real ink
    alpha = layer.split()[3].point(lambda v: int(v * 0.82))
    layer.putalpha(alpha)
    base.alpha_composite(layer)


def guilloche(draw, x0, y0, x1, y1, colour=(190, 178, 150)):
    for k in range(5):
        pts = []
        for xx in range(x0, x1 + 1, 8):
            yy = y0 + 8 + k * 9 + 3 * math.sin((xx - x0) / 26.0 + k)
            pts.append((xx, yy))
        draw.line(pts, fill=colour, width=1)
def coat_of_arms(draw, cx, y, s=34):
    """Shield with a wave and a compass star, in gold outline."""
    pts = [(cx - s // 2, y), (cx + s // 2, y), (cx + s // 2, y + s),
           (cx, y + s + s // 3), (cx - s // 2, y + s)]
    draw.polygon(pts, outline=GOLD, width=3)
    draw.line([(cx - s // 2 + 4, y + s // 2), (cx + s // 2 - 4, y + s // 2)],
              fill=GOLD, width=2)
    draw.line([(cx - s // 2 + 4, y + s // 2 + 8),
               (cx + s // 2 - 4, y + s // 2 + 8)], fill=GOLD, width=2)
    # compass star above the wave
    draw.polygon([(cx, y + 4), (cx + 4, y + 14), (cx, y + 24), (cx - 4, y + 14)],
                 fill=GOLD)
    draw.polygon([(cx - 12, y + 14), (cx, y + 10), (cx + 12, y + 14),
                  (cx, y + 18)], fill=GOLD)


def left_page(draw):
    x0, y0, x1, y1 = 34, 96, 502, 928
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=PAPER,
                           outline=(120, 104, 80), width=2)
    guilloche(draw, x0 + 14, y0 + 8, x1 - 14, y0 + 52)
    centred(draw, (x0 + x1) // 2, y0 + 18, "REPUBLIC OF THALASSIA",
            F.serif_b(24), fill=INK)
    centred(draw, (x0 + x1) // 2, y0 + 50, "P A S S P O R T",
            F.sans(13), fill=INK_SOFT)
    coat_of_arms(draw, (x0 + x1) // 2, y0 + 78, s=30)
    draw.line([(x0 + 24, y0 + 132), (x1 - 24, y0 + 132)], fill=RULE, width=1)
    centred(draw, (x0 + x1) // 2, y0 + 142, "PASSPORT  •  PASSEPORT",
            F.sans(11), fill=INK_SOFT)

    # portrait, left; data fields, right
    px, py, pw, ph = x0 + 26, y0 + 176, 150, 190
    draw_portrait(draw, px, py, pw, ph)
    draw_text(draw, (px, py + ph + 6), "PHOTO  •  35 × 45 mm",
              F.sans(10), fill=INK_SOFT)
    fx = x0 + 200
    label_value(draw, fx, y0 + 176, "TYPE / TYPE", "P", width=54)
    label_value(draw, fx + 74, y0 + 176, "CODE", "THA", width=54)
    label_value(draw, fx + 148, y0 + 176, "PASSPORT No.", "TH 4829167",
                vfont=F.sans_b(15), width=120)
    label_value(draw, fx, y0 + 236, "SURNAME / NOM", "MARLOW", width=268)
    label_value(draw, fx, y0 + 296, "GIVEN NAMES / PRÉNOMS",
                "ELENA SOFIA", width=268)
    label_value(draw, fx, y0 + 356, "NATIONALITY / NATIONALITÉ",
                "THALASSIAN", width=268)
    label_value(draw, fx, y0 + 416, "DATE OF BIRTH", "14 MAR 1992", width=130)
    label_value(draw, fx + 150, y0 + 416, "SEX / SEXE", "F", width=40)
    label_value(draw, fx, y0 + 476, "PLACE OF BIRTH", "PORT MERIDIAN",
                width=268)
    label_value(draw, fx, y0 + 536, "OCCUPATION / PROFESSION",
                "MARINE BIOLOGIST", width=268)
    label_value(draw, fx, y0 + 596, "DATE OF ISSUE", "02 JUN 2024",
                vfont=F.sans_b(15), width=130)
    label_value(draw, fx + 150, y0 + 596, "DATE OF EXPIRY", "01 JUN 2034",
                vfont=F.sans_b(15), width=118)
    label_value(draw, fx, y0 + 656, "AUTHORITY / AUTORITÉ",
                "MINISTRY OF THE INTERIOR", width=268)
    draw_text(draw, (fx, y0 + 716),
              "Thalassian  •  English  •  Français",
              F.sans(12), fill=INK_SOFT)

    # holder's signature, under the portrait
    sy = y0 + 420
    draw_text(draw, (x0 + 26, sy), "HOLDER'S SIGNATURE", F.sans(10),
              fill=INK_SOFT)
    draw_text(draw, (x0 + 30, sy + 14), "E. Marlow", F.serif(22), fill=INK)
    draw.line([(x0 + 26, sy + 48), (x0 + 176, sy + 48)], fill=INK, width=1)

    # machine-readable zone
    mz0, mz1 = y1 - 78, y1 - 14
    draw.rectangle([x0 + 14, mz0 - 8, x1 - 14, y1 - 8], fill=(238, 232, 216))
    l1, l2 = mrz_lines()
    draw_text(draw, (x0 + 22, mz0), l1, F.sans(13), fill=INK)
    draw_text(draw, (x0 + 22, mz0 + 22), l2, F.sans(13), fill=INK)


def right_page(img, draw):
    x0, y0, x1, y1 = 522, 96, 990, 928
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=PAPER,
                           outline=(120, 104, 80), width=2)
    centred(draw, (x0 + x1) // 2, y0 + 20, "VISAS", F.serif_b(22), fill=INK)
    draw.line([(x0 + 24, y0 + 54), (x1 - 24, y0 + 54)], fill=RULE, width=1)
    draw_text(draw, (x0 + 26, y0 + 66), "VISAS  •  ENTRY AND EXIT STAMPS",
              F.sans(11), fill=INK_SOFT)

    # visa sticker: Kingdom of Veldoria
    vx0, vy0, vx1, vy1 = x0 + 26, y0 + 92, x1 - 26, y0 + 250
    draw.rounded_rectangle([vx0, vy0, vx1, vy1], radius=4,
                           outline=BLUE_INK, width=2)
    draw.rectangle([vx0, vy0, vx1, vy0 + 30], fill=BLUE_INK)
    centred(draw, (vx0 + vx1) // 2, vy0 + 7, "KINGDOM OF VELDORIA  —  VISA",
            F.sans_b(14), fill=(255, 255, 255))
    draw_text(draw, (vx0 + 12, vy0 + 44), "Single entry  •  Valid 19 JUL 2024 – 17 AUG 2024",
              F.sans(13), fill=INK)
    draw_text(draw, (vx0 + 12, vy0 + 66), "Purpose: TOURISM — ISLAND HOPPING",
              F.sans(13), fill=INK)
    draw_text(draw, (vx0 + 12, vy0 + 88),
              "NOT VALID FOR EMPLOYMENT  •  No. VL-2024-11873",
              F.sans_b(13), fill=RED_INK)
    draw_text(draw, (vx0 + 12, vy0 + 112),
              "Issued at Port Meridian, 12 JUN 2024  •  Fee paid 40 KR",
              F.sans(12), fill=INK_SOFT)

    # stamps: one plausible trip, all after the 02 JUN 2024 issue date
    stamp(img, (x0 + 26, y0 + 268, x0 + 216, y0 + 344),
          ["VELDORIA", "ARRIVAL", "19 JUL 2024"], BLUE_INK, -8, 14)
    stamp(img, (x0 + 246, y0 + 268, x0 + 436, y0 + 344),
          ["VELDORIA", "DEPARTURE", "02 AUG 2024"], BLUE_INK, 7, 14)
    stamp(img, (x0 + 26, y0 + 364, x0 + 216, y0 + 440),
          ["KORVATH", "ARRIVAL", "03 AUG 2024"], GREEN_INK, 6, 14)
    stamp(img, (x0 + 246, y0 + 364, x0 + 436, y0 + 440),
          ["KORVATH", "DEPARTURE", "21 AUG 2024"], GREEN_INK, -6, 14)
    stamp(img, (x0 + 26, y0 + 460, x0 + 216, y0 + 536),
          ["ISLE OF SEREN", "ARRIVAL", "22 AUG 2024"], PURPLE_INK, -5, 14)
    stamp(img, (x0 + 246, y0 + 460, x0 + 436, y0 + 536),
          ["ISLE OF SEREN", "DEPARTURE", "05 SEP 2024"], PURPLE_INK, 8, 14)

    # fee stamp + travel note
    draw.ellipse([x0 + 336, y0 + 556, x0 + 430, y0 + 650], outline=RED_INK,
                 width=3)
    draw.ellipse([x0 + 346, y0 + 566, x0 + 420, y0 + 640], outline=RED_INK,
                 width=1)
    centred(draw, (x0 + 383), y0 + 580, "FEE", F.sans_b(14), fill=RED_INK)
    centred(draw, (x0 + 383), y0 + 598, "PAID", F.sans_b(14), fill=RED_INK)
    centred(draw, (x0 + 383), y0 + 616, "40 KR", F.sans_b(12), fill=RED_INK)
    draw_text(draw, (x0 + 26, y0 + 556),
              "Route: Port Meridian → Veldoria → Korvath →",
              F.sans(13), fill=INK)
    draw_text(draw, (x0 + 26, y0 + 578), "Isle of Seren → Port Meridian,",
              F.sans(13), fill=INK)
    draw_text(draw, (x0 + 26, y0 + 600), "19 JUL – 05 SEP 2024. One journey,",
              F.sans(13), fill=INK)
    draw_text(draw, (x0 + 26, y0 + 622), "three neighbouring states.",
              F.sans(13), fill=INK)

    # telling paperwork detail: the island republic, in its own words
    draw.line([(x0 + 26, y0 + 676), (x1 - 26, y0 + 676)], fill=RULE, width=1)
    draw_text(draw, (x0 + 26, y0 + 690),
              "Thalassia — an island republic in the Meridian Sea.",
              F.serif(14), fill=INK_SOFT)
    draw_text(draw, (x0 + 26, y0 + 712),
              "This document is issued under the Thalassian",
              F.serif(14), fill=INK_SOFT)
    draw_text(draw, (x0 + 26, y0 + 734),
              "Passports Act 2019. If found, please return to",
              F.serif(14), fill=INK_SOFT)
    draw_text(draw, (x0 + 26, y0 + 756),
              "any Thalassian consulate. Reward 25 KR.",
              F.serif(14), fill=INK_SOFT)


def render():
    img = Image.new("RGBA", (W, H), DESK + (255,))
    draw = ImageDraw.Draw(img)
    # desk shading
    for i in range(0, H, 4):
        draw.line([(0, i), (W, i)], fill=(58 - i // 90, 47 - i // 110,
                                           40 - i // 130), width=4)
    # soft shadow under the spread
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([44, 110, 992, 940], radius=8, fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(shadow)
    # centre seam shadow
    draw.rectangle([508, 96, 516, 928], fill=(120, 104, 80))
    left_page(draw)
    right_page(img, draw)
    # thin gold frame around the whole spread
    draw.rounded_rectangle([30, 92, 994, 932], radius=8,
                           outline=GOLD, width=2)
    return img.convert("RGB")


def fallback_png(path):
    """Stdlib-only fallback if Pillow is unavailable: a simplified spread.

    Kept deliberately plain — the Pillow path above is the real entry.
    """
    import struct
    import zlib

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    w = h = 512
    raw = bytearray()
    for yy in range(h):
        raw.append(0)
        for xx in range(w):
            if 20 <= xx < 492 and 40 <= yy < 472:
                raw += bytes((247, 242, 230))
            else:
                raw += bytes((58, 47, 40))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h,
          8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw))) +
           chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    outdir = "/output" if os.path.isdir("/output") else "output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    if HAVE_PIL:
        render().save(path, "PNG", optimize=True)
    else:  # pragma: no cover
        fallback_png(path)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
