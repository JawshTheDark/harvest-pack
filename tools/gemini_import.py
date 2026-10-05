"""Turns a sheet of AI-drawn pixel icons into clean sprites for the pack.

An image model never draws on an exact pixel grid, so its "pixel art" has blurry edges and
pixels of slightly different sizes. This finds each icon on the sheet, works out how big its
pixels really are, samples one colour per pixel, snaps the colours to a small palette and writes
an exact RGBA PNG. The icon sits on a magenta (#FF00FF) background; anything else is cut away.

    python3 tools/gemini_import.py sheets/batch1.webp --names builder,market,coins,... [--debug out.png]

`--names` lists the icons in reading order (rows top to bottom, left to right); use `-` for one
you do not want. Sprites are written to art/<name>.png.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(os.path.dirname(HERE), "art")
CANVAS = 32
CONTENT = 30  # a transparent pixel is kept all round, so icons never touch a tile edge


def is_bg(r, g, b, reach=90):
    return (255 - r) ** 2 + g ** 2 + (255 - b) ** 2 < reach * reach


def components(im):
    w, h = im.size
    px = im.load()
    mask = bytearray(w * h)
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if not is_bg(r, g, b):
                mask[y * w + x] = 1
    seen = bytearray(w * h)
    out = []
    for start in range(w * h):
        if not mask[start] or seen[start]:
            continue
        stack = [start]
        seen[start] = 1
        x0 = x1 = start % w
        y0 = y1 = start // w
        area = 0
        while stack:
            p = stack.pop()
            x, y = p % w, p // w
            area += 1
            if x < x0: x0 = x
            if x > x1: x1 = x
            if y < y0: y0 = y
            if y > y1: y1 = y
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        q = ny * w + nx
                        if mask[q] and not seen[q]:
                            seen[q] = 1
                            stack.append(q)
        out.append({"box": [x0, y0, x1 + 1, y1 + 1], "area": area})
    return out


def merge(groups, gap, small=3500):
    """Joins pieces of one icon (the dashes of a dashed square, a loose coin). Two big pieces
    are two icons, however close they sit."""
    changed = True
    while changed:
        changed = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                a, b = groups[i]["box"], groups[j]["box"]
                if min(groups[i]["area"], groups[j]["area"]) > small:
                    continue
                if a[0] - gap < b[2] and b[0] - gap < a[2] and a[1] - gap < b[3] and b[1] - gap < a[3]:
                    groups[i] = {"box": [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])], "area": groups[i]["area"] + groups[j]["area"]}
                    del groups[j]
                    changed = True
                    break
            if changed:
                break
    return groups


def frame_thickness(im, box, s):
    """If `box` is a thin coloured frame around a cell, how thick it is; otherwise None."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    px = im.load()

    def solid(x, y):
        return 0 <= x < im.width and 0 <= y < im.height and not is_bg(*px[x, y])

    def strip(fixed, along0, along1, horizontal):
        n = hit = 0
        for t in range(along0, along1):
            n += 1
            hit += solid(t, fixed) if horizontal else solid(fixed, t)
        return hit / max(1, n)

    # all four sides must be (nearly) solid lines
    for off in (3, 5):
        if min(strip(y0 + off, x0 + 8, x1 - 8, True), strip(y1 - 1 - off, x0 + 8, x1 - 8, True),
               strip(x0 + off, y0 + 8, y1 - 8, False), strip(x1 - 1 - off, y0 + 8, y1 - 8, False)) < 0.9:
            return None

    def run(x, y, dx, dy):
        skip = 0
        while 0 <= x < im.width and 0 <= y < im.height and not solid(x, y) and skip < 6 * s:
            x, y, skip = x + dx, y + dy, skip + 1
        n = 0
        while solid(x, y) and n < 60 * s:
            x, y, n = x + dx, y + dy, n + 1
        return n

    runs = []
    for f in (0.2, 0.35, 0.5, 0.65, 0.8):
        runs += [("t", run(int(x0 + f * w), y0, 0, 1)), ("b", run(int(x0 + f * w), y1 - 1, 0, -1)),
                 ("l", run(x0, int(y0 + f * h), 1, 0)), ("r", run(x1 - 1, int(y0 + f * h), -1, 0))]
    per_side = {k: min(v for kk, v in runs if kk == k) for k in "tblr"}
    t = max(per_side.values())
    if t > 24 * s or min(per_side.values()) < 4:
        return None
    return t


def find_icons(im):
    """Returns (cleaned sheet, icons). Frames drawn around cells are painted out first."""
    s = im.width / 1024.0
    clean_im = im.copy()
    cp = clean_im.load()
    for c in components(im):
        x0, y0, x1, y1 = c["box"]
        w, h = x1 - x0, y1 - y0
        if w > im.width * 0.45 or h > im.height * 0.5 or w < 140 * s or h < 140 * s:
            continue
        t = frame_thickness(im, c["box"], s)
        if t is None:
            continue
        ring = int(t + 3)
        for y in range(y0, y1):
            for x in range(x0, x1):
                if x < x0 + ring or x >= x1 - ring or y < y0 + ring or y >= y1 - ring:
                    cp[x, y] = (255, 0, 255)
    parts = []
    for c in components(clean_im):
        x0, y0, x1, y1 = c["box"]
        w, h = x1 - x0, y1 - y0
        if c["area"] < 120 * s * s:
            continue
        if x0 <= 1 or y0 <= 1 or x1 >= im.width - 1 or y1 >= im.height - 1:
            continue  # pieces of the sheet's border
        if min(w, h) <= 16 * s and max(w, h) >= 25 * s:
            continue  # separator lines
        if (w >= 100 * s and h >= 100 * s and c["area"] / (w * h) < 0.05) or (w > im.width * 0.6) or (h > im.height * 0.6):
            continue  # grid of separators
        parts.append(c)
    groups = merge(parts, 30 * s, 3500 * s * s)
    groups = [g for g in groups if (g["box"][2] - g["box"][0]) >= 30 * s and (g["box"][3] - g["box"][1]) >= 30 * s]
    # reading order
    groups.sort(key=lambda g: (g["box"][1] + g["box"][3]) / 2)
    rows, cur = [], []
    for g in groups:
        cy = (g["box"][1] + g["box"][3]) / 2
        if cur and abs(cy - sum((k["box"][1] + k["box"][3]) / 2 for k in cur) / len(cur)) > 55 * s:
            rows.append(cur)
            cur = []
        cur.append(g)
    if cur:
        rows.append(cur)
    ordered = []
    for r in rows:
        ordered += sorted(r, key=lambda g: g["box"][0])
    return clean_im, ordered


def edge_profile(im, box, axis):
    px = im.load()
    x0, y0, x1, y1 = box
    out = []
    if axis == 0:
        for x in range(x0, x1 - 1):
            s = 0
            for y in range(y0, y1):
                a, b = px[x, y], px[x + 1, y]
                s += abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
            out.append(s)
    else:
        for y in range(y0, y1 - 1):
            s = 0
            for x in range(x0, x1):
                a, b = px[x, y], px[x, y + 1]
                s += abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])
            out.append(s)
    return out


def _autocorr(p, lag):
    n = len(p)
    if lag >= n - 2:
        return 0.0
    m = sum(p) / n
    q = [v - m for v in p]
    den = sum(v * v for v in q) or 1.0
    return sum(q[i] * q[i + lag] for i in range(n - lag)) / den


def sheet_block(im, icons):
    """The size of one art pixel on this sheet. The generator draws on a fixed grid, so every icon
    on a sheet shares it; the edges of every icon repeat with that period."""
    nominal = im.width / 250.0
    profiles = []
    for g in icons:
        profiles.append(edge_profile(im, g["box"], 0))
        profiles.append(edge_profile(im, g["box"], 1))
    best, score = nominal, None
    lag = nominal * 0.9
    while lag <= nominal * 1.1:
        lo = int(lag)
        f = lag - lo
        s = sum((1 - f) * _autocorr(p, lo) + f * _autocorr(p, lo + 1) for p in profiles)
        if score is None or s > score:
            best, score = lag, s
        lag += 0.05
    return best


def snap(im, box, block):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    nx, ny = max(1, round(w / block)), max(1, round(h / block))
    bx, by = w / nx, h / ny
    px = im.load()
    out = Image.new("RGBA", (nx, ny), (0, 0, 0, 0))
    op = out.load()
    for j in range(ny):
        for i in range(nx):
            xa, xb = x0 + i * bx + 0.22 * bx, x0 + (i + 1) * bx - 0.22 * bx
            ya, yb = y0 + j * by + 0.22 * by, y0 + (j + 1) * by - 0.22 * by
            cols = []
            total = 0
            for y in range(int(ya), max(int(ya) + 1, int(yb) + 1)):
                for x in range(int(xa), max(int(xa) + 1, int(xb) + 1)):
                    if 0 <= x < im.width and 0 <= y < im.height:
                        total += 1
                        r, g, bl = px[x, y]
                        if not is_bg(r, g, bl, 48):  # tighter than when finding icons: a purple ball must not read as backdrop
                            cols.append((r, g, bl))
            if total and len(cols) * 2 > total:
                cols.sort(key=lambda c: c[0])
                mr = cols[len(cols) // 2][0]
                mg = sorted(c[1] for c in cols)[len(cols) // 2]
                mb = sorted(c[2] for c in cols)[len(cols) // 2]
                op[i, j] = (mr, mg, mb, 255)
    return out


def grey_to_clear(img, border=2):
    """Icons drawn on a plain grey tile: keep what is drawn on it."""
    w, h = img.size
    out = Image.new("RGBA", (w - 2 * border, h - 2 * border), (0, 0, 0, 0))
    ip, op = img.load(), out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = ip[x + border, y + border]
            if a and not (max(r, g, b) - min(r, g, b) < 26 and 110 < (r + g + b) / 3 < 205):
                op[x, y] = (r, g, b, a)
    return out


TOUCH_UP = {"expand": grey_to_clear, "terrain": lambda im: keep_main(im, 0)}


def clean(img, colors=28):
    """Snaps colours to a small palette and repairs magenta fringe on the edge."""
    w, h = img.size
    rgb = Image.new("RGB", (w, h), (0, 0, 0))
    rgb.paste(img.convert("RGB"), (0, 0), img.split()[3])
    pal = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ip, op, pp = img.load(), out.load(), pal.load()
    for y in range(h):
        for x in range(w):
            if ip[x, y][3]:
                op[x, y] = pp[x, y] + (255,)
    for y in range(h):
        for x in range(w):
            r, g, b, a = op[x, y]
            if not a:
                continue
            edge = any(not (0 <= x + dx < w and 0 <= y + dy < h) or op[x + dx, y + dy][3] == 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if edge and r > 90 and b > 90 and g < 0.55 * min(r, b):
                op[x, y] = (26, 20, 34, 255)
    return out


def shrink(img, content=CONTENT):
    """Scales an icon down so its longest side is `content`. Colours are blended in premultiplied
    form so the transparent background does not bleed into the edge, then alpha is thresholded."""
    w, h = img.size
    f = min(1.0, content / max(w, h))
    if f == 1.0:
        return img
    nw, nh = max(1, round(w * f)), max(1, round(h * f))
    pre = Image.new("RGBA", (w, h))
    pp, ip = pre.load(), img.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = ip[x, y]
            pp[x, y] = (r * a // 255, g * a // 255, b * a // 255, a)
    small = pre.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (nw, nh), (0, 0, 0, 0))
    op, sp = out.load(), small.load()
    for y in range(nh):
        for x in range(nw):
            r, g, b, a = sp[x, y]
            if a >= 128:
                k = 255 / a
                op[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)
    return out


def center(img):
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((CANVAS - img.width) // 2, (CANVAS - img.height) // 2))
    return canvas


def keep_main(img, reach=3):
    """Drops specks of the sheet (frame bits, dashes) that float away from the drawing."""
    w, h = img.size
    px = img.load()
    seen, comps = set(), []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] and (x, y) not in seen:
                stack, cells = [(x, y)], []
                seen.add((x, y))
                while stack:
                    cx, cy = stack.pop()
                    cells.append((cx, cy))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            n = (cx + dx, cy + dy)
                            if 0 <= n[0] < w and 0 <= n[1] < h and px[n][3] and n not in seen:
                                seen.add(n)
                                stack.append(n)
                comps.append(cells)
    if len(comps) < 2:
        return img
    main_cells = max(comps, key=len)
    mx0, mx1 = min(c[0] for c in main_cells), max(c[0] for c in main_cells)
    my0, my1 = min(c[1] for c in main_cells), max(c[1] for c in main_cells)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for cells in comps:
        near = any(mx0 - reach <= x <= mx1 + reach and my0 - reach <= y <= my1 + reach for x, y in cells[:1])
        if cells is main_cells or (near and len(cells) > 6):
            for x, y in cells:
                op[x, y] = px[x, y]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--names", default="")
    ap.add_argument("--debug")
    ap.add_argument("--colors", type=int, default=28)
    args = ap.parse_args()
    im = Image.open(args.sheet).convert("RGB")
    im, icons = find_icons(im)
    block = sheet_block(im, icons)
    names = [n.strip() for n in args.names.split(",")] if args.names else []
    print("%d icons found" % len(icons))
    if args.debug:
        dbg = im.copy()
        d = ImageDraw.Draw(dbg)
        for i, g in enumerate(icons):
            d.rectangle(g["box"], outline=(255, 255, 0))
            d.text((g["box"][0] + 3, g["box"][1] + 2), "%d %s" % (i, names[i] if i < len(names) else ""), fill=(255, 255, 255))
        dbg.save(args.debug)
    os.makedirs(ART, exist_ok=True)
    # a name ending in "+" joins that icon with the next one (an icon the detector split in two)
    jobs, i = [], 0
    while i < len(icons):
        name = names[i] if i < len(names) else None
        box = list(icons[i]["box"])
        if name and name.endswith("+") and i + 1 < len(icons):
            nb = icons[i + 1]["box"]
            box = [min(box[0], nb[0]), min(box[1], nb[1]), max(box[2], nb[2]), max(box[3], nb[3])]
            pad = int((box[3] - box[1]) * 0.15)  # a joined icon's thin parts (a centre line) can stick out past both halves
            box[1] = max(0, box[1] - pad)
            box[3] = min(im.height, box[3] + pad)
            name = name[:-1]
            i += 1
        jobs.append((name, box))
        i += 1
    for k, (name, box) in enumerate(jobs):
        snapped = snap(im, box, block)
        print("%2d %-10s box %-22s block %.2f -> %dx%d" % (k, name or "(unused)", tuple(box), block, snapped.width, snapped.height))
        if name and name != "-":
            if name in TOUCH_UP:
                snapped = TOUCH_UP[name](snapped)
            center(clean(shrink(snapped), args.colors)).save(os.path.join(ART, name + ".png"))


if __name__ == "__main__":
    main()
