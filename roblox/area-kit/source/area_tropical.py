"""Area 2 -- Tropical Island: bamboo, layered thatch, carved tiki wood, jungle green."""
import math

from kit import PI, TAU, Builder, R, T, V, catenary

AREA = "TropicalIsland"
GROUND = (126, 196, 104)


def bamboo_pole(b, p0, p1, r=0.35, st="Bamboo", node="BambooDark", seg=2.4):
    p0, p1 = V(p0), V(p1)
    b.cyl(st, p0, p1, r, 8)
    L = (p1 - p0).length
    n = int(L / seg)
    for k in range(1, n + 1):
        p = p0.lerp(p1, k / (n + 1))
        b.cyl(node, p - (p1 - p0).normalized() * 0.12, p + (p1 - p0).normalized() * 0.12, r * 1.18, 8)


def thatch_roof(b, cx, cy, z0, w, d, h, over=1.6, layers=3, dark="ThatchDark", light="Thatch"):
    """A hip roof in stepped thatch layers, with a ragged fringe at the eaves."""
    for k in range(layers):
        f = k / layers
        st = dark if k % 2 == 0 else light
        ww = (w + 2 * over) * (1 - f * 0.62)
        dd = (d + 2 * over) * (1 - f * 0.62)
        zz = z0 + h * f * 0.78
        b.hip_roof(st, cx, cy, zz, ww - 2 * over * 0, dd, h * (1 - f * 0.78), over=0.0, base=0.9)
    rng = b.rng
    W, D = w / 2 + over, d / 2 + over
    for side in range(4):
        L = 2 * (W if side % 2 == 0 else D)
        n = int(L / 0.9)
        for i in range(n):
            t = -L / 2 + (i + 0.5) * L / n
            hh = rng.uniform(0.8, 1.6)
            if side == 0:
                c = (cx + t, cy - D + 0.15, z0 - 0.9 - hh / 2)
                rz = 0
            elif side == 1:
                c = (cx + W - 0.15, cy + t, z0 - 0.9 - hh / 2)
                rz = PI / 2
            elif side == 2:
                c = (cx + t, cy + D - 0.15, z0 - 0.9 - hh / 2)
                rz = 0
            else:
                c = (cx - W + 0.15, cy + t, z0 - 0.9 - hh / 2)
                rz = PI / 2
            b.box(dark if i % 3 else light, c, (1.0, 0.35, hh), rz=rz, rx=rng.uniform(-0.12, 0.12), bev=0)


def tiki_face(b, c, w, h, wood, paint, rz=0.0, mouth="Charcoal"):
    """One carved tiki head block, face toward local -Y."""
    with b.at(T(c), R(0, 0, rz)):
        b.box(wood, (0, 0, h / 2), (w, w, h))
        b.box(paint, (0, -w / 2 - 0.1, h * 0.78), (w * 0.95, 0.3, h * 0.12))
        for sx in (-1, 1):
            b.cyl("White", (sx * w * 0.22, -w / 2 - 0.05, h * 0.6), (sx * w * 0.22, -w / 2 - 0.35, h * 0.6), w * 0.15, 10)
            b.cyl("Black", (sx * w * 0.22, -w / 2 - 0.3, h * 0.6), (sx * w * 0.22, -w / 2 - 0.42, h * 0.6), w * 0.07, 8)
        b.prism_x(wood, [(-w / 2, h * 0.5), (-w / 2 - w * 0.28, h * 0.32), (-w / 2, h * 0.3)], -w * 0.1, w * 0.1)
        b.box(mouth, (0, -w / 2 - 0.05, h * 0.18), (w * 0.6, 0.3, h * 0.12))
        for k in range(4):
            x = -w * 0.22 + k * w * 0.147
            b.box("White", (x, -w / 2 - 0.12, h * 0.22), (w * 0.08, 0.3, h * 0.06), bev=0)
        for sx in (-1, 1):
            b.box(paint, (sx * (w / 2 + 0.15), 0, h * 0.55), (0.3, w * 0.4, h * 0.3))


def tree_house():
    b = Builder("TreeHouse", AREA)
    b.lathe("Bark", [(0, 0), (6.4, 0), (5.0, 2.0), (4.0, 5.0), (3.5, 14.0), (3.3, 26.0), (3.0, 38.0), (2.6, 46.0), (1.8, 50.0), (0, 50.5)], n=12)
    for k in range(7):
        a = TAU * k / 7 + 0.3
        b.cyl("Bark", (math.cos(a) * 3.0, math.sin(a) * 3.0, 3.6), (math.cos(a) * 8.2, math.sin(a) * 8.2, 0.0), 1.3, 7, r2=0.45)
    for z, a in ((9, 0.5), (24, 2.4), (31, 4.2), (13, 3.6)):
        b.ball("Bark", (math.cos(a) * 3.4, math.sin(a) * 3.4, z), 0.9, seg=(8, 6), sc=(1, 1, 1.3))
    # vines
    for a in (1.2, 3.0, 5.1):
        pts = [(math.cos(a + k * 0.09) * 3.45, math.sin(a + k * 0.09) * 3.45, 2 + k * 1.6) for k in range(14)]
        b.tube("LeafDark", pts, 0.18, 5)
        for k in range(2, 14, 3):
            p = pts[k]
            b.ball("Leaf", (p[0] * 1.08, p[1] * 1.08, p[2]), 0.55, seg=(6, 4), sc=(1, 1, 0.5))
    # main platform
    PZ = 18.0
    b.round_deck(["Plank", "WoodLight", "WoodDark"], 0, 0, PZ, 12.0, t=0.6, bw=1.3, hole=3.6, rim="WoodDark", sides=16)
    for k in range(8):
        a = TAU * k / 8
        b.cyl("WoodDark", (math.cos(a) * 3.3, math.sin(a) * 3.3, PZ - 7.5), (math.cos(a) * 11.0, math.sin(a) * 11.0, PZ - 1.0), 0.45, 6)
        b.cyl("WoodDark", (math.cos(a) * 3.2, math.sin(a) * 3.2, PZ - 0.8), (math.cos(a) * 11.6, math.sin(a) * 11.6, PZ - 0.8), 0.4, 6)
    # railing: posts + bamboo top rail + rope
    posts = []
    for k in range(20):
        a = TAU * k / 20
        if -PI / 2 - 0.4 < (a - TAU if a > PI else a) < -PI / 2 + 0.2:
            continue
        posts.append(a)
        bamboo_pole(b, (math.cos(a) * 11.6, math.sin(a) * 11.6, PZ), (math.cos(a) * 11.6, math.sin(a) * 11.6, PZ + 3.6), r=0.3, seg=1.6)
    ring_pts = [(math.cos(a) * 11.6, math.sin(a) * 11.6, PZ + 3.5) for a in posts]
    b.tube("Bamboo", ring_pts, 0.28, 6)
    b.tube("Rope", [(p[0], p[1], PZ + 1.9) for p in ring_pts], 0.12, 5)
    # the hut on the front of the platform
    X0, X1, Y0, Y1 = -6.0, 6.0, -10.4, -3.0
    Z0, Z1 = PZ, PZ + 8.5
    b.bx("Bamboo", X0, X1, Y0, Y1, Z0, Z1)
    for i in range(18):
        x = X0 + 0.35 + i * (X1 - X0 - 0.7) / 17
        if -1.6 < x < 1.6:
            continue
        if 2.6 < x < 5.0 or -5.0 < x < -2.6:
            b.cylz("BambooDark" if i % 4 == 0 else "Bamboo", x, Y0 - 0.15, Z0, Z0 + 3.0, 0.34, 6)
            b.cylz("BambooDark" if i % 4 == 0 else "Bamboo", x, Y0 - 0.15, Z0 + 6.2, Z1, 0.34, 6)
        else:
            b.cylz("BambooDark" if i % 4 == 0 else "Bamboo", x, Y0 - 0.15, Z0, Z1, 0.34, 6)
    for sx in (-1, 1):
        for j in range(9):
            y = Y0 + 0.4 + j * (Y1 - Y0 - 0.8) / 8
            b.cylz("Bamboo" if j % 3 else "BambooDark", sx * (X1 + 0.15), y, Z0, Z1, 0.34, 6)
        b.bx("Charcoal", sx * 3.8 - 1.1, sx * 3.8 + 1.1, Y0 - 0.1, Y0 + 0.2, Z0 + 3.0, Z0 + 6.2)
        with b.at(T(sx * 3.8, Y0 - 0.4, Z0 + 6.4), R(-0.9, 0, 0)):
            for k in range(5):
                b.cyl("Bamboo", (-1.3 + k * 0.65, 0, 0), (-1.3 + k * 0.65, -3.2, 0), 0.22, 6)
        b.cyl("WoodDark", (sx * 3.8, Y0 - 0.4, Z0 + 3.0), (sx * 3.8, Y0 - 2.4, Z0 + 4.6), 0.12, 4)
    b.bx("Charcoal", -1.6, 1.6, Y0 - 0.1, Y0 + 0.2, Z0, Z0 + 6.8)
    b.bx("WoodDark", -2.0, 2.0, Y0 - 0.5, Y0 - 0.1, Z0 + 6.8, Z0 + 7.4)
    for x in (-1.9, 1.9):
        b.bx("WoodDark", x - 0.3, x + 0.3, Y0 - 0.5, Y0 - 0.1, Z0, Z0 + 7.4)
    for k in range(6):
        b.cylz(("Orange", "Red", "Yellow")[k % 3], -1.2 + k * 0.48, Y0 - 0.3, Z0 + 3.5 + (k % 2) * 0.4, Z0 + 6.6, 0.18, 5)
    thatch_roof(b, 0, (Y0 + Y1) / 2, Z1, X1 - X0, Y1 - Y0, 5.5, over=1.8, layers=3)
    b.cylz("WoodDark", 0, (Y0 + Y1) / 2, Z1 + 5.0, Z1 + 7.0, 0.25, 6)
    b.ball("Orange", (0, (Y0 + Y1) / 2, Z1 + 7.2), 0.5, seg=(8, 6))
    # hanging lanterns on the platform rim
    for a in (0.3, 1.2, 2.2, 2.9, 3.9):
        x, y = math.cos(a) * 11.9, math.sin(a) * 11.9
        b.cylz("Rope", x, y, PZ - 2.4, PZ - 0.6, 0.06, 4)
        b.ball("Orange", (x, y, PZ - 3.0), 0.75, seg=(10, 8), sc=(1, 1, 1.25))
        b.cylz("WoodDark", x, y, PZ - 2.2, PZ - 2.0, 0.45, 8)
        b.cylz("WoodDark", x, y, PZ - 4.0, PZ - 3.8, 0.45, 8)
    # spiral stairs round the trunk, ground to platform
    steps = 24
    for i in range(steps):
        a = -PI / 2 - 0.15 - (steps - i) * math.radians(17)
        z = (i + 1) * PZ / (steps + 1)
        with b.at(T(0, 0, z), R(0, 0, a)):
            b.bx("Plank" if i % 2 else "WoodLight", 3.5, 7.8, -0.85, 0.85, -0.25, 0.25)
            b.cyl("WoodDark", (7.6, 0, 0), (7.6, 0, 3.4), 0.18, 5)
            b.cyl("WoodDark", (3.6, 0, -0.3), (6.5, 0, -1.8), 0.22, 5)
    rail = []
    for i in range(steps + 1):
        a = -PI / 2 - 0.15 - (steps - i) * math.radians(17)
        z = (i + 1) * PZ / (steps + 1)
        rail.append((math.cos(a) * 7.6, math.sin(a) * 7.6, z + 3.3))
    b.tube("Bamboo", rail, 0.24, 6)
    # lookout + rope ladder
    LZ = 33.0
    b.round_deck(["Plank", "WoodLight"], 0, 0, LZ, 6.5, t=0.5, bw=1.2, hole=3.1, rim="WoodDark", sides=12)
    for k in range(6):
        a = TAU * k / 6 + 0.3
        b.cyl("WoodDark", (math.cos(a) * 3.0, math.sin(a) * 3.0, LZ - 4.5), (math.cos(a) * 6.0, math.sin(a) * 6.0, LZ - 0.8), 0.35, 6)
    for k in range(12):
        a = TAU * k / 12
        bamboo_pole(b, (math.cos(a) * 6.3, math.sin(a) * 6.3, LZ), (math.cos(a) * 6.3, math.sin(a) * 6.3, LZ + 3.4), r=0.26, seg=1.5)
    b.torus("Bamboo", (0, 0, LZ + 3.3), 6.3, 0.24, 16, 6)
    b.torus("Rope", (0, 0, LZ + 1.8), 6.3, 0.1, 16, 4)
    for sx in (-0.9, 0.9):
        b.cyl("Rope", (sx, 9.0, PZ), (sx, 6.4, LZ), 0.13, 5)
    for k in range(13):
        t = (k + 0.5) / 13
        b.box("WoodLight", (0, 9.0 - t * 2.6, PZ + t * (LZ - PZ)), (2.2, 0.35, 0.3), rx=-0.15)
    # flag on the lookout
    b.cylz("WoodDark", 0, 0, 50.5, 54.5, 0.12, 5)
    # canopy: branches + leaf clusters
    clusters = [(0, 0, 54, 8.5), (8, 3, 49, 6.8), (-7.5, 4, 50, 6.6), (2, -7.5, 48, 6.4), (-3, 8, 47, 6.0), (6, -4, 44, 5.2), (-6, -5, 45, 5.0)]
    for (x, y, z, r) in clusters[1:]:
        b.cyl("Bark", (x * 0.25, y * 0.25, z - 9), (x * 0.85, y * 0.85, z - 1.5), 0.9, 6, r2=0.45)
    for k, (x, y, z, r) in enumerate(clusters):
        b.foliage("Leaf", (x, y, z), r, n=5, spread=0.6, sc=(1, 1, 0.62), styles=["Leaf", "LeafDark", "LeafLight", "Leaf"])
    return b


def stilt_hut():
    b = Builder("StiltHut", AREA)
    DZ = 7.0
    for x in (-9, 0, 9):
        for y in (-9, 0, 9):
            b.cylz("Bark", x, y, 0, DZ, 0.7, 8)
            b.torus("Rope", (x, y, DZ - 1.6), 0.72, 0.12, 10, 4)
    for x in (-9, 0, 9):
        b.bx("WoodDark", x - 0.4, x + 0.4, -10, 10, DZ - 1.2, DZ - 0.4)
    b.planks(["Bamboo", "BambooDark", "Plank"], -10.5, 10.5, -10.5, 10.5, DZ, t=0.5, bw=1.0, along="x")
    # railing
    for (p0, p1) in (((-10.3, -10.3), (-3, -10.3)), ((3, -10.3), (10.3, -10.3)), ((10.3, -10.3), (10.3, 10.3)),
                     ((10.3, 10.3), (-10.3, 10.3)), ((-10.3, 10.3), (-10.3, -10.3))):
        b.rail("Bamboo", "Bamboo", p0, p1, DZ, h=3.2, spacing=2.4, pr=0.25, square=False)
    # hut
    X0, X1, Y0, Y1 = -6.5, 6.5, -5, 7
    Z0, Z1 = DZ, DZ + 8.0
    b.bx("BambooDark", X0, X1, Y0, Y1, Z0, Z1)
    for side in range(4):
        L = (X1 - X0) if side % 2 == 0 else (Y1 - Y0)
        n = int(L / 0.72)
        for i in range(n):
            t = -L / 2 + (i + 0.5) * L / n
            if side == 0:
                if abs(t) < 1.8 or (3.2 < abs(t) < 5.6):
                    if abs(t) < 1.8:
                        continue
                    b.cylz("Bamboo", t, Y0 - 0.2, Z0, Z0 + 2.8, 0.34, 6)
                    b.cylz("Bamboo", t, Y0 - 0.2, Z0 + 6.0, Z1, 0.34, 6)
                    continue
                b.cylz("Bamboo", t, Y0 - 0.2, Z0, Z1, 0.34, 6)
            elif side == 2:
                b.cylz("Bamboo", t, Y1 + 0.2, Z0, Z1, 0.34, 6)
            else:
                x = X1 + 0.2 if side == 1 else X0 - 0.2
                b.cylz("Bamboo", x, (Y0 + Y1) / 2 + t, Z0, Z1, 0.34, 6)
    for z in (Z0 + 1.0, Z1 - 0.8):
        b.bx("Rope", X0 - 0.5, X1 + 0.5, Y0 - 0.55, Y0 - 0.35, z - 0.12, z + 0.12, bev=0)
    b.bx("Charcoal", -1.8, 1.8, Y0 - 0.15, Y0 + 0.1, Z0, Z0 + 6.6)
    for x in (-2.1, 2.1):
        b.cylz("WoodDark", x, Y0 - 0.4, Z0, Z0 + 7.0, 0.32, 6)
    b.cyl("WoodDark", (-2.6, Y0 - 0.4, Z0 + 6.9), (2.6, Y0 - 0.4, Z0 + 6.9), 0.32, 6)
    for sx in (-1, 1):
        b.bx("Charcoal", sx * 4.4 - 1.2, sx * 4.4 + 1.2, Y0 - 0.15, Y0 + 0.1, Z0 + 2.8, Z0 + 6.0)
        with b.at(T(sx * 4.4, Y0 - 0.4, Z0 + 6.2), R(-0.85, 0, 0)):
            b.bx("Thatch", -1.5, 1.5, -3.2, 0, -0.2, 0.2)
        b.cyl("WoodDark", (sx * 4.4, Y0 - 0.4, Z0 + 2.9), (sx * 4.4, Y0 - 2.3, Z0 + 4.3), 0.12, 4)
    thatch_roof(b, 0, (Y0 + Y1) / 2, Z1, X1 - X0, Y1 - Y0, 8.5, over=2.6, layers=4)
    b.cylz("WoodDark", 0, (Y0 + Y1) / 2, Z1 + 7.6, Z1 + 10.2, 0.3, 6)
    b.ball("Turquoise", (0, (Y0 + Y1) / 2, Z1 + 10.4), 0.5, seg=(8, 6))
    # ladder down the front
    for sx in (-1.1, 1.1):
        b.cyl("Bamboo", (sx, -12.6, 0), (sx, -10.4, DZ + 2.8), 0.28, 6)
    for k in range(7):
        t = (k + 0.6) / 8
        b.cyl("BambooDark", (-1.2, -12.6 + t * 2.2, t * (DZ + 2.8)), (1.2, -12.6 + t * 2.2, t * (DZ + 2.8)), 0.18, 5)
    # fishing net, basket, drying fish
    pts = catenary((5, -10.4, DZ + 2.8), (9.6, -10.4, DZ + 2.8), 1.6, 8)
    for k in range(5):
        a = [(p[0], p[1], p[2] - k * 0.5) for p in pts]
        b.tube("Rope", a, 0.06, 4)
    for k in range(9):
        p = pts[k]
        b.cyl("Rope", (p[0], p[1], p[2]), (p[0], p[1], p[2] - 2.2), 0.06, 4)
    b.lathe("Thatch", [(0, 0), (0.9, 0), (1.2, 1.2), (1.1, 1.3), (0.8, 0.15), (0, 0.15)], c=(-7.5, -7.5, DZ), n=10)
    for k in range(3):
        b.ball("SkyBlue", (-7.5 + k * 0.4 - 0.4, -7.5, DZ + 1.2), 0.3, seg=(6, 4), sc=(1, 2.2, 0.6))
    return b


def tiki_bar():
    b = Builder("TikiBar", AREA)
    b.bx("Stone", -15, 15, -9, 9, 0, 0.8)
    b.planks(["Plank", "WoodLight", "WoodDark"], -14.5, 14.5, -8.5, 8.5, 1.1, t=0.4, bw=1.3, along="x")
    # carved tiki posts
    for x in (-12.5, 0, 12.5):
        for y in (-7.0, 7.0):
            b.cylz("WoodDark", x, y, 1.1, 12.0, 0.75, 8)
            for z, col in ((3.0, "Orange"), (6.0, "Teal"), (9.0, "Red")):
                b.cylz(col, x, y, z, z + 0.45, 0.85, 8)
            if y < 0:
                tiki_face(b, (x, y - 0.3, 9.6), 1.8, 2.4, "WoodDark", "Orange")
    # gable thatch roof
    b.gable_roof("ThatchDark", 0, 0, 12.0, 26, 15, 6.0, t=1.0, over=2.2)
    b.gable_roof("Thatch", 0, 0, 12.8, 26, 15, 5.2, t=0.6, over=1.6)
    for x in (-13.6, 13.6):
        b.gable_end("Bamboo", x, 0, 12.0, 14, 5.6, t=0.4)
    for k in range(34):
        x = -14.5 + k * 0.88
        hh = b.rng.uniform(0.8, 1.7)
        for sy in (-1, 1):
            b.box("ThatchDark" if k % 3 else "Thatch", (x, sy * 9.6, 9.6 - hh / 2), (0.95, 0.35, hh), rx=sy * 0.4, bev=0)
    # bar counter (U) with bamboo front
    for (x0, x1, y0, y1) in ((-9, 9, -4.2, -2.4), (-9, -7.2, -4.2, 3.5), (7.2, 9, -4.2, 3.5)):
        b.bx("WoodDark", x0, x1, y0, y1, 1.1, 4.6)
        b.bx("Plank", x0 - 0.4, x1 + 0.4, y0 - 0.4, y1 + 0.4, 4.6, 5.1)
    for i in range(24):
        x = -8.8 + i * 0.765
        b.cylz("Bamboo" if i % 4 else "BambooDark", x, -4.4, 1.1, 4.6, 0.36, 6)
    for i in range(9):
        y = -3.8 + i * 0.85
        for x in (-9.2, 9.2):
            b.cylz("Bamboo" if i % 3 else "BambooDark", x, y, 1.1, 4.6, 0.36, 6)
    b.bx("Turquoise", -8.6, 8.6, -4.85, -4.6, 3.6, 4.0, bev=0)
    # stools
    for x in (-6, -2, 2, 6):
        for sx, sy in ((-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)):
            b.cylz("Bamboo", x + sx, -6.2 + sy, 1.1, 3.6, 0.13, 5)
        b.cylz("WoodLight", x, -6.2, 3.6, 4.1, 1.0, 10)
        b.torus("Bamboo", (x, -6.2, 2.3), 0.62, 0.1, 10, 4)
    # back shelf with bottles + coconut cups
    b.bx("WoodDark", -9, 9, 5.8, 7.4, 1.1, 8.6)
    for z in (4.2, 6.6):
        b.bx("Plank", -8.6, 8.6, 5.2, 5.8, z - 0.2, z + 0.15)
        for k in range(15):
            x = -8.0 + k * 1.14
            col = ("GlassDark", "Green", "Orange", "Turquoise", "Red")[k % 5]
            b.cylz(col, x, 5.5, z + 0.15, z + 1.5, 0.32, 8)
            b.cylz(col, x, 5.5, z + 1.5, z + 1.9, 0.14, 6)
    for x in (-5, -1.5, 2, 5.5):
        b.ball("Chocolate", (x, -3.3, 5.5), 0.55, seg=(8, 6))
        b.cyl("Pink", (x + 0.1, -3.3, 5.8), (x + 0.4, -3.4, 6.7), 0.06, 4)
    # sign
    b.bx("WoodDark", -6.5, 6.5, -9.6, -9.1, 13.0, 16.0)
    b.text("Yellow", "TIKI BAR", (0, -9.75, 14.5), 1.9, depth=0.35)
    for x in (-5.4, 5.4):
        b.cyl("Rope", (x, -9.3, 16.0), (x, -9.3, 17.4), 0.1, 4)
    # tiki torches at the front corners
    for x in (-16.0, 16.0):
        bamboo_pole(b, (x, -10.0, 0), (x, -10.0, 9.0), r=0.3, seg=2.0)
        b.lathe("Thatch", [(0.2, 0), (0.75, 0.6), (0.85, 1.7), (0, 1.7)], c=(x, -10.0, 9.0), n=8)
        b.cylz("Fire", x, -10.0, 10.6, 12.0, 0.6, 7, r2=0.0)
        b.cylz("Ember", x, -10.0, 10.6, 11.2, 0.7, 7, r2=0.3)
    return b


def totem_gate():
    b = Builder("TotemGate", AREA)
    segs = (("WoodDark", "Orange"), ("Bark", "Teal"), ("WoodRed", "Yellow"), ("WoodDark", "Turquoise"), ("Bark", "Red"))
    for x in (-10.5, 10.5):
        b.cylz("Rock", x, 0, 0, 1.2, 2.5, 8)
        z = 1.2
        for k, (w, p) in enumerate(segs):
            tiki_face(b, (x, 0, z), 3.1 - k * 0.12, 4.0, w, p, mouth="Charcoal" if k % 2 else "Red")
            z += 4.0
        b.lathe("Stone", [(0, 0), (1.0, 0), (1.9, 1.0), (1.9, 1.3), (0, 1.3)], c=(x, 0, z), n=10)
        b.cylz("Fire", x, 0, z + 1.2, z + 3.6, 1.3, 8, r2=0.0)
        b.cylz("Ember", x, 0, z + 1.2, z + 2.2, 1.6, 8, r2=0.6)
        for sx in (-1, 1):
            with b.at(T(x + sx * 1.5, 0, z - 3.2)):
                b.prism_y("Teal", [(0, 0), (sx * 2.8, 1.4), (sx * 3.3, 3.0), (sx * 0.4, 2.2)], -0.25, 0.25)
                b.prism_y("Yellow", [(sx * 0.4, 0.5), (sx * 2.2, 1.5), (sx * 2.6, 2.5), (sx * 0.4, 1.7)], -0.35, -0.25)
    # crossbeam lashed between the totems, thatch on top
    b.bx("WoodDark", -9.2, 9.2, -0.9, 0.9, 14.0, 15.6)
    b.gable_roof("ThatchDark", 0, 0, 15.6, 17.0, 2.4, 1.6, t=0.5, over=0.7)
    for k in range(20):
        x = -9 + k * 0.95
        hh = b.rng.uniform(0.5, 1.1)
        for sy in (-1, 1):
            b.box("Thatch", (x, sy * 1.85, 15.2 - hh / 2), (0.95, 0.25, hh), rx=sy * 0.3, bev=0)
    for x in (-8.9, 8.9):
        for k in range(4):
            b.torus("Rope", (x, 0, 14.2 + k * 0.38), 1.25, 0.11, 10, 4, ry=PI / 2)
    b.bx("Plank", -7.2, 7.2, -1.4, -0.9, 10.2, 13.4)
    b.bx("WoodDark", -7.5, 7.5, -1.5, -0.8, 13.2, 13.6)
    b.bx("WoodDark", -7.5, 7.5, -1.5, -0.8, 10.0, 10.4)
    b.text("Yellow", "ISLAND", (0, -1.55, 11.8), 2.0, depth=0.35)
    for x in (-6.0, 6.0):
        b.cyl("Rope", (x, -1.15, 13.4), (x, -1.15, 14.2), 0.12, 4)
    for k in range(6):
        x = -7.5 + k * 3
        b.cyl("Rope", (x, 0.6, 14.0), (x, 0.6, 12.6 - (k % 2) * 0.7), 0.06, 4)
        b.ball(("Peach", "Coral", "White")[k % 3], (x, 0.6, 12.3 - (k % 2) * 0.7), 0.4, seg=(6, 4), sc=(1, 0.5, 1.2))
    return b


def rope_bridge():
    b = Builder("RopeBridge", AREA)
    L = 56.0
    DZ = 10.0
    for sy in (-1, 1):
        y = sy * L / 2
        with b.at(T(0, y + sy * 3.5, 0)):
            for x in (-3.6, 3.6):
                for yy in (-3, 3):
                    b.cylz("Bark", x, yy, 0, DZ + (3.8 if yy == -3 * sy else 0), 0.55, 8)
            b.planks(["Plank", "WoodLight"], -4.2, 4.2, -3.6, 3.6, DZ, t=0.5, bw=1.2, along="x")
            b.bx("WoodDark", -4.4, 4.4, -3.8, 3.8, DZ - 1.2, DZ - 0.5)
            b.stairs("Plank", (0, -sy * 3.6 - (0 if sy < 0 else 0), 0), 4.0, 12, DZ / 12, 1.0, rz=(0 if sy > 0 else PI))
    # deck planks hung on a sag
    n = 44
    sag = 3.2
    for k in range(n):
        t = (k + 0.5) / n
        y = -L / 2 + t * L
        z = DZ - sag * math.sin(PI * t)
        dz = -sag * PI * math.cos(PI * t) / L
        b.box("Plank" if k % 3 else "Driftwood", (b.rng.uniform(-0.15, 0.15), y, z - 0.2), (5.2 + b.rng.uniform(-0.4, 0.4), 1.0, 0.35),
              rx=math.atan(dz), rz=b.rng.uniform(-0.05, 0.05))
    for x in (-2.4, 2.4):
        b.tube("Rope", catenary((x, -L / 2, DZ - 0.45), (x, L / 2, DZ - 0.45), sag, 24), 0.16, 5)
    for x in (-3.4, 3.4):
        hand = catenary((x, -L / 2 - 0.5, DZ + 3.6), (x, L / 2 + 0.5, DZ + 3.6), sag * 0.8, 24)
        b.tube("Rope", hand, 0.22, 6)
        for k in range(1, 24):
            t = k / 24
            p = hand[k]
            zdeck = DZ - sag * math.sin(PI * t) - 0.3
            b.cyl("Rope", (x, p.y, p.z), (x * 0.75, p.y, zdeck), 0.07, 4)
    return b


def waterfall_cliff():
    b = Builder("WaterfallCliff", AREA)
    rng = b.rng
    # cliff mass: stacked faceted rocks
    for k in range(26):
        x = rng.uniform(-17, 17)
        y = rng.uniform(2, 11)
        z = rng.uniform(0, 22) * (1 - abs(x) / 30)
        r = rng.uniform(4.5, 7.5)
        b.rock("Rock" if k % 3 else "StoneDark", (x, y, z), r, sc=(1.2, 0.9, 0.9), jitter=0.22)
    for x in (-12, -6, 0, 6, 12):
        b.rock("Rock", (x, 8, 24 - abs(x) * 0.5), 6.0, sc=(1.1, 1.0, 0.7))
    # moss + plants on top
    for k in range(12):
        x = rng.uniform(-15, 15)
        b.rock("Grass", (x, rng.uniform(6, 11), 27.5 - abs(x) * 0.5), rng.uniform(2.4, 3.6), sc=(1.3, 1.1, 0.45), jitter=0.12)
    for (x, y, z) in ((-11, 3, 21), (12, 4, 18), (-15, -1, 9), (15, 0, 7)):
        b.foliage("Leaf", (x, y, z), 2.2, n=4, styles=["Leaf", "LeafDark", "LeafLight"])
    # the falls: a stepped curtain of water from the lip to the pool
    lip = 26.0
    for k in range(9):
        z1 = lip - k * 2.9
        z0 = z1 - 3.1
        w = 7.0 + k * 0.25
        yy = 2.6 - k * 0.5 - (k ** 1.2) * 0.12
        b.box("Water", (0, yy, (z0 + z1) / 2), (w, 0.9, z1 - z0), rx=-0.12)
        for j in range(5):
            x = -w / 2 + 0.7 + j * (w - 1.4) / 4
            b.box("White", (x + rng.uniform(-0.3, 0.3), yy - 0.5, (z0 + z1) / 2), (0.25, 0.2, (z1 - z0) * 0.8), rx=-0.12, bev=0)
    b.box("Water", (0, 4.0, lip + 0.3), (7.6, 4.0, 0.6))
    # pool + rim stones + foam
    b.lathe("Water", [(0, 0), (11.0, 0), (11.0, 0.9), (0, 0.9)], c=(0, -6, 0), n=20)
    for k in range(18):
        a = TAU * k / 18
        if 1.1 < a < 2.0:
            continue
        b.rock("Stone" if k % 2 else "Rock", (math.cos(a) * 11.6, -6 + math.sin(a) * 10.8, 0.6), rng.uniform(1.4, 2.2), sc=(1.2, 1, 0.7))
    for k in range(10):
        b.ball("White", (rng.uniform(-4, 4), rng.uniform(-3, 0), 1.0), rng.uniform(0.6, 1.2), seg=(8, 6), sc=(1, 1, 0.45))
    # lily pads
    for (x, y) in ((-6, -9), (5, -11), (-2, -13)):
        b.cylz("LeafLight", x, y, 0.9, 1.05, 1.1, 10)
        b.ball("Flower", (x + 0.3, y, 1.3), 0.35, seg=(6, 4))
    return b


def canoe():
    b = Builder("Canoe", AREA)
    L = 17.0
    n = 16
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        y = -L / 2 + t * L
        w = max(0.12, 1.7 * math.sin(PI * t) ** 0.6)
        lift = 0.9 * (abs(t - 0.5) * 2) ** 3
        sec = [(-w, 1.7 + lift), (-0.85 * w, 0.6 + lift), (-0.4 * w, 0.1 + lift * 0.9), (0, lift * 0.8),
               (0.4 * w, 0.1 + lift * 0.9), (0.85 * w, 0.6 + lift), (w, 1.7 + lift)]
        outer.append([(x, y, z) for x, z in sec])
        th = min(0.25, w * 0.5)
        inner.append([(x * max(0.0, w - th) / w, y, z + th) for x, z in sec])
    verts, faces = [], []
    k = 7
    ring = 2 * k
    for i in range(n + 1):
        verts += outer[i] + inner[i][::-1]
    for i in range(n):
        a, c = i * ring, (i + 1) * ring
        for j in range(ring):
            jj = (j + 1) % ring
            faces.append([a + j, a + jj, c + jj, c + j])
    faces.append(list(range(ring))[::-1])
    faces.append(list(range(n * ring, n * ring + ring)))
    b.mesh("WoodDark", verts, faces)
    # painted band of triangles along both sides
    for sx in (-1, 1):
        for i in range(2, 14):
            t = i / 16
            y = -L / 2 + t * L
            w = 1.7 * math.sin(PI * t) ** 0.6
            with b.at(T(sx * (w * 0.93 + 0.05), y, 1.2), R(0, 0, PI / 2 if sx > 0 else -PI / 2)):
                b.prism_y("Red" if i % 2 else "Yellow", [(-0.5, -0.3), (0.5, -0.3), (0, 0.4)], -0.05, 0.05)
    # outrigger float + booms
    with b.at(T(5.6, 0, 0.3)):
        b.ball("Bark", (0, 0, 0.4), 1.0, seg=(12, 6), sc=(0.55, 6.2, 0.5))
    for y in (-3.2, 3.2):
        b.cyl("Bamboo", (-1.8, y, 1.9), (5.6, y, 1.9), 0.2, 6)
        b.cyl("Bamboo", (5.6, y, 1.9), (5.6, y, 0.7), 0.16, 5)
        b.torus("Rope", (1.6, y, 1.9), 0.24, 0.08, 6, 4, ry=PI / 2)
    # paddle across the seats
    b.cyl("WoodLight", (-0.6, -5.5, 1.1), (0.4, 2.5, 1.5), 0.12, 6)
    b.ball("WoodLight", (-0.75, -6.8, 1.05), 1.0, seg=(10, 6), sc=(0.5, 1.3, 0.08), rz=0.12)
    for y in (-3.0, 3.0):
        b.bx("Plank", -1.4, 1.4, y - 0.4, y + 0.4, 1.0, 1.25)
    return b


def fruit_stand():
    b = Builder("FruitStand", AREA)
    for x in (-6, 6):
        for y in (0.6, 4.6):
            bamboo_pole(b, (x, y, 0), (x, y, 10.6 if y > 1 else 9.6), r=0.3, seg=2.0)
    with b.at(T(0, 2.4, 10.2), R(math.atan2(1.0, 6.0), 0, 0)):
        b.bx("Thatch", -7.4, 7.4, -3.8, 3.8, -0.3, 0.3)
        b.bx("ThatchDark", -7.2, 7.2, -3.4, 3.4, 0.3, 0.7)
    for k in range(17):
        x = -7.3 + k * 0.91
        hh = b.rng.uniform(0.6, 1.2)
        b.box("ThatchDark" if k % 3 else "Thatch", (x, -1.35, 9.5 - hh / 2), (0.92, 0.3, hh), bev=0)
    # stepped table of crates
    b.bx("WoodDark", -6.3, 6.3, -3.0, 3.0, 0, 3.0)
    for k, (x, y, z) in enumerate(((-4.2, -2.0, 3.0), (0, -2.0, 3.0), (4.2, -2.0, 3.0), (-4.2, 1.2, 4.2), (0, 1.2, 4.2), (4.2, 1.2, 4.2))):
        b.bx("WoodLight", x - 1.9, x + 1.9, y - 1.3, y + 1.3, z, z + 1.2)
        for zz in (z + 0.3, z + 0.9):
            b.bx("Plank", x - 1.95, x + 1.95, y - 1.35, y - 1.25, zz - 0.15, zz + 0.15, bev=0)
        top = z + 1.25
        if k in (0, 3):
            for i in range(6):
                px, py = x - 1.1 + (i % 3) * 1.1, y - 0.5 + (i // 3) * 1.0
                b.ball("Yellow", (px, py, top + 0.75), 0.55, seg=(8, 6), sc=(1, 1, 1.4))
                for j in range(5):
                    a = TAU * j / 5
                    b.cyl("LeafDark", (px, py, top + 1.4), (px + math.cos(a) * 0.45, py + math.sin(a) * 0.45, top + 2.3), 0.12, 4, r2=0.0)
        elif k in (1, 4):
            for i in range(7):
                px, py = x - 1.2 + (i % 4) * 0.8, y - 0.5 + (i // 4) * 0.9
                b.ball("Chocolate", (px, py, top + 0.45), 0.5, seg=(8, 6))
            b.ball("White", (x + 1.0, y + 0.4, top + 0.6), 0.5, seg=(8, 6), sc=(1, 1, 0.4))
        else:
            for i in range(3):
                with b.at(T(x - 0.9 + i * 0.9, y, top + 0.2)):
                    for j in range(5):
                        a = -0.5 + j * 0.25
                        pts = [(math.sin(a) * 0.3 + 0.0, -1.0 + s * 0.5, 0.25 + 0.6 * math.sin(s * 0.7)) for s in range(5)]
                        b.tube("Yellow", pts, 0.18, 6)
    b.ball("Green", (5.6, -4.0, 0.9), 0.9, seg=(10, 6), sc=(1.3, 1, 1))
    with b.at(T(-5.2, -4.2, 0.0), R(PI / 2, 0, 0.3)):
        b.lathe("Green", [(0, 0), (1.2, 0), (1.2, 0.2), (0, 0.2)], n=12, a0=0, a1=PI)
        b.lathe("Red", [(0, 0.2), (1.05, 0.2), (1.05, 0.35), (0, 0.35)], n=12, a0=0, a1=PI)
    # chalk price board
    b.bx("WoodDark", -2.6, 2.6, -1.6, -1.3, 7.0, 8.6)
    b.text("White", "FRESH", (0, -1.7, 7.8), 0.9, depth=0.12)
    for x in (-2.0, 2.0):
        b.cyl("Rope", (x, -1.45, 8.6), (x, -1.45, 9.4), 0.06, 4)
    return b


def bamboo_fence():
    b = Builder("BambooFence", AREA)
    rng = b.rng
    for i in range(22):
        x = -10 + i * 0.95
        h = 5.4 + rng.uniform(-0.6, 0.6)
        bamboo_pole(b, (x, 0, 0), (x, 0, h), r=0.42, st="Bamboo" if i % 5 else "BambooDark", seg=1.8)
        b.cylz("BambooDark", x, 0, h - 0.05, h + 0.05, 0.28, 6)
    for z in (1.4, 3.8):
        for sy in (-1, 1):
            bamboo_pole(b, (-10.6, sy * 0.6, z), (10.6, sy * 0.6, z), r=0.24, st="BambooDark", node="Bamboo", seg=3.0)
        for i in range(0, 22, 3):
            x = -10 + i * 0.95
            b.torus("Rope", (x, 0, z), 0.62, 0.1, 8, 4, rx=PI / 2, rz=PI / 2)
    for x in (-10.8, 10.8):
        b.cylz("WoodDark", x, 0, 0, 6.6, 0.55, 8)
        b.cylz("WoodDark", x, 0, 6.6, 7.0, 0.75, 8, r2=0.2)
    return b


def bonfire():
    b = Builder("Bonfire", AREA)
    rng = b.rng
    b.cylz("Sand", 0, 0, 0, 0.15, 13.5, 24)
    for k in range(14):
        a = TAU * k / 14
        b.rock("Stone" if k % 2 else "StoneDark", (math.cos(a) * 3.2, math.sin(a) * 3.2, 0.5), 0.9, sc=(1.1, 1, 0.8))
    b.cylz("Charcoal", 0, 0, 0.15, 0.4, 2.8, 12)
    for k in range(7):
        a = TAU * k / 7
        b.cyl("Bark", (math.cos(a) * 2.4, math.sin(a) * 2.4, 0.3), (math.cos(a) * 0.3, math.sin(a) * 0.3, 4.2), 0.35, 6)
    for k in range(5):
        a = TAU * k / 5 + 0.3
        h = rng.uniform(3.0, 5.2)
        b.cyl("Fire", (math.cos(a) * 0.9, math.sin(a) * 0.9, 0.4), (math.cos(a) * 0.4, math.sin(a) * 0.4, h), 0.9, 6, r2=0.0)
    b.cylz("Ember", 0, 0, 0.4, 2.6, 1.6, 7, r2=0.4)
    b.cylz("Fire", 0, 0, 0.4, 6.2, 1.2, 7, r2=0.0)
    # log seats
    for k in range(4):
        a = TAU * k / 4 + PI / 4
        with b.at(T(math.cos(a) * 8.4, math.sin(a) * 8.4, 0), R(0, 0, a + PI / 2)):
            b.cyl("Bark", (-3.2, 0, 1.1), (3.2, 0, 1.1), 1.1, 8)
            for sx in (-1, 1):
                b.cyl("WoodLight", (sx * 3.2, 0, 1.1), (sx * 3.25, 0, 1.1), 1.0, 8)
            b.bx("WoodLight", -3.0, 3.0, -0.6, 0.6, 2.0, 2.25, bev=0)
    # drum
    b.lathe("WoodRed", [(0, 0), (0.9, 0), (1.1, 1.5), (0.95, 2.6), (0, 2.6)], c=(5.6, -1.0, 0), n=10)
    b.cylz("Cream", 5.6, -1.0, 2.6, 2.75, 1.0, 10)
    return b


def hammock():
    b = Builder("Hammock", AREA)
    for x in (-7.0, 7.0):
        bamboo_pole(b, (x, 0, 0), (x * 0.96, 0, 8.0), r=0.45, seg=2.2)
        b.cylz("Rock", x, 0, 0, 0.6, 1.0, 8)
        b.ball("BambooDark", (x * 0.96, 0, 8.1), 0.48, seg=(8, 6))
    rings = []
    n = 14
    for i in range(n + 1):
        t = i / n
        x = -4.6 + t * 9.2
        z = 4.3 - 1.9 * math.sin(PI * t)
        w = 0.9 + 1.0 * math.sin(PI * t) ** 0.5
        ring = []
        for j in range(7):
            u = -1 + 2 * j / 6
            ring.append((x, u * w, z + 0.55 * u * u * math.sin(PI * t)))
        rings.append(ring)
    # sling = a thin strip lofted from the rings (top and bottom skins)
    for k in range(0, n):
        st = ("Red", "Yellow", "Turquoise", "White")[k % 4]
        verts, faces = [], []
        for ring in (rings[k], rings[k + 1]):
            for p in ring:
                verts.append(p)
        for ring in (rings[k], rings[k + 1]):
            for p in ring:
                verts.append((p[0], p[1], p[2] - 0.12))
        m = 7
        for j in range(m - 1):
            faces.append([j, j + 1, m + j + 1, m + j])
            faces.append([2 * m + j, 2 * m + m + j, 2 * m + m + j + 1, 2 * m + j + 1])
        for j in (0, m - 1):
            faces.append([j, m + j, 3 * m + j, 2 * m + j])
        b.mesh(st, verts, faces)
    for sx in (-1, 1):
        x_end = sx * 4.6
        for u in (-0.9, 0, 0.9):
            b.cyl("Rope", (x_end, u, 4.3), (sx * 6.7, 0, 7.4), 0.07, 4)
        b.cyl("WoodDark", (x_end, -1.0, 4.3), (x_end, 1.0, 4.3), 0.16, 6)
    b.ball("White", (-2.8, 0, 3.2), 1.0, seg=(10, 6), sc=(0.8, 1.2, 0.35))
    return b


ASSETS = [tree_house, stilt_hut, tiki_bar, totem_gate, rope_bridge, waterfall_cliff, canoe, fruit_stand,
          bamboo_fence, bonfire, hammock]
