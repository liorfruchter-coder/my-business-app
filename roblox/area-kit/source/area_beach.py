"""Area 1 -- Beach: pastel wood, sun-bleached planks, teal roofs."""
import math

from kit import PI, TAU, Builder, R, T, V

AREA = "Beach"
GROUND = (240, 220, 164)


def beach_house():
    b = Builder("BeachHouse", AREA)
    DZ = 8.0  # deck height
    # stilts + bracing
    xs = (-18, -6, 6, 18)
    ys = (-14, 0, 14)
    for x in xs:
        for y in ys:
            b.cylz("WoodDark", x, y, 0, DZ, 0.75, 10)
            b.cylz("Concrete", x, y, 0, 0.6, 1.1, 10)
    for y in ys:
        b.bx("WoodDark", -19, 19, y - 0.45, y + 0.45, DZ - 1.6, DZ - 0.6)
        for x0, x1 in ((-18, -6), (6, 18)):
            L = math.hypot(x1 - x0, DZ - 2.2)
            a = math.atan2(DZ - 2.2, x1 - x0)
            b.box("WoodDark", ((x0 + x1) / 2, y, 1.1 + (DZ - 2.2) / 2), (L, 0.4, 0.55), ry=-a)
    # deck
    b.planks(["Plank", "WoodLight", "Driftwood"], -21, 21, -16, 16, DZ, t=0.6, bw=1.5)
    for y in (-16.2, 16.2):
        b.bx("WoodDark", -21.2, 21.2, y - 0.3, y + 0.3, DZ - 1.3, DZ - 0.2)
    for x in (-21.2, 21.2):
        b.bx("WoodDark", x - 0.3, x + 0.3, -16.2, 16.2, DZ - 1.3, DZ - 0.2)
    # ground floor body (y -4..14)
    X0, X1, Y0, Y1 = -13, 13, -4, 14
    Z0, Z1 = DZ, DZ + 11
    b.bx("Accent", X0, X1, Y0, Y1, Z0, Z1)
    # clapboard siding
    for k in range(10):
        z = Z0 + 0.6 + k * 1.05
        b.bx("Accent", X0 - 0.22, X1 + 0.22, Y0 - 0.22, Y0 + 0.1, z, z + 0.32, bev=0)
        b.bx("Accent", X0 - 0.22, X1 + 0.22, Y1 - 0.1, Y1 + 0.22, z, z + 0.32, bev=0)
        b.bx("Accent", X0 - 0.22, X0 + 0.1, Y0, Y1, z, z + 0.32, bev=0)
        b.bx("Accent", X1 - 0.1, X1 + 0.22, Y0, Y1, z, z + 0.32, bev=0)
    for x in (X0, X1):
        for y in (Y0, Y1):
            b.bx("White", x - 0.55, x + 0.55, y - 0.55, y + 0.55, Z0, Z1 + 0.2)
    b.bx("White", X0 - 0.5, X1 + 0.5, Y0 - 0.5, Y1 + 0.5, Z1 - 0.2, Z1 + 0.6)
    # front: door + windows
    b.door("White", "White", (0, Y0 - 0.2, Z0), 4.2, 7.6, panels=True)
    b.box("Glass", (0, Y0 - 0.5, Z0 + 5.6), (2.4, 0.2, 2.4))
    for x in (-8, 8):
        b.window("Glass", "White", (x, Y0 - 0.25, Z0 + 5.4), 4.4, 4.6, shutters="Teal", sill="White")
    for y in (1, 9):
        b.window("Glass", "White", (X0 - 0.25, y, Z0 + 5.4), 3.6, 4.4, rz=-PI / 2, shutters="Teal", sill="White")
        b.window("Glass", "White", (X1 + 0.25, y, Z0 + 5.4), 3.6, 4.4, rz=PI / 2, shutters="Teal", sill="White")
    # lanterns by the door
    for x in (-3.4, 3.4):
        b.bx("Black", x - 0.45, x + 0.45, Y0 - 0.9, Y0 - 0.1, Z0 + 6.2, Z0 + 7.6)
        b.box("WindowGlow", (x, Y0 - 0.55, Z0 + 6.9), (0.6, 0.6, 1.0))
    # porch roof on posts
    for x in (-19.5, -7, 7, 19.5):
        b.bx("White", x - 0.45, x + 0.45, -15.5, -14.6, DZ, DZ + 9.4)
    b.bx("White", -20.5, 20.5, -15.8, -14.4, DZ + 9.2, DZ + 10.0)
    with b.at(T(0, -10.3, DZ + 10.25), R(math.atan2(1.1, 10.6), 0, 0)):
        b.box("Teal", (0, 0, 0), (43, 12.6, 0.5))
        for k in range(22):
            b.box("Teal", (-20.5 + k * 1.95, 0, 0.32), (0.32, 12.6, 0.22), bev=0)
    # rooftop deck around the upper storey
    b.planks(["Plank", "WoodLight"], X0 - 0.4, X1 + 0.4, Y0 - 0.4, Y1 + 0.4, Z1 + 1.0, t=0.4, bw=1.4)
    b.rail_loop("White", "White", [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)], Z1 + 1.0, h=2.8, spacing=4.3,
                balusters="White", bal_sp=0.9)
    # upper storey
    U0, U1, V0, V1 = -8, 8, 1, 13
    Z2, Z3 = Z1 + 1.0, Z1 + 9.5
    b.bx("Accent", U0, U1, V0, V1, Z2, Z3)
    for k in range(8):
        z = Z2 + 0.5 + k * 1.05
        b.bx("Accent", U0 - 0.22, U1 + 0.22, V0 - 0.22, V0 + 0.1, z, z + 0.32, bev=0)
        b.bx("Accent", U0 - 0.22, U0 + 0.1, V0, V1, z, z + 0.32, bev=0)
        b.bx("Accent", U1 - 0.1, U1 + 0.22, V0, V1, z, z + 0.32, bev=0)
    for x in (U0, U1):
        for y in (V0, V1):
            b.bx("White", x - 0.5, x + 0.5, y - 0.5, y + 0.5, Z2, Z3)
    b.door("Glass", "White", (-3.2, V0 - 0.2, Z2), 3.6, 6.6, panels=False, knob=None)
    b.window("Glass", "White", (3.6, V0 - 0.25, Z2 + 4.2), 3.4, 4.0, shutters="Teal", sill="White")
    for y in (4.5, 9.5):
        b.window("Glass", "White", (U0 - 0.25, y, Z2 + 4.2), 3.0, 3.6, rz=-PI / 2, sill="White")
        b.window("Glass", "White", (U1 + 0.25, y, Z2 + 4.2), 3.0, 3.6, rz=PI / 2, sill="White")
    b.hip_roof("Teal", 0, (V0 + V1) / 2, Z3, U1 - U0, V1 - V0, 5.5, over=1.6, base=0.5)
    b.bx("White", U0 - 1.7, U1 + 1.7, V0 - 1.7, V1 + 1.7, Z3 - 0.8, Z3 - 0.3)
    # widow's walk cupola + weathervane
    cz = Z3 + 4.2
    b.bx("White", -1.8, 1.8, 5.2, 8.8, cz - 1.2, cz + 2.6)
    for x in (-1.85, 1.85):
        b.box("Glass", (x, 7, cz + 0.9), (0.2, 2.4, 2.4))
    b.box("Glass", (0, 5.15, cz + 0.9), (2.4, 0.2, 2.4))
    b.hip_roof("Teal", 0, 7, cz + 2.6, 3.6, 3.6, 2.2, over=0.5, base=0.3)
    b.cylz("DarkMetal", 0, 7, cz + 4.6, cz + 8.0, 0.12, 6)
    b.prism_y("DarkMetal", [(-1.6, 0), (1.4, 0), (1.9, 0.5), (1.4, 1.0), (-0.6, 1.0), (-1.6, 1.4)], 6.94, 7.06)
    with b.at(T(0, 7, cz + 7.0)):
        b.prism_y("DarkMetal", [(-1.6, -0.1), (1.6, -0.1), (2.2, 0.4), (1.6, 0.9), (-1.0, 0.9), (-1.8, 1.5)], -0.06, 0.06)
    # deck railing (gap where the stairs arrive)
    rail = dict(h=3.0, spacing=4.2, balusters="White", bal_sp=0.9)
    b.rail("White", "White", (-21, -16), (21, -16), DZ, **rail)
    b.rail("White", "White", (-21, -16), (-21, 16), DZ, **rail)
    b.rail("White", "White", (-21, 16), (21, 16), DZ, **rail)
    b.rail("White", "White", (21, -16), (21, -6), DZ, **rail)
    b.rail("White", "White", (21, 0), (21, 16), DZ, **rail)
    # stairs up the right side
    b.stairs("Plank", (23.4, -21.0 + 0.0, 0), 4.6, 12, DZ / 12, 1.25, rz=0, stringer="WoodDark", rails="White")
    b.bx("Plank", 21.0, 25.8, -6.0, 0.0, DZ - 0.6, DZ)
    for x in (21.4, 25.4):
        b.cylz("WoodDark", x, -3, 0, DZ - 0.6, 0.45, 8)
    b.rail("White", "White", (25.7, -6), (25.7, 0), DZ, **rail)
    b.rail("White", "White", (21, 0), (25.7, 0), DZ, **rail)
    # deck furniture: two chairs, a planter, a lifebuoy
    for x, col in ((-15, "Coral"), (-10.5, "SkyBlue")):
        with b.at(T(x, -11, DZ), R(0, 0, 0.15)):
            b.bx(col, -1.2, 1.2, -1.2, 1.4, 1.4, 1.8)
            b.box(col, (0, 1.6, 3.0), (2.4, 0.4, 3.2), rx=-0.3)
            for sx in (-1.3, 1.3):
                b.bx(col, sx - 0.2, sx + 0.2, -1.2, 1.6, 2.4, 2.7)
                b.bx(col, sx - 0.2, sx + 0.2, -1.0, -0.6, 0, 2.4)
                b.bx(col, sx - 0.2, sx + 0.2, 1.0, 1.4, 0, 2.4)
    b.cylz("WoodDark", -17, 11, DZ, DZ + 2.0, 1.3, 10, r2=1.5)
    b.foliage("Leaf", (-17, 11, DZ + 3.4), 1.6, n=4, styles=["Leaf", "LeafLight", "LeafDark"])
    b.torus("Red", (13.8, 5.6, Z0 + 6.6), 1.4, 0.42, 16, 6, rx=PI / 2, rz=PI / 2)
    for k in range(4):
        a = PI / 4 + k * PI / 2
        b.torus("White", (13.8, 5.6, Z0 + 6.6), 1.4, 0.45, 3, 6, rx=PI / 2, rz=PI / 2, a0=a - 0.3, a1=a + 0.3)
    return b


def surf_shack():
    b = Builder("SurfShack", AREA)
    # sand footings + deck
    for x in (-14, -5, 5, 14):
        for y in (-10, 0, 10):
            b.bx("Concrete", x - 0.7, x + 0.7, y - 0.7, y + 0.7, 0, 0.8)
    b.planks(["Plank", "WoodLight", "Driftwood"], -15, 15, -11, 11, 1.4, t=0.6, bw=1.4, along="y")
    b.bx("WoodDark", -15.2, 15.2, -11.3, -10.7, 0.5, 1.2)
    # shack body: board-and-batten
    X0, X1, Y0, Y1 = -10, 10, -1, 10
    Z0, Z1 = 1.4, 11.5
    b.bx("Driftwood", X0, X1, Y0, Y1, Z0, Z1)
    for i in range(14):
        x = X0 + 0.4 + i * (X1 - X0 - 0.8) / 13
        b.bx("WoodLight", x - 0.18, x + 0.18, Y0 - 0.25, Y0, Z0, Z1, bev=0)
    for i in range(8):
        y = Y0 + 0.4 + i * (Y1 - Y0 - 0.8) / 7
        b.bx("WoodLight", X0 - 0.25, X0, y - 0.18, y + 0.18, Z0, Z1, bev=0)
        b.bx("WoodLight", X1, X1 + 0.25, y - 0.18, y + 0.18, Z0, Z1, bev=0)
    # serving window, counter, prop-up shutter
    b.bx("Charcoal", -6.5, 6.5, Y0 - 0.32, Y0 - 0.1, 5.2, 9.4)
    b.bx("WoodDark", -7.0, 7.0, Y0 - 0.5, Y0 - 0.15, 9.4, 9.9)
    b.bx("WoodDark", -7.0, -6.5, Y0 - 0.5, Y0 - 0.15, 5.0, 9.9)
    b.bx("WoodDark", 6.5, 7.0, Y0 - 0.5, Y0 - 0.15, 5.0, 9.9)
    b.bx("Plank", -7.4, 7.4, Y0 - 2.0, Y0, 4.9, 5.4)
    for x in (-6.0, 6.0):
        b.box("WoodDark", (x, Y0 - 1.6, 4.0), (0.4, 0.4, 1.8), rx=0.5)
    with b.at(T(0, Y0 - 0.2, 9.9), R(-1.0, 0, 0)):
        b.bx("Accent", -7.2, 7.2, -4.6, 0, -0.18, 0.18)
        for k in range(5):
            x = -7.2 + 1.44 + k * 2.88
            b.bx("White", x - 0.72, x + 0.72, -4.6, 0, 0.18, 0.28, bev=0)
    for x in (-6.2, 6.2):
        b.cyl("WoodDark", (x, Y0 - 0.3, 5.5), (x, Y0 - 3.6, 12.2), 0.15, 6)
    # goods behind the counter
    for k, col in enumerate(("Coral", "Yellow", "Mint", "SkyBlue", "Lilac")):
        b.bx(col, -5.6 + k * 2.4, -4.4 + k * 2.4, Y0 + 0.3, Y0 + 1.3, 5.4, 6.6)
    # side door
    b.door("Teal", "White", (X1 + 0.2, 5, Z0), 3.4, 7.2, rz=PI / 2)
    b.window("Glass", "White", (X0 - 0.2, 5, 7.0), 3.2, 3.2, rz=-PI / 2, sill="WoodDark")
    # shed roof (corrugated tin)
    with b.at(T(0, 4.5, 12.4), R(math.atan2(2.4, 15.0), 0, 0)):
        b.box("Metal", (0, 0, 0), (23.0, 16.5, 0.35))
        for k in range(24):
            b.cyl("Metal", (-11.2 + k * 0.97, -8.2, 0.2), (-11.2 + k * 0.97, 8.2, 0.2), 0.2, 6)
    b.bx("WoodDark", X0, X1, Y0 - 0.3, Y0 + 0.3, Z1, 12.0)
    b.bx("WoodDark", X0, X1, Y1 - 0.3, Y1 + 0.3, Z1, 14.4)
    # sign board on top
    b.bx("WoodDark", -7.5, 7.5, -3.6, -3.1, 13.0, 17.4)
    for x in (-6.0, 6.0):
        b.bx("WoodDark", x - 0.3, x + 0.3, -3.1, -2.5, 10.4, 17.0)
    b.bx("Teal", -7.0, 7.0, -3.85, -3.55, 13.4, 17.0)
    b.text("White", "SURF", (0, -3.95, 15.2), 3.3, depth=0.4)
    with b.at(T(0, -4.0, 13.8)):
        pts = [(-6.4, 0)] + [(-6.4 + i * 0.4, 0.35 + 0.35 * math.sin(i * 0.9)) for i in range(33)] + [(6.4, 0)]
        b.prism_y("SkyBlue", pts, -0.15, 0.15)
    # surfboards: a rack and two leaning on the wall

    def board(col, stripe, c, rz=0.0, rx=0.0, ry=0.0, L=8.0):
        with b.at(T(c), R(rx, ry, rz)):
            b.ball(col, (0, 0, 0), 1.0, seg=(16, 8), sc=(1.05, 0.16, L / 2))
            b.box(stripe, (0, -0.02, 0), (0.28, 0.36, L * 0.86), bev=0)
            b.prism_x(stripe, [(0.0, -L / 2 + 0.6), (0.9, -L / 2 + 0.4), (0.0, -L / 2 + 1.6)], -0.06, 0.06)

    with b.at(T(-13.0, 3.0, 1.4)):
        for y in (-3.5, 3.5):
            b.cyl("WoodDark", (-0.9, y, 0), (0, y, 6.4), 0.22, 6)
            b.cyl("WoodDark", (0.9, y, 0), (0, y, 6.4), 0.22, 6)
        b.cyl("WoodDark", (0, -4, 6.3), (0, 4, 6.3), 0.2, 6)
        for k, (col, st) in enumerate((("Yellow", "Red"), ("Coral", "White"), ("SkyBlue", "Navy"), ("Mint", "Teal"))):
            board(col, st, (0.35 * (-1) ** k, -2.6 + k * 1.7, 4.2), rz=PI / 2, ry=0.18 * (-1) ** k, L=7.2)
    board("Lilac", "White", (8.4, Y0 - 0.7, 5.4), rx=0.12, L=8.0)
    board("Orange", "Navy", (-8.6, Y0 - 0.7, 5.4), rx=0.12, ry=0.05, L=8.0)
    # stools, cooler, barrel, flag
    for x in (-4.5, 0.0, 4.5):
        b.cylz("WoodDark", x, -5.6, 1.4, 4.2, 0.25, 6)
        b.cylz("Accent", x, -5.6, 4.2, 4.7, 1.0, 12)
    b.bx("Blue", 11.0, 13.6, -9.6, -7.6, 1.4, 3.2)
    b.bx("White", 10.9, 13.7, -9.7, -7.5, 3.2, 3.7)
    b.lathe("WoodLight", [(0, 0), (1.1, 0), (1.3, 1.4), (1.1, 2.8), (0, 2.8)], c=(-12.6, -8.6, 1.4), n=12)
    for z in (1.9, 3.7):
        b.torus("DarkMetal", (-12.6, -8.6, z), 1.27, 0.08, 14, 4)
    b.cylz("White", 13.8, 9.0, 1.4, 20.0, 0.18, 8)
    b.prism_y("Accent", [(13.95, 19.7), (13.95, 16.0), (19.2, 17.85)], 8.94, 9.06)
    return b


def ice_cream_kiosk():
    b = Builder("IceCreamKiosk", AREA)
    b.lathe("White", [(0, 0), (8.5, 0), (8.5, 0.6), (0, 0.6)], n=32)
    for k in range(16):
        a0, a1 = TAU * k / 16, TAU * (k + 1) / 16
        if k % 2 == 0:
            b.mesh("Pink", [(0, 0, 0.62), (math.cos(a0) * 8.3, math.sin(a0) * 8.3, 0.62), (math.cos(a1) * 8.3, math.sin(a1) * 8.3, 0.62)], [[0, 1, 2]])
    b.lathe("Pink", [(0, 0.6), (5.6, 0.6), (5.6, 4.2), (0, 4.2)], n=24)
    b.lathe("White", [(0, 4.2), (6.6, 4.2), (6.6, 4.9), (0, 4.9)], n=24)
    b.lathe("White", [(0, 4.9), (5.4, 4.9), (5.4, 9.0), (0, 9.0)], n=24)
    for k in range(10):
        a = TAU * k / 10
        b.box("Pink", (math.cos(a) * 5.6, math.sin(a) * 5.6, 2.4), (0.4, 0.7, 3.4), rz=a, bev=0)
    # service windows on the front half
    for a in (-PI / 2 - 0.75, -PI / 2, -PI / 2 + 0.75):
        with b.at(T(math.cos(a) * 5.4, math.sin(a) * 5.4, 0), R(0, 0, a + PI / 2)):
            b.bx("Charcoal", -1.6, 1.6, -0.25, 0.05, 5.2, 8.2)
            b.bx("Mint", -1.9, 1.9, -0.45, -0.05, 8.2, 8.6)
            b.bx("Mint", -1.9, -1.6, -0.45, -0.05, 4.9, 8.6)
            b.bx("Mint", 1.6, 1.9, -0.45, -0.05, 4.9, 8.6)
            b.box("Glass", (0, -1.4, 5.7), (3.0, 1.6, 1.4))
            for k, col in enumerate(("Pink", "Mint", "Chocolate", "Lemon")):
                b.bx(col, -1.3 + k * 0.68, -0.8 + k * 0.68, -1.9, -0.9, 5.0, 5.6, bev=0)
    b.lathe("Mint", [(0, 9.0), (3.2, 9.0), (3.0, 10.4), (0, 10.4)], n=20)
    b.striped_canopy("Pink", "White", (0, 0), 8.6, 3.2, n=16, z=10.2)
    # sign band on the canopy
    b.bx("Cream", -5.2, 5.2, -8.6, -8.0, 9.2, 11.0)
    b.text("Cherry", "ICE CREAM", (0, -8.75, 10.1), 1.25, depth=0.3)
    # the giant cone
    b.cyl("Waffle", (0, 0, 12.6), (0, 0, 21.5), 0.4, 16, r2=3.6)
    for k in range(5):
        z = 14.0 + k * 1.6
        r = 0.4 + (z - 12.6) / 8.9 * 3.2
        b.torus("Chocolate", (0, 0, z), r + 0.02, 0.12, 16, 4)
    for k in range(12):
        a = TAU * k / 12
        b.cyl("Chocolate", (math.cos(a) * 0.5, math.sin(a) * 0.5, 12.8), (math.cos(a) * 3.62, math.sin(a) * 3.62, 21.4), 0.1, 4)
    b.torus("Waffle", (0, 0, 21.5), 3.6, 0.45, 20, 6)

    def scoop(col, z, r):
        b.ball(col, (0, 0, z), r, seg=(18, 12), sc=(1, 1, 0.86))
        for k in range(10):
            a = TAU * k / 10 + 0.3
            b.ball(col, (math.cos(a) * r * 0.92, math.sin(a) * r * 0.92, z - r * 0.55 - (k % 3) * 0.25), r * 0.22, seg=(8, 6),
                   sc=(1, 1, 1.4))

    scoop("Pink", 23.4, 3.7)
    scoop("Mint", 26.6, 3.2)
    scoop("Chocolate", 29.3, 2.7)
    for k in range(14):
        a = TAU * k / 14
        b.box(("Yellow", "SkyBlue", "Lilac", "White")[k % 4], (math.cos(a) * 2.2, math.sin(a) * 2.2, 30.6 + (k % 2) * 0.3),
              (0.7, 0.18, 0.18), rz=a + 0.8, rx=0.4, bev=0)
    b.ball("Cherry", (0, 0, 32.4), 0.9, seg=(10, 8))
    b.cyl("LeafDark", (0, 0, 33.1), (0.5, 0.2, 34.4), 0.08, 4)
    # menu board + bistro set
    with b.at(T(-6.0, -11.0, 0), R(0, 0, 0.3)):
        b.box("WoodDark", (0, -0.6, 2.0), (2.6, 0.3, 4.0), rx=-0.18)
        b.box("WoodDark", (0, 0.6, 2.0), (2.6, 0.3, 4.0), rx=0.18)
        b.box("Charcoal", (0, -0.9, 2.2), (2.2, 0.1, 3.0), rx=-0.18, bev=0)
        for k, col in enumerate(("Pink", "Mint", "Lemon")):
            b.box(col, (0, -1.0, 3.1 - k * 0.8), (1.6, 0.06, 0.24), rx=-0.18, bev=0)
    for cx, cy in ((7.4, -9.6), (11.5, -3.5)):
        b.cylz("White", cx, cy, 0, 0.2, 1.0, 12)
        b.cylz("Metal", cx, cy, 0, 3.0, 0.15, 6)
        b.cylz("White", cx, cy, 3.0, 3.3, 1.5, 16)
        for a in (0.4, 0.4 + PI):
            x, y = cx + math.cos(a) * 2.6, cy + math.sin(a) * 2.6
            b.cylz("Mint", x, y, 1.8, 2.1, 0.9, 12)
            for k in range(4):
                aa = TAU * k / 4 + 0.78
                b.cyl("Metal", (x + math.cos(aa) * 0.6, y + math.sin(aa) * 0.6, 0), (x + math.cos(aa) * 0.5, y + math.sin(aa) * 0.5, 1.8), 0.08, 4)
            bx = x + math.cos(a) * 0.8
            by = y + math.sin(a) * 0.8
            b.box("Mint", (bx, by, 3.2), (0.3, 1.8, 2.2), rz=a, ry=0.12)
    return b


def pier():
    b = Builder("Pier", AREA)
    DZ = 6.0
    L = 70.0
    W = 12.0
    # posts + beams + braces
    for i in range(10):
        y = -L / 2 + 2 + i * (L - 4) / 9
        for sx in (-1, 1):
            b.cylz("WoodDark", sx * (W / 2 - 0.6), y, 0, DZ + 3.4 if i % 3 == 0 else DZ - 0.4, 0.75, 10)
        b.bx("WoodDark", -W / 2 - 0.4, W / 2 + 0.4, y - 0.5, y + 0.5, DZ - 1.6, DZ - 0.5)
        if i < 9:
            a = math.atan2(DZ - 2.5, W - 1.2)
            b.box("WoodDark", (0, y, 1.0 + (DZ - 2.5) / 2), (math.hypot(W - 1.2, DZ - 2.5), 0.4, 0.5), ry=a * (1 if i % 2 else -1))
    for sx in (-1, 1):
        b.bx("WoodDark", sx * (W / 2 - 0.6) - 0.4, sx * (W / 2 - 0.6) + 0.4, -L / 2, L / 2, DZ - 2.0, DZ - 0.5)
    b.planks(["Plank", "Driftwood", "WoodLight"], -W / 2, W / 2, -L / 2, L / 2, DZ, t=0.55, bw=1.25, along="x")
    # rope rail strung between the tall posts
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.6)
        ys = [-L / 2 + 2 + i * (L - 4) / 9 for i in (0, 3, 6, 9)]
        for y0, y1 in zip(ys, ys[1:]):
            pts = []
            for k in range(13):
                t = k / 12
                pts.append((x, lerp(y0, y1, t), DZ + 2.9 - math.sin(t * PI) * 1.2))
            b.tube("Rope", pts, 0.16, 6)
        for y in ys:
            b.cylz("WoodDark", x, y, DZ + 3.4, DZ + 3.8, 0.9, 10)
    # lamps
    for y in (-L / 2 + 14, 4, L / 2 - 16):
        for sx in (-1, 1):
            b.lamp("DarkMetal", "WindowGlow", (sx * (W / 2 - 0.6), y, DZ), h=7.5)
    # ramp steps at the land end
    b.stairs("Plank", (0, -L / 2 - 9.6, 0), 8.0, 8, DZ / 8, 1.2, stringer="WoodDark")
    # end platform + gazebo
    PY = L / 2 + 10
    for x in (-12, -4, 4, 12):
        for y in (PY - 9, PY, PY + 9):
            b.cylz("WoodDark", x, y, 0, DZ - 0.4, 0.75, 10)
    b.planks(["Plank", "Driftwood", "WoodLight"], -13.5, 13.5, L / 2 - 0.2, PY + 10.5, DZ, t=0.55, bw=1.25, along="x")
    b.bx("WoodDark", -13.7, 13.7, PY + 10.5, PY + 11.0, DZ - 1.2, DZ - 0.2)
    pts = [(-13.2, L / 2), (-13.2, PY + 10.3), (13.2, PY + 10.3), (13.2, L / 2)]
    b.rail_loop("WoodDark", "White", pts, DZ, h=3.0, spacing=3.6, closed=False, balusters="White", bal_sp=1.0)
    b.rail("WoodDark", "White", (-13.2, L / 2), (-W / 2, L / 2), DZ, h=3.0, spacing=3.6, balusters="White")
    b.rail("WoodDark", "White", (W / 2, L / 2), (13.2, L / 2), DZ, h=3.0, spacing=3.6, balusters="White")
    gz = (0, PY + 2)
    for k in range(6):
        a = TAU * k / 6 + PI / 6
        x, y = gz[0] + math.cos(a) * 6.5, gz[1] + math.sin(a) * 6.5
        b.cylz("White", x, y, DZ, DZ + 8.5, 0.35, 8)
        b.cylz("White", x, y, DZ, DZ + 0.8, 0.6, 8)
    b.lathe("White", [(6.8, DZ + 8.4), (7.6, DZ + 8.4), (7.6, DZ + 9.2), (6.8, DZ + 9.2)], c=(gz[0], gz[1], 0), n=6, )
    b.lathe("Teal", [(0, DZ + 9.2), (8.4, DZ + 9.2), (8.4, DZ + 9.7), (0.3, DZ + 13.6), (0, DZ + 13.6)],
            c=(gz[0], gz[1], 0), n=6)
    b.cylz("White", gz[0], gz[1], DZ + 13.4, DZ + 14.6, 0.5, 8, r2=0.2)
    b.ball("White", (gz[0], gz[1], DZ + 14.9), 0.45, seg=(8, 6))
    for k in range(3):
        a = PI / 2 + TAU * k / 6 + PI / 6 + PI / 2
        x, y = gz[0] + math.cos(a) * 4.8, gz[1] + math.sin(a) * 4.8
        with b.at(T(x, y, DZ), R(0, 0, a + PI / 2)):
            b.bx("Plank", -2.4, 2.4, -0.7, 0.7, 1.6, 2.0)
            for sx in (-2.0, 2.0):
                b.bx("WoodDark", sx - 0.2, sx + 0.2, -0.5, 0.5, 0, 1.6)
    # a bell post + bucket
    b.cylz("WoodDark", 10.5, PY + 7.5, DZ, DZ + 5.5, 0.3, 8)
    b.cyl("WoodDark", (10.5, PY + 7.5, DZ + 5.3), (8.8, PY + 7.5, DZ + 5.3), 0.2, 6)
    b.lathe("Brass", [(0, 0), (0.9, 0), (0.7, 0.4), (0.55, 1.3), (0.25, 1.6), (0, 1.6)], c=(8.9, PY + 7.5, DZ + 3.5), n=12)
    b.lathe("SkyBlue", [(0, 0), (0.7, 0), (0.9, 1.3), (0.8, 1.3), (0.6, 0.15), (0, 0.15)], c=(-9.5, PY + 6, DZ), n=12)
    return b


def lerp(a, b_, t):
    return a + (b_ - a) * t


def beach_cabanas():
    b = Builder("BeachCabanas", AREA)
    b.planks(["Plank", "Driftwood"], -17.5, 17.5, -7.0, 5.0, 0.9, t=0.9, bw=1.3, along="x")
    b.bx("WoodDark", -17.7, 17.7, -7.2, -6.8, 0.0, 0.9)
    cols = ("Coral", "SkyBlue", "Yellow", "Mint")
    for i, col in enumerate(cols):
        cx = -12.6 + i * 8.4
        HW, Y0, Y1, Z0, Z1 = 3.5, -2.6, 4.2, 0.9, 8.6
        with b.at(T(cx, 0, 0)):
            b.bx(col, -HW, HW, Y0, Y1, Z0, Z1)
            for k in range(7):
                z = Z0 + 0.5 + k * 1.05
                b.bx(col, -HW - 0.15, HW + 0.15, Y0 - 0.15, Y0, z, z + 0.3, bev=0)
                b.bx(col, -HW - 0.15, -HW, Y0, Y1, z, z + 0.3, bev=0)
                b.bx(col, HW, HW + 0.15, Y0, Y1, z, z + 0.3, bev=0)
            for x in (-HW, HW):
                for y in (Y0, Y1):
                    b.bx("White", x - 0.35, x + 0.35, y - 0.35, y + 0.35, Z0, Z1 + 0.1)
            b.bx("White", -HW - 0.3, HW + 0.3, Y0 - 0.4, Y1 + 0.3, Z1 - 0.1, Z1 + 0.35)
            # double doors
            b.bx("White", -2.3, 2.3, Y0 - 0.45, Y0 - 0.15, Z0, Z0 + 6.4)
            for sx in (-1, 1):
                x = sx * 1.05
                b.bx("White", x - 0.95, x + 0.95, Y0 - 0.6, Y0 - 0.4, Z0 + 0.2, Z0 + 6.0)
                for k in (-0.5, 0.0, 0.5):
                    b.bx(col, x + k - 0.08, x + k + 0.08, Y0 - 0.66, Y0 - 0.58, Z0 + 0.5, Z0 + 3.6, bev=0)
                b.bx("Glass", x - 0.65, x + 0.65, Y0 - 0.66, Y0 - 0.58, Z0 + 4.0, Z0 + 5.6, bev=0)
                b.ball("Brass", (sx * 0.35, Y0 - 0.72, Z0 + 3.2), 0.16, seg=(6, 4))
            # front gable roof (ridge front-to-back)
            with b.at(T(0, (Y0 + Y1) / 2, 0), R(0, 0, PI / 2)):
                b.gable_roof("White", 0, 0, Z1 + 0.3, Y1 - Y0, 2 * HW, 3.2, t=0.45, over=0.7)
                b.gable_end("White", -(Y1 - Y0) / 2 - 0.05, 0, Z1 + 0.3, 2 * HW, 3.2, t=0.4)
                b.gable_end("White", (Y1 - Y0) / 2, 0, Z1 + 0.3, 2 * HW, 3.2, t=0.4)
            a = math.atan2(3.2, HW)
            Lb = math.hypot(HW + 0.7, 3.2 + 0.7 * math.tan(a)) + 0.3
            for sx in (-1, 1):
                b.box(col, (sx * (HW + 0.7) / 2, Y0 - 1.05, Z1 + 0.3 + 3.2 / 2 - 0.25), (Lb, 0.3, 0.55), ry=sx * a)
            b.cyl("Charcoal", (0, Y0 - 0.55, Z1 + 1.6), (0, Y0 - 0.85, Z1 + 1.6), 0.6, 12)
            b.cyl(col, (0, Y0 - 0.5, Z1 + 1.6), (0, Y0 - 0.95, Z1 + 1.6), 0.75, 12, caps=True)
            b.cyl("Charcoal", (0, Y0 - 0.5, Z1 + 1.6), (0, Y0 - 1.0, Z1 + 1.6), 0.55, 12)
            b.text("White", str(i + 1), (HW - 0.9, Y0 - 0.2, Z1 - 1.0), 0.9, depth=0.12)
            b.cylz("WoodDark", -HW + 0.5, Y0 - 0.2, Z0 + 6.2, Z0 + 6.4, 0.1, 4)
    b.stairs("Plank", (0, -9.4, 0), 33.0, 2, 0.45, 1.2, rz=0)
    return b


def shower_station():
    b = Builder("ShowerStation", AREA)
    b.bx("WoodDark", -3.2, 3.2, -3.2, 3.2, 0, 0.35)
    for k in range(9):
        y = -2.8 + k * 0.7
        b.bx("Plank", -3.0, 3.0, y - 0.25, y + 0.25, 0.35, 0.7, bev=0)
    b.cylz("Metal", 0, 1.8, 0.7, 11.0, 0.32, 10)
    b.cylz("Teal", 0, 1.8, 0.7, 1.4, 0.75, 10)
    b.cyl("Metal", (-3.2, 1.8, 11.0), (3.2, 1.8, 11.0), 0.25, 8)
    b.ball("Metal", (0, 1.8, 11.0), 0.45, seg=(8, 6))
    for sx in (-1, 1):
        x = sx * 3.2
        b.cyl("Metal", (x, 1.8, 11.0), (x, 0.6, 10.3), 0.2, 8)
        b.cyl("Metal", (x, 0.6, 10.3), (x, 0.3, 9.6), 0.25, 10, r2=0.6)
        for k in range(7):
            a = TAU * k / 7
            b.cylz("Water", x + math.cos(a) * 0.35, 0.3 + math.sin(a) * 0.35, 0.7, 9.5, 0.05, 4)
    b.cyl("Metal", (0, 1.8, 3.6), (0, 0.9, 3.6), 0.12, 6)
    b.ball("Red", (0, 0.8, 3.6), 0.3, seg=(8, 6))
    b.bx("White", -1.6, 1.6, 2.15, 2.35, 6.0, 7.8)
    b.text("Teal", "SHOWER", (0, 2.0, 6.9), 0.6, depth=0.12)
    b.lathe("Blue", [(0, 0), (0.7, 0), (0.8, 1.2), (0.7, 1.2), (0.6, 0.15), (0, 0.15)], c=(2.4, -2.0, 0.7), n=10)
    return b


def volleyball_court():
    b = Builder("VolleyballCourt", AREA)
    hw, hd = 18.0, 9.0
    b.bx("Sand", -hw - 4, hw + 4, -hd - 4, hd + 4, 0, 0.3, bev=0.2)
    for (x0, x1, y0, y1) in ((-hw, hw, -hd - 0.3, -hd + 0.3), (-hw, hw, hd - 0.3, hd + 0.3),
                             (-hw - 0.3, -hw + 0.3, -hd, hd), (hw - 0.3, hw + 0.3, -hd, hd)):
        b.bx("White", x0, x1, y0, y1, 0.3, 0.42, bev=0)
    for (x, y) in ((-hw, -hd), (hw, -hd), (-hw, hd), (hw, hd)):
        b.cylz("Red", x, y, 0, 0.5, 0.25, 6)
    for y in (-hd - 1.2, hd + 1.2):
        b.cylz("WoodDark", 0, y, 0, 10.5, 0.42, 10)
        b.cylz("Concrete", 0, y, 0, 0.6, 0.9, 10)
        b.ball("WoodDark", (0, y, 10.6), 0.5, seg=(8, 6))
    NZ0, NZ1 = 6.8, 9.8
    b.bx("White", -0.12, 0.12, -hd - 0.8, hd + 0.8, NZ1 - 0.35, NZ1)
    b.bx("White", -0.1, 0.1, -hd - 0.8, hd + 0.8, NZ0, NZ0 + 0.18, bev=0)
    for k in range(41):
        y = -hd - 0.6 + k * (2 * hd + 1.2) / 40
        b.bx("Black", -0.04, 0.04, y - 0.04, y + 0.04, NZ0, NZ1 - 0.35, bev=0)
    for k in range(8):
        z = NZ0 + 0.18 + k * 0.33
        b.bx("Black", -0.04, 0.04, -hd - 0.6, hd + 0.6, z - 0.04, z + 0.04, bev=0)
    for y in (-hd, hd):
        for k in range(8):
            b.cylz("Red" if k % 2 == 0 else "White", 0, y, NZ0 + k * 0.6, NZ0 + (k + 1) * 0.6, 0.08, 6)
    # referee chair
    with b.at(T(0, -hd - 4.5, 0)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.cyl("Metal", (sx * 1.4, sy * 1.4, 0), (sx * 0.8, sy * 0.8, 6.2), 0.14, 6)
        for z in (2.0, 4.0):
            b.bx("Metal", -1.3, 1.3, -1.35, -1.15, z - 0.1, z + 0.1)
        b.bx("Yellow", -1.2, 1.2, -1.2, 1.2, 6.2, 6.7)
        b.bx("Yellow", -1.2, 1.2, 1.0, 1.4, 6.7, 9.0)
        b.cylz("White", 0, 0.2, 6.7, 12.6, 0.1, 6)
        b.striped_canopy("Yellow", "White", (0, 0.2), 2.6, 1.2, n=8, z=12.4)
    # bleacher behind the far line
    with b.at(T(0, hd + 9.0, 0)):
        for k in range(3):
            z = 1.2 + k * 1.3
            y = -2.4 + k * 1.6
            b.planks(["Plank", "WoodLight"], -11, 11, y - 0.8, y + 0.8, z, t=0.35, bw=0.8, along="x")
            b.bx("Plank", -11, 11, y - 0.95, y - 0.75, z - 1.25, z - 0.35, bev=0)
        for x in (-10.5, -3.5, 3.5, 10.5):
            b.bx("Metal", x - 0.15, x + 0.15, -3.2, -2.9, 0, 0.9)
            b.bx("Metal", x - 0.15, x + 0.15, 1.8, 2.1, 0, 3.8)
            b.box("Metal", (x, -0.55, 1.9), (0.3, 5.6, 0.3), rx=0.62)
        b.rail("Metal", "Metal", (-11, 2.0), (11, 2.0), 3.8, h=2.6, spacing=5.5, pr=0.12, square=False)
    # ball
    b.ball("White", (6, -4, 1.4), 1.1, seg=(14, 10))
    for rz in (0, PI / 2):
        b.torus("Blue", (6, -4, 1.4), 1.1, 0.12, 16, 4, rx=PI / 2, rz=rz)
    b.torus("Yellow", (6, -4, 1.4), 1.1, 0.12, 16, 4)
    # bench + cooler
    with b.at(T(-hw - 4, 0, 0), R(0, 0, PI / 2)):
        b.bx("Plank", -4, 4, -0.7, 0.7, 1.9, 2.3)
        for sx in (-3.4, 3.4):
            b.bx("WoodDark", sx - 0.3, sx + 0.3, -0.6, 0.6, 0, 1.9)
    b.bx("Red", -hw - 6.5, -hw - 4.6, 6, 7.4, 0, 1.6)
    b.bx("White", -hw - 6.6, -hw - 4.5, 5.9, 7.5, 1.6, 2.0)
    return b


def row_boat():
    b = Builder("RowBoat", AREA)
    L, D = 15.0, 2.6
    n = 14
    outer, inner = [], []
    for i in range(n + 1):
        t = i / n
        y = -L / 2 + t * L
        w = 2.8 * (math.sin(PI * (0.18 + 0.82 * t)) ** 0.7) if t < 1 else 0.12
        w = max(w, 0.12)
        zk = 0.0 + 1.1 * max(0, t - 0.75) ** 2 * 6
        sec = [(-w, D + zk * 0.3), (-0.92 * w, 0.55 * D + zk * 0.5), (-0.55 * w, 0.14 * D + zk * 0.8), (0, zk),
               (0.55 * w, 0.14 * D + zk * 0.8), (0.92 * w, 0.55 * D + zk * 0.5), (w, D + zk * 0.3)]
        outer.append([(x, y, z) for x, z in sec])
        th = min(0.32, w * 0.4)
        inner.append([(x * max(0, (w - th)) / w, y, z + th * (1 if abs(x) < w * 0.6 else 0.6)) for x, z in sec])
    k = len(outer[0])
    verts, faces = [], []
    for i in range(n + 1):
        verts += outer[i] + inner[i][::-1]
    ring = 2 * k
    for i in range(n):
        a, c = i * ring, (i + 1) * ring
        for j in range(ring):
            jj = (j + 1) % ring
            faces.append([a + j, a + jj, c + jj, c + j])
    faces.append(list(range(ring))[::-1])
    faces.append(list(range(n * ring, n * ring + ring)))
    with b.at(T(0, 0, 0.0), R(0.0, 0.08, 0.0)):
        # the hull is painted: lower half Accent, upper White trim drawn on top
        b.mesh("Accent", verts, faces)
        gun = [(o[0][0], o[0][1], o[0][2]) for o in outer]
        b.tube("WoodDark", [(p[0] - 0.05, p[1], p[2] + 0.05) for p in gun], 0.22, 6)
        b.tube("WoodDark", [(-p[0] + 0.05, p[1], p[2] + 0.05) for p in gun], 0.22, 6)
        b.tube("White", [(p[0] * 0.99 - 0.08, p[1], p[2] - 0.55) for p in gun[:-1]], 0.14, 5)
        b.tube("White", [(-p[0] * 0.99 + 0.08, p[1], p[2] - 0.55) for p in gun[:-1]], 0.14, 5)
        b.bx("Plank", -1.9, 1.9, -6.6, -6.0, 0.4, 2.0)
        b.planks(["Plank", "WoodLight"], -1.4, 1.4, -5.6, 4.6, 0.75, t=0.2, bw=0.7, along="y")
        for y in (-3.6, 0.8):
            w = 2.8 * (math.sin(PI * (0.18 + 0.82 * (y + L / 2) / L)) ** 0.7) - 0.25
            b.bx("Plank", -w, w, y - 0.6, y + 0.6, 1.7, 2.05)
        for sx in (-1, 1):
            b.cyl("WoodLight", (sx * 1.15, -4.6, 2.25), (sx * 0.85, 5.6, 2.3), 0.13, 6)
            b.ball("WoodLight", (sx * 1.2, -5.5, 2.24), 1.0, seg=(10, 6), sc=(0.4, 1.2, 0.08))
            b.cyl("Brass", (sx * 2.65, -1.0, 2.5), (sx * 2.65, -1.0, 3.0), 0.12, 6)
    b.cyl("Rope", (0, 7.3, 1.6), (1.0, 9.5, 0.2), 0.12, 5)
    b.tube("Rope", [(1.0 + math.cos(a) * 0.9, 10.2 + math.sin(a) * 0.9, 0.15) for a in [i * TAU / 10 for i in range(11)]], 0.12, 5)
    return b


def boardwalk():
    b = Builder("Boardwalk", AREA)
    L, W = 40.0, 10.0
    for y in (-L / 2 + 1, -L / 2 + 13, L / 2 - 13, L / 2 - 1):
        b.bx("WoodDark", -W / 2, W / 2, y - 0.5, y + 0.5, 0, 0.8)
    for sx in (-1, 1):
        b.bx("WoodDark", sx * (W / 2 - 1) - 0.4, sx * (W / 2 - 1) + 0.4, -L / 2, L / 2, 0.4, 1.0)
    b.planks(["Plank", "Driftwood", "WoodLight"], -W / 2, W / 2, -L / 2, L / 2, 1.5, t=0.5, bw=1.0, along="x")
    for sx in (-1, 1):
        x = sx * (W / 2 + 0.3)
        ys = [-L / 2 + 1 + i * (L - 2) / 4 for i in range(5)]
        for y in ys:
            b.cylz("Driftwood", x, y, 0, 4.4, 0.45, 8)
            b.cylz("WoodDark", x, y, 4.4, 4.7, 0.6, 8)
        for y0, y1 in zip(ys, ys[1:]):
            pts = [(x, lerp(y0, y1, k / 10), 3.8 - math.sin(k / 10 * PI) * 0.9) for k in range(11)]
            b.tube("Rope", pts, 0.14, 6)
    b.lamp("DarkMetal", "WindowGlow", (W / 2 + 0.3, 0, 0), h=8.0)
    b.lamp("DarkMetal", "WindowGlow", (-W / 2 - 0.3, -L / 2 + 10.5, 0), h=8.0)
    b.lamp("DarkMetal", "WindowGlow", (-W / 2 - 0.3, L / 2 - 10.5, 0), h=8.0)
    for k, (x, y) in enumerate(((-3.0, -12.0), (2.6, 7.0), (-1.4, 15.0))):
        b.prism_z(("Coral", "Yellow", "Orange")[k], [(x + math.cos(a) * (0.9 if j % 2 == 0 else 0.38), y + math.sin(a) * (0.9 if j % 2 == 0 else 0.38))
                                                   for j, a in enumerate([PI / 2 + i * PI / 5 for i in range(10)])], 1.5, 1.72)
    return b


def beach_arch():
    b = Builder("BeachArch", AREA)

    def board(col, stripe, x):
        with b.at(T(x, 0, 0)):
            b.ball(col, (0, 0, 9.5), 1.0, seg=(20, 10), sc=(2.6, 0.5, 9.8))
            b.box(stripe, (0, -0.15, 9.5), (0.7, 0.9, 17.0), bev=0)
            b.prism_x(stripe, [(0.0, 3.2), (-1.6, 2.6), (0.0, 5.0)], -0.12, 0.12)
            b.cylz("Concrete", 0, 0, 0, 1.2, 3.0, 12)

    board("Yellow", "Coral", -11.5)
    board("SkyBlue", "White", 11.5)
    # crossbeam sign
    b.bx("WoodDark", -14, 14, -0.9, 0.9, 15.6, 17.0)
    b.bx("Cream", -10.0, 10.0, -1.2, -0.7, 11.2, 15.6)
    b.bx("WoodDark", -10.4, 10.4, -1.25, -0.6, 15.2, 15.7)
    b.bx("WoodDark", -10.4, 10.4, -1.25, -0.6, 10.8, 11.3)
    b.text("Teal", "BEACH", (0, -1.35, 13.4), 3.4, depth=0.5)
    for x in (-8.0, 8.0):
        b.cyl("Rope", (x, -1.4, 15.7), (x, -1.4, 17.2), 0.14, 5)
        for k in range(4):
            b.torus("Rope", (x, 0, 15.9 + k * 0.32), 1.05, 0.12, 10, 4, rx=0, ry=PI / 2 * 0, rz=0)
    # shells and starfish on the beam
    for x, col in ((-12.5, "Coral"), (12.5, "Peach")):
        with b.at(T(x, -1.0, 16.3), R(PI / 2, 0, 0)):
            b.prism_z(col, [(math.cos(a) * (1.4 if j % 2 == 0 else 0.6), math.sin(a) * (1.4 if j % 2 == 0 else 0.6))
                           for j, a in enumerate([PI / 2 + i * PI / 5 for i in range(10)])], -0.2, 0.2)
    with b.at(T(0, -1.0, 17.0), R(PI / 2, 0, 0)):
        b.lathe("Pink", [(0, 0), (1.8, 0.0), (0, 0.3)], c=(0, 0, 0), n=10, a0=0, a1=PI)
        for k in range(6):
            a = PI * (k + 0.5) / 6
            b.box("Peach", (math.cos(a) * 0.9, math.sin(a) * 0.9, 0.2), (1.8, 0.14, 0.12), rz=a, bev=0)
    return b


ASSETS = [beach_house, surf_shack, ice_cream_kiosk, pier, beach_cabanas, shower_station,
          volleyball_court, row_boat, boardwalk, beach_arch]
