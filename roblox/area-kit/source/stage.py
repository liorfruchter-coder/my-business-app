"""Preview staging: lay an area's assets out on a ground disc, light, frame, render, label."""
import json
import math

import addon_utils
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector as V

from kit import material, srgb_to_linear, style, STYLES, Builder

addon_utils.enable("cycles", default_set=True)


def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)


def bounds(root):
    mn = V((1e9, 1e9, 1e9))
    mx = V((-1e9, -1e9, -1e9))
    for ch in root.children:
        for c in ch.bound_box:
            w = ch.matrix_world @ V(c)
            mn = V((min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)))
            mx = V((max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)))
    return mn, mx


def layout(roots, gap=10.0, max_row=None):
    """Rows, biggest at the back; each row centred on x = 0."""
    items = []
    for r in roots:
        sx, sy, sz = r["size"]
        items.append((r, sx, sy, sz))
    items.sort(key=lambda it: -(it[1] * it[2] + it[3] * 4))
    total_w = sum(it[1] for it in items) + gap * len(items)
    max_row = max_row or max(140.0, math.sqrt(total_w * 120))
    rows, row, w = [], [], 0
    for it in items:
        if row and w + it[1] > max_row:
            rows.append(row)
            row, w = [], 0
        row.append(it)
        w += it[1] + gap
    if row:
        rows.append(row)
    y = 0.0
    placed = []
    for ri, row in enumerate(rows):
        depth = max(it[2] for it in row)
        width = sum(it[1] for it in row) + gap * (len(row) - 1)
        x = -width / 2
        for it in row:
            r = it[0]
            r.location = (x + it[1] / 2, y - depth / 2, 0)
            placed.append(r)
            x += it[1] + gap
        y -= depth + gap
    # centre the whole block on the origin
    ys = [r.location.y for r in placed]
    cy = (max(ys) + min(ys)) / 2
    for r in placed:
        r.location.y -= cy
    return placed


def setup(ground_rgb, sky_rgb=(170, 214, 240), res=(1920, 1080), samples=48, ground_r=None):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 4
    sc.cycles.transparent_max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    import os
    if os.environ.get("VT", "std") == "std":
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.view_settings.exposure = -0.35
    else:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    sc.render.film_transparent = False
    w = sc.world or bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = tuple(srgb_to_linear(c) for c in sky_rgb) + (1,)
    bg.inputs[1].default_value = 0.55
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.8
    sun.data.angle = math.radians(6)
    sun.rotation_euler = (math.radians(44), 0, math.radians(-38))
    sc.collection.objects.link(sun)
    style("_Ground", tuple(int(c * 0.8) for c in ground_rgb), "Sand", rough=0.95)
    gm = bpy.data.meshes.new("Ground")
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=ground_r or 4000)
    bm.to_mesh(gm)
    bm.free()
    gm.materials.append(material("_Ground"))
    g = bpy.data.objects.new("Ground", gm)
    g.location.z = -0.02
    sc.collection.objects.link(g)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.lens = 38
    cam.data.clip_end = 5000
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def frame(cam, roots, az=-22, el=30, margin=0.04):
    bpy.context.view_layer.update()
    cam.data.shift_x = cam.data.shift_y = 0
    pts = []
    for r in roots:
        mn, mx = bounds(r)
        for x in (mn.x, mx.x):
            for y in (mn.y, mx.y):
                for z in (mn.z, mx.z):
                    pts.append(V((x, y, z)))
    c = sum(pts, V()) / len(pts)
    d = V((math.sin(math.radians(az)) * math.cos(math.radians(el)),
           -math.cos(math.radians(az)) * math.cos(math.radians(el)),
           math.sin(math.radians(el))))
    sc = bpy.context.scene
    look = (-d).to_track_quat("-Z", "Y")
    cam.rotation_euler = look.to_euler()

    def fits(dist):
        cam.location = c + d * dist
        bpy.context.view_layer.update()
        for p in pts:
            q = world_to_camera_view(sc, cam, p)
            if q.z <= 0 or not (margin <= q.x <= 1 - margin and margin + 0.05 <= q.y <= 1 - margin - 0.05):
                return False
        return True

    lo, hi = 5.0, 5000.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if fits(mid):
            hi = mid
        else:
            lo = mid
    cam.location = c + d * hi
    # re-centre the frame on the projected bounds
    bpy.context.view_layer.update()
    qs = [world_to_camera_view(sc, cam, p) for p in pts]
    cx = (min(q.x for q in qs) + max(q.x for q in qs)) / 2 - 0.5
    cy = (min(q.y for q in qs) + max(q.y for q in qs)) / 2 - 0.5
    cam.data.shift_x = cx
    cam.data.shift_y = cy * sc.render.resolution_y / sc.render.resolution_x
    bpy.context.view_layer.update()


def label_points(cam, roots):
    bpy.context.view_layer.update()
    sc = bpy.context.scene
    out = []
    for r in roots:
        mn, mx = bounds(r)
        top = V(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mx.z + 1.5))
        base = V(((mn.x + mx.x) / 2, mn.y, 0))
        q = world_to_camera_view(sc, cam, top)
        qb = world_to_camera_view(sc, cam, base)
        out.append(dict(name=r.name, x=q.x, y=1 - q.y, bx=qb.x, by=1 - qb.y,
                        size=list(r["size"]), tris=r["tris"]))
    return out


def render(path):
    sc = bpy.context.scene
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
