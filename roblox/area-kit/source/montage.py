import os
import sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]
files = sys.argv[2:]
ims = [Image.open(f).convert("RGB") for f in files]
w, h = ims[0].size
cols = 2 if len(ims) > 1 else 1
if len(ims) > 4:
    cols = 3
rows = (len(ims) + cols - 1) // cols
G = 6
sheet = Image.new("RGB", (w * cols + G * (cols - 1), h * rows + G * (rows - 1)), (30, 30, 30))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 26)
for i, im in enumerate(ims):
    x, y = (i % cols) * (w + G), (i // cols) * (h + G)
    sheet.paste(im.resize((w, h)), (x, y))
    d.text((x + 12, y + 8), os.path.basename(files[i]).split("_")[0], font=f, fill=(20, 20, 20))
sheet.save(out)
