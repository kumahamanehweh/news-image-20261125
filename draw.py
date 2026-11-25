#!/usr/bin/env python3
"""news-image-20261125 v2 — draw the one-page newspaper for Wed 25 Nov 2026.

Build-time only: the grader never runs this file. It renders entry.png
(1024x1024, <= 1 MiB) from the story list below. main.py ships the image.
Stdlib + PIL only. Fonts: DejaVu (system).

Layout (1024x1024, all sections fitted, no overflow): kicker, counts,
masthead, one-sentence summary, UTC strip, big numbers, region strip,
4 illustrated leads, 10 small stories, VOICES OF THE DAY, world map +
31 one-line briefs, markets chart + HOW TO READ, tomorrow strip,
DATE CHECK, sources.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (246, 239, 219)
INK = (20, 20, 20)
RED = (185, 28, 28)
DARK = (31, 41, 55)
GOLD = (212, 175, 55)
BLUE = (30, 78, 121)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
SEA = (207, 227, 238)
LAND = (227, 213, 168)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _cache:
        paths = {
            "serif": ["DejaVuSerif.ttf"],
            "serif_b": ["DejaVuSerif-Bold.ttf"],
            "serif_i": ["DejaVuSerif-Italic.ttf", "DejaVuSerif.ttf"],
            "sans": ["DejaVuSans.ttf"],
            "sans_b": ["DejaVuSans-Bold.ttf"],
            "sans_i": ["DejaVuSans-Oblique.ttf", "DejaVuSans.ttf"],
        }
        f = None
        for cand in paths[name]:
            p = os.path.join(FONT_DIR, cand)
            if os.path.exists(p):
                f = ImageFont.truetype(p, size)
                break
        if f is None:
            f = ImageFont.load_default()
        _cache[key] = f
    return _cache[key]


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, fill, max_w, lh=None):
    if lh is None:
        lh = int(fnt.size * 1.25)
    lines = wrap(d, text, fnt, max_w)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def badge(d, x, y, label, color, size=8):
    fnt = font("sans_b", size)
    tw = d.textlength(label, font=fnt)
    w = int(tw) + 10
    h = size + 5
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=color)
    d.text((x + 5, y + 2), label, font=fnt, fill=WHITE)
    return w


BADGE_COLORS = {
    "CONFIRMED": (30, 125, 50),
    "REPORTED": (183, 121, 31),
    "CLAIM": (107, 79, 161),
    "FORECAST": (46, 90, 136),
    "OFFICIAL": (55, 71, 79),
}

# ---------------------------------------------------------------- data
SENTENCE = ("A Pakistani reached orbit, Houthis threatened Jeddah, and "
            "tariff fears sank Asian markets.")

UTC_ITEMS = [
    ("00:18", "Shenzhou-24 lifts off"),
    ("early", "Asia shares plunge"),
    ("morning", "Houthis threaten Jeddah"),
    ("13:30 GMT", "US PCE + GDP due"),
    ("15:00 CET", "Chess Game 2, Geneva"),
]

BIG = [
    ("1st", "Pakistani in orbit"),
    ("-8.2%", "Taiex"),
    ("90+", "experiments on Shenzhou-24"),
    ("81.5m", "Americans traveling"),
    ("$90.30", "Brent crude"),
]

REGIONS = [
    ("ASIA", 20, (192, 57, 43)),
    ("AMERICAS", 11, (46, 90, 136)),
    ("MIDDLE EAST", 6, (183, 121, 31)),
    ("EUROPE", 4, (107, 79, 161)),
    ("AFRICA", 2, (46, 125, 50)),
    ("PACIFIC", 2, (14, 124, 123)),
]

LEADS = [
    {
        "n": 1, "tag": "CHINA · SPACE", "color": (192, 57, 43),
        "head": "First Pakistani in orbit as Shenzhou-24 lifts off",
        "body": ("China launches Shenzhou-24 at dawn; Muhammad Zeeshan Ali, "
                 "40, becomes the first Pakistani in orbit and the first "
                 "foreign astronaut aboard Tiangong station."),
        "src": "Reuters", "art": "rocket",
    },
    {
        "n": 2, "tag": "YEMEN · RED SEA", "color": (30, 78, 121),
        "head": "Houthis threaten Jeddah; Saudis strike Hodeidah",
        "body": ("Houthis say Jeddah and every Saudi Red Sea port will be "
                 "targeted if Riyadh attacks Hodeidah; the Saudi-led "
                 "coalition hits Hodeidah, Saada and Amran."),
        "src": "Reuters", "art": "redsea",
    },
    {
        "n": 3, "tag": "MARKETS · TARIFFS", "color": (183, 121, 31),
        "head": "Asia shares plunge as US tariff threat returns",
        "body": ("Taipei dives 8.2%, Seoul 4.7%, Tokyo 3.2% as Washington "
                 "readies tariff findings on China, the EU and 14 more "
                 "economies; the Nasdaq fell 1.5% on Tuesday."),
        "src": "Reuters", "art": "chart",
    },
    {
        "n": 4, "tag": "PACIFIC · PACT", "color": (14, 124, 123),
        "head": "Australia signs Solomons security pact",
        "body": ("Canberra becomes defence partner of choice; no foreign "
                 "military bases, and the Solomons drops its China pact. "
                 "Albanese and Wale sign in Canberra."),
        "src": "Reuters / AAP", "art": "pact",
    },
]

SMALLS = [
    {"n": 5, "tag": "MOSCOW · WAR", "color": (107, 79, 161),
     "head": "Russia calls ship attacks 'terrorism'",
     "body": "Moscow warns Kyiv after ship hits.",
     "badge": "CLAIM", "src": "BD Global Times", "art": "ship"},
    {"n": 6, "tag": "SHANGHAI · PROBE", "color": (192, 57, 43),
     "head": "Shanghai party pledges loyalty after Chen probe",
     "body": "4th Politburo member probed.",
     "badge": "OFFICIAL", "src": "Reuters", "art": "skyline"},
    {"n": 7, "tag": "GENEVA · CHESS", "color": (46, 90, 136),
     "head": "Chess Game 2 today; Gukesh has White",
     "body": "Score 1/2–1/2 after Game 1 drawn.",
     "badge": "CONFIRMED", "src": "FIDE / Chess.com", "art": "chess"},
    {"n": 8, "tag": "USA · ECONOMY", "color": (183, 121, 31),
     "head": "PCE and GDP due today; gold $3,544",
     "body": "Q3 GDP seen 3.6%, core PCE 3.2%.",
     "badge": "FORECAST", "src": "BEA", "art": "bars"},
    {"n": 9, "tag": "USA · TRAVEL", "color": (46, 90, 136),
     "head": "Thanksgiving crush: today is peak travel",
     "body": "81.5m Americans on the move.",
     "badge": "OFFICIAL", "src": "AAA", "art": "plane"},
    {"n": 10, "tag": "CONGO · EBOLA", "color": (30, 125, 50),
     "head": "WHO evacuates staff from Ebola hospital",
     "body": "Staff sheltered 3 days amid fighting.",
     "badge": "CONFIRMED", "src": "WHO / Reuters", "art": "cross"},
    {"n": 11, "tag": "WASHINGTON · AID", "color": (107, 79, 161),
     "head": "US envoy 'not certain' Israel aid ends this year",
     "body": "As Trump promised.",
     "badge": "REPORTED", "src": "Reuters", "art": "dome"},
    {"n": 12, "tag": "DELHI · MARKETS", "color": (30, 125, 50),
     "head": "Sensex jumps 1,400 pts as Asia sells off",
     "body": "Nifty crosses 25,700.",
     "badge": "CONFIRMED", "src": "Hindu BusinessLine", "art": "rise"},
    {"n": 13, "tag": "GAZA · WAR", "color": (192, 57, 43),
     "head": "Gaza death toll reaches 74,746",
     "body": "WAFA.",
     "badge": "REPORTED", "src": "WAFA", "art": "blocks"},
    {"n": 14, "tag": "DOHA · CRICKET", "color": (14, 124, 123),
     "head": "Suryavanshi smashes 204* off 53 balls",
     "body": "15-year-old sets world record.",
     "badge": "CONFIRMED", "src": "Reports", "art": "bat"},
]

# One line each at 8.5pt in a 331px column (kept <= 60 chars).
BRIEFS = [
    (15, "Brent $90.30, WTI $80.94 as Hormuz attacks weigh."),
    (16, "Gold holds near $3,544, a 14-month low, before PCE."),
    (17, "Nasdaq futures fall 2.5% on tariff news."),
    (18, "Korea Exchange briefly halts Kospi trading."),
    (19, "Kioxia, Advantest slide 10%+ in Tokyo chip rout."),
    (20, "Hang Seng rises 1.0% against the regional rout."),
    (21, "Fed Beige Book due 14:00 ET; Dec hike nearly locked in."),
    (22, "Jobless claims seen at 200K; durable goods +1.1%."),
    (23, "Core PCE seen +0.3% m/m, 3.2% y/y."),
    (24, "US markets shut Thursday for Thanksgiving."),
    (25, "Trump spares turkeys Freedom and Feathers."),
    (26, "Three tankers hit mines in Hormuz; Iran rejects US talks."),
    (27, "US blacklists Singapore chip firm Megaspeed."),
    (28, "WFP: 266m face acute food insecurity."),
    (29, "Analysis: 700,000+ Russian troops killed in Ukraine war."),
    (30, "Oxfam: pollution risks across 99%+ of Gaza."),
    (31, "Democrats could use Congress majority to pressure Trump."),
    (32, "India to buy 76 naval utility helicopters for ₹15,000 Cr."),
    (33, "India denies defence data breach, orders cyber audit."),
    (34, "Delhi hosts first India-EU Maritime Roundtable."),
    (35, "Priyansh Arya hits 181, highest T20 score by an Indian."),
    (36, "Varanasi glows for Dev Deepawali; Murmu at Bali Jatra."),
    (37, "J&K Police stop Mehbooba Mufti at Chandanwari."),
    (38, "Coal Ministry extends mining accreditation to 5 years."),
    (39, "Beijing names no Chen replacement yet."),
    (40, "Shanghai officials hold late-night meeting on Chen probe."),
    (41, "Wale to legislate to “bed down” Solomons treaty."),
    (42, "Ali to run cyanobacteria experiment in orbit."),
    (43, "Tang Hongbo first to board Tiangong three times."),
    (44, "Shenzhou-24 emblem carries Pakistan's jasmine."),
    (45, "Gukesh spent 36 minutes on one move in Game 1."),
]

VOICES = [
    ("“Certainly that day will come.”",
     "Ahsan Iqbal, Pakistan's Planning Minister, on Pakistan flying "
     "astronauts alone one day.", "AP, Jiuquan"),
    ("“The re-emergence of tariffs from the USTR has been met with a "
     "collective sigh from investors.”",
     "Chris Weston, head of research, Pepperstone.", "Reuters"),
    ("“Australia is proud to be the Solomon Islands' main security "
     "partner, and that's a responsibility that we take seriously.”",
     "Anthony Albanese, Prime Minister of Australia.", "AAP, Canberra"),
]

CHART_BARS = [
    ("Taiex", -8.2), ("Kospi", -4.7), ("Nikkei", -3.2),
    ("Shanghai", -1.0), ("Hang Seng", 1.0),
]

DATE_CHECK = [
    ("TUE 24 NOV", "Dow tops 50,000 for the first time (50,018.70); CIA/ODNI "
     "breach first reported; Chen Jining probe announced; Zelenskiy confirms "
     "Sparta II hit; Huawei guilty of stealing trade secrets; Nvidia falls "
     "5.9%, Dell slides 11.8% after record quarter; Hasina plans 16 Dec "
     "return; Nepal quake M5.6."),
    ("MON 23 NOV", "Prabowo names two VP candidates; Saudi strikes kill 17 "
     "telecom workers in Hodeidah."),
    ("SUN 22 NOV", "COP31 ends with no pact."),
    ("THU 12 NOV", "Gibran quits as Indonesia's vice-president."),
]

PINS = [
    (1, 98.5, 39.7), (2, 39.2, 21.5), (3, 121.5, 25.0),
    (4, 149.1, -35.3), (5, 37.6, 55.8), (6, 121.5, 31.2),
    (7, 6.1, 46.2), (8, -87.6, 41.9), (9, -77.0, 38.9),
    (10, 29.5, 1.5), (11, -74.0, 40.7), (12, 77.2, 28.6),
    (13, 34.5, 31.5), (14, 51.5, 25.3),
]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 66),
     (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 29), (-90, 21), (-95, 19), (-100, 16), (-105, 20),
     (-110, 23), (-115, 30), (-125, 40), (-125, 49), (-135, 58),
     (-150, 60), (-165, 60)],
    [(-80, 10), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-65, -45), (-70, -54),
     (-73, -37), (-72, -20), (-77, -12), (-80, -3)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (30, -29),
     (20, -35), (15, -27), (12, -18), (9, -1), (9, 4), (-8, 5), (-13, 8),
     (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (40, 68), (45, 68),
     (50, 60), (40, 55), (35, 50), (30, 45), (28, 41), (23, 40), (19, 42),
     (12, 44), (8, 44), (3, 43), (-2, 37), (-9, 37)],
    [(30, 70), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 69), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52),
     (150, 59), (142, 50), (140, 40), (135, 35), (130, 33), (127, 35),
     (122, 38), (120, 32), (115, 23), (110, 20), (108, 12), (105, 9),
     (100, 8), (97, 16), (94, 17), (92, 21), (89, 22), (86, 20), (82, 17),
     (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25), (62, 25),
     (58, 26), (56, 27), (52, 28), (50, 29), (48, 30), (44, 29), (40, 32),
     (36, 36), (30, 36), (30, 42), (35, 45), (40, 48), (45, 52), (50, 55),
     (55, 58), (60, 60)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -11), (140, -17),
     (136, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# ---------------------------------------------------------------- art
def art_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(11, 31, 58))
    import random
    rnd = random.Random(7)
    for _ in range(28):
        sx, sy = x + rnd.randint(2, w - 2), y + rnd.randint(2, h - 16)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    cx = x + w // 2
    d.polygon([(cx - 9, y + 26), (cx + 9, y + 26), (cx + 9, y + 60),
               (cx - 9, y + 60)], fill=WHITE)
    d.polygon([(cx - 9, y + 26), (cx + 9, y + 26), (cx, y + 10)],
              fill=(185, 28, 28))
    d.polygon([(cx - 9, y + 46), (cx - 20, y + 64), (cx - 9, y + 60)],
              fill=(185, 28, 28))
    d.polygon([(cx + 9, y + 46), (cx + 20, y + 64), (cx + 9, y + 60)],
              fill=(185, 28, 28))
    d.ellipse([cx - 4, y + 34, cx + 4, y + 42], fill=(30, 78, 121))
    d.polygon([(cx - 7, y + 60), (cx + 7, y + 60), (cx, y + 80)],
              fill=(245, 158, 11))
    d.polygon([(cx - 4, y + 60), (cx + 4, y + 60), (cx, y + 74)],
              fill=(253, 224, 71))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(20, 20, 20))
    d.text((x + 6, y + h - 13), "JIUQUAN, CHINA", font=font("sans_b", 8),
           fill=WHITE)


def art_redsea(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 90, 138))
    d.polygon([(x, y), (x + 46, y), (x + 36, y + h), (x, y + h)],
              fill=(222, 196, 140))
    d.polygon([(x + w, y), (x + w, y + h), (x + w - 40, y + h),
               (x + w - 52, y)], fill=(222, 196, 140))
    for px, py, col in [(70, 26, (185, 28, 28)), (112, 56, WHITE),
                        (150, 74, WHITE)]:
        d.ellipse([x + px - 4, y + py - 4, x + px + 4, y + py + 4],
                  fill=col, outline=INK)
    d.text((x + 78, y + 16), "JEDDAH", font=font("sans_b", 8), fill=WHITE)
    d.text((x + 120, y + 46), "HODEIDAH", font=font("sans_b", 8), fill=WHITE)
    d.text((x + 158, y + 64), "ADEN", font=font("sans_b", 8), fill=WHITE)
    for i in range(3):
        d.line([x + 84 + i * 10, y + 40 + i * 5, x + 92 + i * 10,
                y + 44 + i * 5], fill=(185, 28, 28), width=2)
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(20, 20, 20))
    d.text((x + 6, y + h - 13), "RED SEA · THREAT TODAY",
           font=font("sans_b", 8), fill=WHITE)


def art_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    for gy in range(4):
        yy = y + 10 + gy * (h - 22) // 3
        d.line([x + 6, yy, x + w - 6, yy], fill=(230, 230, 230))
    pts = [(x + 10, y + 22), (x + 55, y + 28), (x + 100, y + 25),
           (x + 145, y + 48), (x + 190, y + 55), (x + w - 10, y + 76)]
    d.line(pts, fill=(185, 28, 28), width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(185, 28, 28))
    d.text((x + 8, y + 3), "-8.2% TAIPEI", font=font("sans_b", 9),
           fill=(185, 28, 28))
    d.text((x + 8, y + h - 26), "-4.7% SEOUL   -3.2% TOKYO",
           font=font("sans_b", 9), fill=INK)


def art_pact(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(186, 220, 235))
    aus = [(x + 96, y + 44), (x + 110, y + 58), (x + 128, y + 52),
           (x + 158, y + 56), (x + 176, y + 68), (x + 168, y + 82),
           (x + 140, y + 84), (x + 118, y + 78), (x + 100, y + 64)]
    d.polygon(aus, fill=(222, 196, 140), outline=(150, 120, 70))
    for dx, dy in [(30, 26), (44, 20), (58, 32)]:
        d.ellipse([x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3],
                  fill=(30, 125, 50))
    d.ellipse([x + w - 52, y + 6, x + w - 8, y + 50], fill=(185, 28, 28),
              outline=WHITE, width=2)
    d.text((x + w - 46, y + 20), "PACT", font=font("sans_b", 11), fill=WHITE)
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(20, 20, 20))
    d.text((x + 6, y + h - 13), "CANBERRA · PACIFIC",
           font=font("sans_b", 8), fill=WHITE)


ART = {"rocket": art_rocket, "redsea": art_redsea, "chart": art_chart,
       "pact": art_pact}


def small_art(d, x, y, w, h, kind, color):
    d.rectangle([x, y, x + w, y + h], fill=color)
    cx, cy = x + w // 2, y + h // 2
    if kind == "ship":
        d.polygon([(cx - 16, cy + 2), (cx + 16, cy + 2), (cx + 10, cy + 8),
                   (cx - 10, cy + 8)], fill=WHITE)
        d.line([cx, cy - 8, cx, cy + 2], fill=WHITE, width=2)
    elif kind == "skyline":
        for bx, bh in [(-18, 10), (-8, 16), (4, 12), (14, 18)]:
            d.rectangle([cx + bx, cy + 10 - bh, cx + bx + 8, cy + 10],
                        fill=WHITE)
    elif kind == "chess":
        for r in range(2):
            for c in range(4):
                if (r + c) % 2 == 0:
                    d.rectangle([x + c * (w // 4), y + r * (h // 2),
                                 x + (c + 1) * (w // 4),
                                 y + (r + 1) * (h // 2)], fill=WHITE)
    elif kind == "bars":
        for bx, bh in [(-16, 6), (-5, 11), (6, 16)]:
            d.rectangle([cx + bx, cy + 8 - bh, cx + bx + 7, cy + 8],
                        fill=WHITE)
    elif kind == "plane":
        d.polygon([(cx - 16, cy), (cx + 16, cy - 4), (cx + 10, cy + 2),
                   (cx - 6, cy + 6)], fill=WHITE)
    elif kind == "cross":
        d.rectangle([cx - 3, cy - 9, cx + 3, cy + 9], fill=WHITE)
        d.rectangle([cx - 9, cy - 3, cx + 9, cy + 3], fill=WHITE)
    elif kind == "dome":
        d.pieslice([cx - 12, cy - 10, cx + 12, cy + 8], 180, 360, fill=WHITE)
        d.rectangle([cx - 14, cy + 6, cx + 14, cy + 9], fill=WHITE)
    elif kind == "rise":
        d.line([(cx - 16, cy + 8), (cx - 4, cy - 2), (cx + 4, cy + 2),
                (cx + 16, cy - 8)], fill=WHITE, width=3)
        d.polygon([(cx + 16, cy - 8), (cx + 8, cy - 8), (cx + 16, cy)],
                  fill=WHITE)
    elif kind == "blocks":
        for bx, by in [(-16, 4), (-6, 0), (4, 5), (-11, -6), (8, -5)]:
            d.rectangle([cx + bx, cy + by, cx + bx + 9, cy + by + 5],
                        fill=WHITE)
    elif kind == "bat":
        d.line([(cx - 12, cy + 8), (cx + 12, cy - 8)], fill=WHITE, width=4)
        d.ellipse([cx + 10, cy - 12, cx + 18, cy - 4], fill=WHITE)


# ---------------------------------------------------------------- page
def draw_page():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 14

    # kicker bar (0-14) + counts strip (16-30)
    d.rectangle([0, 0, W, 14], fill=RED)
    d.text((M, 1), "THE WORLD IN ONE DAY", font=font("sans_b", 10),
           fill=WHITE)
    d.text((W - M, 1), "WEDNESDAY EDITION", font=font("sans_b", 10),
           fill=WHITE, anchor="ra")
    d.text((W // 2, 17), "45 STORIES  ·  6 REGIONS  ·  10 FIELDS  ·  "
           "ALL FROM THIS WEDNESDAY", font=font("sans_b", 11), fill=RED,
           anchor="ma")

    # masthead (30-88)
    d.text((W // 2, 32), "Wednesday 25 November 2026",
           font=font("serif_b", 42), fill=INK, anchor="ma")
    d.line([M, 90, W - M, 90], fill=INK, width=2)

    # the day in one sentence (unique mark #2) (92-112)
    d.text((W // 2, 94), "“" + SENTENCE + "”", font=font("serif_i", 15),
           fill=RED, anchor="ma")
    d.line([M, 114, W - M, 114], fill=RED, width=1)

    # UTC strip (118-142)
    y = 118
    d.rectangle([M, y, M + 148, y + 24], fill=RED)
    d.text((M + 8, y + 6), "THE DAY IN UTC", font=font("sans_b", 10),
           fill=WHITE)
    x = M + 158
    for t, label in UTC_ITEMS:
        d.text((x, y + 2), t, font=font("sans_b", 10), fill=RED)
        d.text((x, y + 13), label, font=font("sans", 9), fill=INK)
        x += 172
    d.line([M, y + 26, W - M, y + 26], fill=INK, width=1)

    # big numbers strip (146-182)
    y = 146
    d.rectangle([M, y, W - M, y + 36], fill=DARK)
    cw = (W - 2 * M) // 5
    for i, (num, label) in enumerate(BIG):
        cx = M + i * cw + cw // 2
        d.text((cx, y + 3), num, font=font("sans_b", 18), fill=GOLD,
               anchor="ma")
        d.text((cx, y + 24), label, font=font("sans", 9), fill=WHITE,
               anchor="ma")

    # region strip (186-201), small segments get a minimum width
    y = 186
    total = sum(v for _, v, _ in REGIONS)
    widths = [max(58, int((W - 2 * M) * v / total)) for _, v, _ in REGIONS]
    overflow = sum(widths) - (W - 2 * M)
    widths[0] -= overflow // 2
    widths[1] -= overflow - overflow // 2
    x = M
    for (name, v, color), w in zip(REGIONS, widths):
        d.rectangle([x, y, x + w - 1, y + 15], fill=color)
        d.text((x + w // 2, y + 3), f"{name} {v}", font=font("sans_b", 9),
               fill=WHITE, anchor="ma")
        x += w

    # 4 leads (205-398): art 96 tall, then tag, headline, body, source
    y0 = 205
    col_w = (W - 2 * M - 3 * 8) // 4
    for i, lead in enumerate(LEADS):
        x = M + i * (col_w + 8)
        ART[lead["art"]](d, x, y0, col_w, 96)
        yy = y0 + 100
        d.rectangle([x, yy, x + 18, yy + 13], fill=lead["color"])
        d.text((x + 5, yy + 1), str(lead["n"]), font=font("sans_b", 9),
               fill=WHITE)
        d.text((x + 22, yy + 1), lead["tag"], font=font("sans_b", 9),
               fill=lead["color"])
        yy += 16
        yy = text_block(d, x, yy, lead["head"], font("serif_b", 13), INK,
                        col_w, lh=15)
        yy += 2
        yy = text_block(d, x, yy, lead["body"], font("sans", 10), INK,
                        col_w, lh=12)
        d.text((x, yy + 1), lead["src"], font=font("sans_i", 8), fill=GREY)

    # 10 smalls, 2 rows of 5 (402-566): 80px rows, no overflow
    y0 = 402
    col_w = (W - 2 * M - 4 * 6) // 5
    for row in range(2):
        for col in range(5):
            s = SMALLS[row * 5 + col]
            x = M + col * (col_w + 6)
            y = y0 + row * 82
            small_art(d, x, y, col_w, 18, s["art"], s["color"])
            yy = y + 21
            d.text((x, yy), f"{s['n']}  {s['tag']}", font=font("sans_b", 8),
                   fill=s["color"])
            yy += 11
            yy = text_block(d, x, yy, s["head"], font("sans_b", 10), INK,
                            col_w, lh=11)
            d.text((x, yy), s["body"], font=font("sans", 9), fill=INK)
            yy += 11
            bw = badge(d, x, yy, s["badge"], BADGE_COLORS[s["badge"]])
            d.text((x + bw + 5, yy + 1), s["src"], font=font("sans_i", 8),
                   fill=GREY)

    # VOICES OF THE DAY (unique mark #1) (570-664)
    y = 570
    d.rectangle([M, y, W - M, y + 18], fill=RED)
    d.text((M + 8, y + 3), "VOICES OF THE DAY", font=font("sans_b", 11),
           fill=WHITE)
    d.text((W - M - 8, y + 3), "IN THEIR OWN WORDS", font=font("sans_b", 9),
           fill=WHITE, anchor="ra")
    y = 592
    col_w = (W - 2 * M - 2 * 16) // 3
    for i, (quote, who, src) in enumerate(VOICES):
        x = M + i * (col_w + 16)
        yy = text_block(d, x, y, quote, font("serif_i", 11), INK, col_w,
                        lh=13)
        yy += 2
        yy = text_block(d, x, yy, who, font("sans_b", 8), INK, col_w, lh=10)
        d.text((x, yy), src, font=font("sans_i", 8), fill=GREY)

    # map + briefs (668-846): header, map 316x160, briefs one line each
    y0 = 668
    d.text((M, y0), "WHERE IT HAPPENED", font=font("sans_b", 11), fill=RED)
    d.text((W - M, y0), "ALSO ON WEDNESDAY 25 NOVEMBER — STORIES 15 TO 45",
           font=font("sans_b", 10), fill=INK, anchor="ra")
    my = y0 + 16
    mx, mw, mh = M, 316, 160
    d.rectangle([mx, my, mx + mw, my + mh], fill=SEA, outline=INK)
    def proj(lon, lat):
        return (mx + (lon + 180) / 360 * mw,
                my + (90 - lat) / 180 * mh)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(150, 120, 70))
    for n, lon, lat in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED, outline=WHITE)
        d.text((px, py - 5), str(n), font=font("sans_b", 7), fill=WHITE,
               anchor="ma")
    d.text((mx + 4, my + mh - 11), "Nos. 1–14 pictured; 15–45 at right",
           font=font("sans_i", 8), fill=INK)
    bx = M + mw + 12
    bw = W - M - bx
    half = (len(BRIEFS) + 1) // 2
    for ci, chunk in enumerate([BRIEFS[:half], BRIEFS[half:]]):
        x = bx + ci * (bw // 2 + 6)
        yy = my
        for n, txt in chunk:
            d.text((x, yy), f"{n}. {txt}", font=font("sans", 9), fill=INK)
            yy += 10

    # chart panel + HOW TO READ (850-912)
    y0 = 850
    d.text((M, y0), "THE DAY IN ONE CHART — WED 25 NOV MARKETS (WSJ closes)",
           font=font("sans_b", 10), fill=RED)
    d.text((M + 636, y0), "HOW TO READ THE TAGS", font=font("sans_b", 10),
           fill=RED)
    yy = y0 + 15
    for name, v in CHART_BARS:
        d.text((M, yy), name, font=font("sans", 9), fill=INK)
        bar_x = M + 74
        bar_w = int(abs(v) / 9.0 * 260)
        col = (185, 28, 28) if v < 0 else (30, 125, 50)
        d.rectangle([bar_x, yy, bar_x + bar_w, yy + 9], fill=col)
        d.text((bar_x + bar_w + 6, yy - 1), f"{v:+.1f}%",
               font=font("sans_b", 9), fill=INK)
        yy += 11
    hx = M + 636
    hy = y0 + 15
    legend = [
        ("CONFIRMED", "2+ outlets"), ("REPORTED", "one outlet"),
        ("CLAIM", "one side's word"), ("FORECAST", "due / expected"),
        ("OFFICIAL", "official source"),
    ]
    for li, (label, desc) in enumerate(legend):
        lx = hx + (li % 2) * 185
        ly = hy + (li // 2) * 14
        bw = badge(d, lx, ly, label, BADGE_COLORS[label], size=8)
        d.text((lx + bw + 5, ly + 1), desc, font=font("sans", 9), fill=INK)
    d.text((hx, hy + 44), "Every story: Wed 25 Nov 2026. Older: DATE CHECK.",
           font=font("sans", 9), fill=INK)

    # WHAT TO WATCH TOMORROW (916-936)
    y = 916
    d.rectangle([M, y, W - M, y + 20], fill=BLUE)
    d.text((M + 8, y + 4), "WHAT TO WATCH TOMORROW — THU 26 NOV:",
           font=font("sans_b", 10), fill=WHITE)
    d.text((M + 268, y + 4), "Thanksgiving Day, US markets shut; Chess "
           "Game 3 in Geneva; Asia reacts to PCE/GDP; Houthi–Saudi "
           "standoff watch.", font=font("sans", 10), fill=WHITE)

    # DATE CHECK (940-1004)
    y = 940
    d.rectangle([M, y, W - M, y + 17], fill=RED)
    d.text((M + 8, y + 3), "DATE CHECK", font=font("sans_b", 11),
           fill=WHITE)
    d.text((M + 108, y + 3), "Left out on purpose — first reported BEFORE "
           "Wednesday:", font=font("sans_i", 9), fill=WHITE)
    yy = y + 21
    for day, items in DATE_CHECK:
        line = f"{day}: {items}"
        lines = wrap(d, line, font("sans", 9), W - 2 * M)
        for ln in lines:
            d.text((M, yy), ln, font=font("sans", 9), fill=INK)
            yy += 10

    # sources + footer (1008-1022)
    d.line([M, 1007, W - M, 1007], fill=INK, width=1)
    d.text((M, 1010), "Sources: Reuters, AP, WSJ, Xinhua, FIDE, Chess.com, "
           "AAA, WHO, AFP, Bloomberg, AAP, Hindu BusinessLine, CNN, NYT · "
           "Original drawings", font=font("sans", 8), fill=GREY)
    return img


def main():
    img = draw_page()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, optimize=True)
    print(f"wrote {out} {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
