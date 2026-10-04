"""Builds the Harvest resource pack: pixel-art menu backgrounds, banners and button icons.

Everything is drawn here with Pillow, so the art can be changed and rebuilt:

    python generate.py

It reads ../harvest-gui/chest_menus.json (which buttons sit in which chest slot), draws one
background per menu with a plaque behind each used slot, and writes

- harvest_pack/            the pack, as plain files
- harvest-pack.zip         the same, zipped, for the server to hand to clients
- harvest-pack.sha1        the hash pumpkin.toml needs
- ../harvest-ui/data/menus.json   the menu descriptions the plugins load, with each menu's
                                  background glyph filled in

How a chest menu is skinned: the window title is a text component in the `harvest:gui` font.
Its first character moves the cursor 8 px left, the second is a 176x222 glyph that is the whole
background (opaque, so it covers the vanilla chest texture), the third moves the cursor back,
and the real title text follows on top of the art. Button icons are items with an
`item_model` component pointing at `harvest:icon/<name>`.
"""
import hashlib
import json
import os
import random
import shutil
import zipfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "harvest_pack")
SPEC = os.path.join(HERE, "chest_menus.json")
if not os.path.exists(SPEC):
    SPEC = os.path.join(HERE, "..", "harvest-gui", "chest_menus.json")
DATA = os.path.join(HERE, "..", "harvest-ui", "data")

W, H = 176, 222

# Families: accent colours (matching the dialogs' gradients), banner order and stock layouts.
FAMILIES = {
    "main": ((255, 140, 40), (255, 215, 100)),
    "edit": ((255, 170, 0), (255, 85, 85)),
    "shops": ((60, 220, 130), (40, 170, 200)),
    "eco": ((255, 215, 60), (255, 150, 30)),
    "log": ((90, 200, 255), (140, 110, 255)),
}
ORDER = list(FAMILIES)

# Layouts the plugins use for menus built at run time: slots with a plaque behind them.
GRID = [r * 9 + c for r in range(1, 5) for c in range(1, 8)] + [45, 47, 49, 51, 53]
DETAIL = [13, 29, 31, 33, 22, 49]
STOCK = {"grid": GRID, "detail": DETAIL}

INK = (24, 12, 6)
PANEL_A = (62, 38, 20)
PANEL_B = (68, 43, 23)
BAND = (38, 22, 11)
PLAQUE = (104, 68, 36)
PLAQUE_HI = (140, 94, 50)
PLAQUE_LO = (66, 40, 20)
RECESS = (30, 18, 10)
RECESS_HI = (88, 58, 32)


def shade(c, f):
    return tuple(max(0, min(255, round(v * f))) for v in c)


# ---------------------------------------------------------------- sprites

def pumpkin(size=16):
    """A small jack-o'-lantern, drawn pixel by pixel."""
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o1, o2, o3 = (232, 112, 20), (196, 80, 12), (150, 56, 10)
    d.ellipse((0, 4, 15, 15), fill=o2)
    d.ellipse((2, 4, 13, 15), fill=o1)
    d.ellipse((5, 4, 10, 15), fill=(250, 140, 36))
    d.line((7, 5, 7, 14), fill=o3)
    d.line((4, 6, 4, 13), fill=o3)
    d.line((11, 6, 11, 13), fill=o3)
    d.rectangle((7, 1, 8, 4), fill=(86, 120, 40))
    d.point((9, 2), fill=(86, 120, 40))
    glow = (255, 226, 110)
    d.polygon([(3, 8), (6, 8), (4, 6)], fill=glow)
    d.polygon([(9, 8), (12, 8), (11, 6)], fill=glow)
    d.rectangle((4, 11, 11, 12), fill=glow)
    d.point((6, 13), fill=glow)
    d.point((9, 13), fill=glow)
    return im


def outline(im, color=INK):
    """Adds a one-pixel dark outline around the opaque pixels."""
    w, h = im.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px, op = im.load(), out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                op[x, y] = px[x, y]
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3]:
                    op[x, y] = color + (255,)
                    break
    return out


def canvas():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


GOLD = (255, 205, 70)
GOLD_D = (200, 140, 30)
WOOD = (150, 98, 48)
WOOD_D = (100, 62, 28)
STEEL = (200, 208, 216)
STEEL_D = (130, 140, 154)
GREEN = (90, 190, 80)
GREEN_D = (50, 130, 50)
RED = (220, 70, 60)
BLUE = (80, 150, 230)
WHITE = (250, 250, 245)
PAPER = (240, 224, 180)
PAPER_D = (200, 176, 120)


def arrow(direction, color=WHITE):
    im, d = canvas()
    pts = {"left": [(2, 8), (8, 2), (8, 5), (14, 5), (14, 10), (8, 10), (8, 13)],
           "right": [(13, 8), (7, 2), (7, 5), (1, 5), (1, 10), (7, 10), (7, 13)]}[direction]
    d.polygon(pts, fill=color)
    return outline(im)


def icon_back():
    return arrow("left", (255, 215, 100))


def icon_next():
    return arrow("right", (255, 215, 100))


def icon_prev():
    return arrow("left", (255, 215, 100))


def icon_close():
    im, d = canvas()
    d.line((3, 3, 12, 12), fill=RED, width=2)
    d.line((12, 3, 3, 12), fill=RED, width=2)
    return outline(im)


def icon_build():
    im, d = canvas()
    d.line((4, 12, 11, 5), fill=WOOD, width=2)
    d.rectangle((8, 1, 14, 5), fill=STEEL)
    d.rectangle((8, 1, 14, 2), fill=WHITE)
    d.rectangle((12, 3, 14, 5), fill=STEEL_D)
    return outline(im)


def icon_select():
    im, d = canvas()
    for x in range(2, 14, 3):
        d.point((x, 3), fill=GOLD)
        d.point((x, 12), fill=GOLD)
    for y in range(3, 13, 3):
        d.point((2, y), fill=GOLD)
        d.point((13, y), fill=GOLD)
    d.rectangle((6, 6, 9, 9), fill=(255, 235, 150))
    return outline(im)


def icon_shape():
    im, d = canvas()
    d.polygon([(8, 1), (14, 4), (8, 7), (2, 4)], fill=(150, 220, 255))
    d.polygon([(2, 4), (8, 7), (8, 14), (2, 11)], fill=(80, 150, 230))
    d.polygon([(14, 4), (8, 7), (8, 14), (14, 11)], fill=(50, 100, 190))
    return outline(im)


def icon_terrain():
    im, d = canvas()
    d.polygon([(0, 14), (6, 5), (11, 14)], fill=(120, 130, 140))
    d.polygon([(6, 14), (11, 7), (16, 14)], fill=(90, 100, 112))
    d.polygon([(6, 5), (4, 8), (8, 8)], fill=WHITE)
    d.rectangle((12, 10, 12, 14), fill=WOOD_D)
    d.ellipse((10, 6, 14, 11), fill=GREEN)
    return outline(im)


def icon_clipboard():
    im, d = canvas()
    d.rectangle((3, 2, 12, 14), fill=WOOD)
    d.rectangle((4, 4, 11, 13), fill=PAPER)
    d.rectangle((6, 1, 9, 3), fill=STEEL)
    for y in (6, 8, 10):
        d.line((5, y, 10, y), fill=PAPER_D)
    return outline(im)


def icon_brush():
    im, d = canvas()
    d.line((3, 13, 10, 6), fill=WOOD, width=2)
    d.polygon([(9, 7), (14, 2), (15, 5), (11, 9)], fill=RED)
    d.rectangle((1, 12, 4, 15), fill=BLUE)
    return outline(im)


def icon_tool():
    im, d = canvas()
    d.line((3, 13, 11, 5), fill=WOOD, width=2)
    d.arc((4, 0, 15, 9), 200, 340, fill=STEEL, width=3)
    d.line((12, 2, 14, 4), fill=STEEL_D, width=1)
    return outline(im)


def icon_wand():
    im, d = canvas()
    d.line((3, 13, 10, 6), fill=WOOD, width=2)
    d.polygon([(11, 1), (12, 4), (15, 5), (12, 6), (11, 9), (10, 6), (7, 5), (10, 4)], fill=GOLD)
    return outline(im)


def icon_scroll():
    im, d = canvas()
    d.rectangle((3, 3, 12, 12), fill=PAPER)
    d.ellipse((1, 2, 5, 5), fill=PAPER_D)
    d.ellipse((10, 10, 14, 13), fill=PAPER_D)
    for y in (6, 8, 10):
        d.line((5, y, 10, y), fill=PAPER_D)
    return outline(im)


def icon_undo():
    im, d = canvas()
    d.arc((3, 4, 14, 14), 180, 360, fill=(120, 200, 255), width=3)
    d.polygon([(1, 7), (7, 7), (4, 11)], fill=(120, 200, 255))
    return outline(im)


def icon_redo():
    im, d = canvas()
    d.arc((2, 4, 13, 14), 180, 360, fill=(120, 255, 170), width=3)
    d.polygon([(15, 7), (9, 7), (12, 11)], fill=(120, 255, 170))
    return outline(im)


def icon_shop():
    im, d = canvas()
    d.rectangle((2, 7, 13, 14), fill=WOOD)
    d.rectangle((2, 7, 13, 8), fill=WOOD_D)
    d.polygon([(1, 7), (3, 2), (12, 2), (14, 7)], fill=RED)
    for x in (4, 8, 12):
        d.line((x, 2, x - 1, 6), fill=WHITE)
    d.rectangle((6, 10, 9, 14), fill=GOLD_D)
    return outline(im)


def icon_coin():
    im, d = canvas()
    d.ellipse((2, 2, 13, 13), fill=GOLD)
    d.ellipse((4, 4, 11, 11), fill=GOLD_D)
    d.rectangle((7, 5, 8, 10), fill=GOLD)
    return outline(im)


def icon_pay():
    im, d = canvas()
    d.ellipse((1, 1, 8, 8), fill=GOLD)
    d.ellipse((3, 3, 6, 6), fill=GOLD_D)
    d.polygon([(7, 10), (12, 10), (12, 8), (15, 11), (12, 14), (12, 12), (7, 12)], fill=GREEN)
    return outline(im)


def icon_crown():
    im, d = canvas()
    d.polygon([(2, 12), (2, 5), (5, 8), (8, 3), (11, 8), (14, 5), (14, 12)], fill=GOLD)
    d.rectangle((2, 11, 13, 13), fill=GOLD_D)
    d.point((8, 8), fill=RED)
    return outline(im)


def icon_log():
    im, d = canvas()
    d.ellipse((2, 2, 10, 10), fill=(160, 220, 255))
    d.ellipse((3, 3, 9, 9), fill=(40, 70, 110))
    d.line((9, 9, 14, 14), fill=WOOD, width=2)
    d.point((5, 5), fill=WHITE)
    return outline(im)


def icon_auction():
    im, d = canvas()
    d.rectangle((6, 1, 13, 5), fill=WOOD)
    d.rectangle((6, 1, 13, 2), fill=WOOD_D)
    d.line((4, 12, 9, 6), fill=WOOD_D, width=2)
    d.rectangle((1, 13, 10, 14), fill=STEEL_D)
    return outline(im)


def icon_info():
    im, d = canvas()
    d.ellipse((1, 1, 14, 14), fill=BLUE)
    d.rectangle((7, 6, 8, 11), fill=WHITE)
    d.rectangle((7, 3, 8, 4), fill=WHITE)
    return outline(im)


def icon_form():
    im, d = canvas()
    d.rectangle((2, 2, 13, 13), fill=PAPER)
    d.rectangle((4, 4, 11, 5), fill=BLUE)
    d.rectangle((4, 7, 11, 8), fill=BLUE)
    d.rectangle((4, 10, 8, 11), fill=GREEN)
    return outline(im)


def icon_check():
    im, d = canvas()
    d.line((2, 8, 6, 12), fill=GREEN, width=3)
    d.line((6, 12, 14, 3), fill=GREEN, width=3)
    return outline(im)


def icon_crest():
    return outline(pumpkin())


ICONS = {
    "back": icon_back, "next": icon_next, "prev": icon_prev, "close": icon_close, "build": icon_build,
    "select": icon_select, "shape": icon_shape, "terrain": icon_terrain, "clipboard": icon_clipboard,
    "brush": icon_brush, "tool": icon_tool, "wand": icon_wand, "scroll": icon_scroll, "undo": icon_undo,
    "redo": icon_redo, "shop": icon_shop, "coin": icon_coin, "pay": icon_pay, "crown": icon_crown, "log": icon_log,
    "auction": icon_auction, "info": icon_info, "form": icon_form, "check": icon_check, "crest": icon_crest,
}


# ---------------------------------------------------------------- backgrounds

def slot_xy(slot):
    return 7 + 18 * (slot % 9), 17 + 18 * (slot // 9)


def background(family, used):
    acc, acc2 = FAMILIES[family]
    rnd = random.Random(sum(map(ord, family)))
    im = Image.new("RGBA", (W, H), PANEL_A + (255,))
    px = im.load()
    for y in range(H):
        for x in range(W):
            if (x + y) % 2 == 0 and rnd.random() < 0.55:
                px[x, y] = PANEL_B + (255,)
    d = ImageDraw.Draw(im)

    # Header band with a trim line in the family colour.
    d.rectangle((3, 3, W - 4, 15), fill=BAND)
    d.line((3, 16, W - 4, 16), fill=acc)
    d.line((3, 17, W - 4, 17), fill=shade(acc, 0.55))
    for x in range(8, W - 8, 16):
        d.point((x, 3), fill=shade(acc2, 0.7))

    # Footer-of-content line and the band behind the "Inventory" label.
    d.rectangle((3, 126, W - 4, 137), fill=BAND)
    d.line((3, 125, W - 4, 125), fill=acc)
    d.line((3, 138, W - 4, 138), fill=shade(acc, 0.55))

    # Plaques behind the slots in use.
    for s in used:
        x, y = slot_xy(s)
        d.rectangle((x, y, x + 17, y + 17), fill=INK)
        d.rectangle((x + 1, y + 1, x + 16, y + 16), fill=PLAQUE)
        d.line((x + 1, y + 1, x + 16, y + 1), fill=PLAQUE_HI)
        d.line((x + 1, y + 1, x + 1, y + 16), fill=PLAQUE_HI)
        d.line((x + 1, y + 16, x + 16, y + 16), fill=PLAQUE_LO)
        d.line((x + 16, y + 1, x + 16, y + 16), fill=PLAQUE_LO)
        d.point((x + 2, y + 2), fill=shade(acc2, 0.9))
        d.point((x + 15, y + 15), fill=shade(acc, 0.8))

    # The player's inventory and hotbar slots, recessed.
    def recess(x, y):
        d.rectangle((x, y, x + 17, y + 17), fill=RECESS)
        d.line((x, y + 17, x + 17, y + 17), fill=RECESS_HI)
        d.line((x + 17, y, x + 17, y + 17), fill=RECESS_HI)
    for r in range(3):
        for c in range(9):
            recess(7 + 18 * c, 139 + 18 * r)
    for c in range(9):
        recess(7 + 18 * c, 197)

    # Border: dark outline, trim in the family colour, bevel, cut corners.
    d.rectangle((0, 0, W - 1, H - 1), outline=INK)
    d.rectangle((1, 1, W - 2, H - 2), outline=shade(acc, 0.75))
    d.rectangle((2, 2, W - 3, H - 3), outline=shade(acc, 0.4))
    for cx, cy in ((0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1)):
        px[cx, cy] = (0, 0, 0, 0)

    # Crest in the header's right corner, and a couple of leaves.
    crest = pumpkin()
    im.alpha_composite(outline(crest), (W - 24, 1))
    leaf = (150, 110, 30)
    for x, y in ((W - 40, 12), (W - 36, 8), (W - 33, 12)):
        d.point((x, y), fill=leaf)
    return im


def banner(family):
    """The 288x32 banner at the top of a dialog."""
    acc, acc2 = FAMILIES[family]
    w, h = 288, 32
    im = Image.new("RGBA", (w, h), PANEL_A + (255,))
    rnd = random.Random(7)
    px = im.load()
    for y in range(h):
        for x in range(w):
            if (x + y) % 2 == 0 and rnd.random() < 0.55:
                px[x, y] = PANEL_B + (255,)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=INK)
    d.rectangle((1, 1, w - 2, h - 2), outline=shade(acc, 0.75))
    d.rectangle((2, 2, w - 3, h - 3), outline=shade(acc, 0.4))
    # Gradient stripe along the bottom.
    for x in range(4, w - 4):
        f = (x - 4) / (w - 9)
        c = tuple(round(acc[i] + (acc2[i] - acc[i]) * f) for i in range(3))
        d.line((x, h - 7, x, h - 5), fill=c)
    # A row of pumpkins at both ends.
    crest = outline(pumpkin())
    for x in (8, 26):
        im.alpha_composite(crest, (x, 5))
    for x in (w - 42, w - 24):
        im.alpha_composite(crest, (x, 5))
    # Pixel leaves in between.
    rnd = random.Random(3)
    for _ in range(40):
        x, y = rnd.randrange(50, w - 60), rnd.randrange(5, 20)
        d.point((x, y), fill=[(190, 110, 30), (150, 90, 20), (220, 140, 40)][rnd.randrange(3)])
    return im


# ---------------------------------------------------------------- pack writing

def write(path, data, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if mode == "w":
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(data)
    else:
        with open(path, "wb") as f:
            f.write(data)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    menus = json.load(open(SPEC, encoding="utf-8"))
    assets = os.path.join(OUT, "assets", "harvest")

    # One background per distinct (family, slots) layout, plus the stock layouts.
    layouts = {}

    def layout(family, used):
        key = family + ":" + ",".join(map(str, sorted(used)))
        if key not in layouts:
            layouts[key] = 0xE100 + len(layouts)
        return key

    stock = {}
    for fam in ORDER:
        for name, slots in STOCK.items():
            stock["%s/%s" % (fam, name)] = layout(fam, slots)
    for m in menus.values():
        used = [s["slot"] for s in m["slots"]] + [49]
        m["bg"] = layout(m["family"], used)

    providers = [{"type": "space", "advances": {"": -8, "": -169, "": -1}}]
    for key, code in layouts.items():
        fam, slots = key.split(":")
        name = "bg_%04x" % code
        background(fam, [int(x) for x in slots.split(",") if x]).save(
            _mk(os.path.join(assets, "textures", "gui", name + ".png")))
        providers.append({"type": "bitmap", "file": "harvest:gui/%s.png" % name, "ascent": 13, "height": H, "chars": [chr(code)]})
    write(os.path.join(assets, "font", "gui.json"), json.dumps({"providers": providers}, indent=1))

    banners = []
    for i, fam in enumerate(ORDER):
        banner(fam).save(_mk(os.path.join(assets, "textures", "gui", "banner_%s.png" % fam)))
        banners.append({"type": "bitmap", "file": "harvest:gui/banner_%s.png" % fam, "ascent": 28, "height": 32, "chars": [chr(0xE300 + i)]})
    write(os.path.join(assets, "font", "banner.json"), json.dumps({"providers": banners}, indent=1))

    for name, fn in ICONS.items():
        fn().save(_mk(os.path.join(assets, "textures", "item", "icon", name + ".png")))
        write(os.path.join(assets, "models", "item", "icon", name + ".json"),
              json.dumps({"parent": "minecraft:item/generated", "textures": {"layer0": "harvest:item/icon/%s" % name}}))
        write(os.path.join(assets, "items", "icon", name + ".json"),
              json.dumps({"model": {"type": "minecraft:model", "model": "harvest:item/icon/%s" % name}}))

    write(os.path.join(OUT, "pack.mcmeta"), json.dumps({
        "pack": {"description": "Harvest menus: pixel-art backgrounds and icons", "min_format": 64, "max_format": 999, "pack_format": 84}}, indent=1))
    icon = pumpkin().resize((64, 64), Image.NEAREST)
    icon.save(_mk(os.path.join(OUT, "pack.png")))

    # Hand the plugins their menu descriptions, with glyph codes instead of layout keys.
    final = {"stock": {k: chr(layouts[v]) for k, v in stock.items()}, "icons": sorted(ICONS), "menus": {}}
    for key, m in menus.items():
        m = dict(m)
        m["bg"] = chr(layouts[m["bg"]])
        final["menus"][key] = m
    os.makedirs(DATA, exist_ok=True)
    write(os.path.join(DATA, "menus.json"), json.dumps(final, indent=1, ensure_ascii=False) + "\n")

    zip_path = os.path.join(HERE, "harvest-pack.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for f in sorted(files):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
    digest = hashlib.sha1(open(zip_path, "rb").read()).hexdigest()
    write(os.path.join(HERE, "harvest-pack.sha1"), digest + "\n")
    print("pack: %d backgrounds, %d icons, sha1 %s" % (len(layouts), len(ICONS), digest))


def _mk(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


if __name__ == "__main__":
    main()
