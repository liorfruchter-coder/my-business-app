"""Area 9 -- Moon Base: white panelled hulls, grey regolith, purple and cyan light strips."""
import math

from kit import PI, TAU, Builder, R, T, V, catenary

AREA = "MoonBase"
GROUND = (96, 98, 122)


def panel_dome(b, c, r, sc=(1, 1, 1), ribs=12, rings=3, st="MoonWhite", rib="MoonPanel"):
    b.dome(st, c, r, seg=24, rings=8, sc=sc)
    x, y, z = c
    for k in range(ribs):
        a = TAU * k / ribs
        pts = [(x + math.cos(a) * r * sc[0] * 1.01 * math.cos(t), y + math.sin(a) * r * sc[1] * 1.01 * math.cos(t), z + r * sc[2] * 1.01 * math.sin(t))
               for t in [i * PI / 2 / 10 for i in range(10)]]
        b.tube(rib, pts, 0.18 * r / 8 + 0.08, 4)
    for j in range(1, rings + 1):
        t = j * PI / 2 / (rings + 1)
        b.torus(rib, (x, y, z + r * sc[2] * math.sin(t)), r * math.cos(t) * 1.01, 0.16 * r / 8 + 0.08, 32, 4)


def hazard_ring(b, c, r_out, r_in, z, n=24):
    for k in range(n):
        a0, a1 = TAU * k / n, TAU * (k + 1) / n
        st = "Yellow" if k % 2 else "Black"
        b.mesh(st, [(c[0] + math.cos(a0) * r_in, c[1] + math.sin(a0) * r_in, z), (c[0] + math.cos(a0) * r_out, c[1] + math.sin(a0) * r_out, z),
                    (c[0] + math.cos(a1) * r_out, c[1] + math.sin(a1) * r_out, z), (c[0] + math.cos(a1) * r_in, c[1] + math.sin(a1) * r_in, z)],
               [[0, 1, 2, 3]])


def tunnel(b, p0, p1, r=3.2, ribs=True, windows=True):
    p0, p1 = V(p0), V(p1)
    b.cyl("MoonWhite", p0, p1, r, 14)
    d = p1 - p0
    L = d.length
    if ribs:
        n = max(2, int(L / 4.0))
        for k in range(n + 1):
            p = p0.lerp(p1, k / n)
            q = V((0, 0, 1)).rotation_difference(d.normalized())
            b.cyl("MoonPanel", p - d.normalized() * 0.3, p + d.normalized() * 0.3, r + 0.3, 14)
    if windows:
        side = V((-d.y, d.x, 0)).normalized()
        n = max(1, int(L / 4.0))
        for k in range(n):
            p = p0.lerp(p1, (k + 0.5) / n)
            for s in (-1, 1):
                b.cyl("NeonCyan", p + side * s * (r - 0.1) + V((0, 0, 0.6)), p + side * s * (r + 0.12) + V((0, 0, 0.6)), 0.6, 10)


def command_center():
    b = Builder("CommandCenter", AREA)
    # regolith pad
    b.lathe("Grey", [(0, 0), (30, 0), (30, 0.6), (0, 0.6)], n=32)
    hazard_ring(b, (0, 0), 29.5, 28.0, 0.62, n=40)
    # base drum with a window band
    b.lathe("MoonDark", [(0, 0.6), (17.0, 0.6), (17.0, 7.0), (0, 7.0)], n=28)
    b.ring("NeonPurple", (0, 0, 0), 17.15, 16.8, 4.6, 5.2, n=28)
    for k in range(18):
        a = TAU * k / 18
        b.box("GlassDark", (math.cos(a) * 17.05, math.sin(a) * 17.05, 3.0), (2.4, 0.3, 2.0), rz=a + PI / 2, bev=0)
    b.ring("MoonPanel", (0, 0, 0), 17.6, 15.0, 7.0, 7.8, n=28)
    panel_dome(b, (0, 0, 7.8), 15.6, sc=(1, 1, 0.82), ribs=14, rings=3)
    # top observation cupola + mast + dish
    b.lathe("MoonPanel", [(0, 0), (4.0, 0), (4.0, 1.2), (0, 1.2)], c=(0, 0, 20.4), n=16)
    b.lathe("Glass", [(0, 0), (3.6, 0), (3.6, 1.6), (0, 1.6)], c=(0, 0, 21.6), n=16)
    b.dome("MoonWhite", (0, 0, 23.2), 3.8, seg=16, rings=4, sc=(1, 1, 0.6))
    b.cylz("MoonDark", 0, 0, 25.4, 34.0, 0.35, 8)
    for z in (28.0, 31.0):
        b.cyl("MoonDark", (-2.4, 0, z), (2.4, 0, z), 0.14, 5)
    b.ball("NeonRed", (0, 0, 34.3), 0.4, seg=(6, 4))
    with b.at(T(2.6, 0, 30.5), R(0, -0.7, 0.3)):
        b.lathe("MoonWhite", [(0, 0), (3.2, 0.9), (3.4, 1.1), (0.4, 0.5), (0, 0.5)], n=16)
        b.cylz("MoonDark", 0, 0, 0.5, 2.4, 0.12, 5)
        b.ball("NeonCyan", (0, 0, 2.5), 0.25, seg=(6, 4))
    # front airlock tunnel + door
    tunnel(b, (0, -16.0, 4.0), (0, -27.0, 4.0), r=3.4)
    b.cyl("MoonPanel", (0, -27.0, 4.0), (0, -28.0, 4.0), 4.0, 6)
    b.cyl("MoonDark", (0, -27.8, 4.0), (0, -28.2, 4.0), 2.6, 6)
    b.box("NeonPurple", (0, -28.25, 4.0), (0.3, 0.1, 4.4), bev=0)
    b.lathe("MoonPanel", [(0, 0), (4.0, 0), (4.0, 0.6), (0, 0.6)], c=(0, -28, 0.6), n=6)
    b.text("NeonPurple", "LUNAR HQ", (0, -17.25, 9.3), 1.6, depth=0.2, font="black", rz=0.0)
    # side pods with tunnels
    for sx in (-1, 1):
        cx = sx * 25.0
        b.lathe("MoonDark", [(0, 0.6), (6.5, 0.6), (6.5, 3.6), (0, 3.6)], c=(cx, 6, 0), n=20)
        panel_dome(b, (cx, 6, 3.6), 6.2, sc=(1, 1, 0.9), ribs=8, rings=2)
        b.ring("NeonCyan", (cx, 6, 0), 6.6, 6.4, 2.0, 2.4, n=20)
        tunnel(b, (sx * 16.6, 3.0, 3.2), (sx * 19.0, 5.0, 3.2), r=2.6, windows=False)
    # landing lights round the pad
    for k in range(12):
        a = TAU * k / 12
        b.cylz("MoonDark", math.cos(a) * 26, math.sin(a) * 26, 0.6, 1.4, 0.45, 8)
        b.ball("NeonPurple" if k % 2 else "NeonCyan", (math.cos(a) * 26, math.sin(a) * 26, 1.6), 0.35, seg=(6, 4))
    return b


def launch_pad():
    b = Builder("LaunchPad", AREA)
    b.lathe("Concrete", [(0, 0), (22.0, 0), (21.0, 2.4), (0, 2.4)], n=8)
    b.lathe("Grey", [(0, 2.4), (14.0, 2.4), (14.0, 2.6), (0, 2.6)], n=8)
    hazard_ring(b, (0, 0), 13.8, 12.4, 2.62, n=32)
    # flame trench
    b.bx("Charcoal", -3.5, 3.5, -22.5, -6.0, 1.2, 2.45, bev=0)
    b.bx("Black", -2.8, 2.8, -22.6, -6.0, 1.2, 2.47, bev=0)
    b.bx("Charcoal", -5.0, 5.0, -5.0, 5.0, 2.4, 3.2)
    b.cylz("Ember", 0, 0, 3.2, 3.25, 2.8, 16)
    for k in range(4):
        a = TAU * k / 4 + PI / 4
        with b.at(T(math.cos(a) * 6.5, math.sin(a) * 6.5, 2.6), R(0, 0, a)):
            b.bx("MoonDark", -1.2, 1.2, -1.0, 1.0, 0, 3.2)
            b.bx("Orange", -2.4, -1.0, -0.5, 0.5, 2.2, 3.0)
    # gantry tower (lattice) beside the pad
    GX, GY, H = 14.0, 0.0, 62.0
    h = 3.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cylz("Orange", GX + sx * h, GY + sy * h, 2.4, H, 0.4, 6)
    z = 2.4
    k = 0
    while z + 4.0 <= H:
        for rz in (0, PI / 2, PI, -PI / 2):
            with b.at(T(GX, GY, 0), R(0, 0, rz)):
                b.cyl("Orange" if k % 2 else "MoonDark", (-h, -h, z), (h, -h, z + 4.0), 0.16, 4)
                b.cyl("MoonDark", (-h, -h, z + 4.0), (h, -h, z + 4.0), 0.18, 4)
        z += 4.0
        k += 1
    b.bx("MoonDark", GX - 4.0, GX + 4.0, GY - 4.0, GY + 4.0, H, H + 1.0)
    b.cylz("MoonDark", GX, GY, H + 1.0, H + 8.0, 0.25, 6)
    b.ball("NeonRed", (GX, GY, H + 8.2), 0.4, seg=(6, 4))
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.ball("NeonRed", (GX + sx * 3.8, GY + sy * 3.8, H + 1.3), 0.3, seg=(6, 4))
    # elevator cage + service arms reaching toward the pad
    b.bx("Glass", GX - 1.8, GX + 1.8, GY - 1.8, GY + 1.8, 20.0, 24.0)
    b.bx("MoonWhite", GX - 2.0, GX + 2.0, GY - 2.0, GY + 2.0, 24.0, 24.4)
    for z, L in ((28.0, 10.0), (46.0, 9.0)):
        b.bx("MoonDark", GX - 3.0 - L, GX - 3.0, -1.4, 1.4, z, z + 0.6)
        b.rail("MoonDark", "Orange", (GX - 3.0 - L, -1.3), (GX - 3.0, -1.3), z + 0.6, h=2.0, spacing=2.5, pr=0.1)
        b.rail("MoonDark", "Orange", (GX - 3.0 - L, 1.3), (GX - 3.0, 1.3), z + 0.6, h=2.0, spacing=2.5, pr=0.1)
        b.bx("MoonWhite", GX - 3.6 - L, GX - 2.6 - L, -2.0, 2.0, z - 0.6, z + 2.8)
        b.cyl("MoonDark", (GX - 3.0, 1.0, z - 4.0), (GX - 3.0 - L * 0.6, 1.0, z), 0.2, 5)
    b.text("NeonCyan", "PAD 39", (0, -20.9, 1.2), 2.0, depth=0.2, upright=True, rz=0.0, font="black")
    return b


def observatory():
    b = Builder("Observatory", AREA)
    b.lathe("Grey", [(0, 0), (14, 0), (14, 0.5), (0, 0.5)], n=24)
    b.lathe("MoonWhite", [(0, 0.5), (9.0, 0.5), (9.0, 14.0), (0, 14.0)], n=24)
    for z in (5.0, 9.5):
        b.ring("MoonPanel", (0, 0, 0), 9.15, 8.9, z, z + 0.5, n=24)
    b.ring("NeonPurple", (0, 0, 0), 9.15, 8.95, 13.2, 13.6, n=24)
    b.ring("MoonPanel", (0, 0, 0), 9.6, 8.5, 14.0, 14.8, n=24)
    # dome with an open slit
    b.dome("MoonPanel", (0, 0, 14.8), 9.0, seg=24, rings=6)
    b.bx("Black", -1.8, 1.8, -9.2, 2.0, 15.0, 24.0, ry=0.0, bev=0)
    b.box("Black", (0, -4.5, 22.6), (3.6, 9.0, 1.5), rx=-0.55, bev=0)
    for sx in (-1, 1):
        pts = [(sx * 2.0, -9.0 * math.cos(t), 14.8 + 9.0 * math.sin(t)) for t in [i * PI / 2 / 8 for i in range(9)]]
        b.tube("MoonDark", pts, 0.3, 4)
    # telescope poking out
    with b.at(T(0, -1.0, 17.0), R(-0.7, 0, 0)):
        b.cylz("MoonDark", 0, 0, 0, 12.0, 1.5, 12)
        b.cylz("MoonWhite", 0, 0, 7.0, 12.4, 1.8, 12)
        b.cylz("Glass", 0, 0, 12.4, 12.6, 1.5, 12)
        b.ring("NeonCyan", (0, 0, 0), 1.9, 1.6, 12.4, 12.7, n=12)
    # catwalk with rail + door + ladder
    b.ring("MoonDark", (0, 0, 0), 11.2, 9.0, 10.0, 10.5, n=24)
    for k in range(24):
        a = TAU * k / 24
        b.cylz("MoonDark", math.cos(a) * 11.0, math.sin(a) * 11.0, 10.5, 12.6, 0.1, 4)
    b.torus("Orange", (0, 0, 12.6), 11.0, 0.14, 32, 4)
    b.door("MoonDark", "MoonPanel", (0, -9.1, 0.5), 3.2, 5.4)
    b.box("NeonPurple", (0, -9.6, 6.3), (3.4, 0.1, 0.25), bev=0)
    for sx in (-0.5, 0.5):
        b.cylz("MoonDark", 9.8 + sx * 0.0, sx * 1.2, 0.5, 10.0, 0.08, 4)
    for k in range(12):
        b.cyl("MoonDark", (9.8, -0.6, 1.2 + k * 0.75), (9.8, 0.6, 1.2 + k * 0.75), 0.06, 3)
    return b


def hab_module():
    b = Builder("HabModule", AREA)
    L, Rr = 34.0, 6.0
    ZC = 8.0
    b.cyl("MoonWhite", (-L / 2, 0, ZC), (L / 2, 0, ZC), Rr, 20)
    for sx in (-1, 1):
        with b.at(T(sx * L / 2, 0, ZC), R(0, sx * PI / 2, 0)):
            b.dome("MoonWhite", (0, 0, 0), Rr, seg=20, rings=4, sc=(1, 1, 0.55))
    for k in range(7):
        x = -L / 2 + 2 + k * (L - 4) / 6
        b.cyl("MoonPanel", (x - 0.4, 0, ZC), (x + 0.4, 0, ZC), Rr + 0.3, 20)
    for k in range(6):
        x = -L / 2 + 2 + (k + 0.5) * (L - 4) / 6
        b.cyl("GlassDark", (x, -Rr + 0.2, ZC + 1.0), (x, -Rr - 0.15, ZC + 1.0), 1.0, 12)
        b.torus("NeonCyan", (x, -Rr - 0.1, ZC + 1.0), 1.05, 0.12, 12, 4, rx=PI / 2)
    b.bx("NeonPurple", -L / 2 + 1, L / 2 - 1, -Rr - 0.05, -Rr + 0.3, ZC - 2.6, ZC - 2.2, bev=0)
    # legs
    for x in (-L / 2 + 4, 0, L / 2 - 4):
        for sy in (-1, 1):
            b.cyl("MoonDark", (x, sy * 3.0, ZC - 4.0), (x, sy * 6.0, 0.4), 0.45, 6)
            b.cylz("MoonDark", x, sy * 6.0, 0, 0.4, 1.2, 8)
    # airlock on the end
    with b.at(T(L / 2 + 3.0, 0, ZC), R(0, PI / 2, 0)):
        b.cylz("MoonPanel", 0, 0, 0, 3.0, 3.0, 6)
        b.cylz("MoonDark", 0, 0, 3.0, 3.4, 2.2, 6)
    b.box("NeonPurple", (L / 2 + 6.45, 0, ZC), (0.1, 0.3, 3.4), bev=0)
    # solar wings on a mast + radiator fins
    b.cylz("MoonDark", 0, 0, ZC + Rr, ZC + Rr + 5.0, 0.3, 6)
    b.cyl("MoonDark", (-14, 0, ZC + Rr + 5.0), (14, 0, ZC + Rr + 5.0), 0.2, 5)
    for sx in (-1, 1):
        with b.at(T(sx * 8.5, 0, ZC + Rr + 5.0), R(0.5, 0, 0)):
            b.bx("Solar", -5.5, 5.5, -3.0, 3.0, -0.1, 0.1)
            for k in range(1, 6):
                b.bx("Metal", -5.5 + k * 11 / 6 - 0.05, -5.5 + k * 11 / 6 + 0.05, -3.0, 3.0, 0.1, 0.16, bev=0)
            b.bx("Metal", -5.5, 5.5, -0.05, 0.05, 0.1, 0.16, bev=0)
    for k in range(4):
        x = -10 + k * 6.6
        b.bx("White", x - 1.4, x + 1.4, Rr - 0.2, Rr + 3.6, ZC + 1.0, ZC + 1.2)
    b.text("MoonDark", "HAB-02", (6.0, -Rr - 0.2, ZC + 3.6), 1.1, depth=0.1, font="black")
    return b


def solar_array():
    b = Builder("SolarArray", AREA)
    for row in range(2):
        y = -4.0 + row * 9.0
        for k in range(4):
            x = -13.5 + k * 9.0
            b.cylz("MoonDark", x, y, 0, 3.6, 0.25, 6)
            b.cylz("MoonDark", x, y, 0, 0.3, 0.9, 8)
            with b.at(T(x, y, 4.0), R(0.55, 0, 0)):
                b.bx("MoonWhite", -4.3, 4.3, -3.2, 3.2, -0.25, 0.0)
                b.bx("Solar", -4.1, 4.1, -3.0, 3.0, 0.0, 0.12, bev=0)
                for j in range(1, 5):
                    b.bx("Metal", -4.1 + j * 8.2 / 5 - 0.04, -4.1 + j * 8.2 / 5 + 0.04, -3.0, 3.0, 0.12, 0.16, bev=0)
                for j in range(1, 3):
                    b.bx("Metal", -4.1, 4.1, -3.0 + j * 2.0 - 0.04, -3.0 + j * 2.0 + 0.04, 0.12, 0.16, bev=0)
    b.bx("MoonWhite", 17.0, 20.0, -2.0, 2.0, 0, 3.6)
    b.bx("NeonGreen", 17.2, 18.0, -2.05, -2.0, 2.6, 3.0, bev=0)
    b.bx("Orange", 17.0, 20.0, -2.1, 2.1, 3.6, 3.9, bev=0)
    b.tube("Black", [(13.5, -4.0, 0.2), (15.5, -3.0, 0.2), (17.0, -1.0, 0.4)], 0.18, 5)
    b.tube("Black", [(13.5, 5.0, 0.2), (15.5, 3.0, 0.2), (17.0, 1.0, 0.4)], 0.18, 5)
    return b


def airlock_tunnel():
    b = Builder("AirlockTunnel", AREA)
    L = 30.0
    tunnel(b, (0, -L / 2, 4.0), (0, L / 2, 4.0), r=3.4)
    for y in (-L / 2, L / 2):
        b.cyl("MoonPanel", (0, y - 0.6, 4.0), (0, y + 0.6, 4.0), 4.2, 6)
    b.bx("Grey", -3.0, 3.0, -L / 2, L / 2, 0, 0.8)
    for y in (-8, 0, 8):
        b.bx("MoonDark", -2.6, 2.6, y - 0.5, y + 0.5, 0.8, 1.6)
    b.bx("NeonPurple", -3.45, -3.3, -L / 2 + 1, L / 2 - 1, 2.4, 2.7, bev=0)
    b.bx("NeonPurple", 3.3, 3.45, -L / 2 + 1, L / 2 - 1, 2.4, 2.7, bev=0)
    return b


def lunar_lander():
    b = Builder("LunarLander", AREA)
    b.lathe("Grey", [(0, 0), (12, 0), (12, 0.3), (0, 0.3)], n=24)
    hazard_ring(b, (0, 0), 11.6, 10.6, 0.32, n=24)
    b.text("White", "H", (0, -7.0, 0.32), 3.0, depth=0.05, upright=False)
    Z = 5.5
    # descent stage in gold foil
    b.lathe("Gold", [(0, Z), (4.2, Z), (4.2, Z + 3.4), (0, Z + 3.4)], n=8)
    b.cylz("DarkMetal", 0, 0, Z - 1.6, Z, 1.2, 10, r2=0.8)
    for k in range(4):
        a = TAU * k / 4 + PI / 4
        fx, fy = math.cos(a) * 8.0, math.sin(a) * 8.0
        b.cyl("Metal", (math.cos(a) * 3.8, math.sin(a) * 3.8, Z + 2.6), (fx, fy, 1.0), 0.32, 6)
        b.cyl("Metal", (math.cos(a) * 3.6, math.sin(a) * 3.6, Z + 0.2), (fx * 0.8, fy * 0.8, 2.2), 0.18, 5)
        b.lathe("Metal", [(0, 0.3), (1.2, 0.3), (1.0, 0.9), (0, 0.9)], c=(fx, fy, 0), n=10)
    # ascent stage: angular cabin
    b.mesh("MoonPanel", [(-3.2, -2.6, Z + 3.4), (3.2, -2.6, Z + 3.4), (3.2, 2.6, Z + 3.4), (-3.2, 2.6, Z + 3.4),
                         (-2.4, -3.2, Z + 6.6), (2.4, -3.2, Z + 6.6), (2.8, 2.2, Z + 7.4), (-2.8, 2.2, Z + 7.4)],
           [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
    for sx in (-1, 1):
        b.mesh("Black", [(sx * 0.4, -3.1, Z + 5.0), (sx * 1.9, -3.0, Z + 5.0), (sx * 1.7, -3.15, Z + 6.2), (sx * 0.4, -3.2, Z + 6.2)],
               [[0, 1, 2, 3], [3, 2, 1, 0]])
    b.bx("MoonDark", -0.8, 0.8, -3.5, -2.8, Z + 3.4, Z + 5.0)
    b.cylz("MoonDark", 1.6, 1.4, Z + 7.2, Z + 10.0, 0.12, 4)
    with b.at(T(1.6, 1.4, Z + 10.0), R(0.6, 0.3, 0)):
        b.lathe("MoonWhite", [(0, 0), (1.4, 0.4), (1.5, 0.5), (0.2, 0.2), (0, 0.2)], n=12)
    b.bx("Gold", -1.8, 1.8, 2.4, 3.4, Z + 3.6, Z + 6.0)
    # ladder down one leg + a flag
    for k in range(5):
        b.cyl("Metal", (-0.7, -4.4 - k * 0.5, Z + 1.8 - k * 0.9), (0.7, -4.4 - k * 0.5, Z + 1.8 - k * 0.9), 0.08, 4)
    b.cylz("White", 8.0, -4.0, 0.3, 8.0, 0.1, 5)
    b.cyl("White", (8.0, -4.0, 7.9), (10.6, -4.0, 7.9), 0.08, 4)
    b.bx("Purple", 8.1, 10.6, -4.05, -3.95, 6.0, 7.9, bev=0)
    b.ball("Yellow", (9.35, -4.1, 6.95), 0.45, seg=(8, 6), sc=(1, 0.2, 1))
    return b


def comm_tower():
    b = Builder("CommTower", AREA)
    H = 48.0
    b.bx("Concrete", -4, 4, -4, 4, 0, 1.0)
    corners = [(math.cos(TAU * k / 3 + PI / 2) * 2.6, math.sin(TAU * k / 3 + PI / 2) * 2.6) for k in range(3)]
    for (x, y) in corners:
        b.cyl("MoonWhite", (x * 1.4, y * 1.4, 1.0), (x * 0.5, y * 0.5, H), 0.3, 6)
    z = 1.0
    k = 0
    while z < H - 3:
        f0 = 1.4 - 0.9 * (z - 1.0) / (H - 1.0)
        f1 = 1.4 - 0.9 * (z + 3.0 - 1.0) / (H - 1.0)
        for i in range(3):
            (x0, y0), (x1, y1) = corners[i], corners[(i + 1) % 3]
            b.cyl("Orange" if (k // 3) % 2 else "MoonWhite", (x0 * f0, y0 * f0, z), (x1 * f1, y1 * f1, z + 3.0), 0.1, 4)
            b.cyl("MoonDark", (x0 * f1, y0 * f1, z + 3.0), (x1 * f1, y1 * f1, z + 3.0), 0.1, 4)
        z += 3.0
        k += 1
    for zz, a in ((22.0, 0.3), (34.0, 2.6)):
        with b.at(T(math.cos(a) * 2.6, math.sin(a) * 2.6, zz), R(0, 0, a), R(0, PI / 2 - 0.25, 0)):
            b.lathe("MoonWhite", [(0, 0), (3.4, 1.0), (3.6, 1.2), (0.4, 0.4), (0, 0.4)], n=16)
            b.cylz("MoonDark", 0, 0, 0.4, 2.6, 0.1, 4)
    b.cylz("MoonDark", 0, 0, H, H + 6, 0.2, 5)
    for zz in (H * 0.33, H * 0.66, H + 6.2):
        b.ball("NeonRed", (0, 0, zz), 0.4, seg=(6, 4))
    for (x, y) in corners:
        b.cyl("MoonDark", (x * 0.55, y * 0.55, H * 0.8), (x * 7.0, y * 7.0, 0.3), 0.05, 3)
        b.cylz("MoonDark", x * 7.0, y * 7.0, 0, 0.6, 0.5, 6)
    return b


def cargo_pods():
    b = Builder("CargoPods", AREA)
    spots = ((-6, -2, 0, 0.1), (0, -2.6, 0, -0.05), (-3, -2.2, 5.2, 0.15), (6.5, 0, 0, 0.3))
    for (x, y, z, rz) in spots:
        with b.at(T(x, y, z), R(0, 0, rz)):
            b.bx("MoonWhite", -2.6, 2.6, -2.6, 2.6, 0, 5.2)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    b.bx("MoonDark", sx * 2.6 - 0.45, sx * 2.6 + 0.45, sy * 2.6 - 0.45, sy * 2.6 + 0.45, 0, 5.2)
            b.bx("Orange", -2.65, 2.65, -2.65, 2.65, 2.2, 3.0, bev=0)
            b.cyl("NeonCyan", (0, -2.6, 4.2), (0, -2.75, 4.2), 0.5, 6)
    # fuel canisters
    for k in range(3):
        x = -6 + k * 2.4
        b.cylz("Orange", x, 6, 0, 4.4, 1.0, 12)
        b.lathe("MoonDark", [(0, 4.4), (1.0, 4.4), (0.5, 5.0), (0.5, 5.4), (0, 5.4)], c=(x, 6, 0), n=12)
        b.ring("Black", (x, 6, 0), 1.05, 0.95, 1.0, 1.4, n=12)
    # little loader robot
    with b.at(T(9.0, 7.0, 0)):
        for sy in (-1.2, 1.2):
            b.bx("MoonDark", -1.6, 1.6, sy - 0.4, sy + 0.4, 0, 1.0)
        b.bx("Yellow", -1.4, 1.4, -1.0, 1.0, 1.0, 3.0)
        b.bx("MoonDark", 1.4, 3.2, -0.3, 0.3, 2.0, 2.4)
        b.bx("MoonDark", 3.0, 3.4, -1.0, 1.0, 0.4, 2.4)
        b.box("Glass", (0, -0.6, 3.6), (1.6, 0.8, 1.2))
        b.ball("NeonCyan", (0, -1.05, 3.6), 0.2, seg=(6, 4))
    return b


def fuel_tanks():
    b = Builder("FuelTanks", AREA)
    b.bx("Concrete", -14, 14, -6, 6, 0, 0.8)
    for k, x in enumerate((-8.0, 1.0, 10.0)):
        r = 4.2 if k != 1 else 5.0
        zc = 0.8 + 3.0 + r
        for j in range(4):
            a = TAU * j / 4 + PI / 4
            b.cyl("MoonDark", (x + math.cos(a) * r * 0.75, math.sin(a) * r * 0.75, 0.8), (x + math.cos(a) * r * 0.6, math.sin(a) * r * 0.6, zc - r * 0.3), 0.3, 6)
        b.ball("MoonWhite", (x, 0, zc), r, seg=(18, 12))
        b.torus("Orange", (x, 0, zc), r * 1.0, 0.25, 24, 4)
        b.torus("MoonPanel", (x, 0, zc + r * 0.55), r * 0.84, 0.15, 24, 4)
        b.text("MoonDark", ("LOX", "LH2", "N2")[k], (x, -r * 0.98, zc + 1.2), 1.0, depth=0.1, font="black")
        b.cylz("MoonDark", x, 0, zc + r, zc + r + 1.2, 0.45, 8)
    # pipe run + catwalk between tanks
    b.tube("Metal", [(-8, 0, 12.0), (-4, 0, 13.0), (1, 0, 13.6), (6, 0, 13.0), (10, 0, 12.0)], 0.35, 6)
    b.tube("Metal", [(-14, -4, 1.4), (-8, -4, 1.4), (1, -4, 1.4), (10, -4, 1.4), (14, -4, 1.4)], 0.3, 6)
    for x in (-11, -4, 5.5, 13):
        b.cylz("MoonDark", x, -4, 0.8, 1.4, 0.25, 5)
    b.bx("MoonDark", -12, 12, 4.2, 6.0, 7.0, 7.4)
    b.rail("MoonDark", "Yellow", (-12, 5.9), (12, 5.9), 7.4, h=2.0, spacing=3.0, pr=0.1)
    for x in (-12, 12):
        b.cylz("MoonDark", x, 5.1, 0.8, 7.0, 0.2, 5)
    for k in range(12):
        x = -13.8 + k * 2.4
        b.bx("Yellow" if k % 2 else "Black", x - 1.2, x + 1.2, -6.1, -5.9, 0.0, 0.8, bev=0)
    return b


def moon_gate():
    b = Builder("MoonGate", AREA)
    # hexagonal portal frame
    R_out, R_in, D = 13.0, 10.0, 5.0
    pts_o = [(math.cos(TAU * k / 6) * R_out, math.sin(TAU * k / 6) * R_out + R_out * 0.866) for k in range(6)]
    pts_i = [(math.cos(TAU * k / 6) * R_in, math.sin(TAU * k / 6) * R_in + R_out * 0.866) for k in range(6)]
    for k in range(6):
        if k == 4:
            continue
        a, c = pts_o[k], pts_o[(k + 1) % 6]
        ai, ci = pts_i[k], pts_i[(k + 1) % 6]
        b.prism_y("MoonWhite", [a, c, ci, ai], -D / 2, D / 2)
        b.cyl("NeonPurple", (a[0], -D / 2 - 0.1, a[1]), (c[0], -D / 2 - 0.1, c[1]), 0.2, 4)
    # feet
    for sx in (-1, 1):
        b.bx("MoonDark", sx * 7.6 - 2.8, sx * 7.6 + 2.8, -3.6, 3.6, 0, 1.6)
        b.ball("NeonCyan", (sx * 7.6, -3.7, 0.8), 0.4, seg=(6, 4))
    # inner edge glow strips
    for k in range(6):
        if k == 4:
            continue
        ai, ci = V((pts_i[k][0], 0, pts_i[k][1])), V((pts_i[(k + 1) % 6][0], 0, pts_i[(k + 1) % 6][1]))
        b.cyl("NeonCyan", ai + V((0, -D / 2 - 0.15, 0)), ci + V((0, -D / 2 - 0.15, 0)), 0.18, 4)
    b.bx("MoonDark", -7.5, 7.5, -2.9, -2.5, 22.6, 25.6)
    b.text("NeonPurple", "MOON BASE", (0, -2.95, 24.1), 1.8, depth=0.2, font="black")
    for sx in (-1, 1):
        b.cylz("MoonDark", sx * 6.0, 0, 24.6, 30.0, 0.15, 5)
        b.ball("NeonRed", (sx * 6.0, 0, 30.2), 0.35, seg=(6, 4))
    return b


ASSETS = [command_center, launch_pad, observatory, hab_module, solar_array, airlock_tunnel, lunar_lander,
          comm_tower, cargo_pods, fuel_tanks, moon_gate]
