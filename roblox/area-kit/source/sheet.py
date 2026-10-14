"""Lay the renders out as labelled preview sheets.

    python3 sheet.py <out_dir>
Writes <out>/previews/<Area>.png (every asset, close up), <Area>_lineup.png (all together, labelled)
and AllAreas.png (one lineup per area).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

out = sys.argv[1]
raw = os.path.join(out, "previews", "_raw")
assets = json.load(open(os.path.join(out, "assets.json")))
F = "/usr/share/fonts/opentype/inter/"
TITLE = ImageFont.truetype(F + "Inter-ExtraBold.otf", 54)
SUB = ImageFont.truetype(F + "Inter-SemiBold.otf", 26)
NAME = ImageFont.truetype(F + "Inter-Bold.otf", 30)
SMALL = ImageFont.truetype(F + "Inter-Medium.otf", 22)
TAG = ImageFont.truetype(F + "Inter-Bold.otf", 22)

NICE = {"Beach": "1  Beach", "TropicalIsland": "2  Tropical Island", "Volcano": "3  Volcano", "ThemePark": "4  Theme Park",
        "RichCity": "5  Rich City", "CruiseShip": "6  Cruise Ship Harbor", "SnowyPeaks": "7  Snowy Peaks",
        "PyramidDesert": "8  Pyramid Desert", "MoonBase": "9  Moon Base", "Shared": "Shared border pieces"}
BG = (24, 26, 34)
FG = (240, 242, 248)
DIM = (160, 166, 182)


def sheet(area, items):
    cols = 4 if len(items) > 6 else (3 if len(items) > 2 else 2)
    cw, ch = 600, 450
    pad, head = 14, 120
    rows = (len(items) + cols - 1) // cols
    W = cols * cw + (cols + 1) * pad
    H = head + rows * (ch + 64) + (rows + 1) * pad
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((pad + 6, 22), NICE.get(area, area), font=TITLE, fill=FG)
    tris = sum(it["tris"] for it in items)
    d.text((pad + 8, 86), f"{len(items)} assets  ·  sizes in studs (W × H × D)  ·  {tris:,} triangles in all", font=SUB, fill=DIM)
    for i, it in enumerate(items):
        x = pad + (i % cols) * (cw + pad)
        y = head + pad + (i // cols) * (ch + 64 + pad)
        p = os.path.join(raw, "solo", f"{it['name']}.png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
            img.paste(im, (x, y))
        d.rectangle([x, y + ch, x + cw, y + ch + 64], fill=(34, 37, 48))
        d.text((x + 14, y + ch + 6), it["name"], font=NAME, fill=FG)
        s = it["size_studs"]
        d.text((x + 14, y + ch + 38), f"{s['x']:g} × {s['y']:g} × {s['z']:g}   ·   {it['tris']:,} tris   ·   {it['parts']} parts", font=SMALL, fill=DIM)
    img.save(os.path.join(out, "previews", f"{area}.jpg"), quality=90, optimize=True)
    return img


def lineup(area):
    p = os.path.join(raw, "scene", f"{area}.png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGB")
    labels = json.load(open(p.replace(".png", ".json")))
    d = ImageDraw.Draw(im)
    W, H = im.size
    for lb in labels:
        x, y = lb["x"] * W, lb["y"] * H
        tw = d.textlength(lb["name"], font=TAG)
        x0, y0 = x - tw / 2 - 10, y - 36
        x0 = max(6, min(W - tw - 26, x0))
        y0 = max(6, y0)
        d.rounded_rectangle([x0, y0, x0 + tw + 20, y0 + 32], radius=9, fill=(20, 22, 30))
        d.text((x0 + 10, y0 + 4), lb["name"], font=TAG, fill=FG)
    bar = Image.new("RGB", (W, 84), BG)
    db = ImageDraw.Draw(bar)
    db.text((24, 14), NICE.get(area, area), font=TITLE, fill=FG)
    out_im = Image.new("RGB", (W, H + 84), BG)
    out_im.paste(bar, (0, 0))
    out_im.paste(im, (0, 84))
    out_im.save(os.path.join(out, "previews", f"{area}_lineup.jpg"), quality=90, optimize=True)
    return out_im


lineups = []
for area, items in assets.items():
    sheet(area, items)
    lu = lineup(area)
    if lu is not None and area != "Shared":
        lineups.append(lu)

if lineups:
    tw = 960
    th = int(lineups[0].size[1] * tw / lineups[0].size[0])
    cols = 3
    rows = (len(lineups) + cols - 1) // cols
    allimg = Image.new("RGB", (cols * tw + (cols + 1) * 10, 110 + rows * th + (rows + 1) * 10), BG)
    d = ImageDraw.Draw(allimg)
    total = sum(len(v) for v in assets.values())
    d.text((20, 18), f"Fish a Human  ·  area building kit  ·  {total} assets", font=TITLE, fill=FG)
    for i, lu in enumerate(lineups):
        x = 10 + (i % cols) * (tw + 10)
        y = 110 + (i // cols) * (th + 10)
        allimg.paste(lu.resize((tw, th), Image.LANCZOS), (x, y))
    allimg.save(os.path.join(out, "previews", "AllAreas.jpg"), quality=90, optimize=True)
print("sheets done")
