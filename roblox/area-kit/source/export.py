"""Build every area, render the previews, save .blend files and export FBX for Roblox.

    python export.py <out_dir> [--no-render] [--areas=a,b]

Writes:
    <out>/fbx/<Area>.fbx              every asset of the area in one file (one model each)
    <out>/fbx/<Area>/<Asset>.fbx      one file per asset
    <out>/blend/<Area>.blend          the editable Blender scene
    <out>/previews/_raw/...           renders (sheet.py lays them out)
    <out>/assets.json                 size / triangle / part counts
"""
import importlib
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import bpy  # noqa: E402  (bpy first: it puts addon_utils on the path)
import addon_utils
from mathutils import Matrix

import kit
import stage

AREAS = ["area_beach", "area_tropical", "area_volcano", "area_themepark", "area_richcity", "area_cruise",
         "area_snowy", "area_desert", "area_moon", "area_shared"]

out = os.path.abspath(sys.argv[1])
render = "--no-render" not in sys.argv
only = None
for a in sys.argv[2:]:
    if a.startswith("--areas="):
        only = a.split("=", 1)[1].split(",")

addon_utils.enable("io_scene_fbx", default_set=True)
for d in ("fbx", "blend", "previews/_raw/solo", "previews/_raw/scene"):
    os.makedirs(os.path.join(out, d), exist_ok=True)

meta_path = os.path.join(out, "assets.json")
meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}

TURN = Matrix.Rotation(math.pi, 4, "Z")  # model front -Y  ->  Roblox -Z


def select_only(objs):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def export_fbx(path, objs):
    select_only(objs)
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={"EMPTY", "MESH"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
        axis_forward="-Z", axis_up="Y", bake_space_transform=True,
        use_mesh_modifiers=True, mesh_smooth_type="FACE", use_tspace=False,
        add_leaf_bones=False, bake_anim=False, path_mode="AUTO", use_custom_props=False)


for modname in AREAS:
    if only and modname not in only and modname.replace("area_", "") not in only:
        continue
    t0 = time.time()
    mod = importlib.import_module(modname)
    stage.reset()
    kit._materials.clear()
    col = bpy.data.collections.new(mod.AREA)
    bpy.context.scene.collection.children.link(col)
    roots = []
    for fn in mod.ASSETS:
        r = fn().finish(col)
        roots.append(r)
    stage.layout(roots, gap=10)
    cam = stage.setup(mod.GROUND, res=(1920, 1080), samples=64)
    area_meta = []
    for r in roots:
        sx, sy, sz = r["size"]
        area_meta.append(dict(name=r.name, size_studs=dict(x=sx, y=sz, z=sy), tris=r["tris"], parts=r["parts"],
                              styles=sorted({c.name.split("_")[1] for c in r.children})))
    meta[mod.AREA] = area_meta

    if render:
        stage.frame(cam, roots)
        stage.render(os.path.join(out, "previews/_raw/scene", f"{mod.AREA}.png"))
        json.dump(stage.label_points(cam, roots), open(os.path.join(out, "previews/_raw/scene", f"{mod.AREA}.json"), "w"), indent=1)
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = 1200, 900
        sc.cycles.samples = 48
        for r in roots:
            for o in roots:
                for ch in o.children:
                    ch.hide_render = o is not r
            stage.frame(cam, [r], az=-28, el=26, margin=0.06)
            stage.render(os.path.join(out, "previews/_raw/solo", f"{r.name}.png"))
        for o in roots:
            for ch in o.children:
                ch.hide_render = False

    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "blend", f"{mod.AREA}.blend"), compress=True)

    # FBX: turn every asset to face -Z, export one file per asset and one per area
    for r in roots:
        for ch in r.children:
            ch.data.transform(TURN)
    os.makedirs(os.path.join(out, "fbx", mod.AREA), exist_ok=True)
    keep = {r.name: r.location.copy() for r in roots}
    for r in roots:
        r.location = (0, 0, 0)
    bpy.context.view_layer.update()
    for r in roots:
        export_fbx(os.path.join(out, "fbx", mod.AREA, f"{r.name}.fbx"), [r] + list(r.children))
    # bundle: assets in a row along x, 20 studs apart
    x = 0.0
    for r in roots:
        w = r["size"][0]
        r.location = (x + w / 2, 0, 0)
        x += w + 20.0
    bpy.context.view_layer.update()
    allobjs = [o for r in roots for o in [r] + list(r.children)]
    export_fbx(os.path.join(out, "fbx", f"{mod.AREA}.fbx"), allobjs)
    print(f"{mod.AREA}: {len(roots)} assets in {time.time() - t0:.0f}s", flush=True)
    json.dump(meta, open(meta_path, "w"), indent=1)

# style table for the Roblox side
styles = {k: v for k, v in kit.STYLES.items() if not k.startswith("_")}
json.dump(styles, open(os.path.join(out, "styles.json"), "w"), indent=1)
print("done", flush=True)
