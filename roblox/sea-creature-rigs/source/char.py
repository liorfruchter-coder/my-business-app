"""Fish a Human -- sea creature character rigs: shared builder, R15 body, materials, texture bake.

Units are studs; Blender Z is up, the ground is z = 0 and the character faces -Y
(so its left side is +X). The body follows the blocky R15 layout: 5.2 studs from
the soles to the top of the head, legs to z = 2, torso 2..4, head 4..5.2.

Every R15 body part is its own mesh object, named exactly as in Roblox (Head,
UpperTorso, LeftHand ...). Creature pieces that stick out (fins, claws,
tentacles, the jelly bell) are separate objects named "<BodyPart>__<Piece>";
Roblox welds them to that body part, so the body parts keep their standard
sizes for collisions and the Head keeps the regular head shape the player's
face decal is drawn on. Small "Joint_<Name>" cubes mark the R15 joints.
"""
import math
import os
import sys
from contextlib import contextmanager

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "blender"))
import kit  # noqa: E402
from kit import PI, TAU, R, S, T, V, rmf_frames  # noqa: E402,F401

BODY_PARTS = ["Head", "UpperTorso", "LowerTorso",
              "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm", "RightLowerArm", "RightHand",
              "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg", "RightFoot"]

# R15 joints (Blender coordinates). Left = +X.
ARM_X, LEG_X = 1.5, 0.5
JOINTS = {
    "Root": (0, 0, 2.2), "Waist": (0, 0, 2.4), "Neck": (0, 0, 4.0),
    "LeftShoulder": (ARM_X, 0, 3.75), "LeftElbow": (ARM_X, 0, 2.98), "LeftWrist": (ARM_X, 0, 2.34),
    "RightShoulder": (-ARM_X, 0, 3.75), "RightElbow": (-ARM_X, 0, 2.98), "RightWrist": (-ARM_X, 0, 2.34),
    "LeftHip": (LEG_X, 0, 2.0), "LeftKnee": (LEG_X, 0, 1.1), "LeftAnkle": (LEG_X, 0, 0.36),
    "RightHip": (-LEG_X, 0, 2.0), "RightKnee": (-LEG_X, 0, 1.1), "RightAnkle": (-LEG_X, 0, 0.36),
}
HEAD_R, HEAD_Z0, HEAD_H = 0.6, 4.0, 1.2


# ---------------------------------------------------------------------------
# Materials: each style is a procedural Blender material that gets baked
# ---------------------------------------------------------------------------

def _lin(c):
    return tuple(kit.srgb_to_linear(x) for x in c) + (1.0,)


class Shader:
    def __init__(self, name):
        self.m = bpy.data.materials.new(name)
        self.m.use_nodes = True
        self.nt = self.m.node_tree
        self.N = self.nt.nodes
        self.L = self.nt.links
        self.bsdf = next(n for n in self.N if n.type == "BSDF_PRINCIPLED")
        self.tc = self.N.new("ShaderNodeTexCoord")
        self.geo = self.N.new("ShaderNodeNewGeometry")

    def rgb(self, c):
        n = self.N.new("ShaderNodeRGB")
        n.outputs[0].default_value = _lin(c)
        return n.outputs[0]

    def value(self, v):
        n = self.N.new("ShaderNodeValue")
        n.outputs[0].default_value = v
        return n.outputs[0]

    def mix(self, a, b, fac, blend="MIX"):
        n = self.N.new("ShaderNodeMix")
        n.data_type = "RGBA"
        n.blend_type = blend
        if isinstance(fac, (int, float)):
            n.inputs[0].default_value = fac
        else:
            self.L.new(fac, n.inputs[0])
        self.L.new(a, n.inputs[6])
        self.L.new(b, n.inputs[7])
        return n.outputs[2]

    def math(self, op, a, b=None, clamp=False):
        n = self.N.new("ShaderNodeMath")
        n.operation = op
        n.use_clamp = clamp
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                self.L.new(x, n.inputs[i])
        return n.outputs[0]

    def maprange(self, x, a, b, c=0.0, d=1.0):
        n = self.N.new("ShaderNodeMapRange")
        n.clamp = True
        self.L.new(x, n.inputs["Value"])
        n.inputs["From Min"].default_value = a
        n.inputs["From Max"].default_value = b
        n.inputs["To Min"].default_value = c
        n.inputs["To Max"].default_value = d
        return n.outputs["Result"]

    def sep(self, vec):
        n = self.N.new("ShaderNodeSeparateXYZ")
        self.L.new(vec, n.inputs[0])
        return n.outputs

    def voronoi(self, scale, feature="F1", rnd=1.0, vec=None):
        n = self.N.new("ShaderNodeTexVoronoi")
        n.feature = feature
        n.inputs["Scale"].default_value = scale
        n.inputs["Randomness"].default_value = rnd
        self.L.new(vec or self.tc.outputs["Object"], n.inputs["Vector"])
        return n

    def noise(self, scale, detail=3.0, vec=None):
        n = self.N.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        self.L.new(vec or self.tc.outputs["Object"], n.inputs["Vector"])
        return n

    def ellipsoid_mask(self, center, radii, soft=0.08):
        """1 inside an ellipsoid (object space), 0 outside."""
        sub = self.N.new("ShaderNodeVectorMath")
        sub.operation = "SUBTRACT"
        self.L.new(self.tc.outputs["Object"], sub.inputs[0])
        sub.inputs[1].default_value = center
        div = self.N.new("ShaderNodeVectorMath")
        div.operation = "DIVIDE"
        self.L.new(sub.outputs[0], div.inputs[0])
        div.inputs[1].default_value = radii
        ln = self.N.new("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        self.L.new(div.outputs[0], ln.inputs[0])
        return self.maprange(ln.outputs["Value"], 1.0, 1.0 - soft, 0.0, 1.0)


SCALE_TILE = os.path.join(os.path.dirname(__file__), "scales_tile.png")


def make_scale_tile(path=SCALE_TILE):
    """A tileable shingle pattern of fish scales: 1 = scale centre, 0 = scale rim."""
    if os.path.exists(path):
        return path
    import numpy as np
    from PIL import Image
    N, sp, rr = 768, 32, 22.0
    img = np.ones((N, N), dtype=np.float32)
    rows = N // (sp // 2) + 4
    for r in range(rows, -4, -1):           # bottom rows first: upper scales overlap their tops
        cy = r * (sp // 2)
        off = (r % 2) * (sp // 2)
        for c in range(-2, N // sp + 3):
            cx = c * sp + off
            x0, x1 = max(0, int(cx - rr - 1)), min(N, int(cx + rr + 2))
            y0, y1 = max(0, int(cy - rr - 1)), min(N, int(cy + rr + 2))
            if x0 >= x1 or y0 >= y1:
                continue
            ys, xs = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            d = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
            inside = d <= rr
            shade = 1.0 - 0.5 * (((ys - cy) / rr + 1) / 2)
            val = 0.28 + 0.72 * shade
            val = np.where(d > rr - 2.6, 0.0, val)
            sub = img[y0:y1, x0:x1]
            sub[inside] = val[inside]
    tile = img[256:512, 256:512]
    # Blender reads images bottom row first: flip so the scale rims point down on the model
    Image.fromarray((np.clip(tile[::-1], 0, 1) * 255).astype(np.uint8), "L").save(path)
    return path


# Painted markings: crisp shapes drawn with PIL in a front, back or side view and
# projected onto the surfaces that face that way (shark bellies, orca patches ...)
MASK_DIR = os.path.join(os.path.dirname(__file__), "masks")
PAINT_U0, PAINT_W = -2.8, 5.6       # x (front / back) or y (side), studs
PAINT_Z0, PAINT_H = -0.2, 8.0
PAINT_PX = 150                      # pixels per stud


def paint_mask(path, shapes):
    """shapes: ("poly", pts) | ("smooth", ctrl) | ("ellipse", (cu, cz, ru, rz)) | ("rect", (u0, z0, u1, z1)),
    each optionally prefixed "-" to erase. Coordinates are studs (u = x or y, z up)."""
    from PIL import Image, ImageDraw
    ss = 3
    W, H = int(PAINT_W * PAINT_PX), int(PAINT_H * PAINT_PX)
    im = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(im)

    def P(u, z):
        return ((u - PAINT_U0) * PAINT_PX * ss, (PAINT_Z0 + PAINT_H - z) * PAINT_PX * ss)
    for sh in shapes:
        kind, arg = sh
        val = 255
        if kind.startswith("-"):
            kind, val = kind[1:], 0
        if kind == "poly":
            d.polygon([P(*q) for q in arg], fill=val)
        elif kind == "smooth":
            d.polygon([P(*q) for q in smooth_outline(arg, 10)], fill=val)
        elif kind == "ellipse":
            cu, cz, ru, rz = arg
            (x0, y0), (x1, y1) = P(cu - ru, cz + rz), P(cu + ru, cz - rz)
            d.ellipse([x0, y0, x1, y1], fill=val)
        elif kind == "rect":
            u0, z0, u1, z1 = arg
            (x0, y0), (x1, y1) = P(u0, z1), P(u1, z0)
            d.rectangle([x0, y0, x1, y1], fill=val)
        else:
            raise ValueError(kind)
    im = im.resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    return path


def char_material(name, spec):
    """spec: color, [grad], [patterns], [regions], [front_clean], [rough], [emit], [alpha]."""
    sh = Shader(name)
    base = spec["color"]
    col = sh.rgb(base)
    g = spec.get("grad", 0.16)
    if g:
        z = sh.sep(sh.tc.outputs["Generated"])[2]
        dark = sh.rgb(tuple(max(0, int(c * (1 - g))) for c in base))
        col = sh.mix(dark, col, sh.maprange(z, 0.0, 0.85))
    mask = None
    if spec.get("front_clean"):
        ny = sh.sep(sh.geo.outputs["Normal"])[1]
        mask = sh.maprange(ny, -0.75, -0.35)
    for p in spec.get("patterns", []):
        kind = p[0]
        if kind == "scales":
            _, tile, edge = p
            if tile > 3:
                tile = 16.0 / tile
            tex = sh.N.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(make_scale_tile(), check_existing=True)
            tex.image.colorspace_settings.name = "Non-Color"
            tex.projection = "BOX"
            tex.projection_blend = 0.3
            sc_ = sh.N.new("ShaderNodeVectorMath")
            sc_.operation = "SCALE"
            sh.L.new(sh.tc.outputs["Object"], sc_.inputs[0])
            sc_.inputs["Scale"].default_value = 1.0 / tile
            sh.L.new(sc_.outputs[0], tex.inputs["Vector"])
            v = tex.outputs["Color"]
            bw = sh.N.new("ShaderNodeRGBToBW")
            sh.L.new(v, bw.inputs[0])
            v = bw.outputs[0]
            shade = sh.maprange(v, 0.25, 1.0, 0.86, 1.07)
            sg = sh.N.new("ShaderNodeCombineColor")
            for i in range(3):
                sh.L.new(shade, sg.inputs[i])
            shaded = sh.mix(col, sg.outputs[0], 1.0, "MULTIPLY")
            f = sh.maprange(v, 0.04, 0.2)
            if mask is not None:
                f = sh.math("MAXIMUM", f, sh.math("SUBTRACT", 1.0, mask))
                shaded = sh.mix(col, shaded, mask)
            col = sh.mix(sh.rgb(edge), shaded, f)
        elif kind in ("spots", "dots"):
            _, scale, color, size = p
            vn = sh.voronoi(scale, "F1", 1.0)
            f = sh.maprange(vn.outputs["Distance"], size, size - 0.04)
            if mask is not None:
                f = sh.math("MULTIPLY", f, mask)
            col = sh.mix(col, sh.rgb(color), f)
        elif kind == "mottle":
            _, scale, color, amount = p
            nz = sh.noise(scale, 4.0)
            f = sh.maprange(nz.outputs["Fac"], 0.45, 0.75, 0.0, amount)
            if mask is not None:
                f = sh.math("MULTIPLY", f, mask)
            col = sh.mix(col, sh.rgb(color), f)
        elif kind == "zgrad":
            # (kind, z_low, z_high, colour_at_low): blend toward a colour lower down the body
            _, zl, zh, color = p
            z = sh.sep(sh.tc.outputs["Object"])[2]
            f = sh.maprange(z, zh, zl)
            col = sh.mix(col, sh.rgb(color), f)
        elif kind == "stripes_z":
            # horizontal bands: (kind, period, color, width)
            _, period, color, width = p
            z = sh.sep(sh.tc.outputs["Object"])[2]
            fr = sh.math("FRACT", sh.math("DIVIDE", z, period))
            f = sh.math("LESS_THAN", fr, width)
            col = sh.mix(col, sh.rgb(color), f)
    for (center, radii, color, *rest) in spec.get("regions", []):
        f = sh.ellipsoid_mask(center, radii, 0.3 * (rest[0] if rest else 0.08))
        col = sh.mix(col, sh.rgb(color), f)
    for k, (view, color, shapes) in enumerate(spec.get("paint", [])):
        img = bpy.data.images.load(paint_mask(os.path.join(MASK_DIR, f"{name}_{k}.png"), shapes))
        img.colorspace_settings.name = "Non-Color"
        tex = sh.N.new("ShaderNodeTexImage")
        tex.image = img
        tex.interpolation = "Cubic"
        tex.extension = "CLIP"
        o = sh.sep(sh.tc.outputs["Object"])
        n = sh.sep(sh.geo.outputs["Normal"])
        cv = sh.N.new("ShaderNodeCombineXYZ")
        sh.L.new(sh.maprange(o[1] if view == "side" else o[0], PAINT_U0, PAINT_U0 + PAINT_W), cv.inputs[0])
        sh.L.new(sh.maprange(o[2], PAINT_Z0, PAINT_Z0 + PAINT_H), cv.inputs[1])
        sh.L.new(cv.outputs[0], tex.inputs["Vector"])
        if view == "front":
            w = sh.maprange(n[1], -0.25, -0.5)
        elif view == "back":
            w = sh.maprange(n[1], 0.25, 0.5)
        elif view == "side":
            w = sh.maprange(sh.math("ABSOLUTE", n[0]), 0.25, 0.5)
        else:
            w = sh.value(1.0)
        f = sh.math("MULTIPLY", sh.sep(tex.outputs["Color"])[0], w)
        col = sh.mix(col, sh.rgb(color), f)
    tip = spec.get("tip")
    if tip or spec.get("rays") or spec.get("edge") or spec.get("root"):
        attr = sh.N.new("ShaderNodeAttribute")
        attr.attribute_name = "Grad"
        gv = sh.sep(attr.outputs["Vector"])
        if tip:
            f = sh.maprange(gv[0], spec.get("tip_from", 0.25), 1.0)
            col = sh.mix(col, sh.rgb(tip), f)
        if spec.get("rays"):
            # the fin rays: darker lines that fade out toward the edge
            rc, amt = spec["rays"] if isinstance(spec["rays"][0], tuple) else (spec["rays"], 0.8)
            f = sh.math("MULTIPLY", sh.maprange(gv[1], 0.15, 0.9), sh.maprange(gv[0], 1.0, 0.55, 0.25, amt))
            col = sh.mix(col, sh.rgb(rc), f)
        if spec.get("edge"):
            ec, frm = spec["edge"]
            col = sh.mix(col, sh.rgb(ec), sh.maprange(gv[0], frm, frm + 0.05))
        if spec.get("root"):
            # fins start in the body colour and turn into the fin colour a little way out
            rc, r0, r1 = spec["root"] if isinstance(spec["root"][0], tuple) else (spec["root"], 0.0, 1.0)
            col = sh.mix(sh.rgb(rc), col, sh.maprange(gv[2], r0, r1))
    if spec.get("light", True):
        # a soft painted key light from above-front, baked into the texture
        n = sh.sep(sh.geo.outputs["Normal"])
        lv = sh.math("ADD", sh.math("MULTIPLY", n[2], 0.6), sh.math("MULTIPLY", n[1], -0.3))
        lf = sh.maprange(lv, -0.9, 0.9, 0.8, 1.09)
        lc = sh.N.new("ShaderNodeCombineColor")
        for i in range(3):
            sh.L.new(lf, lc.inputs[i])
        col = sh.mix(col, lc.outputs[0], 1.0, "MULTIPLY")
        ef = sh.maprange(sh.geo.outputs["Pointiness"], 0.46, 0.62, 0.95, 1.08)
        ec = sh.N.new("ShaderNodeCombineColor")
        for i in range(3):
            sh.L.new(ef, ec.inputs[i])
        col = sh.mix(col, ec.outputs[0], 1.0, "MULTIPLY")
    # fine grain so flat areas still read as a surface
    nz = sh.noise(55.0, 2.0)
    grain = sh.maprange(nz.outputs["Fac"], 0.3, 0.7, 0.96, 1.03)
    gcol = sh.N.new("ShaderNodeCombineColor")
    for i in range(3):
        sh.L.new(grain, gcol.inputs[i])
    col = sh.mix(col, gcol.outputs[0], 1.0, "MULTIPLY")
    sh.L.new(col, sh.bsdf.inputs["Base Color"])
    sh.bsdf.inputs["Roughness"].default_value = spec.get("rough", 0.5)
    return sh.m


# ---------------------------------------------------------------------------
# Builder: geometry goes into the current part; styles become material slots
# ---------------------------------------------------------------------------

class CharBuilder(kit.Builder):
    def __init__(self, name, styles):
        super().__init__(name, "Characters")
        self.styles = styles          # style name -> spec
        self.cur = None
        self.pbms = {}
        self.pmats = {}
        self.gradfn = None

    @contextmanager
    def grad(self, fn):
        """Paint a 0..1 gradient (base -> tip colour) on what is built inside."""
        prev = self.gradfn
        self.gradfn = fn
        try:
            yield
        finally:
            self.gradfn = prev

    @contextmanager
    def part(self, name):
        prev = self.cur
        self.cur = name
        try:
            yield
        finally:
            self.cur = prev

    def _bm(self, st):
        if st not in self.styles:
            raise KeyError(f"{self.name}: no style {st}")
        if self.cur not in self.pbms:
            self.pbms[self.cur] = bmesh.new()
            self.pmats[self.cur] = []
        bm = self.pbms[self.cur]
        # BMesh reuses freed slots and bevel overwrites tags, so finished faces carry a
        # "done" layer instead (bevel copies it from the face it splits)
        if not bm.faces.layers.int.get("done"):
            bm.faces.layers.int.new("done")
        return bm

    def _done(self, st, bm, f0):
        mats = self.pmats[self.cur]
        if st not in mats:
            mats.append(st)
        idx = mats.index(st)
        lay = bm.loops.layers.float_color.get("Grad") or bm.loops.layers.float_color.new("Grad")
        fn = self.gradfn
        done = bm.faces.layers.int["done"]
        for f in bm.faces:
            if not f[done]:
                f.material_index = idx
                f[done] = 1
                if fn is not None:
                    for lp in f.loops:
                        g = max(0.0, min(1.0, fn(lp.vert.co)))
                        lp[lay] = (g, g, g, 1.0)

    def _auto_bevel(self, st, size, bev):
        if bev is not None and bev != "auto":
            return bev
        m = min(abs(size[0]), abs(size[1]), abs(size[2]))
        if m < 0.12:
            return 0
        return min(0.1, m * 0.18)

    def box(self, st, c, s, rx=0.0, ry=0.0, rz=0.0, bev="auto", segs=2):
        bm = self._bm(st)
        f0 = len(bm.faces)
        M = self.M @ T(c) @ R(rx, ry, rz) @ S(s)
        ret = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
        w = self._auto_bevel(st, s, bev)
        if w > 0:
            vs = ret["verts"]
            es = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(bm, geom=vs + es, offset=w, offset_type="OFFSET", segments=segs,
                            profile=0.5, affect="EDGES", clamp_overlap=True)
        self._done(st, bm, f0)

    def ttube(self, st, pts, radii, n=10, cap=True, flat=1.0, flat_b=1.0, lift=0.0, grad=True):
        """A tube along pts whose radius follows radii (tapering tentacles, stalks)."""
        pts = [V(p) for p in pts]
        frames = rmf_frames(pts, False)
        rings = []
        for p, r, (t, nrm, bn) in zip(pts, radii, frames):
            ring = []
            for i in range(n):
                a = TAU * i / n
                ring.append(tuple(self.M @ (p + nrm * (lift * r + math.cos(a) * r * flat) + bn * math.sin(a) * r * flat_b)))
            rings.append(ring)
        k = n
        verts = [q for ring in rings for q in ring]
        faces = []
        for a in range(len(rings) - 1):
            for i in range(k):
                j = (i + 1) % k
                faces.append([a * k + i, a * k + j, (a + 1) * k + j, (a + 1) * k + i])
        if cap:
            faces.append(list(range(k))[::-1])
            last = (len(rings) - 1) * k
            faces.append(list(range(last, last + k)))
        # verts are already in world space: add them without the stack transform
        bm = self._bm(st)
        f0 = len(bm.faces)
        lay = bm.loops.layers.float_color.get("Grad") or bm.loops.layers.float_color.new("Grad")
        vs = [bm.verts.new(q) for q in verts]
        nr = len(rings)
        for f in faces:
            try:
                face = bm.faces.new([vs[i] for i in f])
            except ValueError:
                continue
            if grad and self.gradfn is None:
                for lp, i in zip(face.loops, f):
                    g = (i // k) / max(nr - 1, 1)
                    lp[lay] = (g, g, g, 1.0)
        self._done(st, bm, f0)
        return pts, frames

    def mesh_styled(self, verts, faces, styles):
        """Add verts (local coordinates) and faces (index tuples), each face with its own style."""
        for st in set(styles):
            self._bm(st)
        bm = self._bm(styles[0])
        done = bm.faces.layers.int["done"]
        mats = self.pmats[self.cur]
        vs = [bm.verts.new(self.M @ V(p)) for p in verts]
        for f, st in zip(faces, styles):
            try:
                face = bm.faces.new([vs[i] for i in f])
            except ValueError:
                continue
            if st not in mats:
                mats.append(st)
            face.material_index = mats.index(st)
            face[done] = 1
        loose = [v for v in vs if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")

    def skin_rings(self, st, sections, cap=True):
        """Skin closed rings (same point count) in order; caps close the two ends."""
        bm = self._bm(st)
        f0 = len(bm.faces)
        rings = [[bm.verts.new(self.M @ V(p)) for p in sec] for sec in sections]
        k = len(rings[0])
        for a, b_ in zip(rings, rings[1:]):
            for i in range(k):
                j = (i + 1) % k
                bm.faces.new([a[i], a[j], b_[j], b_[i]])
        if cap:
            for ring, rev in ((rings[0], True), (rings[-1], False)):
                c = bm.verts.new(sum((v.co for v in ring), V((0, 0, 0))) / k)
                for i in range(k):
                    j = (i + 1) % k
                    vs = [ring[i], ring[j], c]
                    bm.faces.new(vs[::-1] if rev else vs)
        self._done(st, bm, f0)

    def rbox(self, st, c, size, bot=(1.0, 1.0), bev=0.18, segs=4, shift=(0.0, 0.0)):
        """A rounded box whose bottom face is scaled by bot (tapered limbs, torso)."""
        sx, sy, sz = size
        bx, by = sx * bot[0] / 2, sy * bot[1] / 2
        tx, ty = sx / 2, sy / 2
        x, y, z = c
        z0, z1 = z - sz / 2, z + sz / 2
        verts = [(x - bx + shift[0], y - by + shift[1], z0), (x + bx + shift[0], y - by + shift[1], z0),
                 (x + bx + shift[0], y + by + shift[1], z0), (x - bx + shift[0], y + by + shift[1], z0),
                 (x - tx, y - ty, z1), (x + tx, y - ty, z1), (x + tx, y + ty, z1), (x - tx, y + ty, z1)]
        bm = self._bm(st)
        f0 = len(bm.faces)
        vs = [bm.verts.new(self.M @ V(p)) for p in verts]
        for f in ([3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]):
            bm.faces.new([vs[i] for i in f])
        es = list({e for v in vs for e in v.link_edges})
        if bev > 0:
            bmesh.ops.bevel(bm, geom=vs + es, offset=bev, offset_type="OFFSET", segments=segs, profile=0.5,
                            affect="EDGES", clamp_overlap=True)
        self._done(st, bm, f0)

    def fin3(self, st, ctrl, M, thick=0.14, rays=0, pleat=0.0, scallop=0.0, curl=0.0, cup=0.0, per=6, cols=None,
             rows=16, flare=1.3, flare_len=0.22, sink=0.08):
        """A cartoon fin that grows out of the body.

        ctrl: closed outline (u, v); ctrl[0] -> ctrl[1] is the base line (v ~ 0), the rest the edge.
        Local frame from M: x = u, z = v (away from the body), y = thickness.
        The fin is a grid fanned from the base line to the edge (its columns are the rays). It keeps
        an even, chunky thickness with a fully rounded rim, and flares out at the base (flare x
        thicker over flare_len studs) into a fillet that sinks into the body, so it reads as part
        of the body rather than a cut-out stuck on. With rays it gets soft ridges along them and
        a gently wavy edge.
        Grad colour: x = 0 at the base .. 1 at the edge, y = 1 on a ray, z = 0 at the base .. 1 a
        quarter stud out (styles blend from the body colour with it)."""
        out = smooth_outline(ctrl, per)
        b1, b0 = V((*ctrl[1], 0)), V((*ctrl[0], 0))
        edge = [V((u, v, 0)) for u, v in out[per:]] + [V((*out[0], 0))]
        # resample the edge evenly by arc length
        L = [0.0]
        for a, c in zip(edge, edge[1:]):
            L.append(L[-1] + (c - a).length)
        total = L[-1] or 1.0
        ncol = cols or (max(30, rays * 8) if rays else 34)
        E, k = [], 0
        for j in range(ncol):
            d = total * j / (ncol - 1)
            while k < len(L) - 2 and L[k + 1] < d:
                k += 1
            seg = (L[k + 1] - L[k]) or 1.0
            E.append(edge[k].lerp(edge[k + 1], (d - L[k]) / seg))
        us = [p.x for p in E]
        uc, uh = (max(us) + min(us)) / 2, max((max(us) - min(us)) / 2, 1e-3)
        down = V((0, -sink, 0))
        half = thick / 2
        rim = thick * 0.85
        grid_t, grid_b, gvals, lip = [], [], [], []
        for i in range(rows + 1):
            f = 0.5 - 0.5 * math.cos(math.pi * i / rows)
            rt, rb, rv = [], [], []
            for j in range(ncol):
                c = j / (ncol - 1) * rays if rays else 0.0
                on_ray = 0.5 + 0.5 * math.cos(TAU * c) if rays else 0.0
                Bj = b1.lerp(b0, j / (ncol - 1)) + down
                Ej = E[j]
                if rays and 0 < j < ncol - 1:
                    Ej = Bj + (Ej - Bj) * (1 - scallop * (1 - on_ray) * (1 - abs(2 * j / (ncol - 1) - 1)) ** 0.3)
                span = (Ej - Bj).length
                P = Bj.lerp(Ej, f)
                to_edge, from_base = (1 - f) * span, f * span
                h = half * math.sqrt(max(0.0, 1 - max(0.0, 1 - to_edge / rim) ** 2))
                h = max(h, half * 0.22) + half * flare * max(0.0, 1 - from_base / flare_len) ** 2
                w = curl * f * f + cup * ((P.x - uc) / uh) ** 2 * f
                if rays:
                    w += pleat * min(1.0, from_base / 0.3) * math.cos(TAU * c)
                rt.append(V((P.x, w + h, P.y)))
                rb.append(V((P.x, w - h, P.y)))
                rv.append((f, on_ray ** 3, min(1.0, max(0.0, (from_base - sink) / 0.22))))
                if i == rows:
                    out_d = (Ej - Bj).normalized() if span > 1e-6 else V((0, 1, 0))
                    q = P + out_d * h * 0.8
                    lip.append(V((q.x, w, q.y)))
            grid_t.append(rt)
            grid_b.append(rb)
            gvals.append(rv)
        bm = self._bm(st)
        f0 = len(bm.faces)
        lay = bm.loops.layers.float_color.get("Grad") or bm.loops.layers.float_color.new("Grad")
        Mw = self.M @ M
        vt = [[bm.verts.new(Mw @ p) for p in row] for row in grid_t]
        vb = [[bm.verts.new(Mw @ p) for p in row] for row in grid_b]
        vl = [bm.verts.new(Mw @ p) for p in lip]
        quads = []
        for i in range(rows):
            for j in range(ncol - 1):
                quads.append(([vt[i][j], vt[i][j + 1], vt[i + 1][j + 1], vt[i + 1][j]],
                              [(i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j)]))
                quads.append(([vb[i][j], vb[i + 1][j], vb[i + 1][j + 1], vb[i][j + 1]],
                              [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]))
        for j in range(ncol - 1):       # the rounded lip and the (buried) base
            quads.append(([vt[rows][j], vt[rows][j + 1], vl[j + 1], vl[j]], [(rows, j), (rows, j + 1), (rows, j + 1), (rows, j)]))
            quads.append(([vl[j], vl[j + 1], vb[rows][j + 1], vb[rows][j]], [(rows, j), (rows, j + 1), (rows, j + 1), (rows, j)]))
            quads.append(([vt[0][j + 1], vt[0][j], vb[0][j], vb[0][j + 1]], [(0, j + 1), (0, j), (0, j), (0, j + 1)]))
        for jj in (0, ncol - 1):        # the two ends of the fan
            for i in range(rows):
                quads.append(([vt[i][jj], vt[i + 1][jj], vb[i + 1][jj], vb[i][jj]], [(i, jj), (i + 1, jj), (i + 1, jj), (i, jj)]))
            quads.append(([vt[rows][jj], vl[jj], vb[rows][jj]], [(rows, jj)] * 3))
        for vs, ids in quads:
            try:
                face = bm.faces.new(vs)
            except ValueError:
                continue
            for lp, (i, j) in zip(face.loops, ids):
                g, r, z = gvals[i][j]
                lp[lay] = (g, r, z, 1.0)
        self._done(st, bm, f0)

    def eye(self, c, r, look=(0, -1, 0), white="EyeWhite", pupil="Pupil"):
        c = V(c)
        d = V(look).normalized()
        self.ball(white, tuple(c), r, seg=(16, 12))
        self.ball(pupil, tuple(c + d * r * 0.62), r * 0.52, seg=(12, 8), sc=(1, 1, 1))
        up = V((0, 0, 1))
        side = d.cross(up).normalized() if abs(d.z) < 0.9 else V((1, 0, 0))
        self.ball(white, tuple(c + d * r * 0.98 + up * r * 0.25 + side * r * 0.18), r * 0.14, seg=(8, 6))

    def finish_char(self, collection):
        self.mat_cache = {st: char_material(f"{self.name}_{st}", spec) for st, spec in self.styles.items()}
        objs = {}
        for part, bm in self.pbms.items():
            if not len(bm.faces):
                continue
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            for L in (bm.faces.layers.int, bm.verts.layers.int):
                for nm in ("done", "fresh"):
                    if L.get(nm):
                        L.remove(L[nm])
            me = bpy.data.meshes.new(part)
            bm.to_mesh(me)
            bm.free()
            for st in self.pmats[part]:
                me.materials.append(self.mat_cache[st])
            for p in me.polygons:
                p.use_smooth = True
            me.set_sharp_from_angle(angle=math.radians(38))
            ob = bpy.data.objects.new(part, me)
            collection.objects.link(ob)
            objs[part] = ob
        self.pbms = {}
        return objs


# ---------------------------------------------------------------------------
# Creature hoods: the regular head sits inside, its face shows through the mouth
# ---------------------------------------------------------------------------

def _unit(th, ph):
    t, p = math.radians(th), math.radians(ph)
    return V((math.cos(p) * math.cos(t), math.cos(p) * math.sin(t), math.sin(p)))


class Hood:
    """A creature head worn like a hoodie hat over the regular Roblox head.

    A thick shell (outer skin, inner lining, rounded rims) around the head, open at the
    bottom over the neck and with a mouth opening at the front that frames the face.
    The shell is a grid in (azimuth th, elevation ph) degrees; the mouth is a block of grid
    cells that is left out, and the grid around it is warped so the opening is a smooth
    ellipse (hole = its half-size in degrees). bumps = [(th, ph, amount, width_deg)] swell
    the shell outwards (snouts, foreheads, cheeks)."""

    def __init__(self, c=(0, 0.08, 4.62), r=(0.92, 0.94, 0.86), t=0.11, bumps=(), hole=(39.375, 34.29), phc=-2.0,
                 k=(7, 8), bottom=-49.0):
        self.c, self.r, self.t = V(c), r, t
        self.bumps = [(_unit(th, ph), amt, math.radians(w)) for th, ph, amt, w in bumps]
        self.hth, self.hph = hole
        self.kth, self.kph = k
        self.dth, self.dph = self.hth / self.kth, self.hph / self.kph
        self.n = int(round(360 / self.dth))
        self.thc, self.phc = -90.0, phc
        self.ic = int(round(self.thc / self.dth)) % self.n
        self.j0 = int(round((phc - bottom) / self.dph))
        self.jt = int((86 - phc) / self.dph)

    def radial(self, th, ph):
        d = _unit(th, ph)
        m = 1.0
        for bd, amt, w in self.bumps:
            a = math.acos(max(-1.0, min(1.0, d.dot(bd))))
            m += amt * math.exp(-a * a / (2 * w * w))
        return V((d.x * self.r[0], d.y * self.r[1], d.z * self.r[2])) * m

    def surf(self, th, ph, inner=False):
        p = self.radial(th, ph)
        if inner:
            p = p * (1 - self.t / p.length)
        return self.c + p

    def normal(self, th, ph):
        e = 0.5
        a = self.surf(th + e, ph) - self.surf(th - e, ph)
        b_ = self.surf(th, ph + e) - self.surf(th, ph - e)
        n = a.cross(b_)
        if n.length < 1e-9:
            return _unit(th, ph)
        n.normalize()
        return n if n.dot(self.surf(th, ph) - self.c) > 0 else -n

    def point(self, th, ph, out=0.0):
        """A point on (or out from) the outer skin and the outward normal there."""
        n = self.normal(th, ph)
        return self.surf(th, ph) + n * out, n

    def _angles(self, i, j):
        di = ((i - self.ic + self.n // 2) % self.n) - self.n // 2
        X, Y = di / self.kth, (j - self.j0) / self.kph
        s = max(abs(X), abs(Y))
        if 0 < s < 2.6:
            f = s / math.hypot(X, Y)
            t = min(1.0, max(0.0, (s - 1) / 1.6))
            t = t * t * (3 - 2 * t)
            sc = f + (1 - f) * t
            X, Y = X * sc, Y * sc
        return self.thc + X * self.hth, self.phc + Y * self.hph

    def in_hole(self, i, j):
        di = ((i - self.ic + self.n // 2) % self.n) - self.n // 2
        return -self.kth <= di < self.kth and self.j0 - self.kph <= j < self.j0 + self.kph

    def build(self, b, st, lining, lip, rim=None):
        """Adds the shell to the current part. Returns the lip ring (points round the mouth)."""
        n, J = self.n, self.j0 + self.jt
        verts, faces, styles = [], [], []
        ang = [[self._angles(i, j) for i in range(n)] for j in range(J + 1)]
        O = [[len(verts) + j * n + i for i in range(n)] for j in range(J + 1)]
        verts += [self.surf(*ang[j][i]) for j in range(J + 1) for i in range(n)]
        I_ = [[len(verts) + j * n + i for i in range(n)] for j in range(J + 1)]
        verts += [self.surf(*ang[j][i], inner=True) for j in range(J + 1) for i in range(n)]
        po, pi = len(verts), len(verts) + 1
        verts += [self.surf(0, 90), self.surf(0, 90, inner=True)]
        for j in range(J):
            for i in range(n):
                if self.in_hole(i, j):
                    continue
                i2 = (i + 1) % n
                faces.append((O[j][i], O[j][i2], O[j + 1][i2], O[j + 1][i]))
                styles.append(st)
                faces.append((I_[j][i], I_[j + 1][i], I_[j + 1][i2], I_[j][i2]))
                styles.append(lining)
        for i in range(n):
            i2 = (i + 1) % n
            faces.append((O[J][i], O[J][i2], po))
            styles.append(st)
            faces.append((I_[J][i2], I_[J][i], pi))
            styles.append(lining)

        def strip(loop, push, style, closed=True):
            # outer -> rounded middle -> inner along a loop of grid indices
            mids = []
            for (i, j) in loop:
                th, ph = ang[j][i]
                po_, pi_ = verts[O[j][i]], verts[I_[j][i]]
                mids.append(len(verts))
                verts.append((po_ + pi_) / 2 + push(th, ph) * self.t * 0.7)
            m = len(loop)
            for k in range(m if closed else m - 1):
                k2 = (k + 1) % m
                (i, j), (i2, j2) = loop[k], loop[k2]
                faces.append((O[j][i], mids[k], mids[k2], O[j2][i2]))
                faces.append((mids[k], I_[j][i], I_[j2][i2], mids[k2]))
                styles.extend([style, style])
            return [verts[x] for x in mids]

        strip([(i, 0) for i in range(n)], lambda th, ph: V((0, 0, -1)), rim or st)
        kt, kp, j0 = self.kth, self.kph, self.j0
        loop = ([((self.ic + a) % n, j0 - kp) for a in range(-kt, kt)] +
                [((self.ic + kt) % n, j0 - kp + a) for a in range(0, 2 * kp)] +
                [((self.ic + kt - a) % n, j0 + kp) for a in range(0, 2 * kt)] +
                [((self.ic - kt) % n, j0 + kp - a) for a in range(0, 2 * kp)])
        ring = strip(loop, self.normal, lip)
        b.mesh_styled(verts, faces, styles)
        return ring


# ---------------------------------------------------------------------------
# The standard body
# ---------------------------------------------------------------------------

def head_profile(r=HEAD_R, h=HEAD_H, rc=0.27, n=7):
    pts = [(0, 0)]
    for i in range(n + 1):
        a = -PI / 2 + PI / 2 * i / n
        pts.append((r - rc + rc * math.cos(a), rc + rc * math.sin(a)))
    for i in range(n + 1):
        a = PI / 2 * i / n
        pts.append((r - rc + rc * math.cos(a), h - rc + rc * math.sin(a)))
    pts.append((0, h))
    return pts


BODY = dict(chest=(2.0, 1.0), chest_bot=(1.0, 1.0), chest_bev=0.075, waist=(2.0, 1.0), waist_bev=0.075,
            arm=1.0, arm_bot=1.0, leg=1.0, leg_bot=1.0, limb_bev=0.075, belly=None, hand="block", foot="block",
            chest_ball=None)


def standard_body(b, st, hands=True, feet=True, shape=None):
    """st: style names for head, chest, waist, arm, forearm, hand, thigh, shin, foot.
    The R15 parts at their usual places, shaped by shape (see BODY): torso width / depth and
    taper (chest_bot scales the bottom of the chest: a V for sharks, a sack for octopuses),
    roundness (bevels), limb thickness and taper, a belly bulge (sx, sy, sz), mitt hands and
    flipper feet; chest_ball (rx, ry, rz) makes the chest a ball (pufferfish).
    With no shape it is the crisp blocky R15 body."""
    sh = dict(BODY, **(shape or {}))
    segs = 3 if sh["chest_bev"] < 0.15 else 5
    lsegs = 3 if sh["limb_bev"] < 0.15 else 4
    with b.part("Head"):
        b.lathe(st["head"], head_profile(), c=(0, 0, HEAD_Z0), n=48)
    cw, cd = sh["chest"]
    with b.part("UpperTorso"):
        if sh["chest_ball"]:
            b.ball(st["chest"], (0, 0, 3.18), 1.0, seg=(40, 28), sc=sh["chest_ball"])
        else:
            b.rbox(st["chest"], (0, 0, 3.2), (cw, cd, 1.6), bot=sh["chest_bot"], bev=sh["chest_bev"], segs=segs)
        if sh["belly"]:
            bx, by, bz = sh["belly"]
            b.ball(st["chest"], (0, -cd / 2 + by * 0.35, 3.08), 1.0, seg=(32, 20), sc=(bx, by, bz))
    ww, wd = sh["waist"]
    with b.part("LowerTorso"):
        b.rbox(st["waist"], (0, 0, 2.2), (ww, wd, 0.4), bot=(0.96, 0.96), bev=min(sh["waist_bev"], 0.18), segs=segs)
    aw, ab, lw, lb, lbev = sh["arm"], sh["arm_bot"], sh["leg"], sh["leg_bot"], sh["limb_bev"]
    for side, sx in (("Left", 1), ("Right", -1)):
        x = sx * ARM_X
        mid = aw + (ab * aw - aw) * 0.62           # forearm width where the upper arm stops
        with b.part(f"{side}UpperArm"):
            b.rbox(st["arm"], (x, 0, 3.49), (aw, aw, 1.02), bot=(mid / aw, mid / aw), bev=lbev, segs=lsegs)
        with b.part(f"{side}LowerArm"):
            b.rbox(st["forearm"], (x, 0, 2.66), (mid, mid, 0.64), bot=(ab * aw / mid, ab * aw / mid), bev=min(lbev, 0.2),
                   segs=lsegs)
        if hands:
            hw = ab * aw
            with b.part(f"{side}Hand"):
                if sh["hand"] == "mitt":
                    b.rbox(st["hand"], (x, 0, 2.15), (hw * 0.98, hw * 0.96, 0.38), bot=(0.9, 0.9), bev=min(0.16, hw * 0.2), segs=4)
                    b.rbox(st["hand"], (x - sx * hw * 0.42, -hw * 0.3, 2.2), (0.24, 0.3, 0.3), bev=0.1, segs=3)
                else:
                    b.rbox(st["hand"], (x, 0, 2.17), (hw, hw, 0.34), bev=min(lbev, 0.12), segs=3)
        xl = sx * LEG_X
        lmid = lw + (lb * lw - lw) * 0.55
        with b.part(f"{side}UpperLeg"):
            b.rbox(st["thigh"], (xl, 0, 1.55), (lw, lw, 0.9), bot=(lmid / lw, lmid / lw), bev=lbev, segs=lsegs)
        with b.part(f"{side}LowerLeg"):
            b.rbox(st["shin"], (xl, 0, 0.73), (lmid, lmid, 0.74), bot=(lb * lw / lmid, lb * lw / lmid), bev=min(lbev, 0.2),
                   segs=lsegs)
        if feet:
            fw = lb * lw
            with b.part(f"{side}Foot"):
                if sh["foot"] == "flipper":
                    # a wide, flat webbed foot that sticks out in front
                    b.rbox(st["foot"], (xl, -0.12, 0.15), (fw * 1.08, 1.24, 0.3), bot=(1.06, 1.04), bev=0.12, segs=4)
                else:
                    b.rbox(st["foot"], (xl, 0, 0.18), (fw, fw, 0.36), bev=min(lbev, 0.12), segs=3)


def smooth_outline(ctrl, per=5):
    """Closed Catmull-Rom outline through 2D control points."""
    P = [V((u, v, 0)) for u, v in ctrl]
    n = len(P)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
        for k in range(per):
            t = k / per
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)
            out.append((q.x, q.y))
    return out


def joint_markers(collection):
    for name, p in JOINTS.items():
        me = bpy.data.meshes.new("Joint_" + name)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=0.1, matrix=Matrix.Translation(V(p)))
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("Joint_" + name, me)
        collection.objects.link(ob)


# ---------------------------------------------------------------------------
# UV + bake
# ---------------------------------------------------------------------------

def unwrap(objs):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.002, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin=0.003)
    bpy.ops.object.mode_set(mode="OBJECT")


def bake_atlas(objs, path, size=1024):
    """Bake every style's colour and the ambient occlusion into one texture."""
    import numpy as np
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 64
    sc.render.bake.margin = 8
    sc.render.bake.use_clear = True
    w = sc.world or bpy.data.worlds.new("W")
    sc.world = w
    w.light_settings.distance = 0.9
    hidden = []
    for o in bpy.context.scene.objects:
        if o.name.startswith(("_Face", "Joint_")) and not o.hide_render:
            o.hide_render = True
            hidden.append(o)
    imgs = {}
    for kind in ("COLOR", "AO"):
        img = bpy.data.images.new(f"bake_{kind}", size, size, alpha=False, float_buffer=False)
        imgs[kind] = img
        mats = {m for o in objs for m in o.data.materials}
        for m in mats:
            nt = m.node_tree
            node = nt.nodes.get("BakeTarget") or nt.nodes.new("ShaderNodeTexImage")
            node.name = "BakeTarget"
            node.image = img
            nt.nodes.active = node
        for o in bpy.context.scene.objects:
            o.select_set(False)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        if kind == "COLOR":
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=8)
        else:
            sc.cycles.samples = 96
            bpy.ops.object.bake(type="AO", margin=8)
    for o in hidden:
        o.hide_render = False
    col = np.array(imgs["COLOR"].pixels[:]).reshape(size, size, 4)
    ao = np.array(imgs["AO"].pixels[:]).reshape(size, size, 4)[..., :1]
    out = col.copy()
    out[..., :3] = col[..., :3] * (0.5 + 0.5 * np.clip(ao, 0, 1) ** 0.85)
    final = bpy.data.images.new("Atlas", size, size, alpha=False)
    final.pixels = out.ravel().tolist()
    final.filepath_raw = path
    final.file_format = "PNG"
    final.save()
    return final


def atlas_materials(img, name):
    """Plain / glow / glass versions of the baked texture material."""
    mats = {}
    for kind in ("plain", "glow", "glass"):
        m = bpy.data.materials.new(f"{name}_{kind}")
        m.use_nodes = True
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.45
        if kind == "glow":
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = 2.5
        if kind == "glass":
            bsdf.inputs["Alpha"].default_value = 0.6
            bsdf.inputs["Roughness"].default_value = 0.1
        mats[kind] = m
    return mats
