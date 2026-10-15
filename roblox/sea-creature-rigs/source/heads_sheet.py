"""Close-ups of every head in one sheet.   python3 heads_sheet.py <out_dir>
Needs <out_dir>/previews/_raw/<Name>_head.png (closeup.py renders them)."""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

out = sys.argv[1]
raw = os.path.join(out, "previews", "_raw")
meta = json.load(open(os.path.join(out, "rigs.json")))
ORDER = ["TinyFish", "Pufferfish", "Crab", "Jellyfish", "Octopus", "MorayEel", "Shark", "HammerheadShark", "Orca",
         "GiantSquid", "Clownfish"]
cell, gap, cols = 420, 12, 4
rows = (len(ORDER) + cols - 1) // cols
W, H = cols * cell + (cols + 1) * gap, rows * (cell + 56) + gap + 90
sheet = Image.new("RGB", (W, H), (226, 230, 236))
d = ImageDraw.Draw(sheet)
d.text((gap + 8, 28), "Heads up close", font=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 40),
       fill=(24, 40, 70))
f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 26)
for i, n in enumerate(ORDER):
    x = gap + (i % cols) * (cell + gap)
    y = 90 + (i // cols) * (cell + 56)
    im = Image.open(os.path.join(raw, f"{n}_head.png")).convert("RGB").resize((cell, cell), Image.LANCZOS)
    sheet.paste(im, (x, y))
    d.text((x + cell / 2, y + cell + 26), f"{i + 1}  {meta[n]['display']}", font=f, fill=(30, 44, 70), anchor="mm")
p = os.path.join(out, "previews", "Heads.jpg")
sheet.save(p, quality=90)
print("wrote", p)
