"""Build one area's assets, stage them and render previews.
   python run.py <area_module> [draft|final] [only=A,B] [solo] [hero]"""
import importlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import bpy
import stage

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "out"))
mod = importlib.import_module(sys.argv[1])
quality = sys.argv[2] if len(sys.argv) > 2 else "draft"
only = None
for a in sys.argv[3:]:
    if a.startswith("only="):
        only = set(a[5:].split(","))
do_solo = "solo" in sys.argv
do_hero = "hero" in sys.argv or not do_solo

stage.reset()
col = bpy.data.collections.new(mod.AREA)
bpy.context.scene.collection.children.link(col)
roots = []
t0 = time.time()
for fn in mod.ASSETS:
    b = fn()
    if only and b.name not in only:
        continue
    r = b.finish(col)
    roots.append(r)
    print(f"{r.name:22s} size {tuple(r['size'])} tris {r['tris']} parts {r['parts']}")
print("build", round(time.time() - t0, 1), "s")
final = quality == "final"
stage.layout(roots, gap=10)
cam = stage.setup(mod.GROUND, res=(1920, 1080) if final else (1280, 720), samples=64 if final else 20)
if do_hero:
    stage.frame(cam, roots)
    tag = "_".join(sorted(only)) if only else mod.AREA
    png = os.path.join(OUT, f"{tag}_{quality}.png")
    t0 = time.time()
    stage.render(png)
    print("render", round(time.time() - t0, 1), "s ->", png)
    json.dump(stage.label_points(cam, roots), open(png.replace(".png", ".json"), "w"), indent=1)
if do_solo:
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = (1200, 900) if final else (800, 600)
    sc.cycles.samples = 48 if final else 16
    os.makedirs(os.path.join(OUT, "solo"), exist_ok=True)
    for r in roots:
        for o in roots:
            hide = o is not r
            for ch in o.children:
                ch.hide_render = hide
        stage.frame(cam, [r], az=-28, el=26, margin=0.06)
        png = os.path.join(OUT, "solo", f"{r.name}_{quality}.png")
        stage.render(png)
        print("solo ->", png)
