"""Area 5 -- Rich City: marble, gold trim, dark glass towers, cream stone."""
import math

from kit import PI, TAU, Builder, R, T, V, catenary

AREA = "RichCity"
GROUND = (176, 184, 200)


def window_grid(b, c, rz, w, z0, z1, nx, nz, ww, wh, glass="GlassDark", frame=None, sill=None, lit=0.0, depth=0.25):
    """A grid of windows on a wall face whose outside is local -Y (rz turns it)."""
    rng = b.rng
    with b.at(T(c), R(0, 0, rz)):
        for j in range(nz):
            z = z0 + (j + 0.5) * (z1 - z0) / nz
            for i in range(nx):
                x = -w / 2 + (i + 0.5) * w / nx
                st = "WindowGlow" if rng.random() < lit else glass
                b.box(st, (x, -depth / 2, z), (ww, depth, wh))
                if frame:
                    b.box(frame, (x, -depth - 0.1, z + wh / 2 + 0.2), (ww + 0.6, 0.35, 0.4))
                if sill:
                    b.box(sill, (x, -depth - 0.15, z - wh / 2 - 0.2), (ww + 0.5, 0.5, 0.3))


def column(b, x, y, z0, h, r=0.9, shaft="Marble", trim="Marble", fluted=True):
    b.bx(trim, x - r * 1.35, x + r * 1.35, y - r * 1.35, y + r * 1.35, z0, z0 + 0.6)
    b.cylz(trim, x, y, z0 + 0.6, z0 + 1.1, r * 1.2, 12)
    b.cylz(shaft, x, y, z0 + 1.1, z0 + h - 1.1, r, 12, r2=r * 0.9)
    if fluted:
        for k in range(8):
            a = TAU * k / 8
            b.cylz(trim, x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92, z0 + 1.6, z0 + h - 1.6, 0.12, 4)
    b.cylz(trim, x, y, z0 + h - 1.1, z0 + h - 0.6, r * 0.9, 12, r2=r * 1.25)
    b.bx(trim, x - r * 1.4, x + r * 1.4, y - r * 1.4, y + r * 1.4, z0 + h - 0.6, z0 + h)


def balustrade(b, p0, p1, z, h=2.4, st="White"):
    p0, p1 = V((p0[0], p0[1], z)), V((p1[0], p1[1], z))
    d = p1 - p0
    L = d.length
    rz = math.atan2(d.y, d.x)
    mid = (p0 + p1) / 2
    b.box(st, (mid.x, mid.y, z + 0.25), (L, 1.0, 0.5), rz=rz)
    b.box(st, (mid.x, mid.y, z + h - 0.25), (L + 0.4, 1.1, 0.5), rz=rz)
    n = max(2, int(L / 0.9))
    for i in range(n):
        p = p0 + d * ((i + 0.5) / n)
        b.lathe(st, [(0, 0.5), (0.3, 0.5), (0.45, 0.9), (0.22, 1.4), (0.3, h - 0.6), (0.2, h - 0.5), (0, h - 0.5)], c=(p.x, p.y, z), n=6)


def mansion():
    b = Builder("Mansion", AREA)
    # terrace + grand stair
    b.bx("Marble", -36, 36, -16, 24, 0, 2.0)
    b.bx("MarbleDark", -36.3, 36.3, -16.3, 24.3, 1.1, 1.6, bev=0)
    for i in range(5):
        y = -16 - 1.0 * (5 - i)
        b.bx("Marble", -10 - (5 - i) * 0.5, 10 + (5 - i) * 0.5, y, -16, 0, 0.4 * (i + 1))
    b.bx("Red", -3.2, 3.2, -21.2, -10.0, 2.02, 2.08, bev=0)
    for i in range(5):
        b.bx("Red", -3.2, 3.2, -16 - 1.0 * (5 - i) + 0.02, -16 - 1.0 * (4 - i), 0.4 * (i + 1) + 0.01, 0.4 * (i + 1) + 0.06, bev=0)
    # central block
    X0, X1, Y0, Y1 = -14, 14, -6, 18
    Z0, Z1 = 2.0, 24.0
    b.bx("Cream", X0, X1, Y0, Y1, Z0, Z1)
    for x in (X0, X1):
        for k in range(10):
            z = Z0 + k * 2.2
            ext = 1.4 if k % 2 else 0.9
            b.bx("White", x - ext / 2 - 0.3, x + ext / 2 + 0.3, Y0 - 0.4, Y0 + 1.2, z, z + 2.0)
    for z in (Z0 + 10.4, Z1 - 1.4):
        b.bx("White", X0 - 0.4, X1 + 0.4, Y0 - 0.6, Y1 + 0.4, z, z + 1.0)
    b.bx("White", X0 - 1.0, X1 + 1.0, Y0 - 1.2, Y1 + 1.0, Z1, Z1 + 1.2)
    balustrade(b, (X0, Y0 - 0.6), (X1, Y0 - 0.6), Z1 + 1.2)
    balustrade(b, (X0 - 0.4, Y0), (X0 - 0.4, Y1), Z1 + 1.2)
    balustrade(b, (X1 + 0.4, Y0), (X1 + 0.4, Y1), Z1 + 1.2)
    for x in (-10, -5.5, 5.5, 10):
        for z, h in ((Z0 + 4.8, 6.4), (Z0 + 15.6, 5.4)):
            b.window("GlassDark", "White", (x, Y0 - 0.25, z), 2.6, h, cross=True, sill="White", lintel="Gold" if z < 12 else "White",
                     arch=z < 12)
    # portico: six columns, entablature, pediment with a gold crest
    for x in (-9.6, -5.8, -1.9, 1.9, 5.8, 9.6):
        column(b, x, -10.0, 2.0, 18.0, r=0.95)
    b.bx("Marble", -11.6, 11.6, -12.0, Y0, 20.0, 22.4)
    b.bx("Gold", -11.6, 11.6, -12.15, -11.9, 20.6, 21.0, bev=0)
    b.prism_y("Marble", [(-12.2, 22.4), (12.2, 22.4), (0, 28.0)], -12.4, Y0)
    b.prism_y("Cream", [(-10.4, 22.9), (10.4, 22.9), (0, 27.1)], -12.6, -12.3)
    b.cyl("Gold", (0, -12.4, 24.8), (0, -12.8, 24.8), 1.6, 16)
    b.cyl("White", (0, -12.7, 24.8), (0, -12.9, 24.8), 1.1, 16)
    b.text("Gold", "R", (0, -13.0, 24.8), 1.5, depth=0.2, font="serif")
    b.bx("Marble", -12.6, 12.6, -12.6, -11.8, 22.2, 22.6, bev=0)
    # door
    b.door("WoodDark", "Gold", (0, Y0 - 0.2, Z0), 4.6, 9.0, arch=True)
    b.box("Glass", (0, Y0 - 0.5, Z0 + 11.4), (3.4, 0.2, 1.6))
    # dome on a windowed drum
    DC = (0, 6, Z1 + 1.2)
    b.lathe("Cream", [(0, 0), (8.0, 0), (8.0, 7.0), (0, 7.0)], c=DC, n=20)
    for k in range(10):
        a = TAU * k / 10
        x, y = DC[0] + math.cos(a) * 8.0, DC[1] + math.sin(a) * 8.0
        b.cylz("White", x, y, DC[2], DC[2] + 7.0, 0.55, 8)
        a2 = a + TAU / 20
        b.window("GlassDark", "White", (DC[0] + math.cos(a2) * 8.05, DC[1] + math.sin(a2) * 8.05, DC[2] + 3.6), 1.5, 3.6,
                 rz=a2 + PI / 2, arch=True, cross=False, ft=0.25)
    b.ring("White", DC, 8.8, 7.6, 7.0, 8.0, n=20)
    b.dome("Gold", (DC[0], DC[1], DC[2] + 8.0), 8.2, seg=20, rings=6, sc=(1, 1, 1.05))
    for k in range(10):
        a = TAU * k / 10
        pts = [(DC[0] + math.cos(a) * 8.25 * math.cos(t), DC[1] + math.sin(a) * 8.25 * math.cos(t), DC[2] + 8.0 + 8.6 * math.sin(t))
               for t in [i * PI / 2 / 8 for i in range(8)]]
        b.tube("Brass", pts, 0.22, 5)
    b.lathe("White", [(0, 0), (1.6, 0), (1.6, 3.0), (0, 3.0)], c=(DC[0], DC[1], DC[2] + 16.4), n=10)
    b.dome("Gold", (DC[0], DC[1], DC[2] + 19.4), 1.9, seg=10, rings=4)
    b.cylz("Gold", DC[0], DC[1], DC[2] + 21.2, DC[2] + 24.0, 0.15, 6)
    b.ball("Gold", (DC[0], DC[1], DC[2] + 24.2), 0.45, seg=(8, 6))
    # wings
    for sx in (-1, 1):
        wx0, wx1 = (sx * 14, sx * 34) if sx > 0 else (sx * 34, sx * 14)
        WZ1 = 16.0
        b.bx("Cream", wx0, wx1, -2, 18, Z0, WZ1)
        for z in (Z0 + 7.4, WZ1 - 1.2):
            b.bx("White", wx0 - 0.3, wx1 + 0.3, -2.5, 18.3, z, z + 0.9)
        xo = sx * 34
        for k in range(7):
            z = Z0 + k * 2.0
            b.bx("White", xo - 0.9, xo + 0.9, -2.6, -1.2 + (k % 2), z, z + 1.8)
        for x in [sx * 18, sx * 23, sx * 28]:
            b.window("GlassDark", "White", (x, -2.25, Z0 + 3.8), 2.6, 5.2, sill="White", lintel="White", shutters=None)
            b.window("GlassDark", "White", (x, -2.25, Z0 + 10.6), 2.4, 4.4, sill="White")
        b.hip_roof("MarbleDark", (wx0 + wx1) / 2, 8, WZ1, abs(wx1 - wx0), 20, 6.0, over=1.0, base=0.8)
        for y in (2.0, 13.0):
            b.bx("Cream", sx * 30 - 1.0, sx * 30 + 1.0, y - 1.0, y + 1.0, WZ1 + 1.0, WZ1 + 8.5)
            b.bx("White", sx * 30 - 1.3, sx * 30 + 1.3, y - 1.3, y + 1.3, WZ1 + 8.5, WZ1 + 9.1)
        # hedge planters + urns along the terrace
        for x in [sx * 18, sx * 23, sx * 28]:
            b.bx("Marble", x - 1.8, x + 1.8, -9.5, -6.0, 2.0, 3.2)
            b.rock("Hedge", (x, -7.75, 4.0), 1.5, sc=(1.3, 1.1, 0.8), jitter=0.12)
        b.lathe("Marble", [(0, 0), (1.2, 0), (0.6, 0.6), (0.6, 1.0), (1.5, 2.2), (1.7, 3.2), (0, 3.2)], c=(sx * 13.5, -14.5, 2.0), n=10)
        b.ball("Hedge", (sx * 13.5, -14.5, 6.2), 1.7, seg=(10, 8))
        b.lamp("Charcoal", "WindowGlow", (sx * 11.5, -20.0, 0), h=9.0, arms=2)
    return b


def glass_tower():
    b = Builder("GlassTower", AREA)
    # podium
    b.bx("MarbleDark", -16, 16, -16, 16, 0, 9.0)
    b.bx("Marble", -16.5, 16.5, -16.5, 16.5, 9.0, 10.0)
    for rz in (0, PI / 2, PI, -PI / 2):
        with b.at(R(0, 0, rz)):
            b.bx("GlassDark", -13, 13, -16.15, -15.8, 1.0, 8.0)
            for k in range(7):
                x = -13 + k * 26 / 6
                b.bx("Metal", x - 0.2, x + 0.2, -16.35, -15.8, 1.0, 8.0, bev=0)
    b.bx("Glass", -4, 4, -16.4, -15.9, 0, 6.5)
    b.bx("Metal", -6, 6, -23.3, -15.8, 7.0, 7.5)
    b.bx("Gold", -6, 6, -23.4, -23.1, 7.0, 7.6, bev=0)
    for x in (-5.4, 5.4):
        b.cylz("Metal", x, -22.6, 0, 7.0, 0.18, 6)
    b.text("Gold", "SKY ONE", (0, -23.5, 8.7), 1.2, depth=0.2)
    # shaft
    def shaft(hw, z0, z1, bands=4.0):
        b.bx("GlassDark", -hw, hw, -hw, hw, z0, z1)
        for rz in (0, PI / 2, PI, -PI / 2):
            with b.at(R(0, 0, rz)):
                n = int(2 * hw / 3.0)
                for i in range(n + 1):
                    x = -hw + i * 2 * hw / n
                    b.bx("Metal", x - 0.16, x + 0.16, -hw - 0.3, -hw, z0, z1, bev=0)
                k = 0
                z = z0 + bands
                while z < z1 - 0.5:
                    b.bx("Metal", -hw, hw, -hw - 0.25, -hw, z - 0.2, z + 0.2, bev=0)
                    z += bands
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.bx("Metal", sx * hw - 0.5, sx * hw + 0.5, sy * hw - 0.5, sy * hw + 0.5, z0, z1)
    shaft(12, 10, 68)
    b.bx("Metal", -12.6, 12.6, -12.6, 12.6, 68, 69.2)
    shaft(9, 69.2, 82)
    b.bx("Metal", -9.6, 9.6, -9.6, 9.6, 82, 83.0)
    shaft(6, 83.0, 90)
    for hw, z in ((12.6, 69.2), (9.6, 83.0)):
        for rz in (0, PI / 2, PI, -PI / 2):
            with b.at(R(0, 0, rz)):
                b.bx("NeonCyan", -hw, hw, -hw - 0.1, -hw + 0.2, z - 0.25, z - 0.05, bev=0)
    # crown + spire + helipad on the setback
    b.bx("Metal", -6.4, 6.4, -6.4, 6.4, 90, 91.0)
    b.cylz("Metal", 0, 0, 91, 96, 1.0, 8, r2=0.4)
    b.cylz("Metal", 0, 0, 96, 104, 0.25, 6, r2=0.08)
    b.ball("NeonRed", (0, 0, 104.2), 0.4, seg=(6, 4))
    b.cylz("Charcoal", 0, -7.0, 69.2, 69.5, 4.6, 16)
    b.ring("White", (0, -7.0, 0), 4.2, 3.7, 69.5, 69.6, n=16)
    b.text("White", "H", (0, -7.0, 69.6), 3.0, depth=0.08, upright=False)
    b.bx("DarkMetal", 5.0, 8.0, 3.0, 7.0, 69.2, 71.6)
    return b


def art_deco_tower():
    b = Builder("ArtDecoTower", AREA)
    tiers = ((17, 0, 24), (13, 24, 50), (9.5, 50, 68), (6, 68, 78))
    for k, (hw, z0, z1) in enumerate(tiers):
        b.bx("Cream", -hw, hw, -hw, hw, z0, z1)
        for rz in (0, PI / 2, PI, -PI / 2):
            with b.at(R(0, 0, rz)):
                n = int(2 * hw / 2.4)
                for i in range(n):
                    x = -hw + (i + 0.5) * 2 * hw / n
                    if i % 2 == 0:
                        b.bx("Cream", x - 0.45, x + 0.45, -hw - 0.5, -hw, z0 + (3 if k == 0 else 0.5), z1 - 0.6)
                    else:
                        b.bx("GlassDark", x - 0.7, x + 0.7, -hw - 0.15, -hw + 0.1, z0 + (5 if k == 0 else 1.0), z1 - 1.0, bev=0)
                        zz = z0 + (5 if k == 0 else 1.0) + 3.0
                        while zz < z1 - 1.5:
                            b.bx("Brass", x - 0.75, x + 0.75, -hw - 0.25, -hw, zz - 0.18, zz + 0.18, bev=0)
                            zz += 3.0
                b.bx("Gold", -hw - 0.4, hw + 0.4, -hw - 0.55, -hw, z1 - 0.8, z1 - 0.2, bev=0)
        b.bx("Cream", -hw - 0.6, hw + 0.6, -hw - 0.6, hw + 0.6, z1 - 0.2, z1 + 0.6)
        # corner fins
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.bx("Cream", sx * hw - 0.9, sx * hw + 0.9, sy * hw - 0.9, sy * hw + 0.9, z0, z1 + 2.0)
                b.prism_x("Gold", [(sy * hw - 0.9, z1 + 2.0), (sy * hw + 0.9, z1 + 2.0), (sy * hw, z1 + 3.6)], sx * hw - 0.9, sx * hw + 0.9)
    # sunburst crown
    for rz in (0, PI / 2, PI, -PI / 2):
        with b.at(R(0, 0, rz)):
            for k in range(7):
                a = PI * (k + 0.5) / 7
                b.box("Gold", (math.cos(a) * 2.8, -6.3, 78.6 + math.sin(a) * 2.8), (0.45, 0.3, 4.2), ry=-(a - PI / 2))
            b.bx("NeonYellow", -2.0, 2.0, -6.4, -6.2, 78.8, 79.2, bev=0)
    b.lathe("Gold", [(0, 0), (3.6, 0), (2.4, 4.0), (1.0, 9.0), (0.2, 16.0), (0, 16.0)], c=(0, 0, 78.6), n=8)
    for k in range(5):
        b.ring("Brass", (0, 0, 0), 2.9 - k * 0.42, 2.5 - k * 0.42, 80.0 + k * 2.0, 80.4 + k * 2.0, n=8)
    # lobby entrance
    b.bx("MarbleDark", -8, 8, -17.4, -16.9, 0, 9.0)
    b.bx("Glass", -3, 3, -17.6, -17.2, 0, 6.0)
    b.prism_y("Gold", [(-6, 6.4), (6, 6.4), (0, 9.6)], -17.8, -17.3)
    b.prism_y("GlassDark", [(-4.6, 6.6), (4.6, 6.6), (0, 9.0)], -17.95, -17.75)
    b.cylz("Glass", 0, -18.6, 0, 6.0, 2.0, 12)
    b.cylz("Brass", 0, -18.6, 6.0, 6.4, 2.2, 12)
    b.cylz("Brass", 0, -18.6, 0, 6.0, 0.15, 6)
    for k in range(4):
        a = TAU * k / 4 + 0.4
        b.box("Brass", (math.cos(a) * 1.0, -18.6 + math.sin(a) * 1.0, 3.0), (2.0, 0.12, 5.8), rz=a, bev=0)
    for x in (-6.5, 6.5):
        b.lamp("Brass", "WindowGlow", (x, -19.0, 0), h=6.0)
    return b


def bank():
    b = Builder("Bank", AREA)
    W, D = 40.0, 28.0
    for i in range(4):
        e = (3 - i) * 1.0
        b.bx("Marble", -W / 2 - e, W / 2 + e, -D / 2 - e, D / 2, i * 0.6, (i + 1) * 0.6)
    Z0 = 2.4
    b.bx("Cream", -W / 2 + 2, W / 2 - 2, -D / 2 + 6, D / 2 - 1, Z0, Z0 + 18)
    for x in (-W / 2 + 2, W / 2 - 2):
        for k in range(8):
            b.bx("Marble", x - 0.8, x + 0.8, -D / 2 + 5.6, -D / 2 + 6.8 + (k % 2) * 0.6, Z0 + k * 2.25, Z0 + k * 2.25 + 2.0)
    # columns across the front
    cols = [-15.5, -9.3, -3.1, 3.1, 9.3, 15.5]
    for x in cols:
        column(b, x, -D / 2 + 1.5, Z0, 17.0, r=1.1)
    b.bx("Marble", -W / 2, W / 2, -D / 2, D / 2 - 1, Z0 + 17, Z0 + 21)
    b.bx("Marble", -W / 2 - 0.4, W / 2 + 0.4, -D / 2 - 0.4, D / 2 - 0.6, Z0 + 21, Z0 + 21.8)
    b.bx("Gold", -W / 2 + 0.5, W / 2 - 0.5, -D / 2 - 0.15, -D / 2 + 0.1, Z0 + 17.4, Z0 + 17.8, bev=0)
    b.text("Gold", "BANK", (0, -D / 2 - 0.2, Z0 + 19.3), 2.6, depth=0.3, font="serif", spacing=1.4)
    for k in range(12):
        x = -W / 2 + 1.5 + k * (W - 3) / 11
        b.bx("Marble", x - 0.6, x + 0.6, -D / 2 - 0.3, -D / 2, Z0 + 20.6, Z0 + 21.0)
    b.prism_y("Marble", [(-W / 2 - 0.4, Z0 + 21.8), (W / 2 + 0.4, Z0 + 21.8), (0, Z0 + 28.5)], -D / 2 - 0.4, D / 2 - 0.6)
    b.prism_y("Cream", [(-W / 2 + 2.6, Z0 + 22.4), (W / 2 - 2.6, Z0 + 22.4), (0, Z0 + 27.4)], -D / 2 - 0.6, -D / 2 - 0.3)
    b.cyl("Gold", (0, -D / 2 - 0.5, Z0 + 24.4), (0, -D / 2 - 1.1, Z0 + 24.4), 2.0, 20)
    b.text("Cream", "$", (0, -D / 2 - 1.15, Z0 + 24.4), 2.6, depth=0.2, font="serif")
    b.torus("Gold", (0, -D / 2 - 0.8, Z0 + 24.4), 2.0, 0.18, 20, 4, rx=PI / 2)
    # big bronze doors + tall windows
    b.door("Brass", "Marble", (0, -D / 2 + 5.8, Z0), 5.4, 11.0, ft=0.8)
    for x in (-11, 11):
        b.window("GlassDark", "Marble", (x, -D / 2 + 5.75, Z0 + 8.0), 3.4, 8.0, sill="Marble", lintel="Marble")
    for y in (-2, 6):
        for sx in (-1, 1):
            b.window("GlassDark", "Marble", (sx * (W / 2 - 1.75), y, Z0 + 8.0), 3.0, 8.0, rz=sx * PI / 2, sill="Marble")
    # gold bars on the step, lamps, flag
    for i, (x, y) in enumerate(((-6.5, -16.6), (6.0, -16.4))):
        for r, cnt in ((0, 3), (1, 2), (2, 1)):
            for j in range(cnt):
                xx = x - (cnt - 1) * 0.65 + j * 1.3
                b.mesh("Gold", [(xx - 0.6, y - 1.0, 2.4 + r * 0.6), (xx + 0.6, y - 1.0, 2.4 + r * 0.6), (xx + 0.6, y + 1.0, 2.4 + r * 0.6),
                                (xx - 0.6, y + 1.0, 2.4 + r * 0.6), (xx - 0.45, y - 0.8, 3.0 + r * 0.6), (xx + 0.45, y - 0.8, 3.0 + r * 0.6),
                                (xx + 0.45, y + 0.8, 3.0 + r * 0.6), (xx - 0.45, y + 0.8, 3.0 + r * 0.6)],
                       [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
    for x in (-W / 2 - 1.5, W / 2 + 1.5):
        b.lamp("Charcoal", "WindowGlow", (x, -D / 2 - 2.5, 0), h=8.0, arms=2)
    b.cylz("White", W / 2 - 3, D / 2 - 6, Z0 + 21.8, Z0 + 32, 0.15, 6)
    b.prism_y("Green", [(W / 2 - 2.9, Z0 + 31.8), (W / 2 + 1.5, Z0 + 31.8), (W / 2 + 1.5, Z0 + 29.2), (W / 2 - 2.9, Z0 + 29.2)], D / 2 - 6.05, D / 2 - 5.95)
    return b


def gold_fountain():
    b = Builder("GoldFountain", AREA)
    b.lathe("Marble", [(0, 0), (12.0, 0), (12.0, 1.8), (11.0, 1.8), (11.0, 0.6), (0, 0.6)], n=24)
    b.lathe("Marble", [(11.0, 1.8), (12.4, 1.8), (12.4, 2.3), (11.0, 2.3)], n=24, cap=False)
    b.lathe("Water", [(0, 0.6), (11.0, 0.6), (11.0, 1.5), (0, 1.5)], n=24)
    b.lathe("Marble", [(0, 0), (2.4, 0), (1.6, 2.0), (1.4, 5.0), (0, 5.0)], n=12)
    b.lathe("Gold", [(0, 5.0), (1.4, 5.0), (5.8, 6.2), (6.2, 7.2), (5.6, 7.2), (1.2, 6.2), (0, 6.2)], n=20)
    b.lathe("Water", [(0, 6.4), (5.6, 6.4), (5.6, 7.0), (0, 7.0)], n=20)
    b.lathe("Marble", [(0, 7.0), (1.0, 7.0), (0.8, 10.0), (0, 10.0)], n=10)
    b.lathe("Gold", [(0, 10.0), (0.8, 10.0), (3.0, 10.8), (3.2, 11.6), (2.8, 11.6), (0.6, 10.8), (0, 10.8)], n=16)
    b.lathe("Water", [(0, 10.9), (2.8, 10.9), (2.8, 11.4), (0, 11.4)], n=16)
    # finial: a gold pinecone
    b.ball("Gold", (0, 0, 13.0), 1.1, seg=(10, 8), sc=(1, 1, 1.5))
    for k in range(3):
        b.torus("Brass", (0, 0, 12.2 + k * 0.7), 1.0 - k * 0.2, 0.14, 10, 4)
    b.cylz("Gold", 0, 0, 14.4, 15.4, 0.25, 6, r2=0.0)
    # falling water sheets + jets
    for k in range(10):
        a = TAU * k / 10
        r0, r1 = 6.0, 7.6
        b.cyl("Water", (math.cos(a) * r0, math.sin(a) * r0, 6.8), (math.cos(a) * r1, math.sin(a) * r1, 1.5), 0.35, 6)
    for k in range(8):
        a = TAU * k / 8 + 0.2
        b.cyl("Water", (math.cos(a) * 3.0, math.sin(a) * 3.0, 11.2), (math.cos(a) * 4.6, math.sin(a) * 4.6, 7.0), 0.22, 6)
    for k in range(8):
        a = TAU * k / 8
        pts = [(math.cos(a) * (10.6 - 4.5 * t), math.sin(a) * (10.6 - 4.5 * t), 2.0 + 5.0 * math.sin(PI * t) - t * 0.6) for t in [i / 10 for i in range(11)]]
        b.tube("Water", pts, 0.16, 5)
        b.ball("Gold", (math.cos(a) * 10.9, math.sin(a) * 10.9, 2.6), 0.6, seg=(8, 6), sc=(1, 1, 0.8))
    for k in range(6):
        a = TAU * k / 6 + 0.5
        b.ball("Gold", (math.cos(a) * 7.0, math.sin(a) * 7.0, 1.6), 0.45, seg=(6, 4), sc=(1, 1, 0.3))
    return b


def hotel():
    b = Builder("Hotel", AREA)
    W, D, H = 36.0, 22.0, 58.0
    b.bx("MarbleDark", -W / 2 - 0.5, W / 2 + 0.5, -D / 2 - 0.5, D / 2 + 0.5, 0, 7.5)
    b.bx("Peach", -W / 2, W / 2, -D / 2, D / 2, 7.5, H)
    b.bx("GlassDark", -W / 2 + 2, W / 2 - 2, -D / 2 - 0.7, -D / 2 - 0.4, 0.5, 6.8)
    for k in range(9):
        x = -W / 2 + 2 + k * (W - 4) / 8
        b.bx("Gold", x - 0.18, x + 0.18, -D / 2 - 0.9, -D / 2 - 0.4, 0.5, 6.8, bev=0)
    # floors of windows with balconies on the front
    floors = 12
    fh = (H - 10.0) / floors
    for f in range(floors):
        z = 8.5 + f * fh
        for i in range(8):
            x = -W / 2 + 2.5 + i * (W - 5) / 7
            st = "WindowGlow" if b.rng.random() < 0.18 else "GlassDark"
            b.bx(st, x - 1.3, x + 1.3, -D / 2 - 0.15, -D / 2 + 0.1, z + 0.6, z + fh - 0.6)
            b.bx("White", x - 1.6, x + 1.6, -D / 2 - 0.35, -D / 2, z + fh - 0.6, z + fh - 0.2)
        if f % 2 == 1:
            for i in range(4):
                x = -W / 2 + 2.5 + (2 * i + 0.5) * (W - 5) / 7
                b.bx("White", x - 3.0, x + 3.0, -D / 2 - 2.2, -D / 2, z, z + 0.4)
                b.rail("White", "Glass", (x - 3.0, -D / 2 - 2.1), (x + 3.0, -D / 2 - 2.1), z + 0.4, h=1.8, spacing=3.0, pr=0.15)
        for side in (-1, 1):
            for j in range(5):
                y = -D / 2 + 2.5 + j * (D - 5) / 4
                b.bx("GlassDark", side * W / 2 - 0.15 if side < 0 else side * W / 2 - 0.1, side * W / 2 + 0.15 if side > 0 else side * W / 2 + 0.1,
                     y - 1.2, y + 1.2, z + 0.6, z + fh - 0.6)
    for z in (7.5, H - 0.8):
        b.bx("White", -W / 2 - 0.6, W / 2 + 0.6, -D / 2 - 0.6, D / 2 + 0.6, z, z + 1.0)
    for sx in (-1, 1):
        b.bx("White", sx * W / 2 - 1.0, sx * W / 2 + 0.2 if sx < 0 else sx * W / 2 + 1.0, -D / 2 - 0.4, D / 2 + 0.4, 7.5, H)
    # vertical neon sign
    with b.at(T(W / 2 - 3.5, -D / 2 - 1.6, 20.0)):
        b.bx("Navy", -1.6, 1.6, -0.6, 0.6, 0, 22.0)
        for k, ch in enumerate("HOTEL"):
            b.text("NeonPink", ch, (0, -0.65, 19.2 - k * 4.2), 3.0, depth=0.2, font="black")
        b.bx("Gold", -1.8, 1.8, -0.7, 0.7, -0.4, 0.0)
        b.bx("Gold", -1.8, 1.8, -0.7, 0.7, 22.0, 22.4)
    # entrance canopy on brass poles with a red carpet
    b.bx("Red", -6.0, 6.0, -D / 2 - 9.0, -D / 2 - 0.5, 6.4, 7.1)
    b.bx("Gold", -6.2, 6.2, -D / 2 - 9.2, -D / 2 - 8.8, 6.3, 7.2, bev=0)
    for x in (-5.6, 5.6):
        b.cylz("Brass", x, -D / 2 - 8.6, 0, 6.4, 0.2, 6)
    b.bx("Red", -2.4, 2.4, -D / 2 - 12.0, -D / 2 - 0.5, 0.0, 0.1, bev=0)
    b.text("Gold", "GRAND", (0, -D / 2 - 9.3, 6.75), 0.6, depth=0.1, font="serif")
    # rooftop: pool, umbrellas, sky bar
    RZ = H + 0.2
    b.bx("White", -W / 2 + 2, W / 2 - 2, -D / 2 + 2, D / 2 - 2, RZ, RZ + 0.6)
    b.bx("Water", -10, 6, -6, 2, RZ + 0.3, RZ + 0.75)
    b.bx("SkyBlue", -10.4, 6.4, -6.4, 2.4, RZ + 0.2, RZ + 0.5, bev=0)
    for x in (-8, -2, 4):
        b.cylz("White", x, 5.5, RZ + 0.6, RZ + 5.0, 0.12, 5)
        b.striped_canopy("Coral", "White", (x, 5.5), 2.4, 1.0, n=8, z=RZ + 4.8, scallop=False)
    b.bx("GlassDark", 9, 15, -6, 6, RZ, RZ + 4.0)
    b.bx("White", 8.6, 15.4, -6.4, 6.4, RZ + 4.0, RZ + 4.6)
    b.rail_loop("White", "Glass", [(-W / 2 + 1, -D / 2 + 1), (W / 2 - 1, -D / 2 + 1), (W / 2 - 1, D / 2 - 1), (-W / 2 + 1, D / 2 - 1)],
                RZ, h=2.2, spacing=4.0, pr=0.15)
    return b


def limo():
    b = Builder("Limo", AREA)
    L = 26.0
    # body: lofted from cross-sections along y
    def sec(y, top, w, nose=0.0):
        hw = w / 2
        return [(-hw, y, 1.0), (hw, y, 1.0), (hw, y, top - 0.6), (hw - 0.4, y, top), (-hw + 0.4, y, top), (-hw, y, top - 0.6)]
    ys = [-L / 2, -L / 2 + 0.8, -L / 2 + 3.5, L / 2 - 3.0, L / 2 - 0.8, L / 2]
    tops = [2.4, 3.0, 3.3, 3.3, 3.1, 2.6]
    ws = [6.2, 7.0, 7.2, 7.2, 7.0, 6.4]
    b.loft("Black", [sec(y, t, w) for y, t, w in zip(ys, tops, ws)])
    # cabin
    cy0, cy1 = -L / 2 + 6.5, L / 2 - 5.0
    b.mesh("Black", [(-3.2, cy0, 3.3), (3.2, cy0, 3.3), (3.2, cy1, 3.3), (-3.2, cy1, 3.3),
                     (-2.8, cy0 + 2.0, 5.6), (2.8, cy0 + 2.0, 5.6), (2.8, cy1 - 1.4, 5.6), (-2.8, cy1 - 1.4, 5.6)],
           [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
    for sx in (-1, 1):
        b.mesh("GlassDark", [(sx * 3.22, cy0 + 0.6, 3.6), (sx * 3.22, cy1 - 0.4, 3.6), (sx * 2.87, cy1 - 1.5, 5.3), (sx * 2.87, cy0 + 2.1, 5.3)],
               [[0, 1, 2, 3], [3, 2, 1, 0]])
        for y in (cy0 + 5.0, cy0 + 9.0, cy0 + 13.0):
            b.bx("Black", sx * 3.25 - 0.1, sx * 3.25 + 0.1, y - 0.3, y + 0.3, 3.5, 5.4, bev=0)
        b.bx("Metal", sx * 3.62 - 0.08, sx * 3.62 + 0.08, -L / 2 + 1, L / 2 - 1, 2.1, 2.35, bev=0)
    b.mesh("GlassDark", [(-2.9, cy0 + 0.1, 3.45), (2.9, cy0 + 0.1, 3.45), (2.7, cy0 + 1.9, 5.45), (-2.7, cy0 + 1.9, 5.45)],
           [[0, 1, 2, 3], [3, 2, 1, 0]])
    # wheels (3 axles for a stretch)
    for y in (-L / 2 + 3.6, L / 2 - 6.5, L / 2 - 3.4):
        for sx in (-1, 1):
            b.cyl("Rubber", (sx * 3.0, y, 1.35), (sx * 3.7, y, 1.35), 1.35, 14)
            b.cyl("Metal", (sx * 3.7, y, 1.35), (sx * 3.8, y, 1.35), 0.8, 10)
    # grille, lights, ornament
    b.bx("Metal", -2.2, 2.2, -L / 2 - 0.15, -L / 2 + 0.1, 1.4, 2.2)
    for k in range(6):
        b.bx("Black", -1.9 + k * 0.76, -1.7 + k * 0.76, -L / 2 - 0.2, -L / 2, 1.5, 2.1, bev=0)
    for sx in (-1, 1):
        b.bx("NeonWhite", sx * 2.7 - 0.5, sx * 2.7 + 0.5, -L / 2 - 0.1, -L / 2 + 0.2, 1.7, 2.2, bev=0)
        b.bx("NeonRed", sx * 2.8 - 0.5, sx * 2.8 + 0.5, L / 2 - 0.2, L / 2 + 0.1, 2.0, 2.5, bev=0)
    b.bx("Metal", -3.2, 3.2, -L / 2 - 0.4, -L / 2 + 0.3, 0.8, 1.2)
    b.bx("Metal", -3.2, 3.2, L / 2 - 0.3, L / 2 + 0.4, 0.8, 1.2)
    b.ball("Gold", (0, -L / 2 + 0.6, 3.0), 0.25, seg=(6, 4))
    return b


def boutique_row():
    b = Builder("BoutiqueRow", AREA)
    shops = (("Navy", "Cream", "COUTURE", "Gold"), ("Mint", "White", "JEWELS", "Gold"), ("Plum", "Cream", "SHOES", "Gold"))
    W = 14.0
    for i, (col, trim, name, gold) in enumerate(shops):
        cx = (i - 1) * (W + 0.4)
        with b.at(T(cx, 0, 0)):
            H = 18.0 + (i % 2) * 2.0
            b.bx("Cream", -W / 2, W / 2, -5, 6, 0, H)
            b.bx(col, -W / 2, W / 2, -5.3, -4.9, 0, 8.5)
            b.bx("Glass", -5.4, 2.0, -5.5, -5.2, 0.9, 7.2)
            b.bx(trim, -5.8, 2.4, -5.6, -5.25, 0.5, 0.9)
            b.bx(trim, -5.8, 2.4, -5.6, -5.25, 7.2, 7.6)
            for x in (-5.6, -1.7, 2.2):
                b.bx(trim, x - 0.2, x + 0.2, -5.6, -5.25, 0.9, 7.2, bev=0)
            b.door("GlassDark", trim, (4.6, -5.2, 0), 2.6, 6.8, knob="Gold")
            # mannequins / display
            for k, x in enumerate((-4.0, -0.6)):
                b.cylz("Metal", x, -4.2, 0.9, 1.1, 0.6, 8)
                b.cylz("Metal", x, -4.2, 1.1, 2.8, 0.1, 5)
                b.lathe(("Red", "Gold", "Pink")[(i + k) % 3], [(0, 2.8), (1.0, 2.8), (0.55, 4.6), (0.7, 5.2), (0.3, 5.5), (0, 5.5)], c=(x, -4.2, 0), n=8)
                b.ball("White", (x, -4.2, 6.0), 0.4, seg=(8, 6))
            # awning
            with b.at(T(-1.6, -5.4, 8.2), R(-0.35, 0, 0)):
                for k in range(8):
                    x = -4.6 + (k + 0.5) * 9.2 / 8
                    b.box(col if k % 2 else "White", (x, -1.6, 0), (9.2 / 8, 3.2, 0.25))
            b.bx(col, -6.2, 6.2, -5.5, -5.0, 9.4, 11.6)
            b.text(gold, name, (0, -5.55, 10.5), 1.2, depth=0.15, font="serif", spacing=1.3)
            # upper floors
            for x in (-4.0, 0.0, 4.0):
                b.window("GlassDark", "White", (x, -5.2, 14.5), 2.2, 3.6, sill="White", lintel=trim, cross=True)
                b.bx("Charcoal", x - 1.6, x + 1.6, -6.4, -5.2, 12.2, 12.4)
                for k in range(5):
                    b.bx("Charcoal", x - 1.5 + k * 0.75, x - 1.4 + k * 0.75, -6.4, -6.3, 12.4, 13.5, bev=0)
                b.bx("Charcoal", x - 1.6, x + 1.6, -6.45, -6.25, 13.4, 13.6, bev=0)
            b.bx(trim, -W / 2 - 0.3, W / 2 + 0.3, -5.8, 6.3, H - 0.6, H + 0.4)
            b.bx(trim, -W / 2 - 0.2, W / 2 + 0.2, -5.5, 6.2, 8.5, 9.2)
            if i == 1:
                b.prism_y(trim, [(-4, H + 0.4), (4, H + 0.4), (0, H + 3.0)], -5.6, -4.8)
    # street lamps + planters on the pavement
    b.bx("Concrete", -22, 22, -10.5, -5.0, 0, 0.3, bev=0)
    for x in (-14.4, 0.0, 14.4):
        b.lamp("Charcoal", "WindowGlow", (x - 7.2, -9.4, 0.3), h=8.0)
    for x in (-11, 3.5, 17.5):
        b.bx("Charcoal", x - 1.0, x + 1.0, -9.8, -7.8, 0.3, 1.6)
        b.rock("Hedge", (x, -8.8, 2.4), 1.0, sc=(1, 1, 1.2), jitter=0.1)
    return b


def golden_fish_statue():
    b = Builder("GoldenFishStatue", AREA)
    b.bx("Marble", -5, 5, -5, 5, 0, 1.0)
    b.bx("MarbleDark", -4.2, 4.2, -4.2, 4.2, 1.0, 7.0)
    b.bx("Marble", -4.8, 4.8, -4.8, 4.8, 7.0, 8.0)
    b.bx("Gold", -3.0, 3.0, -4.3, -4.15, 3.0, 5.0, bev=0)
    b.text("MarbleDark", "FOUNDER", (0, -4.35, 4.0), 0.75, depth=0.1, font="serif")
    # wave base
    with b.at(T(0, 0, 8.0)):
        pts = []
        for k in range(14):
            a = PI * k / 13
            pts.append((-3.6 + 7.2 * k / 13, 1.4 + 1.6 * math.sin(a * 2) * (1 - k / 13) + 1.0 * (k / 13) ** 2 * 3))
        b.prism_y("Gold", [(-3.8, 0)] + pts + [(3.8, 0)], -2.0, 2.0)
    # the leaping fish
    with b.at(T(0, 0, 14.5), R(0, -0.55, 0)):
        b.ball("Gold", (0, 0, 0), 1.0, seg=(16, 10), sc=(4.2, 1.6, 2.4))
        b.prism_y("Gold", [(-3.4, 0), (-6.4, 2.6), (-5.6, 0), (-6.4, -2.6)], -0.3, 0.3)
        b.prism_y("Gold", [(-1.4, 2.1), (1.6, 2.2), (-0.6, 3.8)], -0.25, 0.25)
        b.prism_y("Gold", [(-1.2, -2.0), (0.6, -2.1), (-0.8, -3.2)], -0.2, 0.2)
        for sy in (-1, 1):
            b.prism_x("Gold", [(sy * 1.4, -0.4), (sy * 2.8, -1.4), (sy * 1.4, 0.6)], 0.6, 1.6)
            b.ball("White", (3.0, sy * 1.1, 0.6), 0.45, seg=(8, 6))
            b.ball("Black", (3.25, sy * 1.25, 0.65), 0.22, seg=(6, 4))
        b.box("Charcoal", (4.0, 0, -0.5), (0.5, 1.2, 0.25), ry=0.3, bev=0)
    for k in range(3):
        b.ball("Water", (2.6 + k * 0.8, -0.6, 19.5 + k * 1.3), 0.35 + k * 0.08, seg=(8, 6))
    for (x, y) in ((-4.6, -4.6), (4.6, -4.6), (-4.6, 4.6), (4.6, 4.6)):
        b.cylz("Gold", x, y, 8.0, 8.6, 0.5, 8)
    return b


def street_clock():
    b = Builder("StreetClock", AREA)
    b.lathe("Charcoal", [(0, 0), (1.4, 0), (1.4, 0.6), (1.0, 1.0), (0.9, 2.4), (0.5, 3.0), (0.4, 11.0), (0.7, 11.6), (0, 11.6)], n=12)
    for k in range(8):
        a = TAU * k / 8
        b.cylz("Brass", math.cos(a) * 0.42, math.sin(a) * 0.42, 3.4, 10.6, 0.08, 4)
    b.torus("Gold", (0, 0, 2.6), 0.85, 0.12, 12, 4)
    b.torus("Gold", (0, 0, 10.8), 0.55, 0.12, 12, 4)
    b.bx("Charcoal", -1.8, 1.8, -1.8, 1.8, 11.6, 15.4)
    for rz in (0, PI / 2, PI, -PI / 2):
        with b.at(R(0, 0, rz)):
            b.cyl("Gold", (0, -1.8, 13.5), (0, -2.0, 13.5), 1.55, 20)
            b.cyl("White", (0, -1.95, 13.5), (0, -2.1, 13.5), 1.3, 20)
            for k in range(12):
                a = TAU * k / 12
                b.box("Black", (math.cos(a) * 1.1, -2.15, 13.5 + math.sin(a) * 1.1), (0.12, 0.05, 0.25), ry=-a + PI / 2, bev=0)
            b.box("Black", (0.25, -2.2, 13.85), (0.12, 0.05, 0.9), ry=-0.6, bev=0)
            b.box("Black", (0.35, -2.22, 13.4), (0.7, 0.05, 0.1), ry=0.2, bev=0)
    b.bx("Gold", -2.0, 2.0, -2.0, 2.0, 15.4, 15.8)
    b.hip_roof("Charcoal", 0, 0, 15.8, 3.6, 3.6, 1.8, over=0.2, base=0.2)
    b.ball("Gold", (0, 0, 17.8), 0.35, seg=(8, 6))
    return b


def city_gate():
    b = Builder("CityGate", AREA)
    for sx in (-1, 1):
        x = sx * 11.0
        b.bx("Marble", x - 3.2, x + 3.2, -3.2, 3.2, 0, 1.6)
        b.bx("MarbleDark", x - 2.6, x + 2.6, -2.6, 2.6, 1.6, 3.2)
        b.bx("Marble", x - 2.2, x + 2.2, -2.2, 2.2, 3.2, 20.0)
        for k in range(5):
            b.bx("Marble", x - 2.45, x + 2.45, -2.45, 2.45, 4.0 + k * 3.4, 4.5 + k * 3.4)
        b.bx("Gold", x - 2.5, x + 2.5, -2.5, 2.5, 19.4, 20.4)
        b.bx("Marble", x - 2.8, x + 2.8, -2.8, 2.8, 20.4, 21.4)
        b.lathe("Marble", [(0, 0), (1.4, 0), (1.0, 1.0), (1.8, 2.4), (1.6, 3.2), (0, 3.2)], c=(x, 0, 21.4), n=10)
        b.ball("Gold", (x, 0, 25.4), 1.2, seg=(10, 8))
        b.cylz("Gold", x, 0, 26.4, 28.0, 0.2, 6, r2=0.0)
        b.lamp("Charcoal", "WindowGlow", (x + sx * 4.6, -2.0, 0), h=9.0, arms=2)
    # arch with gold scrollwork and a crown
    b.arch("Marble", (0, 0, 15.0), 8.8, 10.6, 3.6, n=16)
    b.arch("Gold", (0, -1.85, 15.0), 10.6, 11.1, 0.3, n=16)
    b.arch("Gold", (0, -1.85, 15.0), 8.4, 8.8, 0.3, n=16)
    for k in range(9):
        a = PI * (k + 0.5) / 9
        b.ball("Gold", (math.cos(a) * 9.7, -1.95, 15.0 + math.sin(a) * 9.7), 0.35, seg=(6, 4))
    b.bx("Marble", -8.8, 8.8, -1.4, 1.4, 15.0, 16.0)
    b.bx("Navy", -7.0, 7.0, -1.9, -1.6, 16.4, 19.6)
    b.text("Gold", "RICH CITY", (0, -1.95, 18.0), 1.8, depth=0.2, font="serif", spacing=1.2)
    with b.at(T(0, 0, 25.4)):
        b.lathe("Gold", [(0, 0), (2.4, 0), (2.4, 0.6), (2.0, 0.6), (2.0, 0.3), (0, 0.3)], n=16)
        for k in range(8):
            a = TAU * k / 8
            b.cyl("Gold", (math.cos(a) * 2.2, math.sin(a) * 2.2, 0.5), (math.cos(a) * 2.4, math.sin(a) * 2.4, 2.6), 0.3, 6, r2=0.05)
            b.ball("Red" if k % 2 else "Blue", (math.cos(a) * 2.42, math.sin(a) * 2.42, 2.7), 0.32, seg=(6, 4))
        b.ball("Purple", (0, 0, 1.4), 1.6, seg=(10, 6), sc=(1, 1, 0.8))
        b.ball("Gold", (0, 0, 2.9), 0.4, seg=(6, 4))
    # red carpet through the arch
    b.bx("Red", -3.0, 3.0, -9.0, 9.0, 0, 0.08, bev=0)
    b.bx("Gold", -3.2, -3.0, -9.0, 9.0, 0, 0.1, bev=0)
    b.bx("Gold", 3.0, 3.2, -9.0, 9.0, 0, 0.1, bev=0)
    return b


ASSETS = [mansion, glass_tower, art_deco_tower, bank, gold_fountain, hotel, limo, boutique_row,
          golden_fish_statue, street_clock, city_gate]
