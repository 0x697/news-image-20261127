"""Friday 27 November 2026, set as a one-page newspaper front with Pillow.

The page is assembled from data tables (STORIES and the two brief
columns) plus small drawing routines for the diagrams and glyphs. No file
is fetched, no clock is read, and the fonts come from the system DejaVu
set, so rendering twice gives the same PNG byte for byte.
"""

from PIL import Image
from PIL import ImageDraw, ImageFont

W, H = 1024, 1024
LEFT = 24
RIGHT = W - LEFT

PALETTE = {
    "paper": (251, 246, 236),
    "ink": (25, 25, 25),
    "red": (166, 25, 46),
    "teal": (15, 94, 90),
    "navy": (29, 58, 95),
    "amber": (199, 123, 10),
    "grey": (98, 98, 94),
    "card": (255, 255, 255),
    "sky": (214, 232, 240),
    "gold": (255, 232, 170),
    "flame": (255, 150, 20),
    "smoke": (150, 150, 145),
}

FONT_FILES = "/usr/share/fonts/truetype/dejavu/"


def _face(name, size):
    return ImageFont.truetype(FONT_FILES + name + ".ttf", size)


def bold(size):
    return _face("DejaVuSans-Bold", size)


def plain(size):
    return _face("DejaVuSans", size)


def wrap_text(draw, text, face, max_w):
    """Split text into lines that fit max_w pixels, greedily."""
    words = text.split()
    lines = []
    start = 0
    while start < len(words):
        end = start + 1
        while (end <= len(words)
               and draw.textlength(" ".join(words[start:end]), font=face)
               <= max_w):
            end += 1
        lines.append(" ".join(words[start:end - 1]))
        start = end - 1
    return lines


def put_text(draw, x, y, lines, face, fill, leading=1.28):
    """Draw lines top to bottom, returning the y below the last one."""
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += round(face.size * leading)
    return y


def band(draw, top, bottom, fill):
    """A full-width colour band between two y coordinates."""
    draw.rectangle([0, top, W, bottom], fill=fill)


def hline(draw, y, weight=3, fill=None):
    """A horizontal rule across the text column."""
    draw.rectangle([LEFT, y, RIGHT, y + weight - 1],
                   fill=fill or PALETTE["ink"])


def center_text(draw, text, face, y, fill):
    """Draw text centred on the page, using its measured bounding box."""
    box = draw.textbbox((0, 0), text, font=face)
    draw.text(((W - (box[2] - box[0])) / 2 - box[0], y), text, font=face,
              fill=fill)


# ---------------------------------------------------------------- diagrams

def kuwait_panel(draw, px, py, pw, ph):
    """Kuwait: a radar station, an incoming drone, an explosion burst."""
    draw.rectangle([px, py, px + pw, py + ph], fill=PALETTE["sky"],
                   outline=PALETTE["ink"], width=2)
    draw.text((px + 12, py + 10), "KUWAIT — AIR-DEFENCE STATION",
              font=bold(13), fill=PALETTE["navy"])
    floor = py + ph - 22
    # Radar tower with a dish.
    tx = px + 46
    draw.rectangle([tx, floor - 110, tx + 34, floor],
                   fill=PALETTE["navy"], outline=PALETTE["ink"])
    draw.ellipse([tx - 14, floor - 124, tx + 48, floor - 102],
                 fill=PALETTE["card"], outline=PALETTE["ink"], width=2)
    draw.line([tx + 17, floor - 102, tx + 17, floor - 88],
              fill=PALETTE["ink"], width=3)
    # Second mast and a fence.
    mx = px + 120
    draw.rectangle([mx, floor - 78, mx + 20, floor],
                   fill=PALETTE["grey"], outline=PALETTE["ink"])
    draw.ellipse([mx - 2, floor - 92, mx + 22, floor - 76],
                 fill=PALETTE["gold"], outline=PALETTE["ink"])
    for fx in range(px + 12, px + pw - 12, 22):
        draw.line([fx, floor - 14, fx, floor], fill=PALETTE["ink"], width=2)
    draw.line([px + 12, floor - 14, px + pw - 12, floor - 14],
              fill=PALETTE["ink"], width=2)
    # Explosion burst over the station.
    bx, by = px + 210, floor - 96
    for r, col in ((34, PALETTE["flame"]), (24, PALETTE["gold"]),
                   (13, PALETTE["red"])):
        pts = []
        for k in range(12):
            import math
            ang = math.pi * k / 6
            rad = r if k % 2 == 0 else r * 0.55
            pts.append((bx + rad * math.cos(ang), by + rad * math.sin(ang)))
        draw.polygon(pts, fill=col)
    # Smoke puffs, left of the burst.
    for sx, sy in ((px + 150, py + 60), (px + 178, py + 46),
                   (px + 200, py + 62)):
        draw.ellipse([sx - 12, sy - 10, sx + 12, sy + 10],
                     fill=PALETTE["smoke"])
    # Incoming drone, top right.
    dx, dy = px + pw - 64, py + 34
    draw.ellipse([dx - 22, dy - 4, dx + 22, dy + 4], fill=PALETTE["ink"])
    draw.line([dx - 30, dy - 8, dx - 14, dy], fill=PALETTE["ink"], width=3)
    draw.line([dx + 14, dy, dx + 30, dy - 8], fill=PALETTE["ink"], width=3)
    draw.line([dx - 30, dy + 14, dx - 14, dy + 4], fill=PALETTE["ink"],
              width=2)
    draw.text((px + 12, py + ph - 18), "Two technicians dead  •  Iran denies "
              "any role", font=bold(12), fill=PALETTE["red"])


def glyph_burst(draw, cx, cy):
    """An explosion burst: jagged star, flame centre."""
    import math
    pts = []
    for k in range(12):
        ang = math.pi * k / 6
        rad = 24 if k % 2 == 0 else 13
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=PALETTE["flame"], outline=PALETTE["red"])
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=PALETTE["gold"])


def glyph_storm(draw, cx, cy):
    """A storm cloud with a lightning bolt."""
    draw.ellipse([cx - 26, cy - 12, cx - 2, cy + 8], fill=PALETTE["grey"])
    draw.ellipse([cx - 12, cy - 20, cx + 14, cy + 6], fill=PALETTE["smoke"])
    draw.ellipse([cx + 2, cy - 10, cx + 26, cy + 8], fill=PALETTE["grey"])
    draw.polygon([(cx - 2, cy + 4), (cx + 8, cy + 4), (cx + 1, cy + 14),
                  (cx + 9, cy + 14), (cx - 4, cy + 28), (cx + 1, cy + 16),
                  (cx - 6, cy + 16)], fill=PALETTE["amber"],
                 outline=PALETTE["ink"])


def glyph_down(draw, cx, cy):
    """A falling chart arrow: migration down."""
    draw.rectangle([cx - 24, cy - 22, cx + 24, cy + 22],
                   outline=PALETTE["ink"], width=2)
    draw.line([cx - 18, cy - 14, cx - 6, cy - 2, cx + 2, cy - 10,
               cx + 18, cy + 8], fill=PALETTE["teal"], width=4)
    draw.polygon([(cx + 18, cy + 8), (cx + 6, cy + 6), (cx + 12, cy + 18)],
                 fill=PALETTE["teal"])


def glyph_gavel(draw, cx, cy):
    """A judge's gavel on its block."""
    draw.rectangle([cx - 24, cy + 16, cx + 24, cy + 24],
                   fill=(222, 184, 135), outline=PALETTE["ink"])
    draw.polygon([(cx - 24, cy - 16), (cx + 2, cy - 26), (cx + 10, cy - 12),
                  (cx - 16, cy - 2)], fill=PALETTE["navy"],
                 outline=PALETTE["ink"])
    draw.line([cx - 2, cy - 8, cx + 14, cy + 16], fill=(120, 72, 20),
              width=5)


def glyph_ship(draw, cx, cy):
    """A tanker listing to one side, half under water."""
    draw.polygon([(cx - 34, cy - 6), (cx + 30, cy - 22), (cx + 34, cy - 2),
                  (cx - 26, cy + 14)], fill=(70, 70, 70))
    draw.rectangle([cx - 20, cy - 22, cx - 2, cy - 10],
                   fill=PALETTE["red"])
    draw.rectangle([cx + 2, cy - 26, cx + 18, cy - 14],
                   fill=PALETTE["teal"])
    draw.line([cx - 38, cy + 20, cx + 38, cy + 20], fill=PALETTE["teal"],
              width=2)
    draw.line([cx - 34, cy + 26, cx + 34, cy + 26], fill=PALETTE["teal"],
              width=2)


def glyph_flame(draw, cx, cy):
    """Fire: outer tongues, an inner tongue, a base line."""
    draw.polygon([(cx - 19, cy + 20), (cx - 13, cy - 4), (cx - 3, cy - 24),
                  (cx + 3, cy - 6), (cx + 11, cy - 18), (cx + 17, cy),
                  (cx + 19, cy + 20)], fill=PALETTE["flame"],
                 outline=PALETTE["red"])
    draw.polygon([(cx - 8, cy + 20), (cx - 3, cy + 4), (cx + 3, cy - 8),
                  (cx + 8, cy + 6), (cx + 8, cy + 20)], fill=PALETTE["gold"])
    draw.rectangle([cx - 24, cy + 22, cx + 24, cy + 26], fill=PALETTE["ink"])


# ------------------------------------------------------------------- panels

def story_card(draw, x, y, w, h, kicker, headline, body, accent, glyph):
    """One second-lead card: accent strip, kicker, headline, body, glyph."""
    draw.rectangle([x, y, x + w, y + h], fill=PALETTE["card"],
                   outline=PALETTE["ink"], width=2)
    draw.rectangle([x, y, x + w, y + 5], fill=accent)
    glyph(draw, x + w - 46, y + 40)
    draw.text((x + 12, y + 12), kicker, font=bold(11), fill=accent)
    head = wrap_text(draw, headline, bold(16), w - 118)
    yy = put_text(draw, x + 12, y + 30, head, bold(16), PALETTE["ink"], 1.12)
    rest = wrap_text(draw, body, plain(12), w - 24)
    put_text(draw, x + 12, yy + 4, rest, plain(12), PALETTE["ink"], 1.22)


STORIES = [
    ("GAZA  •  CONFLICT", "ISRAEL KILLS 10 IN GAZA; HAMAS WEIGHS REPLY",
     "Israeli strikes kill 10 people in Gaza, Reuters reports; Hamas "
     "weighs its response as the ceasefire frays.",
     PALETTE["red"], glyph_burst),
    ("NEW YORK  •  WEATHER", "STORM GROUNDS THE PARADE — FOR NOW",
     "A nor'easter leaves 900,000 without power on Thanksgiving and "
     "postpones the 100th Macy's parade, a first for weather.",
     PALETTE["navy"], glyph_storm),
    ("LONDON  •  MIGRATION", "UK NET MIGRATION LOWEST SINCE 1997",
     "Net migration falls to its lowest since 1997, outside the "
     "pandemic years, new figures show.",
     PALETTE["teal"], glyph_down),
    ("PARIS  •  JUSTICE", "DEPARDIEU TO STAND TRIAL FOR ALLEGED RAPE",
     "A French court orders Gérard Depardieu to stand trial over an "
     "alleged rape in 2018.",
     PALETTE["navy"], glyph_gavel),
    ("IBIZA  •  DISASTER", "TANKER CAPSIZES OFF IBIZA; ONE DEAD",
     "A diesel tanker carrying up to 7,000 tonnes capsizes near Ibiza, "
     "killing one person.",
     PALETTE["red"], glyph_ship),
    ("BANGKOK  •  INDUSTRY", "BLAST AT BANGKOK REFINERY HURTS NINE",
     "An explosion at a Bangkok oil facility injures nine, three "
     "critically, and forces an evacuation alert.",
     PALETTE["teal"], glyph_flame),
]

BRIEFS_LEFT = [
    "CHESS — Gukesh–Sindarov draw a marathon Game 3.",
    "SHOPPING — Black Friday: cautious shoppers as inflation bites.",
    "WASHINGTON — Trump seeks probe into 'fake' GDP figures.",
    "MANILA — Duterte's ICC trial set to open Monday.",
    "LONDON — UK reservists contacted as the 'threat environment' rises.",
]
BRIEFS_RIGHT = [
    "MOTORSPORT — F1 heads to Qatar as the Verstappen–Russell feud flares.",
    "WELLINGTON — NZ final count due today; coalition holds 67 of 131.",
    "LONDON — UK train knifeman guilty of trying to murder 14.",
    "HEALTH — Cheaper HIV prevention jab reaches Africa.",
    "MYANMAR — Myanmar refuses parts of the ICJ genocide ruling.",
]


def build_page():
    img = Image.new("RGB", (W, H), PALETTE["paper"])
    draw = ImageDraw.Draw(img)

    band(draw, 0, 92, PALETTE["ink"])
    center_text(draw, "THE WORLD TODAY", bold(58), 14, PALETTE["card"])
    band(draw, 92, 126, PALETTE["red"])
    center_text(draw, "FRIDAY, 27 NOVEMBER 2026  •  FROM FIVE CONTINENTS",
                bold(17), 99, PALETTE["card"])

    # Lead story on the left, Kuwait diagram on the right.
    lead_y = 142
    draw.text((LEFT, lead_y), "MIDDLE EAST  •  KUWAIT", font=bold(15),
              fill=PALETTE["red"])
    head = wrap_text(draw, "DRONE STRIKE KILLS TWO ITALIANS IN KUWAIT",
                     bold(34), 600)
    yy = put_text(draw, LEFT, lead_y + 24, head, bold(34), PALETTE["ink"],
                  1.08)
    deck = ("Two Italian technicians are killed at an air-defence station "
            "in a drone strike Kuwait and Italy blame on Iran. Tehran "
            "denies any role.")
    yy = put_text(draw, LEFT, yy + 8,
                  wrap_text(draw, deck, plain(17), 600),
                  plain(17), PALETTE["ink"], 1.3)
    for fact in ("Victims worked for Rheinmetall Italia, on Kuwait's "
                 "Skyguard system",
                 "Second reported strike on the Gulf state this month",
                 "Two more wounded by shrapnel: a Kuwaiti soldier, a "
                 "Pakistani national"):
        draw.text((LEFT, yy + 6), "—  " + fact, font=bold(13),
                  fill=PALETTE["navy"])
        yy += 21
    kuwait_panel(draw, 656, lead_y + 2, 344, 228)

    # One-line strip of the day's figures.
    hline(draw, 382)
    draw.text((LEFT, 390), "BY THE NUMBERS —", font=bold(12),
              fill=PALETTE["red"])
    draw.text((LEFT + 148, 390),
              "2 dead in Kuwait   •   10 killed in Gaza   •   900,000 "
              "without power   •   1 dead off Ibiza   •   9 hurt in Bangkok",
              font=plain(12), fill=PALETTE["ink"])

    # The grid of second leads.
    grid_y, card_h, card_w, gap = 414, 150, 318, 8
    draw.text((LEFT, grid_y), "THE DAY IN SIX STORIES", font=bold(16),
              fill=PALETTE["ink"])
    grid_y += 28
    for i, (kicker, headline, body, accent, glyph) in enumerate(STORIES):
        cx = LEFT + (i % 3) * (card_w + gap)
        cy = grid_y + (i // 3) * (card_h + gap)
        story_card(draw, cx, cy, card_w, card_h, kicker, headline, body,
                   accent, glyph)

    # Also-today band, then the sources footer.
    band_y = 772
    hline(draw, band_y)
    draw.text((LEFT, band_y + 8), "ALSO TODAY", font=bold(15),
              fill=PALETTE["red"])
    col_w = (W - 2 * LEFT) // 2
    yy = band_y + 32
    for item in BRIEFS_LEFT:
        draw.text((LEFT, yy), "•  " + item, font=plain(13),
                  fill=PALETTE["ink"])
        yy += 24
    yy = band_y + 32
    for item in BRIEFS_RIGHT:
        draw.text((LEFT + col_w, yy), "•  " + item, font=plain(13),
                  fill=PALETTE["ink"])
        yy += 24
    hline(draw, 984, weight=2)
    draw.text((LEFT, 992),
              "Sources: Reuters, BBC, CNN, NYT, The Times — 27 November "
              "2026.",
              font=plain(12), fill=PALETTE["grey"])
    draw.text((RIGHT - 190, 992), "THE WORLD TODAY  •  No. 331",
              font=bold(12), fill=PALETTE["grey"])
    return img


if __name__ == "__main__":
    page = build_page()
    page.save("entry.png", format="PNG", optimize=True)
