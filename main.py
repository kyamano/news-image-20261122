#!/usr/bin/env python3
"""news-image-20261122: draw one 1024x1024 image summing up the world news of
Sunday 22 November 2026. Pure standard library only (the grading sandbox
installs nothing): a tiny framebuffer rasterizer, a 5x7 bitmap font, and a
hand-rolled PNG encoder. Running this file twice writes byte-identical PNGs.
"""

import hashlib
import math
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- font: 5x7
# Each glyph is seven rows of five bits, written as strings, "#" set, "." clear.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}

# ------------------------------------------------------------------ canvas
W = 1024
H = 1024
PAPER = (246, 241, 231)
NAVY = (20, 33, 61)
RED = (180, 35, 24)
INK = (38, 34, 28)
MUTED = (96, 90, 78)
GOLD = (232, 181, 74)
WHITE = (255, 255, 255)
CREAM = (250, 246, 238)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(0, w * h * 3, 3):
            self.px[i] = bg[0]
            self.px[i + 1] = bg[1]
            self.px[i + 2] = bg[2]

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            for xx in range(w):
                i = base + xx * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def hline(self, x, y, length, color, thick=1):
        self.rect(x, y, length, thick, color)

    def vline(self, x, y, length, color, thick=1):
        self.rect(x, y, thick, length, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - thick // 2, y - thick // 2, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, color)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for t in range(thick):
            self.circle(cx, cy, r - t, color, fill=False)

    def poly(self, points, color):
        # scanline fill of a simple polygon
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, color)


def text_width(text, scale):
    return len(text) * 6 * scale - scale if text else 0


def draw_text(cv, x, y, text, scale, color, align="left"):
    if align == "center":
        x = x - text_width(text, scale) // 2
    elif align == "right":
        x = x - text_width(text, scale)
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


# ------------------------------------------------------------------- icons
# Every pictogram is drawn inside a 104x104 box whose top-left is (bx, by).
# fg is the pictogram colour (near-white), accent a second colour.

def _star_points(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    return pts


def icon_globe(cv, bx, by, fg, accent):
    cx, cy = bx + 52, by + 52
    cv.ring(cx, cy, 36, fg, 3)
    cv.hline(cx - 36, cy, 73, fg, 2)
    cv.line(cx - 26, cy - 25, cx - 26, cy + 25, fg, 2)
    cv.line(cx + 26, cy - 25, cx + 26, cy + 25, fg, 2)
    cv.circle(cx + 14, cy - 14, 7, accent)


def icon_ship(cv, bx, by, fg, accent):
    cv.poly([(bx + 18, by + 58), (bx + 86, by + 58), (bx + 74, by + 80),
             (bx + 30, by + 80)], fg)
    cv.vline(bx + 52, by + 26, 34, fg, 3)
    cv.poly([(bx + 52, by + 26), (bx + 74, by + 34), (bx + 52, by + 42)], accent)
    for yy in (by + 88, by + 94):
        cv.hline(bx + 14, yy, 76, fg, 2)


def icon_building(cv, bx, by, fg, accent):
    cv.rect(bx + 26, by + 34, 52, 52, fg)
    for wx in (bx + 34, bx + 46, bx + 58):
        for wy in (by + 42, by + 56, by + 70):
            cv.rect(wx, wy, 7, 7, accent)
    cv.poly([(bx + 52, by + 12), (bx + 64, by + 30), (bx + 58, by + 30),
             (bx + 52, by + 22), (bx + 46, by + 30), (bx + 40, by + 30)], accent)


def icon_tanker(cv, bx, by, fg, accent):
    cv.poly([(bx + 14, by + 56), (bx + 90, by + 56), (bx + 80, by + 78),
             (bx + 24, by + 78)], fg)
    for cx in (bx + 32, bx + 52, bx + 72):
        cv.circle(cx, by + 48, 9, fg)
    cv.poly([(bx + 52, by + 16), (bx + 62, by + 32), (bx + 56, by + 32),
             (bx + 52, by + 26), (bx + 48, by + 32), (bx + 42, by + 32)], accent)
    cv.hline(bx + 12, by + 88, 80, fg, 2)


def icon_badge(cv, bx, by, fg, accent):
    cv.poly(_star_points(bx + 52, by + 50, 38, 16), fg)
    cv.circle(bx + 52, by + 50, 12, accent)
    cv.hline(bx + 22, by + 90, 60, fg, 3)


def icon_boat(cv, bx, by, fg, accent):
    cv.poly([(bx + 20, by + 52), (bx + 84, by + 52), (bx + 72, by + 74),
             (bx + 32, by + 74)], fg)
    cv.vline(bx + 52, by + 28, 26, fg, 3)
    cv.poly([(bx + 52, by + 28), (bx + 70, by + 38), (bx + 52, by + 46)], accent)
    for yy in (by + 82, by + 90):
        cv.hline(bx + 14, yy, 76, fg, 2)


def icon_factory(cv, bx, by, fg, accent):
    cv.rect(bx + 18, by + 48, 56, 38, fg)
    cv.poly([(bx + 18, by + 48), (bx + 32, by + 34), (bx + 46, by + 48),
             (bx + 60, by + 34), (bx + 74, by + 48)], fg)
    cv.rect(bx + 78, by + 24, 10, 62, fg)
    cv.poly([(bx + 52, by + 10), (bx + 62, by + 26), (bx + 56, by + 26),
             (bx + 52, by + 20), (bx + 48, by + 26), (bx + 42, by + 26)], accent)
    cv.hline(bx + 14, by + 92, 76, fg, 2)


def icon_chip(cv, bx, by, fg, accent):
    cv.rect(bx + 32, by + 32, 40, 40, fg)
    cv.rect(bx + 42, by + 42, 20, 20, accent)
    for xx in (bx + 38, bx + 48, bx + 58):
        cv.vline(xx, by + 20, 12, fg, 3)
        cv.vline(xx, by + 72, 12, fg, 3)
    for yy in (by + 38, by + 48, by + 58):
        cv.hline(bx + 20, yy, 12, fg, 3)
        cv.hline(bx + 72, yy, 12, fg, 3)


def icon_shield(cv, bx, by, fg, accent):
    cv.poly([(bx + 52, by + 16), (bx + 84, by + 28), (bx + 84, by + 54),
             (bx + 52, by + 88), (bx + 20, by + 54), (bx + 20, by + 28)], fg)
    draw_text(cv, bx + 52, by + 38, "5", 4, accent, align="center")


def icon_castle(cv, bx, by, fg, accent):
    cv.rect(bx + 22, by + 66, 60, 22, fg)
    cv.poly([(bx + 18, by + 66), (bx + 30, by + 52), (bx + 74, by + 52),
             (bx + 86, by + 66)], accent)
    cv.rect(bx + 34, by + 34, 36, 20, fg)
    cv.poly([(bx + 30, by + 34), (bx + 40, by + 22), (bx + 64, by + 22),
             (bx + 74, by + 34)], accent)
    cv.rect(bx + 48, by + 12, 8, 12, fg)
    cv.rect(bx + 48, by + 74, 8, 14, accent)


ICONS = [icon_globe, icon_ship, icon_building, icon_tanker, icon_badge,
         icon_boat, icon_factory, icon_chip, icon_shield, icon_castle]

# -------------------------------------------------------------------- data
# Headline lines are at most 17 chars; detail lines at most 25 chars.
PANELS = [
    ("CLIMATE TALKS", "COLLAPSE",
     "COP31 IN TURKEY ENDS", "WITH NO FOSSIL DEAL",
     (14, 124, 123), icon_globe),
    ("UKRAINE SANK", "RUSSIAN WARSHIP",
     "ZELENSKYY CONFIRMS", "STRIKE OFF LIBYA",
     (46, 90, 136), icon_ship),
    ("14 KILLED IN", "KYIV REGION",
     "RUSSIAN STRIKES HIT", "APARTMENT BLOCK",
     (166, 58, 46), icon_building),
    ("TANKERS HIT", "NEAR HORMUZ",
     "IRAN STRIKES THREE", "SHIPS; STANDOFF GROWS",
     (199, 125, 10), icon_tanker),
    ("MEXICO CAPTURES", "CARTEL KINGPIN",
     "'CHAPO ISIDRO' SEIZED", "11 DEAD IN FIREFIGHT",
     (47, 107, 51), icon_badge),
    ("BOAT CAPSIZES", "IN NIGERIA",
     "24 DEAD AS BOAT", "CARRYING MOURNERS SINKS",
     (31, 78, 121), icon_boat),
    ("FACTORY FIRE", "IN INDONESIA",
     "3 DEAD, 36 MISSING", "AFTER CANDY PLANT BLAZE",
     (199, 91, 18), icon_factory),
    ("US PRESSES", "NVIDIA ON CHIPS",
     "BESSENT SEEKS ANSWERS", "ON AI SALES TO CHINA",
     (91, 74, 138), icon_chip),
    ("TRUMP OPEN TO", "UKRAINE PLEDGES",
     "KUSHNER: ARTICLE 5", "STYLE DEALS ON TABLE",
     (74, 101, 114), icon_shield),
    ("SHURI CASTLE", "REBORN",
     "OKINAWA HALL RESTORED", "7 YEARS AFTER FIRE",
     (166, 43, 43), icon_castle),
]

# Brief lines are at most 25 chars each.
BRIEFS = [
    ("CHINA EASES MARGIN", "RULES TO 80% FROM NOV 30"),
    ("SETTLERS TORCH HOMES", "AND CARS IN WEST BANK"),
    ("RUSSIAN SHIP ABLAZE", "IN BALTIC AFTER DRONES"),
    ("ICE ARRESTS AT SEATTLE", "AIRPORT DENOUNCED"),
    ("YOUTH CONGRESS PROTESTS", "AT META OFFICES IN INDIA"),
    ("JETS 27, CHARGERS 24", "PROTOCOL AFTER LOSS"),
    ("BRONCOS 38, RAIDERS 24", "DENVER WINS AT HOME"),
    ("LIONS 31, BUCS 21", "SIXTH STRAIGHT WIN"),
    ("49ERS 35, VIKINGS 10", "WIN IN MEXICO CITY"),
    ("TRUMP: US WORKING ON", "BROADER UKRAINE TRUCE"),
    ("NEPAL PM BEGINS", "TWO-DAY INDIA VISIT"),
    ("TAIWAN WARNS CANADA", "OVER CLOSER CHINA TIES"),
    ("CHINA SPY BID FOR", "AI CHIPS, NYT REPORTS"),
    ("US-CHINA POWER GAP", "NARROWS, LOWY INDEX"),
    ("ROHINGYA WELCOME UN", "COURT GENOCIDE VERDICT"),
    ("RUSSIAN MISSILES LAND", "IN POLAND; NATO PROTESTS"),
    ("MISSILE HITS ZELENSKYY", "HOMETOWN; 2 KILLED"),
    ("ILLICIT ALCOHOL KILLS", "11 IN INDIA, 180 HURT"),
    ("US CLEARED 900,000", "AI CHIPS FOR CHINA"),
    ("MYANMAR CALLS ASEAN", "DECISION UNFAIR"),
]

# ------------------------------------------------------------------- build
def build():
    cv = Canvas(W, H, PAPER)

    # Masthead
    cv.rect(0, 0, W, 84, NAVY)
    draw_text(cv, W // 2, 12, "THE WORLD IN ONE DAY", 5, WHITE, align="center")
    draw_text(cv, W // 2, 58, "SUNDAY, 22 NOVEMBER 2026", 2, GOLD, align="center")
    cv.hline(0, 84, W, RED, 4)

    # Subhead
    draw_text(cv, W // 2, 94, "THE DAY'S WORLD NEWS IN ONE IMAGE", 2, NAVY,
              align="center")

    # Panels: 2 columns x 5 rows
    for idx, (h1, h2, d1, d2, bg, icon) in enumerate(PANELS):
        col = idx % 2
        row = idx // 2
        px = 10 + col * 506
        py = 112 + row * 130
        cv.rect(px, py, 498, 124, WHITE)
        cv.rect(px, py, 498, 2, NAVY)
        cv.rect(px, py + 122, 498, 2, NAVY)
        cv.rect(px, py, 2, 124, NAVY)
        cv.rect(px + 496, py, 2, 124, NAVY)
        cv.rect(px + 10, py + 10, 104, 104, bg)
        icon(cv, px + 10, py + 10, CREAM, GOLD)
        tx = px + 126
        cv.rect(tx, py + 12, 30, 3, RED)
        draw_text(cv, tx, py + 20, h1, 3, NAVY)
        draw_text(cv, tx, py + 42, h2, 3, NAVY)
        draw_text(cv, tx, py + 70, d1, 2, INK)
        draw_text(cv, tx, py + 86, d2, 2, INK)

    # Briefs strip: 3 columns, 7 / 7 / 6
    cv.hline(10, 764, 1004, NAVY, 2)
    draw_text(cv, 10, 772, "ALSO ON 22 NOVEMBER", 2, NAVY)
    draw_text(cv, 1014, 776, "SOURCES: AP, REUTERS, SCMP, BBC, JAPAN TIMES, WION",
              1, MUTED, align="right")
    cols = [BRIEFS[0:7], BRIEFS[7:14], BRIEFS[14:20]]
    for ci, group in enumerate(cols):
        bx = 10 + ci * 338
        for ri, (b1, b2) in enumerate(group):
            by = 792 + ri * 32
            cv.rect(bx, by + 1, 4, 30, RED)
            draw_text(cv, bx + 10, by, b1, 2, INK)
            draw_text(cv, bx + 10, by + 15, b2, 2, INK)

    return cv


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    png = encode_png(build())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes) sha256=%s" % (
        path, len(png), hashlib.sha256(png).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
