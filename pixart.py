"""Hand-drawn pixel icons.

Every icon is drawn on a small grid, one character per pixel, with a fixed palette. A shape is
drawn once in its middle tone; `finish` adds the light edge (top, left), the shaded edge
(bottom, right) and a dark outline in the colour of whatever it surrounds. The result is 16x16
and is only ever enlarged by whole numbers, so every pixel stays a clean square.

Palette letters (light / middle / dark):
    gold Y y z     steel S s t    wood W w x     red R r q      blue B b c
    green G g h    purple P p o   pink K k j     orange O a n   teal T e f
    stone U u v    paper C m      white #        black d
"""
import math

from PIL import Image

PAL = {
    "Y": (255, 238, 150), "y": (255, 200, 60), "z": (206, 132, 28),
    "S": (240, 246, 252), "s": (188, 198, 216), "t": (118, 130, 156),
    "W": (214, 158, 92), "w": (164, 108, 56), "x": (104, 64, 34),
    "R": (255, 134, 116), "r": (228, 62, 58), "q": (156, 30, 46),
    "B": (150, 208, 255), "b": (66, 134, 238), "c": (36, 80, 172),
    "G": (168, 238, 132), "g": (80, 186, 86), "h": (40, 118, 62),
    "P": (214, 182, 255), "p": (154, 102, 228), "o": (96, 56, 170),
    "K": (255, 204, 228), "k": (248, 132, 186), "j": (190, 76, 130),
    "O": (255, 200, 124), "a": (250, 142, 50), "n": (184, 84, 28),
    "T": (156, 242, 232), "e": (58, 192, 186), "f": (30, 128, 136),
    "U": (206, 210, 220), "u": (160, 166, 178), "v": (110, 116, 132),
    "C": (255, 246, 214), "m": (222, 200, 146),
    "#": (255, 255, 252), "d": (50, 42, 70),
}

# a middle tone -> (its light, its dark); letters of one ramp count as the same material
MID = {
    "y": ("Y", "z"), "s": ("S", "t"), "w": ("W", "x"), "r": ("R", "q"), "b": ("B", "c"),
    "g": ("G", "h"), "p": ("P", "o"), "k": ("K", "j"), "a": ("O", "n"), "e": ("T", "f"), "u": ("U", "v"),
}
GROUP = {}
for _mid, (_l, _d) in MID.items():
    GROUP[_mid] = GROUP[_l] = GROUP[_d] = _mid
GROUP.update({"C": "C", "m": "C"})

SIZE = 14


class Pix:
    def __init__(self, w=SIZE, h=SIZE):
        self.w, self.h = w, h
        self.g = [["."] * w for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = c

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else "."

    def stamp(self, x0, y0, text, clip=None):
        """Draws rows of text with its top-left at (x0, y0); '.' leaves the pixel alone."""
        rows = [r for r in text.strip("\n").split("\n")]
        for dy, row in enumerate(rows):
            for dx, c in enumerate(row):
                if c != "." and c != " ":
                    self.put(x0 + dx, y0 + dy, c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        x, y = x0, y0
        while True:
            self.put(x, y, c)
            if thick > 1:
                self.put(x + 1, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        n = len(pts)
        for y in range(self.h):
            for x in range(self.w):
                px, py = x + 0.5, y + 0.5
                inside = False
                j = n - 1
                for i in range(n):
                    xi, yi = pts[i]
                    xj, yj = pts[j]
                    if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                        inside = not inside
                    j = i
                if inside:
                    self.put(x, y, c)

    def disc(self, cx, cy, rx, ry, ramp, only=None):
        """A lit ball: `ramp` is (light, mid, dark) or (light, mid, dark, darkest)."""
        lx, ly, lz = -0.52, -0.62, 0.59
        for y in range(self.h):
            for x in range(self.w):
                dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d2 = dx * dx + dy * dy
                if d2 <= 1.0:
                    v = dx * lx + dy * ly + math.sqrt(1 - d2) * lz
                    if v > 0.58:
                        c = ramp[0]
                    elif v > 0.0:
                        c = ramp[1]
                    elif v > -0.42 or len(ramp) < 4:
                        c = ramp[2]
                    else:
                        c = ramp[3]
                    if only is None or self.get(x, y) in only:
                        self.put(x, y, c)

    def ring(self, cx, cy, r_out, r_in, c):
        for y in range(self.h):
            for x in range(self.w):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if r_in <= d <= r_out:
                    self.put(x, y, c)

    def arrow_arc(self, cx, cy, r, a0, a1, c, thick=2.4, head=3.2, hw=2.9):
        """A curved arrow along a circle, travelling from angle a0 to a1 (degrees, y down, so
        increasing angles go clockwise on screen), with its head at a1."""
        step = 1 if a1 >= a0 else -1
        span = abs(a1 - a0)
        trim = math.degrees(head * 0.55 / r)
        for y in range(self.h):
            for x in range(self.w):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                if abs(math.hypot(dx, dy) - r) <= thick / 2:
                    ang = math.degrees(math.atan2(dy, dx))
                    prog = ((ang - a0) * step) % 360
                    if prog <= span - trim:
                        self.put(x, y, c)
        a = math.radians(a1)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        tx, ty = (-math.sin(a), math.cos(a)) if step > 0 else (math.sin(a), -math.cos(a))
        nx, ny = math.cos(a), math.sin(a)
        self.poly([(ex + tx * head, ey + ty * head), (ex + nx * hw, ey + ny * hw), (ex - nx * hw, ey - ny * hw)], c)

    def mirror_x(self):
        self.g = [row[::-1] for row in self.g]

    def silhouette(self):
        return {(x, y) for y in range(self.h) for x in range(self.w) if self.g[y][x] != "."}


def _bevel(p):
    """Light on the top-left edges of each material, shade on the bottom-right ones."""
    out = [row[:] for row in p.g]
    for y in range(p.h):
        for x in range(p.w):
            c = p.g[y][x]
            if c not in MID:
                continue
            grp = GROUP[c]

            def other(xx, yy):
                n = p.get(xx, yy)
                return n == "." or GROUP.get(n, n) != grp

            tl = other(x, y - 1) or other(x - 1, y)
            br = other(x, y + 1) or other(x + 1, y)
            if tl and not br:
                out[y][x] = MID[c][0]
            elif br and not tl:
                out[y][x] = MID[c][1]
    p.g = out


def _outline(p):
    """A 1px outline in a dark version of the colour it touches. Returns a (w+2) x (h+2) grid of RGBA."""
    w, h = p.w, p.h
    px = [[None] * (w + 2) for _ in range(h + 2)]
    for y in range(h):
        for x in range(w):
            c = p.g[y][x]
            if c != ".":
                px[y + 1][x + 1] = PAL[c] + (255,)
    final = [row[:] for row in px]
    for y in range(h + 2):
        for x in range(w + 2):
            if px[y][x] is not None:
                continue
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w + 2 and 0 <= ny < h + 2 and px[ny][nx] is not None:
                    col = px[ny][nx]
                    if best is None or sum(col[:3]) < sum(best[:3]):
                        best = col
            if best is not None:
                final[y][x] = tuple(max(0, int(v * 0.30)) for v in best[:3]) + (255,)
    return final


def finish(p, bevel=True):
    # centre the drawing on the 14x14 canvas
    if bevel:
        _bevel(p)
    minx = min((x for y in range(p.h) for x in range(p.w) if p.g[y][x] != "."), default=0)
    maxx = max((x for y in range(p.h) for x in range(p.w) if p.g[y][x] != "."), default=0)
    miny = min((y for y in range(p.h) for x in range(p.w) if p.g[y][x] != "."), default=0)
    maxy = max((y for y in range(p.h) for x in range(p.w) if p.g[y][x] != "."), default=0)
    cw, ch = maxx - minx + 1, maxy - miny + 1
    ox, oy = (SIZE - cw) // 2 - minx, (SIZE - ch) // 2 - miny
    q = Pix(SIZE, SIZE)
    for y in range(p.h):
        for x in range(p.w):
            if p.g[y][x] != ".":
                q.put(x + ox, y + oy, p.g[y][x])
    px = _outline(q)
    img = Image.new("RGBA", (SIZE + 2, SIZE + 2), (0, 0, 0, 0))
    ip = img.load()
    for y, row in enumerate(px):
        for x, v in enumerate(row):
            if v is not None:
                ip[x, y] = v
    return img


ART = {}
DRAW = {}


def art(name, text):
    ART[name] = text


def draw(name):
    def deco(fn):
        DRAW[name] = fn
        return fn
    return deco


# ---------------------------------------------------------------- hubs

art("builder", """
rrrrSrrrrSrrrr
rrrrSrrrrSrrrr
SSSSSSSSSSSSSS
rrSrrrrSrrrrSr
rrSrrrrSrrrrSr
SSSSSSSSSSSSSS
rrrrSrrrrSrrrr
rrrrSrrrrSrrrr
SSSSSSSSSSSSSS
rrSrrrrSrrrrSr
rrSrrrrSrrrrSr
""")


art("market", """
rr##rr##rr##rr
rr##rr##rr##rr
rr##rr##rr##rr
qq##qq##qq##qq
.x..........x.
.x.rr.gg.yy.x.
.x.rr.gg.yy.x.
wwwwwwwwwwwwww
wwwwwwwwwwwwww
wwxwwwwwwwwxww
wwxwwwwwwwwxww
xxxxxxxxxxxxxx
""")

art("coins", """
....YYYYyy....
...Yyyyyyyz...
..Yyyyyyyyyz..
..Yyyyzzyyyz..
.Yyyyzyyzyyyz.
.YyyzyYYyzyyz.
.YyyzyYYyzyyz.
.Yyyyzyyzyyyz.
..Yyyyzzyyyz..
..yyyyyyyyzz..
...yyyyyyzz...
....yyzzzz....
""")
ART["coin"] = ART["coins"]

art("notepad", """
rrrrrrrrrr
CCCCCCCCCm
CbbbbbbbCm
CCCCCCCCCm
CbbbbbbCCm
CCCCCCCCCm
CbbbbbbbCm
CCCCCCCCCm
CbbbbCCCCm
CCCCCCCCCm
CCCCCCCCCm
CCCCCCCCCm
mmmmmmmmmm
""")


@draw("logbook")
def _logbook(p):
    p.stamp(0, 0, ART["notepad"])
    p.stamp(6, 6, """
.ssss...
sBBBBs..
sB#BBs..
sBBBBs..
.ssssw..
.....ww.
......ww
""")


@draw("magnifier")
def _magnifier(p):
    p.disc(5.0, 5.0, 4.6, 4.6, "BBbc")
    p.ring(5.0, 5.0, 5.0, 3.6, "s")
    p.put(3, 3, "#")
    p.put(4, 3, "#")
    p.put(3, 4, "#")
    p.line(9, 9, 12, 12, "w", thick=2)
    p.line(9, 10, 11, 12, "w")


@draw("world")
def _world(p):
    p.disc(7.0, 6.5, 6.4, 6.4, "Bbcc")
    p.stamp(3, 2, """
.gg.
gggg
.ggg
..g.
""")
    p.stamp(7, 6, """
.ggg
gggg
.ggg
..g.
""")
    for x in range(p.w):
        for y in range(p.h):
            pass
    p.stamp(5, 12, """
.xxxx.
xxxxxx
""")


# ---------------------------------------------------------------- selection and shapes

@draw("select")
def _select(p):
    for i in range(0, 12, 2):
        p.put(i, 0, "y")
        p.put(i, 11, "y")
        p.put(0, i, "y")
        p.put(11, i, "y")
    p.stamp(6, 5, """
#.......
##......
###.....
####....
#####...
######..
#######.
####....
##.##...
#..##...
...##...
""")


def _iso(p, top, left, right, pts_top, pts_left, pts_right):
    p.poly(pts_top, top)
    p.poly(pts_left, left)
    p.poly(pts_right, right)


@draw("cube")
def _cube(p):
    _iso(p, "B", "b", "c", [(7, 0), (14, 3.5), (7, 7), (0, 3.5)], [(0, 3.5), (7, 7), (7, 14), (0, 10.5)], [(14, 3.5), (7, 7), (7, 14), (14, 10.5)])


@draw("shapes")
def _shapes(p):
    _iso(p, "O", "r", "q", [(7, 0), (14, 3.5), (7, 7), (0, 3.5)], [(0, 3.5), (7, 7), (7, 14), (0, 10.5)], [(14, 3.5), (7, 7), (7, 14), (14, 10.5)])


@draw("pyramid")
def _pyramid(p):
    p.poly([(7, 0), (0, 9), (7, 14)], "Y")
    p.poly([(7, 0), (7, 14), (14, 9)], "z")
    p.put(6, 2, "#")


@draw("sphere")
def _sphere(p):
    p.disc(7, 7, 6.9, 6.9, "Ppoo")
    p.put(4, 3, "#")
    p.put(5, 3, "#")
    p.put(4, 4, "#")


@draw("ellipsoid")
def _ellipsoid(p):
    p.disc(7, 7, 7, 4.6, "Ppoo")
    p.put(3, 5, "#")
    p.put(4, 5, "#")
    p.put(4, 4, "#")


art("cylinder", """
..GGGGGGGG..
.GGGGGGGGGG.
GGGGGGGGGGGG
.GGGGGGGGGG.
hhhhhhhhhhhh
ggggggggghhh
ggggggggghhh
ggggggggghhh
ggggggggghhh
ggggggggghhh
ggggggggghhh
.gggggggghh.
..ggggggghh.
...hhhhhhh..
""")


@draw("polygon")
def _polygon(p):
    p.poly([(7, 0.5), (13.5, 5.2), (11, 13), (3, 13), (0.5, 5.2)], "e")
    for x, y in ((7, 0), (13, 5), (10, 12), (3, 12), (1, 5)):
        p.put(x, y, "#")


@draw("grid")
def _grid(p):
    for i in range(3):
        for j in range(3):
            c = "y" if (i, j) == (1, 1) else "u"
            p.rect(i * 5, j * 5, i * 5 + 3, j * 5 + 3, c)


@draw("ruler")
def _ruler(p):
    p.rect(0, 3, 13, 9, "y")
    for i in range(0, 14, 2):
        p.rect(i, 3, i, 5 if i % 4 == 0 else 4, "d")


@draw("expand")
def _expand(p):
    p.rect(5, 5, 8, 8, "u")
    p.stamp(5, 0, "..g..\n.ggg.\n")
    p.rect(6, 2, 7, 3, "g")
    p.stamp(5, 12, ".ggg.\n..g..\n")
    p.rect(6, 10, 7, 11, "g")
    p.stamp(0, 5, ".g\ngg\n.g\n")
    p.rect(2, 6, 3, 7, "g")
    p.stamp(12, 5, "g.\ngg\ng.\n")
    p.rect(10, 6, 11, 7, "g")


@draw("eraser")
def _eraser(p):
    p.poly([(0, 8), (6, 2), (12, 8), (6, 14)], "k")
    p.poly([(6, 2), (9, 0), (14, 5), (12, 8)], "#")
    p.line(0, 13, 13, 13, "t")


# ---------------------------------------------------------------- terrain and nature

art("terrain", """
.....##.......
....####......
...##uuv..##..
...#uuuvv.####
..##uuuuvvvvv.
..#uuuuuuuvvv.
.##uuuuuuuuvvv
.#uuuuuuuuuuvv
##uuuuuuuuuuuv
gguuuuuuuuuuvg
gggguuuuuuuggg
gggggggggggggg
""")


@draw("tree")
def _tree(p):
    p.rect(6, 9, 7, 13, "w")
    p.disc(7, 5.2, 6.4, 5.2, "GgGh")
    p.disc(4.2, 5.8, 3.4, 3.4, "GgGh")
    p.disc(10, 5.8, 3.4, 3.4, "GgGh")
    p.disc(7, 4.2, 4.2, 3.6, "GGgg")
    p.put(5, 2, "#")
    p.put(6, 2, "#")


@draw("sapling")
def _sapling(p):
    p.rect(6, 6, 7, 13, "g")
    p.stamp(1, 1, """
.ggg
gggg
.ggg
..gg
""")
    p.stamp(7, 2, """
ggg.
gggg
ggg.
gg..
""")


@draw("flower")
def _flower(p):
    p.rect(6, 8, 7, 13, "g")
    p.stamp(7, 10, "gg\ngg")
    for ang in (-90, -18, 54, 126, 198):
        a = math.radians(ang)
        p.disc(7 + math.cos(a) * 3.6, 4.6 + math.sin(a) * 3.6, 2.4, 2.4, "Kkkj")
    p.disc(7, 4.6, 1.9, 1.9, "Yyyz")


@draw("up")
def _up(p):
    p.stamp(0, 0, """
.....aa.....
....aaaa....
...aaaaaa...
..aaaaaaaa..
.aaaaaaaaaa.
....aaaa....
....aaaa....
....aaaa....
....aaaa....
uuuuuuuuuuuu
uuuuuuuuuuuu
""")


@draw("down")
def _down(p):
    p.stamp(0, 0, """
uuuuuuuuuuuu
uuuuuuuuuuuu
....aaaa....
....aaaa....
....aaaa....
....aaaa....
.aaaaaaaaaa.
..aaaaaaaa..
...aaaaaa...
....aaaa....
.....aa.....
""")


art("crystal", """
..PPppppoo..
.PPPPpppooo.
PPPPPPpooooo
pppppppppppp
.ppppppppoo.
..ppppppoo..
...ppppoo...
....ppoo....
.....po.....
......o.....
""")


# ---------------------------------------------------------------- clipboard

@draw("copy")
def _copy(p):
    p.rect(0, 0, 7, 9, "s")
    p.rect(1, 1, 6, 8, "S")
    p.rect(5, 4, 12, 13, "#")
    p.rect(5, 4, 12, 4, "s")
    p.rect(5, 4, 5, 13, "s")
    p.rect(12, 4, 12, 13, "s")
    p.rect(5, 13, 12, 13, "s")
    for y in (6, 8, 10):
        p.rect(7, y, 10, y, "b")


@draw("clipboard")
def _clipboard(p):
    p.stamp(0, 0, """
...ssss...
WWWSssSWWw
WCCCCCCCCw
WCbbbbbbCw
WCCCCCCCCw
WCbbbbCCCw
WCCCCCCCCw
WCbbbbbbCw
WCCCCCCCCw
WCbbbCCCCw
WCCCCCCCCw
wwwwwwwwwx
xxxxxxxxxx
""")


@draw("paste")
def _paste(p):
    p.stamp(0, 0, """
...ssss...
WWWSssSWWw
WCCCCCCCCw
WCbbbbbbCw
WCCCCCCCCw
WCCCCCCCCw
WCCCCCCCCw
WCCCCCCCCw
WCCCCCCCCw
WCCCCCCCCw
WCCCCCCCCw
wwwwwwwwwx
xxxxxxxxxx
""")
    p.stamp(3, 4, """
..gg..
..gg..
gggggg
.gggg.
..gg..
""")


@draw("scissors")
def _scissors(p):
    p.line(3, 0, 9, 8, "s")
    p.line(4, 0, 10, 8, "s")
    p.line(10, 0, 4, 8, "s")
    p.line(9, 0, 3, 8, "s")
    p.put(6, 4, "t")
    p.put(7, 4, "t")
    p.ring(3.0, 11.0, 3.0, 1.6, "r")
    p.ring(11.0, 11.0, 3.0, 1.6, "r")


@draw("flip")
def _flip(p):
    p.poly([(0, 1), (0, 13), (5.5, 7)], "e")
    p.poly([(14, 1), (14, 13), (8.5, 7)], "y")
    for y in range(0, 14, 2):
        p.put(6, y, "#")
        p.put(7, y, "#")


@draw("trash")
def _trash(p):
    p.stamp(0, 0, """
.....ss.....
suuuuuuuuuus
.sSSSSSSSSs.
..sSsSsSsSs.
..sSsSsSsSs.
..sSsSsSsSs.
..sSsSsSsSs.
..sSsSsSsSs.
..sSsSsSsSs.
..ssssssssss
""")


@draw("folder")
def _folder(p):
    p.stamp(0, 0, """
yyyyyy......
yyyyyyyyyyyy
yCCCCCCCCCCy
yyyyyyyyyyyy
yyyyyyyyyyyy
yyyyyyyyyyyy
yyyyyyyyyyyy
yyyyyyyyyyyy
yyyyyyyyyyyy
""")


@draw("compass")
def _compass(p):
    p.disc(7, 7, 6.9, 6.9, "SSsT")
    p.ring(7, 7, 6.9, 5.6, "t")
    p.poly([(7, 1.6), (10, 7), (4, 7)], "r")
    p.poly([(7, 12.4), (10, 7), (4, 7)], "t")
    p.rect(6, 6, 7, 7, "d")


# ---------------------------------------------------------------- arrows

@draw("undo")
def _undo(p):
    p.arrow_arc(8.0, 6.0, 4.8, 28, -165, "b", thick=2.2, head=4.8, hw=4.2)


@draw("redo")
def _redo(p):
    p.arrow_arc(8.0, 6.0, 4.8, 28, -165, "g", thick=2.2, head=4.8, hw=4.2)
    p.mirror_x()


@draw("rotate")
def _rotate(p):
    p.arrow_arc(7.0, 7.0, 4.9, 25, 292, "b", thick=2.4, head=4.8, hw=4.2)


@draw("cycle")
def _cycle(p):
    p.arrow_arc(7.0, 7.0, 5.0, 205, 325, "g", thick=2.2, head=4.4, hw=3.8)
    p.arrow_arc(7.0, 7.0, 5.0, 25, 145, "g", thick=2.2, head=4.4, hw=3.8)


art("swap", """
.........b....
.........bb...
bbbbbbbbbbbbb.
bbbbbbbbbbbbbb
bbbbbbbbbbbbb.
.........bb...
.........b....
....a.........
...aa.........
.aaaaaaaaaaaaa
aaaaaaaaaaaaaa
.aaaaaaaaaaaaa
...aa.........
....a.........
""")


@draw("back")
def _back(p):
    p.stamp(0, 0, """
.....yy.......
....yyy.......
...yyyy.......
..yyyyyyyyyyy.
.yyyyyyyyyyyy.
yyyyyyyyyyyyy.
.yyyyyyyyyyyy.
..yyyyyyyyyyy.
...yyyy.......
....yyy.......
.....yy.......
""")


@draw("next")
def _next(p):
    p.stamp(0, 0, """
.......yy.....
.......yyy....
.......yyyy...
.yyyyyyyyyyy..
.yyyyyyyyyyyy.
.yyyyyyyyyyyyy
.yyyyyyyyyyyy.
.yyyyyyyyyyy..
.......yyyy...
.......yyy....
.......yy.....
""")


@draw("close")
def _close(p):
    for i in range(12):
        p.put(i, i, "r")
        p.put(i + 1, i, "r")
        p.put(11 - i, i, "r")
        p.put(12 - i, i, "r")


# ---------------------------------------------------------------- shops and money

@draw("gavel")
def _gavel(p):
    p.stamp(0, 0, """
.wwwwwwwwww.
wwwwwwwwwwww
wxwwwwwwwwxw
wxwwwwwwwwxw
wwwwwwwwwwww
.wwwwwwwwww.
.....ww.....
.....ww.....
.....ww.....
.....ww.....
.tttttttttt.
.tttttttttt.
""")


@draw("chest")
def _chest(p):
    p.stamp(0, 0, """
.wwwwwwwwwwww.
wwwwwwwwwwwwww
wxxxxxxxxxxxxw
yyyyyyyyyyyyyy
wwwwwyyyywwwww
wwwwwyddywwwww
wwwwwwddwwwwww
wxxxxxxxxxxxxw
wwwwwwwwwwwwww
""")


@draw("tag")
def _tag(p):
    p.poly([(0, 7), (6, 1), (13, 1), (13, 8), (7, 14)], "y")
    p.disc(10.4, 4.0, 1.4, 1.4, "dddd")
    p.rect(6, 6, 7, 9, "z")
    p.rect(5, 7, 8, 7, "z")
    p.rect(5, 9, 8, 9, "z")


@draw("gift")
def _gift(p):
    p.stamp(0, 0, """
...yyy..yyy...
..yy.yyyy.yy..
..yyyyyyyyyy..
rrrrrryyrrrrrr
rrrrrryyrrrrrr
.qqqqqyyqqqqq.
.rrrrryyrrrrr.
.rrrrryyrrrrr.
.rrrrryyrrrrr.
.rrrrryyrrrrr.
.rrrrryyrrrrr.
""")


@draw("book")
def _book(p):
    p.stamp(0, 0, """
rrbbbbbbbbbb
rrbCCCCCCCCm
rrbCbbbbbbCm
rrbCCCCCCCCm
rrbCbbbbbCCm
rrbCCCCCCCCm
rrbCbbbbbbCm
rrbCCCCCCCCm
rrbCCCCCCCCm
rrbmmmmmmmmm
""")


@draw("wallet")
def _wallet(p):
    p.stamp(5, 0, """
.yyyy.
yyYYyy
yyzzyy
.yyyy.
""")
    p.stamp(0, 4, """
wwwwwwwwwwww
wwwwwwwwwwww
wxxxxxxxxxxw
wwwwwwwwwyyw
wwwwwwwwwyyw
wwwwwwwwwwww
wxxxxxxxxxxw
""")


@draw("crown")
def _crown(p):
    p.stamp(0, 0, """
y....yy....y
yy..yyyy..yy
yyy.yyyy.yyy
yyyyyyyyyyyy
yyyyyyyyyyyy
yyyyyyyyyyyy
yzzzzzzzzzzy
""")
    p.put(5, 4, "r")
    p.put(6, 4, "r")
    p.put(3, 5, "b")
    p.put(8, 5, "b")


@draw("send")
def _send(p):
    p.disc(5, 5, 4.6, 4.6, "Yyyz")
    p.stamp(0, 9, """
...........g..
............gg
gggggggggggggg
............gg
...........g..
""")


# ---------------------------------------------------------------- logs

@draw("radar")
def _radar(p):
    p.disc(7, 7, 6.9, 6.9, "dddd")
    p.ring(7, 7, 6.2, 5.2, "g")
    p.line(7, 2, 7, 12, "h")
    p.line(2, 7, 12, 7, "h")
    p.line(7, 7, 11, 3, "G")
    p.line(7, 8, 11, 4, "G")
    p.put(9, 9, "r")
    p.put(4, 4, "r")
    p.put(4, 10, "r")


@draw("clock")
def _clock(p):
    p.disc(7, 7, 6.4, 6.4, "CCCm")
    p.ring(7, 7, 6.4, 5.1, "b")
    p.line(7, 7, 7, 3, "d")
    p.line(7, 7, 10, 9, "d")
    p.put(7, 7, "d")


@draw("gauge")
def _gauge(p):
    for y in range(14):
        for x in range(14):
            dx, dy = x + 0.5 - 7, y + 0.5 - 10.5
            d = math.hypot(dx, dy)
            if d <= 6.9 and dy <= 0.5:
                if d < 4.2:
                    p.put(x, y, "C")
                else:
                    a = math.degrees(math.atan2(dy, dx))
                    p.put(x, y, "r" if a > -60 else ("y" if a > -120 else "g"))
    p.line(7, 9, 10, 4, "d")
    p.rect(6, 9, 8, 10, "d")
    p.rect(0, 11, 13, 11, "t")


@draw("info")
def _info(p):
    p.disc(7, 7, 6.5, 6.5, "Bbcc")
    p.rect(6, 6, 7, 10, "#")
    p.rect(6, 3, 7, 4, "#")


art("gear", """
.....ss.....
..s.ssss.s..
..ssssssss..
.ssssssssss.
sssss..sssss
ssss....ssss
ssss....ssss
sssss..sssss
.ssssssssss.
..ssssssss..
..s.ssss.s..
.....ss.....
""")


@draw("form")
def _form(p):
    p.stamp(0, 0, """
CCCCCCCCCm
CbbbbbbbCm
CCCCCCCCCm
CbbbbbbbCm
CCCCCCCCCm
CbbbbbbbCm
CCCCCCCCCm
CbbbbCCCCm
CCCCCCCCCm
mmmmmmmmmm
""")
    p.line(13, 1, 7, 8, "y", thick=2)
    p.put(6, 9, "d")
    p.put(7, 9, "d")


art("schem", """
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
CbbbbbbbbbbbbC
""")


@draw("schem")
def _schem(p):
    p.stamp(0, 0, ART["schem"])
    for x in range(2, 12, 3):
        for y in range(0, 9):
            if p.get(x, y) == "b":
                p.put(x, y, "B")
    for y in (2, 5):
        for x in range(1, 13):
            if p.get(x, y) in ("b", "B"):
                p.put(x, y, "B")
    p.stamp(4, 1, """
..##..
.####.
######
##bb##
##bb##
""")


@draw("brush")
def _brush(p):
    p.line(13, 0, 6, 7, "w", thick=2)
    p.poly([(5, 6), (8, 9), (4, 13), (1, 13), (0, 10)], "r")
    p.poly([(5, 6), (8, 9), (7, 10), (4, 7)], "s")
    p.rect(11, 10, 13, 13, "b")


@draw("pickaxe")
def _pickaxe(p):
    # The handle runs up the diagonal; the head is an arc centred on that diagonal, so both tips
    # curve back toward the handle (Minecraft's pickaxe).
    p.line(0, 13, 9, 4, "w", thick=2)
    cx, cy, R = 5.3, 8.7, 7.4
    for y in range(14):
        for x in range(14):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            ang = math.degrees(math.atan2(dy, dx))
            off = abs(((ang + 45 + 180) % 360) - 180)  # distance from the axis, degrees
            if off <= 74:
                half = 1.7 - 0.8 * (off / 74) ** 2
                if abs(math.hypot(dx, dy) - R) <= half:
                    p.put(x, y, "s")


@draw("axe")
def _axe(p):
    p.line(0, 13, 10, 3, "w", thick=2)
    hx, hy = 10.5, 3.5
    for y in range(14):
        for x in range(14):
            dx, dy = x + 0.5 - hx, y + 0.5 - hy
            d = math.hypot(dx, dy)
            ang = math.degrees(math.atan2(dy, dx)) % 360
            if d <= 7.2 and 168 <= ang <= 282 and d >= 1.5:
                p.put(x, y, "s")
    # the flat back of the head, opposite the blade
    p.rect(11, 3, 13, 6, "t")


@draw("wand")
def _wand(p):
    p.line(0, 13, 8, 5, "d", thick=2)
    p.stamp(7, 0, """
...yy...
...yy...
yyyyyyyy
.yyyyyy.
..yyyy..
.yy..yy.
yy....yy
""")


@draw("eye")
def _eye(p):
    p.stamp(0, 0, """
....######....
..##########..
.############.
##############
##############
.############.
..ssssssssss..
....ssssss....
""")
    p.disc(7, 3.7, 3.1, 3.1, "BbcC", only={"#", "s"})
    p.rect(6, 3, 7, 4, "d")
    p.put(5, 2, "#")


@draw("dotted")
def _dotted(p):
    for a, b in (((7, 0), (13, 3)), ((13, 3), (13, 10)), ((13, 10), (7, 13)), ((7, 13), (0, 10)), ((0, 10), (0, 3)), ((0, 3), (7, 0)),
                 ((7, 6), (0, 3)), ((7, 6), (13, 3)), ((7, 6), (7, 13))):
        p.line(a[0], a[1], b[0], b[1], "B")
    for v in ((7, 0), (13, 3), (13, 10), (7, 13), (0, 10), (0, 3), (7, 6)):
        p.rect(v[0], v[1], v[0] + 1, v[1] + 1, "#") if v[0] < 13 else p.rect(v[0] - 0, v[1], v[0], v[1] + 1, "#")


ALIAS = {
    "prev": "back", "coin": "coins", "price": "tag", "help": "book", "balance": "wallet", "top": "crown", "pay": "send",
    "inspect": "magnifier", "near": "radar", "rollback": "clock", "status": "gauge", "tools": "gear", "pick": "pickaxe",
    "blueprint": "schem", "preview": "eye", "outline": "dotted", "load": "folder", "auction": "gavel", "regen": "crystal",
    "size": "ruler", "chunk": "grid", "clear": "eraser", "stall": "market", "globe": "world", "mountain": "terrain",
}


def render(name, scale=1):
    """The finished icon, 16x16 times `scale`, or None if there is no hand-drawn version."""
    name = ALIAS.get(name, name)
    if name in DRAW:
        p = Pix()
        DRAW[name](p)
    elif name in ART:
        p = Pix()
        p.stamp(0, 0, ART[name])
    else:
        return None
    img = finish(p)
    if scale > 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    return img


def names():
    return sorted(set(ART) | set(DRAW))
