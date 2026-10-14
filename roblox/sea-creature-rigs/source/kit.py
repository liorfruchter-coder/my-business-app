"""Fish a Human -- area building kit: modelling helpers.

Units: 1 Blender unit = 1 stud. Z is up while modelling, the ground is z = 0,
and every asset is modelled with its FRONT facing -Y (toward the preview
camera). export.py turns it to face -Z in Roblox.

Each asset is a Builder: geometry goes into one bmesh per style (WoodLight,
Glass, Lava...), and each style becomes one mesh object named
"<Asset>_<Style>" (or "<Asset>_<Style>_<n>" when a style passes the triangle
budget and is split), so in Roblox every asset is a handful of MeshParts
whose names say what colour and material they take (AreaKitStyles.lua).
"""
import math
import random
import zlib
from contextlib import contextmanager

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

V = Vector
PI = math.pi
TAU = 2 * math.pi
I4 = Matrix.Identity(4)

CHUNK_TRIS = 9000  # per MeshPart (Roblox allows 20k; stay well under)


def T(x, y=None, z=None):
    if y is None:
        return Matrix.Translation(V(x))
    return Matrix.Translation(V((x, y, z)))


def R(rx=0.0, ry=0.0, rz=0.0):
    return Euler((rx, ry, rz), "XYZ").to_matrix().to_4x4()


def S(s):
    if isinstance(s, (int, float)):
        s = (s, s, s)
    return Matrix.Diagonal(V((s[0], s[1], s[2], 1.0)))


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------------------
# Styles: what each part looks like (preview material + Roblox Material)
# ---------------------------------------------------------------------------

STYLES = {}


def style(name, rgb, mat="SmoothPlastic", rough=0.55, metal=0.0, emit=0.0, alpha=1.0, bevel=True):
    STYLES[name] = dict(rgb=rgb, mat=mat, rough=rough, metal=metal, emit=emit, alpha=alpha, bevel=bevel)


# neutrals
style("White", (246, 246, 242))
style("OffWhite", (238, 230, 214), "Plaster")
style("Cream", (250, 238, 208), "Plaster")
style("Grey", (150, 152, 158), "Concrete")
style("Charcoal", (52, 54, 60))
style("Black", (30, 30, 34))
style("Concrete", (178, 178, 182), "Concrete")
style("Asphalt", (70, 72, 78), "Asphalt")
style("Metal", (172, 178, 186), "Metal", rough=0.35, metal=0.8)
style("DarkMetal", (74, 78, 88), "Metal", rough=0.4, metal=0.7)
style("Rust", (150, 82, 48), "CorrodedMetal", rough=0.8)
style("Gold", (246, 192, 58), "Foil", rough=0.25, metal=0.9)
style("Brass", (214, 164, 70), "Metal", rough=0.3, metal=0.85)
style("Copper", (200, 120, 70), "Metal", rough=0.35, metal=0.85)
style("Rubber", (36, 36, 40), "Rubber", rough=0.9)
style("Glass", (150, 214, 245), "Glass", rough=0.05, alpha=0.45, bevel=False)
style("GlassDark", (60, 96, 140), "Glass", rough=0.05, alpha=0.75, bevel=False)
style("Water", (70, 176, 232), "Glass", rough=0.05, alpha=0.6, bevel=False)
style("WindowGlow", (255, 222, 140), "Neon", emit=2.2, bevel=False)
# wood + plants
style("WoodLight", (214, 170, 118), "Wood")
style("Plank", (188, 138, 90), "WoodPlanks")
style("WoodDark", (124, 84, 54), "WoodPlanks")
style("WoodRed", (150, 64, 48), "WoodPlanks")
style("Driftwood", (196, 180, 156), "Wood")
style("Bark", (104, 70, 44), "Wood", rough=0.9)
style("Bamboo", (204, 190, 104), "Wood")
style("BambooDark", (150, 136, 64), "Wood")
style("Thatch", (220, 184, 106), "Fabric", rough=0.95)
style("ThatchDark", (176, 140, 72), "Fabric", rough=0.95)
style("Rope", (204, 174, 124), "Fabric", rough=0.95, bevel=False)
style("Leaf", (74, 180, 76), "Grass", rough=0.8)
style("LeafDark", (42, 134, 64), "LeafyGrass", rough=0.8)
style("LeafLight", (130, 206, 92), "Grass", rough=0.8)
style("Grass", (96, 182, 84), "Grass", rough=0.9)
style("Hedge", (58, 146, 72), "LeafyGrass", rough=0.9)
style("Flower", (250, 120, 160), "SmoothPlastic", bevel=False)
# stone + earth
style("Stone", (156, 154, 158), "Cobblestone", rough=0.85)
style("StoneDark", (110, 108, 114), "Slate", rough=0.85)
style("Rock", (128, 118, 110), "Rock", rough=0.9)
style("Sand", (240, 214, 156), "Sand", rough=0.95)
style("Sandstone", (228, 192, 130), "Sandstone", rough=0.85)
style("SandstoneDark", (192, 150, 92), "Sandstone", rough=0.85)
style("SandstoneLight", (240, 214, 166), "Sandstone", rough=0.85)
style("Adobe", (206, 146, 100), "Plaster", rough=0.9)
style("AdobeLight", (226, 178, 128), "Plaster", rough=0.9)
style("Marble", (242, 240, 234), "Marble", rough=0.3)
style("MarbleDark", (60, 62, 70), "Marble", rough=0.3)
style("Brick", (178, 84, 62), "Brick", rough=0.85)
style("Basalt", (58, 52, 58), "Basalt", rough=0.85)
style("BasaltLight", (98, 88, 92), "Slate", rough=0.85)
style("Obsidian", (34, 26, 44), "Glass", rough=0.15, metal=0.2)
style("Lava", (255, 104, 28), "Neon", emit=4.0, bevel=False)
style("LavaDim", (210, 70, 30), "CrackedLava", emit=0.8)
style("Fire", (255, 178, 60), "Neon", emit=6.0, bevel=False)
style("Ember", (255, 70, 30), "Neon", emit=4.0, bevel=False)
style("Snow", (250, 252, 255), "Snow", rough=0.9)
style("Ice", (176, 222, 250), "Ice", rough=0.1, alpha=0.82)
style("IceDeep", (110, 180, 236), "Glacier", rough=0.15)
style("IceGlow", (150, 230, 255), "Neon", emit=2.5, bevel=False)
# colours
style("Red", (222, 62, 62))
style("RedDark", (160, 40, 44))
style("Pink", (250, 146, 192))
style("HotPink", (232, 62, 150))
style("Coral", (250, 128, 104))
style("Peach", (252, 196, 156))
style("Orange", (250, 142, 42))
style("Yellow", (255, 212, 64))
style("Lemon", (255, 240, 140))
style("Mint", (156, 232, 200))
style("Green", (80, 190, 92))
style("Teal", (36, 166, 176))
style("Turquoise", (52, 196, 196))
style("SkyBlue", (124, 202, 246))
style("Blue", (58, 128, 230))
style("Navy", (30, 48, 98))
style("Lilac", (196, 166, 240))
style("Purple", (146, 88, 220))
style("Plum", (96, 48, 120))
style("Waffle", (222, 164, 84))
style("Chocolate", (112, 66, 42))
style("Cherry", (210, 30, 50))
# space
style("MoonWhite", (234, 237, 244))
style("MoonPanel", (186, 192, 206), "DiamondPlate", rough=0.5, metal=0.3)
style("MoonDark", (64, 68, 84), "Metal", rough=0.5, metal=0.4)
style("Solar", (38, 62, 150), "Glass", rough=0.1, metal=0.3, bevel=False)
style("NeonPurple", (186, 120, 255), "Neon", emit=3.0, bevel=False)
style("NeonCyan", (90, 228, 255), "Neon", emit=3.0, bevel=False)
style("NeonPink", (255, 90, 190), "Neon", emit=3.0, bevel=False)
style("NeonGreen", (110, 255, 140), "Neon", emit=3.0, bevel=False)
style("NeonRed", (255, 60, 60), "Neon", emit=3.0, bevel=False)
style("NeonYellow", (255, 226, 90), "Neon", emit=3.0, bevel=False)
style("NeonWhite", (255, 252, 236), "Neon", emit=3.0, bevel=False)
# tinted per placement in Roblox (AreaKitStyles: Accent / Party)
style("Accent", (232, 96, 96))
style("Party", (90, 190, 250))


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


_materials = {}


def material(st):
    if st in _materials:
        return _materials[st]
    d = STYLES[st]
    m = bpy.data.materials.new("M_" + st)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    col = tuple(srgb_to_linear(c) for c in d["rgb"]) + (1.0,)
    bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = d["rough"]
    bsdf.inputs["Metallic"].default_value = d["metal"]
    if d["emit"] > 0:
        bsdf.inputs["Emission Color"].default_value = col
        bsdf.inputs["Emission Strength"].default_value = d["emit"]
    if d["alpha"] < 1.0:
        bsdf.inputs["Alpha"].default_value = d["alpha"]
    m.diffuse_color = col
    _materials[st] = m
    return m


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

_fonts = {}
FONT_FILES = {
    "bold": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
}


def _font(key):
    if key not in _fonts:
        _fonts[key] = bpy.data.fonts.load(FONT_FILES[key])
    return _fonts[key]


def rmf_frames(pts, closed=False, up=V((0, 0, 1))):
    """Rotation-minimising frames (double reflection) along a polyline."""
    n = len(pts)
    tans = []
    for i in range(n):
        if closed:
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        tans.append((b - a).normalized())
    t0 = tans[0]
    r0 = (up - t0 * up.dot(t0))
    if r0.length < 1e-6:
        r0 = V((1, 0, 0)) - t0 * t0.x
    r0.normalize()
    frames = [(t0, r0, t0.cross(r0))]
    for i in range(n - 1):
        t_i, r_i, _ = frames[-1]
        v1 = pts[i + 1] - pts[i]
        c1 = v1.dot(v1)
        if c1 < 1e-12:
            frames.append(frames[-1])
            continue
        rL = r_i - (2 / c1) * v1.dot(r_i) * v1
        tL = t_i - (2 / c1) * v1.dot(t_i) * v1
        v2 = tans[i + 1] - tL
        c2 = v2.dot(v2)
        r_next = rL - (2 / c2) * v2.dot(rL) * v2 if c2 > 1e-12 else rL
        frames.append((tans[i + 1], r_next.normalized(), tans[i + 1].cross(r_next).normalized()))
    return frames


class Builder:
    def __init__(self, name, area, size_hint=""):
        self.name = name
        self.area = area
        self.parts = {}
        self.tris = {}
        self.stack = [I4.copy()]
        self.rng = random.Random(zlib.crc32(name.encode()))
        self.note = size_hint

    # --- transform stack ---------------------------------------------------
    @property
    def M(self):
        return self.stack[-1]

    @contextmanager
    def at(self, *mats):
        M = I4.copy()
        for m in mats:
            M = M @ m
        self.stack.append(self.stack[-1] @ M)
        try:
            yield
        finally:
            self.stack.pop()

    # --- bookkeeping -------------------------------------------------------
    def _bm(self, st):
        if st not in STYLES:
            raise KeyError("unknown style " + st)
        lst = self.parts.setdefault(st, [bmesh.new()])
        return lst[-1]

    def _done(self, st, bm, f0):
        bm.faces.ensure_lookup_table()
        t = 0
        for i in range(f0, len(bm.faces)):
            t += len(bm.faces[i].verts) - 2
        self.tris[st] = self.tris.get(st, 0) + t
        if self.tris[st] > CHUNK_TRIS:
            self.parts[st].append(bmesh.new())
            self.tris[st] = 0

    def _auto_bevel(self, st, size, bev):
        if bev is not None and bev != "auto":
            return bev
        if not STYLES[st]["bevel"]:
            return 0
        m = min(abs(size[0]), abs(size[1]), abs(size[2]))
        if m < 0.7:
            return 0
        return min(0.3, m * 0.1)

    # --- primitives --------------------------------------------------------
    def box(self, st, c, s, rx=0.0, ry=0.0, rz=0.0, bev="auto"):
        bm = self._bm(st)
        f0 = len(bm.faces)
        M = self.M @ T(c) @ R(rx, ry, rz) @ S(s)
        ret = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
        w = self._auto_bevel(st, s, bev)
        if w > 0:
            vs = ret["verts"]
            es = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(bm, geom=vs + es, offset=w, offset_type="OFFSET", segments=1,
                            profile=0.5, affect="EDGES", clamp_overlap=True)
        self._done(st, bm, f0)

    def bx(self, st, x0, x1, y0, y1, z0, z1, **kw):
        self.box(st, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                 (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), **kw)

    def cyl(self, st, p0, p1, r, n=12, r2=None, caps=True):
        p0, p1 = V(p0), V(p1)
        d = p1 - p0
        L = d.length
        if L < 1e-6:
            return
        q = V((0, 0, 1)).rotation_difference(d.normalized())
        M = self.M @ T((p0 + p1) / 2) @ q.to_matrix().to_4x4()
        bm = self._bm(st)
        f0 = len(bm.faces)
        rb = r
        rt = r if r2 is None else r2
        ret = bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=n,
                                    radius1=max(rb, 1e-4), radius2=max(rt, 1e-4), depth=L, matrix=M)
        if rb < 1e-3 or rt < 1e-3:
            bmesh.ops.remove_doubles(bm, verts=ret["verts"], dist=1e-3)
        self._done(st, bm, f0)

    def cylz(self, st, x, y, z0, z1, r, n=12, r2=None, caps=True):
        self.cyl(st, (x, y, z0), (x, y, z1), r, n, r2, caps)

    def ball(self, st, c, r, seg=(12, 8), sc=(1, 1, 1), rx=0.0, ry=0.0, rz=0.0, ico=None):
        bm = self._bm(st)
        f0 = len(bm.faces)
        M = self.M @ T(c) @ R(rx, ry, rz) @ S((r * sc[0], r * sc[1], r * sc[2]))
        if ico is not None:
            bmesh.ops.create_icosphere(bm, subdivisions=ico, radius=1.0, matrix=M)
        else:
            bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=1.0, matrix=M)
        self._done(st, bm, f0)

    def rock(self, st, c, r, sc=(1, 1, 1), jitter=0.22, sub=1, rz=None, flat_bottom=True):
        """A faceted low-poly rock / bush: an icosphere with its points pushed about."""
        bm = self._bm(st)
        f0 = len(bm.faces)
        ret = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0, matrix=I4)
        rng = self.rng
        for v in ret["verts"]:
            k = 1 + rng.uniform(-jitter, jitter)
            v.co = v.co * k
            if flat_bottom and v.co.z < -0.35:
                v.co.z = -0.35
        rz = rng.uniform(0, TAU) if rz is None else rz
        M = self.M @ T(c) @ R(0, 0, rz) @ S((r * sc[0], r * sc[1], r * sc[2]))
        bmesh.ops.transform(bm, matrix=M, verts=ret["verts"])
        self._done(st, bm, f0)

    def dome(self, st, c, r, seg=16, rings=6, sc=(1, 1, 1), rx=0.0, ry=0.0, rz=0.0, cap=True):
        """The top half of a sphere, base on c."""
        bm = self._bm(st)
        f0 = len(bm.faces)
        ret = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings * 2, radius=1.0, matrix=I4)
        low = [v for v in ret["verts"] if v.co.z < -1e-4]
        bmesh.ops.delete(bm, geom=low, context="VERTS")
        keep = [v for v in ret["verts"] if v.is_valid]
        if cap:
            edges = list({e for v in keep for e in v.link_edges if e.is_boundary})
            if edges:
                bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        M = self.M @ T(c) @ R(rx, ry, rz) @ S((r * sc[0], r * sc[1], r * sc[2]))
        bmesh.ops.transform(bm, matrix=M, verts=keep)
        self._done(st, bm, f0)

    def mesh(self, st, verts, faces):
        """Raw geometry in the current frame."""
        bm = self._bm(st)
        f0 = len(bm.faces)
        vs = [bm.verts.new(self.M @ V(p)) for p in verts]
        for f in faces:
            try:
                bm.faces.new([vs[i] for i in f])
            except ValueError:
                pass
        self._done(st, bm, f0)

    def extrude(self, st, pts, vec):
        """A planar polygon (3D points) pushed along vec into a solid."""
        n = len(pts)
        vec = V(vec)
        verts = [V(p) for p in pts] + [V(p) + vec for p in pts]
        faces = [list(range(n))[::-1], list(range(n, 2 * n))]
        for i in range(n):
            j = (i + 1) % n
            faces.append([i, j, n + j, n + i])
        self.mesh(st, verts, faces)

    def prism_y(self, st, pts_xz, y0, y1):
        self.extrude(st, [(x, y0, z) for x, z in pts_xz], (0, y1 - y0, 0))

    def prism_x(self, st, pts_yz, x0, x1):
        self.extrude(st, [(x0, y, z) for y, z in pts_yz], (x1 - x0, 0, 0))

    def prism_z(self, st, pts_xy, z0, z1):
        self.extrude(st, [(x, y, z0) for x, y in pts_xy], (0, 0, z1 - z0))

    def loft(self, st, rings, cap0=True, cap1=True, closed=True):
        """Quads between rings of equal length (each a list of 3D points)."""
        k = len(rings[0])
        verts = [p for ring in rings for p in ring]
        faces = []
        for a in range(len(rings) - 1):
            for i in range(k if closed else k - 1):
                j = (i + 1) % k
                faces.append([a * k + i, a * k + j, (a + 1) * k + j, (a + 1) * k + i])
        if cap0:
            faces.append(list(range(k))[::-1])
        if cap1:
            last = (len(rings) - 1) * k
            faces.append(list(range(last, last + k)))
        self.mesh(st, verts, faces)

    def lathe(self, st, prof, c=(0, 0, 0), n=16, a0=0.0, a1=TAU, sc=(1, 1), cap=True):
        """Turn a (radius, z) profile, bottom to top, round the z axis."""
        verts, rows = [], []
        full = abs((a1 - a0) - TAU) < 1e-6
        cnt = n if full else n + 1
        for r, z in prof:
            if r < 1e-4:
                rows.append([len(verts)])
                verts.append((c[0], c[1], c[2] + z))
                continue
            row = []
            for i in range(cnt):
                a = a0 + (a1 - a0) * i / n
                row.append(len(verts))
                verts.append((c[0] + math.cos(a) * r * sc[0], c[1] + math.sin(a) * r * sc[1], c[2] + z))
            rows.append(row)
        faces = []
        for A, B in zip(rows, rows[1:]):
            if len(A) == 1 and len(B) == 1:
                continue
            if len(A) == 1:
                for i in range(len(B) - (0 if full else 1)):
                    faces.append([A[0], B[i], B[(i + 1) % len(B)]])
            elif len(B) == 1:
                for i in range(len(A) - (0 if full else 1)):
                    faces.append([A[(i + 1) % len(A)], A[i], B[0]])
            else:
                for i in range(len(A) - (0 if full else 1)):
                    j = (i + 1) % len(A)
                    faces.append([A[i], A[j], B[j], B[i]])
        if cap and full and len(rows[0]) > 1:
            faces.append(rows[0][::-1])
        if cap and full and len(rows[-1]) > 1:
            faces.append(rows[-1])
        self.mesh(st, verts, faces)

    def tube(self, st, path, r, n=8, closed=False, cap=True, frames=None, sc=(1, 1)):
        pts = [V(p) for p in path]
        frames = frames or rmf_frames(pts, closed)
        rings = []
        for p, (t, nrm, bn) in zip(pts, frames):
            ring = []
            for i in range(n):
                a = TAU * i / n
                ring.append(p + nrm * math.cos(a) * r * sc[0] + bn * math.sin(a) * r * sc[1])
            rings.append(ring)
        if closed:
            rings.append(rings[0])
        self.loft(st, rings, cap0=cap and not closed, cap1=cap and not closed)

    def torus(self, st, c, R_, r, nmaj=24, nmin=8, rx=0.0, ry=0.0, rz=0.0, a0=0.0, a1=TAU):
        full = abs((a1 - a0) - TAU) < 1e-6
        cnt = nmaj if full else nmaj + 1
        path = [V((math.cos(a0 + (a1 - a0) * i / nmaj) * R_, math.sin(a0 + (a1 - a0) * i / nmaj) * R_, 0)) for i in range(cnt)]
        with self.at(T(c), R(rx, ry, rz)):
            frames = []
            for p in path:
                tng = V((-p.y, p.x, 0)).normalized()
                frames.append((tng, p.normalized(), tng.cross(p.normalized())))
            self.tube(st, path, r, nmin, closed=full, frames=frames)

    def ring(self, st, c, r_out, r_in, z0, z1, n=24):
        """A flat washer / round wall."""
        self.lathe(st, [(r_in, z0), (r_out, z0), (r_out, z1), (r_in, z1), (r_in, z0)], c=c, n=n, cap=False)

    def arch(self, st, c, r_in, r_out, depth, a0=0.0, a1=PI, n=10, rz=0.0):
        """An arch ring in the XZ plane (opening toward -Y), centred on c."""
        pts = []
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            pts.append((math.cos(a) * r_out, math.sin(a) * r_out))
        for i in range(n, -1, -1):
            a = a0 + (a1 - a0) * i / n
            pts.append((math.cos(a) * r_in, math.sin(a) * r_in))
        with self.at(T(c), R(0, 0, rz)):
            self.prism_y(st, pts, -depth / 2, depth / 2)

    def text(self, st, s, c, size, depth=0.3, rz=0.0, font="bold", upright=True, spacing=1.0):
        cu = bpy.data.curves.new("txt", "FONT")
        cu.body = s
        cu.size = size
        cu.extrude = depth / 2
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.space_character = spacing
        cu.font = _font(font)
        ob = bpy.data.objects.new("txt", cu)
        bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        tmp = bmesh.new()
        tmp.from_mesh(me)
        bpy.data.meshes.remove(me)
        M = self.M @ T(c) @ R(0, 0, rz) @ (R(PI / 2, 0, 0) if upright else I4)
        bmesh.ops.transform(tmp, matrix=M, verts=tmp.verts)
        bm = self._bm(st)
        f0 = len(bm.faces)
        tmp.verts.index_update()
        vm = [bm.verts.new(v.co) for v in tmp.verts]
        for f in tmp.faces:
            try:
                bm.faces.new([vm[v.index] for v in f.verts])
            except ValueError:
                pass
        tmp.free()
        self._done(st, bm, f0)

    # --- composite helpers -------------------------------------------------
    def gable_roof(self, st, cx, cy, z0, w, d, h, t=0.7, over=1.2, ridge=None, trim=None):
        """Ridge along X. Footprint w (x) by d (y); eaves at z0, ridge at z0 + h."""
        a = math.atan2(h, d / 2)
        dz = t / math.cos(a)
        ex = d / 2 + over
        ez = z0 - over * math.tan(a)
        for sgn in (-1, 1):
            pts = [(cy + sgn * ex, ez), (cy, z0 + h), (cy, z0 + h - dz), (cy + sgn * ex, ez - dz)]
            if sgn > 0:
                pts = pts[::-1]
            self.prism_x(st, pts, cx - w / 2 - over, cx + w / 2 + over)
        if ridge:
            self.box(ridge, (cx, cy, z0 + h + 0.05), (w + 2 * over + 0.4, 0.9, 0.9), rx=PI / 4)
        if trim:
            for sgn in (-1, 1):
                self.box(trim, (cx, cy + sgn * ex, ez - dz / 2), (w + 2 * over, 0.35, dz + 0.1))

    def gable_end(self, st, x, cy, z0, d, h, t=0.6):
        self.prism_x(st, [(cy - d / 2, z0), (cy + d / 2, z0), (cy, z0 + h)], x - t / 2, x + t / 2)

    def hip_roof(self, st, cx, cy, z0, w, d, h, over=1.0, base=0.6):
        """A solid hip roof (ridge along the longer side); square -> pyramid."""
        W, D = w / 2 + over, d / 2 + over
        zb = z0 - base
        if abs(W - D) < 1e-3:
            verts = [(cx - W, cy - D, zb), (cx + W, cy - D, zb), (cx + W, cy + D, zb), (cx - W, cy + D, zb),
                     (cx - W, cy - D, z0), (cx + W, cy - D, z0), (cx + W, cy + D, z0), (cx - W, cy + D, z0),
                     (cx, cy, z0 + h)]
            faces = [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],
                     [4, 5, 8], [5, 6, 8], [6, 7, 8], [7, 4, 8]]
        elif W > D:
            rl = W - D
            verts = [(cx - W, cy - D, zb), (cx + W, cy - D, zb), (cx + W, cy + D, zb), (cx - W, cy + D, zb),
                     (cx - W, cy - D, z0), (cx + W, cy - D, z0), (cx + W, cy + D, z0), (cx - W, cy + D, z0),
                     (cx - rl, cy, z0 + h), (cx + rl, cy, z0 + h)]
            faces = [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],
                     [4, 5, 9, 8], [5, 6, 9], [6, 7, 8, 9], [7, 4, 8]]
        else:
            rl = D - W
            verts = [(cx - W, cy - D, zb), (cx + W, cy - D, zb), (cx + W, cy + D, zb), (cx - W, cy + D, zb),
                     (cx - W, cy - D, z0), (cx + W, cy - D, z0), (cx + W, cy + D, z0), (cx - W, cy + D, z0),
                     (cx, cy - rl, z0 + h), (cx, cy + rl, z0 + h)]
            faces = [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],
                     [4, 5, 8], [5, 6, 9, 8], [6, 7, 9], [7, 4, 8, 9]]
        self.mesh(st, verts, faces)

    def window(self, glass, frame, c, w, h, rz=0.0, ft=0.35, depth=0.35, cross=True, sill=None,
               shutters=None, arch=False, lintel=None):
        """A window on a wall whose outside faces local -Y (rz turns it)."""
        with self.at(T(c), R(0, 0, rz)):
            self.box(glass, (0, -depth * 0.3, 0), (w, 0.2, h))
            for sx in (-1, 1):
                self.box(frame, (sx * (w / 2 + ft / 2), -depth / 2, 0), (ft, depth, h + 2 * ft))
            self.box(frame, (0, -depth / 2, -h / 2 - ft / 2), (w, depth, ft))
            if arch:
                self.arch(frame, (0, -depth / 2, h / 2), w / 2, w / 2 + ft, depth, n=10)
                self.prism_y(glass, [(math.cos(PI * i / 10) * w / 2, h / 2 + math.sin(PI * i / 10) * w / 2) for i in range(11)],
                             -depth * 0.3 - 0.1, -depth * 0.3 + 0.1)
            else:
                self.box(frame, (0, -depth / 2, h / 2 + ft / 2), (w + 2 * ft, depth, ft))
            if cross:
                self.box(frame, (0, -depth * 0.45, 0), (ft * 0.55, depth * 0.6, h))
                self.box(frame, (0, -depth * 0.45, 0), (w, depth * 0.6, ft * 0.55))
            if sill:
                self.box(sill, (0, -depth / 2 - 0.25, -h / 2 - ft - 0.15), (w + 2 * ft + 0.6, depth + 0.6, 0.35))
            if lintel:
                self.box(lintel, (0, -depth / 2 - 0.15, h / 2 + ft + 0.3), (w + 2 * ft + 0.8, depth + 0.4, 0.6))
            if shutters:
                for sx in (-1, 1):
                    x = sx * (w / 2 + ft + w / 4 + 0.1)
                    self.box(shutters, (x, -0.25, 0), (w / 2, 0.3, h + ft))
                    for k in range(4):
                        zz = -h / 2 + (k + 0.5) * h / 4
                        self.box(shutters, (x, -0.42, zz), (w / 2 - 0.3, 0.12, 0.16), bev=0)

    def door(self, panel, frame, c, w, h, rz=0.0, ft=0.45, knob="Brass", arch=False, steps=None, panels=True):
        """A door; c is the bottom centre on the wall face (outside = local -Y)."""
        with self.at(T(c), R(0, 0, rz)):
            self.box(panel, (0, -0.15, h / 2), (w, 0.3, h))
            for sx in (-1, 1):
                self.box(frame, (sx * (w / 2 + ft / 2), -0.25, h / 2), (ft, 0.5, h + ft))
            if arch:
                self.arch(frame, (0, -0.25, h), w / 2, w / 2 + ft, 0.5, n=10)
                self.prism_y(panel, [(math.cos(PI * i / 10) * w / 2, h + math.sin(PI * i / 10) * w / 2) for i in range(11)], -0.3, 0.0)
            else:
                self.box(frame, (0, -0.25, h + ft / 2), (w + 2 * ft, 0.5, ft))
            if panels:
                for zz in (h * 0.28, h * 0.7):
                    self.box(frame, (0, -0.33, zz), (w * 0.62, 0.08, h * 0.28), bev=0)
            if knob:
                self.ball(knob, (w * 0.32, -0.42, h * 0.48), 0.22, seg=(8, 6))
            if steps:
                self.box(steps, (0, -0.9, 0.2), (w + 2 * ft + 1.2, 1.8, 0.4))

    def rail(self, post, top, p0, p1, z, h=3.0, spacing=3.0, pr=0.22, balusters=None, bal_sp=0.8, square=True):
        """Posts + a top rail from p0 to p1 (x, y) standing on z."""
        p0, p1 = V((p0[0], p0[1], z)), V((p1[0], p1[1], z))
        d = p1 - p0
        L = d.length
        if L < 1e-3:
            return
        rz = math.atan2(d.y, d.x)
        n = max(1, round(L / spacing))
        for i in range(n + 1):
            p = p0 + d * (i / n)
            if square:
                self.box(post, (p.x, p.y, z + h / 2), (pr * 2, pr * 2, h), rz=rz)
            else:
                self.cylz(post, p.x, p.y, z, z + h, pr, 8)
        mid = (p0 + p1) / 2
        self.box(top, (mid.x, mid.y, z + h), (L + pr * 2, pr * 2.2, pr * 1.4), rz=rz)
        if balusters:
            m = max(1, round(L / bal_sp))
            for i in range(1, m):
                p = p0 + d * (i / m)
                self.box(balusters, (p.x, p.y, z + h / 2), (0.18, 0.18, h - 0.2), rz=rz, bev=0)
            self.box(top, (mid.x, mid.y, z + 0.35), (L, pr * 1.6, pr), rz=rz)
        else:
            self.box(top, (mid.x, mid.y, z + h * 0.5), (L, pr * 1.2, pr), rz=rz)

    def rail_loop(self, post, top, pts, z, h=3.0, spacing=3.0, closed=True, **kw):
        k = len(pts)
        for i in range(k if closed else k - 1):
            self.rail(post, top, pts[i], pts[(i + 1) % k], z, h, spacing, **kw)

    def planks(self, styles, x0, x1, y0, y1, z, t=0.5, bw=1.6, along="x", gap=0.12):
        """A floor of separate boards, alternating styles (boards run along `along`)."""
        rng = self.rng
        if along == "x":
            n = max(1, int((y1 - y0) / bw))
            w = (y1 - y0) / n
            for i in range(n):
                st = styles[i % len(styles)] if rng.random() > 0.25 else styles[rng.randrange(len(styles))]
                yc = y0 + (i + 0.5) * w
                self.box(st, ((x0 + x1) / 2, yc, z - t / 2 + rng.uniform(-0.02, 0.02)), (x1 - x0, w - gap, t))
        else:
            n = max(1, int((x1 - x0) / bw))
            w = (x1 - x0) / n
            for i in range(n):
                st = styles[i % len(styles)] if rng.random() > 0.25 else styles[rng.randrange(len(styles))]
                xc = x0 + (i + 0.5) * w
                self.box(st, (xc, (y0 + y1) / 2, z - t / 2 + rng.uniform(-0.02, 0.02)), (w - gap, y1 - y0, t))

    def stairs(self, st, c, w, n, rise, run, rz=0.0, stringer=None, rails=None):
        """Steps climbing toward local +Y from c (bottom front centre)."""
        with self.at(T(c), R(0, 0, rz)):
            for i in range(n):
                self.box(st, (0, run * (i + 0.5), rise * (i + 0.5)), (w, run, rise))
                self.box(st, (0, run * (i + 0.5) + run * 0.08, rise * (i + 1) - 0.12), (w + 0.2, run + 0.25, 0.3))
            if stringer:
                L = math.hypot(n * run, n * rise)
                a = math.atan2(n * rise, n * run)
                for sx in (-1, 1):
                    self.box(stringer, (sx * (w / 2 + 0.25), n * run / 2, n * rise / 2), (0.5, L + 0.4, 0.9), rx=a)
            if rails:
                for sx in (-1, 1):
                    x = sx * (w / 2 + 0.25)
                    for i in (0, n - 1):
                        self.box(rails, (x, run * (i + 0.5), rise * (i + 1) + 1.6), (0.3, 0.3, 3.2))
                    a = math.atan2(rise, run)
                    L = math.hypot((n - 1) * run, (n - 1) * rise)
                    self.box(rails, (x, run * n / 2, rise * (n / 2 + 0.5) + 3.1), (0.3, L + 0.4, 0.3), rx=a)

    def fence(self, post, board, p0, p1, z=0.0, h=3.5, picket=0.7, gap=0.45, pointed=True):
        p0, p1 = V((p0[0], p0[1], z)), V((p1[0], p1[1], z))
        d = p1 - p0
        L = d.length
        rz = math.atan2(d.y, d.x)
        n = max(1, int(L / (picket + gap)))
        for i in range(n):
            p = p0 + d * ((i + 0.5) / n)
            hh = h + self.rng.uniform(-0.15, 0.15)
            self.box(board, (p.x, p.y, z + hh / 2), (picket, 0.22, hh), rz=rz)
            if pointed:
                with self.at(T(p.x, p.y, z + hh), R(0, 0, rz)):
                    self.prism_y(board, [(-picket / 2, 0), (picket / 2, 0), (0, picket * 0.55)], -0.11, 0.11)
        mid = (p0 + p1) / 2
        for zz in (h * 0.3, h * 0.75):
            self.box(post, (mid.x, mid.y + 0.0, z + zz), (L, 0.3, 0.4), rz=rz)
        for p in (p0, p1):
            self.box(post, (p.x, p.y, z + h / 2 + 0.2), (0.55, 0.55, h + 0.4), rz=rz)

    def lamp(self, post, glow, c, h=9.0, arms=1, head="lantern", base=None):
        x, y, z = c
        if base:
            self.cylz(base, x, y, z, z + 0.8, 0.9, 10)
        self.cylz(post, x, y, z, z + h, 0.22, 8)
        self.cylz(post, x, y, z + 0.8, z + 2.2, 0.38, 8, r2=0.24)
        if arms == 1:
            self.ball(glow, (x, y, z + h + 0.55), 0.6, seg=(10, 8))
            self.cylz(post, x, y, z + h - 0.1, z + h + 0.1, 0.5, 10)
            self.cylz(post, x, y, z + h + 1.05, z + h + 1.35, 0.55, 10, r2=0.1)
        else:
            for k in range(arms):
                a = TAU * k / arms
                ex, ey = x + math.cos(a) * 1.6, y + math.sin(a) * 1.6
                self.cyl(post, (x, y, z + h - 0.5), (ex, ey, z + h - 0.1), 0.12, 6)
                self.ball(glow, (ex, ey, z + h - 0.75), 0.5, seg=(10, 8))
                self.cylz(post, ex, ey, z + h - 0.25, z + h, 0.45, 10, r2=0.15)
            self.ball(post, (x, y, z + h + 0.2), 0.35, seg=(8, 6))

    def foliage(self, st, c, r, n=5, spread=0.7, sc=(1, 1, 0.8), styles=None):
        """A cluster of faceted leaf balls."""
        rng = self.rng
        styles = styles or [st]
        self.rock(styles[0], c, r, sc=sc, jitter=0.15, flat_bottom=False)
        for i in range(n):
            a = TAU * i / n + rng.uniform(-0.3, 0.3)
            rr = r * spread
            p = (c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr, c[2] + rng.uniform(-0.25, 0.15) * r)
            self.rock(styles[(i + 1) % len(styles)], p, r * rng.uniform(0.55, 0.75), sc=sc, jitter=0.15, flat_bottom=False)

    def striped_canopy(self, a, b, c, r, h, n=12, z=0.0, scallop=True, r_top=0.0):
        """A round cone canopy in alternating stripes, with scalloped trim."""
        x, y = c[0], c[1]
        for i in range(n):
            st = a if i % 2 == 0 else b
            a0 = TAU * i / n
            a1 = TAU * (i + 1) / n
            p0 = (x + math.cos(a0) * r, y + math.sin(a0) * r, z)
            p1 = (x + math.cos(a1) * r, y + math.sin(a1) * r, z)
            t0 = (x + math.cos(a0) * r_top, y + math.sin(a0) * r_top, z + h)
            t1 = (x + math.cos(a1) * r_top, y + math.sin(a1) * r_top, z + h)
            th = 0.35
            if r_top > 0.01:
                vs = [p0, p1, t1, t0, (p0[0], p0[1], p0[2] - th), (p1[0], p1[1], p1[2] - th), (t1[0], t1[1], t1[2] - th), (t0[0], t0[1], t0[2] - th)]
                fs = [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]
            else:
                vs = [p0, p1, (x, y, z + h), (p0[0], p0[1], p0[2] - th), (p1[0], p1[1], p1[2] - th), (x, y, z + h - th)]
                fs = [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]]
            self.mesh(st, vs, fs)
            if scallop:
                am = (a0 + a1) / 2
                rr = r * math.cos(PI / n)
                with self.at(T(x + math.cos(am) * rr, y + math.sin(am) * rr, z - 0.2), R(0, 0, am + PI / 2)):
                    w = 2 * r * math.sin(PI / n)
                    pts = [(-w / 2, 0)] + [(math.cos(PI + PI * k / 6) * w / 2, math.sin(PI + PI * k / 6) * w * 0.35) for k in range(1, 6)] + [(w / 2, 0)]
                    self.prism_y(st, pts, -0.12, 0.12)

    def round_deck(self, styles, cx, cy, z, r, t=0.5, bw=1.4, hole=0.0, rim=None, sides=None):
        """A round floor of boards (running along x) clipped to radius r, with an optional hole."""
        rng = self.rng
        n = max(1, int(2 * r / bw))
        w = 2 * r / n
        for i in range(n):
            y = -r + (i + 0.5) * w
            half = math.sqrt(max(r * r - y * y, 0.0))
            if half < 0.4:
                continue
            st = styles[i % len(styles)] if rng.random() > 0.25 else styles[rng.randrange(len(styles))]
            zz = z - t / 2 + rng.uniform(-0.02, 0.02)
            if hole > 0 and abs(y) < hole:
                hx = math.sqrt(hole * hole - y * y)
                for a, bb in ((-half, -hx), (hx, half)):
                    if bb - a > 0.3:
                        self.box(st, (cx + (a + bb) / 2, cy + y, zz), (bb - a, w - 0.12, t))
            else:
                self.box(st, (cx, cy + y, zz), (2 * half, w - 0.12, t))
        if rim:
            self.ring(rim, (cx, cy, 0), r + 0.35, r - 0.25, z - t - 0.6, z - t + 0.05, n=sides or 24)

    def human(self, c, rz=0.0, shirt="Blue", skin="Peach"):
        """A 6-stud person for scale (previews only)."""
        with self.at(T(c), R(0, 0, rz)):
            for sx in (-0.45, 0.45):
                self.box("Navy", (sx, 0, 1.25), (0.8, 0.8, 2.5), bev=0.1)
            self.box(shirt, (0, 0, 3.5), (2.0, 1.0, 2.0), bev=0.1)
            for sx in (-1.3, 1.3):
                self.box(skin, (sx, 0, 3.5), (0.6, 0.6, 2.0), bev=0.1)
            self.box(skin, (0, 0, 5.15), (1.2, 1.2, 1.2), bev=0.15)

    # --- output ------------------------------------------------------------
    def finish(self, collection, recenter=True):
        root = bpy.data.objects.new(self.name, None)
        root.empty_display_size = 2
        collection.objects.link(root)
        mn = V((1e9, 1e9, 1e9))
        mx = V((-1e9, -1e9, -1e9))
        for lst in self.parts.values():
            for bm in lst:
                for v in bm.verts:
                    mn.x, mn.y, mn.z = min(mn.x, v.co.x), min(mn.y, v.co.y), min(mn.z, v.co.z)
                    mx.x, mx.y, mx.z = max(mx.x, v.co.x), max(mx.y, v.co.y), max(mx.z, v.co.z)
        shift = V(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, 0)) if recenter else V((0, 0, 0))
        objs = []
        tri_total = 0
        for st, lst in self.parts.items():
            lst = [bm for bm in lst if len(bm.faces)]
            for i, bm in enumerate(lst):
                bmesh.ops.translate(bm, vec=-shift, verts=bm.verts)
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
                nm = f"{self.name}_{st}" + (f"_{i + 1}" if len(lst) > 1 else "")
                me = bpy.data.meshes.new(nm)
                bm.to_mesh(me)
                bm.free()
                me.materials.append(material(st))
                ob = bpy.data.objects.new(nm, me)
                collection.objects.link(ob)
                ob.parent = root
                objs.append(ob)
                tri_total += sum(len(p.vertices) - 2 for p in me.polygons)
        self.parts = {}
        size = mx - mn
        root["size"] = (round(size.x, 1), round(size.y, 1), round(size.z, 1))
        root["tris"] = tri_total
        root["area"] = self.area
        root["parts"] = len(objs)
        return root


def catenary(p0, p1, sag, n=12):
    p0, p1 = V(p0), V(p1)
    return [p0.lerp(p1, k / n) - V((0, 0, sag * math.sin(PI * k / n))) for k in range(n + 1)]
