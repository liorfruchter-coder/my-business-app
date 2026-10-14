"""Area 3 -- Volcano: black basalt, obsidian glass, lava light and rusted iron."""
import math

from kit import PI, TAU, Builder, R, T, V, catenary

AREA = "Volcano"
GROUND = (112, 76, 66)


def face_stones(b, st, c, w, z0, z1, rz=0.0, density=0.35, bh=1.2, bw=2.4):
    """Scattered proud stone blocks on a wall face (outside = local -Y)."""
    rng = b.rng
    with b.at(T(c), R(0, 0, rz)):
        rows = int((z1 - z0) / bh)
        for r in range(rows):
            off = (r % 2) * bw / 2
            n = int(w / bw) + 1
            for i in range(n):
                if rng.random() > density:
                    continue
                x = -w / 2 + off + i * bw + bw / 2
                if x - bw / 2 < -w / 2 + 0.2 or x + bw / 2 > w / 2 - 0.2:
                    continue
                z = z0 + r * bh + bh / 2
                b.box(st, (x, -0.12, z), (bw - 0.25, 0.4, bh - 0.22), bev=0.12)


def brazier(b, c, r=1.4, h=4.0, bowl="DarkMetal", stand="DarkMetal"):
    x, y, z = c
    b.cylz(stand, x, y, z, z + 0.5, r * 0.8, 8)
    b.cylz(stand, x, y, z + 0.5, z + h - 1.0, r * 0.25, 8)
    b.lathe(bowl, [(0, 0), (r * 0.4, 0), (r, 0.7), (r * 1.1, 1.1), (0, 1.0)], c=(x, y, z + h - 1.1), n=10)
    b.cylz("Fire", x, y, z + h - 0.1, z + h + r * 1.8, r * 0.85, 7, r2=0.0)
    b.cylz("Ember", x, y, z + h - 0.1, z + h + 0.7, r * 0.95, 7, r2=r * 0.4)


def horn(b, st, base, sx, scale=1.0):
    pts = []
    for k in range(9):
        t = k / 8
        pts.append((base[0] + sx * (math.sin(t * 1.4) * 3.2) * scale, base[1], base[2] + (t * 4.2 - t * t * 0.8) * scale))
    for k in range(8):
        r0 = (1.0 - k / 8) * 0.9 * scale + 0.05
        b.cyl(st, pts[k], pts[k + 1], r0, 8, r2=(1.0 - (k + 1) / 8) * 0.9 * scale + 0.05)


def obsidian_temple():
    b = Builder("ObsidianTemple", AREA)
    tiers = [(56, 7.0), (44, 7.0), (32, 7.0), (21, 6.0)]
    z = 0.0
    for k, (w, h) in enumerate(tiers):
        b.bx("Basalt", -w / 2, w / 2, -w / 2, w / 2, z, z + h)
        b.bx("BasaltLight", -w / 2 - 0.4, w / 2 + 0.4, -w / 2 - 0.4, w / 2 + 0.4, z + h - 0.8, z + h)
        if k < 3:
            # paved walkway round the tier above
            b.bx("Stone", -w / 2 + 0.4, w / 2 - 0.4, -w / 2 + 0.4, w / 2 - 0.4, z + h, z + h + 0.15, bev=0.1)
        b.bx("BasaltLight", -w / 2 - 0.3, w / 2 + 0.3, -w / 2 - 0.3, w / 2 + 0.3, z, z + 0.7)
        for rz in (0, PI / 2, PI, -PI / 2):
            with b.at(R(0, 0, rz)):
                face_stones(b, "BasaltLight", (0, -w / 2, 0), w - 10 if rz == 0 else w, z + 0.8, z + h - 0.8, density=0.28)
                if rz != 0:
                    # a glowing glyph band + lava seam down the middle of each side
                    b.bx("Lava", -0.7, 0.7, -w / 2 - 0.15, -w / 2 + 0.2, z + 0.7, z + h - 0.8)
                    b.bx("Basalt", -1.4, -0.7, -w / 2 - 0.4, -w / 2 + 0.2, z + 0.7, z + h - 0.8)
                    b.bx("Basalt", 0.7, 1.4, -w / 2 - 0.4, -w / 2 + 0.2, z + 0.7, z + h - 0.8)
                    for gx in (-w / 4, w / 4):
                        b.bx("LavaDim", gx - 1.4, gx + 1.4, -w / 2 - 0.25, -w / 2, z + h / 2 - 1.4, z + h / 2 + 1.4)
                        b.bx("Gold", gx - 0.5, gx + 0.5, -w / 2 - 0.4, -w / 2, z + h / 2 - 0.5, z + h / 2 + 0.5, bev=0)
        # corner braziers on the lower three tiers
        if k < 3:
            w2 = tiers[k + 1][0]
            for sx in (-1, 1):
                for sy in (-1, 1):
                    m = (w / 2 + w2 / 2) / 2
                    brazier(b, (sx * m, sy * m, z + h), r=1.1, h=3.2)
        z += h
    top = z
    # grand stair up the front, lava rills either side
    rise_total = top
    n = int(rise_total / 0.9)
    run = (56 / 2 - 21 / 2) / n
    for i in range(n):
        zz = (i + 1) * rise_total / n
        y = -28 - 2 + i * run
        b.bx("BasaltLight", -5, 5, y, y + run + 0.4, zz - rise_total / n, zz)
        b.bx("Stone", -5.1, 5.1, y - 0.1, y + 0.4, zz - 0.25, zz + 0.05, bev=0)
    L = math.hypot(n * run, top)
    a = math.atan2(top, n * run)
    for sx in (-1, 1):
        with b.at(T(sx * 6.4, -30 + n * run / 2, top / 2), R(a, 0, 0)):
            b.box("Basalt", (0, 0, 0.9), (2.6, L + 1.0, 2.2))
            b.box("Lava", (sx * -0.1, 0, 2.05), (1.0, L + 0.6, 0.3))
            b.box("Basalt", (sx * 0.9, 0, 2.4), (0.6, L + 0.6, 0.9))
            b.box("Basalt", (-sx * 0.9, 0, 2.4), (0.6, L + 0.6, 0.9))
        brazier(b, (sx * 6.4, -31.0, 0), r=1.4, h=4.4)
    # shrine on top
    S0, S1 = -7.5, 7.5
    b.bx("Obsidian", S0, S1, S0 + 1, S1, top, top + 9.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.bx("BasaltLight", sx * 7.5 - 0.9, sx * 7.5 + 0.9, sy * 7.5 - 0.9 + (0.5 if sy < 0 else 0), sy * 7.5 + 0.9, top, top + 9.6)
    for x in (-4.6, -1.6, 1.6, 4.6):
        b.cylz("BasaltLight", x, -8.2, top, top + 9.2, 0.75, 8)
        b.bx("BasaltLight", x - 1.0, x + 1.0, -9.2, -7.2, top, top + 0.6)
        b.bx("BasaltLight", x - 1.0, x + 1.0, -9.2, -7.2, top + 8.6, top + 9.2)
    b.bx("Ember", -2.4, 2.4, -6.7, -6.4, top, top + 6.5)
    b.arch("Basalt", (0, -6.6, top + 6.5), 2.4, 3.2, 0.8, n=8)
    b.bx("Basalt", -3.2, -2.4, -7.0, -6.2, top, top + 6.5)
    b.bx("Basalt", 2.4, 3.2, -7.0, -6.2, top, top + 6.5)
    b.bx("Basalt", -9.5, 9.5, -10.0, 9.5, top + 9.2, top + 10.6)
    b.bx("BasaltLight", -10.0, 10.0, -10.5, 10.0, top + 10.6, top + 11.2)
    b.bx("Basalt", -7.0, 7.0, -7.0, 7.0, top + 11.2, top + 13.6)
    b.hip_roof("Obsidian", 0, 0, top + 13.6, 13, 13, 4.5, over=0.4, base=0.3)
    horn(b, "Obsidian", (-6.4, -8.6, top + 11.2), -1, 1.1)
    horn(b, "Obsidian", (6.4, -8.6, top + 11.2), 1, 1.1)
    b.ball("Lava", (0, -10.6, top + 9.9), 1.1, seg=(10, 8), sc=(1, 0.4, 1))
    # obsidian shards round the summit
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * 9.0, sy * 9.0
            for k in range(3):
                a = k * 2.1
                b.lathe("Obsidian", [(0, 0), (0.9 - k * 0.15, 0), (0.9 - k * 0.15, 3.0 - k * 0.5), (0, 4.6 - k * 0.7)],
                        c=(cx + math.cos(a) * 0.9, cy + math.sin(a) * 0.9, top), n=6)
    return b


def lava_forge():
    b = Builder("LavaForge", AREA)
    X0, X1, Y0, Y1 = -12, 12, -4, 12
    Z0, Z1 = 0, 13
    b.bx("BasaltLight", X0 - 0.6, X1 + 0.6, Y0 - 0.6, Y1 + 0.6, 0, 1.2)
    b.bx("Basalt", X0, X1, Y0, Y1, Z0, Z1)
    face_stones(b, "BasaltLight", (0, Y0, 0), X1 - X0, 1.2, Z1 - 0.6, density=0.4)
    with b.at(R(0, 0, PI / 2)):
        face_stones(b, "BasaltLight", (4, -X1, 0), Y1 - Y0, 1.2, Z1 - 0.6, density=0.4)
    with b.at(R(0, 0, -PI / 2)):
        face_stones(b, "BasaltLight", (-4, X0, 0), Y1 - Y0, 1.2, Z1 - 0.6, density=0.4)
    for x in (X0, X1):
        for k in range(6):
            z = 1.2 + k * 2.0
            b.bx("BasaltLight", x - 0.8, x + 0.8, Y0 - 0.8, Y0 + 1.6 + (k % 2), z, z + 1.8)
    # iron door
    b.bx("DarkMetal", -3.4, 3.4, Y0 - 0.4, Y0 + 0.1, 1.2, 9.0)
    b.arch("BasaltLight", (0, Y0 - 0.2, 9.0), 3.4, 4.4, 1.0, n=10)
    b.prism_y("DarkMetal", [(math.cos(PI * i / 10) * 3.4, 9.0 + math.sin(PI * i / 10) * 3.4) for i in range(11)], Y0 - 0.4, Y0 + 0.1)
    for x in (-3.9, 3.9):
        b.bx("BasaltLight", x - 0.5, x + 0.5, Y0 - 0.7, Y0 + 0.3, 1.2, 9.0)
    for z in (2.6, 5.4, 8.2):
        b.bx("Rust", -3.4, 3.4, Y0 - 0.6, Y0 - 0.35, z - 0.3, z + 0.3, bev=0)
        for x in (-2.8, -1.4, 0, 1.4, 2.8):
            b.ball("Metal", (x, Y0 - 0.65, z), 0.18, seg=(6, 4))
    b.torus("Metal", (1.5, Y0 - 0.75, 5.0), 0.5, 0.1, 10, 4, rx=PI / 2)
    # glowing barred windows
    for x in (-8, 8):
        b.bx("Ember", x - 1.6, x + 1.6, Y0 - 0.15, Y0 + 0.1, 5.0, 9.0)
        b.bx("BasaltLight", x - 2.2, x + 2.2, Y0 - 0.6, Y0, 4.4, 5.0)
        b.bx("BasaltLight", x - 2.2, x + 2.2, Y0 - 0.6, Y0, 9.0, 9.6)
        for k in range(4):
            b.cylz("DarkMetal", x - 1.2 + k * 0.8, Y0 - 0.3, 5.0, 9.0, 0.14, 6)
    # roof: rusted corrugated iron with a stone parapet front
    with b.at(T(0, (Y0 + Y1) / 2, Z1 + 2.0), R(-math.atan2(3.0, 17), 0, 0)):
        b.box("Rust", (0, 0, 0), (26.0, 18.5, 0.35))
        for k in range(26):
            b.cyl("Rust", (-12.5 + k * 1.0, -9.2, 0.2), (-12.5 + k * 1.0, 9.2, 0.2), 0.22, 6)
    b.bx("Basalt", X0, X1, Y1 - 0.8, Y1, Z1, Z1 + 3.6)
    b.bx("BasaltLight", X0 - 0.8, X1 + 0.8, Y0 - 0.8, Y0 + 0.4, Z1 - 0.4, Z1 + 0.6)
    # big chimney with a glowing throat
    b.lathe("Basalt", [(0, 0), (4.2, 0), (4.2, 12.0), (3.4, 18.0), (2.9, 31.0), (0, 31.0)], c=(-7.5, 9.0, 0), n=8)
    for z in (14.0, 22.0):
        b.ring("BasaltLight", (-7.5, 9.0, 0), 3.9 - (z - 14) * 0.03, 2.5, z, z + 1.0, n=8)
    b.ring("BasaltLight", (-7.5, 9.0, 0), 3.7, 2.2, 30.0, 32.0, n=8)
    b.cylz("Lava", -7.5, 9.0, 30.5, 31.8, 2.3, 8)
    # outdoor forge: furnace, anvil, quench barrel, tool rack, lava channel
    FX, FY = 8.0, -12.0
    b.lathe("Basalt", [(0, 0), (4.4, 0), (4.4, 2.0), (4.0, 4.6), (2.8, 6.6), (1.2, 7.6), (0, 7.8)], c=(FX, FY, 0), n=12)
    b.cylz("Basalt", FX, FY, 7.0, 11.0, 1.0, 8)
    b.cylz("Ember", FX, FY, 10.6, 11.1, 0.75, 8)
    with b.at(T(FX, FY - 3.9, 0)):
        b.bx("Lava", -1.6, 1.6, -0.5, 0.4, 1.4, 3.8)
        b.arch("BasaltLight", (0, -0.4, 3.8), 1.6, 2.4, 1.1, n=8)
        b.bx("BasaltLight", -2.4, -1.6, -0.95, 0.15, 0, 3.8)
        b.bx("BasaltLight", 1.6, 2.4, -0.95, 0.15, 0, 3.8)
        b.bx("BasaltLight", -2.6, 2.6, -1.5, 0.2, 0.9, 1.4)
    # bellows
    with b.at(T(FX + 5.4, FY + 0.5, 1.2), R(0, 0, -0.4)):
        b.prism_z("WoodDark", [(-1.0, 1.6), (1.0, 1.6), (0.3, -1.4), (-0.3, -1.4)], 0, 0.3)
        b.prism_z("Chocolate", [(-0.9, 1.4), (0.9, 1.4), (0.25, -1.2), (-0.25, -1.2)], 0.3, 1.2)
        b.prism_z("WoodDark", [(-1.0, 1.6), (1.0, 1.6), (0.3, -1.4), (-0.3, -1.4)], 1.2, 1.5)
        b.cyl("DarkMetal", (0, -1.4, 0.7), (0, -2.8, 0.7), 0.22, 6)
    # anvil on a stump
    AX, AY = 0.0, -14.5
    b.cylz("Bark", AX, AY, 0, 2.6, 1.4, 10)
    b.cylz("WoodLight", AX, AY, 2.6, 2.7, 1.32, 10)
    b.bx("DarkMetal", AX - 1.0, AX + 1.0, AY - 0.6, AY + 0.6, 2.7, 3.6)
    b.bx("DarkMetal", AX - 0.6, AX + 0.6, AY - 0.45, AY + 0.45, 3.6, 4.4)
    b.bx("DarkMetal", AX - 1.6, AX + 1.4, AY - 0.65, AY + 0.65, 4.4, 5.3)
    b.prism_y("DarkMetal", [(AX + 1.4, 4.4), (AX + 3.0, 5.3), (AX + 1.4, 5.3)], AY - 0.4, AY + 0.4)
    b.bx("Ember", AX - 0.8, AX + 0.6, AY - 0.15, AY + 0.15, 5.3, 5.5, bev=0)
    b.cyl("WoodDark", (AX - 1.2, AY + 0.4, 5.4), (AX - 3.2, AY + 1.6, 5.6), 0.14, 6)
    b.bx("DarkMetal", AX - 1.4, AX - 0.9, AY + 0.1, AY + 0.7, 5.3, 6.0)
    b.lathe("WoodDark", [(0, 0), (1.3, 0), (1.4, 2.6), (0, 2.6)], c=(-6.0, -12.5, 0), n=12)
    b.cylz("Water", -6.0, -12.5, 2.2, 2.45, 1.25, 12)
    for z in (0.5, 2.1):
        b.torus("Rust", (-6.0, -12.5, z), 1.38, 0.1, 12, 4)
    # sword + axe rack
    with b.at(T(-10.5, -8.0, 0)):
        for x in (-1.8, 1.8):
            b.bx("WoodDark", x - 0.25, x + 0.25, -0.25, 0.25, 0, 4.4)
        b.bx("WoodDark", -2.2, 2.2, -0.3, 0.3, 3.6, 4.0)
        b.bx("WoodDark", -2.2, 2.2, -0.3, 0.3, 1.0, 1.3)
        for k in range(4):
            x = -1.2 + k * 0.8
            b.bx("Metal", x - 0.15, x + 0.15, -0.55, -0.4, 1.3, 4.6, bev=0)
            b.bx("Gold", x - 0.45, x + 0.45, -0.6, -0.35, 4.6, 4.8, bev=0)
            b.cylz("WoodDark", x, -0.48, 4.8, 5.6, 0.12, 5)
    # lava channel feeding the furnace
    b.bx("BasaltLight", FX - 1.8, FX + 1.8, FY - 9.0, FY - 4.4, 0, 0.9)
    b.bx("Lava", FX - 0.9, FX + 0.9, FY - 8.6, FY - 4.4, 0.4, 0.95)
    b.ring("BasaltLight", (FX, FY - 10.4, 0), 2.6, 1.6, 0, 1.0, n=12)
    b.cylz("Lava", FX, FY - 10.4, 0, 0.85, 1.7, 12)
    # sign
    b.bx("DarkMetal", -4.5, 4.5, Y0 - 0.9, Y0 - 0.6, 10.2, 12.2)
    b.text("Fire", "FORGE", (0, Y0 - 1.0, 11.2), 1.4, depth=0.2)
    return b


def watchtower():
    b = Builder("Watchtower", AREA)
    H = 34.0
    b.bx("BasaltLight", -8.2, 8.2, -8.2, 8.2, 0, 1.6)
    with b.at():
        b.mesh("Basalt", [(-7, -7, 0), (7, -7, 0), (7, 7, 0), (-7, 7, 0), (-5.6, -5.6, H), (5.6, -5.6, H), (5.6, 5.6, H), (-5.6, 5.6, H)],
               [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
    for k in range(int(H / 2.2)):
        z = 1.6 + k * 2.2
        f = z / H
        hw = 7 - 1.4 * f
        for sx in (-1, 1):
            for sy in (-1, 1):
                ext = 1.8 if k % 2 else 1.1
                b.bx("BasaltLight", sx * hw - (0.7 if sx > 0 else -0.7) - 0.75, sx * hw - (0.7 if sx > 0 else -0.7) + 0.75,
                     sy * hw - sy * ext / 2 - 0.75, sy * hw - sy * ext / 2 + 0.75, z, z + 1.9)
    for rz in (0, PI / 2, PI, -PI / 2):
        with b.at(R(0, 0, rz)):
            for z in (10.0, 20.0, 28.0):
                hw = 7 - 1.4 * z / H
                b.bx("Ember", -0.45, 0.45, -hw - 0.1, -hw + 0.3, z, z + 3.0)
                b.bx("BasaltLight", -1.1, 1.1, -hw - 0.5, -hw + 0.2, z - 0.5, z)
                b.bx("BasaltLight", -1.1, 1.1, -hw - 0.5, -hw + 0.2, z + 3.0, z + 3.5)
    b.bx("DarkMetal", -2.0, 2.0, -7.15, -6.7, 1.6, 7.2)
    b.arch("BasaltLight", (0, -7.0, 7.2), 2.0, 2.8, 1.0, n=8)
    b.prism_y("DarkMetal", [(math.cos(PI * i / 8) * 2.0, 7.2 + math.sin(PI * i / 8) * 2.0) for i in range(9)], -7.15, -6.7)
    for z in (3.0, 5.6):
        for x in (-1.2, 0, 1.2):
            b.ball("Metal", (x, -7.25, z), 0.16, seg=(6, 4))
    # corbelled top platform with crenellations
    b.bx("BasaltLight", -7.6, 7.6, -7.6, 7.6, H, H + 1.2)
    for k in range(8):
        t = -6.6 + k * 1.9
        for (x, y) in ((t, -7.2), (t, 7.2), (-7.2, t), (7.2, t)):
            b.bx("BasaltLight", x - 0.55, x + 0.55, y - 0.55, y + 0.55, H - 1.6, H)
    b.bx("Basalt", -8.0, 8.0, -8.0, 8.0, H + 1.2, H + 2.2)
    for k in range(5):
        t = -6.4 + k * 3.2
        for (x, y) in ((t, -7.4), (t, 7.4), (-7.4, t), (7.4, t)):
            b.bx("Basalt", x - 0.9, x + 0.9, y - 0.6, y + 0.6, H + 2.2, H + 4.6)
    brazier(b, (0, 0, H + 1.2), r=2.0, h=3.2)
    # banner
    b.cyl("DarkMetal", (-3.0, -6.4, H - 2.0), (3.0, -6.4, H - 2.0), 0.15, 6)
    b.prism_y("RedDark", [(-2.6, H - 2.0), (2.6, H - 2.0), (2.6, H - 12.0), (0, H - 10.6), (-2.6, H - 12.0)], -6.55, -6.35)
    b.prism_y("Gold", [(0, H - 4.2), (1.3, H - 6.0), (0, H - 8.4), (-1.3, H - 6.0)], -6.62, -6.5)
    return b


def lava_bridge():
    b = Builder("LavaBridge", AREA)
    L, W = 64.0, 12.0
    DZ = 13.0
    # lava river + crusted banks underneath
    b.bx("Lava", -W / 2 - 14, W / 2 + 14, -14, 14, 0, 0.5)
    for sy in (-1, 1):
        for k in range(10):
            x = -W / 2 - 13 + k * 3.6
            b.rock("BasaltLight" if k % 2 else "Basalt", (x, sy * 15.5, 0.6), 2.4, sc=(1.2, 1, 0.6))
    # piers + arches (three spans)
    piers = (-12.0, 12.0)
    for y in piers:
        b.bx("Basalt", -W / 2, W / 2, y - 3, y + 3, 0, DZ - 1)
        b.prism_y("Basalt", [(-W / 2, 0), (0, -0.01), (W / 2, 0)], y - 3, y + 3)
        for sy in (-1, 1):
            b.prism_x("BasaltLight", [(y + sy * 3, 0), (y + sy * 5.5, 0), (y + sy * 3, 6.0)], -W / 2 + 0.6, W / 2 - 0.6)
    for (y0, y1) in ((-L / 2, -15.0), (-9.0, 9.0), (15.0, L / 2)):
        span = y1 - y0
        cy = (y0 + y1) / 2
        r_in = span / 2
        with b.at(T(0, cy, 0), R(0, 0, PI / 2)):
            b.arch("BasaltLight", (0, 0, DZ - 1 - r_in * 0.55), r_in, r_in + 1.6, W - 0.6, a0=math.asin(0.55), a1=PI - math.asin(0.55), n=12)
    b.bx("Basalt", -W / 2, W / 2, -L / 2, L / 2, DZ - 2.6, DZ)
    for y in (-L / 2 + 1.5, L / 2 - 1.5):
        b.bx("Basalt", -W / 2, W / 2, y - 1.5, y + 1.5, 0, DZ - 2.6)
    # deck paving + parapets with merlons
    for k in range(int(L / 2)):
        y = -L / 2 + 1 + k * 2
        b.bx("Stone" if k % 2 else "StoneDark", -W / 2 + 1.2, W / 2 - 1.2, y - 0.95, y + 0.95, DZ, DZ + 0.3, bev=0.1)
    for sx in (-1, 1):
        b.bx("BasaltLight", sx * (W / 2 - 0.6) - 0.6, sx * (W / 2 - 0.6) + 0.6, -L / 2, L / 2, DZ, DZ + 2.4)
        for k in range(9):
            y = -L / 2 + 2 + k * (L - 4) / 8
            b.bx("Basalt", sx * (W / 2 - 0.6) - 0.85, sx * (W / 2 - 0.6) + 0.85, y - 1.0, y + 1.0, DZ, DZ + 3.6)
            if k in (0, 4, 8):
                brazier(b, (sx * (W / 2 - 0.6), y, DZ + 3.6), r=1.0, h=2.6)
        b.bx("Basalt", sx * (W / 2) - 0.5, sx * (W / 2) + 0.5, -L / 2, L / 2, DZ - 2.9, DZ - 2.4)
    # dripping lava from the deck edge
    for (x, y) in ((-W / 2 - 0.2, -4), (W / 2 + 0.2, 5), (-W / 2 - 0.2, 21)):
        b.cylz("Lava", x, y, 1.0, DZ - 2.6, 0.35, 6, r2=0.55)
    return b


def magma_gate():
    b = Builder("MagmaGate", AREA)
    for sx in (-1, 1):
        x = sx * 11.0
        b.bx("BasaltLight", x - 5.0, x + 5.0, -4.5, 4.5, 0, 2.0)
        b.mesh("Basalt", [(x - 4.2, -3.8, 2), (x + 4.2, -3.8, 2), (x + 4.2, 3.8, 2), (x - 4.2, 3.8, 2),
                          (x - 3.4, -3.2, 24), (x + 3.4, -3.2, 24), (x + 3.4, 3.2, 24), (x - 3.4, 3.2, 24)],
               [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
        face_stones(b, "BasaltLight", (x, -3.6, 0), 7.0, 2.2, 22.0, density=0.35)
        b.bx("BasaltLight", x - 4.2, x + 4.2, -3.9, 3.9, 24, 25.6)
        horn(b, "Obsidian", (x + sx * 2.0, 0, 25.4), sx, 1.4)
        horn(b, "Obsidian", (x - sx * 1.5, 0, 25.4), -sx, 0.8)
        # lava spout from a carved mouth into a basin
        b.bx("Charcoal", x - 1.2, x + 1.2, -3.6, -3.1, 12.0, 13.4)
        b.prism_x("BasaltLight", [(-3.4, 13.4), (-5.0, 13.0), (-3.4, 12.6)], x - 1.6, x + 1.6)
        b.box("Lava", (x, -4.9, 7.6), (1.4, 0.6, 9.4), rx=-0.08)
        b.lathe("BasaltLight", [(0, 0), (2.6, 0), (2.9, 2.0), (2.5, 2.0), (2.3, 0.6), (0, 0.6)], c=(x, -5.6, 2.0), n=10)
        b.cylz("Lava", x, -5.6, 2.3, 3.6, 2.45, 10)
        b.ball("Fire", (x, -5.0, 3.6), 0.9, seg=(8, 6), sc=(1, 1, 0.6))
    # the arch, a glowing keystone, iron portcullis drawn up
    b.arch("BasaltLight", (0, 0, 15.0), 7.6, 10.4, 7.0, n=14)
    b.arch("Basalt", (0, -3.7, 15.0), 10.4, 11.0, 0.6, n=14)
    b.prism_y("Lava", [(-1.4, 25.2), (1.4, 25.2), (1.0, 22.6), (-1.0, 22.6)], -3.9, 3.6)
    b.prism_y("Basalt", [(-1.9, 25.8), (1.9, 25.8), (1.4, 22.2), (-1.4, 22.2)], -3.7, 3.4)
    for k in range(9):
        x = -6.4 + k * 1.6
        top = 15.0 + math.sqrt(max(0, 7.6 ** 2 - x * x)) - 0.4
        b.bx("DarkMetal", x - 0.22, x + 0.22, -0.3, 0.3, 17.0, top)
        b.cylz("DarkMetal", x, 0, 16.2, 17.0, 0.3, 6, r2=0.0)
    for z in (18.0, 20.0):
        b.bx("DarkMetal", -7.4, 7.4, -0.35, 0.35, z, z + 0.4)
    b.bx("BasaltLight", -16.0, 16.0, -4.4, 4.4, 25.6, 27.0)
    b.bx("Basalt", -8.0, 8.0, -4.2, -3.6, 21.4, 25.4)
    b.text("Fire", "VOLCANO", (0, -4.35, 23.4), 2.3, depth=0.3, font="black")
    # stair threshold
    b.bx("BasaltLight", -7.6, 7.6, -5.6, 4.5, 0, 0.8)
    b.bx("BasaltLight", -6.6, 6.6, -6.8, -5.6, 0, 0.4)
    return b


def crystal_cluster():
    b = Builder("CrystalCluster", AREA)
    b.rock("Basalt", (0, 0, 0.6), 4.6, sc=(1.3, 1.1, 0.5))
    b.rock("BasaltLight", (3.4, 1.6, 0.4), 2.4, sc=(1.2, 1, 0.6))
    rng = b.rng
    spec = [(0, 0, 0.0, 0.0, 1.6, 11.0, "Obsidian"), (1.8, 0.6, 0.35, 0.5, 1.1, 7.0, "Obsidian"),
            (-1.9, 0.9, -0.4, -0.2, 1.0, 6.4, "Obsidian"), (0.6, -1.9, 0.25, -0.3, 0.9, 5.2, "Ember"),
            (-1.0, -1.4, -0.3, -0.5, 0.7, 4.2, "Lava"), (2.6, -0.8, 0.5, -0.2, 0.6, 3.6, "Ember"),
            (-2.8, -0.4, -0.55, 0.1, 0.7, 4.6, "Obsidian"), (0.4, 2.2, 0.1, 0.45, 0.9, 6.0, "Ember"),
            (3.6, 1.8, 0.3, 0.4, 0.6, 3.4, "Obsidian")]
    for (x, y, ax, ay, r, h, st) in spec:
        with b.at(T(x, y, 1.6), R(ay * 0.8, ax * 0.8, rng.uniform(0, 1))):
            b.lathe(st, [(0, -1.0), (r, -1.0), (r, h * 0.72), (0, h)], n=6)
            if st == "Obsidian":
                b.lathe("Lava", [(0, h * 0.2), (r * 0.42, h * 0.2), (r * 0.42, h * 0.6), (0, h * 0.75)], n=6)
    return b


def lava_fall():
    b = Builder("LavaFall", AREA)
    rng = b.rng
    for k in range(24):
        x = rng.uniform(-16, 16)
        y = rng.uniform(3, 10)
        z = rng.uniform(0, 18) * (1 - abs(x) / 28)
        b.rock("Basalt" if k % 3 else "BasaltLight", (x, y, z), rng.uniform(4.5, 7.0), sc=(1.2, 0.9, 0.9), jitter=0.24)
    for x in (-10, -4, 3, 9):
        b.rock("Basalt", (x, 7, 21 - abs(x) * 0.4), 5.6, sc=(1.1, 1.0, 0.7))
    lip = 22.5
    for k in range(8):
        z1 = lip - k * 2.9
        z0 = z1 - 3.2
        w = 4.6 + k * 0.35
        yy = 2.0 - k * 0.55
        b.box("Lava", (0, yy, (z0 + z1) / 2), (w, 0.9, z1 - z0), rx=-0.12)
        for j in range(3):
            b.box("Fire", (-w / 2 + 1 + j * (w - 2) / 2, yy - 0.5, (z0 + z1) / 2), (0.3, 0.2, (z1 - z0) * 0.7), rx=-0.12, bev=0)
    b.box("Lava", (0, 4.0, lip + 0.2), (5.0, 4.0, 0.6))
    # pool with a crust edge and floating crust plates
    b.lathe("Lava", [(0, 0), (10.0, 0), (10.0, 0.7), (0, 0.7)], c=(0, -6, 0), n=20)
    b.ring("LavaDim", (0, -6, 0), 11.2, 9.6, 0.0, 0.9, n=20)
    for k in range(16):
        a = TAU * k / 16
        if 1.2 < a < 1.95:
            continue
        b.rock("Basalt" if k % 2 else "BasaltLight", (math.cos(a) * 11.6, -6 + math.sin(a) * 11.0, 0.6), rng.uniform(1.4, 2.3), sc=(1.2, 1, 0.7))
    for k in range(6):
        a = rng.uniform(0, TAU)
        rr = rng.uniform(3, 7.5)
        b.rock("Basalt", (math.cos(a) * rr, -6 + math.sin(a) * rr, 0.75), rng.uniform(0.8, 1.5), sc=(1.4, 1.2, 0.2))
    for k in range(6):
        b.ball("Fire", (rng.uniform(-3, 3), rng.uniform(-3, 0), 0.9), rng.uniform(0.5, 1.0), seg=(8, 6), sc=(1, 1, 0.5))
    return b


def mine_cart():
    b = Builder("MineCart", AREA)
    L = 30.0
    for k in range(16):
        y = -L / 2 + 1 + k * (L - 2) / 15
        b.bx("WoodDark", -2.6, 2.6, y - 0.5, y + 0.5, 0, 0.5)
    for sx in (-1, 1):
        b.bx("Metal", sx * 1.6 - 0.18, sx * 1.6 + 0.18, -L / 2, L / 2, 0.5, 0.95)
        b.bx("DarkMetal", sx * 1.6 - 0.35, sx * 1.6 + 0.35, -L / 2, L / 2, 0.5, 0.62, bev=0)
    # buffer stop
    b.bx("WoodDark", -2.6, 2.6, L / 2 - 0.6, L / 2 + 0.6, 0.5, 3.2)
    for sx in (-1, 1):
        b.cyl("WoodDark", (sx * 1.6, L / 2 - 3.0, 0.5), (sx * 1.6, L / 2 - 0.3, 3.0), 0.3, 6)
        b.cyl("Red", (sx * 1.6, L / 2 - 0.6, 2.4), (sx * 1.6, L / 2 - 1.4, 2.4), 0.45, 8)
    # the cart
    with b.at(T(0, -3.0, 0.95)):
        for sy in (-1.8, 1.8):
            for sx in (-1, 1):
                b.cyl("DarkMetal", (sx * 1.45, sy, 0.95), (sx * 1.85, sy, 0.95), 0.95, 12)
                b.cyl("Metal", (sx * 1.85, sy, 0.95), (sx * 1.95, sy, 0.95), 0.35, 8)
            b.cyl("DarkMetal", (-1.5, sy, 0.95), (1.5, sy, 0.95), 0.18, 6)
        b.bx("DarkMetal", -1.8, 1.8, -2.6, 2.6, 1.4, 1.9)
        b.mesh("Rust", [(-1.9, -2.6, 1.9), (1.9, -2.6, 1.9), (1.9, 2.6, 1.9), (-1.9, 2.6, 1.9),
                        (-2.5, -3.3, 5.0), (2.5, -3.3, 5.0), (2.5, 3.3, 5.0), (-2.5, 3.3, 5.0)],
               [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
        for z in (2.4, 4.6):
            f = (z - 1.9) / 3.1
            hw, hd = 1.9 + 0.6 * f + 0.08, 2.6 + 0.7 * f + 0.08
            b.bx("DarkMetal", -hw, hw, -hd, -hd + 0.25, z - 0.2, z + 0.2, bev=0)
            b.bx("DarkMetal", -hw, hw, hd - 0.25, hd, z - 0.2, z + 0.2, bev=0)
        for k in range(12):
            x, y = b.rng.uniform(-1.8, 1.8), b.rng.uniform(-2.4, 2.4)
            st = ("Ember", "Gold", "BasaltLight", "Lava")[k % 4]
            b.rock(st, (x, y, 5.0), b.rng.uniform(0.6, 1.0), sc=(1, 1, 0.9))
        b.cyl("DarkMetal", (0, -3.3, 3.6), (0, -4.2, 3.6), 0.15, 6)
        b.torus("DarkMetal", (0, -4.5, 3.6), 0.35, 0.1, 8, 4, rx=PI / 2)
    # lantern post
    b.cylz("WoodDark", 4.4, 6.0, 0, 8.0, 0.35, 6)
    b.cyl("WoodDark", (4.4, 6.0, 7.6), (2.6, 6.0, 7.6), 0.2, 6)
    b.cylz("DarkMetal", 2.6, 6.0, 6.0, 6.3, 0.55, 8)
    b.cylz("Fire", 2.6, 6.0, 6.3, 7.1, 0.42, 8)
    b.cylz("DarkMetal", 2.6, 6.0, 7.1, 7.5, 0.55, 8, r2=0.15)
    # ore pile beside the track
    for k in range(9):
        b.rock(("BasaltLight", "Ember", "Basalt")[k % 3], (-5.0 + b.rng.uniform(-1.5, 1.5), 6.0 + b.rng.uniform(-1.5, 1.5), 0.5 + (k % 3) * 0.6), 1.1)
    return b


def fire_pillar():
    b = Builder("FirePillar", AREA)
    b.bx("BasaltLight", -3.6, 3.6, -3.6, 3.6, 0, 1.4)
    b.bx("Basalt", -3.0, 3.0, -3.0, 3.0, 1.4, 2.4)
    b.mesh("Basalt", [(-2.2, -2.2, 2.4), (2.2, -2.2, 2.4), (2.2, 2.2, 2.4), (-2.2, 2.2, 2.4),
                      (-1.6, -1.6, 15.0), (1.6, -1.6, 15.0), (1.6, 1.6, 15.0), (-1.6, 1.6, 15.0)],
           [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
    for rz in (0, PI / 2, PI, -PI / 2):
        with b.at(R(0, 0, rz)):
            for k, z in enumerate((4.0, 6.6, 9.2, 11.8)):
                hw = 2.2 - 0.6 * (z - 2.4) / 12.6
                shape = k % 3
                if shape == 0:
                    b.bx("Lava", -0.5, 0.5, -hw - 0.15, -hw + 0.1, z, z + 1.6)
                    b.bx("Lava", -0.9, 0.9, -hw - 0.15, -hw + 0.1, z + 0.6, z + 1.0)
                elif shape == 1:
                    b.prism_y("Lava", [(-0.8, z), (0.8, z), (0, z + 1.6)], -hw - 0.15, -hw + 0.1)
                else:
                    b.bx("Lava", -0.8, 0.8, -hw - 0.15, -hw + 0.1, z, z + 0.35)
                    b.bx("Lava", -0.18, 0.18, -hw - 0.15, -hw + 0.1, z, z + 1.6)
    b.bx("BasaltLight", -2.4, 2.4, -2.4, 2.4, 15.0, 15.8)
    b.lathe("DarkMetal", [(0, 0), (1.0, 0), (2.6, 1.2), (2.9, 1.8), (0, 1.6)], c=(0, 0, 15.8), n=10)
    for k in range(4):
        a = TAU * k / 4 + PI / 4
        b.cyl("DarkMetal", (math.cos(a) * 2.6, math.sin(a) * 2.6, 17.4), (math.cos(a) * 3.2, math.sin(a) * 3.2, 18.6), 0.2, 5, r2=0.05)
    b.cylz("Fire", 0, 0, 17.2, 21.5, 2.0, 8, r2=0.0)
    b.cylz("Ember", 0, 0, 17.2, 18.8, 2.3, 8, r2=0.9)
    return b


def charred_hut():
    b = Builder("CharredHut", AREA)
    rng = b.rng
    X0, X1, Y0, Y1 = -8, 8, -6, 7
    b.bx("BasaltLight", X0 - 0.8, X1 + 0.8, Y0 - 0.8, Y1 + 0.8, 0, 0.8)
    # broken walls: block courses with a ragged top
    for side, (ax, ay, L) in enumerate(((X0, Y0, X1 - X0), (X1, Y0, Y1 - Y0), (X1, Y1, X1 - X0), (X0, Y1, Y1 - Y0))):
        n = int(L / 2.0)
        for i in range(n):
            t = (i + 0.5) * L / n
            topz = 8.5 - abs(math.sin(i * 1.7 + side)) * 5.0 - (3.0 if (side == 0 and 3 <= i <= 4) else 0)
            if side == 0 and 3 <= i <= 4:
                topz = 0.8
            rows = int((topz - 0.8) / 1.2)
            for r in range(rows):
                z = 0.8 + r * 1.2
                off = 0.5 if r % 2 else 0
                if side == 0:
                    c = (ax + t + off - 0.25, ay, z + 0.6)
                    s = (2.0 - 0.2, 1.4, 1.1)
                elif side == 1:
                    c = (ax, ay + t + off - 0.25, z + 0.6)
                    s = (1.4, 2.0 - 0.2, 1.1)
                elif side == 2:
                    c = (ax - t - off + 0.25, ay, z + 0.6)
                    s = (2.0 - 0.2, 1.4, 1.1)
                else:
                    c = (ax, ay + L - t - off + 0.25, z + 0.6)
                    s = (1.4, 2.0 - 0.2, 1.1)
                b.box("Basalt" if rng.random() > 0.25 else "StoneDark", c, s, rz=rng.uniform(-0.03, 0.03), bev=0.15)
    # fallen roof beams, charred
    for k, (p0, p1) in enumerate((((-7, -4, 0.9), (2, 5, 6.0)), ((-3, -5, 0.9), (6, 6, 7.0)), ((5, -5, 0.9), (-6, 4, 4.0)),
                                 ((-8, 2, 8.0), (8, 2, 6.5)))):
        b.cyl("Charcoal", p0, p1, 0.55, 6)
    for k in range(10):
        b.rock("Ember" if k % 3 == 0 else "Charcoal", (rng.uniform(-6, 6), rng.uniform(-4, 5), 1.0), rng.uniform(0.5, 1.0), sc=(1.4, 1.2, 0.6))
    for k in range(3):
        x, y = rng.uniform(-4, 4), rng.uniform(-3, 4)
        b.cylz("Fire", x, y, 0.9, 0.9 + rng.uniform(1.6, 2.6), 0.6, 6, r2=0.0)
    b.bx("Rust", -2.0, 2.0, Y0 - 3.0, Y0 - 2.6, 0.8, 1.2, rz=0.3)
    return b


ASSETS = [obsidian_temple, lava_forge, watchtower, lava_bridge, magma_gate, crystal_cluster, lava_fall,
          mine_cart, fire_pillar, charred_hut]
