"""Render a close-up of a saved rig:  python closeup.py <blend> <out.png> [az] [el] [centre z] [distance]"""
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=args[0])
az = float(args[2]) if len(args) > 2 else -18
el = float(args[3]) if len(args) > 3 else 4
sc = bpy.context.scene
cam = sc.camera
cz = float(args[4]) if len(args) > 4 else 4.95
dist = float(args[5]) if len(args) > 5 else 7.6
c = Vector((0, -0.1 if cz > 4 else 0.5, cz))
d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)),
            math.sin(math.radians(el))))
cam.location = c + d * dist
cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
cam.data.shift_x = cam.data.shift_y = 0
cam.data.lens = 85
sc.render.resolution_x = sc.render.resolution_y = 800
sc.cycles.samples = 64
sc.render.film_transparent = False
sc.render.filepath = args[1]
bpy.ops.render.render(write_still=True)
