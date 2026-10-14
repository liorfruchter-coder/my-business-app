"""Area 7 -- Snowy Peaks: log cabins under thick snow, blue ice, red trim."""
import math

from kit import PI, TAU, Builder, R, T, V, catenary

AREA = "SnowyPeaks"
GROUND = (226, 236, 246)


def icicles(b, p0, p1, z, n=None, maxlen=1.8, st="Ice"):
    p0, p1 = V((p0[0], p0[1], z)), V((p1[0], p1[1], z))
    L = (p1 - p0).length
    n = n or max(2, int(L / 1.1))
    for i in range(n):
        p = p0.lerp(p1, (i + 0.5) / n)
        h = b.rng.uniform(0.5, maxlen)
        b.cyl(st, (p.x, p.y, z), (p.x, p.y, z - h), 0.3, 5, r2=0.0)


def drift(b, c, r, sc=(1.4, 1.1, 0.5)):
    b.dome("Snow", (c[0], c[1], 0.0), r, seg=14, rings=4, sc=(sc[0], sc[1], sc[2] * 1.3))


def snow_cap(b, x0, x1, y0, y1, z, t=0.8, over=0.4):
    b.bx("Snow", x0 - over, x1 + over, y0 - over, y1 + over, z, z + t, bev=0.3)


def log_wall(b, p0, p1, z0, z1, r=0.62, styles=("WoodDark", "Bark"), over=1.2):
    p0, p1 = V((p0[0], p0[1], 0)), V((p1[0], p1[1], 0))
    d = (p1 - p0).normalized()
    n = int((z1 - z0) / (2 * r * 0.92))
    for k in range(n):
        z = z0 + r + k * 2 * r * 0.92
        a = p0 - d * over
        bb = p1 + d * over
        b.cyl(styles[k % len(styles)], (a.x, a.y, z), (bb.x, bb.y, z), r, 8)
        for e in (a, bb):
            b.cyl("WoodLight", (e.x, e.y, z), (e.x - d.x * 0.05, e.y - d.y * 0.05, z), r * 0.85, 8)


def ice_castle():
    b = Builder("IceCastle", AREA)
    rng = b.rng
    # snow mound base
    b.lathe("Snow", [(0, 0), (32, 0), (30, 1.5), (26, 2.6), (0, 2.8)], n=24, sc=(1.0, 0.8))
    Z = 2.6
    # curtain walls round a court
    corners = [(-18, -12), (18, -12), (18, 12), (-18, 12)]
    for i in range(4):
        (x0, y0), (x1, y1) = corners[i], corners[(i + 1) % 4]
        if i == 0:
            for (a, c) in ((x0, -5.0), (5.0, x1)):
                b.bx("IceDeep", a, c, y0 - 1.6, y0 + 1.6, Z, Z + 14)
            b.bx("IceDeep", -5.0, 5.0, y0 - 1.6, y0 + 1.6, Z + 11, Z + 14)
        else:
            b.bx("IceDeep", min(x0, x1) - 1.6, max(x0, x1) + 1.6, min(y0, y1) - 1.6, max(y0, y1) + 1.6, Z, Z + 14)
        # block coursing on the outer faces
        d = V((x1 - x0, y1 - y0, 0))
        L = d.length
        nrm = V((d.y, -d.x, 0)).normalized()
        rz = math.atan2(d.y, d.x)
        for row in range(5):
            z = Z + 1.4 + row * 2.6
            m = int(L / 3.0)
            for j in range(m):
                if (row + j) % 3 == 0:
                    continue
                t = (j + 0.5 + (0.5 if row % 2 else 0)) / m
                if t > 1:
                    continue
                p = V((x0, y0, 0)) + d * t + nrm * 1.65
                if i == 0 and abs(p.x) < 5.6 and z < Z + 11:
                    continue
                b.box("Ice", (p.x, p.y, z), (2.6, 0.5, 2.2), rz=rz, bev=0.2)
        # crenellations + snow
        for j in range(int(L / 3.0)):
            t = (j + 0.5) / int(L / 3.0)
            p = V((x0, y0, 0)) + d * t + nrm * 1.0
            b.box("Ice", (p.x, p.y, Z + 15.2), (1.8, 1.2, 2.4), rz=rz)
            b.box("Snow", (p.x, p.y, Z + 16.6), (2.0, 1.4, 0.5), rz=rz, bev=0.2)
        icicles(b, (x0 + nrm.x * 1.8, y0 + nrm.y * 1.8), (x1 + nrm.x * 1.8, y1 + nrm.y * 1.8), Z + 14.0, maxlen=2.2)
    # gate: glowing arch + icicle portcullis
    b.arch("IceGlow", (0, -12 - 1.7, Z + 6.5), 5.0, 5.8, 0.6, n=12)
    b.arch("IceDeep", (0, -12, Z + 6.5), 5.0, 6.6, 3.2, n=12)
    b.bx("IceDeep", -6.6, -5.0, -13.6, -10.4, Z, Z + 6.5)
    b.bx("IceDeep", 5.0, 6.6, -13.6, -10.4, Z, Z + 6.5)
    for k in range(7):
        x = -4.2 + k * 1.4
        top = Z + 6.5 + math.sqrt(max(0, 25 - x * x)) - 0.3
        b.cyl("Ice", (x, -12, top), (x, -12, top - 3.0 - (k % 2) * 1.2), 0.32, 6, r2=0.0)
    b.bx("Snow", -5.0, 5.0, -15.0, -10.0, Z, Z + 0.3, bev=0)

    def tower(x, y, r, h, sides=6, spire=8.0, glow=True):
        b.lathe("IceDeep", [(0, Z), (r, Z), (r * 0.94, Z + h), (0, Z + h)], c=(x, y, 0), n=sides)
        for k in range(sides):
            a = TAU * (k + 0.5) / sides
            for z in (Z + h * 0.35, Z + h * 0.7):
                ww = 0.9
                with b.at(T(x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9, z), R(0, 0, a + PI / 2)):
                    b.box("IceGlow", (0, -0.2, 0), (ww, 0.4, 2.6))
                    b.arch("Ice", (0, -0.35, 1.3), ww / 2, ww / 2 + 0.4, 0.4, n=6)
        b.lathe("Ice", [(r * 0.94, Z + h), (r + 1.0, Z + h), (r + 1.0, Z + h + 1.6), (r * 0.94, Z + h + 1.6)], c=(x, y, 0), n=sides, cap=False)
        b.lathe("Ice", [(0, Z + h), (r * 0.95, Z + h), (r * 0.95, Z + h + 1.0), (0, Z + h + 1.0)], c=(x, y, 0), n=sides)
        b.lathe("Snow", [(0, Z + h + 1.6), (r + 1.2, Z + h + 1.6), (r + 0.4, Z + h + 2.6), (0, Z + h + 2.4)], c=(x, y, 0), n=sides)
        b.lathe("Ice", [(0, Z + h + 2.4), (r * 0.85, Z + h + 2.4), (0, Z + h + 2.4 + spire)], c=(x, y, 0), n=sides)
        if glow:
            b.ball("IceGlow", (x, y, Z + h + 2.6 + spire), 0.6, seg=(8, 6))
        for k in range(sides):
            a = TAU * k / sides
            b.cyl("Ice", (x + math.cos(a) * (r + 1.0), y + math.sin(a) * (r + 1.0), Z + h), (x + math.cos(a) * (r + 1.0), y + math.sin(a) * (r + 1.0), Z + h - 2.0), 0.3, 5, r2=0.0)

    for (x, y) in corners:
        tower(x, y, 4.4, 20.0, spire=8.0)
    tower(0, 3.0, 7.2, 34.0, sides=8, spire=14.0)
    for sx in (-1, 1):
        tower(sx * 7.0, -12.0, 2.6, 16.0, spire=5.0, glow=False)
    # crystal shards at the base
    for k in range(10):
        a = rng.uniform(0, TAU)
        rr = rng.uniform(22, 27)
        x, y = math.cos(a) * rr, math.sin(a) * rr * 0.8
        for j in range(3):
            with b.at(T(x + rng.uniform(-1, 1), y + rng.uniform(-1, 1), 1.2), R(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, 1))):
                h = rng.uniform(2.5, 6.0)
                b.lathe("IceGlow" if j == 0 else "Ice", [(0, -0.5), (0.6, -0.5), (0.6, h * 0.7), (0, h)], n=6)
    return b


def ski_lodge():
    b = Builder("SkiLodge", AREA)
    W, D = 32.0, 22.0
    X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
    # stone foundation storey
    b.bx("Stone", X0, X1, Y0, Y1, 0, 4.0)
    for k in range(40):
        x = b.rng.uniform(X0 + 0.8, X1 - 0.8)
        z = b.rng.uniform(0.6, 3.4)
        b.box("StoneDark", (x, Y0 - 0.12, z), (b.rng.uniform(1.0, 2.0), 0.4, b.rng.uniform(0.7, 1.1)), bev=0.15)
    # log walls
    for (p0, p1) in (((X0, Y0), (X1, Y0)), ((X1, Y0), (X1, Y1)), ((X1, Y1), (X0, Y1)), ((X0, Y1), (X0, Y0))):
        log_wall(b, p0, p1, 4.0, 14.0)
    b.bx("WoodDark", X0 + 0.3, X1 - 0.3, Y0 + 0.3, Y1 - 0.3, 4.0, 14.0)
    # gable roof (ridge front to back) with a thick snow layer
    with b.at(R(0, 0, PI / 2)):
        b.gable_roof("WoodRed", 0, 0, 14.0, D, W, 11.0, t=0.9, over=2.2)
        a = math.atan2(11.0, W / 2)
        for sgn in (-1, 1):
            ex = W / 2 + 2.2
            ez = 14.0 - 2.2 * math.tan(a)
            pts = [(sgn * ex, ez + 0.01), (0, 14.0 + 11.0 + 0.01), (0, 14.0 + 11.0 + 1.3), (sgn * (ex + 0.3), ez + 1.0)]
            if sgn > 0:
                pts = pts[::-1]
            b.prism_x("Snow", pts, -D / 2 - 2.0, D / 2 + 2.0)
        b.gable_end("WoodDark", -D / 2 - 0.2, 0, 14.0, W, 11.0, t=0.5)
        b.gable_end("WoodDark", D / 2 + 0.2, 0, 14.0, W, 11.0, t=0.5)
    # big A-frame window in the front gable
    with b.at(T(0, Y0 - 0.6, 14.0)):
        b.prism_y("Glass", [(-8.0, 0.6), (8.0, 0.6), (0, 8.4)], -0.1, 0.1)
        for x in (-4.0, 0.0, 4.0):
            top = 8.4 - abs(x) * (7.8 / 8.0)
            b.bx("WoodDark", x - 0.25, x + 0.25, -0.35, 0.05, 0.6, top)
        b.bx("WoodDark", -8.0, 8.0, -0.35, 0.05, 0.3, 0.8)
        b.bx("WoodDark", -5.3, 5.3, -0.35, 0.05, 3.4, 3.8)
    # balcony across the front
    b.bx("WoodLight", X0 - 1.0, X1 + 1.0, Y0 - 4.0, Y0, 13.4, 14.0)
    for x in (X0 - 0.6, -8, 0, 8, X1 + 0.6):
        b.cylz("WoodDark", x, Y0 - 3.6, 4.0, 13.4, 0.35, 8)
        b.cyl("WoodDark", (x, Y0 - 3.6, 11.4), (x, Y0 - 0.2, 13.2), 0.22, 6)
    b.rail("WoodDark", "WoodLight", (X0 - 0.8, Y0 - 3.8), (X1 + 0.8, Y0 - 3.8), 14.0, h=2.8, spacing=2.6, balusters="WoodDark", bal_sp=0.7)
    snow_cap(b, X0 - 1.0, X1 + 1.0, Y0 - 4.2, Y0 - 3.4, 16.8, t=0.4, over=0.2)
    # ground floor door + windows, windows above
    b.door("WoodRed", "WoodDark", (0, Y0 - 0.2, 4.0), 4.0, 7.0, steps="Stone")
    for x in (-10, -5, 5, 10):
        b.window("WindowGlow" if x in (-5, 10) else "Glass", "WoodDark", (x, Y0 - 0.7, 9.2), 2.6, 3.4, shutters="Red", sill="WoodDark")
        b.bx("Snow", x - 1.8, x + 1.8, Y0 - 1.6, Y0 - 0.7, 7.15, 7.5, bev=0.1)
    for y in (-5, 0, 5):
        for sx in (-1, 1):
            b.window("Glass", "WoodDark", (sx * (W / 2 + 0.7), y, 9.2), 2.4, 3.2, rz=sx * PI / 2, shutters="Red", sill="WoodDark")
    # chimney
    b.bx("Stone", X1 - 6, X1 - 2.6, Y1 - 6, Y1 - 2.6, 14.0, 26.0)
    b.bx("StoneDark", X1 - 6.3, X1 - 2.3, Y1 - 6.3, Y1 - 2.3, 25.4, 26.4)
    b.bx("Snow", X1 - 6.4, X1 - 2.2, Y1 - 6.4, Y1 - 2.2, 26.4, 26.9, bev=0.2)
    # sign + skis by the door + snow drifts
    b.bx("WoodDark", -5.0, 5.0, Y0 - 4.5, Y0 - 4.1, 15.4, 17.2)
    b.text("White", "LODGE", (0, Y0 - 4.6, 16.3), 1.3, depth=0.15, font="black")
    for k, col in enumerate(("Red", "Navy", "Yellow", "SkyBlue")):
        b.box(col, (5.0 + k * 0.7, Y0 - 1.0, 3.8), (0.4, 0.15, 7.2), rx=0.15)
    for k in range(6):
        a = TAU * k / 6
        drift(b, (math.cos(a) * 19, math.sin(a) * 14, 0.3), 2.6, sc=(1.4, 1.1, 0.5))
    return b


def ski_lift_station():
    b = Builder("SkiLiftStation", AREA)
    b.bx("Concrete", -12, 12, -9, 9, 0, 1.0)
    b.bx("WoodRed", -12, 12, 4, 9, 1.0, 9.0)
    for x in (-11.4, 11.4):
        b.bx("WoodRed", x - 0.6, x + 0.6, -9, 9, 1.0, 9.0)
    for x in (-11.4, 11.4):
        b.bx("Concrete", x - 0.8, x + 0.8, -9, -6, 1.0, 13.0)
    b.bx("White", -12.8, 12.8, -9.5, 9.5, 13.0, 13.8)
    with b.at(R(0, 0, PI / 2)):
        b.gable_roof("Charcoal", 0, 0, 13.8, 19, 25.6, 4.0, t=0.5, over=0.8)
        a = math.atan2(4.0, 12.8)
        for sgn in (-1, 1):
            pts = [(sgn * 13.6, 13.6), (0, 17.85), (0, 18.7), (sgn * 13.8, 14.3)]
            if sgn > 0:
                pts = pts[::-1]
            b.prism_x("Snow", pts, -10.3, 10.3)
    # bull wheel
    b.cylz("DarkMetal", 0, 0, 1.0, 12.4, 0.8, 10)
    b.torus("Metal", (0, 0, 11.0), 7.0, 0.55, 28, 6)
    for k in range(8):
        a = TAU * k / 8
        b.cyl("Metal", (0, 0, 11.6), (math.cos(a) * 7.0, math.sin(a) * 7.0, 11.0), 0.2, 5)
    b.lathe("Yellow", [(0, 11.4), (1.8, 11.4), (1.4, 12.6), (0, 12.6)], n=10)
    # cables heading out (toward -Y) + parked chairs
    for x in (-7.0, 7.0):
        b.cyl("Charcoal", (x, 0, 11.0), (x, -20.0, 13.0), 0.12, 4)
    for k, (x, y) in enumerate(((-7.0, -6.0), (7.0, -10.0), (7.0, 3.0))):
        chair(b, (x, y, 11.0 + (-y * 0.1 if y < 0 else 0)), col=("Red", "Navy", "Yellow")[k])
    # loading ramp + operator hut
    b.bx("WoodLight", -3.0, 3.0, -9.0, -2.0, 1.0, 1.4)
    with b.at(T(9.0, -12.0, 0)):
        b.bx("White", -2.5, 2.5, -2.0, 2.0, 0, 6.5)
        b.bx("GlassDark", -2.6, 2.6, -2.1, 2.1, 3.5, 5.6, bev=0)
        b.bx("Red", -3.0, 3.0, -2.5, 2.5, 6.5, 7.0)
        b.bx("Snow", -3.1, 3.1, -2.6, 2.6, 7.0, 7.5, bev=0.2)
    b.bx("Navy", -5, 5, -9.7, -9.3, 9.4, 11.8)
    b.text("White", "SKI LIFT", (0, -9.75, 10.6), 1.4, depth=0.15, font="black")
    return b


def chair(b, top, col="Red"):
    x, y, z = top
    b.cyl("DarkMetal", (x, y, z), (x, y, z - 6.0), 0.12, 5)
    b.torus("DarkMetal", (x, y, z + 0.1), 0.3, 0.08, 8, 3, rx=PI / 2)
    with b.at(T(x, y, z - 6.0)):
        b.cyl("DarkMetal", (-1.8, 0, 0), (1.8, 0, 0), 0.1, 4)
        for sx in (-1.8, 1.8):
            b.cyl("DarkMetal", (sx, 0, 0), (sx, 0, -2.4), 0.1, 4)
        b.bx(col, -1.8, 1.8, -0.9, 0.9, -2.5, -2.2)
        b.bx(col, -1.8, 1.8, 0.6, 0.9, -2.2, -0.4)
        b.cyl("DarkMetal", (-1.8, -0.8, -0.4), (1.8, -0.8, -0.4), 0.08, 4)


def ski_lift_tower():
    b = Builder("SkiLiftTower", AREA)
    b.bx("Concrete", -2.4, 2.4, -2.4, 2.4, 0, 1.2)
    b.lathe("Metal", [(0, 1.2), (1.4, 1.2), (0.9, 26.0), (0, 26.0)], n=8)
    for z in (6, 12, 18):
        b.torus("DarkMetal", (0, 0, z), 1.35 - z * 0.019, 0.12, 10, 4)
    b.bx("Yellow", -8.0, 8.0, -0.8, 0.8, 26.0, 27.2)
    for sx in (-1, 1):
        x = sx * 7.0
        b.bx("DarkMetal", x - 0.3, x + 0.3, -3.2, 3.2, 25.0, 25.6)
        for y in (-2.4, -0.8, 0.8, 2.4):
            b.cyl("Charcoal", (x - 0.35, y, 25.0), (x + 0.35, y, 25.0), 0.55, 10)
        b.cyl("Charcoal", (x, -16.0, 23.6), (x, 16.0, 26.4), 0.12, 4)
    chair(b, (7.0, -6.0, 24.6), "Red")
    chair(b, (-7.0, 8.0, 25.6), "Navy")
    # maintenance ladder
    for sx in (-0.35, 0.35):
        b.cyl("DarkMetal", (sx, -1.45, 1.2), (sx, -1.0, 25.0), 0.06, 4)
    for k in range(30):
        t = k / 30
        b.cyl("DarkMetal", (-0.35, -1.45 + 0.45 * t, 1.6 + t * 23), (0.35, -1.45 + 0.45 * t, 1.6 + t * 23), 0.05, 3)
    b.bx("Snow", -8.2, 8.2, -1.0, 1.0, 27.2, 27.6, bev=0.15)
    return b


def log_cabin():
    b = Builder("LogCabin", AREA)
    W, D = 16.0, 12.0
    b.bx("StoneDark", -W / 2, W / 2, -D / 2, D / 2, 0, 1.0)
    for (p0, p1) in (((-W / 2, -D / 2), (W / 2, -D / 2)), ((W / 2, -D / 2), (W / 2, D / 2)), ((W / 2, D / 2), (-W / 2, D / 2)), ((-W / 2, D / 2), (-W / 2, -D / 2))):
        log_wall(b, p0, p1, 1.0, 9.0, r=0.55, styles=("Bark", "WoodDark"), over=1.0)
    b.bx("WoodDark", -W / 2 + 0.3, W / 2 - 0.3, -D / 2 + 0.3, D / 2 - 0.3, 1.0, 9.0)
    b.gable_roof("WoodDark", 0, 0, 9.0, W, D, 5.5, t=0.6, over=1.5)
    a = math.atan2(5.5, D / 2)
    for sgn in (-1, 1):
        ex = D / 2 + 1.5
        ez = 9.0 - 1.5 * math.tan(a)
        pts = [(sgn * ex, ez + 0.01), (0, 14.5 + 0.01), (0, 15.8), (sgn * (ex + 0.25), ez + 1.1)]
        if sgn > 0:
            pts = pts[::-1]
        b.prism_x("Snow", pts, -W / 2 - 1.8, W / 2 + 1.8)
    for x in (-W / 2 - 0.2, W / 2 + 0.2):
        b.gable_end("WoodDark", x, 0, 9.0, D, 5.5, t=0.4)
    icicles(b, (-W / 2 - 1.5, -D / 2 - 1.6), (W / 2 + 1.5, -D / 2 - 1.6), ez + 0.1, maxlen=1.6)
    b.door("WoodRed", "WoodLight", (-2.5, -D / 2 - 0.6, 1.0), 3.0, 6.0)
    b.window("WindowGlow", "WoodLight", (3.5, -D / 2 - 0.6, 5.0), 2.6, 2.6, shutters="Red", sill="WoodLight")
    b.bx("Snow", 1.8, 5.2, -D / 2 - 1.6, -D / 2 - 0.6, 3.25, 3.6, bev=0.1)
    # chimney + porch lantern + firewood stack
    b.bx("Stone", W / 2 - 3.6, W / 2 - 1.4, -1.0, 1.4, 9.0, 17.4)
    b.bx("Snow", W / 2 - 3.8, W / 2 - 1.2, -1.2, 1.6, 17.4, 17.9, bev=0.2)
    b.bx("Charcoal", -4.4, -3.8, -D / 2 - 1.2, -D / 2 - 0.6, 5.6, 6.6)
    b.box("WindowGlow", (-4.1, -D / 2 - 0.9, 6.1), (0.45, 0.45, 0.7))
    with b.at(T(-W / 2 - 2.5, 0, 0)):
        for row in range(4):
            for k in range(5 - (row % 2)):
                y = -4 + k * 1.9 + (row % 2) * 0.95
                b.cyl("Bark", (-1.4, y, 0.55 + row * 1.0), (1.4, y, 0.55 + row * 1.0), 0.5, 7)
                b.cyl("WoodLight", (-1.42, y, 0.55 + row * 1.0), (-1.38, y, 0.55 + row * 1.0), 0.42, 7)
        b.bx("Snow", -1.6, 1.6, -5.0, 5.0, 4.0, 4.4, bev=0.15)
    return b


def hot_cocoa_stand():
    b = Builder("HotCocoaStand", AREA)
    b.bx("WoodDark", -6, 6, -1.0, 3.5, 0, 4.0)
    b.bx("WoodLight", -6.4, 6.4, -1.6, 3.8, 4.0, 4.5)
    for k in range(10):
        x = -5.4 + k * 1.2
        b.bx("Plank", x - 0.5, x + 0.5, -1.15, -0.95, 0.3, 3.8, bev=0)
    b.bx("Red", -6, 6, -1.25, -1.1, 1.5, 2.5, bev=0)
    for x in (-5.6, 5.6):
        b.cylz("WoodDark", x, -0.6, 4.5, 9.6, 0.3, 6)
        b.cylz("WoodDark", x, 3.2, 0, 10.4, 0.3, 6)
    b.bx("WoodDark", -6, 6, 3.0, 3.5, 4.5, 10.4)
    with b.at(T(0, 1.3, 10.1), R(math.atan2(0.8, 4.6), 0, 0)):
        for k in range(9):
            x = -6.6 + (k + 0.5) * 13.2 / 9
            b.box("Red" if k % 2 else "White", (x, 0, 0), (13.2 / 9, 5.8, 0.3))
    b.bx("Snow", -6.8, 6.8, -1.6, 4.2, 10.7, 11.2, bev=0.2)
    # mugs on the counter
    for k, col in enumerate(("Red", "White", "Navy", "Red")):
        x = -4.0 + k * 2.4
        b.lathe(col, [(0, 0), (0.55, 0), (0.6, 1.0), (0.5, 1.0), (0.45, 0.2), (0, 0.2)], c=(x, 0.2, 4.5), n=10)
        b.cylz("Chocolate", x, 0.2, 4.6, 5.35, 0.47, 10)
        b.torus(col, (x + 0.65, 0.2, 5.0), 0.3, 0.09, 8, 4, rx=PI / 2)
        b.bx("White", x - 0.18, x + 0.18, 0.05, 0.4, 5.35, 5.6, bev=0)
    # big mug sign on the roof
    with b.at(T(0, 1.5, 11.2)):
        b.lathe("Red", [(0, 0), (1.9, 0), (2.1, 3.4), (1.8, 3.4), (1.7, 0.3), (0, 0.3)], n=14)
        b.cylz("Chocolate", 0, 0, 0.3, 3.1, 1.75, 14)
        b.torus("Red", (2.4, 0, 1.7), 0.9, 0.3, 10, 5, rx=PI / 2)
        for (x, y) in ((-0.6, 0.3), (0.5, -0.4), (0.2, 0.7)):
            b.bx("White", x - 0.4, x + 0.4, y - 0.4, y + 0.4, 3.0, 3.6, bev=0.1)
    b.bx("Navy", -3.5, 3.5, -1.7, -1.5, 8.0, 9.6)
    b.text("White", "HOT COCOA", (0, -1.75, 8.8), 0.8, depth=0.1, font="black")
    # patio heater + barrel table
    b.cylz("Metal", 8.5, -2.0, 0, 0.5, 1.2, 10)
    b.cylz("Metal", 8.5, -2.0, 0.5, 8.0, 0.2, 6)
    b.lathe("Metal", [(0, 8.0), (2.0, 8.4), (2.2, 8.7), (0, 8.7)], c=(8.5, -2.0, 0), n=10)
    b.cylz("Ember", 8.5, -2.0, 7.0, 8.0, 0.5, 8)
    b.lathe("WoodDark", [(0, 0), (1.3, 0), (1.5, 1.8), (1.3, 3.6), (0, 3.6)], c=(-9.0, -2.5, 0), n=10)
    b.bx("Snow", -11.0, -7.0, -4.5, -0.5, 3.6, 3.9, bev=0.1)
    return b


def ice_arch():
    b = Builder("IceArch", AREA)
    rng = b.rng
    ZC = 14.4
    for sx in (-1, 1):
        x = sx * 9.5
        for k in range(6):
            z = k * 2.4
            b.box("Ice" if k % 2 else "IceDeep", (x + rng.uniform(-0.15, 0.15), 0, z + 1.2), (4.6 - k * 0.12, 4.0, 2.3),
                  rz=rng.uniform(-0.04, 0.04), bev=0.3)
    n = 11
    for k in range(n):
        a = PI * (k + 0.5) / n
        x, z = math.cos(a) * 9.5, ZC + math.sin(a) * 9.5
        b.box("Ice" if k % 2 else "IceDeep", (x, 0, z), (2.9, 4.0, 2.6), ry=-a - PI / 2, bev=0.3)
        xs, zs = math.cos(a) * 11.0, ZC + math.sin(a) * 11.0
        b.box("Snow", (xs, 0, zs), (3.0, 4.3, 0.6), ry=-a - PI / 2, bev=0.2)
    b.ball("IceGlow", (0, -2.1, ZC + 9.5), 0.9, seg=(10, 8))
    # sign hung under the crown
    b.bx("WoodDark", -6.4, 6.4, -2.4, -2.0, 15.6, 18.4)
    b.text("White", "SNOWY PEAKS", (0, -2.45, 17.0), 1.45, depth=0.2, font="black")
    b.bx("Snow", -6.6, 6.6, -2.6, -1.8, 18.4, 18.9, bev=0.15)
    for x in (-5.4, 5.4):
        b.cyl("Rope", (x, -2.2, 18.9), (x * 0.9, -2.2, ZC + math.sqrt(8.2 ** 2 - (x * 0.9) ** 2)), 0.1, 4)
    icicles(b, (-6.2, -2.3), (6.2, -2.3), 15.6, maxlen=1.2)
    for k in range(9):
        a = PI * (k + 0.5) / 9
        b.cyl("Ice", (math.cos(a) * 8.2, -1.4, ZC + math.sin(a) * 8.2), (math.cos(a) * 8.2, -1.4, ZC + math.sin(a) * 8.2 - b.rng.uniform(0.8, 1.8)), 0.25, 5, r2=0.0)
    for sx in (-1, 1):
        b.lamp("Charcoal", "WindowGlow", (sx * 14.0, -2.0, 0), h=8.0)
        drift(b, (sx * 13.0, 1.5, 0.3), 2.2, sc=(1.4, 1.1, 0.5))
    return b


def ski_rack():
    b = Builder("SkiRack", AREA)
    for x in (-5, 5):
        b.bx("WoodDark", x - 0.3, x + 0.3, -0.3, 0.3, 0, 6.0)
        b.bx("WoodDark", x - 0.3, x + 0.3, -1.6, 1.6, 0, 0.4)
    b.bx("WoodDark", -5.4, 5.4, -0.35, 0.35, 5.6, 6.2)
    b.bx("WoodDark", -5.4, 5.4, -1.2, 1.2, 1.4, 1.7)
    b.bx("Snow", -5.6, 5.6, -0.5, 0.5, 6.2, 6.6, bev=0.15)
    cols = ("Red", "Navy", "Yellow", "SkyBlue", "Green", "Orange")
    for k, col in enumerate(cols):
        x = -4.2 + k * 1.6
        for dx in (-0.25, 0.25):
            b.box(col, (x + dx, -0.6, 3.6), (0.4, 0.14, 7.0), rx=0.12)
            b.box(col, (x + dx, -1.05, 7.15), (0.4, 0.14, 0.7), rx=0.9)
        b.bx("Black", x - 0.4, x + 0.4, -0.85, -0.55, 3.0, 3.4, bev=0)
    for k in range(4):
        x = -3 + k * 2
        b.cyl("Metal", (x, 0.6, 0), (x + 0.2, 0.9, 5.4), 0.06, 4)
        b.cylz("Black", x + 0.2, 0.9, 5.4, 5.8, 0.12, 4)
        b.torus("Black", (x + 0.02, 0.63, 0.6), 0.35, 0.05, 8, 3)
    # sled leaning on the side
    with b.at(T(7.6, 0, 0), R(0, -0.25, 0)):
        for y in (-1.0, 1.0):
            b.cyl("Red", (0, y, 0.2), (0, y, 5.6), 0.15, 5)
            b.torus("Red", (0, y, 5.6), 0.5, 0.15, 8, 4, rx=PI / 2, rz=PI / 2, a0=0, a1=PI)
        for k in range(5):
            b.bx("WoodLight", -0.55, -0.15, -1.3, 1.3, 0.8 + k * 0.95, 1.4 + k * 0.95)
    drift(b, (0, -2.2, 0.2), 2.0, sc=(2.2, 0.9, 0.4))
    return b


def ice_fish_sculpture():
    b = Builder("IceFishSculpture", AREA)
    b.bx("Snow", -5.5, 5.5, -5.5, 5.5, 0, 1.0, bev=0.3)
    b.bx("IceDeep", -4.2, 4.2, -4.2, 4.2, 1.0, 3.6)
    b.bx("IceGlow", -4.3, 4.3, -4.3, 4.3, 1.1, 1.4, bev=0)
    with b.at(T(0, 0, 3.6)):
        pts = [(-3.6, 0)] + [(-3.6 + 7.2 * k / 13, 1.0 + 1.4 * math.sin(PI * 2 * k / 13) * (1 - k / 13) + 2.8 * (k / 13) ** 2) for k in range(14)] + [(3.6, 0)]
        b.prism_y("Ice", pts, -2.0, 2.0)
    with b.at(T(0, 0, 10.0), R(0, -0.6, 0)):
        b.ball("Ice", (0, 0, 0), 1.0, seg=(14, 9), sc=(3.8, 1.5, 2.2))
        b.prism_y("Ice", [(-3.0, 0), (-5.8, 2.4), (-5.0, 0), (-5.8, -2.4)], -0.3, 0.3)
        b.prism_y("Ice", [(-1.2, 1.9), (1.4, 2.0), (-0.6, 3.4)], -0.25, 0.25)
        for sy in (-1, 1):
            b.ball("IceGlow", (2.6, sy * 1.0, 0.5), 0.4, seg=(8, 6))
    for k in range(6):
        a = TAU * k / 6
        b.cylz("IceGlow", math.cos(a) * 4.8, math.sin(a) * 4.8, 1.0, 1.6, 0.3, 6)
    return b


def ice_rink():
    b = Builder("IceRink", AREA)
    A, Bb = 18.0, 11.0
    b.lathe("Ice", [(0, 0), (1.0, 0), (1.0, 0.5), (0, 0.5)], n=32, sc=(A, Bb))
    # boards: posts + white kick-board + red top rail
    n = 36
    pts = [(math.cos(TAU * k / n) * (A + 0.6), math.sin(TAU * k / n) * (Bb + 0.6)) for k in range(n)]
    for k in range(n):
        if k in (26, 27):
            continue
        p0, p1 = pts[k], pts[(k + 1) % n]
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        rz = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        b.box("White", (mid[0], mid[1], 1.2), (L + 0.1, 0.4, 2.0), rz=rz)
        b.box("WoodRed", (mid[0], mid[1], 2.35), (L + 0.1, 0.55, 0.3), rz=rz, bev=0)
    for k in range(0, n, 3):
        b.cylz("WoodRed", pts[k][0], pts[k][1], 0, 2.6, 0.25, 6)
    # rink markings
    b.ring("Red", (0, 0, 0), 3.0, 2.6, 0.5, 0.53, n=24)
    b.bx("Red", -0.15, 0.15, -Bb + 0.5, Bb - 0.5, 0.5, 0.53, bev=0)
    for sx in (-1, 1):
        b.bx("SkyBlue", sx * 7 - 0.2, sx * 7 + 0.2, -Bb + 1.2, Bb - 1.2, 0.5, 0.53, bev=0)
    # lamps, a bench, snow banks
    for (x, y) in ((-A - 3, 0), (A + 3, 0), (0, Bb + 3)):
        b.lamp("Charcoal", "WindowGlow", (x, y, 0), h=9.0, arms=2)
    with b.at(T(-6, -Bb - 3.5, 0)):
        b.bx("WoodRed", -3, 3, -0.6, 0.6, 1.8, 2.2)
        b.bx("WoodRed", -3, 3, 0.4, 0.7, 2.2, 3.8)
        for x in (-2.6, 2.6):
            b.bx("Charcoal", x - 0.2, x + 0.2, -0.5, 0.6, 0, 1.8)
        b.bx("Snow", -3.1, 3.1, -0.65, 0.65, 2.2, 2.4, bev=0)
    for k in range(9):
        a = TAU * k / 9 + 0.3
        drift(b, (math.cos(a) * (A + 4.5), math.sin(a) * (Bb + 4.5), 0.2), 2.4, sc=(1.4, 1.1, 0.45))
    return b


def snowmobile():
    b = Builder("Snowmobile", AREA)
    # skis
    for sx in (-1.6, 1.6):
        b.bx("Charcoal", sx - 0.35, sx + 0.35, -6.0, -1.0, 0.0, 0.25)
        b.tube("Charcoal", [(sx, -6.0, 0.12), (sx, -6.8, 0.5), (sx, -7.0, 1.0)], 0.2, 5)
        b.cyl("DarkMetal", (sx, -3.5, 0.25), (sx * 0.7, -3.0, 1.8), 0.15, 5)
    # track unit
    b.bx("Rubber", -1.3, 1.3, -1.5, 5.5, 0.0, 1.8, bev=0.5)
    for k in range(9):
        y = -1.2 + k * 0.8
        b.bx("Charcoal", -1.35, 1.35, y - 0.12, y + 0.12, -0.05, 0.1, bev=0)
    # body
    b.mesh("Red", [(-1.8, -5.2, 1.4), (1.8, -5.2, 1.4), (1.9, 1.0, 1.4), (-1.9, 1.0, 1.4),
                   (-1.3, -4.0, 3.0), (1.3, -4.0, 3.0), (1.6, 0.5, 3.4), (-1.6, 0.5, 3.4)],
           [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
    b.bx("White", -1.95, 1.95, -3.0, 0.6, 1.9, 2.4, bev=0)
    b.mesh("GlassDark", [(-1.4, -0.4, 3.4), (1.4, -0.4, 3.4), (1.1, 0.6, 5.0), (-1.1, 0.6, 5.0)], [[0, 1, 2, 3], [3, 2, 1, 0]])
    b.bx("Black", -1.4, 1.4, 1.0, 5.6, 2.2, 3.0)
    b.bx("Charcoal", -1.5, 1.5, 1.0, 5.6, 3.0, 3.5)
    b.cyl("Charcoal", (-2.2, 0.8, 4.0), (2.2, 0.8, 4.0), 0.12, 5)
    b.bx("NeonWhite", -0.6, 0.6, -5.3, -5.15, 2.0, 2.5, bev=0)
    b.bx("NeonRed", -1.0, 1.0, 5.55, 5.7, 1.6, 2.0, bev=0)
    return b


ASSETS = [ice_castle, ski_lodge, ski_lift_station, ski_lift_tower, log_cabin, hot_cocoa_stand, ice_arch,
          ski_rack, ice_fish_sculpture, ice_rink, snowmobile]
