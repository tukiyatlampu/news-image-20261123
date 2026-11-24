#!/usr/bin/env python3
"""news-image-20261123: one-day world news broadsheet poster.

Writes a 1024x1024 PNG summing up Monday 23 November 2026 world news to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). No network, stdlib +
Pillow only, fully deterministic: two runs write identical bytes.

Layout (1024x1024): masthead -> DAY IN NUMBERS -> STORIES BY REGION bar ->
3 hero picture stories (Nvidia chart, Libya map, Hormuz diagram) -> 10 more
picture stories -> world map (numbered pins 1-13, dots 14-36) + 23 briefs
grouped by region -> DATE CHECK + HOW TO READ boxes.
All 36 stories first reported Mon 23 Nov 2026 (UTC); see DATE CHECK box.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

# ---- palette: warm newsprint broadsheet ----
PAPER = (247, 243, 232)
INK = (20, 20, 20)
MUTED = (90, 86, 76)
RED = (179, 32, 44)
NAVY = (27, 58, 92)
TEAL = (14, 110, 110)
GOLD = (176, 124, 22)
GREEN = (32, 120, 60)
CARD = (255, 255, 255)
LINE = (200, 192, 172)
SKY = (178, 214, 232)
SEA = (140, 190, 220)
LAND = (232, 222, 196)
SAND = (214, 196, 150)
REGION_COLORS = {
    "Europe": (27, 58, 92),
    "Americas": (179, 32, 44),
    "Middle East": (176, 124, 22),
    "Africa": (32, 120, 60),
    "Asia-Pacific": (14, 110, 110),
}
TAG_COLORS = {
    "CONFIRMED": (32, 120, 60),
    "OFFICIAL": (27, 58, 92),
    "REPORTED": (120, 90, 10),
    "CLAIM": (150, 70, 10),
    "DISPUTED": (179, 32, 44),
}


def font(size, bold=False, serif=False):
    """Best available font; falls back to PIL default if none found."""
    cands = []
    if serif:
        cands = ["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf",
                 "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"]
    elif bold:
        cands = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
    else:
        cands = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    for name in cands:
        for base in ("/usr/share/fonts/truetype/dejavu",
                     "/usr/share/fonts/truetype/liberation",
                     "/usr/share/fonts/truetype/noto"):
            path = os.path.join(base, name)
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
    return ImageFont.load_default(size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    """Draw lines; returns y after last line."""
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tag_chip(draw, x, y, tag):
    """Small filled confidence tag; returns width used."""
    fnt = font(9, bold=True)
    w = int(draw.textlength(tag, font=fnt)) + 10
    col = TAG_COLORS.get(tag, MUTED)
    draw.rounded_rectangle([x, y, x + w, y + 14], radius=3, fill=col)
    draw.text((x + 5, y + 2), tag, font=fnt, fill=(255, 255, 255))
    return w


def pin(draw, cx, cy, n, color=RED):
    """Numbered map pin (circle + number)."""
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=color,
                 outline=(255, 255, 255), width=2)
    fnt = font(10, bold=True)
    t = str(n)
    tw = draw.textlength(t, font=fnt)
    draw.text((cx - tw / 2, cy - 6), t, font=fnt, fill=(255, 255, 255))


def dot(draw, cx, cy):
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=INK,
                 outline=(255, 255, 255), width=1)


# ---- story data: every item first reported Mon 23 Nov 2026 (UTC) ----
# picture stories 1-13 (hero 1-3); briefs 14-36. lon/lat for the map.
PICTURE = [
    dict(n=1, region="Americas", lon=-122.0, lat=37.4, tag="CONFIRMED",
         src="REUTERS", art="nvidia",
         title="Huang is back at Nvidia",
         body="Board reinstates Jensen Huang as CEO 11 days after he quit; "
              "shares jump 31%, Nasdaq +6%. Trump called into the board meeting."),
    dict(n=2, region="Europe", lon=20.1, lat=32.1, tag="CLAIM",
         src="KYIV / AP", art="merkury",
         title="Ukraine sinks Russian ship off Libya",
         body="Zelenskyy says seven sea drones sank the corvette Merkury at "
              "Benghazi and hit the cargo ship Angara. UN seeks a probe."),
    dict(n=3, region="Middle East", lon=56.5, lat=26.5, tag="OFFICIAL",
         src="US TREASURY", art="hormuz",
         title="US hits Iran's shadow banks",
         body="Sanctions on 2 dozen+ exchange houses and front firms as the "
              "Hormuz blockade standoff deepens; Iran vows to hit back."),
    dict(n=4, region="Europe", lon=30.5, lat=50.5, tag="CONFIRMED",
         src="AFP", art="kyiv",
         title="15 killed in strikes on Kyiv region",
         body="Boy, 7, pulled alive from rubble in Dymer after 14 hours. "
              "NATO meets in Brussels over missiles in Polish airspace."),
    dict(n=5, region="Europe", lon=4.35, lat=50.85, tag="OFFICIAL",
         src="EU COMMISSION", art="sanctions",
         title="EU proposes sweeping Russia sanctions",
         body="60 banks, crypto platforms and 70 shadow-fleet ships targeted; "
              "Russian teams barred from flying the flag in Europe."),
    dict(n=6, region="Americas", lon=-97.7, lat=30.3, tag="CONFIRMED",
         src="REUTERS", art="crowdstrike",
         title="CrowdStrike buys Zscaler for $43.9bn",
         body="All-stock cybersecurity mega-deal announced Monday as cyber "
              "threats mount; shares in both firms move sharply."),
    dict(n=7, region="Asia-Pacific", lon=106.3, lat=-6.2, tag="CONFIRMED",
         src="AP", art="factory",
         title="24 dead in Indonesia factory fire",
         body="Police pull 24 body bags from the gutted sweets factory in "
              "Cikande; about 30 workers still missing after Saturday's blaze."),
    dict(n=8, region="Europe", lon=-0.1, lat=51.5, tag="OFFICIAL",
         src="NHS", art="nhs",
         title="NHS trials AI breast screening",
         body="EDITH trial invites nearly 700,000 women to test whether AI "
              "spots breast cancer earlier than radiologists alone."),
    dict(n=9, region="Europe", lon=8.65, lat=49.87, tag="OFFICIAL",
         src="ESA / JAXA", art="mercury",
         title="BepiColombo reaches Mercury",
         body="After an eight-year journey, the ESA-JAXA spacecraft pair "
              "enter orbit around Mercury, the Solar System's smallest planet."),
    dict(n=10, region="Middle East", lon=50.9, lat=34.6, tag="REPORTED",
         src="LAWYERS / REUTERS", art="singer",
         title="Iran flogs singer Parastoo Ahmadi",
         body="Ahmadi and four band members get 74 lashes each in Qom over a "
              "2024 livestreamed concert performed without a hijab."),
    dict(n=11, region="Africa", lon=-102.3, lat=21.2, tag="CONFIRMED",
         src="AFRICA TOP SPORTS", art="ghana",
         title="Ghana win Amputee World Cup",
         body="Black Challenge beat Morocco 1-0 in the final in Mexico, a "
              "first world title; Mubarik top scorer with seven goals."),
    dict(n=12, region="Americas", lon=-72.5, lat=7.9, tag="REPORTED",
         src="OFFICIALS", art="drone",
         title="Drones hit Colombia police base",
         body="Explosive drones strike a base in Cucuta, damaging 60 homes; "
              "casualty count unclear. A second station hit in Cesar."),
    dict(n=13, region="Americas", lon=-122.4, lat=37.8, tag="CLAIM",
         src="ANTHROPIC", art="riemann",
         title="AI 'proves' the Riemann hypothesis",
         body="Anthropic says AI helped prove the famous maths puzzle; "
              "mathematicians debate whether the proof can be verified."),
]

BRIEFS = [
    # Europe 14-18
    dict(n=14, region="Europe", lon=24.9, lat=60.2, tag="REPORTED",
         src="FINNISH MFA", title="Finland summons Russian envoy"),
    dict(n=15, region="Europe", lon=19.0, lat=47.5, tag="REPORTED",
         src="BUDAPEST", title="Hungary PM to visit Transcarpathia"),
    dict(n=16, region="Europe", lon=4.6, lat=50.85, tag="CONFIRMED",
         src="SKEYES", title="Belgium airports shut for a day"),
    dict(n=17, region="Europe", lon=21.0, lat=52.2, tag="CLAIM",
         src="POLAND", title="Poland: Russia tried to kill rapper"),
    dict(n=18, region="Europe", lon=4.1, lat=50.85, tag="OFFICIAL",
         src="NATO", title="NATO meets on Poland missiles"),
    # Middle East 19-23
    dict(n=19, region="Middle East", lon=51.4, lat=35.7, tag="OFFICIAL",
         src="TEHRAN", title="Iran vows to counter Hormuz blockade"),
    dict(n=20, region="Middle East", lon=35.2, lat=31.8, tag="REPORTED",
         src="KAN", title="Netanyahu urges Trump to hit Iran"),
    dict(n=21, region="Middle East", lon=34.45, lat=31.5, tag="REPORTED",
         src="OXFAM", title="Gaza 99% toxic, Oxfam report"),
    dict(n=22, region="Middle East", lon=42.95, lat=14.8, tag="CLAIM",
         src="HOUTHI MEDIA", title="Saudi strike on Hodeida kills 4"),
    dict(n=23, region="Middle East", lon=13.2, lat=32.9, tag="OFFICIAL",
         src="UNSMIL", title="UN seeks probe into Libya strikes"),
    # Americas 24-28
    dict(n=24, region="Americas", lon=-92.0, lat=30.2, tag="CONFIRMED",
         src="AMTRAK", title="Amtrak derails in Louisiana"),
    dict(n=25, region="Americas", lon=-119.1, lat=36.1, tag="REPORTED",
         src="POLICE", title="Nine shot at California concert"),
    dict(n=26, region="Americas", lon=-91.3, lat=40.8, tag="OFFICIAL",
         src="WHITE HOUSE", title="Trump pauses Iowa explosives blast"),
    dict(n=27, region="Americas", lon=-107.4, lat=24.8, tag="CONFIRMED",
         src="MEXICO", title="Mexico captures Chapo Isidro"),
    dict(n=28, region="Americas", lon=-76.9, lat=40.3, tag="OFFICIAL",
         src="PA HEALTH", title="Pennsylvania measles deaths reach 9"),
    # Africa 29-32
    dict(n=29, region="Africa", lon=15.5, lat=-1.15, tag="CONFIRMED",
         src="OYO SUMMIT", title="Kenya, DR Congo restore full ties"),
    dict(n=30, region="Africa", lon=7.5, lat=9.1, tag="REPORTED",
         src="ABUJA", title="Tinubu: villa hit by power cuts"),
    dict(n=31, region="Africa", lon=29.5, lat=1.8, tag="OFFICIAL",
         src="WHO", title="Fighting disrupts Ebola response"),
    dict(n=32, region="Africa", lon=28.0, lat=-26.2, tag="OFFICIAL",
         src="CAF", title="CAF, Coca-Cola back AFCON 27/28"),
    # Asia-Pacific 33-36
    dict(n=33, region="Asia-Pacific", lon=77.2, lat=28.6, tag="OFFICIAL",
         src="NEW DELHI", title="India offers \u20ac1.4bn to Nepal"),
    dict(n=34, region="Asia-Pacific", lon=127.0, lat=37.5, tag="OFFICIAL",
         src="SEOUL", title="Seoul: Aden role is not war role"),
    dict(n=35, region="Asia-Pacific", lon=125.8, lat=39.0, tag="REPORTED",
         src="KCNA", title="Kim stresses sovereignty"),
    dict(n=36, region="Asia-Pacific", lon=29.0, lat=41.0, tag="REPORTED",
         src="ISTANBUL", title="Lion on the loose near Istanbul"),
]

NUMBERS = [
    ("+31%", "Nvidia shares"),
    ("+6%", "Nasdaq"),
    ("$43.9bn", "CrowdStrike\u2013Zscaler"),
    ("4.0%", "Euro inflation"),
    ("24", "Dead, Indonesia fire"),
    ("700,000", "NHS AI trial women"),
]

REGION_COUNTS = [("Europe", 10), ("Americas", 9), ("Middle East", 7),
                 ("Africa", 5), ("Asia-Pacific", 5)]

# ---- vector illustrations (no photos; all drawn) ----

def art_nvidia(draw, x, y, w, h):
    """Bar chart: NVDA +31, Nasdaq +6, S&P +5, chips +12."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 40, 26))
    f = font(11, bold=True)
    draw.text((x + 10, y + 6), "MARKET REACTION, MON 23 NOV", font=f,
              fill=(255, 255, 255))
    bars = [("NVDA", 31, (76, 175, 80)), ("NASDAQ", 6, (140, 190, 220)),
            ("S&P 500", 5, (140, 190, 220)), ("CHIPS", 12, (240, 200, 90))]
    bw, gap = 46, 22
    base = y + h - 26
    for i, (label, val, col) in enumerate(bars):
        bx = x + 14 + i * (bw + gap)
        bh = int(val / 40.0 * (h - 72))
        draw.rectangle([bx, base - bh, bx + bw, base], fill=col)
        vf = font(14, bold=True)
        vt = "+%d%%" % val
        draw.text((bx + bw / 2 - draw.textlength(vt, font=vf) / 2,
                   base - bh - 20), vt, font=vf, fill=(255, 255, 255))
        lf = font(10, bold=True)
        draw.text((bx + bw / 2 - draw.textlength(label, font=lf) / 2,
                   base + 5), label, font=lf, fill=(220, 220, 220))
    draw.line([x + 8, base, x + w - 8, base], fill=(255, 255, 255), width=2)


def art_merkury(draw, x, y, w, h):
    """Mini Mediterranean: Libya coast, Benghazi pin, drone path, ship."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    # Libya landmass (top-right) and Europe hint (top-left)
    draw.polygon([(x + w * 0.52, y), (x + w, y), (x + w, y + h * 0.42),
                  (x + w * 0.60, y + h * 0.55), (x + w * 0.45, y + h * 0.38)],
                 fill=SAND)
    draw.polygon([(x, y), (x + w * 0.30, y), (x + w * 0.22, y + h * 0.22),
                  (x, y + h * 0.18)], fill=LAND)
    f = font(10, bold=True)
    draw.text((x + w * 0.66, y + 8), "LIBYA", font=f, fill=(90, 70, 40))
    draw.text((x + 8, y + 6), "MEDITERRANEAN SEA", font=f, fill=NAVY)
    # Benghazi pin + capsized ship
    px, py = x + w * 0.72, y + h * 0.42
    draw.ellipse([px - 26, py + 8, px + 26, py + 26], fill=(60, 60, 60))
    draw.rectangle([px - 26, py + 12, px + 26, py + 18], fill=(30, 30, 30))
    draw.line([px - 26, py + 18, px - 14, py + 26], fill=(30, 30, 30), width=3)
    draw.text((px - 34, py + 30), "MERKURY", font=font(10, bold=True),
              fill=(255, 255, 255))
    pin(draw, px, py, 2)
    # drone path from the north (dashed)
    for i in range(7):
        sx = x + w * 0.30 + i * (w * 0.055)
        sy = y + h * 0.16 + i * (h * 0.035)
        draw.line([sx, sy, sx + 10, sy + 5], fill=(255, 255, 255), width=2)
    draw.text((x + w * 0.30, y + h * 0.72), "7 SEA DRONES",
              font=font(10, bold=True), fill=(255, 255, 255))
    draw.text((x + 8, y + h - 20), "BENGHAZI", font=f, fill=(255, 255, 255))


def art_hormuz(draw, x, y, w, h):
    """Strait of Hormuz diagram: Iran top, Oman bottom, tanker, block."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 52, 84))
    # land: Iran (top) and Oman (bottom)
    draw.polygon([(x, y), (x + w, y), (x + w, y + h * 0.34),
                  (x + w * 0.62, y + h * 0.30), (x + w * 0.42, y + h * 0.42),
                  (x, y + h * 0.36)], fill=(214, 196, 150))
    draw.polygon([(x, y + h), (x + w, y + h), (x + w, y + h * 0.62),
                  (x + w * 0.55, y + h * 0.66), (x + w * 0.40, y + h * 0.58),
                  (x, y + h * 0.66)], fill=(196, 178, 140))
    f = font(10, bold=True)
    draw.text((x + 10, y + 6), "IRAN", font=f, fill=(60, 45, 20))
    draw.text((x + w - 52, y + h - 20), "OMAN", font=f, fill=(60, 45, 20))
    # strait channel + tanker
    draw.text((x + w * 0.30, y + h * 0.40), "STRAIT OF HORMUZ",
              font=f, fill=(255, 255, 255))
    tx, ty = x + w * 0.52, y + h * 0.58
    draw.rectangle([tx, ty, tx + 64, ty + 12], fill=(179, 32, 44))
    draw.rectangle([tx + 10, ty - 8, tx + 26, ty], fill=(179, 32, 44))
    draw.rectangle([tx + 40, ty - 8, tx + 54, ty], fill=(179, 32, 44))
    # blockade marker
    bx, by = x + w * 0.82, y + h * 0.44
    draw.ellipse([bx - 16, by - 16, bx + 16, by + 16], fill=(255, 255, 255),
                 outline=RED, width=3)
    draw.text((bx - 6, by - 7), "!", font=font(16, bold=True), fill=RED)
    draw.text((x + 10, y + h - 20), "2 DOZEN+ EXCHANGE HOUSES HIT",
              font=f, fill=(255, 255, 255))


def art_kyiv(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(38, 48, 66))
    # damaged block of flats
    draw.rectangle([x + 8, y + 18, x + w - 8, y + h], fill=(120, 110, 100))
    for r in range(3):
        for c in range(4):
            wx = x + 14 + c * 13
            wy = y + 24 + r * 16
            lit = (r + c) % 2 == 0
            draw.rectangle([wx, wy, wx + 9, wy + 11],
                           fill=(255, 210, 90) if lit else (50, 45, 40))
    # broken corner + smoke
    draw.polygon([(x + w - 8, y + 18), (x + w - 8, y + 44),
                  (x + w - 26, y + 44), (x + w - 18, y + 18)],
                 fill=(38, 48, 66))
    for i, (sx, sy, sr) in enumerate([(x + w - 20, y + 12, 5),
                                      (x + w - 30, y + 8, 6),
                                      (x + w - 42, y + 12, 4)]):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(180, 180, 180))
    # rescue ladder
    draw.line([x + 10, y + h - 4, x + 30, y + h * 0.45], fill=(240, 200, 90),
              width=3)
    draw.text((x + 6, y + h - 14), "KYIV", font=font(9, bold=True),
              fill=(255, 255, 255))


def art_sanctions(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(27, 58, 92))
    # bank building
    draw.rectangle([x + 8, y + h - 22, x + w - 8, y + h - 14], fill=(255, 255, 255))
    for i in range(4):
        cx = x + 16 + i * 12
        draw.rectangle([cx, y + 26, cx + 6, y + h - 22], fill=(255, 255, 255))
    draw.polygon([(x + 4, y + 28), (x + w - 4, y + 28), (x + w / 2, y + 12)],
                 fill=(240, 200, 90))
    f = font(11, bold=True)
    draw.text((x + 6, y + h - 13), "60 BANKS", font=font(9, bold=True),
              fill=(255, 255, 255))
    # crossed crypto coin
    cx, cy = x + w - 16, y + 16
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(240, 200, 90))
    draw.text((cx - 4, cy - 8), "B", font=font(12, bold=True), fill=INK)
    draw.line([cx - 13, cy - 13, cx + 13, cy + 13], fill=RED, width=3)


def art_crowdstrike(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(20, 20, 20))
    # two merging puzzle pieces -> shield
    draw.polygon([(x + 10, y + 14), (x + w / 2 - 2, y + 14),
                  (x + w / 2 - 2, y + 26), (x + w / 2 + 10, y + 26),
                  (x + w / 2 + 10, y + 14), (x + w - 10, y + 14),
                  (x + w - 10, y + h - 14), (x + w / 2, y + h - 4),
                  (x + 10, y + h - 14)], fill=(179, 32, 44))
    draw.text((x + w / 2 - 7, y + h / 2 - 12), "C+Z",
              font=font(16, bold=True), fill=(255, 255, 255))
    draw.text((x + 6, y + h - 15), "$43.9bn", font=font(11, bold=True),
              fill=(240, 200, 90))


def art_factory(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 40, 32))
    # factory silhouette
    draw.rectangle([x + 6, y + h - 26, x + w - 6, y + h], fill=(40, 30, 25))
    draw.rectangle([x + 10, y + h - 44, x + 18, y + h - 26], fill=(40, 30, 25))
    draw.rectangle([x + 22, y + h - 38, x + 30, y + h - 26], fill=(40, 30, 25))
    # flames
    for i, (fx, fy, fs) in enumerate([(x + 14, y + 16, 9), (x + 30, y + 10, 12),
                                      (x + 46, y + 18, 8)]):
        draw.polygon([(fx - fs, fy + fs), (fx, fy - fs), (fx + fs, fy + fs)],
                     fill=(240, 120, 20) if i % 2 else (255, 190, 40))
    draw.text((x + 6, y + h - 14), "24 DEAD", font=font(11, bold=True),
              fill=(255, 255, 255))


def art_nhs(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(14, 110, 110))
    # scan screen
    draw.rectangle([x + 8, y + 10, x + w - 8, y + h - 20], fill=(255, 255, 255))
    draw.ellipse([x + 14, y + 16, x + w - 14, y + h - 26],
                 outline=(14, 110, 110), width=2)
    draw.ellipse([x + w / 2 - 5, y + h / 2 - 5, x + w / 2 + 5, y + h / 2 + 5],
                 fill=RED)
    draw.text((x + 6, y + h - 15), "700K",
              font=font(10, bold=True), fill=(255, 255, 255))


def art_mercury(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(10, 12, 30))
    # stars
    for sx, sy in [(x + 8, y + 8), (x + w - 12, y + 12), (x + 14, y + h - 18),
                   (x + w - 20, y + h - 10), (x + w / 2, y + 6)]:
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    # Mercury + orbit + spacecraft
    cx, cy = x + w / 2, y + h / 2 + 4
    draw.ellipse([x + 6, y + 6, x + w - 6, y + h - 6], outline=(150, 150, 170),
                 width=1)
    draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(190, 170, 150))
    draw.ellipse([cx - 8, cy - 6, cx - 2, cy, ], fill=(150, 130, 110))
    draw.ellipse([cx + 4, cy + 4, cx + 10, cy + 10], fill=(150, 130, 110))
    draw.rectangle([x + w - 22, y + 12, x + w - 10, y + 20], fill=(240, 200, 90))
    draw.text((x + 6, y + h - 14), "8 YRS", font=font(10, bold=True),
              fill=(255, 255, 255))


def art_singer(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(90, 30, 46))
    # microphone + bars
    draw.ellipse([x + w / 2 - 10, y + 12, x + w / 2 + 10, y + 32],
                 fill=(220, 220, 220))
    draw.rectangle([x + w / 2 - 3, y + 32, x + w / 2 + 3, y + h - 14],
                   fill=(220, 220, 220))
    for i in range(4):
        bx = x + 8 + i * 14
        draw.line([bx, y + 6, bx, y + h - 6], fill=(40, 10, 16), width=3)
    draw.text((x + 6, y + h - 14), "74", font=font(10, bold=True),
              fill=(255, 255, 255))


def art_ghana(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(32, 120, 60))
    # pitch lines + ball + trophy
    draw.line([x, y + h / 2, x + w, y + h / 2], fill=(255, 255, 255), width=1)
    draw.ellipse([x + w / 2 - 12, y + h / 2 - 12, x + w / 2 + 12,
                  y + h / 2 + 12], outline=(255, 255, 255), width=1)
    draw.ellipse([x + 12, y + 10, x + 30, y + 28], fill=(255, 255, 255))
    draw.polygon([(x + 14, y + 12), (x + 18, y + 18), (x + 22, y + 12),
                  (x + 26, y + 18), (x + 21, y + 26), (x + 17, y + 26)],
                 fill=INK)
    # trophy
    tx, ty = x + w - 22, y + h - 22
    draw.polygon([(tx - 6, ty - 12), (tx + 6, ty - 12), (tx + 3, ty + 2),
                  (tx - 3, ty + 2)], fill=(240, 200, 90))
    draw.rectangle([tx - 5, ty + 2, tx + 5, ty + 6], fill=(240, 200, 90))
    draw.text((x + 6, y + h - 14), "1-0", font=font(11, bold=True),
              fill=(255, 255, 255))


def art_drone(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(70, 80, 95))
    # quadcopter
    cx, cy = x + w / 2, y + h / 2 - 4
    draw.rectangle([cx - 14, cy - 4, cx + 14, cy + 4], fill=(30, 30, 30))
    for dx, dy in [(-16, -12), (16, -12), (-16, 12), (16, 12)]:
        draw.ellipse([cx + dx - 8, cy + dy - 3, cx + dx + 8, cy + dy + 3],
                     fill=(200, 200, 200))
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    # houses below
    for i in range(3):
        hx = x + 8 + i * 18
        draw.polygon([(hx, y + h - 14), (hx + 7, y + h - 22),
                      (hx + 14, y + h - 14)], fill=(179, 32, 44))
        draw.rectangle([hx + 1, y + h - 14, hx + 13, y + h - 4],
                       fill=(220, 210, 190))
    draw.text((x + 6, y + 4), "60 HOMES HIT", font=font(10, bold=True),
              fill=(255, 255, 255))


def art_riemann(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(247, 243, 232))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    f = font(16, bold=True)
    draw.text((x + 8, y + 8), "\u03b6(s) = 0", font=f, fill=INK)
    draw.text((x + 8, y + 30), "Re(s) = \u00bd ?", font=font(13, bold=True),
              fill=INK)
    # checkmark vs question
    draw.line([x + 10, y + h - 14, x + 18, y + h - 6, x + 30, y + h - 24],
              fill=GREEN, width=3)
    draw.text((x + w - 16, y + h - 22), "?", font=font(16, bold=True),
              fill=RED)


ART = {"nvidia": art_nvidia, "merkury": art_merkury, "hormuz": art_hormuz,
       "kyiv": art_kyiv, "sanctions": art_sanctions,
       "crowdstrike": art_crowdstrike, "factory": art_factory,
       "nhs": art_nhs, "mercury": art_mercury, "singer": art_singer,
       "ghana": art_ghana, "drone": art_drone, "riemann": art_riemann}

# ---- simplified world map (stylised continents, lon/lat polygons) ----
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 73), (-60, 60), (-55, 47), (-65, 44), (-75, 35), (-80, 25),
     (-85, 20), (-90, 15), (-95, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-140, 60), (-165, 60)],
    [(-58, 64), (-45, 60), (-30, 68), (-40, 76), (-60, 76)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -38), (-65, -45), (-70, -52), (-73, -40),
     (-70, -20), (-78, -5), (-80, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 70), (40, 68),
     (45, 68), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (19, 42),
     (12, 44), (3, 42), (-2, 37), (-9, 37)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 20), (43, 12), (48, 10), (51, 12), (48, 0), (40, -10), (35, -20),
     (32, -28), (25, -34), (18, -35), (14, -25), (12, -12), (9, 4),
     (-8, 5), (-13, 8), (-17, 15)],
    [(40, 68), (60, 70), (75, 73), (90, 75), (110, 76), (130, 72),
     (160, 70), (178, 66), (170, 60), (162, 55), (158, 50), (142, 45),
     (140, 40), (130, 35), (127, 35), (122, 30), (120, 22), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 13), (77, 8),
     (72, 20), (66, 25), (60, 25), (55, 26), (50, 28), (48, 30), (44, 30),
     (40, 35), (36, 36), (35, 30), (42, 40), (40, 45)],
    [(113, -22), (114, -32), (124, -33), (130, -32), (137, -35), (142, -38),
     (147, -39), (150, -37), (153, -27), (150, -22), (146, -19), (142, -11),
     (136, -12), (132, -11), (126, -14), (122, -17), (118, -20), (113, -22)],
    [(95, 5), (98, 10), (100, 5), (104, -2), (106, -6), (110, -8),
     (114, -9), (119, -9), (122, -4), (120, 0), (117, 3), (112, 2),
     (105, -3), (100, -2), (97, 2)],  # Indonesia
    [(129, 31), (131, 34), (135, 34), (138, 36), (140, 39), (141, 43),
     (143, 42), (140, 38), (137, 35), (133, 33), (130, 31)],  # Japan
    [(167, -41), (170, -43), (173, -40), (175, -38), (174, -35),
     (172, -35), (169, -38)],  # New Zealand
]


def project(lon, lat, mx, my, mw, mh):
    """Equirectangular projection into map box."""
    return (mx + (lon + 180.0) / 360.0 * mw,
            my + (90.0 - lat) / 180.0 * mh)


def draw_map(draw, mx, my, mw, mh):
    draw.rectangle([mx, my, mx + mw, my + mh], fill=SKY,
                   outline=LINE, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=(180, 168, 130))
    # brief dots first (under pins), then numbered pins
    dot_off = {19: (14, 8), 20: (8, 4), 21: (-8, -6), 16: (4, 8),
               18: (-4, -8)}
    for b in BRIEFS:
        cx, cy = project(b["lon"], b["lat"], mx, my, mw, mh)
        dx, dy = dot_off.get(b["n"], (0, 0))
        dot(draw, cx + dx, cy + dy)
    # Europe cluster pins get leader-line offsets so they do not stack
    pin_off = {8: (-16, -12), 5: (0, 15), 9: (17, -9), 13: (-15, 11)}
    for s in PICTURE:
        cx, cy = project(s["lon"], s["lat"], mx, my, mw, mh)
        dx, dy = pin_off.get(s["n"], (0, 0))
        if (dx, dy) != (0, 0):
            draw.line([cx, cy, cx + dx, cy + dy], fill=INK, width=1)
            dot(draw, cx, cy)
        pin(draw, cx + dx, cy + dy, s["n"])


def section_label(draw, x, y, text):
    fnt = font(11, bold=True)
    draw.text((x, y), text, font=fnt, fill=RED)
    return y + 15


def draw_masthead(draw):
    draw.text((10, 6), "THE WORLD IN ONE DAY", font=font(40, serif=True),
              fill=INK)
    df = font(13, bold=True)
    draw.text((10, 50), "MONDAY 23 NOVEMBER 2026  \u00b7  36 STORIES  \u00b7  "
              "5 REGIONS  \u00b7  ALL TIMES UTC", font=df, fill=NAVY)
    rf = font(11, bold=True)
    rt = "ONE DAY \u00b7 ONE IMAGE"
    draw.text((W - 10 - draw.textlength(rt, font=rf), 52), rt, font=rf,
              fill=RED)
    draw.rectangle([10, 66, W - 10, 69], fill=RED)


def draw_numbers(draw):
    y = section_label(draw, 10, 74, "DAY IN NUMBERS \u2014 EVERY FIGURE "
                      "FIRST REPORTED MON 23 NOV")
    cw = (W - 20) / 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = 10 + i * cw
        draw.text((x, y), num, font=font(22, bold=True), fill=RED)
        draw.text((x, y + 26), cap, font=font(10), fill=MUTED)
        if i:
            draw.line([x - 5, y, x - 5, y + 40], fill=LINE, width=1)
    draw.line([10, 134, W - 10, 134], fill=LINE, width=1)


def draw_region_bar(draw):
    y = 140
    draw.text((10, y), "STORIES BY REGION", font=font(11, bold=True),
              fill=RED)
    total = sum(c for _, c in REGION_COUNTS)
    bx, bw, bh = 10, W - 20, 12
    cx = bx
    for name, cnt in REGION_COUNTS:
        seg = bw * cnt / total
        draw.rectangle([cx, y + 16, cx + seg - 1, y + 16 + bh],
                       fill=REGION_COLORS[name])
        cx += seg
    labels = "   ".join("%s %d" % (n, c) for n, c in REGION_COUNTS)
    draw.text((10, y + 32), labels, font=font(10, bold=True), fill=INK)
    draw.line([10, 188, W - 10, 188], fill=LINE, width=1)


def draw_hero(draw, s, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    ART[s["art"]](draw, x + 1, y + 1, w - 2, 140)
    ty = y + 148
    nf = font(13, bold=True)
    draw.text((x + 8, ty), "%d." % s["n"], font=nf, fill=RED)
    lines = wrap(draw, s["title"], font(16, bold=True), w - 26)
    text_block(draw, x + 26, ty, lines[:2], font(16, bold=True),
               leading=19)
    by = ty + 19 * len(lines[:2]) + 2
    blines = wrap(draw, s["body"], font(11), w - 16)
    text_block(draw, x + 8, by, blines[:3], font(11), leading=14)
    fy = y + h - 20
    chip_w = tag_chip(draw, x + 8, fy, s["tag"])
    sf = font(9, bold=True)
    draw.text((x + 8 + chip_w + 6, fy + 2), s["src"], font=sf, fill=MUTED)


def draw_mid(draw, s, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    ART[s["art"]](draw, x + 1, y + 1, 62, h - 2)
    tx = x + 68
    lines = wrap(draw, "%d. %s" % (s["n"], s["title"]), font(11, bold=True),
                 w - 74)
    text_block(draw, tx, y + 5, lines[:3], font(11, bold=True), leading=13)
    tag_chip(draw, tx, y + h - 18, s["tag"])


def draw_briefs(draw, x, y, w, h):
    """Briefs grouped by region, two columns."""
    groups = [("Europe", [b for b in BRIEFS if b["region"] == "Europe"]),
              ("Middle East", [b for b in BRIEFS
                               if b["region"] == "Middle East"]),
              ("Americas", [b for b in BRIEFS if b["region"] == "Americas"]),
              ("Africa", [b for b in BRIEFS if b["region"] == "Africa"]),
              ("Asia-Pacific", [b for b in BRIEFS
                                if b["region"] == "Asia-Pacific"])]
    col_w = (w - 12) / 2
    cols = [[groups[0], groups[1]], [groups[2], groups[3], groups[4]]]
    for ci, col in enumerate(cols):
        cx = x + ci * (col_w + 12)
        cy = y
        for name, items in col:
            draw.text((cx, cy), name.upper(), font=font(10, bold=True),
                      fill=REGION_COLORS[name])
            cy += 15
            for b in items:
                nf = font(10, bold=True)
                draw.text((cx, cy), "%d." % b["n"], font=nf, fill=RED)
                lines = wrap(draw, b["title"], font(10), col_w - 22)
                text_block(draw, cx + 20, cy, lines[:2], font(10),
                           leading=12)
                cy += 12 * len(lines[:2]) + 4
            cy += 4


def draw_bottom(draw):
    y = 938
    # DATE CHECK box
    draw.rectangle([10, y, 508, 1010], outline=RED, width=2)
    draw.text((18, y + 6), "DATE CHECK \u2014 WHAT WE LEFT OUT",
              font=font(11, bold=True), fill=RED)
    dc = font(9)
    lines = [
        "SUN 22 NOV \u2014 OUT: COP31 talks collapse, Antalya (AFP); "
        "Khartoum drone strikes (AFP).",
        "SAT 21 NOV \u2014 OUT: Indonesia factory fire breaks out "
        "(toll confirmed Mon 23 Nov).",
        "NOT YET: EU sanctions need 27-state approval \u00b7 Istanbul "
        "lion at large \u00b7 NATO outcome late.",
    ]
    yy = y + 22
    for line in lines:
        yy = text_block(draw, 18, yy, wrap(draw, line, dc, 478), dc,
                        leading=12) + 2
    # HOW TO READ box
    draw.rectangle([516, y, W - 10, 1010], outline=NAVY, width=2)
    draw.text((524, y + 6), "HOW TO READ", font=font(11, bold=True),
              fill=NAVY)
    hr = font(9)
    hlines = [
        "Thumbnail: date, 3 leads, 6 big numbers. Full size: 36 stories "
        "by region.",
        "Pins 1\u201313 = picture stories; dots 14\u201336 = briefs.",
        "Tags: CONFIRMED 2+ outlets \u00b7 OFFICIAL the body \u00b7 "
        "REPORTED 1 outlet \u00b7 CLAIM 1 side.",
    ]
    yy = y + 22
    for line in hlines:
        yy = text_block(draw, 524, yy, wrap(draw, line, hr, 478), hr,
                        leading=12) + 2

def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_numbers(draw)
    draw_region_bar(draw)
    # hero tier: 3 leads
    hw, hy, hh = 326, 194, 258
    for i, s in enumerate(PICTURE[:3]):
        draw_hero(draw, s, 10 + i * (hw + 13), hy, hw, hh)
    # picture stories: 10 more, 5 x 2
    mw, mh = 196, 96
    for i, s in enumerate(PICTURE[3:]):
        r, c = divmod(i, 5)
        draw_mid(draw, s, 10 + c * (mw + 6), 458 + r * (mh + 6), mw, mh)
    # world map (left) + briefs by region (right)
    my = 660
    section_label(draw, 10, my, "WORLD MAP \u2014 PINS 1\u201313 \u00b7 "
                  "DOTS 14\u201336")
    draw_map(draw, 10, my + 18, 386, 220)
    cap = ("Pin #9 BepiColombo sits at ESA mission control, Darmstadt. "
           "Pins are picture stories; dots are briefs.")
    text_block(draw, 10, my + 244,
               wrap(draw, cap, font(9), 386), font(9), fill=MUTED,
               leading=12)
    draw.text((408, my), "ALSO ON \u2014 BRIEFS BY REGION",
              font=font(11, bold=True), fill=RED)
    draw_briefs(draw, 408, my + 18, 606, 256)
    draw_bottom(draw)
    draw.text((10, 1015),
              "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 NYT \u00b7 Eurostat "
              "\u00b7 NHS \u00b7 ESA \u00b7 Daily Summary of World. "
              "No photos \u2014 all art drawn.",
              font=font(9), fill=MUTED)
    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img = build()
    img.save(OUT_PATH, format="PNG", compress_level=9)
    data = open(OUT_PATH, "rb").read()
    if len(data) > 1048576:
        print("FAIL: entry.png %d bytes exceeds 1 MiB" % len(data),
              file=sys.stderr)
        sys.exit(1)
    if img.size != (1024, 1024):
        print("FAIL: size %s is not 1024x1024" % (img.size,), file=sys.stderr)
        sys.exit(1)
    print("WROTE %s" % OUT_PATH)
    print("SIZE %d bytes" % len(data))
    print("SHA256 %s" % hashlib.sha256(data).hexdigest())
    print("STORIES %d (13 picture + 23 briefs)" % (len(PICTURE)
                                                    + len(BRIEFS)))


if __name__ == "__main__":
    main()
