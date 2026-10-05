"""The illustrations on the menu tiles.

Two kinds of art live side by side. Icons in `art/<name>.png` are the real thing: 32x32 pixel art
(see tools/gemini_import.py for how sheets of AI-drawn icons become these). Any icon without a
PNG falls back to the small hand-drawn one in `pixart.py` (16x16). Either way the icon is only
ever enlarged by whole numbers, so every pixel stays a clean square.
"""
import os

from PIL import Image

import pixart

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art")
_halves = {}


def _custom(name):
    for n in (name, pixart.ALIAS.get(name)):
        if n:
            p = os.path.join(ART, n + ".png")
            if os.path.exists(p):
                return n, Image.open(p).convert("RGBA")
    return None, None


def _half(key, img):
    """A 16x16 version of a 32x32 icon, for the small slots."""
    if key in _halves:
        return _halves[key]
    w, h = img.size
    pre = Image.new("RGBA", (w, h))
    pp, ip = pre.load(), img.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = ip[x, y]
            pp[x, y] = (r * a // 255, g * a // 255, b * a // 255, a)
    small = pre.resize((w // 2, h // 2), Image.BOX)
    sp = small.load()
    out = Image.new("RGBA", small.size, (0, 0, 0, 0))
    op = out.load()
    for y in range(small.height):
        for x in range(small.width):
            r, g, b, a = sp[x, y]
            if a >= 120:
                k = 255 / a
                op[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)
    rgb = Image.new("RGB", out.size, (0, 0, 0))
    rgb.paste(out, (0, 0), out.split()[3])
    q = rgb.quantize(colors=20, dither=Image.Dither.NONE).convert("RGB")
    qp = q.load()
    for y in range(out.height):
        for x in range(out.width):
            if op[x, y][3]:
                op[x, y] = qp[x, y] + (255,)
    _halves[key] = out
    return out


def render(name, size):
    """The icon as an RGBA image. `size` is the room you have, minus 4. The icon is enlarged to
    the biggest whole multiple that fits, allowing a few pixels of its empty border to overhang."""
    avail = size + 4
    key, img = _custom(name)
    if img is not None:
        base = img.width
        if avail + 4 >= base:
            scale = max(1, (avail + 4) // base)
            return img.resize((base * scale, img.height * scale), Image.NEAREST)
        small = _half(key, img)
        scale = max(1, (avail + 2) // small.width)
        return small.resize((small.width * scale, small.height * scale), Image.NEAREST)
    scale = max(1, (avail) // 16)
    out = pixart.render(name, scale)
    if out is None:
        out = pixart.render("gear", scale)
    return out
