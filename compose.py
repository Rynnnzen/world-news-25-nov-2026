#!/usr/bin/env python3
"""Compose "THE WORLD IN ONE DAY" - a dense newspaper front page summing up
the world news of Wednesday 25 November 2026.

Original composition drawn entirely with Pillow primitives. No photographs,
no external images, no network. The output is deterministic: the same bytes
are produced on every run.

Run with:  /data/home/makefun/venv/bin/python compose.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas and palette
# --------------------------------------------------------------------------
W = H = 1024
M = 12

PAPER = (247, 243, 233)
PAPER_DARK = (238, 232, 219)
INK = (26, 23, 20)
INK_SOFT = (78, 72, 64)
RULE = (44, 40, 35)
RED = (168, 40, 34)
WHITE = (255, 255, 255)

REGION_COLORS = {
    "EUROPE": (32, 74, 138),
    "MIDDLE EAST": (158, 48, 42),
    "ASIA": (16, 118, 108),
    "AMERICAS": (88, 58, 140),
    "AFRICA": (150, 104, 18),
    "OCEANIA": (20, 118, 150),
    "WORLD": (58, 58, 64),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")

_font_cache = {}


def get_font(size, bold=False, serif=False):
    key = (int(size), bold, serif)
    if key not in _font_cache:
        if serif and bold:
            path = SERIF_BOLD
        elif serif:
            path = SERIF
        elif bold:
            path = SANS_BOLD
        else:
            path = SANS
        _font_cache[key] = ImageFont.truetype(path, int(size))
    return _font_cache[key]


def blend(a, b, t):
    """Mix colour a over b; t=0 gives b, t=1 gives a."""
    return tuple(int(a[i] * t + b[i] * (1 - t)) for i in range(3))


def tw(draw, text, font):
    return draw.textlength(text, font=font)


# --------------------------------------------------------------------------
# Text fitting helpers - text is shrunk and finally ellipsised, never spilled
# --------------------------------------------------------------------------
def wrap_lines(draw, text, font, maxw):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if not cur or tw(draw, trial, font) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(draw, text, maxw, maxlines, size, minsize, bold, serif):
    """Return (font, lines) that fit maxw x maxlines, shrinking then eliding."""
    s = int(size)
    while s > minsize:
        f = get_font(s, bold, serif)
        lines = wrap_lines(draw, text, f, maxw)
        if len(lines) <= maxlines:
            return f, lines
        s -= 1
    f = get_font(int(minsize), bold, serif)
    lines = wrap_lines(draw, text, f, maxw)
    if len(lines) > maxlines:
        lines = lines[:maxlines]
        last = lines[-1]
        while last and tw(draw, last + "\u2026", f) > maxw:
            last = last[:-1]
        lines[-1] = last.rstrip() + "\u2026"
    return f, lines


def fit_single(draw, text, maxw, size, minsize, bold=False, serif=False):
    """Shrink a single line until it fits, then ellipsise."""
    s = int(size)
    while s > minsize:
        f = get_font(s, bold, serif)
        if tw(draw, text, f) <= maxw:
            return f, text
        s -= 1
    f = get_font(int(minsize), bold, serif)
    if tw(draw, text, f) <= maxw:
        return f, text
    t = text
    while t and tw(draw, t + "\u2026", f) > maxw:
        t = t[:-1]
    return f, t.rstrip() + "\u2026"


def draw_block(draw, text, x, y, maxw, maxlines, size, minsize,
               fill, bold=False, serif=False, lh=None):
    f, lines = fit_block(draw, text, maxw, maxlines, size, minsize, bold, serif)
    if lh is None:
        lh = int(size * 1.18)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lh), line, font=f, fill=fill)
    return y + len(lines) * lh


# --------------------------------------------------------------------------
# Icons - every one is drawn from scratch with primitive shapes
# --------------------------------------------------------------------------
def _pt(x, y, w, h, fx, fy):
    return (x + fx * w, y + fy * h)


def icon_leaf(d, x, y, w, h, col):
    cx = x + .50 * w
    top = y + .06 * h
    bot = y + .86 * h
    n = 26
    left, right = [], []
    for i in range(n + 1):
        u = i / n
        yy = top + u * (bot - top)
        half = math.sin(math.pi * u) * .40 * w
        left.append((cx - half, yy))
        right.append((cx + half, yy))
    d.polygon(left + right[::-1], fill=(92, 150, 78), outline=(40, 92, 40))
    d.line([(cx, top + 2), (cx, bot - 2)], fill=(40, 92, 40), width=1)
    for fy in (.26, .44, .62, .80):
        yy = top + fy * (bot - top)
        half = math.sin(math.pi * fy) * .36 * w
        d.line([(cx, yy), (cx + half, yy - .10 * h)], fill=(40, 92, 40), width=1)
        d.line([(cx, yy), (cx - half, yy - .10 * h)], fill=(40, 92, 40), width=1)
    d.line([(cx, bot - 2), (cx, y + .98 * h)], fill=(96, 68, 40), width=2)


def icon_refinery(d, x, y, w, h, col):
    base = y + .93 * h
    d.line([(x + .04 * w, base), (x + .96 * w, base)], fill=(70, 66, 60), width=1)
    for fx, top in ((.08, .56), (.36, .64), (.56, .68)):
        d.rectangle([x + fx * w, y + top * h, x + (fx + .18) * w, base],
                    fill=(96, 96, 102), outline=(60, 60, 66))
        d.ellipse([x + fx * w, y + (top - .06) * h,
                   x + (fx + .18) * w, y + (top + .06) * h],
                  fill=(128, 128, 134), outline=(60, 60, 66))
    d.rectangle([x + .76 * w, y + .30 * h, x + .86 * w, base],
                fill=(96, 96, 102), outline=(60, 60, 66))
    d.polygon([_pt(x, y, w, h, .81, .30), _pt(x, y, w, h, .72, .13),
               _pt(x, y, w, h, .90, .13)], fill=(224, 122, 34))
    d.ellipse([x + .70 * w, y + .03 * h, x + .80 * w, y + .12 * h],
              fill=(196, 196, 196))
    d.ellipse([x + .76 * w, y + .00 * h, x + .86 * w, y + .08 * h],
              fill=(210, 210, 210))


def icon_tanker(d, x, y, w, h, col):
    for i, fy in enumerate((.84, .90, .96)):
        d.line([(x + .06 * w, y + fy * h), (x + .94 * w, y + fy * h)],
               fill=(40, 110, 140), width=1)
    d.polygon([_pt(x, y, w, h, .10, .60), _pt(x, y, w, h, .86, .60),
               _pt(x, y, w, h, .78, .80), _pt(x, y, w, h, .18, .80)],
              fill=(64, 68, 76), outline=(30, 32, 38))
    d.rectangle([x + .56 * w, y + .44 * h, x + .74 * w, y + .60 * h],
                fill=(210, 210, 214), outline=(30, 32, 38))
    d.rectangle([x + .62 * w, y + .34 * h, x + .68 * w, y + .44 * h],
                fill=(210, 210, 214), outline=(30, 32, 38))
    star(d, x + .30 * w, y + .36 * h, .24 * min(w, h), .10 * min(w, h), 9,
         (232, 142, 30), (150, 60, 20))
    d.ellipse([x + .25 * w, y + .60 * h, x + .35 * w, y + .70 * h],
              fill=(30, 30, 34))
    for a in range(0, 360, 45):
        ang = math.radians(a)
        d.line([(x + .30 * w + math.cos(ang) * .05 * min(w, h),
                 y + .65 * h + math.sin(ang) * .05 * min(w, h)),
                (x + .30 * w + math.cos(ang) * .09 * min(w, h),
                 y + .65 * h + math.sin(ang) * .09 * min(w, h))],
               fill=(30, 30, 34), width=1)


def icon_rocket(d, x, y, w, h, col):
    cx = x + .50 * w
    d.rounded_rectangle([x + .43 * w, y + .28 * h, x + .57 * w, y + .72 * h],
                        radius=2, fill=(226, 228, 232), outline=(90, 92, 100))
    d.polygon([_pt(x, y, w, h, .43, .30), _pt(x, y, w, h, .50, .06),
               _pt(x, y, w, h, .57, .30)], fill=(190, 48, 40))
    d.polygon([_pt(x, y, w, h, .43, .56), _pt(x, y, w, h, .32, .74),
               _pt(x, y, w, h, .43, .70)], fill=(190, 48, 40))
    d.polygon([_pt(x, y, w, h, .57, .56), _pt(x, y, w, h, .68, .74),
               _pt(x, y, w, h, .57, .70)], fill=(190, 48, 40))
    d.ellipse([cx - .045 * w, y + .38 * h, cx + .045 * w, y + .47 * h],
              fill=(90, 150, 190), outline=(50, 90, 120))
    d.polygon([_pt(x, y, w, h, .44, .72), _pt(x, y, w, h, .50, .97),
               _pt(x, y, w, h, .56, .72)], fill=(236, 160, 40))
    d.polygon([_pt(x, y, w, h, .47, .72), _pt(x, y, w, h, .50, .88),
               _pt(x, y, w, h, .53, .72)], fill=(250, 226, 120))
    for fx, fy in ((.16, .20), (.82, .30), (.20, .62), (.80, .66), (.70, .14)):
        d.ellipse([x + fx * w - 1, y + fy * h - 1,
                   x + fx * w + 1, y + fy * h + 1], fill=(120, 130, 150))


def icon_mine(d, x, y, w, h, col):
    for i, fy in enumerate((.74, .82, .90, .97)):
        d.arc([x + .04 * w, y + (fy - .07) * h, x + .40 * w, y + (fy + .07) * h],
              200, 340, fill=(48, 110, 150), width=1)
        d.arc([x + .34 * w, y + (fy - .07) * h, x + .70 * w, y + (fy + .07) * h],
              200, 340, fill=(48, 110, 150), width=1)
        d.arc([x + .64 * w, y + (fy - .07) * h, x + .96 * w, y + (fy + .07) * h],
              200, 340, fill=(48, 110, 150), width=1)
    d.line([(x + .20 * w, y + .72 * h), (x + .40 * w, y + .20 * h)],
           fill=(80, 60, 44), width=2)
    d.line([(x + .62 * w, y + .72 * h), (x + .40 * w, y + .20 * h)],
           fill=(80, 60, 44), width=2)
    d.line([(x + .26 * w, y + .52 * h), (x + .56 * w, y + .52 * h)],
           fill=(80, 60, 44), width=1)
    d.ellipse([x + .35 * w, y + .14 * h, x + .45 * w, y + .26 * h],
              fill=(120, 90, 60), outline=(60, 44, 30))
    d.rectangle([x + .16 * w, y + .70 * h, x + .66 * w, y + .74 * h],
                fill=(90, 70, 50))


def icon_blast(d, x, y, w, h, col):
    cx, cy = x + .50 * w, y + .50 * h
    u = min(w, h)
    for rr, aa in ((.46, 40), (.38, 70)):
        d.ellipse([cx - rr * u, cy - rr * u, cx + rr * u, cy + rr * u],
                  outline=(230, 190, 120), width=1)
    star(d, cx, cy, .40 * u, .15 * u, 12, (232, 126, 30), (150, 54, 18))
    star(d, cx, cy, .24 * u, .09 * u, 10, (250, 210, 90), (200, 140, 40))
    d.line([(x + .05 * w, y + .93 * h), (x + .95 * w, y + .93 * h)],
           fill=(90, 80, 66), width=2)


def icon_tariff(d, x, y, w, h, col):
    d.polygon([_pt(x, y, w, h, .12, .20), _pt(x, y, w, h, .54, .20),
               _pt(x, y, w, h, .86, .50), _pt(x, y, w, h, .54, .80),
               _pt(x, y, w, h, .12, .80)],
              fill=(70, 92, 128), outline=(38, 52, 78))
    d.ellipse([x + .19 * w, y + .30 * h, x + .29 * w, y + .42 * h],
              fill=PAPER, outline=(38, 52, 78))
    f = get_font(max(7, int(.30 * h)), bold=True)
    label = "%"
    lw = tw(d, label, f)
    d.text((x + .60 * w - lw / 2, y + .50 * h - .17 * h), label,
           font=f, fill=WHITE)


def icon_chart_up(d, x, y, w, h, col):
    d.line([(x + .12 * w, y + .10 * h), (x + .12 * w, y + .86 * h),
            (x + .92 * w, y + .86 * h)], fill=(70, 66, 60), width=1)
    for i, fx in enumerate((.24, .44, .64)):
        bh = (.28 + .12 * i) * h
        d.rectangle([x + fx * w, y + .84 * h - bh,
                     x + (fx + .13) * w, y + .84 * h],
                    fill=(52, 122, 92), outline=(30, 78, 58))
    d.line([_pt(x, y, w, h, .20, .70), _pt(x, y, w, h, .44, .56),
            _pt(x, y, w, h, .60, .40), _pt(x, y, w, h, .84, .18)],
           fill=(190, 48, 40), width=2)
    d.polygon([_pt(x, y, w, h, .84, .18), _pt(x, y, w, h, .72, .18),
               _pt(x, y, w, h, .84, .30)], fill=(190, 48, 40))


def icon_gavel(d, x, y, w, h, col):
    d.rectangle([x + .16 * w, y + .84 * h, x + .84 * w, y + .92 * h],
                fill=(120, 90, 58), outline=(74, 54, 34))
    d.line([_pt(x, y, w, h, .28, .78), _pt(x, y, w, h, .60, .36)],
           fill=(120, 90, 58), width=max(2, int(.10 * w)))
    d.polygon([_pt(x, y, w, h, .50, .30), _pt(x, y, w, h, .62, .16),
               _pt(x, y, w, h, .78, .32), _pt(x, y, w, h, .66, .46)],
              fill=(120, 90, 58), outline=(74, 54, 34))
    for fx in (.16, .22):
        d.line([(x + fx * w, y + .20 * h), (x + fx * w, y + .36 * h)],
               fill=(150, 120, 80), width=1)


def icon_film(d, x, y, w, h, col):
    d.rectangle([x + .12 * w, y + .44 * h, x + .88 * w, y + .90 * h],
                fill=(52, 50, 56), outline=(20, 20, 24))
    d.polygon([_pt(x, y, w, h, .12, .26), _pt(x, y, w, h, .90, .26),
               _pt(x, y, w, h, .90, .44), _pt(x, y, w, h, .12, .44)],
              fill=(220, 216, 208), outline=(20, 20, 24))
    for i in range(5):
        fx = .14 + i * .15
        d.polygon([_pt(x, y, w, h, fx, .26), _pt(x, y, w, h, fx + .07, .26),
                   _pt(x, y, w, h, fx + .02, .44), _pt(x, y, w, h, fx - .05, .44)],
                  fill=(52, 50, 56))
    d.ellipse([x + .16 * w, y + .56 * h, x + .30 * w, y + .70 * h],
              fill=(220, 216, 208))
    d.ellipse([x + .19 * w, y + .59 * h, x + .27 * w, y + .67 * h],
              fill=(52, 50, 56))


def icon_handshake(d, x, y, w, h, col):
    left = [_pt(x, y, w, h, .10, .18), _pt(x, y, w, h, .46, .18),
            _pt(x, y, w, h, .46, .56), _pt(x, y, w, h, .28, .82),
            _pt(x, y, w, h, .10, .56)]
    right = [_pt(x, y, w, h, .90, .18), _pt(x, y, w, h, .54, .18),
             _pt(x, y, w, h, .54, .56), _pt(x, y, w, h, .72, .82),
             _pt(x, y, w, h, .90, .56)]
    d.polygon(left, fill=(70, 100, 150), outline=(40, 60, 96))
    d.polygon(right, fill=(26, 132, 142), outline=(14, 82, 90))
    d.line([_pt(x, y, w, h, .34, .44), _pt(x, y, w, h, .66, .44)],
           fill=WHITE, width=2)
    d.line([_pt(x, y, w, h, .44, .56), _pt(x, y, w, h, .56, .56)],
           fill=WHITE, width=2)


def icon_inflation(d, x, y, w, h, col):
    d.polygon([_pt(x, y, w, h, .18, .54), _pt(x, y, w, h, .82, .54),
               _pt(x, y, w, h, .72, .88), _pt(x, y, w, h, .28, .88)],
              fill=(156, 112, 34), outline=(96, 66, 18))
    d.arc([x + .22 * w, y + .30 * h, x + .78 * w, y + .66 * h],
          200, 340, fill=(96, 66, 18), width=2)
    d.line([_pt(x, y, w, h, .50, .52), _pt(x, y, w, h, .50, .14)],
           fill=(190, 48, 40), width=2)
    d.polygon([_pt(x, y, w, h, .50, .08), _pt(x, y, w, h, .40, .24),
               _pt(x, y, w, h, .60, .24)], fill=(190, 48, 40))
    for fx in (.32, .50, .68):
        d.ellipse([x + fx * w - 2, y + .66 * h - 2,
                   x + fx * w + 2, y + .66 * h + 2], fill=(240, 214, 150))


def icon_dow(d, x, y, w, h, col):
    d.line([(x + .12 * w, y + .10 * h), (x + .12 * w, y + .86 * h),
            (x + .92 * w, y + .86 * h)], fill=(70, 66, 60), width=1)
    pts = [_pt(x, y, w, h, .14, .30), _pt(x, y, w, h, .30, .44),
           _pt(x, y, w, h, .44, .76), _pt(x, y, w, h, .60, .62),
           _pt(x, y, w, h, .86, .20)]
    d.line(pts, fill=(40, 108, 150), width=2, joint="curve")
    d.polygon([_pt(x, y, w, h, .86, .20), _pt(x, y, w, h, .74, .22),
               _pt(x, y, w, h, .84, .34)], fill=(40, 108, 150))
    d.line([(x + .14 * w, y + .78 * h), (x + .88 * w, y + .78 * h)],
           fill=(180, 174, 162), width=1)


ICONS = {
    "leaf": icon_leaf,
    "refinery": icon_refinery,
    "tanker": icon_tanker,
    "rocket": icon_rocket,
    "mine": icon_mine,
    "blast": icon_blast,
    "tariff": icon_tariff,
    "chart_up": icon_chart_up,
    "gavel": icon_gavel,
    "film": icon_film,
    "handshake": icon_handshake,
    "inflation": icon_inflation,
    "dow": icon_dow,
}


def star(draw, cx, cy, r_out, r_in, n, fill, outline=None):
    pts = []
    for i in range(2 * n):
        ang = -math.pi / 2 + i * math.pi / n
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill, outline=outline)


def draw_icon_panel(d, x, y, w, h, key, region):
    col = REGION_COLORS[region]
    tint = blend(col, PAPER, 0.10)
    d.rounded_rectangle([x, y, x + w, y + h], radius=4,
                        fill=tint, outline=blend(col, PAPER, 0.35))
    pad = max(2, int(min(w, h) * 0.10))
    ICONS[key](d, x + pad, y + pad, w - 2 * pad, h - 2 * pad, col)


# --------------------------------------------------------------------------
# Story data
# --------------------------------------------------------------------------
# number, region, headline, summary, icon
PICTURED = [
    (13, "ASIA", "Shenzhou-24 launches with first Pakistani in orbit",
     "Long March-2F lifts off from Jiuquan; Muhammad Zeeshan Ali reaches China's Tiangong station",
     "rocket"),
    (1, "EUROPE", "EU Parliament votes to loosen nature laws",
     "MEPs back review of Birds and Habitats Directives, 367-268", "leaf"),
    (8, "MIDDLE EAST", "Houthis strike Ras Tanura refinery and Jeddah and Jazan ports",
     "Coalition confirms Jazan port hit, minor damage, no casualties", "refinery"),
    (9, "MIDDLE EAST", "Iran says two tankers hit mines and caught fire in Strait of Hormuz",
     "IRGC claims LNG carrier and oil tanker struck mines; vessels unnamed, unverified",
     "tanker"),
    (16, "ASIA", "Nine dead as bodies recovered from flooded illegal West Java gold mine",
     "Flood hit Monday; toll rose to nine on Wednesday, 17 still trapped", "mine"),
    (20, "AMERICAS", "Army detonates 9,500 lb of lead azide in Iowa",
     "Two blasts at 9:00 AM CST succeed; EPA finds zero airborne lead, all-clear issued",
     "blast"),
    (21, "AMERICAS", "Trump unveils Section 301 tariffs on 14 economies",
     "USTR proposes 15-35% duties on China, EU, Japan, India, Vietnam and others",
     "tariff"),
    (22, "AMERICAS", "US economy grows 4.3% in Q3, inflation stays hot",
     "GDP revised up to fastest pace in three years; October PCE inflation 3.8%",
     "chart_up"),
    (27, "AFRICA", "Ramaphosa wins Phala Phala court battle",
     "High Court scraps impeachment report; impeachment process falls away", "gavel"),
    (28, "AFRICA", "Nollywood legend Pete Edochie dies at 79",
     "Family confirms death at 12:30am in Enugu after prostate cancer", "film"),
    (32, "OCEANIA", "Australia and Solomon Islands sign security pact",
     "Canberra becomes Solomons' defence partner of choice, displacing China's deal",
     "handshake"),
    (34, "OCEANIA", "Australia inflation jumps to 4.9%, highest since 2023",
     "ABS October CPI released 25 Nov; electricity up 25.2%, fuelling rate-hike fears",
     "inflation"),
    (39, "WORLD", "Dow erases 1,100-point plunge in dramatic comeback",
     "Dow closes up 0.33% at 50,183; S&P down 0.25%, Nasdaq down 0.62%", "dow"),
]

# number, headline
LISTED = [
    (2, "EUROPE", "EU unveils 50bn euro Quantum Act and tech fund"),
    (3, "EUROPE", "Bad weld and sinking ground blamed for deadly Spain train crash"),
    (4, "EUROPE", "Germany's Q3 growth revised down to 0.1%"),
    (5, "EUROPE", "Poundland collapses into administration"),
    (6, "EUROPE", "Surprise Eurostar strike halts Paris-London trains"),
    (7, "MIDDLE EAST", "Houthis threaten Saudi ports as coalition orders Hodeidah evacuated"),
    (10, "MIDDLE EAST", "Israeli strike kills Hamas security chief and family in Gaza City"),
    (11, "MIDDLE EAST", "Islamic State attack kills two Syrian security personnel in Hasaka"),
    (12, "MIDDLE EAST", "Iraq's top court backs Baghdad troop deployment to Kurdistan borders"),
    (14, "ASIA", "Japan unveils LUPEX moon rover prototype to hunt for lunar water"),
    (15, "ASIA", "North Korea expels Swiss envoy and orders Pyongyang office shut"),
    (17, "ASIA", "MPR begins factual verification of Prabowo's VP candidates"),
    (18, "ASIA", "Aramco and S-OIL open 7bn dollar Shaheen petrochemical complex"),
    (19, "ASIA", "India's Supreme Court quashes CBI and ED probe into Rahul Gandhi's assets"),
    (23, "AMERICAS", "Abrego Garcia lands in Spain after leaving US"),
    (24, "AMERICAS", "Macy's 100th Thanksgiving Parade postponed to Saturday"),
    (25, "AMERICAS", "Puerto Rico court voids LUMA power grid contract"),
    (26, "AMERICAS", "Six victims identified in Mississippi plane crash"),
    (29, "AFRICA", "Africa CDC and WHO set 1.576bn dollar Ebola plan"),
    (30, "AFRICA", "RSF drone strikes kill 19 civilians in Sudan"),
    (31, "AFRICA", "UN evacuates Ebola workers trapped by Congo fighting"),
    (33, "OCEANIA", "Australia apologises to LGBTQ veterans"),
    (35, "OCEANIA", "Australia passes Digital Duty of Care online safety law"),
    (36, "OCEANIA", "Ex-officer guilty of Sydney double murder"),
    (37, "OCEANIA", "RNZ investigates suspected cyber breach"),
    (38, "WORLD", "Gold ticks lower ahead of US inflation data"),
    (40, "WORLD", "South Pole Telescope releases clearest map of universe's matter"),
    (41, "WORLD", "Pope Leo laments failure of COP31 climate talks"),
]

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "ASIA", "AMERICAS", "AFRICA",
                "OCEANIA", "WORLD"]

# lon, lat, story number
PINS = [
    (98, 40, 13),     # Jiuquan / Shenzhou-24
    (39, 21, 8),      # Jeddah / Red Sea ports
    (58, 24, 9),      # Strait of Hormuz / Gulf of Oman
    (-96, 43, 20),    # Iowa
    (-76, 38, 21),    # Washington DC / tariffs
    (107, -7, 16),    # West Java
    (28, -26, 27),    # Pretoria
    (7, 6, 28),       # Enugu
    (160, -9, 32),    # Honiara
    (149, -35, 34),   # Canberra
]

# --------------------------------------------------------------------------
# Approximate continent outlines for the dotted map (lon, lat)
# --------------------------------------------------------------------------
CONTINENTS = [
    # North America
    [(-168, 65), (-160, 71), (-140, 70), (-125, 70), (-110, 68), (-95, 72),
     (-80, 73), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-81, 25), (-97, 26), (-105, 20), (-95, 16), (-84, 9), (-77, 8),
     (-83, 15), (-97, 26), (-115, 30), (-125, 40), (-130, 52), (-140, 60),
     (-155, 58), (-168, 65)],
    # South America
    [(-81, 10), (-76, 8), (-70, 11), (-60, 10), (-50, 0), (-35, -5),
     (-38, -15), (-48, -25), (-58, -35), (-62, -40), (-65, -52), (-70, -55),
     (-73, -45), (-75, -30), (-70, -18), (-81, -5), (-81, 10)],
    # Europe
    [(-10, 36), (-9, 43), (-5, 48), (2, 51), (4, 53), (8, 54), (10, 57),
     (5, 62), (12, 65), (20, 70), (30, 70), (40, 66), (40, 55), (35, 47),
     (28, 45), (26, 40), (22, 38), (15, 38), (12, 45), (8, 44), (3, 42),
     (-2, 37), (-10, 36)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 27), (0, 32), (10, 37), (20, 32), (32, 31),
     (35, 25), (38, 18), (43, 12), (51, 12), (48, 2), (41, -2), (40, -10),
     (35, -20), (33, -26), (27, -34), (20, -35), (18, -30), (13, -20),
     (9, -2), (2, 5), (-8, 5), (-13, 9), (-17, 15)],
    # Asia
    [(40, 66), (60, 70), (80, 74), (100, 76), (120, 73), (140, 70),
     (160, 68), (170, 65), (180, 62), (180, 50), (160, 55), (145, 50),
     (140, 42), (130, 35), (122, 30), (120, 22), (108, 15), (105, 5),
     (100, 2), (95, 8), (90, 22), (80, 10), (75, 8), (70, 20), (62, 25),
     (57, 25), (52, 30), (45, 38), (40, 45), (38, 52), (40, 66)],
    # Australia
    [(113, -22), (114, -35), (122, -34), (130, -32), (138, -35), (145, -38),
     (150, -37), (153, -28), (146, -19), (142, -11), (132, -11), (125, -14),
     (114, -22)],
    # Greenland
    [(-45, 60), (-20, 70), (-25, 82), (-45, 84), (-60, 80), (-58, 68),
     (-45, 60)],
    # British Isles
    [(-6, 50), (-2, 53), (0, 55), (-3, 58), (-7, 57), (-6, 52), (-6, 50)],
    # Japan
    [(130, 31), (135, 34), (140, 38), (142, 42), (145, 44), (141, 40),
     (138, 36), (132, 33), (130, 31)],
    # Indonesia
    [(95, 5), (105, -6), (115, -8), (125, -8), (135, -4), (130, 0),
     (120, 0), (110, -2), (100, 3), (95, 5)],
    # Madagascar
    [(43, -13), (50, -16), (48, -25), (44, -22), (43, -13)],
    # New Zealand
    [(166, -46), (174, -41), (178, -38), (175, -35), (170, -40), (166, -46)],
]


def draw_world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 239, 244),
                outline=(176, 192, 202))
    MW, MH = 720, 360
    mask = Image.new("L", (MW, MH), 0)
    md = ImageDraw.Draw(mask)
    for poly in CONTINENTS:
        pts = [((lon + 180) / 360 * MW, (90 - lat) / 180 * MH) for lon, lat in poly]
        md.polygon(pts, fill=255)

    step = 5
    dot = (96, 124, 144)
    for gy in range(int(y + 4), int(y + h - 4), step):
        for gx in range(int(x + 4), int(x + w - 4), step):
            lon = (gx - x) / w * 360 - 180
            lat = 90 - (gy - y) / h * 180
            mx = int((lon + 180) / 360 * MW)
            my = int((90 - lat) / 180 * MH)
            if 0 <= mx < MW and 0 <= my < MH and mask.getpixel((mx, my)) > 0:
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=dot)

    for lon, lat, num in PINS:
        px = x + (lon + 180) / 360 * w
        py = y + (90 - lat) / 180 * h
        region = next((p[1] for p in PICTURED if p[0] == num), "WORLD")
        col = REGION_COLORS[region]
        r = 5.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=WHITE)
        f = get_font(6.5, bold=True)
        label = str(num)
        lw = tw(d, label, f)
        d.text((px - lw / 2, py - 4.0), label, font=f, fill=WHITE)


# --------------------------------------------------------------------------
# Sections
# --------------------------------------------------------------------------
def draw_masthead(d):
    d.rectangle([0, 0, W, 4], fill=INK)
    d.line([(M, 11), (W - M, 11)], fill=RULE, width=1)
    f = get_font(8)
    d.text((M, 14), "WORLD NEWS SUMMARY  \u00b7  WEDNESDAY 25 NOVEMBER 2026  \u00b7  WORLD EDITION",
           font=f, fill=INK_SOFT)
    right = "41 STORIES  \u00b7  7 REGIONS  \u00b7  ONE DAY"
    d.text((W - M - tw(d, right, f), 14), right, font=f, fill=INK_SOFT)

    title = "THE WORLD IN ONE DAY"
    size = 58
    tf = get_font(size, bold=True, serif=True)
    while tw(d, title, tf) > W - 2 * M - 8 and size > 24:
        size -= 1
        tf = get_font(size, bold=True, serif=True)
    title_w = tw(d, title, tf)
    d.text(((W - title_w) / 2, 22), title, font=tf, fill=INK)

    sub = "Wednesday, 25 November 2026"
    sf = get_font(24, serif=True)
    sw = tw(d, sub, sf)
    d.text(((W - sw) / 2, 80), sub, font=sf, fill=RED)

    d.line([(M, 110), (W - M, 110)], fill=RULE, width=3)
    d.line([(M, 115), (W - M, 115)], fill=RULE, width=1)


def draw_stats(d, y):
    cells = [
        ("41", "STORIES"),
        ("7", "REGIONS"),
        ("13", "PICTURED"),
        ("28", "LISTED"),
        ("25 NOV", "DATE CHECKED"),
    ]
    x0, x1 = M, W - M
    total = x1 - x0
    cw = total / len(cells)
    for i, (big, small) in enumerate(cells):
        x = x0 + i * cw
        if i > 0:
            d.line([(x, y + 4), (x, y + 40)], fill=(190, 182, 168), width=1)
        bf = get_font(22 if big != "25 NOV" else 16, bold=True, serif=True)
        bw = tw(d, big, bf)
        d.text((x + (cw - bw) / 2, y + 1), big, font=bf, fill=RED)
        lf = get_font(7, bold=True)
        lw = tw(d, small, lf)
        d.text((x + (cw - lw) / 2, y + 28), small, font=lf, fill=INK_SOFT)


def number_badge(d, x, y, num, col, r=7.5):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=col)
    f = get_font(7 if num < 10 else 6.5, bold=True)
    label = str(num)
    lw = tw(d, label, f)
    d.text((x + r - lw / 2, y + r - 4.6), label, font=f, fill=WHITE)


def draw_region_tag(d, x, y, region, size=6.5):
    col = REGION_COLORS[region]
    f = get_font(size, bold=True)
    label = region
    w = tw(d, label, f) + 7
    h = size + 4
    d.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=col)
    d.text((x + 3.5, y + 1.6), label, font=f, fill=WHITE)
    return w


def draw_lead_card(d, story, x, y, w, h):
    num, region, head, summ, icon = story
    col = REGION_COLORS[region]
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=col, width=2)
    d.rectangle([x, y, x + w, y + 3], fill=col)

    panel = 104
    draw_icon_panel(d, x + 9, y + 9, panel, h - 18, icon, region)

    tx = x + 9 + panel + 12
    maxw = x + w - 10 - tx
    number_badge(d, tx, y + 8, num, col, r=9)
    tag_x = tx + 24
    tag_w = draw_region_tag(d, tag_x, y + 10, region, size=7.5)
    d.text((tag_x + tag_w + 6, y + 10),
           "PICTURED STORY", font=get_font(6.5, bold=True), fill=INK_SOFT)

    hf, head_txt = fit_single(d, head, maxw, 20, 12, bold=True, serif=True)
    d.text((tx, y + 30), head_txt, font=hf, fill=INK)
    draw_block(d, summ, tx, y + 56, maxw, 2, 9.5, 7, INK_SOFT, lh=12)


def draw_small_card(d, story, x, y, w, h):
    num, region, head, summ, icon = story
    col = REGION_COLORS[region]
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=(206, 198, 184), width=1)
    d.rectangle([x, y, x, y + h], fill=col, width=0)
    d.rectangle([x, y, x + 3, y + h], fill=col)

    pad = 5
    number_badge(d, x + pad + 1, y + pad, num, col, r=7)
    tag_x = x + pad + 18
    tag_w = draw_region_tag(d, tag_x, y + pad + 1, region, size=6)
    if tw(d, region, get_font(6, bold=True)) + 7 + tag_x + 40 < x + w - pad:
        d.text((tag_x + tag_w + 4, y + pad + 1),
               "PIC", font=get_font(6, bold=True), fill=INK_SOFT)

    hf, lines = fit_block(d, head, w - 2 * pad, 2, 10.5, 8,
                          True, True)
    for i, line in enumerate(lines):
        d.text((x + pad, y + pad + 18 + i * 11.5), line, font=hf, fill=INK)

    draw_icon_panel(d, x + w - 38, y + h - 38, 33, 33, icon, region)

    sy = y + pad + 18 + len(lines) * 11.5 + 2
    draw_block(d, summ, x + pad, sy, w - 2 * pad - 38, 2, 8, 6.5,
               INK_SOFT, lh=9)


def draw_pictured(d, top):
    header_y = top
    d.rectangle([M, header_y, W - M, header_y + 15], fill=INK)
    d.text((M + 6, header_y + 3), "THE DAY IN PICTURES",
           font=get_font(9, bold=True), fill=WHITE)
    right = "13 PICTURED STORIES  \u00b7  NUMBERED 1\u201341"
    d.text((W - M - 6 - tw(d, right, get_font(7.5)), header_y + 4),
           right, font=get_font(7.5), fill=(226, 220, 208))

    lead = PICTURED[0]
    draw_lead_card(d, lead, M, header_y + 21, W - 2 * M, 92)

    grid_top = header_y + 21 + 92 + 7
    cols, rows = 4, 3
    gap = 6
    cw = (W - 2 * M - gap * (cols - 1)) / cols
    ch = 92
    rest = PICTURED[1:]
    for i, story in enumerate(rest):
        r, c = divmod(i, cols)
        x = M + c * (cw + gap)
        y = grid_top + r * (ch + gap)
        draw_small_card(d, story, x, y, cw, ch)


def draw_listed(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=(190, 182, 168))
    d.rectangle([x, y, x + w, y + 15], fill=INK)
    d.text((x + 6, y + 3), "ALSO IN THE NEWS",
           font=get_font(9, bold=True), fill=WHITE)
    right = "28 LISTED STORIES  \u00b7  7 REGIONS"
    d.text((x + w - 6 - tw(d, right, get_font(7.5)), y + 4),
           right, font=get_font(7.5), fill=(226, 220, 208))

    col_w = (w - 10) / 2
    col1_x = x
    col2_x = x + col_w + 10
    top = y + 20

    by_region = {r: [] for r in REGION_ORDER}
    for num, region, head in LISTED:
        by_region[region].append((num, head))

    col1_regions = ["EUROPE", "MIDDLE EAST", "ASIA"]
    col2_regions = ["AMERICAS", "AFRICA", "OCEANIA", "WORLD"]

    def draw_column(cx, regions):
        cy = top
        for region in regions:
            col = REGION_COLORS[region]
            entries = by_region[region]
            d.rectangle([cx, cy, cx + col_w, cy + 12], fill=col)
            d.text((cx + 4, cy + 1.5), region,
                   font=get_font(8, bold=True), fill=WHITE)
            count = str(len(entries))
            d.text((cx + col_w - 4 - tw(d, count, get_font(7.5, bold=True)),
                    cy + 2), count, font=get_font(7.5, bold=True), fill=WHITE)
            cy += 15
            for num, head in entries:
                nf = get_font(8.5, bold=True)
                d.text((cx + 2, cy + 2), str(num), font=nf, fill=col)
                hf, line = fit_single(d, head, col_w - 24, 9, 7)
                d.text((cx + 21, cy + 1), line, font=hf, fill=INK)
                cy += 15
        return cy

    draw_column(col1_x, col1_regions)
    draw_column(col2_x, col2_regions)


def draw_map_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=(190, 182, 168))
    d.rectangle([x, y, x + w, y + 16], fill=INK)
    d.text((x + 5, y + 3), "WHERE IT HAPPENED",
           font=get_font(8.5, bold=True), fill=WHITE)
    right = "PINS = PICTURED"
    d.text((x + w - 5 - tw(d, right, get_font(6.5)), y + 4.5),
           right, font=get_font(6.5), fill=(226, 220, 208))

    map_w = w - 16
    map_h = map_w / 2
    draw_world_map(d, x + 8, y + 21, map_w, map_h)

    ly = y + 21 + map_h + 4
    d.ellipse([x + 9, ly + 2, x + 14, ly + 7], fill=(96, 124, 144))
    d.text((x + 18, ly), "land dot", font=get_font(6.5), fill=INK_SOFT)
    d.ellipse([x + 62, ly, x + 74, ly + 12], fill=RED)
    d.text((x + 78, ly), "pictured story dateline", font=get_font(6.5),
           fill=INK_SOFT)

    cap = "Equirectangular dotted map \u00b7 pins mark pictured story datelines."
    cf, cl = fit_block(d, cap, w - 16, 2, 6.5, 6, False, False)
    for i, line in enumerate(cl):
        d.text((x + 8, ly + 16 + i * 8), line, font=cf, fill=INK_SOFT)


TOP_FIVE = [
    (13, "Shenzhou-24 puts first Pakistani astronaut in orbit"),
    (8, "Houthis hit Saudi refinery and Red Sea ports"),
    (20, "Army detonates 9,500 lb of lead azide in Iowa"),
    (21, "Trump unveils Section 301 tariffs on 14 economies"),
    (22, "US GDP grows 4.3%; PCE inflation stays at 3.8%"),
]


def draw_top_stories(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=(190, 182, 168))
    d.rectangle([x, y, x + w, y + 14], fill=RED)
    d.text((x + 5, y + 2.5), "TODAY'S BIG FIVE",
           font=get_font(8, bold=True), fill=WHITE)
    right = "LEAD STORIES"
    d.text((x + w - 5 - tw(d, right, get_font(6.5)), y + 3),
           right, font=get_font(6.5), fill=(250, 232, 226))

    cy = y + 18
    for num, text in TOP_FIVE:
        region = next(p[1] for p in PICTURED if p[0] == num)
        col = REGION_COLORS[region]
        nf = get_font(8, bold=True)
        d.text((x + 19 - tw(d, str(num), nf), cy), str(num),
               font=nf, fill=col)
        f, line = fit_single(d, text, w - 32, 8, 6.5)
        d.text((x + 24, cy), line, font=f, fill=INK)
        cy += 10.6


def draw_date_check(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(252, 240, 236), outline=RED, width=2)
    d.rectangle([x, y, x + w, y + 15], fill=RED)
    d.text((x + 6, y + 3), "DATE CHECK  \u2014  ALL 41 STORIES DATED WEDNESDAY 25 NOVEMBER 2026",
           font=get_font(8, bold=True), fill=WHITE)
    body = ("Every story in this edition happened, or was first reported, on "
            "25 November 2026 in some time zone. Where an event began earlier, "
            "only its 25 November development is carried here. Times are local "
            "unless stated; the Hodeidah events fall on 25 Nov in UTC+3. "
            "Primary releases on the day: Destatis, ABS, USTR, BEA/BLS and EPA.")
    draw_block(d, body, x + 7, y + 19, w - 14, 3, 8.5, 6.5, INK, lh=10.5)


def draw_footer(d, y):
    d.line([(M, y), (W - M, y)], fill=RULE, width=2)
    d.line([(M, y + 4), (W - M, y + 4)], fill=RULE, width=1)
    f = get_font(6.5)
    d.text((M, y + 9),
           "News summary image  \u00b7  Wednesday, 25 November 2026  \u00b7  compiled from open reports",
           font=f, fill=INK_SOFT)
    d.text((M, y + 19),
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Xinhua, ANI, ANTARA, Destatis, ABS and others.",
           font=f, fill=INK_SOFT)
    d.text((M, y + 29),
           "All illustrations are original drawings made with geometric shapes, not photographs.",
           font=f, fill=INK_SOFT)
    right = "This is a summary image, not a live news service."
    rf = get_font(7, bold=True)
    d.text((W - M - tw(d, right, rf), y + 19), right, font=rf, fill=RED)


def build():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    draw_masthead(d)
    draw_stats(d, 121)

    d.line([(M, 168), (W - M, 168)], fill=(190, 182, 168), width=1)
    draw_pictured(d, 172)

    bottom_top = 588
    draw_map_panel(d, M, bottom_top, 356, 232)
    draw_top_stories(d, M, 826, 356, 74)
    draw_listed(d, 380, bottom_top, W - 380 - M, 312)

    draw_date_check(d, M, 908, W - 2 * M, 60)
    draw_footer(d, 976)

    d.rectangle([0, H - 4, W, H], fill=INK)
    return im


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    im = build()
    im.save(out_path, "PNG", optimize=True)

    limit = 1024 * 1024
    size = os.path.getsize(out_path)
    if size > limit:
        q = im.convert("P", palette=Image.ADAPTIVE, colors=256, dither=Image.NONE)
        q.save(out_path, "PNG", optimize=True)
        size = os.path.getsize(out_path)

    print("wrote %s (%d bytes, %dx%d)" % (out_path, size, im.width, im.height))
    if size > limit:
        raise SystemExit("ERROR: image exceeds 1 MiB (%d bytes)" % size)


if __name__ == "__main__":
    main()
