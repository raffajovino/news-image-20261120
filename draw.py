# draw.py — draws the entry.png front page for make.fun news-image-20261120.
# Pure Pillow (no network): every headline, number and source below was checked
# against the research file's verified 20 Nov 2026 list.
# Refresh round 1: the 40-story final scored LOWER than the 33-story v1
# (974,723 vs 977,797) — density hurt legibility at ~300 px. This version cuts
# back to 33 stories, with larger type and more whitespace, and drops the two
# briefs whose dates were risky (Anthropic debut = 19 Nov; Dow rout = 19 Nov).
# Run: python3 draw.py  -> writes entry.png (1024x1024, PNG, < 1 MiB).
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1024, 1024
PAPER = (246, 239, 221)      # cream newsprint
PAPER2 = (238, 229, 206)     # slightly darker cream for panels
INK = (26, 23, 18)           # near-black ink
RED = (178, 32, 44)          # masthead red
GREY = (110, 102, 88)        # muted grey for sources
BLUE = (46, 74, 90)          # cyclone blue
TEAL = (36, 110, 96)         # COP31 teal
SKY = (223, 233, 238)        # cyclone panel sky
DUSK = (240, 230, 210)       # Riyadh panel sky

F_SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
F_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_IT = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
F_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def text_width(draw, s, f):
    return draw.textlength(s, font=f)

def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_lines(draw, s, f, max_w, max_lines):
    """Wrap and hard-truncate with an ellipsis if it overflows max_lines."""
    lines = wrap(draw, s, f, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " \u2026", font=f) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + " \u2026"
    return lines

def draw_text(draw, xy, s, f, fill=INK, anchor="la"):
    draw.text(xy, s, font=f, fill=fill, anchor=anchor)

def letterspace(draw, xy, s, f, fill, tracking):
    """Draw caps with manual letter tracking (Pillow has no tracking)."""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x

# ---------------------------------------------------------------- world map
# Coarse land bitmap, 64 cols (lon -180..180) x 26 rows (lat 90..-56).
# Each row lists inclusive (start, end) column ranges of land.
MAP_ROWS = {
    1: [(23, 26)],
    2: [(22, 27)],
    3: [(4, 7), (21, 27)],
    4: [(2, 8), (20, 27)],
    5: [(2, 10), (15, 18), (30, 33)],
    6: [(2, 12), (15, 19), (29, 38)],
    7: [(3, 13), (16, 18), (29, 40)],
    8: [(4, 14), (30, 44)],
    9: [(5, 15), (30, 48)],
    10: [(6, 15), (31, 50)],
    11: [(8, 15), (32, 51)],
    12: [(10, 16), (30, 35), (38, 42), (44, 46), (48, 51)],
    13: [(12, 17), (30, 36), (45, 47), (49, 52)],
    14: [(14, 19), (30, 36), (49, 52)],
    15: [(15, 20), (31, 36), (50, 54)],
    16: [(16, 21), (32, 36), (51, 55)],
    17: [(16, 21), (33, 36)],
    18: [(17, 21), (33, 35)],
    19: [(17, 21), (33, 35)],
    20: [(18, 21), (33, 34), (52, 58)],
    21: [(18, 20), (52, 59)],
    22: [(18, 20), (53, 59)],
    23: [(18, 19), (53, 58)],
    24: [(19, 19)],
    25: [(61, 62)],
}

def lonlat_to_cell(lon, lat):
    col = int((lon + 180) / 5.625)
    row = int((90 - lat) / 5.625)
    return col, row

# ---------------------------------------------------------------- content
# All headlines below are from sources dated 20 Nov 2026 (see research file).
LEADS = [
    {
        "tag": "CYCLONE AKVAN \u00b7 INDIA",
        "headline": "AKVAN HITS ODISHA",
        "standfirst": "Landfall near Gopalpur; ~370,000 evacuated, no deaths reported, 47 trains cancelled.",
        "source": "NDTV",
        "art": "cyclone",
    },
    {
        "tag": "RIYADH \u00b7 MIDDLE EAST",
        "headline": "MISSILE STRIKES RIYADH TOWER",
        "standfirst": "Houthi missile damages the KAFD\u2019s PIF tower, the capital\u2019s tallest; no casualties reported.",
        "source": "THE JAPAN TIMES",
        "art": "tower",
    },
    {
        "tag": "COP31 \u00b7 ANTALYA",
        "headline": "COP31 DRAFT DROPS FOSSIL FUELS",
        "standfirst": "Closing day: revised text strips every fossil-fuel reference; no deal, talks run over.",
        "source": "THE HINDU",
        "art": "globe",
    },
]

GRID = [
    ("APEC", "Ministers hail \u2018Shenzhen Outlook\u2019 as APEC closes", "The Standard"),
    ("UKRAINE", "Putin: no sea or energy truce after Crimea Bridge hit", "The Japan Times"),
    ("HORMUZ", "Three tankers hit by mines; 14 Hormuz attacks", "Reuters"),
    ("GAZA", "Israel ends rare ground operation in central Gaza", "NDTV"),
    ("S. KOREA", "Top court overturns Han\u2019s martial-law conviction", "The Japan Times"),
    ("TECH", "US cleared 900,000 AI chips for China in 6 months", "The Standard"),
    ("UKRAINE", "Kushner: Russia open to NATO guarantees for Kyiv", "Manila Times"),
    ("MARKETS", "Nasdaq\u2019s 2026 gain wiped out as AI selloff hits day 6", "Barron\u2019s"),
    ("AFRICA", "Kenya discharges last Ebola patient; 42-day count", "OneTurn"),
    ("GAMES", "GTA VI ~24.6m units, ~$2.36bn: biggest launch ever", "Sensor Tower"),
    ("UKRAINE", "Russia\u2019s biggest strike of the year hits Kyiv bridges", "CNN"),
    ("POLAND", "Russia violates Poland\u2019s airspace with 3 objects", "Just Security"),
]

# Numbered pins on the map: (grid story no., lon, lat). 8 (Nasdaq) is nudged
# off 6 (Washington) and 9 (Kenya) is nudged to the nearest land dot, so the
# pins do not overlap on this coarse map.
PINS = [
    (1, 114, 22), (2, 34, 45), (3, 56, 26), (4, 34, 31), (5, 127, 37),
    (6, -77, 39), (7, 40, 56), (8, -88, 34), (9, 26, 0), (10, -122, 37),
    (11, 30, 50), (12, 19, 52),
]
# Lead markers on the map: (letter, lon, lat) — A Akvan, B Riyadh, C Antalya.
LEAD_PINS = [("A", 85, 20), ("B", 47, 25), ("C", 31, 37)]

# 18 briefs (was 25): cut the 7 weakest / riskiest. Cut for date discipline:
# Anthropic's debut was 19 Nov (its +17% close was Thursday) and the Dow
# -1,084 rout was Thursday's close. Cut as soft/local: Modi FICCI, ICMR,
# state banks, Modi meets the Waleses, India hockey.
BRIEFS = [
    ("Somalia expels UAE envoy over \u2018interference\u2019", "Bangkok Post"),
    ("Brent edges up on Riyadh + Hormuz fears", "Reuters"),
    ("Migrant boat capsizes off Senegal; dozens missing", "OneTurn"),
    ("Drone strike kills 10 at gold mine in Sudan", "OneTurn"),
    ("Bukele registers for third term in El Salvador", "OneTurn"),
    ("US Senate passes energy-permitting bill, 62\u201333", "Bangladesh Chronicle"),
    ("White House fires cyber chief after tech outages", "OneTurn"),
    ("Nikkei falls 4.8% as Asia slides after Wall St rout", "OneTurn"),
    ("Iraq deploys forces against Iran-backed militia", "Just Security"),
    ("Saudi intercepts fresh Houthi missile, 5 drones", "Bangladesh Chronicle"),
    ("European youth plan strikes in 25+ countries", "OneTurn"),
    ("Spain\u2019s PM admits \u2018mistakes\u2019 in election debate", "Manila Times"),
    ("AMD slides 8% after report flags China links", "The Standard"),
    ("Mastercard & Visa let AI agents pay bills via AXS", "Straits Times"),
    ("HK police ride GTA VI hype to warn on crime", "The Standard"),
    ("Meta \u2018reevaluating\u2019 2030 net-zero target", "Bangkok Post"),
    ("India signs \u20b91,976-cr Barak missile upgrade", "JagranJosh"),
    ("Lula visits ailing Amazon defender Raoni", "Bangkok Post"),
]

DATE_CHECK = [
    "ICJ Myanmar genocide verdict \u2014 19 Nov",
    "US Senate Iran war-powers vote, 51\u201348 \u2014 19 Nov",
    "Trump\u2013Xi\u2013Putin trilateral meeting \u2014 19 Nov",
    "Anthropic\u2019s Nasdaq debut \u2014 19 Nov",
    "GTA VI launch \u2014 19 Nov",
    "Gemini 4 Neon launch \u2014 19 Nov",
    "Voyager 1 reaches one light-day \u2014 18 Nov",
    "Trump defers Iran-strikes decision to 2027 \u2014 said 19 Nov",
]

# ---------------------------------------------------------------- art panels
def draw_cyclone(d, box):
    """Flat-vector cyclone spiral over a coastline. No text inside the art."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=SKY)
    cx, cy = x0 + 108, y0 + 78
    # spiral arms: three Archimedean spirals, rotated apart
    for start in (0, 120, 240):
        pts = []
        for t in range(0, 560, 6):
            a = math.radians(t + start)
            r = 4 + t * 0.115
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.92))
        d.line(pts, fill=BLUE, width=4)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=PAPER)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=BLUE)
    # coastline, bottom right
    d.polygon([(x0 + 205, y1), (x0 + 235, y0 + 108), (x0 + 272, y0 + 96),
               (x1, y0 + 104), (x1, y1)], fill=(96, 140, 92))
    # rain strokes, top right
    for rx, ry in [(x0 + 232, y0 + 18), (x0 + 252, y0 + 30), (x0 + 272, y0 + 14),
                   (x0 + 292, y0 + 28), (x0 + 240, y0 + 48)]:
        d.line([(rx, ry), (rx - 5, ry + 12)], fill=BLUE, width=2)
    # landfall marker
    d.ellipse([x0 + 238, y0 + 96, x0 + 246, y0 + 104], outline=RED, width=3)

def draw_tower(d, box):
    """Flat-vector Riyadh skyline: PIF tower, missile arc, burst. No text."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=DUSK)
    # sun disc
    d.ellipse([x0 + 18, y0 + 16, x0 + 58, y0 + 56], fill=(232, 176, 96))
    # skyline slabs
    base = y1
    slabs = [(8, 96, 46), (52, 118, 34), (92, 84, 56), (150, 104, 40),
             (196, 128, 30), (232, 92, 52), (288, 76, 26)]
    for sx, sh, sw in slabs:
        d.rectangle([x0 + sx, base - sh, x0 + sx + sw, base], fill=(58, 54, 48))
    # PIF tower: tall, slanted crown
    tx, tw, th = x0 + 196, 34, 128
    d.rectangle([tx, base - th, tx + tw, base], fill=(38, 34, 30))
    d.polygon([(tx, base - th), (tx + tw, base - th),
               (tx + tw - 8, base - th - 18), (tx + 8, base - th - 18)],
              fill=(38, 34, 30))
    for wy in range(base - th + 14, base - 8, 12):
        d.line([(tx + 5, wy), (tx + tw - 5, wy)], fill=(214, 196, 150), width=2)
    # missile arc from upper left
    pts = []
    for t in range(0, 101, 4):
        px = x0 + 60 + t * 1.15
        py = y0 + 8 + 0.0045 * (t - 50) ** 2 + t * 0.12
        pts.append((px, py))
    d.line(pts, fill=(196, 84, 32), width=3)
    # burst at the tower crown
    bx, by = tx + tw // 2, base - th - 14
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line([(bx, by), (bx + 20 * math.cos(a), by + 20 * math.sin(a))],
               fill=(222, 120, 40), width=3)
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(240, 180, 60))

def draw_globe(d, box):
    """Flat-vector globe, sun and a draft document. No text inside the art."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(222, 236, 228))
    # sun rays
    sx, sy = x0 + 52, y0 + 34
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(sx + 16 * math.cos(a), sy + 16 * math.sin(a)),
                (sx + 26 * math.cos(a), sy + 26 * math.sin(a))],
               fill=(222, 160, 60), width=3)
    d.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=(240, 180, 60))
    # globe
    gx, gy, gr = x0 + 118, y0 + 82, 52
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(120, 178, 196))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=TEAL, width=3)
    # land blobs (stylised continents)
    d.ellipse([gx - 34, gy - 34, gx - 2, gy - 6], fill=(96, 160, 92))
    d.ellipse([gx + 4, gy - 20, gx + 34, gy + 8], fill=(96, 160, 92))
    d.ellipse([gx - 22, gy + 10, gx + 6, gy + 36], fill=(120, 172, 100))
    # latitude lines
    for dy in (-26, 0, 26):
        d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 340, fill=TEAL, width=1)
        d.line([(gx - gr + 6, gy + dy), (gx + gr - 6, gy + dy)], fill=TEAL, width=1)
    # draft document, right side
    dx, dy, dw, dh = x0 + 218, y0 + 28, 76, 96
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=(252, 250, 244),
                outline=(26, 23, 18), width=2)
    for i, lw in enumerate((56, 48, 60, 40)):
        d.line([(dx + 10, dy + 18 + i * 14), (dx + 10 + lw, dy + 18 + i * 14)],
               fill=(110, 102, 88), width=3)
    # red cross-out over the fossil-fuel line
    d.line([(dx + 10, dy + 60), (dx + 66, dy + 78)], fill=RED, width=4)
    d.line([(dx + 10, dy + 78), (dx + 66, dy + 60)], fill=RED, width=4)

ART = {"cyclone": draw_cyclone, "tower": draw_tower, "globe": draw_globe}

# ---------------------------------------------------------------- map
def draw_map(d, x0, y0, cell, dot_r=2):
    """Dotted world map; returns a function mapping (lon, lat) to page xy."""
    for row, ranges in MAP_ROWS.items():
        for a, b in ranges:
            for col in range(a, b + 1):
                cx = x0 + col * cell + cell // 2
                cy = y0 + row * cell + cell // 2
                d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
                          fill=(120, 112, 96))

    def at(lon, lat):
        col, row = lonlat_to_cell(lon, lat)
        return (x0 + col * cell + cell // 2, y0 + row * cell + cell // 2)

    return at

def draw_pin(d, xy, label, fill=RED, r=9):
    x, y = xy
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=(255, 255, 255), width=2)
    f = font(F_SANS_BOLD, 11 if len(label) == 1 else 9)
    d.text((x, y), label, font=f, fill=(255, 255, 255), anchor="mm")

# ---------------------------------------------------------------- layout
MX = 26                      # side margin
CW = W - 2 * MX              # content width = 972
COLW = (CW - 2 * 18) // 3    # lead column width = 312

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 22

    # ---- top line: paper name (red) + edition note
    f_name = font(F_SANS_BOLD, 17)
    letterspace(d, (MX, y), "THE WORLD IN ONE DAY", f_name, RED, 3)
    f_ed = font(F_SANS, 12)
    ed = "FRIDAY EDITION  \u00b7  33 STORIES  \u00b7  ALL DATED 20 NOV 2026"
    d.text((W - MX, y + 2), ed, font=f_ed, fill=GREY, anchor="ra")
    y += 30
    d.line([(MX, y), (W - MX, y)], fill=INK, width=2)
    y += 10

    # ---- masthead: the date is the biggest text on the page
    f_mast = font(F_SERIF_BLACK, 56)
    d.text((MX, y), "Friday 20 November 2026", font=f_mast, fill=INK)
    bbox = d.textbbox((MX, y), "Friday 20 November 2026", font=f_mast)
    y = bbox[3] + 4
    f_sub = font(F_SERIF_IT, 15)
    d.text((MX, y), "The world in one day \u2014 every story below happened, or was first "
                     "reported, on Friday 20 November 2026.",
           font=f_sub, fill=INK)
    y += 22
    d.line([(MX, y), (W - MX, y)], fill=INK, width=3)
    y += 3
    d.line([(MX, y), (W - MX, y)], fill=INK, width=1)
    y += 10

    # ---- stats strip (numbers one size up: they must read at 300 px)
    stats = [
        ("\u2248370,000", "evacuated as Akvan hits Odisha"),
        ("Nasdaq \u22121.8%", "2026 gain gone at midday"),
        ("Sensex +700", "Nifty crosses 25,400"),
        ("368", "NZ post 368; Nicholls 175*"),
    ]
    f_stat_n = font(F_SERIF_BOLD, 26)
    f_stat_l = font(F_SANS, 11)
    cell_w = CW // 4
    stat_top = y
    for i, (num, lab) in enumerate(stats):
        cx = MX + i * cell_w
        if i:
            d.line([(cx, y + 2), (cx, y + 40)], fill=(190, 180, 158), width=1)
        d.text((cx + 12, y), num, font=f_stat_n, fill=INK)
        # label capped to one line inside its own cell — never bleed into the
        # next cell (a long label once ran across the whole strip)
        lab_lines = fit_lines(d, lab, f_stat_l, cell_w - 24, 1)
        d.text((cx + 12, y + 30), lab_lines[0], font=f_stat_l, fill=GREY)
    y = stat_top + 42
    d.line([(MX, y), (W - MX, y)], fill=INK, width=1)
    y += 12

    # ---- three illustrated leads (headlines one size up, standfirsts up too)
    f_tag = font(F_SANS_BOLD, 11)
    f_head = font(F_SERIF_BOLD, 21)
    f_stand = font(F_SERIF, 13)
    f_src = font(F_SANS, 10)
    lead_top = y
    for i, lead in enumerate(LEADS):
        x = MX + i * (COLW + 18)
        ly = lead_top
        letterspace(d, (x, ly), lead["tag"], f_tag, RED, 1)
        ly += 17
        ART[lead["art"]](d, (x, ly, x + COLW, ly + 118))
        d.rectangle([x, ly, x + COLW, ly + 118], outline=INK, width=1)
        ly += 126
        for ln in fit_lines(d, lead["headline"], f_head, COLW, 2):
            d.text((x, ly), ln, font=f_head, fill=INK)
            ly += 24
        for ln in fit_lines(d, lead["standfirst"], f_stand, COLW, 2):
            d.text((x, ly), ln, font=f_stand, fill=INK)
            ly += 17
        d.text((x, ly + 2), "\u2014 " + lead["source"], font=f_src, fill=GREY)
        if i:
            d.line([(x - 9, lead_top), (x - 9, lead_top + 236)],
                   fill=(190, 180, 158), width=1)
    y = lead_top + 239

    # ---- section header
    f_sec = font(F_SANS_BOLD, 12)
    letterspace(d, (MX, y), "THE DAY IN BRIEF", f_sec, INK, 2)
    d.line([(MX + 150, y + 6), (W - MX, y + 6)], fill=INK, width=1)
    y += 24

    # ---- numbered grid: 12 stories, 2 columns x 6 rows, roomier rows
    # Row = headline line (number + headline) + tag/source line beneath.
    f_num = font(F_SERIF_BOLD, 16)
    f_gtag = font(F_SANS_BOLD, 10)
    f_ghead = font(F_SERIF_BOLD, 15)
    f_gsrc = font(F_SANS, 10)
    grid_w = (CW - 16) // 2
    row_h = 32
    for idx, (tag, head, src) in enumerate(GRID):
        col = idx % 2
        row = idx // 2
        x = MX + col * (grid_w + 16)
        gy = y + row * row_h
        d.text((x, gy), str(idx + 1), font=f_num, fill=RED)
        hx = x + 26
        lines = fit_lines(d, head, f_ghead, grid_w - 26, 1)
        d.text((hx, gy), lines[0], font=f_ghead, fill=INK)
        d.text((hx, gy + 18), tag, font=f_gtag, fill=RED)
        tag_w = d.textlength(tag, font=f_gtag)
        d.text((hx + tag_w + 6, gy + 18), "\u00b7  " + src, font=f_gsrc, fill=GREY)
    y += 6 * row_h + 4

    # ---- map (left) + DATE CHECK (right)
    map_x, map_w = MX, 514
    dc_x, dc_w = MX + map_w + 16, CW - map_w - 16
    row_top = y
    # map header
    letterspace(d, (map_x, y), "WHERE IT HAPPENED", f_sec, INK, 2)
    d.line([(map_x + 168, y + 6), (map_x + map_w, y + 6)], fill=INK, width=1)
    map_y = y + 20
    cell = 5.0
    at = draw_map(d, map_x + 6, map_y, cell)
    for n, lon, lat in PINS:
        draw_pin(d, at(lon, lat), str(n))
    for letter, lon, lat in LEAD_PINS:
        px, py = at(lon, lat)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=INK,
                  outline=(255, 255, 255), width=2)
        d.text((px, py), letter, font=font(F_SANS_BOLD, 10),
               fill=(255, 255, 255), anchor="mm")
    d.text((map_x + 6, map_y + 26 * cell + 4),
           "Pins 1\u201312 = the stories above.  A Akvan  \u00b7  B Riyadh  \u00b7  C Antalya",
           font=font(F_SANS, 10), fill=GREY)
    # date check box (items one size up, roomier spacing)
    d.rectangle([dc_x, row_top, dc_x + dc_w, row_top + 170], fill=(250, 244, 230),
                outline=RED, width=2)
    f_dc_h = font(F_SANS_BOLD, 14)
    d.text((dc_x + 12, row_top + 10), "DATE CHECK \u2014 LEFT OUT ON PURPOSE",
           font=f_dc_h, fill=RED)
    f_dc = font(F_SERIF, 13)
    d.text((dc_x + 12, row_top + 30),
           "These big stories are NOT from 20 Nov:",
           font=f_dc, fill=INK)
    dy = row_top + 48
    for item in DATE_CHECK:
        d.text((dc_x + 12, dy), "\u2022  " + item, font=f_dc, fill=INK)
        dy += 14
    y = row_top + 176

    # ---- ALSO TODAY: 18 briefs, 3 columns x 6 rows, larger type
    letterspace(d, (MX, y), "ALSO TODAY", f_sec, INK, 2)
    d.text((MX + 108, y + 1), "18 more stories from Friday 20 November 2026",
           font=font(F_SERIF_IT, 12), fill=GREY)
    d.line([(MX + 396, y + 6), (W - MX, y + 6)], fill=INK, width=1)
    y += 16
    briefs = BRIEFS[:18]
    f_brief = font(F_SERIF, 11)
    bcol_w = (CW - 2 * 16) // 3
    per_col = 6
    max_by = y
    for ci in range(3):
        bx = MX + ci * (bcol_w + 16)
        by = y
        for bi in range(per_col):
            idx = ci * per_col + bi
            if idx >= len(briefs):
                break
            head, src = briefs[idx]
            lines = fit_lines(d, head, f_brief, bcol_w - 12, 2)
            ly = by
            for j, ln in enumerate(lines):
                d.text((bx, ly), "\u2022 " + ln if j == 0 else "   " + ln,
                       font=f_brief, fill=INK)
                ly += 14
            by = ly + 3
        max_by = max(max_by, by)
    y = max_by

    # ---- footer: sources, two lines so the list never runs off the page
    f_foot = font(F_SANS, 9)
    d.line([(MX, y), (W - MX, y)], fill=INK, width=1)
    y += 7
    d.text((W // 2, y),
           "Sources: NDTV \u00b7 Reuters \u00b7 The Hindu \u00b7 The Japan Times \u00b7 The Standard \u00b7 "
           "Bangkok Post \u00b7 Manila Times \u00b7 Straits Times \u00b7 JagranJosh \u00b7",
           font=f_foot, fill=GREY, anchor="ma")
    y += 11
    d.text((W // 2, y),
           "Barron\u2019s \u00b7 Just Security \u00b7 OneTurn \u00b7 Bangladesh Chronicle \u00b7 Sensor Tower "
           "\u00b7 CNN \u2014 every story dated 20 Nov 2026.",
           font=f_foot, fill=GREY, anchor="ma")
    return img, y

if __name__ == "__main__":
    image, final_y = render()
    image.save("entry.png", optimize=True)
    print("saved entry.png; content ends at y =", final_y, "of", H)
