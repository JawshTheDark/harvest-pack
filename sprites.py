"""The illustrations on the menu tiles. Each is drawn in unit coordinates, so the same drawing
works at any size; `pxl.Cv` draws it large, shrinks it for clean edges, shades and outlines it.

Light comes from the top left. Arrows point the way the action goes (undo curls to the left,
redo to the right, rotate goes clockwise)."""
import math

from pxl import Cv

WOOD = (180, 120, 62)
WOODD = (124, 78, 40)
STEEL = (208, 216, 230)
STEELD = (140, 152, 172)
GOLD = (255, 208, 64)
GOLDD = (224, 150, 30)
RED = (234, 70, 60)
BLUE = (70, 142, 238)
BLUED = (44, 92, 180)
GREEN = (90, 198, 94)
GREEND = (54, 142, 68)
PURPLE = (156, 104, 232)
WHITE = (250, 250, 246)
PAPER = (246, 232, 188)
BROWN = (124, 82, 54)
STONE = (154, 160, 172)
STONED = (104, 110, 126)
SKY = (150, 212, 255)
PINK = (250, 142, 192)
ORANGE = (252, 152, 52)
TEAL = (60, 192, 192)
DARK = (46, 40, 62)
CREAM = (255, 244, 214)

SPRITES = {}


def sprite(*names):
    def deco(fn):
        for n in names:
            SPRITES[n] = fn
        return fn
    return deco


def circ(cx, cy, r):
    return ("e", (cx - r, cy - r, cx + r, cy + r))


def rot_rect(cx, cy, w, h, deg):
    """A rectangle of size w x h centred on (cx, cy), turned by `deg` (clockwise on screen)."""
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    return ("p", pts)


def arrow(x0, y0, x1, y1, w=0.12, head=0.22):
    """Prims for a straight arrow from (x0, y0) to (x1, y1)."""
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    bx, by = x1 - ux * head, y1 - uy * head
    px, py = -uy, ux
    return [("l", (x0, y0, bx + ux * 0.02, by + uy * 0.02, w)), ("p", [(x1, y1), (bx + px * head * 0.7, by + py * head * 0.7), (bx - px * head * 0.7, by - py * head * 0.7)])]


def dome(cx, cy, rx, ry):
    """The top half of an ellipse as a polygon."""
    return ("p", [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in range(180, 361, 6)])


# ---------------------------------------------------------------- hubs

@sprite("builder")
def _builder(c):
    c.add(WOODD, ("l", (0.30, 0.92, 0.76, 0.38, 0.12)))
    c.add(STEEL, rot_rect(0.76, 0.26, 0.50, 0.24, 45))
    c.add(STEELD, rot_rect(0.64, 0.38, 0.12, 0.24, 45), ol=False)
    c.add(GOLD, dome(0.34, 0.80, 0.28, 0.40), rnd=True)
    c.add(GOLDD, ("r", (0.04, 0.74, 0.66, 0.87)))
    c.add(WHITE, ("r", (0.30, 0.46, 0.38, 0.74)), ol=False, shade=False)


@sprite("market", "stall")
def _market(c):
    c.add(WOODD, ("r", (0.14, 0.34, 0.20, 0.90)), ("r", (0.80, 0.34, 0.86, 0.90)))
    for i in range(5):
        c.add(RED if i % 2 == 0 else WHITE, ("r", (0.10 + 0.16 * i, 0.14, 0.26 + 0.16 * i, 0.38)), ("e", (0.10 + 0.16 * i, 0.30, 0.26 + 0.16 * i, 0.46)))
    c.add(WOOD, ("r", (0.12, 0.64, 0.88, 0.92)))
    c.add(WOODD, ("r", (0.12, 0.64, 0.88, 0.70)))
    c.add(RED, circ(0.30, 0.57, 0.07), rnd=True)
    c.add(GREEN, circ(0.46, 0.58, 0.065), rnd=True)
    c.add(GOLD, circ(0.64, 0.57, 0.07), rnd=True)
    c.add(ORANGE, circ(0.78, 0.58, 0.06), rnd=True)


@sprite("coins", "coin")
def _coins(c):
    for k in range(3):
        y = 0.90 - k * 0.12
        c.add(GOLDD, ("r", (0.08, y - 0.10, 0.44, y)), ("e", (0.08, y - 0.06, 0.44, y + 0.04)))
        c.add(GOLD, ("e", (0.08, y - 0.16, 0.44, y - 0.04)))
    c.add(GOLDD, circ(0.64, 0.46, 0.30), rnd=True)
    c.add(GOLD, circ(0.64, 0.46, 0.23), rnd=True)
    c.add(GOLDD, ("p", [(0.64, 0.30), (0.78, 0.46), (0.64, 0.62), (0.50, 0.46)]), ol=False, shade=False)


@sprite("logbook")
def _logbook(c):
    c.add(BLUED, ("r", (0.08, 0.10, 0.66, 0.90)))
    c.add(BLUE, ("r", (0.14, 0.10, 0.66, 0.86)))
    c.add(WHITE, ("r", (0.62, 0.14, 0.72, 0.84)))
    c.add(GOLD, ("r", (0.22, 0.24, 0.52, 0.31)), ("r", (0.22, 0.38, 0.46, 0.45)), ol=False)
    c.add(WOODD, ("l", (0.80, 0.78, 0.93, 0.92, 0.10)))
    c.add(STEELD, ("a", (0.42, 0.34, 0.90, 0.82, 0, 360, 0.09)))
    c.add(SKY, circ(0.66, 0.58, 0.20), rnd=True)
    c.add(WHITE, ("p", [(0.54, 0.50), (0.60, 0.46), (0.58, 0.52)]), ol=False, shade=False)


@sprite("world", "globe")
def _world(c):
    c.add(BLUE, circ(0.5, 0.46, 0.38), rnd=True)
    c.add(GREEN, ("p", [(0.26, 0.28), (0.44, 0.18), (0.52, 0.34), (0.42, 0.50), (0.28, 0.46)]))
    c.add(GREEN, ("p", [(0.58, 0.48), (0.76, 0.40), (0.82, 0.58), (0.66, 0.72), (0.56, 0.62)]))
    c.add(WOODD, ("r", (0.34, 0.86, 0.66, 0.94)), ("r", (0.45, 0.80, 0.55, 0.88)))


# ---------------------------------------------------------------- selection and shapes

@sprite("select")
def _select(c):
    for i in range(6):
        t = 0.12 + i * 0.15
        c.add(GOLD, ("r", (t, 0.12, t + 0.09, 0.20)), ("r", (t, 0.72, t + 0.09, 0.80)), ol=False)
        c.add(GOLD, ("r", (0.12, t, 0.20, t + 0.09)), ("r", (0.80, t, 0.88, t + 0.09)), ol=False)
    c.add(WHITE, ("p", [(0.46, 0.38), (0.46, 0.92), (0.60, 0.80), (0.70, 0.98), (0.80, 0.93), (0.70, 0.76), (0.88, 0.76)]))


@sprite("shapes")
def _shapes(c):
    c.add(ORANGE, ("p", [(0.5, 0.08), (0.88, 0.28), (0.5, 0.48), (0.12, 0.28)]))
    c.add(RED, ("p", [(0.12, 0.28), (0.5, 0.48), (0.5, 0.92), (0.12, 0.72)]))
    c.add((190, 50, 44), ("p", [(0.88, 0.28), (0.5, 0.48), (0.5, 0.92), (0.88, 0.72)]))


@sprite("cube")
def _cube(c):
    c.add((130, 200, 250), ("p", [(0.5, 0.08), (0.88, 0.28), (0.5, 0.48), (0.12, 0.28)]))
    c.add(BLUE, ("p", [(0.12, 0.28), (0.5, 0.48), (0.5, 0.92), (0.12, 0.72)]))
    c.add(BLUED, ("p", [(0.88, 0.28), (0.5, 0.48), (0.5, 0.92), (0.88, 0.72)]))


@sprite("sphere")
def _sphere(c):
    c.add(PURPLE, circ(0.5, 0.5, 0.40), rnd=True)
    c.add((222, 200, 255), circ(0.36, 0.34, 0.07), ol=False, shade=False)


@sprite("ellipsoid")
def _ellipsoid(c):
    c.add(PURPLE, ("e", (0.04, 0.24, 0.96, 0.76)), rnd=True)
    c.add((222, 200, 255), ("e", (0.18, 0.32, 0.38, 0.42)), ol=False, shade=False)


@sprite("cylinder")
def _cylinder(c):
    c.add(GREEND, ("r", (0.2, 0.26, 0.8, 0.76)), ("e", (0.2, 0.62, 0.8, 0.90)))
    c.add(GREEN, ("r", (0.28, 0.30, 0.38, 0.78)), ol=False, shade=False)
    c.add(GREEN, ("e", (0.2, 0.12, 0.8, 0.40)), rnd=True)


@sprite("pyramid")
def _pyramid(c):
    c.add((250, 220, 110), ("p", [(0.5, 0.08), (0.10, 0.76), (0.5, 0.92)]))
    c.add((226, 170, 60), ("p", [(0.5, 0.08), (0.5, 0.92), (0.92, 0.72)]))


@sprite("polygon")
def _polygon(c):
    pts = [(0.5, 0.10), (0.90, 0.40), (0.74, 0.88), (0.26, 0.88), (0.10, 0.40)]
    c.add(TEAL, ("p", pts))
    for x, y in pts:
        c.add(WHITE, circ(x, y, 0.07), ol=False)


@sprite("grid", "chunk")
def _grid(c):
    for i in range(3):
        for j in range(3):
            col = GOLD if (i, j) == (1, 1) else STONE
            c.add(col, ("r", (0.08 + i * 0.30, 0.08 + j * 0.30, 0.08 + i * 0.30 + 0.26, 0.08 + j * 0.30 + 0.26)), ol=False)


@sprite("ruler", "size")
def _ruler(c):
    c.add(GOLD, ("r", (0.06, 0.32, 0.94, 0.70)))
    for i in range(9):
        x = 0.12 + 0.092 * i
        c.add(DARK, ("r", (x, 0.32, x + 0.035, 0.32 + (0.20 if i % 2 == 0 else 0.12))), ol=False, shade=False)


@sprite("expand")
def _expand(c):
    c.add(STONE, ("r", (0.36, 0.36, 0.64, 0.64)))
    for a in ((0.5, 0.32, 0.5, 0.06), (0.5, 0.68, 0.5, 0.94), (0.32, 0.5, 0.06, 0.5), (0.68, 0.5, 0.94, 0.5)):
        c.add(GREEN, *arrow(*a, w=0.10, head=0.18))


@sprite("eraser", "clear")
def _eraser(c):
    c.add(PINK, rot_rect(0.46, 0.50, 0.70, 0.34, -40))
    c.add(WHITE, rot_rect(0.66, 0.34, 0.30, 0.34, -40))
    c.add(STEELD, ("r", (0.14, 0.90, 0.86, 0.95)), ol=False, shade=False)


# ---------------------------------------------------------------- terrain and nature

@sprite("tree")
def _tree(c):
    c.add(WOODD, ("r", (0.43, 0.56, 0.57, 0.92)))
    c.add(GREEND, circ(0.5, 0.38, 0.32), rnd=True)
    c.add(GREEN, circ(0.40, 0.30, 0.20), circ(0.62, 0.36, 0.20), rnd=True)


@sprite("sapling")
def _sapling(c):
    c.add(WOODD, ("r", (0.46, 0.5, 0.54, 0.9)))
    c.add(GREEN, ("p", [(0.5, 0.52), (0.12, 0.42), (0.28, 0.12), (0.5, 0.28)]))
    c.add(GREEND, ("p", [(0.5, 0.52), (0.88, 0.42), (0.72, 0.12), (0.5, 0.28)]))


@sprite("flower")
def _flower(c):
    c.add(GREEND, ("r", (0.46, 0.5, 0.54, 0.92)), ("p", [(0.5, 0.74), (0.76, 0.62), (0.70, 0.82)]))
    for x, y in [(0.5, 0.20), (0.76, 0.36), (0.66, 0.64), (0.34, 0.64), (0.24, 0.36)]:
        c.add(PINK, circ(x, y, 0.16), rnd=True)
    c.add(GOLD, circ(0.5, 0.44, 0.12), rnd=True)


@sprite("terrain", "mountain")
def _terrain(c):
    c.add(STONED, ("p", [(0.04, 0.88), (0.38, 0.18), (0.72, 0.88)]))
    c.add(STONE, ("p", [(0.40, 0.88), (0.68, 0.34), (0.96, 0.88)]))
    c.add(WHITE, ("p", [(0.38, 0.18), (0.27, 0.42), (0.37, 0.38), (0.46, 0.46), (0.50, 0.36)]))
    c.add(GREEN, circ(0.22, 0.80, 0.11), circ(0.82, 0.82, 0.09), rnd=True)


@sprite("flame", "fire")
def _flame(c):
    c.add(RED, ("p", [(0.5, 0.06), (0.80, 0.46), (0.84, 0.72), (0.62, 0.94), (0.38, 0.94), (0.16, 0.72), (0.22, 0.44), (0.40, 0.52)]))
    c.add(ORANGE, ("p", [(0.5, 0.34), (0.68, 0.64), (0.62, 0.88), (0.38, 0.88), (0.32, 0.64)]))
    c.add(GOLD, ("p", [(0.5, 0.58), (0.58, 0.76), (0.5, 0.88), (0.42, 0.76)]))


@sprite("drop", "water")
def _drop(c):
    c.add(BLUE, ("e", (0.2, 0.4, 0.8, 0.94)), ("p", [(0.5, 0.06), (0.78, 0.56), (0.22, 0.56)]), rnd=True)
    c.add(SKY, circ(0.38, 0.66, 0.07), ol=False, shade=False)


@sprite("snow")
def _snow(c):
    for ang in (0, 60, 120):
        a = math.radians(ang)
        c.add(SKY, ("l", (0.5 - math.cos(a) * 0.40, 0.5 - math.sin(a) * 0.40, 0.5 + math.cos(a) * 0.40, 0.5 + math.sin(a) * 0.40, 0.09)))
    c.add(WHITE, circ(0.5, 0.5, 0.10), rnd=True)


@sprite("bucket")
def _bucket(c):
    c.add(STEELD, ("a", (0.22, 0.04, 0.78, 0.70, 180, 360, 0.06)), ol=False, shade=False)
    c.add(STEEL, ("p", [(0.18, 0.34), (0.82, 0.34), (0.72, 0.90), (0.28, 0.90)]))
    c.add(BLUE, ("r", (0.20, 0.34, 0.80, 0.46)))


@sprite("up")
def _up(c):
    c.add(STONE, ("r", (0.18, 0.74, 0.82, 0.92)))
    c.add(ORANGE, *arrow(0.5, 0.66, 0.5, 0.06, w=0.22, head=0.34))


@sprite("down")
def _down(c):
    c.add(STONE, ("r", (0.18, 0.08, 0.82, 0.26)))
    c.add(ORANGE, *arrow(0.5, 0.34, 0.5, 0.94, w=0.22, head=0.34))


@sprite("crystal", "regen")
def _crystal(c):
    c.add(PURPLE, ("p", [(0.5, 0.06), (0.80, 0.34), (0.66, 0.92), (0.34, 0.92), (0.20, 0.34)]))
    c.add((200, 160, 255), ("p", [(0.5, 0.06), (0.20, 0.34), (0.5, 0.40)]), ol=False)
    c.add((120, 70, 190), ("p", [(0.5, 0.40), (0.80, 0.34), (0.66, 0.92), (0.5, 0.92)]), ol=False)


# ---------------------------------------------------------------- clipboard

@sprite("copy")
def _copy(c):
    c.add(STEEL, ("r", (0.10, 0.08, 0.60, 0.72)))
    c.add(WHITE, ("r", (0.38, 0.28, 0.90, 0.94)))
    for y in (0.42, 0.56, 0.70):
        c.add(BLUE, ("r", (0.46, y, 0.80 if y < 0.7 else 0.70, y + 0.06)), ol=False, shade=False)


@sprite("clipboard")
def _clipboard(c):
    c.add(WOOD, ("r", (0.16, 0.12, 0.84, 0.92)))
    c.add(PAPER, ("r", (0.24, 0.22, 0.76, 0.84)))
    c.add(STEEL, ("r", (0.36, 0.06, 0.64, 0.20)))
    for i in range(4):
        c.add(BLUED, ("r", (0.30, 0.34 + i * 0.12, 0.70 - (i % 2) * 0.16, 0.39 + i * 0.12)), ol=False, shade=False)


@sprite("paste")
def _paste(c):
    _clipboard(c)
    c.add(GREEN, *arrow(0.5, 0.40, 0.5, 0.88, w=0.15, head=0.24))


@sprite("scissors")
def _scissors(c):
    c.add(STEEL, ("l", (0.30, 0.10, 0.72, 0.66, 0.11)), ("l", (0.70, 0.10, 0.28, 0.66, 0.11)))
    c.add(RED, ("a", (0.06, 0.56, 0.40, 0.94, 0, 360, 0.10)), ("a", (0.60, 0.56, 0.94, 0.94, 0, 360, 0.10)))
    c.add(STEELD, circ(0.5, 0.40, 0.05), ol=False, shade=False)


@sprite("rotate")
def _rotate(c):
    c.add(BLUE, ("A", (0.5, 0.52, 0.31, -25, 250, 0.17, 0.34)))


@sprite("flip")
def _flip(c):
    c.add(TEAL, ("p", [(0.06, 0.22), (0.06, 0.78), (0.42, 0.50)]))
    c.add(GOLD, ("p", [(0.94, 0.22), (0.94, 0.78), (0.58, 0.50)]))
    for k in range(5):
        c.add(WHITE, ("r", (0.47, 0.08 + k * 0.18, 0.53, 0.18 + k * 0.18)), ol=False, shade=False)


@sprite("trash")
def _trash(c):
    c.add(STEEL, ("p", [(0.22, 0.30), (0.78, 0.30), (0.72, 0.92), (0.28, 0.92)]))
    c.add(STEELD, ("r", (0.38, 0.40, 0.43, 0.84)), ("r", (0.57, 0.40, 0.62, 0.84)), ol=False)
    c.add(STONE, ("r", (0.14, 0.20, 0.86, 0.30)), ("r", (0.40, 0.10, 0.60, 0.20)))


@sprite("disk", "save")
def _disk(c):
    c.add(BLUE, ("r", (0.12, 0.12, 0.88, 0.88)))
    c.add(STEEL, ("r", (0.28, 0.12, 0.72, 0.40)))
    c.add(WHITE, ("r", (0.24, 0.52, 0.76, 0.88)))
    c.add(DARK, ("r", (0.58, 0.16, 0.66, 0.34)), ol=False)


@sprite("folder", "load")
def _folder(c):
    c.add(GOLDD, ("r", (0.10, 0.20, 0.50, 0.36)))
    c.add(GOLD, ("r", (0.10, 0.32, 0.90, 0.84)))
    c.add(PAPER, ("r", (0.18, 0.28, 0.82, 0.40)), ol=False)


# ---------------------------------------------------------------- shops and money

@sprite("gavel", "auction")
def _gavel(c):
    c.add(WOODD, ("l", (0.14, 0.82, 0.58, 0.40, 0.11)))
    c.add(WOOD, rot_rect(0.62, 0.34, 0.50, 0.26, 45))
    c.add(WOODD, rot_rect(0.50, 0.46, 0.08, 0.26, 45), rot_rect(0.74, 0.22, 0.08, 0.26, 45), ol=False)
    c.add(WOODD, ("r", (0.38, 0.80, 0.94, 0.94)))
    c.add(STEEL, ("r", (0.38, 0.74, 0.94, 0.80)))


@sprite("chest")
def _chest(c):
    c.add(WOODD, ("r", (0.10, 0.34, 0.90, 0.88)))
    c.add(WOOD, ("p", [(0.10, 0.34), (0.90, 0.34), (0.84, 0.14), (0.16, 0.14)]))
    c.add(GOLD, ("r", (0.10, 0.40, 0.90, 0.50)), ("r", (0.44, 0.38, 0.56, 0.62)))
    c.add(GOLDD, ("r", (0.47, 0.50, 0.53, 0.56)), ol=False)


@sprite("tag", "price")
def _tag(c):
    c.add(GOLD, ("p", [(0.10, 0.50), (0.50, 0.10), (0.92, 0.10), (0.92, 0.52), (0.50, 0.92)]))
    c.add(DARK, circ(0.74, 0.28, 0.065), ol=False, shade=False)
    c.add(GOLDD, circ(0.52, 0.48, 0.14), ol=False, shade=False)
    c.add(GOLD, circ(0.52, 0.48, 0.09), ol=False, shade=False)


@sprite("gift")
def _gift(c):
    c.add(RED, ("r", (0.14, 0.40, 0.86, 0.90)))
    c.add((250, 100, 90), ("r", (0.10, 0.28, 0.90, 0.44)))
    c.add(GOLD, ("r", (0.44, 0.28, 0.56, 0.90)))
    c.add(GOLD, circ(0.38, 0.20, 0.10), circ(0.62, 0.20, 0.10), rnd=True)


@sprite("book", "help")
def _book(c):
    c.add(BROWN, ("r", (0.16, 0.10, 0.84, 0.90)))
    c.add(PAPER, ("r", (0.22, 0.14, 0.82, 0.86)))
    c.add(RED, ("r", (0.10, 0.10, 0.24, 0.90)))
    c.add(BLUED, ("r", (0.34, 0.28, 0.70, 0.34)), ("r", (0.34, 0.44, 0.62, 0.50)), ("r", (0.34, 0.60, 0.70, 0.66)), ol=False, shade=False)


@sprite("wallet", "balance")
def _wallet(c):
    c.add(GOLD, circ(0.64, 0.30, 0.20), rnd=True)
    c.add(GOLDD, circ(0.64, 0.30, 0.12), ol=False, rnd=True)
    c.add(BROWN, ("r", (0.10, 0.40, 0.90, 0.88)))
    c.add((156, 106, 70), ("r", (0.10, 0.40, 0.90, 0.50)))
    c.add(GOLD, circ(0.76, 0.66, 0.08), rnd=True)


@sprite("crown", "top")
def _crown(c):
    c.add(GOLD, ("p", [(0.10, 0.80), (0.10, 0.28), (0.32, 0.50), (0.50, 0.16), (0.68, 0.50), (0.90, 0.28), (0.90, 0.80)]))
    c.add(GOLDD, ("r", (0.10, 0.72, 0.90, 0.86)))
    c.add(RED, circ(0.50, 0.58, 0.07), rnd=True)
    c.add(BLUE, circ(0.26, 0.64, 0.05), circ(0.74, 0.64, 0.05), rnd=True)


@sprite("send", "pay")
def _send(c):
    c.add(GOLD, circ(0.34, 0.40, 0.26), rnd=True)
    c.add(GOLDD, circ(0.34, 0.40, 0.16), ol=False, rnd=True)
    c.add(GREEN, *arrow(0.10, 0.80, 0.90, 0.80, w=0.13, head=0.24))


# ---------------------------------------------------------------- logs

@sprite("magnifier", "inspect")
def _magnifier(c):
    c.add(WOODD, ("l", (0.90, 0.90, 0.58, 0.58, 0.14)))
    c.add(STEELD, ("a", (0.06, 0.06, 0.72, 0.72, 0, 360, 0.11)))
    c.add(SKY, circ(0.39, 0.39, 0.25), rnd=True)
    c.add(WHITE, ("p", [(0.26, 0.34), (0.32, 0.26), (0.36, 0.30), (0.30, 0.38)]), ol=False, shade=False)


@sprite("radar", "near")
def _radar(c):
    c.add(DARK, circ(0.5, 0.5, 0.42), rnd=True)
    c.add(GREEN, ("a", (0.12, 0.12, 0.88, 0.88, 0, 360, 0.05)), ("a", (0.30, 0.30, 0.70, 0.70, 0, 360, 0.05)), ol=False, shade=False)
    c.add(GREEN, ("l", (0.5, 0.5, 0.78, 0.24, 0.06)), ol=False, shade=False)
    c.add(RED, circ(0.68, 0.64, 0.06), circ(0.34, 0.36, 0.06), ol=False)


@sprite("clock", "rollback")
def _clock(c):
    c.add(CREAM, circ(0.5, 0.5, 0.29), rnd=True)
    c.add(BLUED, ("a", (0.21, 0.21, 0.79, 0.79, 0, 360, 0.06)), ol=False, shade=False)
    c.add(DARK, ("l", (0.5, 0.5, 0.5, 0.32, 0.055)), ("l", (0.5, 0.5, 0.63, 0.57, 0.055)), ol=False, shade=False)
    c.add(GREEN, ("A", (0.5, 0.5, 0.41, -15, -255, 0.10, 0.26)))


@sprite("gauge", "status")
def _gauge(c):
    c.add(CREAM, ("p", [(0.5 + 0.44 * math.cos(math.radians(a)), 0.72 + 0.44 * math.sin(math.radians(a))) for a in range(180, 361, 6)] + [(0.94, 0.88), (0.06, 0.88)]))
    c.add(GREEN, ("a", (0.14, 0.36, 0.86, 1.08, 185, 240, 0.12)), ol=False, shade=False)
    c.add(GOLD, ("a", (0.14, 0.36, 0.86, 1.08, 240, 300, 0.12)), ol=False, shade=False)
    c.add(RED, ("a", (0.14, 0.36, 0.86, 1.08, 300, 355, 0.12)), ol=False, shade=False)
    c.add(DARK, ("l", (0.5, 0.72, 0.68, 0.42, 0.07)), circ(0.5, 0.72, 0.075), ol=False, shade=False)


@sprite("back", "prev")
def _back(c):
    c.add(GOLD, ("p", [(0.06, 0.5), (0.46, 0.10), (0.46, 0.34), (0.94, 0.34), (0.94, 0.66), (0.46, 0.66), (0.46, 0.90)]))


@sprite("next")
def _next(c):
    c.add(GOLD, ("p", [(0.94, 0.5), (0.54, 0.10), (0.54, 0.34), (0.06, 0.34), (0.06, 0.66), (0.54, 0.66), (0.54, 0.90)]))


@sprite("close")
def _close(c):
    c.add(RED, ("l", (0.18, 0.18, 0.82, 0.82, 0.20)), ("l", (0.82, 0.18, 0.18, 0.82, 0.20)))


@sprite("check")
def _check(c):
    c.add(GREEN, ("l", (0.14, 0.54, 0.40, 0.80, 0.18)), ("l", (0.40, 0.80, 0.88, 0.22, 0.18)))


@sprite("form")
def _form(c):
    c.add(PAPER, ("r", (0.14, 0.08, 0.76, 0.92)))
    for i in range(4):
        c.add(BLUED, ("r", (0.22, 0.22 + i * 0.16, 0.68, 0.28 + i * 0.16)), ol=False, shade=False)
    c.add(GOLD, ("l", (0.90, 0.18, 0.52, 0.72, 0.11)))
    c.add(DARK, ("p", [(0.50, 0.78), (0.46, 0.94), (0.62, 0.84)]), ol=False)


@sprite("info")
def _info(c):
    c.add(BLUE, circ(0.5, 0.5, 0.40), rnd=True)
    c.add(WHITE, ("r", (0.44, 0.42, 0.56, 0.74)), circ(0.5, 0.28, 0.075), ol=False, shade=False)


@sprite("skull", "butcher")
def _skull(c):
    c.add(WHITE, circ(0.5, 0.42, 0.34), ("r", (0.30, 0.55, 0.70, 0.88)), rnd=True)
    c.add(DARK, circ(0.36, 0.44, 0.09), circ(0.64, 0.44, 0.09), ("p", [(0.5, 0.56), (0.44, 0.68), (0.56, 0.68)]), ol=False, shade=False)
    for x in (0.38, 0.48, 0.58):
        c.add(DARK, ("r", (x, 0.78, x + 0.04, 0.88)), ol=False, shade=False)


@sprite("swap", "replace")
def _swap(c):
    c.add(BLUE, *arrow(0.10, 0.30, 0.90, 0.30, w=0.13, head=0.24))
    c.add(ORANGE, *arrow(0.90, 0.70, 0.10, 0.70, w=0.13, head=0.24))


@sprite("cycle")
def _cycle(c):
    c.add(GREEN, ("A", (0.5, 0.5, 0.32, 200, 335, 0.15, 0.27)))
    c.add(GREEN, ("A", (0.5, 0.5, 0.32, 20, 155, 0.15, 0.27)))


@sprite("gear", "tools")
def _gear(c):
    for k in range(4):
        c.add(STEELD, rot_rect(0.5, 0.5, 0.24, 0.90, k * 45), ol=False)
    c.add(STEEL, circ(0.5, 0.5, 0.31), rnd=True)
    c.add(DARK, circ(0.5, 0.5, 0.12), ol=False, shade=False)


@sprite("compass")
def _compass(c):
    c.add(STEEL, circ(0.5, 0.5, 0.40), rnd=True)
    c.add(RED, ("p", [(0.5, 0.14), (0.62, 0.5), (0.38, 0.5)]))
    c.add(WHITE, ("p", [(0.5, 0.86), (0.62, 0.5), (0.38, 0.5)]))
    c.add(DARK, circ(0.5, 0.5, 0.04), ol=False, shade=False)


# ---------------------------------------------------------------- tools

@sprite("pickaxe", "pick")
def _pickaxe(c):
    # The head is a crescent around a point down the handle, so its tips curve toward the grip.
    c.add(WOODD, ("l", (0.14, 0.90, 0.63, 0.37, 0.11)))
    c.add(STEEL, ("a", (-0.335, 0.145, 0.855, 1.335, -108, 18, 0.15)))


@sprite("axe")
def _axe(c):
    c.add(WOODD, ("l", (0.18, 0.90, 0.66, 0.30, 0.11)))
    c.add(STEEL, ("p", [(0.46, 0.10), (0.88, 0.14), (0.92, 0.58), (0.70, 0.44), (0.58, 0.40)]))
    c.add(STEELD, ("p", [(0.88, 0.14), (0.92, 0.58), (0.84, 0.50), (0.82, 0.18)]), ol=False)


@sprite("brush")
def _brush(c):
    c.add(WOODD, ("l", (0.92, 0.10, 0.46, 0.56, 0.11)))
    c.add(STEEL, ("p", [(0.38, 0.46), (0.54, 0.62), (0.44, 0.72), (0.28, 0.56)]))
    c.add(RED, ("p", [(0.28, 0.56), (0.44, 0.72), (0.22, 0.94), (0.06, 0.84)]))
    c.add(BLUE, circ(0.84, 0.80, 0.09), rnd=True)


@sprite("schem", "blueprint")
def _schem(c):
    c.add(BLUE, ("r", (0.10, 0.16, 0.90, 0.84)))
    for i in range(1, 4):
        c.add((150, 200, 255), ("r", (0.10 + 0.2 * i, 0.16, 0.12 + 0.2 * i, 0.84)), ("r", (0.10, 0.16 + 0.17 * i, 0.90, 0.18 + 0.17 * i)), ol=False, shade=False)
    c.add(WHITE, ("p", [(0.30, 0.64), (0.30, 0.42), (0.50, 0.28), (0.70, 0.42), (0.70, 0.64)]), ol=False, shade=False)
    c.add(PAPER, ("r", (0.06, 0.10, 0.14, 0.90)), ("r", (0.86, 0.10, 0.94, 0.90)))


@sprite("wand")
def _wand(c):
    c.add(DARK, ("l", (0.14, 0.90, 0.58, 0.42, 0.10)))
    c.add(GOLD, ("p", [(0.70, 0.06), (0.78, 0.26), (0.96, 0.30), (0.82, 0.44), (0.86, 0.64), (0.70, 0.54), (0.54, 0.64), (0.58, 0.44), (0.44, 0.30), (0.62, 0.26)]))
    c.dots(WHITE, [(0.24, 0.30), (0.12, 0.50), (0.34, 0.12)])


@sprite("undo")
def _undo(c):
    c.add(BLUE, ("A", (0.5, 0.60, 0.31, 20, -165, 0.17, 0.30)))


@sprite("redo")
def _redo(c):
    c.add(GREEN, ("A", (0.5, 0.60, 0.31, 160, 345, 0.17, 0.30)))


@sprite("eye", "preview")
def _eye(c):
    c.add(WHITE, ("e", (0.04, 0.26, 0.96, 0.74)))
    c.add(BLUE, circ(0.5, 0.5, 0.21), rnd=True)
    c.add(DARK, circ(0.5, 0.5, 0.10), ol=False, shade=False)
    c.add(WHITE, circ(0.44, 0.44, 0.045), ol=False, shade=False)


@sprite("dotted", "outline")
def _dotted(c):
    hexa = [(0.5, 0.08), (0.88, 0.28), (0.88, 0.72), (0.5, 0.92), (0.12, 0.72), (0.12, 0.28)]
    for i in range(6):
        (x0, y0), (x1, y1) = hexa[i], hexa[(i + 1) % 6]
        c.add(SKY, ("l", (x0, y0, x1, y1, 0.07)), ol=False, shade=False)
    c.add(SKY, ("l", (0.5, 0.48, 0.12, 0.28, 0.06)), ("l", (0.5, 0.48, 0.88, 0.28, 0.06)), ("l", (0.5, 0.48, 0.5, 0.92, 0.06)), ol=False, shade=False)


@sprite("star")
def _star(c):
    c.add(GOLD, ("p", [(0.5, 0.06), (0.62, 0.36), (0.94, 0.38), (0.70, 0.58), (0.78, 0.92), (0.5, 0.74), (0.22, 0.92), (0.30, 0.58), (0.06, 0.38), (0.38, 0.36)]))


@sprite("lock")
def _lock(c):
    c.add(STEELD, ("a", (0.26, 0.06, 0.74, 0.62, 180, 360, 0.11)))
    c.add(GOLD, ("r", (0.20, 0.42, 0.80, 0.90)))
    c.add(DARK, circ(0.5, 0.62, 0.07), ("r", (0.47, 0.64, 0.53, 0.78)), ol=False, shade=False)


@sprite("sword")
def _sword(c):
    c.add(STEEL, ("p", [(0.86, 0.06), (0.94, 0.14), (0.40, 0.68), (0.32, 0.60)]))
    c.add(GOLD, ("l", (0.22, 0.46, 0.54, 0.78, 0.10)))
    c.add(WOODD, ("l", (0.32, 0.70, 0.10, 0.92, 0.10)))


@sprite("hat")
def _hat(c):
    c.add(RED, ("e", (0.1, 0.1, 0.9, 0.7)), ("r", (0.1, 0.4, 0.9, 0.7)), rnd=True)
    c.add(WOODD, ("r", (0.06, 0.62, 0.94, 0.78)))
    c.add(GOLD, ("r", (0.1, 0.5, 0.9, 0.58)), ol=False)


def render(name, size):
    """The finished sprite as an RGBA image, `size`+4 pixels square (it carries its own outline)."""
    import os
    from PIL import Image
    mine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "art", name + ".png")
    if os.path.exists(mine):
        # A hand-made sprite replaces the generated one.
        return Image.open(mine).convert("RGBA").resize((size + 4, size + 4), Image.NEAREST)
    c = Cv(size)
    SPRITES.get(name, SPRITES["gear"])(c)
    return c.done()
