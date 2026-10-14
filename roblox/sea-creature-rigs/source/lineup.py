"""Preview sheets from the raw cards (build.py renders them on a transparent background).

python3 lineup.py <out_dir>
  previews/Lineup_Front.jpg   all eleven, numbered like the brief
  previews/Lineup_Back.jpg    the same from behind
  previews/<Name>.jpg         one creature, front and back
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

out = sys.argv[1]
RAW = os.path.join(out, "previews", "_raw")
ORDER = ["TinyFish", "Pufferfish", "Crab", "Jellyfish", "Octopus", "MorayEel", "Shark", "HammerheadShark", "Orca",
         "GiantSquid", "Clownfish"]
meta = json.load(open(os.path.join(out, "rigs.json")))
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"


def backdrop(w, h):
    """Soft studio sweep: light at the top, a little darker toward the floor, gentle vignette."""
    top, bot = (236, 239, 244), (204, 209, 218)
    bg = Image.new("RGB", (w, h))
    px = bg.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-w * 0.25, -h * 0.35, w * 1.25, h * 1.3], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(min(w, h) * 0.12))
    dark = Image.new("RGB", (w, h), (178, 184, 196))
    return Image.composite(bg, dark, vig)


def card(name, view, size):
    """The render with its floor shadow. The shadow catcher leaves a faint veil over the whole
    floor; lift it and feather the card's edges so only the contact shadow remains."""
    import numpy as np
    im = np.array(Image.open(os.path.join(RAW, f"{name}_{view}.png")).convert("RGBA")).astype(np.float32)
    h, w = im.shape[:2]
    shadow = im[..., :3].max(axis=2) < 4
    a = im[..., 3]
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    m = min(h, w) * 0.12
    feather = np.clip(np.minimum.reduce([xs, w - 1 - xs, ys, h - 1 - ys]) / m, 0, 1) ** 1.5
    a = np.where(shadow, np.clip((a - 8) * 1.15, 0, 255) * feather, a)
    im[..., 3] = a
    out = Image.fromarray(im.astype(np.uint8), "RGBA")
    return out.resize(size, Image.LANCZOS)


def pill(d, cx, y, num, label, scale=1.0):
    f = ImageFont.truetype(SEMI, int(30 * scale))
    fn = ImageFont.truetype(FONT, int(32 * scale))
    tw = d.textlength(label, font=f)
    h = int(54 * scale)
    r = h // 2
    w = int(tw + h + 40 * scale) if num is not None else int(tw + 48 * scale)
    x0 = int(cx - w / 2)
    d.rounded_rectangle([x0 + 3, y + 4, x0 + w + 3, y + h + 4], r, fill=(150, 160, 178))
    d.rounded_rectangle([x0, y, x0 + w, y + h], r, fill=(22, 70, 150))
    tx = x0 + 24 * scale
    if num is not None:
        d.ellipse([x0 - 4, y - 4, x0 + h + 4, y + h + 4], fill=(255, 255, 255))
        d.ellipse([x0, y, x0 + h, y + h], fill=(38, 132, 245))
        d.text((x0 + h / 2, y + h / 2), str(num), font=fn, fill=(255, 255, 255), anchor="mm")
        tx = x0 + h + 16 * scale
    d.text((tx, y + h / 2), label, font=f, fill=(255, 255, 255), anchor="lm")


def sheet(view, path):
    cw, ch = 400, 500
    rows = [ORDER[:6], ORDER[6:]]
    gap, lab = 10, 80
    W = 6 * cw + 5 * gap + 120
    H = len(rows) * (ch + lab) + 140
    bg = backdrop(W, H)
    d = ImageDraw.Draw(bg)
    d.text((60, 46), "Fish a Human  ·  sea creature rigs", font=ImageFont.truetype(FONT, 44), fill=(24, 40, 70))
    d.text((W - 60, 52), "front" if view == "front" else "back", font=ImageFont.truetype(SEMI, 32), fill=(90, 100, 120), anchor="ra")
    y = 110
    for row in rows:
        x = (W - (len(row) * cw + (len(row) - 1) * gap)) // 2
        for name in row:
            im = card(name, view, (cw, ch))
            bg.paste(im, (x, y), im)
            pill(d, x + cw / 2, y + ch - 6, ORDER.index(name) + 1, meta[name]["display"], 0.82)
            x += cw + gap
        y += ch + lab
    bg.save(path, quality=92)
    print("wrote", path)


def single(name):
    cw, ch = 640, 800
    W, H = 2 * cw + 60, ch + 130
    bg = backdrop(W, H)
    d = ImageDraw.Draw(bg)
    for i, view in enumerate(("front", "back")):
        im = card(name, view, (cw, ch))
        bg.paste(im, (30 + i * cw, 10), im)
    m = meta[name]
    pill(d, W / 2, ch + 20, ORDER.index(name) + 1, m["display"], 1.0)
    info = f"{len(m['parts'])} parts  ·  {m['tris']:,} triangles  ·  {m['body_height']:.1f} studs tall (default R15)"
    d.text((W / 2, ch + 100), info, font=ImageFont.truetype(SEMI, 24), fill=(80, 92, 112), anchor="mm")
    p = os.path.join(out, "previews", f"{name}.jpg")
    bg.save(p, quality=92)


os.makedirs(os.path.join(out, "previews"), exist_ok=True)
sheet("front", os.path.join(out, "previews", "Lineup_Front.jpg"))
sheet("back", os.path.join(out, "previews", "Lineup_Back.jpg"))
for n in ORDER:
    if os.path.exists(os.path.join(RAW, f"{n}_front.png")):
        single(n)
print("sheets done")
