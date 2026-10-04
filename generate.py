"""Builds the Harvest resource pack: illustrated menu windows, pixel fonts and the menu data.

Everything is drawn here with Pillow, so the art can be changed and rebuilt:

    python generate.py

It reads chest_menus.json (the buttons of each menu, written by ../harvest-gui/generate.py),
draws one window per menu with an illustrated tile behind every button, and writes

- harvest_pack/            the pack, as plain files
- harvest-pack.zip         the same, zipped, for the server to hand to clients
- harvest-pack.sha1        the hash pumpkin.toml needs
- ../harvest-ui/data/menus.json   what the plugins load: which slots belong to which button, and
                                  where dynamic text goes

How a chest menu is skinned: the window title is a text component in the `harvest:gui` font. Its
first character moves the cursor 8 px left, the second is a 176x230 glyph that is the whole
window (opaque, so it covers the vanilla chest texture; its top 8 px reach above the window for
the title banner), and the dynamic text (the title, a page number, a balance) follows in the
pixel fonts. The items in the slots are invisible (`harvest:blank`), so the art shows through and
the slots only provide tooltips and clicks.

Drop a PNG named after a sprite into art/ (for example art/builder.png) to replace a generated
illustration with your own.
"""
import hashlib
import json
import os
import shutil
import zipfile

from PIL import Image

import panels
import sprites
from panels import OVER, WIN_H, WIN_W, banner_plate, bar, button, pill, put, recess, slot_box, slots_of, tile, window
from pxl import OUT, draw_text, text_width

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "harvest_pack")
SPEC = os.path.join(HERE, "chest_menus.json")
if not os.path.exists(SPEC):
    SPEC = os.path.join(HERE, "..", "harvest-gui", "chest_menus.json")
DATA = os.path.join(HERE, "..", "harvest-ui", "data")
ART = os.path.join(HERE, "art")

ASCENT_BASE = 13  # where the title baseline sits below the window's top edge
GLYPH_BASE = 0xE100

# ---------------------------------------------------------------- fonts

CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;!?'-+/&%#()$*><="
# Cells are tall: a glyph's ascent may not exceed its height, so text drawn high above the baseline
# (the title plate sits over the window's top edge) needs transparent rows below it.
CW, CH = 7, 16
SHIFT_NEG = ["", "", "", "", "", "", "", ""]  # -1 .. -128
SHIFT_POS = ["", "", "", "", "", "", "", ""]  # +1 .. +128

# name -> look and the y of the top of a glyph cell, in window coordinates
FONTS = {
    "title": dict(color=(70, 70, 70), shadow=(255, 255, 255), outline=None, scale=1, top=-3, pad=0),
    "page": dict(color=(250, 250, 246), shadow=OUT, outline=None, scale=1, top=112, pad=0),
    "bar": dict(color=(250, 250, 246), shadow=None, outline=OUT, scale=2, top=80, pad=1),
}


def shift_provider():
    adv = {}
    for i in range(8):
        adv[SHIFT_NEG[i]] = -(1 << i)
        adv[SHIFT_POS[i]] = 1 << i
    return {"type": "space", "advances": adv}


def build_fonts(assets):
    info = {}
    for name, f in FONTS.items():
        rows = [CHARS[i:i + 16] for i in range(0, len(CHARS), 16)]
        atlas = Image.new("RGBA", (16 * CW, len(rows) * CH), (0, 0, 0, 0))
        advance = {}
        for ri, row in enumerate(rows):
            for ci, ch in enumerate(row):
                cell = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
                draw_text(cell, f["pad"], f["pad"], ch, f["color"], shadow=f["shadow"], outline=f["outline"])
                atlas.alpha_composite(cell, (ci * CW, ri * CH))
                widest = 0
                px = cell.load()
                for x in range(CW):
                    for y in range(CH):
                        if px[x, y][3]:
                            widest = x + 1
                advance[ch] = widest * f["scale"] + 1
        atlas_path = os.path.join(assets, "textures", "font", name + ".png")
        os.makedirs(os.path.dirname(atlas_path), exist_ok=True)
        atlas.save(atlas_path)
        pad = ["".join(r.ljust(16, "\u0000")) for r in rows]
        provider = {
            "type": "bitmap",
            "file": "harvest:font/%s.png" % name,
            "ascent": ASCENT_BASE - f["top"],
            "height": CH * f["scale"],
            "chars": pad,
        }
        write(os.path.join(assets, "font", name + ".json"), json.dumps({"providers": [shift_provider(), {"type": "space", "advances": {" ": 4 * f["scale"]}}, provider]}, indent=1))
        info[name] = {"id": "harvest:" + name, "space": 4 * f["scale"], "advance": advance}
    return info


# ---------------------------------------------------------------- how each button looks

# label -> (sprite, theme, badge)
STYLE = {
    "Build tools": ("builder", "orange", None), "Shops & auctions": ("market", "green", None), "Money": ("coins", "gold", None),
    "Staff logs": ("logbook", "blue", None), "Terra world": ("world", "teal", None),
    "Selection": ("select", "sky", None), "Shapes & fills": ("shapes", "orange", None), "Terrain & nature": ("terrain", "green", None),
    "Clipboard": ("clipboard", "slate", None), "Brushes": ("brush", "pink", None), "Tools": ("pickaxe", "slate", None),
    "Schematics": ("schem", "blue", None), "Get the wand": ("wand", "violet", None), "Undo": ("undo", "blue", None),
    "Redo": ("redo", "green", None), "Preview mode": ("eye", "teal", None), "Selection outline": ("dotted", "sky", None),
    "Box": ("cube", "blue", None), "Grow box": ("expand", "green", None), "Polygon": ("polygon", "teal", None),
    "Ellipsoid": ("ellipsoid", "violet", None), "Sphere": ("sphere", "violet", None), "Cylinder": ("cylinder", "green", None),
    "Convex shape": ("pyramid", "gold", None), "This chunk": ("grid", "slate", None), "Show size": ("ruler", "gold", None),
    "Clear selection": ("eraser", "pink", None), "Fill in a form": ("form", "slate", None),
    "Naturalize selection": ("tree", "green", None), "Flowers in selection": ("flower", "pink", None),
    "Clear above me": ("up", "orange", None), "Clear below me": ("down", "orange", None), "Regenerate selection": ("crystal", "violet", None),
    "Copy": ("copy", "slate", None), "Cut": ("scissors", "red", None), "Paste": ("paste", "green", None),
    "Paste, skip air": ("paste", "sky", "AIR"), "Rotate 90": ("rotate", "blue", "90"), "Rotate 180": ("rotate", "blue", "180"),
    "Rotate 270": ("rotate", "blue", "270"), "Flip": ("flip", "teal", None), "Clear clipboard": ("trash", "red", None),
    "Load a file...": ("folder", "gold", None),
    "Selection wand": ("wand", "violet", None), "Far wand": ("wand", "pink", "FAR"), "Navigation wand": ("compass", "teal", None),
    "Tree planter": ("sapling", "green", None), "Block cycler": ("cycle", "green", None), "Floating tree remover": ("axe", "red", None),
    "Block info": ("info", "blue", None), "Super pickaxe": ("pickaxe", "slate", None), "Pickaxe: area": ("pickaxe", "orange", "AREA"),
    "Pickaxe: vein": ("pickaxe", "teal", "VEIN"), "Wand on/off": ("gear", "slate", None), "Remove tool": ("close", "red", None),
    "Browse auctions": ("gavel", "green", None), "My listings": ("chest", "teal", None), "Sell what I hold": ("tag", "gold", None),
    "Claim my items": ("gift", "pink", None), "My shops": ("market", "orange", None), "How shops work": ("book", "blue", None),
    "My balance": ("wallet", "gold", None), "Richest players": ("crown", "orange", None), "Pay someone": ("send", "green", None),
    "Block inspector": ("magnifier", "blue", None), "Changes near me": ("radar", "teal", None), "Undo last rollback": ("clock", "violet", None),
    "Status": ("gauge", "green", None),
}
LABEL = {
    "Build tools": "BUILD TOOLS", "Shops & auctions": "SHOPS", "Money": "MONEY", "Staff logs": "LOGS", "Terra world": "TERRA",
    "Browse auctions": "AUCTIONS", "Sell what I hold": "SELL", "Naturalize selection": "NATURALIZE", "Regenerate selection": "REGEN",
    "Block inspector": "INSPECT", "Changes near me": "NEARBY", "My balance": "BALANCE", "Richest players": "RICHEST", "Pay someone": "PAY",
}


def style(name):
    return STYLE.get(name, ("gear", "slate", None))


# ---------------------------------------------------------------- menu assembly

def write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if mode == "w":
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    else:
        with open(path, "wb") as f:
            f.write(text)


def user_art(name):
    """A PNG the user dropped into art/ replaces the generated sprite of that name."""
    p = os.path.join(ART, name + ".png")
    return Image.open(p).convert("RGBA") if os.path.exists(p) else None


class Menu:
    def __init__(self, title):
        self.title = title
        self.img = window()
        self.panels = []
        self.named = {}
        self.fields = {"title": {"font": "title", "cx": 88}}
        # the title plate reaches over the top edge
        self.img.alpha_composite(banner_plate(), (32, 0))

    def entry_tile(self, entry, c, r, w, h, label=None):
        sprite, theme, badge = style(entry["name"])
        art = tile(w * 18 - 2, h * 18 - 2, theme, sprite, LABEL.get(entry["name"]) if label is None else label, badge)
        put(self.img, art, c, r, w, h)
        self.panels.append({"slots": slots_of(c, r, w, h), "name": entry["name"], "tip": entry.get("tip", ""), "cmd": entry["cmd"], "close": entry["close"]})

    def back(self, spec, c=8, r=5):
        close = spec["name"] == "Close"
        art = button("red" if close else "slate", "close" if close else "back")
        put(self.img, art, c, r)
        self.panels.append({"slots": [r * 9 + c], "name": spec["name"], "tip": "", "cmd": spec["cmd"], "close": spec["close"]})

    def decor(self, art, c, r, w, h):
        put(self.img, art, c, r, w, h)

    def region(self, name, slots):
        self.named[name] = slots

    def save(self, assets, code):
        name = "win_%04x" % code
        path = os.path.join(assets, "textures", "gui", name + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.img.save(path)
        return {"file": "harvest:gui/%s.png" % name, "ascent": ASCENT_BASE + OVER, "height": WIN_H + OVER, "chars": [chr(code)]}


def lay_main(m, entries, back):
    by = {e["name"]: e for e in entries}
    m.entry_tile(by["Build tools"], 0, 0, 5, 4)
    m.entry_tile(by["Terra world"], 0, 4, 5, 2)
    m.entry_tile(by["Shops & auctions"], 5, 0, 4, 2)
    m.entry_tile(by["Money"], 5, 2, 4, 2)
    m.entry_tile(by["Staff logs"], 5, 4, 4, 2)


def lay_grid(m, entries, back):
    for i, e in enumerate(entries[:12]):
        m.entry_tile(e, (i % 4) * 2, (i // 4) * 2, 2, 2, label="")
    for i, e in enumerate(entries[12:]):
        sprite, theme, badge = style(e["name"])
        put(m.img, tile(16, 16, theme, sprite, None, None), 8, i)
        m.panels.append({"slots": [i * 9 + 8], "name": e["name"], "tip": e.get("tip", ""), "cmd": e["cmd"], "close": e["close"]})
    m.back(back)


def lay_dash(big):
    def run(m, entries, back):
        bigs = [e for n in big for e in entries if e["name"] == n]
        small = [e for e in entries if e not in bigs]
        if bigs:
            m.entry_tile(bigs[0], 0, 0, 5, 3)
        if len(bigs) > 1:
            m.entry_tile(bigs[1], 5, 0, 4, 3)
        for i, e in enumerate(small[:4]):
            m.entry_tile(e, i * 2, 3, 2, 2, label="")
        for i, e in enumerate(small[4:]):
            sprite, theme, badge = style(e["name"])
            put(m.img, tile(16, 16, theme, sprite, None, None), 8, 3 + i)
            m.panels.append({"slots": [(3 + i) * 9 + 8], "name": e["name"], "tip": e.get("tip", ""), "cmd": e["cmd"], "close": e["close"]})
        m.back(back)
    return run


def lay_eco(m, entries, back):
    for i, e in enumerate(entries[:3]):
        m.entry_tile(e, i * 3, 0, 3, 3)
    x, y, w, h = slot_box(0, 3, 9, 2)
    m.img.alpha_composite(bar(w, h), (x, OVER + y))
    m.fields["balance"] = {"font": "bar", "cx": 104}
    m.back(back)


LAYOUTS = {
    "main": lay_main,
    "edit": lay_grid,
    "edit/select": lay_grid,
    "edit/clipboard": lay_grid,
    "edit/tools": lay_grid,
    "edit/terrain": lay_dash(["Naturalize selection", "Regenerate selection"]),
    "shops": lay_dash(["Browse auctions", "Sell what I hold"]),
    "log": lay_dash(["Block inspector", "Changes near me"]),
    "eco": lay_eco,
}


# ---------------------------------------------------------------- stock layouts (menus the plugins fill in)

def stock_list(kind):
    """A grid of listings with a rail of tabs on the left and an illustration on the right."""
    m = Menu("")
    grid = []
    for r in range(5):
        for c in range(1, 7):
            x, y, w, h = slot_box(c, r)
            m.img.alpha_composite(recess(w + 0, h + 0), (x, OVER + y))
            grid.append(r * 9 + c)
    named = {"grid": grid}
    if kind == "ah":
        tabs = [("all", "tag", "gold"), ("auctions", "gavel", "green"), ("buy", "coins", "orange"), ("mine", "chest", "teal"), ("claim", "gift", "pink")]
        for i, (n, sp, th) in enumerate(tabs):
            put(m.img, button(th, sp), 0, i)
            named[n] = [i * 9]
        put(m.img, tile(34, 70, "sky", "market"), 7, 0, 2, 4)
        put(m.img, tile(34, 34, "gold", "tag", None, None), 7, 4, 2, 2)
        named["sell"] = slots_of(7, 4, 2, 2)
    else:
        put(m.img, tile(34, 70, "blue", "schem"), 7, 0, 2, 4)
        put(m.img, tile(34, 34, "slate", "clipboard", None, None), 7, 4, 2, 2)
        named["clipboard"] = slots_of(7, 4, 2, 2)
    put(m.img, button("slate", "back"), 0, 5)
    named["back"] = [45]
    put(m.img, button("gold", "prev"), 1, 5)
    named["prev"] = [46]
    put(m.img, button("gold", "next"), 6, 5)
    named["next"] = [51]
    m.fields["page"] = {"font": "page", "cx": 79}
    m.named = named
    return m


def stock_detail(variant):
    """One listing: the item on a stage, its info plate and the buttons for what you can do."""
    m = Menu("")
    stage = tile(52, 52, "violet", None)
    spot = 26
    from panels import glow
    glow(stage, spot, 22, 30, (255, 240, 200), 0.7)
    put(m.img, stage, 3, 0, 3, 3)
    x, y, w, h = slot_box(4, 1)
    from PIL import ImageDraw
    d = ImageDraw.Draw(m.img)
    d.rectangle([x - 1, OVER + y - 1, x + w, OVER + y + h], outline=(255, 214, 80, 255))
    put(m.img, button("blue", "info"), 4, 2)
    named = {"item": [13], "info": [22], "back": [45]}
    put(m.img, button("slate", "back"), 0, 5)
    pills = {
        "buy": [None, ("BUY NOW", "green", None), None],
        "auction": [("BID MIN", "green", None), ("BID MORE", "blue", None), ("BUYOUT", "orange", None)],
        "auction_nobuyout": [("BID MIN", "green", None), ("BID MORE", "blue", None), None],
        "own": [None, ("CANCEL", "red", None), None],
        "own_bid": [None, ("HAS BID", "slate", None), None],
    }[variant]
    for i, p in enumerate(pills):
        slots = slots_of(i * 3, 4, 3, 1)
        if p:
            label, theme, sp = p
            x, y, w, h = slot_box(i * 3, 4, 3, 1)
            m.img.alpha_composite(pill(w, h, theme, label, sp), (x, OVER + y))
        named["pill_" + "lmr"[i]] = slots if p else []
    m.named = named
    return m


def stock_money():
    return None


STOCK = {
    "ah_list": lambda: stock_list("ah"),
    "schem_list": lambda: stock_list("schem"),
    "detail_buy": lambda: stock_detail("buy"),
    "detail_auction": lambda: stock_detail("auction"),
    "detail_auction_nobuyout": lambda: stock_detail("auction_nobuyout"),
    "detail_own": lambda: stock_detail("own"),
    "detail_own_bid": lambda: stock_detail("own_bid"),
}


# ---------------------------------------------------------------- the pack

def main():
    if os.path.isdir(OUTDIR):
        shutil.rmtree(OUTDIR)
    spec = json.load(open(SPEC, encoding="utf-8"))
    assets = os.path.join(OUTDIR, "assets", "harvest")
    fonts = build_fonts(assets)

    providers = [shift_provider()]
    menus = {}
    code = GLYPH_BASE

    def finish(m, key):
        nonlocal code
        providers.append({"type": "bitmap", **m.save(assets, code)})
        out = {"bg": chr(code), "fields": m.fields, "panels": m.panels, "regions": m.named}
        code += 1
        return out

    for key, s in spec.items():
        layout = LAYOUTS.get(key)
        if not layout:
            print("no layout for", key)
            continue
        entries = [{"name": e["name"], "tip": e["tip"], "cmd": e["cmd"], "close": e["close"]} for e in s["slots"]]
        m = Menu(s["title"])
        layout(m, entries, s["back"])
        out = finish(m, key)
        out["title"] = s["title"]
        menus[key] = out
        m.img.save(os.path.join(HERE, "preview_%s.png" % key.replace("/", "_"))) if os.environ.get("PREVIEW") else None

    stock = {}
    for key, build in STOCK.items():
        m = build()
        stock[key] = finish(m, key)
        if os.environ.get("PREVIEW"):
            m.img.save(os.path.join(HERE, "preview_stock_%s.png" % key))

    write(os.path.join(assets, "font", "gui.json"), json.dumps({"providers": providers}, indent=1))
    write(os.path.join(assets, "items", "blank.json"), json.dumps({"model": {"type": "minecraft:empty"}}))
    write(os.path.join(OUTDIR, "pack.mcmeta"), json.dumps({
        "pack": {"description": "Harvest menus: illustrated windows and pixel fonts", "min_format": 64, "max_format": 999, "pack_format": 84}}, indent=1))
    sprites.render("builder", 28).resize((124, 124), Image.NEAREST).save(os.path.join(OUTDIR, "pack.png"))

    final = {
        "fonts": fonts,
        "shift": {"neg": SHIFT_NEG, "pos": SHIFT_POS},
        "window": {"width": WIN_W, "baseline": ASCENT_BASE},
        "menus": menus,
        "stock": stock,
    }
    os.makedirs(DATA, exist_ok=True)
    write(os.path.join(DATA, "menus.json"), json.dumps(final, indent=1, ensure_ascii=False) + "\n")

    zip_path = os.path.join(HERE, "harvest-pack.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUTDIR):
            for f in sorted(files):
                full = os.path.join(root, f)
                zi = zipfile.ZipInfo(os.path.relpath(full, OUTDIR).replace(os.sep, "/"), date_time=(2026, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(zi, open(full, "rb").read())
    digest = hashlib.sha1(open(zip_path, "rb").read()).hexdigest()
    write(os.path.join(HERE, "harvest-pack.sha1"), digest + "\n")
    print("pack: %d menus, %d stock layouts, %d fonts, sha1 %s" % (len(menus), len(stock), len(fonts), digest))


if __name__ == "__main__":
    main()
