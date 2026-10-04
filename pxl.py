"""A small pixel-art toolkit: a 5x7 font, shaded shapes and text with outlines.

Everything is drawn at the final size with no anti-aliasing, so it stays crisp in the game.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

OUT = (24, 18, 40)


def mul(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def lit(c, f):
    """Lighter: moves each channel toward white by `f` (0..1)."""
    return tuple(max(0, min(255, int(v + (255 - v) * f))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ------------------------------------------------------------------ font

_G = {}


def _glyph(ch, rows):
    _G[ch] = [r.replace(".", " ") for r in rows.split("/")]


for _c, _r in {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".###./#...#/#..../#..../#..../#...#/.###.",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".###./#...#/#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": "###/.#./.#./.#./.#./.#./###",
    "J": "..###/...#./...#./...#./...#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
    "N": "#...#/##..#/#.#.#/#..##/#...#/#...#/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".####/#..../#..../.###./....#/....#/####.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/...#./..#../.#.../#..../#####",
    "0": ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../.###.",
    "2": ".###./#...#/....#/...#./..#../.#.../#####",
    "3": ".###./#...#/....#/..##./....#/#...#/.###.",
    "4": "...#./..##./.#.#./#..#./#####/...#./...#.",
    "5": "#####/#..../####./....#/....#/#...#/.###.",
    "6": "..##./.#.../#..../####./#...#/#...#/.###.",
    "7": "#####/....#/...#./..#../.#.../.#.../.#...",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/...#./.##..",
    ".": "../../../../../##/##",
    ",": "../../../../.#/.#/#.",
    ":": "./././#/././#",
    ";": "../../.#/../.#/.#/#.",
    "!": "#/#/#/#/#/ /#",
    "?": ".###./#...#/....#/...#./..#../...../..#..",
    "'": "#/#/ / / / / ",
    "-": "..../..../..../####/..../..../....",
    "+": "...../..#../..#../#####/..#../..#../.....",
    "/": "...#/...#/..#./..#./.#../.#../#...",
    "&": ".##../#..#./#.#../.#.../#.#.#/#..#./.##.#",
    "%": "##..#/##.#./...#./..#../.#.../.#.##/#..##",
    "#": ".#.#./#####/.#.#./.#.#./#####/.#.#./.....",
    "(": "..#/.#./#../#../#../.#./..#",
    ")": "#../.#./..#/..#/..#/.#./#..",
    "$": "..#../.####/#.#../.###./..#.#/####./..#..",
    "*": "...../#.#.#/.###./#####/.###./#.#.#/.....",
    ">": "#..../.#.../..#../...#./..#../.#.../#....",
    "<": "....#/...#./..#../.#.../..#../...#./....#",
    "=": "...../...../#####/...../#####/...../.....",
    "x": "...../...../#...#/.#.#./..#../.#.#./#...#",
}.items():
    _glyph(_c, _r)
_G[" "] = ["   "] * 7
HEIGHT = 7


def glyph(ch):
    return _G.get(ch.upper(), _G["?"])


def text_width(s, spacing=1):
    return sum(len(glyph(c)[0]) + spacing for c in s) - spacing if s else 0


def draw_text(img, x, y, s, color, shadow=None, outline=None, spacing=1, scale=1):
    """Draws `s` onto `img` with its top-left at (x, y). Optional 1px shadow (down-right) and outline."""
    px = img.load()
    w, h = img.size
    pts = []
    cx = 0
    for ch in s:
        g = glyph(ch)
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == "#":
                    for sy in range(scale):
                        for sx in range(scale):
                            pts.append((cx * scale + c * scale + sx, r * scale + sy))
        cx += len(g[0]) + spacing
    own = set(pts)

    def put(px_, py_, col):
        X, Y = x + px_, y + py_
        if 0 <= X < w and 0 <= Y < h:
            px[X, Y] = col + (255,)

    if outline:
        ring = set()
        for (a, b) in own:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (a + dx, b + dy)
                    if q not in own:
                        ring.add(q)
        for q in ring:
            put(q[0], q[1], outline)
    if shadow:
        for (a, b) in own:
            if (a + 1, b + 1) not in own:
                put(a + 1, b + 1, shadow)
    for (a, b) in own:
        put(a, b, color)


def text_image(s, color, shadow=None, outline=None, spacing=1, scale=1):
    w = text_width(s, spacing) * scale + 2 + (scale if shadow else 0)
    h = HEIGHT * scale + 2 + (scale if shadow else 0)
    img = Image.new("RGBA", (max(w, 1), h), (0, 0, 0, 0))
    draw_text(img, 1, 1, s, color, shadow=shadow, outline=outline, spacing=spacing, scale=scale)
    return img


# ------------------------------------------------------------------ shapes

def round_mask(w, h, r):
    """Mask of a rectangle with pixel-perfect rounded corners."""
    m = Image.new("L", (w, h), 0)
    px = m.load()
    for y in range(h):
        for x in range(w):
            dx = max(r - x, x - (w - 1 - r), 0)
            dy = max(r - y, y - (h - 1 - r), 0)
            if dx * dx + dy * dy <= r * r + (0 if r < 3 else 1):
                px[x, y] = 255
    return m


def gradient(w, h, top, bottom):
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        c = mix(top, bottom, y / max(1, h - 1))
        for x in range(w):
            px[x, y] = c + (255,)
    return img


def paste_mask(dst, src, x, y, mask=None):
    if mask is None:
        dst.alpha_composite(src, (x, y))
    else:
        layer = Image.new("RGBA", src.size, (0, 0, 0, 0))
        layer.paste(src, (0, 0), mask)
        dst.alpha_composite(layer, (x, y))


def outline_around(img, color=OUT, shadow=True):
    """Adds a 1px outline (and a soft drop shadow) around the opaque pixels, growing the image by 2."""
    w, h = img.size
    out = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    out.alpha_composite(img, (2, 2))
    src = out.copy()
    sp, op = src.load(), out.load()
    for y in range(h + 4):
        for x in range(w + 4):
            if sp[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w + 4 and 0 <= ny < h + 4 and sp[nx, ny][3] > 200:
                    op[x, y] = color + (255,)
                    break
    if shadow:
        solid = out.copy().load()
        for y in range(1, h + 4):
            for x in range(1, w + 4):
                if op[x, y][3] == 0 and solid[x - 1, y - 1][3] > 200:
                    op[x, y] = (0, 0, 0, 70)
    return out


SS = 4  # shapes are drawn this many times larger, then shrunk, which keeps curves and diagonals clean


def _strip(cx, cy, rx, ry, a0, a1, w):
    """A polygon for a thick elliptical arc from angle a0 to a1 (degrees, clockwise from the right)."""
    n = max(12, int(abs(a1 - a0) / 4))
    outer, inner = [], []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        outer.append((cx + (rx + w / 2) * math.cos(a), cy + (ry + w / 2) * math.sin(a)))
        inner.append((cx + (rx - w / 2) * math.cos(a), cy + (ry - w / 2) * math.sin(a)))
    return outer + inner[::-1]


class Cv:
    """A square sprite canvas drawn in unit coordinates (0..1)."""

    def __init__(self, size, inner=None):
        self.s = size
        self.im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.inner = size >= 30 if inner is None else inner

    def _mask(self, prims):
        s = self.s
        S = s * SS
        m = Image.new("L", (S, S), 0)
        d = ImageDraw.Draw(m)
        for kind, a in prims:
            if kind == "p":
                d.polygon([(x * S, y * S) for x, y in a], fill=255)
            elif kind == "r":
                x0, y0, x1, y1 = a
                d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=255)
            elif kind == "e":
                x0, y0, x1, y1 = a
                d.ellipse([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=255)
            elif kind == "l":
                x0, y0, x1, y1, w = a
                wd = max(1.0, w * S)
                d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=255, width=round(wd))
                for (px, py) in ((x0, y0), (x1, y1)):
                    d.ellipse([px * S - wd / 2, py * S - wd / 2, px * S + wd / 2, py * S + wd / 2], fill=255)
            elif kind == "a":
                x0, y0, x1, y1, a0, a1, w = a
                cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - w / 2, (y1 - y0) / 2 - w / 2
                d.polygon([(x * S, y * S) for x, y in _strip(cx, cy, rx, ry, a0, a1, w)], fill=255)
            elif kind == "A":
                # a thick arc ending in an arrowhead: (cx, cy, r, from, to, width, head)
                cx, cy, r, a0, a1, w, head = a
                step = 1 if a1 >= a0 else -1
                shaft_end = a1 - step * math.degrees(head * 0.9 / r)
                d.polygon([(x * S, y * S) for x, y in _strip(cx, cy, r, r, a0, shaft_end, w)], fill=255)
                ang = math.radians(shaft_end)
                tx, ty = -math.sin(ang) * step, math.cos(ang) * step
                bx, by = cx + r * math.cos(ang), cy + r * math.sin(ang)
                nx, ny = math.cos(ang), math.sin(ang)
                tip = (bx + tx * head, by + ty * head)
                d.polygon([(tip[0] * S, tip[1] * S), ((bx + nx * head * 0.62) * S, (by + ny * head * 0.62) * S), ((bx - nx * head * 0.62) * S, (by - ny * head * 0.62) * S)], fill=255)
        return m

    def add(self, color, *prims, shade=True, ol=None, rnd=False):
        """Draws a part in one colour. Shading comes from a blurred copy of the shape lit from the
        top-left and cut into a few flat tones; `rnd` blurs it a lot, so round things look round.
        On large sprites a dark outline separates the parts."""
        s = self.s
        hi = self._mask(prims)
        cov = hi.resize((s, s), Image.BOX)
        mask = cov.point(lambda v: 255 if v >= 104 else 0)
        mp = mask.load()
        op = self.im.load()
        ol = self.inner if ol is None else ol
        if ol:
            line = mul(color, 0.42)
            for y in range(s):
                for x in range(s):
                    if mp[x, y]:
                        continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < s and 0 <= ny < s and mp[nx, ny]:
                            op[x, y] = line + (255,)
                            break
        bb = mask.getbbox()
        if not bb:
            return self
        size = min(bb[2] - bb[0], bb[3] - bb[1])
        radius = max(1.0, min(5.0, size * 0.24)) if rnd else 1.0
        hp = mask.filter(ImageFilter.GaussianBlur(radius)).load()

        def h(x, y):
            return hp[min(max(x, 0), s - 1), min(max(y, 0), s - 1)]

        lights = {}
        top = 1e-6
        for y in range(bb[1], bb[3]):
            for x in range(bb[0], bb[2]):
                if mp[x, y]:
                    gx = h(x + 1, y) - h(x - 1, y)
                    gy = h(x, y + 1) - h(x, y - 1)
                    v = 0.7071 * (gx + gy)
                    lights[(x, y)] = v
                    top = max(top, abs(v))
        for (x, y), v in lights.items():
            c = color
            if shade:
                k = v / top
                if k > 0.55:
                    c = lit(color, 0.40)
                elif k > 0.18:
                    c = lit(color, 0.18)
                elif k < -0.55:
                    c = mul(color, 0.62)
                elif k < -0.18:
                    c = mul(color, 0.82)
            op[x, y] = c + (255,)
        return self

    def dots(self, color, pts):
        """Single pixels at unit coordinates."""
        s = self.s
        op = self.im.load()
        for x, y in pts:
            X, Y = int(x * s), int(y * s)
            if 0 <= X < s and 0 <= Y < s:
                op[X, Y] = color + (255,)
        return self

    def done(self):
        return outline_around(self.im)
