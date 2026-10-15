"""Find floating geometry: every loose piece of every mesh must touch the body, directly or
through other pieces (a pupil on an eye on a stalk on the head is fine).

    python check_attach.py [only=Shark,Crab]      (run with the bpy venv)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blender"))
import bpy  # noqa: E402  (bpy before bmesh)
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import creatures  # noqa: E402

EPS = 0.03


def islands(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    seen, out = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            x = stack.pop()
            comp.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen:
                    seen.add(y.index)
                    stack.append(y)
        idx = {x.index for x in comp}
        faces = [f for f in bm.faces if f.verts[0].index in idx]
        verts = [x.co.copy() for x in comp]
        tri = []
        vmap = {x.index: i for i, x in enumerate(comp)}
        for f in faces:
            ids = [vmap[x.index] for x in f.verts]
            for k in range(1, len(ids) - 1):
                tri.append((ids[0], ids[k], ids[k + 1]))
        mn = Vector((min(p.x for p in verts), min(p.y for p in verts), min(p.z for p in verts)))
        mx = Vector((max(p.x for p in verts), max(p.y for p in verts), max(p.z for p in verts)))
        out.append(dict(obj=ob.name, verts=verts, bvh=BVHTree.FromPolygons(verts, tri), mn=mn, mx=mx))
    bm.free()
    return out


def touching(a, b):
    if any(a["mn"][i] > b["mx"][i] + EPS or b["mn"][i] > a["mx"][i] + EPS for i in range(3)):
        return False
    for A, B in ((a, b), (b, a)):
        step = max(1, len(A["verts"]) // 400)
        for p in A["verts"][::step]:
            hit = B["bvh"].find_nearest(p)
            if hit[0] is None:
                continue
            loc, nrm, _, d = hit
            if d < EPS or (p - loc).dot(nrm) < 0 and d < 0.6:
                return True
    return False


only = [a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("only=")]
only = only[0] if only else None
bad_total = 0
for fn in creatures.CREATURES:
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    col = bpy.data.collections.new("c")
    bpy.context.scene.collection.children.link(col)
    b = fn()
    if only and b.name not in only:
        continue
    objs = b.finish_char(col)
    isl = [i for o in objs.values() for i in islands(o)]
    root = [k for k, i in enumerate(isl) if i["obj"] in ("UpperTorso", "LowerTorso", "Head")]
    # the hood shell rests over the head: count its main shell as attached
    hood = [k for k, i in enumerate(isl) if i["obj"] in ("Head__Hood", "Head__BellGlass")]
    if hood:
        root.append(max(hood, key=lambda k: len(isl[k]["verts"])))
    linked = set(root)
    frontier = list(root)
    while frontier:
        k = frontier.pop()
        for j in range(len(isl)):
            if j not in linked and touching(isl[k], isl[j]):
                linked.add(j)
                frontier.append(j)
    bad = [isl[j] for j in range(len(isl)) if j not in linked]
    # stricter: a piece "<Part>__X" is welded to <Part>, so it has to touch that part itself
    # (the hood and the jelly bell are worn over the head, so they count as part of the head)
    for pname in {i["obj"] for i in isl if "__" in i["obj"] and i["obj"] not in ("Head__Hood", "Head__BellGlass")}:
        owner = pname.split("__")[0]
        base = (owner, "Head__Hood", "Head__BellGlass") if owner == "Head" else (owner,)
        group = [j for j, i in enumerate(isl) if i["obj"] == pname or i["obj"] in base]
        ok = {j for j in group if isl[j]["obj"] in base and (isl[j]["obj"] == owner or j in linked)}
        front = list(ok)
        while front:
            k = front.pop()
            for j in group:
                if j not in ok and touching(isl[k], isl[j]):
                    ok.add(j)
                    front.append(j)
        bad += [isl[j] for j in group if j not in ok and isl[j] not in bad]
    bad_total += len(bad)
    print(f"{b.name}: {len(isl)} pieces, {len(bad)} floating or not on their own part")
    for i in bad:
        c = (i["mn"] + i["mx"]) / 2
        print(f"   {i['obj']:<26} at ({c.x:+.2f}, {c.y:+.2f}, {c.z:+.2f})  size {tuple(round(v, 2) for v in (i['mx'] - i['mn']))}")
print("floating total:", bad_total)
