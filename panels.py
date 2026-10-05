"""Windows, banners, tiles and buttons: the pieces a menu background is assembled from."""
from PIL import Image

import sprites
from pxl import OUT, draw_text, gradient, lit, mix, mul, round_mask, text_width

WHITE = (250, 250, 246)

THEMES = {
    "orange": ((255, 196, 92), (226, 100, 52)),
    "green": ((130, 228, 140), (38, 150, 118)),
    "gold": ((255, 234, 120), (236, 158, 44)),
    "blue": ((136, 208, 255), (84, 100, 214)),
    "violet": ((204, 158, 255), (112, 74, 208)),
    "teal": ((124, 238, 222), (44, 146, 176)),
    "red": ((255, 154, 132), (200, 58, 70)),
    "slate": ((156, 182, 226), (74, 94, 158)),
    "pink": ((255, 176, 214), (206, 82, 150)),
    "sky": ((176, 230, 255), (92, 158, 236)),
}

# The 9x6 chest window: slot (c, r) has its item at (8 + 18c, 18 + 18r).
OVER = 8  # how far the banner reaches above the window
WIN_W, WIN_H = 176, 222


def slot_box(c, r, w=1, h=1, inset=1):
    """Pixel box (x, y, width, height) of a block of slots, in window coordinates."""
    return 7 + 18 * c + inset, 17 + 18 * r + inset, 18 * w - 2 * inset, 18 * h - 2 * inset


def slots_of(c, r, w, h):
    return [(r + j) * 9 + c + i for j in range(h) for i in range(w)]


def _edge_pass(img, mask, top_light=0.38, bottom_dark=0.7):
    """Dark outline on the mask's edge, a lit inner edge top-left and a shaded one bottom-right."""
    w, h = img.size
    px = img.load()
    mp = mask.load()

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and mp[x, y] > 0

    edge = set()
    for y in range(h):
        for x in range(w):
            if mp[x, y] and not (inside(x - 1, y) and inside(x + 1, y) and inside(x, y - 1) and inside(x, y + 1)):
                edge.add((x, y))
    for (x, y) in edge:
        px[x, y] = OUT + (255,)
    for y in range(h):
        for x in range(w):
            if not mp[x, y] or (x, y) in edge:
                continue
            c = px[x, y][:3]
            if (x - 1, y) in edge or (x, y - 1) in edge:
                px[x, y] = lit(c, top_light) + (255,)
            elif (x + 1, y) in edge or (x, y + 1) in edge:
                px[x, y] = mul(c, bottom_dark) + (255,)
    for y in range(h):
        for x in range(w):
            if not mp[x, y]:
                px[x, y] = (0, 0, 0, 0)


def glow(img, cx, cy, radius, color, strength=0.5):
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / radius
            if d < 1:
                a = (1 - d) ** 2 * strength
                r, g, b = px[x, y][:3]
                px[x, y] = (int(r + (color[0] - r) * a), int(g + (color[1] - g) * a), int(b + (color[2] - b) * a), 255)


def tile(w, h, theme, sprite=None, label=None, badge=None):
    """A framed, gradient-filled tile with an illustration and an optional label bar."""
    top, bot = THEMES[theme]
    img = gradient(w, h, top, bot)
    px = img.load()
    for y in range(h):
        for x in range(w):
            if ((x - y) // 6) % 3 == 0:
                px[x, y] = lit(px[x, y][:3], 0.07) + (255,)
    side = bool(label) and w >= h * 1.6 and h <= 40
    lines = label.split("\n") if label else []
    lab_h = (2 + 8 * len(lines)) if label and not side else 0
    glow(img, w / 2 if not side else h / 2, (h - lab_h) / 2, min(w, h) * 0.55, lit(top, 0.65), 0.55)
    text_x = None
    if sprite:
        if side:
            spr = sprites.render(sprite, h - 2 - 4)
            img.alpha_composite(spr, (3, (h - spr.height) // 2))
            text_x = 3 + spr.width
        else:
            avail = min(w - 2, h - lab_h)
            spr = sprites.render(sprite, avail - 4)
            img.alpha_composite(spr, ((w - spr.width) // 2, (h - lab_h - spr.height) // 2 + 1))
    if label and side:
        x0 = text_x or 3
        label = label.replace("\n", " ")
        tw = text_width(label)
        draw_text(img, x0 + max(0, (w - x0 - tw) // 2), (h - 7) // 2, label, WHITE, shadow=OUT)
    elif label:
        bar_ = Image.new("RGBA", (w, lab_h), mul(bot, 0.5) + (255,))
        bp = bar_.load()
        for x in range(w):
            bp[x, 0] = lit(mul(bot, 0.5), 0.25) + (255,)
        img.alpha_composite(bar_, (0, h - lab_h))
        for i, line in enumerate(lines):
            tw = text_width(line)
            draw_text(img, (w - tw) // 2, h - lab_h + 2 + 8 * i, line, WHITE, shadow=OUT)
    if badge:
        draw_text(img, 3, 3, badge, WHITE, outline=OUT)
    _edge_pass(img, round_mask(w, h, 3 if min(w, h) >= 24 else 2))
    return img


def pill(w, h, theme, label, sprite=None):
    """A wide button with an icon on the left and a label."""
    top, bot = THEMES[theme]
    img = gradient(w, h, top, bot)
    x = 3
    if sprite:
        s = sprites.render(sprite, h - 6)
        img.alpha_composite(s, (2, (h - s.height) // 2))
        x = s.width + 3
    tw = text_width(label)
    draw_text(img, x + max(0, (w - x - tw) // 2), (h - 7) // 2, label, WHITE, shadow=OUT)
    _edge_pass(img, round_mask(w, h, 3 if h >= 14 else 2))
    return img


def button(theme, sprite):
    """A 1x1 slot button."""
    return tile(16, 16, theme, sprite)


def recess(w, h):
    """A dark square a listing sits in."""
    img = Image.new("RGBA", (w, h), (14, 20, 40, 255))
    px = img.load()
    for x in range(w):
        px[x, 0] = (8, 12, 26, 255)
        px[x, h - 1] = (52, 66, 108, 255)
    for y in range(h):
        px[0, y] = (8, 12, 26, 255)
        px[w - 1, y] = (52, 66, 108, 255)
    return img


def bar(w, h, coin=True):
    """The wide bar a balance is shown in: dark with a gold frame and a coin on the left."""
    img = Image.new("RGBA", (w, h), (20, 26, 48, 255))
    px = img.load()
    for y in range(h):
        for x in range(w):
            if y < 2:
                px[x, y] = (14, 18, 36, 255)
            elif y > h - 3:
                px[x, y] = (46, 58, 98, 255)
    if coin:
        s = sprites.render("coins", h - 6)
        img.alpha_composite(s, (4, (h - s.height) // 2))
    _edge_pass(img, round_mask(w, h, 4), top_light=0.2)
    # a gold rim just inside the outline
    for x in range(2, w - 2):
        for y in (1, h - 2):
            if px[x, y][3]:
                px[x, y] = (236, 170, 50, 255)
    for y in range(2, h - 2):
        for x in (1, w - 2):
            if px[x, y][3]:
                px[x, y] = (236, 170, 50, 255)
    return img


def banner_plate(width=112, height=16):
    """The grey plate the title sits on, reaching up over the window's top edge."""
    img = Image.new("RGBA", (width, height), (214, 214, 214, 255))
    px = img.load()
    for y in range(height):
        for x in range(width):
            if y < 2:
                px[x, y] = (244, 244, 244, 255)
            elif y >= height - 3:
                px[x, y] = (150, 150, 150, 255)
    mask = round_mask(width, height, 3)
    _edge_pass(img, mask, top_light=0.0, bottom_dark=1.0)
    # corner studs
    for x in (4, width - 5):
        for y in (4, height - 5):
            px[x, y] = (110, 110, 110, 255)
    return img


def window(content=True):
    """The window: a light grey vanilla-style frame, a navy inset where the menu lives, and the
    player's inventory slots below. The returned image is OVER pixels taller than the window."""
    img = Image.new("RGBA", (WIN_W, WIN_H + OVER), (0, 0, 0, 0))
    panel = Image.new("RGBA", (WIN_W, WIN_H), (198, 198, 198, 255))
    pp = panel.load()
    for y in range(WIN_H):
        for x in range(WIN_W):
            if x == 0 or y == 0:
                pp[x, y] = (255, 255, 255, 255)
            if x == WIN_W - 1 or y == WIN_H - 1:
                pp[x, y] = (85, 85, 85, 255)
            if x == 1 and y > 0 or y == 1 and x > 0:
                pp[x, y] = (232, 232, 232, 255)
            if x == WIN_W - 2 and y < WIN_H - 1 or y == WIN_H - 2 and x < WIN_W - 1:
                pp[x, y] = (139, 139, 139, 255)
    # rounded outer corners with a black outline, like the real window
    mask = round_mask(WIN_W, WIN_H, 3)
    mp = mask.load()
    for y in range(WIN_H):
        for x in range(WIN_W):
            if not mp[x, y]:
                pp[x, y] = (0, 0, 0, 0)
            else:
                near = [mp[x + dx, y + dy] if 0 <= x + dx < WIN_W and 0 <= y + dy < WIN_H else 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                if not all(near):
                    pp[x, y] = (22, 22, 22, 255)
    img.alpha_composite(panel, (0, OVER))
    if content:
        navy = Image.new("RGBA", (164, 110), (22, 30, 58, 255))
        np_ = navy.load()
        for y in range(110):
            t = y / 109
            c = mix((28, 40, 78), (16, 22, 46), t)
            for x in range(164):
                np_[x, y] = c + (255,)
                if (x * 7 + y * 13) % 53 == 0:
                    np_[x, y] = (60, 78, 128, 255)
        for x in range(164):
            np_[x, 0] = (8, 10, 22, 255)
            np_[x, 109] = (255, 255, 255, 255)
        for y in range(110):
            np_[0, y] = (8, 10, 22, 255)
            np_[163, y] = (255, 255, 255, 255)
        img.alpha_composite(navy, (6, OVER + 16))
    # the player's inventory: vanilla slots
    def slot(x, y):
        s = Image.new("RGBA", (18, 18), (139, 139, 139, 255))
        sp = s.load()
        for i in range(18):
            sp[i, 0] = (55, 55, 55, 255)
            sp[0, i] = (55, 55, 55, 255)
            sp[i, 17] = (255, 255, 255, 255)
            sp[17, i] = (255, 255, 255, 255)
        sp[17, 0] = sp[0, 17] = (139, 139, 139, 255)
        img.alpha_composite(s, (x, OVER + y))

    for r in range(3):
        for c in range(9):
            slot(7 + 18 * c, 139 + 18 * r)
    for c in range(9):
        slot(7 + 18 * c, 197)
    return img


def put(img, art, c, r, w=None, h=None, inset=1):
    """Pastes art into the window over a block of slots."""
    x, y, _, _ = slot_box(c, r, w or 1, h or 1, inset)
    img.alpha_composite(art, (x, OVER + y))
