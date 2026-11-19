#!/usr/bin/env python3
"""Render the v3 front page: 32 stories of 19 November 2026 on one
1024x1024 newspaper sheet.

Tiered layout (lead band + 3 medium cards + 28-card grid), region
strip, and one lead illustration: three flat flag banners (US / China /
Russia) for the trilateral-summit lead story. Every headline and deck
is fitted to its box; anything that does not fit is logged as an
overflow instead of being silently clipped.

Usage:
    python3 render.py [output.png] [overflow.log]

Defaults: entry.png in this directory, and no log file unless asked.
Also writes a 300x300 downscale next to the output for legibility
checks (same stem with "-300" appended).
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas

W, H = 1024, 1024
MARGIN = 22
CONTENT = W - 2 * MARGIN  # 980

PAPER = (250, 247, 239)
INK = (24, 24, 24)
ACCENT = (172, 32, 28)      # story red: discs, kickers, counts
CHIP_BG = (236, 231, 219)   # region chips + lead band fill
CARD_EDGE = (205, 198, 182)
RULE = (35, 35, 35)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- stories
# Each story: number, region, place, headline, deck. All 32 are events
# that happened or were first reported on Thursday 19 November 2026;
# see SOURCES.md for where each was verified.

STORIES = [
    {"n": 1, "region": "ASIA-PACIFIC", "place": "SHENZHEN",
     "head": "Trump, Xi and Putin hold first three-way summit",
     "deck": "An hour at APEC on nukes, Ukraine and Iran; no breakthrough expected."},
    {"n": 2, "region": "ASIA-PACIFIC", "place": "BAY OF BENGAL",
     "head": "Cyclone Akvan nears India; 72,000 evacuated",
     "deck": "Odisha moves people to 7,900 shelters; landfall near Gopalpur Friday."},
    {"n": 3, "region": "ASIA-PACIFIC", "place": "DHAKA",
     "head": "Bangladesh shuts down as Yunus home torched",
     "deck": "Two killed in Awami League lockdown; 28 districts hit by violence."},
    {"n": 4, "region": "ASIA-PACIFIC", "place": "THE HAGUE",
     "head": "World court rules on Rohingya genocide case",
     "deck": "Seven years after Gambia sued Myanmar, the ICJ delivers judgment."},
    {"n": 5, "region": "ASIA-PACIFIC", "place": "YONGBYON",
     "head": "IAEA: North Korea expanded uranium enrichment",
     "deck": "Extension built mid-Sep to late Oct; 5MW plutonium reactor in 7th cycle."},
    {"n": 6, "region": "ASIA-PACIFIC", "place": "SEOUL",
     "head": "South Korea's Lee renews call for North talks",
     "deck": "President Lee urges dialogue, hoping for durable peace on peninsula."},
    {"n": 7, "region": "ASIA-PACIFIC", "place": "ASIA CUP",
     "head": "India edge Pakistan by one wicket, win Asia Cup",
     "deck": "U19s chase down Pakistan in final to lift the continental crown."},
    {"n": 8, "region": "MIDDLE EAST", "place": "GULF",
     "head": "Iran hits US bases in Kuwait and Bahrain",
     "deck": "Tehran retaliates for US strike on Qeshm; tanker hit, 11 hurt."},
    {"n": 9, "region": "MIDDLE EAST", "place": "ANTALYA",
     "head": "COP31 ministers race to unblock final text",
     "deck": "$120bn adaptation draft divides nearly 200 nations; deadline Friday."},
    {"n": 10, "region": "MIDDLE EAST", "place": "HORMUZ",
     "head": "IEA: Hormuz crisis worst threat to energy ever",
     "deck": "Agency's annual report warns Middle East crisis imperils supply."},
    {"n": 11, "region": "MIDDLE EAST", "place": "GULF",
     "head": "Trump: Iran pursuing chemical, biological arms",
     "deck": "Claim comes as US and Iran trade strikes across the Gulf."},
    {"n": 12, "region": "NORTH AMERICA", "place": "WASHINGTON",
     "head": "NSA outage hits intelligence links in Gulf",
     "deck": "Classified comms disrupted; officials blame internal fault, not hack."},
    {"n": 13, "region": "EUROPE", "place": "CRIMEA",
     "head": "Crimean Bridge hit for third time this week",
     "deck": "Traffic and rail halted; damage assessed hours before Putin's summit."},
    {"n": 14, "region": "EUROPE", "place": "MANCHESTER",
     "head": "Pochettino starts as Manchester United boss",
     "deck": "New head coach begins; first test is Liverpool away on Sunday."},
    {"n": 15, "region": "EUROPE", "place": "BRUSSELS",
     "head": "EU approves Indonesia trade pact to offset tariffs",
     "deck": "Council greenlights deal to cut tariffs as US pressures mount."},
    {"n": 16, "region": "EUROPE", "place": "LONDON",
     "head": "Lords debate Jewish community security",
     "deck": "Peers raise tensions over safety of Britain's Jewish community."},
    {"n": 17, "region": "EUROPE", "place": "SICILY",
     "head": "Bayesian report blames hidden wind flaw",
     "deck": "Final report finds vulnerability behind the yacht's fatal sinking."},
    {"n": 18, "region": "NORTH AMERICA", "place": "NEW YORK",
     "head": "Anthropic debuts on Nasdaq in record $81bn IPO",
     "deck": "Claude maker priced at $83; shares start trading as ANT today."},
    {"n": 19, "region": "NORTH AMERICA", "place": "MARKETS",
     "head": "Stocks slide fifth day as Nvidia nears its low",
     "deck": "S&P 500 falls again; chipmaker halts advanced AI sales to China."},
    {"n": 20, "region": "NORTH AMERICA", "place": "CALIFORNIA",
     "head": "Weather delays Dragon's return from station",
     "deck": "Cargo capsule with cancer samples now due to leave Friday."},
    {"n": 21, "region": "NORTH AMERICA", "place": "SPACE",
     "head": "Voyager 1 sends carrier signal but no data",
     "deck": "NASA confirms one-light-day mark by signal as probe goes quiet."},
    {"n": 22, "region": "NORTH AMERICA", "place": "SPACE",
     "head": "Fermi catalog maps 450 gamma-ray sources",
     "deck": "Fourteen years of data open the MeV gap; 60 sources never seen."},
    {"n": 23, "region": "NORTH AMERICA", "place": "NEW YORK",
     "head": "Van Gogh sells for $190.4m, an artist record",
     "deck": "'Blossoming Chestnut Trees' tops $117m mark after Nazi-claim deal."},
    {"n": 24, "region": "NORTH AMERICA", "place": "SPACE",
     "head": "Dust grains point to water beyond Neptune",
     "deck": "Stratospheric grains hint at a heavy-water reservoir in Kuiper Belt."},
    {"n": 25, "region": "AFRICA", "place": "SUDAN",
     "head": "Sudanese army air strike kills 13 in Kordofan",
     "deck": "Rights group says women and children among dead in West Kordofan."},
    {"n": 26, "region": "AFRICA", "place": "KENYA",
     "head": "Drought deepens Kenya's milk shortage",
     "deck": "Processor deliveries down to 74.09m litres; 500ml packets now 79–89 shillings."},
    {"n": 27, "region": "AFRICA", "place": "SOMALIA",
     "head": "Somalia crisis deepens over federal reforms",
     "deck": "Court says president's term expired; two states cut ties with Mogadishu."},
    {"n": 28, "region": "AFRICA", "place": "JOHANNESBURG",
     "head": "South Africa close in as Bangladesh falter",
     "deck": "Bangladesh 100 for 5, trailing by 57 runs on the final day."},
    {"n": 29, "region": "AFRICA", "place": "UN REPORT",
     "head": "UN: many women lack right to refuse sex",
     "deck": "One in four women globally; 45% in west and central Africa, girls worst hit."},
    {"n": 30, "region": "OCEANIA", "place": "WELLINGTON",
     "head": "Nicholls ton rescues New Zealand from 70 for 5",
     "deck": "Century plus Phillips 94 not out steadies first Test against India."},
    {"n": 31, "region": "OCEANIA", "place": "SYDNEY",
     "head": "Bancroft: whole team knew of sandpaper plot",
     "deck": "Ex-opener reopens 2018 scandal; Cummins stands firm, inquiry urged."},
    {"n": 32, "region": "LATIN AMERICA", "place": "SANTA FE",
     "head": "Paraná flood still rising; 4,500 displaced",
     "deck": "River tops evacuation levels in ten towns; crest still days away."},
]

REGIONS = [
    ("ASIA-PACIFIC", 7),
    ("NORTH AMERICA", 8),
    ("EUROPE", 5),
    ("MIDDLE EAST", 4),
    ("AFRICA", 5),
    ("OCEANIA", 2),
    ("LATIN AMERICA", 1),
]

BY_NUMBER = {s["n"]: s for s in STORIES}
LEAD_NUM = 1
MEDIUM_NUMS = (2, 18, 13)  # left to right
GRID_NUMS = [s["n"] for s in STORIES
             if s["n"] not in (LEAD_NUM, *MEDIUM_NUMS)]

# ---------------------------------------------------------------- fonts

FONT_PATHS = [
    Path("/usr/share/fonts/truetype/liberation"),
    Path("/usr/share/fonts/truetype/dejavu"),
]


def find_font(candidates, size):
    """First matching font file, else PIL's built-in bitmap font."""
    for name in candidates:
        for folder in FONT_PATHS:
            path = folder / name
            if path.exists():
                return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


class Fonts:
    """Lazily cached font handles, keyed by (family, size)."""

    def __init__(self):
        self._cache = {}

    def serif_bold(self, size):
        return self._get("serif_bold", size,
                         ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"])

    def sans(self, size):
        return self._get("sans", size,
                         ["LiberationSans-Regular.ttf", "DejaVuSans.ttf"])

    def sans_bold(self, size):
        return self._get("sans_bold", size,
                         ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"])

    def _get(self, family, size, candidates):
        key = (family, size)
        if key not in self._cache:
            self._cache[key] = find_font(candidates, size)
        return self._cache[key]


# ---------------------------------------------------------------- page

class FrontPage:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), PAPER)
        self.d = ImageDraw.Draw(self.img)
        self.fonts = Fonts()
        self.overflows = []

    # -- text fitting -------------------------------------------------

    def wrap(self, text, font, max_w):
        """Greedy word wrap; returns the list of lines."""
        lines, cur = [], ""
        for word in text.split():
            trial = f"{cur} {word}".strip()
            if self.d.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def fit(self, text, font, max_w, max_lines, num, field):
        """Wrap to at most max_lines; log and ellipsize any excess."""
        lines = self.wrap(text, font, max_w)
        if len(lines) <= max_lines:
            return lines
        dropped = " ".join(lines[max_lines:])
        kept = lines[:max_lines]
        last = kept[-1]
        while last and self.d.textlength(last + " …", font=font) > max_w:
            last = last.rsplit(" ", 1)[0] if " " in last else ""
        kept[-1] = (last + " …").strip()
        self.overflows.append(f"#{num} {field}: dropped [{dropped}]")
        return kept

    # -- shared bits --------------------------------------------------

    def disc(self, cx, cy, r, num, font):
        self.d.ellipse([cx - r, cy - r, cx + r, cy + r],
                       fill=ACCENT, outline=WHITE, width=1)
        self.d.text((cx, cy), str(num), font=font, fill=WHITE, anchor="mm")

    def kicker(self, x, y, story, font):
        self.d.text((x, y), f"{story['region']}  \u00b7  {story['place']}",
                    font=font, fill=ACCENT)

    def card(self, story, x, top, w, h, pad, disc_r, kick_font,
             head_font, head_lh, deck_font, deck_lh, fill=None):
        """One story card; the tier differences are parameters."""
        self.d.rectangle([x, top, x + w - 1, top + h - 1],
                         fill=fill, outline=CARD_EDGE, width=1)
        n = story["n"]
        self.disc(x + pad + disc_r, top + pad + disc_r, disc_r, n,
                  self.fonts.sans_bold(9 if disc_r <= 8 else 10))
        self.kicker(x + pad + 2 * disc_r + 4, top + pad + 1, story,
                    kick_font)
        tw = w - 2 * pad
        y = top + pad + 2 * disc_r + 3
        for line in self.fit(story["head"], head_font, tw, 2, n, "headline"):
            self.d.text((x + pad, y), line, font=head_font, fill=INK)
            y += head_lh
        y += 1
        for line in self.fit(story["deck"], deck_font, tw, 2, n, "deck"):
            self.d.text((x + pad, y), line, font=deck_font, fill=INK)
            y += deck_lh

    # -- sections -----------------------------------------------------

    def masthead(self):
        self.d.text((W // 2, 14), "THE WORLD HERALD",
                    font=self.fonts.serif_bold(54), fill=INK, anchor="ma")
        self.d.text(
            (W // 2, 78),
            "THURSDAY, 19 NOVEMBER 2026   \u2014   32 STORIES FROM SEVEN REGIONS",
            font=self.fonts.sans_bold(13), fill=INK, anchor="ma")
        self.d.line([MARGIN, 100, W - MARGIN, 100], fill=RULE, width=2)
        self.d.line([MARGIN, 104, W - MARGIN, 104], fill=RULE, width=1)

    def region_strip(self):
        font = self.fonts.sans_bold(11)
        top, height, gap = 110, 28, 8
        spans = [self.d.textlength(f"{name}  {count}", font=font) + 24
                 for name, count in REGIONS]
        x = (W - (sum(spans) + gap * (len(spans) - 1))) // 2
        for (name, count), span in zip(REGIONS, spans):
            self.d.rounded_rectangle([x, top, x + span, top + height],
                                     radius=6, fill=CHIP_BG)
            self.d.text((x + 12, top + 7), name, font=font, fill=INK)
            name_w = self.d.textlength(name, font=font)
            self.d.text((x + 12 + name_w + 5, top + 7), str(count),
                        font=font, fill=ACCENT)
            x += span + gap

    def lead(self):
        top, height = 146, 96
        story = BY_NUMBER[LEAD_NUM]
        pad = 12
        self.d.rectangle([MARGIN, top, MARGIN + CONTENT - 1,
                          top + height - 1], fill=CHIP_BG,
                         outline=RULE, width=1)
        self.disc(MARGIN + pad + 9, top + pad + 9, 9, LEAD_NUM,
                  self.fonts.sans_bold(10))
        self.kicker(MARGIN + pad + 23, top + pad + 2, story,
                    self.fonts.sans_bold(10))
        # Illustration reserves 150px on the right; the text must still
        # fit on one line each inside what is left.
        illus_w = 150
        self.flags(MARGIN + CONTENT - pad - illus_w, top, height)
        tw = CONTENT - 2 * pad - illus_w - 14
        y = top + pad + 20
        head_lines = self.fit(story["head"], self.fonts.serif_bold(30),
                              tw, 2, LEAD_NUM, "headline")
        if len(head_lines) > 1:
            self.overflows.append("#1 LEAD HEADLINE wrapped to 2 lines")
        for line in head_lines:
            self.d.text((MARGIN + pad, y), line,
                        font=self.fonts.serif_bold(30), fill=INK)
            y += 33
        y += 2
        self.d.line([MARGIN + pad, y, MARGIN + pad + 72, y],
                    fill=ACCENT, width=2)
        y += 6
        deck_lines = self.fit(story["deck"], self.fonts.sans(15),
                              tw, 2, LEAD_NUM, "deck")
        if len(deck_lines) > 1:
            self.overflows.append("#1 LEAD DECK wrapped to 2 lines")
        for line in deck_lines:
            self.d.text((MARGIN + pad, y), line,
                        font=self.fonts.sans(15), fill=INK)
            y += 18

    def medium_row(self):
        top, height, gap = 250, 118, 10
        w = (CONTENT - 2 * gap) // 3
        for i, num in enumerate(MEDIUM_NUMS):
            self.card(BY_NUMBER[num], MARGIN + i * (w + gap), top, w,
                      height, pad=9, disc_r=8,
                      kick_font=self.fonts.sans_bold(10),
                      head_font=self.fonts.serif_bold(22), head_lh=26,
                      deck_font=self.fonts.sans(13), deck_lh=16)

    def grid(self):
        top, cols, rows = 376, 4, 7
        gap_x, gap_y = 10, 8
        col_w = (CONTENT - gap_x * (cols - 1)) // cols
        row_h = (H - 12 - top - gap_y * (rows - 1)) // rows
        assert len(GRID_NUMS) == cols * rows, len(GRID_NUMS)
        for i, num in enumerate(GRID_NUMS):
            r, c = divmod(i, cols)
            self.card(BY_NUMBER[num], MARGIN + c * (col_w + gap_x),
                      top + r * (row_h + gap_y), col_w, row_h, pad=7,
                      disc_r=7, kick_font=self.fonts.sans_bold(8),
                      head_font=self.fonts.serif_bold(15), head_lh=17,
                      deck_font=self.fonts.sans(11), deck_lh=12)
        return col_w, row_h

    # -- flags --------------------------------------------------------

    def star(self, cx, cy, r, fill):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.42
            pts.append((cx + rad * math.cos(ang),
                        cy + rad * math.sin(ang)))
        self.d.polygon(pts, fill=fill)

    def flags(self, x0, band_top, band_h):
        """US / China / Russia banners for the trilateral-summit lead."""
        bw, bh, gap = 46, 66, 6
        y0 = band_top + (band_h - bh) // 2
        # United States: seven stripes, canton, star dots.
        x = x0
        stripe = bh / 7
        for i in range(7):
            colour = (178, 34, 52) if i % 2 == 0 else WHITE
            self.d.rectangle([x, y0 + i * stripe, x + bw - 1,
                              y0 + (i + 1) * stripe], fill=colour)
        self.d.rectangle([x, y0, x + bw * 0.45 - 1, y0 + bh * 0.45 - 1],
                         fill=(60, 59, 110))
        for row in range(3):
            for col in range(2):
                cx, cy = x + 5 + col * 8, y0 + 5 + row * 8
                self.d.ellipse([cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5],
                               fill=WHITE)
        self.d.rectangle([x, y0, x + bw - 1, y0 + bh - 1],
                         outline=RULE, width=1)
        # China: red field, one large and four small yellow stars.
        x += bw + gap
        self.d.rectangle([x, y0, x + bw - 1, y0 + bh - 1],
                         fill=(222, 41, 16))
        self.star(x + 14, y0 + 15, 9, (255, 222, 0))
        for sx, sy in [(31, 8), (36, 14), (36, 22), (31, 27)]:
            self.star(x + sx, y0 + sy, 3.5, (255, 222, 0))
        self.d.rectangle([x, y0, x + bw - 1, y0 + bh - 1],
                         outline=RULE, width=1)
        # Russia: white / blue / red horizontal bands.
        x += bw + gap
        band = bh / 3
        for i, colour in enumerate([(255, 255, 255), (0, 57, 166),
                                    (213, 0, 50)]):
            self.d.rectangle([x, y0 + i * band, x + bw - 1,
                              y0 + (i + 1) * band], fill=colour)
        self.d.rectangle([x, y0, x + bw - 1, y0 + bh - 1],
                         outline=RULE, width=1)

    # -- build --------------------------------------------------------

    def build(self):
        self.masthead()
        self.region_strip()
        self.lead()
        self.medium_row()
        return self.grid()


def render(out_path, log_path=None):
    page = FrontPage()
    col_w, row_h = page.build()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    page.img.save(out_path, format="PNG", optimize=True)
    small = page.img.resize((300, 300), Image.LANCZOS)
    small_path = out_path.with_name(f"{out_path.stem}-300.png")
    small.save(small_path, format="PNG", optimize=True)
    print(f"wrote {out_path} ({page.img.size[0]}x{page.img.size[1]}, "
          f"{out_path.stat().st_size} bytes); grid card {col_w}x{row_h}")
    print(f"wrote {small_path} ({small_path.stat().st_size} bytes)")
    print(f"overflows: {len(page.overflows)}")
    for line in page.overflows:
        print("  " + line)
    if log_path is not None:
        Path(log_path).write_text("\n".join(page.overflows) + "\n")
    return page


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    out = args[0] if args else "entry.png"
    log = args[1] if len(args) > 1 else None
    render(out, log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
