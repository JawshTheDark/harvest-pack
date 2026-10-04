"""A small pixel-art toolkit: a 5x7 font, shaded shapes and text with outlines.

Everything is drawn at the final size with no anti-aliasing, so it stays crisp in the game.
"""
from PIL import Image, ImageDraw

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


class Cv:
    """A square sprite canvas drawn in unit coordinates (0..1)."""

    def __init__(self, size, inner=None):
        self.s = size
        self.im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.inner = size >= 30 if inner is None else inner

    def _mask(self, prims):
        s = self.s
        m = Image.new("L", (s, s), 0)
        d = ImageDraw.Draw(m)
        for kind, a in prims:
            if kind == "p":
                d.polygon([(x * s, y * s) for x, y in a], fill=255)
            elif kind == "r":
                x0, y0, x1, y1 = a
                d.rectangle([round(x0 * s), round(y0 * s), max(round(x0 * s), round(x1 * s) - 1), max(round(y0 * s), round(y1 * s) - 1)], fill=255)
            elif kind == "e":
                x0, y0, x1, y1 = a
                d.ellipse([x0 * s, y0 * s, max(x0 * s, x1 * s - 1), max(y0 * s, y1 * s - 1)], fill=255)
            elif kind == "l":
                x0, y0, x1, y1, w = a
                d.line([(x0 * s, y0 * s), (x1 * s, y1 * s)], fill=255, width=max(1, round(w * s)))
            elif kind == "a":
                x0, y0, x1, y1, a0, a1, w = a
                d.arc([x0 * s, y0 * s, x1 * s - 1, y1 * s - 1], a0, a1, fill=255, width=max(1, round(w * s)))
        return m

    def add(self, color, *prims, shade=True, ol=None):
        """Draws a part in one colour with a lit top-left edge, a shaded bottom-right edge and
        (on large sprites) a dark outline between parts."""
        s = self.s
        mask = self._mask(prims)
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
        for y in range(s):
            for x in range(s):
                if not mp[x, y]:
                    continue
                up = mp[x, y - 1] if y > 0 else 0
                lf = mp[x - 1, y] if x > 0 else 0
                dn = mp[x, y + 1] if y < s - 1 else 0
                rt = mp[x + 1, y] if x < s - 1 else 0
                c = color
                if shade:
                    if not dn or not rt:
                        c = mul(color, 0.74)
                    elif not up or not lf:
                        c = lit(color, 0.32)
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
