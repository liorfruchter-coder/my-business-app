"""Build, bake, render and export the sea creature rigs.

    python build.py <out_dir> [draft|final] [only=Crab,Orca] [--no-export] [--lineup]
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import bpy  # noqa: E402
import addon_utils  # noqa: E402
import bmesh  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Matrix, Vector as V  # noqa: E402

import char  # noqa: E402
import creatures  # noqa: E402

addon_utils.enable("cycles", default_set=True)
addon_utils.enable("io_scene_fbx", default_set=True)

out = os.path.abspath(sys.argv[1])
quality = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith(("only=", "--")) else "draft"
only = None
for a in sys.argv[2:]:
    if a.startswith("only="):
        only = set(a[5:].split(","))
do_export = "--no-export" not in sys.argv
final = quality == "final"
for d in ("fbx", "textures", "blend", "previews/_raw"):
    os.makedirs(os.path.join(out, d), exist_ok=True)

TURN = Matrix.Rotation(math.pi, 4, "Z")


def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.lights, bpy.data.cameras):
        for x in list(block):
            if x.users == 0:
                block.remove(x)


def face_image():
    """The classic Roblox smile, for previews only (the game uses the player's own face)."""
    path = os.path.join(out, "previews", "_raw", "face.png")
    if not os.path.exists(path):
        from PIL import Image, ImageDraw
        im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for cx in (192, 320):
            d.ellipse([cx - 26, 150, cx + 26, 262], fill=(18, 18, 22, 255))
        d.arc([150, 190, 362, 372], 25, 155, fill=(18, 18, 22, 255), width=20)
        im.save(path)
    return bpy.data.images.load(path, check_existing=True)


def face_preview(col):
    a0, a1 = math.radians(-90 - 52), math.radians(-90 + 52)
    z0, z1 = 4.22, 4.98
    r = char.HEAD_R + 0.006
    nu, nv = 18, 6
    me = bpy.data.meshes.new("_Face")
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    vs = [[bm.verts.new((math.cos(a0 + (a1 - a0) * i / nu) * r, math.sin(a0 + (a1 - a0) * i / nu) * r, z0 + (z1 - z0) * j / nv))
           for j in range(nv + 1)] for i in range(nu + 1)]
    for i in range(nu):
        for j in range(nv):
            f = bm.faces.new([vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]])
            for lp, (ii, jj) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uv].uv = (1 - ii / nu, jj / nv)
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.new("FaceDecal")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = face_image()
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.6
    me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("_Face", me)
    col.objects.link(ob)
    return ob


def studio(res, samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 6
    sc.cycles.transparent_max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = -0.1
    w = sc.world or bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.56, 0.59, 0.64, 1)
    bg.inputs[1].default_value = 0.7
    for name, energy, rot, size in (("Key", 700, (50, 0, -40), 6), ("Fill", 240, (68, 0, 115), 8), ("Rim", 520, (58, 0, 165), 4)):
        L = bpy.data.objects.new(name, bpy.data.lights.new(name, "AREA"))
        L.data.energy = energy
        L.data.size = size
        d = V((math.sin(math.radians(rot[2])) * math.sin(math.radians(rot[0])),
               -math.cos(math.radians(rot[2])) * math.sin(math.radians(rot[0])), math.cos(math.radians(rot[0]))))
        L.location = V((0, 0, 3)) + d * 12
        L.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(L)
    gm = bpy.data.meshes.new("Floor")
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=400)
    bm.to_mesh(gm)
    bm.free()
    fm = bpy.data.materials.new("FloorMat")
    fm.use_nodes = True
    fb = next(n for n in fm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    fb.inputs["Base Color"].default_value = (0.46, 0.48, 0.52, 1)
    fb.inputs["Roughness"].default_value = 0.8
    gm.materials.append(fm)
    g = bpy.data.objects.new("Floor", gm)
    g.is_shadow_catcher = True
    sc.collection.objects.link(g)
    # transparent film: lineup.py lays the cards (with their shadows) on a clean studio backdrop
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = "RGBA"
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.lens = 60
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def bounds(objs):
    bpy.context.view_layer.update()
    mn = V((1e9, 1e9, 1e9))
    mx = V((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ V(c)
            mn = V((min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)))
            mx = V((max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)))
    return mn, mx


def frame(cam, objs, az=-25, el=12, margin=0.05, box=None):
    sc = bpy.context.scene
    cam.data.shift_x = cam.data.shift_y = 0
    mn, mx = box if box else bounds(objs)
    mn, mx = V(mn), V(mx)
    pts = [V((x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
    c = (mn + mx) / 2
    d = V((math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)),
           math.sin(math.radians(el))))
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()

    def fits(dist):
        cam.location = c + d * dist
        bpy.context.view_layer.update()
        for p in pts:
            q = world_to_camera_view(sc, cam, p)
            if q.z <= 0 or not (margin <= q.x <= 1 - margin and margin <= q.y <= 1 - margin):
                return False
        return True

    lo, hi = 2.0, 3000.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if fits(mid):
            hi = mid
        else:
            lo = mid
    cam.location = c + d * hi
    bpy.context.view_layer.update()
    qs = [world_to_camera_view(sc, cam, p) for p in pts]
    cam.data.shift_x = (min(q.x for q in qs) + max(q.x for q in qs)) / 2 - 0.5
    cam.data.shift_y = ((min(q.y for q in qs) + max(q.y for q in qs)) / 2 - 0.5) * sc.render.resolution_y / sc.render.resolution_x
    bpy.context.view_layer.update()


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def export_fbx(path, objs):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={"MESH"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
        axis_forward="-Z", axis_up="Y", bake_space_transform=True,
        use_mesh_modifiers=True, mesh_smooth_type="OFF", use_tspace=False,
        add_leaf_bones=False, bake_anim=False, path_mode="COPY", embed_textures=True, use_custom_props=False)


meta_path = os.path.join(out, "rigs.json")
meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}

for fn in creatures.CREATURES:
    reset()
    col = bpy.data.collections.new("Rig")
    bpy.context.scene.collection.children.link(col)
    t0 = time.time()
    if only and not any(o.startswith("".join(w.capitalize() for w in fn.__name__.split("_"))) for o in only):
        continue
    b = fn()
    name = b.name
    if only and name not in only:
        continue
    objs = b.finish_char(col)
    char.joint_markers(col)
    face = face_preview(col)
    parts = list(objs.values())
    char.unwrap(parts)
    tex_path = os.path.join(out, "textures", f"{name}.png")
    img = char.bake_atlas(parts, tex_path, 1024)
    mats = char.atlas_materials(img, name)
    for o in parts:
        kind = "glow" if "Glow" in o.name else ("glass" if "Glass" in o.name else "plain")
        o.data.materials.clear()
        o.data.materials.append(mats[kind])
    for o in parts:
        # the gradient attribute only drives the bake; Roblox could read it as vertex colour
        for a in list(o.data.color_attributes):
            o.data.color_attributes.remove(a)
    tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in parts}
    mn, mx = bounds([objs[p] for p in char.BODY_PARTS if p in objs])
    amn, amx = bounds(parts)
    meta[name] = dict(display=creatures.NAMES[name], parts=sorted(objs.keys()), tris=sum(tris.values()),
                      max_part_tris=max(tris.values()), body_height=round(mx.z - mn.z, 3),
                      full_size=[round(amx.x - amn.x, 2), round(amx.z - amn.z, 2), round(amx.y - amn.y, 2)])
    print(f"{name}: {len(parts)} parts, {sum(tris.values())} tris, body height {mx.z - mn.z:.2f}, bake {time.time() - t0:.0f}s", flush=True)

    # previews: the same fixed framing for every creature, so they line up at one scale
    cam = studio((800, 1000) if final else (480, 600), 128 if final else 24)
    for o in bpy.data.objects:
        if o.name.startswith("Joint_"):
            o.hide_render = True
    CARD = ((-3.1, -1.0, 0.0), (3.1, 2.4, 7.5))
    frame(cam, parts, az=-32, el=7, margin=0.02, box=CARD)
    render(os.path.join(out, "previews", "_raw", f"{name}_front.png"))
    face.hide_render = True
    frame(cam, parts, az=142, el=9, margin=0.02, box=CARD)
    render(os.path.join(out, "previews", "_raw", f"{name}_back.png"))
    face.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "blend", f"{name}.blend"), compress=True)

    if do_export:
        exp = parts + [o for o in bpy.data.objects if o.name.startswith("Joint_")]
        for o in exp:
            o.data.transform(TURN)
        export_fbx(os.path.join(out, "fbx", f"{name}.fbx"), exp)
        for o in exp:
            o.data.transform(TURN)
    json.dump(meta, open(meta_path, "w"), indent=1)
    print(f"{name}: done in {time.time() - t0:.0f}s", flush=True)

print("all done", flush=True)
