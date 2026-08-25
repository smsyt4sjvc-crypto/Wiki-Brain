"""Generate INMA mailer card composites — Front A, Front B, Back."""
from PIL import Image, ImageDraw, ImageFont
import os, urllib.request

OUTFIT_VAR  = 'Outfit-Regular.ttf'   # variable font, weight axis 100-900
DM_SERIF    = 'DMSerif-Regular.ttf'

# Weight axis values (Outfit variable font)
W_MEDIUM    = 500
W_SEMIBOLD  = 600
W_BOLD      = 700

# Convenience aliases used by the layout code
OUTFIT_REG  = OUTFIT_VAR
OUTFIT_MED  = OUTFIT_VAR
OUTFIT_SEMI = OUTFIT_VAR
OUTFIT_BOLD = OUTFIT_VAR
OUTFIT      = OUTFIT_VAR

# Auto-fetch fonts from Google Fonts if not present locally
_FONT_URLS = {
    OUTFIT_VAR: 'https://github.com/google/fonts/raw/main/ofl/outfit/Outfit%5Bwght%5D.ttf',
    DM_SERIF:   'https://github.com/google/fonts/raw/main/ofl/dmserifdisplay/DMSerifDisplay-Regular.ttf',
}
for _f, _url in _FONT_URLS.items():
    if not os.path.exists(_f):
        print(f"fetching {_f} ...")
        urllib.request.urlretrieve(_url, _f)

# Brand colors
DARK     = '#1C1A17'
CREAM    = '#F5F2ED'
GOLD     = '#B8941F'
GOLD_LT  = '#D4A843'
TEXT_LT  = '#EAEAEA'   # body on dark
TEXT_DK  = '#3A3835'   # body on cream
DIM_LT   = '#8A857E'

# Dimensions — 9" x 6" @ 300 DPI = 2700 x 1800 (EDDM Jumbo landscape)
W, H = 2700, 1800

_FONT_WEIGHTS = {
    OUTFIT_BOLD: W_BOLD,    # Bold alias -> 700
    OUTFIT_SEMI: W_SEMIBOLD, # SemiBold alias -> 600
    OUTFIT_MED:  W_MEDIUM,   # Medium alias -> 500
    OUTFIT_REG:  400,        # Regular -> 400
}
# Note: aliases all point at the same variable font path, so we need a separate
# weight hint to pick the right axis. We carry the requested weight via 'weight' kw.

def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    # Variable font — set weight axis if requested
    try:
        axes = f.get_variation_axes()
        if axes and weight is not None:
            f.set_variation_by_axes([weight])
    except (AttributeError, OSError):
        pass
    return f

def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_wrapped(draw, xy, text, fnt, fill, max_width, line_height=None, spacing_after_para=0):
    x, y = xy
    if line_height is None:
        ascent, descent = fnt.getmetrics()
        line_height = int((ascent + descent) * 1.25)
    paragraphs = text.split('\n\n')
    for i, p in enumerate(paragraphs):
        for line in wrap_text(draw, p, fnt, max_width):
            draw.text((x, y), line, font=fnt, fill=fill)
            y += line_height
        if i < len(paragraphs) - 1:
            y += spacing_after_para
    return y

def draw_badge(draw, xy, text, bg=GOLD, fg=DARK, pad_x=28, pad_y=14, fnt=None):
    x, y = xy
    tw = draw.textlength(text, font=fnt)
    th = fnt.size
    box = (x, y, x + tw + pad_x*2, y + th + pad_y*2)
    draw.rounded_rectangle(box, radius=8, fill=bg)
    draw.text((x + pad_x, y + pad_y - 2), text, font=fnt, fill=fg)
    return box[3]  # bottom y

def draw_inma_card(img, draw, x, y, card_w=700, card_h=1500, qr_path=None, scan_caption='', name_line=None, bg=DARK, on_dark=True):
    """Right-rail INMA card with logo, name, QR, contact info."""
    # Card background
    if on_dark:
        # Card is the same dark as the page; just renders inline
        pass
    else:
        # Dark card on cream page
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=20, fill=DARK)

    text_color  = TEXT_LT
    accent      = GOLD
    sub_color   = DIM_LT
    cx = x + card_w // 2

    # Bear logo
    try:
        logo = Image.open('/home/user/INMA-/IMG_6892.jpeg').convert('RGBA')
        # Square crop
        s = min(logo.size); logo = logo.crop(((logo.width-s)//2, (logo.height-s)//2,
                                              (logo.width-s)//2 + s, (logo.height-s)//2 + s))
        logo_size = 280
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        # Rounded mask
        mask = Image.new('L', (logo_size, logo_size), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle((0,0,logo_size,logo_size), radius=24, fill=255)
        logo_y = y + 60
        img.paste(logo, (cx - logo_size//2, logo_y), mask)
        cur_y = logo_y + logo_size + 32
    except Exception:
        cur_y = y + 60

    # INMA name
    f_brand = font(DM_SERIF, 92)
    bw = draw.textlength('INMA', font=f_brand)
    draw.text((cx - bw//2, cur_y), 'INMA', font=f_brand, fill=accent)
    cur_y += 110

    # Optional name line (e.g., "Jake Bishop")
    if name_line:
        f_name = font(OUTFIT_VAR, 36, weight=W_MEDIUM)
        nw = draw.textlength(name_line, font=f_name)
        draw.text((cx - nw//2, cur_y), name_line, font=f_name, fill=text_color)
        cur_y += 50
        f_role = font(OUTFIT_VAR, 24, weight=W_MEDIUM)
        rw = draw.textlength('Your Remodeling Agent', font=f_role)
        draw.text((cx - rw//2, cur_y), 'Your Remodeling Agent', font=f_role, fill=sub_color)
        cur_y += 50
    else:
        f_sub = font(OUTFIT_VAR, 26, weight=W_MEDIUM)
        sub_text = 'Homeowner Remodeling Agency'
        sw = draw.textlength(sub_text, font=f_sub)
        draw.text((cx - sw//2, cur_y), sub_text, font=f_sub, fill=sub_color)
        cur_y += 60

    # Divider
    draw.line((x + 80, cur_y, x + card_w - 80, cur_y), fill='#3a352e', width=2)
    cur_y += 40

    # Scan caption
    if scan_caption:
        f_scan = font(OUTFIT_VAR, 26, weight=W_MEDIUM)
        for line in wrap_text(draw, scan_caption, f_scan, card_w - 80):
            lw = draw.textlength(line, font=f_scan)
            draw.text((cx - lw//2, cur_y), line, font=f_scan, fill=accent)
            cur_y += 36
        cur_y += 12

    # inmagent.com
    f_url = font(OUTFIT_VAR, 32, weight=W_MEDIUM)
    uw = draw.textlength('inmagent.com', font=f_url)
    draw.text((cx - uw//2, cur_y), 'inmagent.com', font=f_url, fill=text_color)
    cur_y += 60

    # QR code
    if qr_path and os.path.exists(qr_path):
        qr = Image.open(qr_path).convert('RGB')
        qr_size = 380
        qr = qr.resize((qr_size, qr_size), Image.LANCZOS)
        # White bg pad for scannability
        pad = 20
        qr_bg = Image.new('RGB', (qr_size+pad*2, qr_size+pad*2), 'white')
        qr_bg.paste(qr, (pad, pad))
        img.paste(qr_bg, (cx - (qr_size+pad*2)//2, cur_y))
        cur_y += qr_size + pad*2 + 30

    # Phone
    f_phone = font(OUTFIT_VAR, 32, weight=W_MEDIUM)
    pw = draw.textlength('(509) 251-7792', font=f_phone)
    draw.text((cx - pw//2, cur_y), '(509) 251-7792', font=f_phone, fill=text_color)


def make_front(filename, badge_text, headline_lines, body_text, italic_body, closing_h, closing_p, scan_caption, qr_file, footer_pointer):
    """Create a front-side mailer (LP siding or older home)."""
    img = Image.new('RGB', (W, H), DARK)
    draw = ImageDraw.Draw(img)

    # Layout
    PAD = 110
    LEFT_X = PAD
    LEFT_W = 1750
    RIGHT_X = W - 700 - PAD
    RIGHT_W = 700

    # Badge
    f_badge = font(OUTFIT_VAR, 36, weight=W_BOLD)
    y_after_badge = draw_badge(draw, (LEFT_X, PAD), badge_text, fnt=f_badge)
    y = y_after_badge + 50

    # Headline (3 lines, mixed white + gold) — BOLD for max contrast
    f_head = font(OUTFIT_VAR, 110, weight=W_BOLD)
    for line, color in headline_lines:
        draw.text((LEFT_X, y), line, font=f_head, fill=color)
        y += 130
    y += 40

    # Gold horizontal divider under headline
    draw.line((LEFT_X, y, LEFT_X + 800, y), fill=GOLD, width=3)
    y += 50

    # Body — MEDIUM weight + pure white for legibility
    f_body = font(OUTFIT_VAR, 38, weight=W_MEDIUM)
    y = draw_wrapped(draw, (LEFT_X, y), body_text, f_body, '#FFFFFF', LEFT_W, line_height=60, spacing_after_para=20)
    y += 30

    # Emphasis paragraph (gold, medium weight)
    if italic_body:
        y = draw_wrapped(draw, (LEFT_X, y), italic_body, f_body, GOLD_LT, LEFT_W, line_height=60)
        y += 50

    # Divider
    draw.line((LEFT_X, y, LEFT_X + 800, y), fill='#3a352e', width=2)
    y += 40

    # Closing — SEMIBOLD header + brighter line
    f_close_h = font(OUTFIT_VAR, 46, weight=W_SEMIBOLD)
    draw.text((LEFT_X, y), closing_h, font=f_close_h, fill='#FFFFFF')
    y += 66
    f_close_p = font(OUTFIT_VAR, 34, weight=W_MEDIUM)
    y = draw_wrapped(draw, (LEFT_X, y), closing_p, f_close_p, '#D8D5D0', LEFT_W, line_height=50)

    # Footer pointer (bottom-left)
    f_foot = font(OUTFIT_VAR, 24, weight=W_MEDIUM)
    draw.text((LEFT_X, H - PAD - 30), '▸ ' + footer_pointer, font=f_foot, fill=DIM_LT)

    # Right-rail INMA card
    draw_inma_card(img, draw, RIGHT_X, PAD, card_w=RIGHT_W, card_h=H-PAD*2,
                   qr_path=qr_file, scan_caption=scan_caption,
                   name_line=None)

    img.save(filename, 'PNG', optimize=True)
    print(f"  saved {filename}  ({W}x{H})")


def make_back(filename, qr_file):
    """Create the shared back side (window pitch on cream bg with INMA card right-rail)."""
    img = Image.new('RGB', (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    PAD = 110
    LEFT_X = PAD
    LEFT_W = 1700
    RIGHT_X = W - 700 - PAD
    RIGHT_W = 700

    # Badge
    f_badge = font(OUTFIT_VAR, 36, weight=W_BOLD)
    y = draw_badge(draw, (LEFT_X, PAD), "WHILE YOU'RE AT IT", fnt=f_badge) + 50

    # Headline — BOLD
    f_head = font(OUTFIT_VAR, 110, weight=W_BOLD)
    draw.text((LEFT_X, y), 'New windows pay', font=f_head, fill=DARK)
    y += 130
    draw.text((LEFT_X, y), 'for themselves.', font=f_head, fill=GOLD)
    y += 130 + 20

    # Gold divider
    draw.line((LEFT_X, y, LEFT_X + 800, y), fill=GOLD, width=3)
    y += 50

    # Body — MEDIUM weight, near-black for max print contrast
    f_body = font(OUTFIT_VAR, 36, weight=W_MEDIUM)
    body = "Drafty windows and doors are the #1 source of heat loss in Spokane-area homes. A full replacement typically returns 65-80% of its cost in savings and appraisal value — before comfort."
    y = draw_wrapped(draw, (LEFT_X, y), body, f_body, '#1C1A17', LEFT_W, line_height=58)
    y += 30

    # 14-year credibility callout — semibold, gold-brown for contrast on cream
    f_credit = font(OUTFIT_VAR, 36, weight=W_SEMIBOLD)
    italic = "Before launching INMA, I spent 14 years installing windows in Spokane — the last 5 as lead installer for our local manufacturer. I know which windows perform here and which install details actually matter."
    y = draw_wrapped(draw, (LEFT_X, y), italic, f_credit, '#5A4205', LEFT_W, line_height=58)
    y += 40

    # Avista box
    box_h = 140
    draw.rounded_rectangle((LEFT_X, y, LEFT_X + 1150, y + box_h), radius=14, outline=GOLD, width=4, fill='#FDF8EE')
    f_avista_h = font(OUTFIT_VAR, 30, weight=W_BOLD)
    draw.text((LEFT_X + 30, y + 24), 'AVISTA REBATES AVAILABLE', font=f_avista_h, fill=GOLD)
    f_avista_b = font(OUTFIT_VAR, 28, weight=W_MEDIUM)
    draw.text((LEFT_X + 30, y + 70), 'Qualifying window installs may be eligible. Visit inmagent.com for details.', font=f_avista_b, fill='#1C1A17')
    y += box_h + 40

    # Three bullets — semibold gold label, medium body
    f_bul_h = font(OUTFIT_VAR, 30, weight=W_BOLD)
    f_bul_b = font(OUTFIT_VAR, 28, weight=W_MEDIUM)
    bullets = [
        ('Lower utility bills',   'Typical savings: $200-$500/yr'),
        ('Warmer winters',        'Eliminate cold drafts room by room'),
        ('Higher appraisal',      'Buyers pay more for efficient homes'),
    ]
    for h, b in bullets:
        draw.text((LEFT_X, y), '— ' + h, font=f_bul_h, fill=GOLD)
        hw = draw.textlength('— ' + h, font=f_bul_h)
        draw.text((LEFT_X + hw + 30, y + 4), b, font=f_bul_b, fill='#1C1A17')
        y += 52
    y += 30

    # How INMA Works header — bold
    f_how_h = font(OUTFIT_VAR, 36, weight=W_BOLD)
    draw.text((LEFT_X, y), 'How INMA works:', font=f_how_h, fill=DARK)
    y += 52
    f_how_b = font(OUTFIT_VAR, 30, weight=W_MEDIUM)
    how = "You call me once. I scope the project, price it to fair-market, find the right vetted contractor, and stand behind the work. My fee (10-12%) comes out of the contractor's price — deducted in front of you, not added on top."
    y = draw_wrapped(draw, (LEFT_X, y), how, f_how_b, '#1C1A17', LEFT_W, line_height=46)

    # Footer
    f_foot = font(OUTFIT_VAR, 22, weight=W_MEDIUM)
    draw.text((LEFT_X, H - PAD - 30), 'INMA — Jake Bishop · Spokane, WA · inmagent.com', font=f_foot, fill=DIM_LT)

    # INMA card (dark card on cream background)
    draw_inma_card(img, draw, RIGHT_X, PAD, card_w=RIGHT_W, card_h=H-PAD*2,
                   qr_path=qr_file,
                   scan_caption='Scan to upload your existing quote — free comparison',
                   name_line='Jake Bishop',
                   on_dark=False)

    img.save(filename, 'PNG', optimize=True)
    print(f"  saved {filename}  ({W}x{H})")


# ---- FRONT A — LP siding ----
make_front(
    'front-a-lp-siding.png',
    badge_text="SIDING ALERT",
    headline_lines=[
        ('If your siding went up',     TEXT_LT),
        ('between 1990 and 2015,',     GOLD),
        ("it's worth a look.",         TEXT_LT),
    ],
    body_text="LP siding has a documented end-of-life window — and homes built then are hitting it now. Seams fail, moisture gets in, and most homeowners don't know until the damage is already visible.",
    italic_body="I've inspected thousands of squares of siding across Spokane. James Hardie fiber cement is today's proven replacement. A free walk-around takes 20 minutes — no pitch, no pressure.",
    closing_h="I'm not a contractor. I'm your remodeling agent.",
    closing_p="I scope it, price it to fair-market, and bring the right crew. My fee comes out of the contract — not added on top.",
    scan_caption="Scan to see recent siding installs",
    qr_file='qr-lp-siding.png',
    footer_pointer="Windows & energy upgrades on the back",
)

# ---- FRONT B — Older Homes ----
make_front(
    'front-b-older-home.png',
    badge_text="OLDER HOME?",
    headline_lines=[
        ('Your siding is working',     TEXT_LT),
        ('harder than it should',      GOLD),
        ('be at this point.',          TEXT_LT),
    ],
    body_text="Homes built before 1990 are often wearing original siding — and it shows. Faded, cracked, or failing cladding costs you in curb appeal, energy efficiency, and moisture protection every single season.",
    italic_body="James Hardie fiber cement is the benchmark for lasting protection in the Pacific Northwest climate. I've done hundreds of installs. I know the fair-market price — and what overpriced looks like.",
    closing_h="There's a better way to hire for this.",
    closing_p="I bring the market to you. No phone tag with four contractors. No bids ranging $12k to $22k for the same job. No second-guessing the cheap guy at 11 PM.",
    scan_caption="Scan to see what fair-market looks like",
    qr_file='qr-older-home.png',
    footer_pointer="Windows, energy & Avista rebates on the back",
)

# ---- BACK — Window pitch ----
make_back('back-window-pitch.png', 'qr-window-pitch.png')

print("Done.")
