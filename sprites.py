"""The illustrations on the menu tiles. Each is drawn in unit coordinates, so the same drawing
works at any size, and shaded and outlined by `pxl.Cv`."""
import math

from pxl import Cv, draw_text

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


def arrow(c, x0, y0, x1, y1, color, w=0.12, head=0.2):
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    bx, by = x1 - ux * head, y1 - uy * head
    px, py = -uy, ux
    c.add(color, ("l", (x0, y0, bx, by, w)), ("p", [(x1, y1), (bx + px * head * 0.8, by + py * head * 0.8), (bx - px * head * 0.8, by - py * head * 0.8)]))


@sprite("builder")
def _builder(c):
    c.add(WOODD, ("l", (0.78, 0.84, 0.34, 0.3, 0.1)))
    c.add(WOOD, ("l", (0.22, 0.84, 0.66, 0.34, 0.1)))
    c.add(STEEL, ("p", [(0.1, 0.26), (0.38, 0.12), (0.46, 0.4), (0.2, 0.5)]))
    c.add(STEELD, ("p", [(0.1, 0.26), (0.16, 0.22), (0.22, 0.46), (0.2, 0.5)]))
    c.add(STEEL, ("p", [(0.52, 0.2), (0.78, 0.1), (0.92, 0.34), (0.66, 0.46)]))
    c.add(RED, ("r", (0.58, 0.7, 0.9, 0.9)))
    c.add(ORANGE, ("r", (0.12, 0.76, 0.44, 0.92)))


@sprite("market", "stall")
def _market(c):
    c.add(WOODD, ("r", (0.14, 0.34, 0.2, 0.9)), ("r", (0.8, 0.34, 0.86, 0.9)))
    for i in range(5):
        c.add(RED if i % 2 == 0 else WHITE, ("r", (0.1 + 0.16 * i, 0.14, 0.26 + 0.16 * i, 0.38)), ("e", (0.1 + 0.16 * i, 0.3, 0.26 + 0.16 * i, 0.46)))
    c.add(WOOD, ("r", (0.12, 0.64, 0.88, 0.92)))
    c.add(WOODD, ("r", (0.12, 0.64, 0.88, 0.7)))
    c.add(RED, circ(0.3, 0.57, 0.07))
    c.add(GREEN, circ(0.46, 0.58, 0.065))
    c.add(GOLD, circ(0.64, 0.57, 0.07))
    c.add(ORANGE, circ(0.78, 0.58, 0.06))


@sprite("coins", "coin")
def _coins(c):
    for i, (x, h) in enumerate([(0.1, 4), (0.64, 3)]):
        for k in range(h):
            y = 0.9 - k * 0.1
            c.add(GOLDD, ("r", (x, y - 0.12, x + 0.26, y)), ("e", (x, y - 0.06, x + 0.26, y + 0.04)))
            c.add(GOLD, ("e", (x, y - 0.18, x + 0.26, y - 0.06)))
    c.add(GOLDD, circ(0.5, 0.5, 0.26))
    c.add(GOLD, circ(0.5, 0.48, 0.23))
    c.add(GOLDD, ("r", (0.46, 0.34, 0.54, 0.62)))
    c.add(GOLD, ("r", (0.38, 0.4, 0.62, 0.46)), ("r", (0.38, 0.52, 0.62, 0.58)))


@sprite("logbook")
def _logbook(c):
    c.add(BLUED, ("r", (0.1, 0.14, 0.7, 0.88)))
    c.add(BLUE, ("r", (0.14, 0.14, 0.7, 0.84)))
    c.add(WHITE, ("r", (0.6, 0.18, 0.74, 0.82)))
    c.add(GOLD, ("r", (0.22, 0.26, 0.5, 0.34)), ("r", (0.22, 0.4, 0.46, 0.46)))
    c.add(STEELD, ("l", (0.72, 0.9, 0.58, 0.72, 0.1)))
    c.add(SKY, circ(0.58, 0.52, 0.22))
    c.add(WHITE, circ(0.52, 0.46, 0.06), shade=False, ol=False)


@sprite("world", "globe")
def _world(c):
    c.add(BLUE, circ(0.5, 0.48, 0.38))
    c.add(GREEN, ("p", [(0.28, 0.28), (0.44, 0.22), (0.5, 0.36), (0.4, 0.5), (0.3, 0.44)]))
    c.add(GREEN, ("p", [(0.56, 0.5), (0.74, 0.42), (0.8, 0.58), (0.66, 0.74), (0.58, 0.64)]))
    c.add(WHITE, ("r", (0.4, 0.1, 0.6, 0.15)), shade=False, ol=False)
    c.add(WOODD, ("r", (0.36, 0.88, 0.64, 0.94)), ("r", (0.46, 0.84, 0.54, 0.9)))


@sprite("select")
def _select(c):
    for i in range(6):
        t = 0.14 + i * 0.15
        c.add(GOLD, ("r", (t, 0.14, t + 0.09, 0.22)), ("r", (t, 0.7, t + 0.09, 0.78)), ol=False)
        c.add(GOLD, ("r", (0.14, t, 0.22, t + 0.09)), ("r", (0.78, t, 0.86, t + 0.09)), ol=False)
    c.add(WHITE, ("p", [(0.44, 0.4), (0.44, 0.9), (0.56, 0.78), (0.66, 0.96), (0.76, 0.9), (0.66, 0.74), (0.82, 0.74)]))


@sprite("shapes")
def _shapes(c):
    c.add(ORANGE, ("p", [(0.5, 0.1), (0.86, 0.3), (0.5, 0.5), (0.14, 0.3)]))
    c.add(RED, ("p", [(0.14, 0.3), (0.5, 0.5), (0.5, 0.92), (0.14, 0.72)]))
    c.add((190, 50, 44), ("p", [(0.86, 0.3), (0.5, 0.5), (0.5, 0.92), (0.86, 0.72)]))


@sprite("cube")
def _cube(c):
    c.add((130, 200, 250), ("p", [(0.5, 0.08), (0.88, 0.28), (0.5, 0.48), (0.12, 0.28)]))
    c.add(BLUE, ("p", [(0.12, 0.28), (0.5, 0.48), (0.5, 0.92), (0.12, 0.72)]))
    c.add(BLUED, ("p", [(0.88, 0.28), (0.5, 0.48), (0.5, 0.92), (0.88, 0.72)]))


@sprite("sphere")
def _sphere(c):
    c.add(PURPLE, circ(0.5, 0.5, 0.4))
    c.add((210, 180, 255), circ(0.38, 0.36, 0.1), shade=False, ol=False)


@sprite("cylinder")
def _cylinder(c):
    c.add(GREEND, ("r", (0.2, 0.26, 0.8, 0.78)), ("e", (0.2, 0.66, 0.8, 0.9)))
    c.add(GREEN, ("e", (0.2, 0.12, 0.8, 0.4)))


@sprite("pyramid")
def _pyramid(c):
    c.add((250, 220, 110), ("p", [(0.5, 0.1), (0.14, 0.74), (0.5, 0.9)]))
    c.add((226, 170, 60), ("p", [(0.5, 0.1), (0.5, 0.9), (0.9, 0.7)]))


@sprite("polygon")
def _polygon(c):
    c.add(TEAL, ("p", [(0.5, 0.1), (0.9, 0.4), (0.74, 0.88), (0.26, 0.88), (0.1, 0.4)]))
    for x, y in [(0.5, 0.1), (0.9, 0.4), (0.74, 0.88), (0.26, 0.88), (0.1, 0.4)]:
        c.add(WHITE, circ(x, y, 0.07), ol=False)


@sprite("grid", "chunk")
def _grid(c):
    for i in range(3):
        for j in range(3):
            col = GOLD if (i, j) == (1, 1) else STONE
            c.add(col, ("r", (0.1 + i * 0.29, 0.1 + j * 0.29, 0.1 + i * 0.29 + 0.25, 0.1 + j * 0.29 + 0.25)), ol=False)


@sprite("ruler", "size")
def _ruler(c):
    c.add(GOLD, ("p", [(0.1, 0.7), (0.7, 0.1), (0.9, 0.3), (0.3, 0.9)]))
    for k in range(5):
        t = 0.2 + k * 0.14
        c.add(DARK, ("l", (t - 0.06, 0.8 - t + 0.06 + 0.02, t - 0.01, 0.8 - t + 0.11 + 0.02, 0.03)), ol=False, shade=False)


@sprite("expand")
def _expand(c):
    c.add(STONE, ("r", (0.36, 0.36, 0.64, 0.64)))
    arrow(c, 0.5, 0.32, 0.5, 0.08, GREEN, 0.1, 0.16)
    arrow(c, 0.5, 0.68, 0.5, 0.92, GREEN, 0.1, 0.16)
    arrow(c, 0.32, 0.5, 0.08, 0.5, GREEN, 0.1, 0.16)
    arrow(c, 0.68, 0.5, 0.92, 0.5, GREEN, 0.1, 0.16)


@sprite("eraser", "clear")
def _eraser(c):
    c.add(PINK, ("p", [(0.1, 0.62), (0.52, 0.2), (0.82, 0.5), (0.4, 0.92)]))
    c.add(WHITE, ("p", [(0.52, 0.2), (0.7, 0.04), (0.96, 0.3), (0.82, 0.5)]))
    c.add(WHITE, ("r", (0.2, 0.9, 0.9, 0.95)), shade=False, ol=False)


@sprite("tree")
def _tree(c):
    c.add(WOODD, ("r", (0.43, 0.56, 0.57, 0.92)))
    c.add(GREEND, circ(0.5, 0.38, 0.3))
    c.add(GREEN, circ(0.4, 0.3, 0.2), circ(0.62, 0.36, 0.2))


@sprite("sapling")
def _sapling(c):
    c.add(WOODD, ("r", (0.46, 0.5, 0.54, 0.9)))
    c.add(GREEN, ("p", [(0.5, 0.52), (0.14, 0.4), (0.3, 0.14), (0.5, 0.3)]))
    c.add(GREEND, ("p", [(0.5, 0.52), (0.86, 0.4), (0.7, 0.14), (0.5, 0.3)]))


@sprite("flower")
def _flower(c):
    c.add(GREEND, ("r", (0.46, 0.5, 0.54, 0.92)), ("p", [(0.5, 0.74), (0.74, 0.62), (0.7, 0.8)]))
    for x, y in [(0.5, 0.2), (0.76, 0.36), (0.66, 0.64), (0.34, 0.64), (0.24, 0.36)]:
        c.add(PINK, circ(x, y, 0.16))
    c.add(GOLD, circ(0.5, 0.44, 0.12))


@sprite("terrain", "mountain")
def _terrain(c):
    c.add(STONED, ("p", [(0.04, 0.88), (0.38, 0.2), (0.7, 0.88)]))
    c.add(STONE, ("p", [(0.4, 0.88), (0.68, 0.34), (0.96, 0.88)]))
    c.add(WHITE, ("p", [(0.38, 0.2), (0.28, 0.42), (0.38, 0.38), (0.46, 0.46), (0.5, 0.36)]))
    c.add(GREEN, circ(0.22, 0.78, 0.12), circ(0.82, 0.8, 0.1))


@sprite("flame", "fire")
def _flame(c):
    c.add(RED, ("p", [(0.5, 0.06), (0.8, 0.46), (0.84, 0.72), (0.6, 0.94), (0.4, 0.94), (0.16, 0.72), (0.22, 0.44), (0.4, 0.5)]))
    c.add(ORANGE, ("p", [(0.5, 0.34), (0.68, 0.64), (0.62, 0.88), (0.38, 0.88), (0.32, 0.64)]))
    c.add(GOLD, ("p", [(0.5, 0.58), (0.58, 0.76), (0.5, 0.88), (0.42, 0.76)]))


@sprite("drop", "water")
def _drop(c):
    c.add(BLUE, ("e", (0.2, 0.4, 0.8, 0.94)), ("p", [(0.5, 0.06), (0.78, 0.55), (0.22, 0.55)]))
    c.add(SKY, circ(0.38, 0.64, 0.07), shade=False, ol=False)


@sprite("snow")
def _snow(c):
    for ang in (0, 60, 120):
        a = math.radians(ang)
        c.add(SKY, ("l", (0.5 - math.cos(a) * 0.4, 0.5 - math.sin(a) * 0.4, 0.5 + math.cos(a) * 0.4, 0.5 + math.sin(a) * 0.4, 0.08)))
    c.add(WHITE, circ(0.5, 0.5, 0.1))


@sprite("bucket")
def _bucket(c):
    c.add(STEELD, ("a", (0.22, 0.04, 0.78, 0.7, 180, 360, 0.05)), ol=False, shade=False)
    c.add(STEEL, ("p", [(0.18, 0.34), (0.82, 0.34), (0.72, 0.9), (0.28, 0.9)]))
    c.add(BLUE, ("r", (0.2, 0.34, 0.8, 0.46)))


@sprite("scissors")
def _scissors(c):
    c.add(STEEL, ("l", (0.3, 0.7, 0.8, 0.12, 0.09)), ("l", (0.7, 0.7, 0.2, 0.12, 0.09)))
    c.add(RED, ("a", (0.08, 0.6, 0.38, 0.92, 0, 360, 0.08)), ("a", (0.62, 0.6, 0.92, 0.92, 0, 360, 0.08)))


@sprite("copy")
def _copy(c):
    c.add(STEEL, ("r", (0.12, 0.1, 0.6, 0.72)))
    c.add(WHITE, ("r", (0.38, 0.28, 0.88, 0.92)))
    c.add(BLUE, ("r", (0.46, 0.4, 0.78, 0.46)), ("r", (0.46, 0.54, 0.78, 0.6)), ("r", (0.46, 0.68, 0.7, 0.74)), ol=False)


@sprite("clipboard")
def _clipboard(c):
    c.add(WOOD, ("r", (0.16, 0.12, 0.84, 0.92)))
    c.add(PAPER, ("r", (0.24, 0.22, 0.76, 0.84)))
    c.add(STEEL, ("r", (0.36, 0.06, 0.64, 0.2)))
    for i in range(4):
        c.add(BLUED, ("r", (0.3, 0.34 + i * 0.12, 0.7 - (i % 2) * 0.16, 0.38 + i * 0.12)), ol=False, shade=False)


@sprite("paste")
def _paste(c):
    _clipboard(c)
    arrow(c, 0.5, 0.42, 0.5, 0.86, GREEN, 0.12, 0.2)


@sprite("rotate")
def _rotate(c):
    c.add(BLUE, ("a", (0.14, 0.14, 0.86, 0.86, 200, 500, 0.13)))
    c.add(BLUE, ("p", [(0.74, 0.08), (0.96, 0.34), (0.66, 0.38)]))


@sprite("flip")
def _flip(c):
    c.add(TEAL, ("p", [(0.08, 0.2), (0.08, 0.8), (0.4, 0.5)]))
    c.add(GOLD, ("p", [(0.92, 0.2), (0.92, 0.8), (0.6, 0.5)]))
    c.add(WHITE, ("r", (0.47, 0.1, 0.53, 0.9)), shade=False, ol=False)


@sprite("trash")
def _trash(c):
    c.add(STEEL, ("p", [(0.22, 0.3), (0.78, 0.3), (0.72, 0.92), (0.28, 0.92)]))
    c.add(STEELD, ("r", (0.38, 0.4, 0.43, 0.84)), ("r", (0.57, 0.4, 0.62, 0.84)), ol=False)
    c.add(STONE, ("r", (0.14, 0.2, 0.86, 0.3)), ("r", (0.4, 0.1, 0.6, 0.2)))


@sprite("disk", "save")
def _disk(c):
    c.add(BLUE, ("r", (0.12, 0.12, 0.88, 0.88)))
    c.add(STEEL, ("r", (0.28, 0.12, 0.72, 0.4)))
    c.add(WHITE, ("r", (0.24, 0.52, 0.76, 0.88)))
    c.add(DARK, ("r", (0.58, 0.16, 0.66, 0.34)), ol=False)


@sprite("folder", "load")
def _folder(c):
    c.add(GOLDD, ("r", (0.1, 0.2, 0.5, 0.36)))
    c.add(GOLD, ("r", (0.1, 0.32, 0.9, 0.84)))
    c.add(PAPER, ("r", (0.18, 0.28, 0.82, 0.4)), ol=False)


@sprite("gavel", "auction")
def _gavel(c):
    c.add(WOODD, ("l", (0.3, 0.84, 0.66, 0.42, 0.1)))
    c.add(WOOD, ("p", [(0.5, 0.14), (0.7, 0.06), (0.9, 0.26), (0.78, 0.46), (0.5, 0.14)]), ("p", [(0.4, 0.26), (0.62, 0.1), (0.8, 0.42), (0.6, 0.6)]))
    c.add(STEEL, ("r", (0.1, 0.84, 0.64, 0.94)))


@sprite("chest")
def _chest(c):
    c.add(WOODD, ("r", (0.1, 0.34, 0.9, 0.88)))
    c.add(WOOD, ("p", [(0.1, 0.34), (0.9, 0.34), (0.84, 0.14), (0.16, 0.14)]))
    c.add(GOLD, ("r", (0.1, 0.4, 0.9, 0.5)), ("r", (0.44, 0.38, 0.56, 0.62)))
    c.add(GOLDD, ("r", (0.47, 0.5, 0.53, 0.56)), ol=False)


@sprite("tag", "price")
def _tag(c):
    c.add(GOLD, ("p", [(0.1, 0.5), (0.5, 0.1), (0.92, 0.1), (0.92, 0.52), (0.5, 0.92)]))
    c.add(DARK, circ(0.74, 0.28, 0.06), ol=False, shade=False)
    c.add(GOLDD, ("r", (0.46, 0.34, 0.54, 0.62)), ("r", (0.38, 0.4, 0.62, 0.46)), ("r", (0.38, 0.52, 0.62, 0.58)), ol=False)


@sprite("gift")
def _gift(c):
    c.add(RED, ("r", (0.14, 0.4, 0.86, 0.9)))
    c.add((250, 100, 90), ("r", (0.1, 0.28, 0.9, 0.44)))
    c.add(GOLD, ("r", (0.44, 0.28, 0.56, 0.9)))
    c.add(GOLD, circ(0.38, 0.2, 0.1), circ(0.62, 0.2, 0.1))


@sprite("book", "help")
def _book(c):
    c.add(BROWN, ("r", (0.16, 0.1, 0.84, 0.9)))
    c.add(PAPER, ("r", (0.22, 0.14, 0.82, 0.86)))
    c.add(RED, ("r", (0.1, 0.1, 0.24, 0.9)))
    c.add(BLUED, ("r", (0.34, 0.28, 0.7, 0.34)), ("r", (0.34, 0.44, 0.62, 0.5)), ("r", (0.34, 0.6, 0.7, 0.66)), ol=False, shade=False)


@sprite("wallet", "balance")
def _wallet(c):
    c.add(GOLD, circ(0.64, 0.3, 0.2))
    c.add(GOLDD, circ(0.64, 0.3, 0.12), ol=False)
    c.add(BROWN, ("r", (0.1, 0.4, 0.9, 0.88)))
    c.add((156, 106, 70), ("r", (0.1, 0.4, 0.9, 0.5)))
    c.add(GOLD, circ(0.76, 0.66, 0.08))


@sprite("crown", "top")
def _crown(c):
    c.add(GOLD, ("p", [(0.1, 0.8), (0.1, 0.28), (0.32, 0.5), (0.5, 0.16), (0.68, 0.5), (0.9, 0.28), (0.9, 0.8)]))
    c.add(GOLDD, ("r", (0.1, 0.72, 0.9, 0.86)))
    c.add(RED, circ(0.5, 0.58, 0.07))
    c.add(BLUE, circ(0.26, 0.64, 0.05), circ(0.74, 0.64, 0.05))


@sprite("send", "pay")
def _send(c):
    c.add(GOLD, circ(0.34, 0.42, 0.26))
    c.add(GOLDD, circ(0.34, 0.42, 0.16), ol=False)
    arrow(c, 0.36, 0.78, 0.9, 0.78, GREEN, 0.12, 0.2)


@sprite("magnifier", "inspect")
def _magnifier(c):
    c.add(WOODD, ("l", (0.9, 0.9, 0.58, 0.58, 0.12)))
    c.add(STEELD, ("a", (0.08, 0.08, 0.7, 0.7, 0, 360, 0.1)))
    c.add(SKY, circ(0.39, 0.39, 0.25), shade=False)
    c.add(WHITE, circ(0.3, 0.3, 0.06), shade=False, ol=False)


@sprite("radar", "near")
def _radar(c):
    c.add(DARK, circ(0.5, 0.5, 0.42))
    c.add(GREEN, ("a", (0.14, 0.14, 0.86, 0.86, 0, 360, 0.04)), ("a", (0.3, 0.3, 0.7, 0.7, 0, 360, 0.04)), ol=False, shade=False)
    c.add(GREEN, ("l", (0.5, 0.5, 0.78, 0.26, 0.05)), ol=False, shade=False)
    c.add(RED, circ(0.68, 0.64, 0.05), circ(0.34, 0.36, 0.05), ol=False)


@sprite("clock", "rollback")
def _clock(c):
    c.add(CREAM, circ(0.5, 0.5, 0.36))
    c.add(BLUED, ("a", (0.14, 0.14, 0.86, 0.86, 0, 360, 0.07)), ol=False, shade=False)
    c.add(DARK, ("l", (0.5, 0.5, 0.5, 0.26, 0.06)), ("l", (0.5, 0.5, 0.66, 0.58, 0.06)), ol=False, shade=False)
    c.add(GREEN, ("p", [(0.06, 0.18), (0.3, 0.12), (0.18, 0.36)]))


@sprite("gauge", "status")
def _gauge(c):
    c.add(CREAM, ("e", (0.1, 0.2, 0.9, 1.0)), ("r", (0.1, 0.6, 0.9, 0.9)))
    c.add(GREEN, ("p", [(0.14, 0.6), (0.2, 0.4), (0.34, 0.5), (0.3, 0.6)]), ol=False)
    c.add(GOLD, ("p", [(0.34, 0.3), (0.5, 0.26), (0.5, 0.42)]), ol=False)
    c.add(RED, ("p", [(0.7, 0.4), (0.86, 0.6), (0.7, 0.6)]), ol=False)
    c.add(DARK, ("l", (0.5, 0.74, 0.7, 0.4, 0.06)), circ(0.5, 0.74, 0.07), ol=False, shade=False)


@sprite("back", "prev")
def _back(c):
    c.add(GOLD, ("p", [(0.08, 0.5), (0.44, 0.1), (0.44, 0.34), (0.92, 0.34), (0.92, 0.66), (0.44, 0.66), (0.44, 0.9)]))


@sprite("next")
def _next(c):
    c.add(GOLD, ("p", [(0.92, 0.5), (0.56, 0.1), (0.56, 0.34), (0.08, 0.34), (0.08, 0.66), (0.56, 0.66), (0.56, 0.9)]))


@sprite("close")
def _close(c):
    c.add(RED, ("l", (0.16, 0.16, 0.84, 0.84, 0.2)), ("l", (0.84, 0.16, 0.16, 0.84, 0.2)))


@sprite("check")
def _check(c):
    c.add(GREEN, ("l", (0.12, 0.54, 0.4, 0.82, 0.18)), ("l", (0.4, 0.82, 0.9, 0.2, 0.18)))


@sprite("form")
def _form(c):
    c.add(PAPER, ("r", (0.16, 0.1, 0.78, 0.9)))
    for i in range(4):
        c.add(BLUED, ("r", (0.24, 0.22 + i * 0.16, 0.7, 0.28 + i * 0.16)), ol=False, shade=False)
    c.add(GOLD, ("l", (0.9, 0.2, 0.52, 0.72, 0.1)))
    c.add(DARK, ("p", [(0.5, 0.78), (0.46, 0.92), (0.6, 0.82)]), ol=False)


@sprite("info")
def _info(c):
    c.add(BLUE, circ(0.5, 0.5, 0.4))
    c.add(WHITE, ("r", (0.44, 0.42, 0.56, 0.74)), circ(0.5, 0.28, 0.07), shade=False, ol=False)


@sprite("skull", "butcher")
def _skull(c):
    c.add(WHITE, circ(0.5, 0.42, 0.34), ("r", (0.3, 0.55, 0.7, 0.88)))
    c.add(DARK, circ(0.36, 0.44, 0.09), circ(0.64, 0.44, 0.09), ("p", [(0.5, 0.56), (0.44, 0.68), (0.56, 0.68)]), ol=False, shade=False)
    c.add(DARK, ("r", (0.38, 0.78, 0.42, 0.88)), ("r", (0.48, 0.78, 0.52, 0.88)), ("r", (0.58, 0.78, 0.62, 0.88)), ol=False, shade=False)


@sprite("crystal", "regen")
def _crystal(c):
    c.add(PURPLE, ("p", [(0.5, 0.06), (0.8, 0.34), (0.66, 0.92), (0.34, 0.92), (0.2, 0.34)]))
    c.add((200, 160, 255), ("p", [(0.5, 0.06), (0.2, 0.34), (0.5, 0.4)]), ol=False)
    c.add((120, 70, 190), ("p", [(0.5, 0.4), (0.8, 0.34), (0.66, 0.92), (0.5, 0.92)]), ol=False)


@sprite("swap", "replace")
def _swap(c):
    arrow(c, 0.12, 0.3, 0.88, 0.3, BLUE, 0.12, 0.2)
    arrow(c, 0.88, 0.7, 0.12, 0.7, ORANGE, 0.12, 0.2)


@sprite("cycle")
def _cycle(c):
    c.add(GREEN, ("a", (0.14, 0.14, 0.86, 0.86, 200, 340, 0.13)), ("a", (0.14, 0.14, 0.86, 0.86, 20, 160, 0.13)))
    c.add(GREEN, ("p", [(0.8, 0.12), (0.94, 0.42), (0.62, 0.34)]), ("p", [(0.2, 0.88), (0.06, 0.58), (0.38, 0.66)]))


@sprite("gear", "tools")
def _gear(c):
    for k in range(8):
        a = math.radians(k * 45)
        c.add(STEELD, ("l", (0.5, 0.5, 0.5 + math.cos(a) * 0.42, 0.5 + math.sin(a) * 0.42, 0.16)), ol=False)
    c.add(STEEL, circ(0.5, 0.5, 0.3))
    c.add(DARK, circ(0.5, 0.5, 0.12), ol=False, shade=False)


@sprite("pickaxe", "pick")
def _pickaxe(c):
    c.add(WOODD, ("l", (0.2, 0.9, 0.7, 0.3, 0.1)))
    c.add(STEEL, ("p", [(0.1, 0.4), (0.4, 0.1), (0.64, 0.14), (0.88, 0.4), (0.82, 0.46), (0.62, 0.3), (0.44, 0.26), (0.2, 0.5)]))


@sprite("axe")
def _axe(c):
    c.add(WOODD, ("l", (0.22, 0.9, 0.7, 0.3, 0.1)))
    c.add(STEEL, ("p", [(0.52, 0.1), (0.9, 0.16), (0.84, 0.6), (0.6, 0.42)]))


@sprite("brush")
def _brush(c):
    c.add(WOODD, ("l", (0.9, 0.12, 0.44, 0.58, 0.11)))
    c.add(STEEL, ("p", [(0.38, 0.5), (0.5, 0.62), (0.4, 0.74), (0.28, 0.62)]))
    c.add(RED, ("p", [(0.28, 0.62), (0.4, 0.74), (0.22, 0.94), (0.06, 0.84)]))
    c.add(BLUE, circ(0.82, 0.78, 0.1), ol=False)


@sprite("schem", "blueprint")
def _schem(c):
    c.add(BLUE, ("r", (0.1, 0.16, 0.9, 0.84)))
    for i in range(1, 4):
        c.add((150, 200, 255), ("r", (0.1 + 0.2 * i, 0.16, 0.12 + 0.2 * i, 0.84)), ("r", (0.1, 0.16 + 0.17 * i, 0.9, 0.18 + 0.17 * i)), ol=False, shade=False)
    c.add(WHITE, ("p", [(0.3, 0.64), (0.3, 0.42), (0.5, 0.28), (0.7, 0.42), (0.7, 0.64)]), ol=False, shade=False)
    c.add(PAPER, ("r", (0.06, 0.1, 0.14, 0.9)), ("r", (0.86, 0.1, 0.94, 0.9)))


@sprite("wand")
def _wand(c):
    c.add(DARK, ("l", (0.16, 0.9, 0.62, 0.38, 0.1)))
    c.add(GOLD, ("p", [(0.7, 0.06), (0.78, 0.26), (0.96, 0.3), (0.82, 0.44), (0.86, 0.64), (0.7, 0.54), (0.54, 0.64), (0.58, 0.44), (0.44, 0.3), (0.62, 0.26)]))
    c.dots(WHITE, [(0.24, 0.3), (0.12, 0.5), (0.34, 0.12)])


@sprite("undo")
def _undo(c):
    c.add(BLUE, ("a", (0.14, 0.2, 0.86, 0.92, 190, 360, 0.15)))
    c.add(BLUE, ("p", [(0.02, 0.5), (0.34, 0.36), (0.2, 0.7)]))


@sprite("redo")
def _redo(c):
    c.add(GREEN, ("a", (0.14, 0.2, 0.86, 0.92, 180, 350, 0.15)))
    c.add(GREEN, ("p", [(0.98, 0.5), (0.66, 0.36), (0.8, 0.7)]))


@sprite("eye", "preview")
def _eye(c):
    c.add(WHITE, ("e", (0.04, 0.26, 0.96, 0.74)))
    c.add(BLUE, circ(0.5, 0.5, 0.2))
    c.add(DARK, circ(0.5, 0.5, 0.1), shade=False, ol=False)
    c.add(WHITE, circ(0.44, 0.44, 0.04), shade=False, ol=False)


@sprite("dotted", "outline")
def _dotted(c):
    pts = [(0.5, 0.1), (0.88, 0.3), (0.88, 0.72), (0.5, 0.92), (0.12, 0.72), (0.12, 0.3)]
    for i in range(6):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % 6]
        for k in range(5):
            t = k / 5
            c.add(SKY, circ(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 0.04), ol=False, shade=False)
    for k in range(5):
        t = k / 5
        c.add(SKY, circ(0.5, 0.5 + 0.42 * t, 0.04), ol=False, shade=False)
        c.add(SKY, circ(0.12 + 0.38 * t, 0.3 + 0.2 * t, 0.04), circ(0.88 - 0.38 * t, 0.3 + 0.2 * t, 0.04), ol=False, shade=False)


@sprite("star")
def _star(c):
    c.add(GOLD, ("p", [(0.5, 0.06), (0.62, 0.36), (0.94, 0.38), (0.7, 0.58), (0.78, 0.92), (0.5, 0.74), (0.22, 0.92), (0.3, 0.58), (0.06, 0.38), (0.38, 0.36)]))


@sprite("lock")
def _lock(c):
    c.add(STEELD, ("a", (0.28, 0.08, 0.72, 0.6, 180, 360, 0.1)))
    c.add(GOLD, ("r", (0.2, 0.42, 0.8, 0.9)))
    c.add(DARK, circ(0.5, 0.62, 0.07), ("r", (0.47, 0.64, 0.53, 0.78)), ol=False, shade=False)


@sprite("sword")
def _sword(c):
    c.add(STEEL, ("p", [(0.86, 0.06), (0.94, 0.14), (0.4, 0.68), (0.32, 0.6)]))
    c.add(GOLD, ("r", (0.2, 0.56, 0.5, 0.64)), ("l", (0.3, 0.52, 0.5, 0.72, 0.1)))
    c.add(WOODD, ("l", (0.3, 0.7, 0.1, 0.9, 0.1)))


@sprite("hat")
def _hat(c):
    c.add(RED, ("e", (0.1, 0.1, 0.9, 0.7)), ("r", (0.1, 0.4, 0.9, 0.7)))
    c.add(WOODD, ("r", (0.06, 0.62, 0.94, 0.78)))
    c.add(GOLD, ("r", (0.1, 0.5, 0.9, 0.58)), ol=False)


@sprite("up")
def _up(c):
    c.add(STONE, ("r", (0.2, 0.7, 0.8, 0.9)), ("r", (0.3, 0.55, 0.7, 0.72)))
    arrow(c, 0.5, 0.56, 0.5, 0.06, ORANGE, 0.2, 0.3)


@sprite("down")
def _down(c):
    c.add(STONE, ("r", (0.2, 0.1, 0.8, 0.3)), ("r", (0.3, 0.28, 0.7, 0.45)))
    arrow(c, 0.5, 0.44, 0.5, 0.94, ORANGE, 0.2, 0.3)


@sprite("ellipsoid")
def _ellipsoid(c):
    c.add(PURPLE, ("e", (0.04, 0.26, 0.96, 0.74)))
    c.add((210, 180, 255), ("e", (0.2, 0.34, 0.4, 0.44)), shade=False, ol=False)


@sprite("compass")
def _compass(c):
    c.add(STEEL, circ(0.5, 0.5, 0.4))
    c.add(RED, ("p", [(0.5, 0.14), (0.62, 0.5), (0.38, 0.5)]))
    c.add(WHITE, ("p", [(0.5, 0.86), (0.62, 0.5), (0.38, 0.5)]))


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
