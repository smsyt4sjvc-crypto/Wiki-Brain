"""Generate INMA social-media post images.

Three cards:
  1. social-hindsight.jpg     — "Hindsight, ahead of time." (1080x1080 cream)
  2. social-leverage.jpg      — "You're the one offering the work." (1080x1080 dark)
  3. social-four-ways.jpg     — Four-tier service menu (1080x1350 cream)
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

OUTFIT_VAR = 'Outfit-Regular.ttf'
DM_SERIF   = 'DMSerif-Regular.ttf'

# Brand
DARK   = '#1C1A17'
CREAM  = '#F5F2ED'
GOLD   = '#B8941F'
OLIVE  = '#6B7F5E'
TEXT_DK = '#3A3835'
TEXT_LT = '#F5F2ED'
DIM_DK  = '#7A756D'
DIM_LT  = '#8A857E'

def font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    try:
        if f.get_variation_axes() and weight is not None:
            f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_centered(draw, y, text, fnt, fill, canvas_w):
    w = draw.textlength(text, font=fnt)
    draw.text(((canvas_w - w) // 2, y), text, font=fnt, fill=fill)

def draw_centered_wrapped(draw, y, text, fnt, fill, canvas_w, max_w, line_h=None):
    lines = wrap(draw, text, fnt, max_w)
    if line_h is None:
        ascent, descent = fnt.getmetrics()
        line_h = int((ascent + descent) * 1.18)
    for line in lines:
        draw_centered(draw, y, line, fnt, fill, canvas_w)
        y += line_h
    return y

def paste_logo(img, x, y, size=80):
    try:
        logo = Image.open('/home/user/INMA-/IMG_6892.jpeg').convert('RGBA')
        s = min(logo.size)
        logo = logo.crop(((logo.width-s)//2, (logo.height-s)//2,
                          (logo.width-s)//2 + s, (logo.height-s)//2 + s))
        logo = logo.resize((size, size), Image.LANCZOS)
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=12, fill=255)
        img.paste(logo, (x, y), mask)
    except Exception as e:
        print(f"  logo paste failed: {e}")


# ====================================================================
# CARD 1 — "Hindsight, ahead of time." (1080x1080 cream)
# ====================================================================
def card_hindsight():
    W, H = 1080, 1080
    img = Image.new('RGB', (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Gold top border
    draw.rectangle((0, 0, W, 12), fill=GOLD)

    # Section label
    f_label = font(OUTFIT_VAR, 28, weight=700)
    draw_centered(draw, 130, 'THE LEVERAGE FLIP', f_label, GOLD, W)

    # Big serif headline — sized to fit within canvas with margins
    f_head = font(DM_SERIF, 140)
    draw_centered(draw, 290, 'Hindsight,', f_head, DARK, W)
    draw_centered(draw, 460, 'ahead of time.', f_head, GOLD, W)

    # Subline
    f_sub = font(OUTFIT_VAR, 38, weight=500)
    y = 680
    y = draw_centered_wrapped(
        draw, y,
        "Know what fair-market is before you sign — not after.",
        f_sub, TEXT_DK, W, max_w=820, line_h=56,
    )

    # Divider
    draw.line((W//2 - 80, 850, W//2 + 80, 850), fill=GOLD, width=3)

    # Brand mark
    f_brand = font(DM_SERIF, 60)
    draw_centered(draw, 880, 'INMA', f_brand, GOLD, W)
    f_url = font(OUTFIT_VAR, 26, weight=500)
    draw_centered(draw, 965, 'inmagent.com', f_url, DIM_DK, W)

    # Gold bottom border
    draw.rectangle((0, H-12, W, H), fill=GOLD)

    out = 'social-hindsight.jpg'
    img.save(out, 'JPEG', quality=92, optimize=True)
    print(f"  saved {out}  ({W}x{H})")


# ====================================================================
# CARD 2 — Leverage quote (1080x1080 dark)
# ====================================================================
def card_leverage():
    W, H = 1080, 1080
    img = Image.new('RGB', (W, H), DARK)
    draw = ImageDraw.Draw(img)

    # Gold accent line top-left
    draw.rectangle((80, 130, 200, 138), fill=GOLD)

    # Eyebrow
    f_brow = font(OUTFIT_VAR, 26, weight=700)
    draw.text((80, 160), 'FROM INMA', font=f_brow, fill=GOLD)

    # Big pull quote (serif)
    f_quote = font(DM_SERIF, 88)
    y = 260
    lines = wrap(draw, "You're the one offering the work.", f_quote, W - 160)
    for line in lines:
        draw.text((80, y), line, font=f_quote, fill=TEXT_LT)
        y += 110

    y += 30
    lines2 = wrap(draw, "The negotiation should reflect that.", f_quote, W - 160)
    for line in lines2:
        draw.text((80, y), line, font=f_quote, fill=GOLD)
        y += 110

    # Tagline at bottom
    f_close = font(OUTFIT_VAR, 36, weight=600)
    draw.text((80, H - 200), 'Leverage flipped.', font=f_close, fill=TEXT_LT)

    f_sub = font(OUTFIT_VAR, 26, weight=500)
    draw.text((80, H - 150), 'inmagent.com  ·  (509) 251-7792', font=f_sub, fill=DIM_LT)

    # Logo bottom-right
    paste_logo(img, W - 130, H - 130, size=80)

    out = 'social-leverage.jpg'
    img.save(out, 'JPEG', quality=92, optimize=True)
    print(f"  saved {out}  ({W}x{H})")


# ====================================================================
# CARD 3 — Four Ways menu (1080x1350 portrait cream)
# ====================================================================
def card_four_ways():
    W, H = 1080, 1350
    img = Image.new('RGB', (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Gold top stripe
    draw.rectangle((0, 0, W, 12), fill=GOLD)

    # Section label
    f_label = font(OUTFIT_VAR, 26, weight=700)
    draw_centered(draw, 80, 'PICK YOUR LEVEL', f_label, GOLD, W)

    # Title
    f_title = font(DM_SERIF, 78)
    draw_centered(draw, 130, 'Four Ways to Work', f_title, DARK, W)
    draw_centered(draw, 220, 'With Me.', f_title, DARK, W)

    # Subline
    f_sub = font(OUTFIT_VAR, 28, weight=500)
    y = draw_centered_wrapped(
        draw, 340,
        "Different commitment levels. All four start with a free conversation.",
        f_sub, DIM_DK, W, max_w=860, line_h=42,
    )

    # Cards
    tiers = [
        ('1', 'DIY Assistance',     'Do it yourself, with a coach',                          '$250/visit + $250/wk'),
        ('2', 'Standalone Proposal','Take it to any contractor you want',                    'Flat fee, paid upfront'),
        ('3', 'Full Scope',         'I represent you through the whole project',             '10–15% of project cost'),
        ('4', 'Home Tune-Up',       'Inspect · Seal · Clean · Report',                       '$750 flat'),
    ]

    card_y = 460
    card_h = 160
    pad_x = 60
    card_w = W - pad_x * 2

    for i, (num, name, tagline, price) in enumerate(tiers):
        cy = card_y + i * (card_h + 18)
        # Highlight tier 3 (Full Scope = INMA Model)
        is_hero = (i == 2)
        if is_hero:
            draw.rounded_rectangle((pad_x, cy, pad_x + card_w, cy + card_h), radius=14, fill=DARK)
            num_color   = GOLD
            name_color  = TEXT_LT
            tag_color   = 'rgba(245,242,237,0.6)' or '#A0978B'
            tag_fill    = '#A0978B'
            price_color = GOLD
        else:
            draw.rounded_rectangle((pad_x, cy, pad_x + card_w, cy + card_h), radius=14, outline='#D6D0C6', width=2)
            num_color   = GOLD
            name_color  = DARK
            tag_fill    = DIM_DK
            price_color = '#1C1A17'

        # Tier number circle
        circle_r = 30
        cx = pad_x + 50
        circle_y = cy + card_h // 2
        draw.ellipse((cx - circle_r, circle_y - circle_r, cx + circle_r, circle_y + circle_r),
                     fill=GOLD if not is_hero else GOLD)
        f_num = font(OUTFIT_VAR, 36, weight=700)
        nw = draw.textlength(num, font=f_num)
        # vertical centering — adjust by ~6 px to optically center
        draw.text((cx - nw // 2, circle_y - 26), num, font=f_num, fill=DARK)

        # Name
        f_name = font(DM_SERIF, 44)
        draw.text((pad_x + 110, cy + 28), name, font=f_name, fill=name_color)

        # Tagline
        f_tag = font(OUTFIT_VAR, 24, weight=500)
        draw.text((pad_x + 110, cy + 86), tagline, font=f_tag, fill=tag_fill)

        # Price (right-aligned)
        f_price = font(OUTFIT_VAR, 26, weight=700)
        pw = draw.textlength(price, font=f_price)
        draw.text((pad_x + card_w - 30 - pw, cy + 116), price, font=f_price, fill=price_color)

        # Tier "INMA Model" tag
        if is_hero:
            f_tag_pill = font(OUTFIT_VAR, 16, weight=700)
            tag_text = 'THE INMA MODEL'
            tw = draw.textlength(tag_text, font=f_tag_pill)
            tag_x = pad_x + card_w - tw - 50
            draw.rounded_rectangle((tag_x - 12, cy - 12, tag_x + tw + 12, cy + 18), radius=6, fill=GOLD)
            draw.text((tag_x, cy - 8), tag_text, font=f_tag_pill, fill=DARK)

    # Brand footer
    f_brand = font(DM_SERIF, 48)
    draw_centered(draw, H - 160, 'INMA', f_brand, GOLD, W)
    f_foot = font(OUTFIT_VAR, 24, weight=500)
    draw_centered(draw, H - 90, 'inmagent.com  ·  (509) 251-7792', f_foot, DIM_DK, W)

    # Gold bottom stripe
    draw.rectangle((0, H-12, W, H), fill=GOLD)

    out = 'social-four-ways.jpg'
    img.save(out, 'JPEG', quality=92, optimize=True)
    print(f"  saved {out}  ({W}x{H})")


if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    card_hindsight()
    card_leverage()
    card_four_ways()
