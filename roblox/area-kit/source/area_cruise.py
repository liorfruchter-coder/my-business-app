"""Area 6 -- Cruise Ship Harbor: navy and white steel, red funnels, yellow cranes, concrete quays."""
import math

from kit import PI, TAU, Builder, R, T, V, catenary

AREA = "CruiseShip"
GROUND = (150, 196, 222)


def hull_halfwidth(t, beam, bow_len=0.28):
    """t = 0 at the stern, 1 at the bow."""
    if t > 1 - bow_len:
        u = (1 - t) / bow_len
        return beam * max(0.02, math.sin(u * PI / 2) ** 0.75)
    if t < 0.05:
        return beam * (0.92 + 0.08 * t / 0.05)
    return beam


def cruise_ship():
    b = Builder("CruiseShip", AREA)
    L, BEAM = 170.0, 16.0
    n = 34
    # hull, bow toward -Y; sections from stern (y = +L/2) to bow (y = -L/2)
    def section(t, z0, z1, grow=0.0, keel_lift=True):
        hw = hull_halfwidth(t, BEAM) + grow
        y = L / 2 - t * L
        rake = max(0.0, t - 0.86) / 0.14
        pts = []
        prof = [(-1.0, 1.0), (-1.0, 0.45), (-0.9, 0.18), (-0.55, 0.04), (0.0, 0.0), (0.55, 0.04), (0.9, 0.18), (1.0, 0.45), (1.0, 1.0)]
        for px, pz in prof:
            z = z0 + (z1 - z0) * pz
            zz = z + (rake * 5.0 * (1 - pz) if keel_lift else 0)
            yy = y - rake * 6.0 * (pz - 0.2) if pz > 0.2 else y
            pts.append((px * hw, yy, max(zz, z0)))
        return pts
    rings_lo, rings_hi = [], []
    for i in range(n + 1):
        t = i / n
        lo = section(t, 0.0, 10.5)
        rings_lo.append(lo)
        hw = hull_halfwidth(t, BEAM)
        y = L / 2 - t * L
        rake = max(0.0, t - 0.86) / 0.14
        sheer = 18.0 + 3.0 * rake
        yy = y - rake * 6.0
        rings_hi.append([(-hw, yy - 0.0, 10.5), (-hw, yy, sheer), (hw, yy, sheer), (hw, yy, 10.5)])
    b.loft("Navy", rings_lo, cap0=True, cap1=False, closed=True)
    b.loft("White", rings_hi, cap0=True, cap1=True, closed=True)
    # red boot stripe + white sheer line
    stripe = []
    for i in range(n + 1):
        t = i / n
        hw = hull_halfwidth(t, BEAM) + 0.15
        y = L / 2 - t * L
        stripe.append([(-hw, y, 3.4), (-hw, y, 4.8), (hw, y, 4.8), (hw, y, 3.4)])
    b.loft("Red", stripe[:-3], cap0=True, cap1=True, closed=True)
    # portholes along the white band
    for sx in (-1, 1):
        for k in range(30):
            t = 0.08 + k * 0.024
            y = L / 2 - t * L
            hw = hull_halfwidth(t, BEAM)
            b.cyl("GlassDark", (sx * (hw - 0.1), y, 14.0), (sx * (hw + 0.15), y, 14.0), 0.55, 8)
        # anchor + hawse pipe at the bow
        t = 0.9
        hw = hull_halfwidth(t, BEAM)
        y = L / 2 - t * L
        with b.at(T(sx * (hw + 0.3), y - 3.0, 13.0), R(0, 0, sx * 0.35)):
            b.cyl("Black", (0, 0, 1.2), (0, 0, 3.4), 0.6, 8)
            b.box("Black", (0, 0, 0.0), (0.6, 0.6, 3.0), bev=0)
            b.box("Black", (0, 0, -1.4), (3.2, 0.6, 0.6), bev=0)
            for sx2 in (-1, 1):
                b.prism_y("Black", [(sx2 * 1.6, -1.1), (sx2 * 2.3, -0.4), (sx2 * 1.6, -1.7)], -0.3, 0.3)
    b.text("Navy", "OCEAN QUEEN", (0, L / 2 + 0.2, 15.2), 2.4, depth=0.3, rz=PI, font="serif")
    # superstructure decks (bow end rounded by a half-cylinder)
    decks = [(18.0, 23.0, 14.6, -58, 72), (23.0, 28.0, 14.0, -52, 70), (28.0, 33.0, 13.4, -46, 66), (33.0, 38.0, 12.0, -38, 56),
             (38.0, 43.0, 9.0, -30, 10)]
    for k, (z0, z1, hw, y0, y1) in enumerate(decks):
        b.bx("White", -hw, hw, y0, y1, z0, z1)
        b.cylz("White", 0, y0, z0, z1, hw, 20)
        b.bx("White", -hw - 0.6, hw + 0.6, y0, y1 + 0.6, z1 - 0.25, z1 + 0.25)
        # window band + balcony fins on the long sides
        for sx in (-1, 1):
            b.bx("GlassDark", sx * hw - 0.15, sx * hw + 0.15, y0 + 1, y1 - 1, z0 + 1.6, z1 - 1.0, bev=0)
            if k < 4:
                m = int((y1 - y0) / 3.2)
                for i in range(m + 1):
                    y = y0 + 1 + i * (y1 - y0 - 2) / m
                    b.bx("White", sx * (hw + 0.6) - 0.6, sx * (hw + 0.6) + 0.6, y - 0.12, y + 0.12, z0, z1 - 0.2, bev=0)
                b.bx("Glass", sx * (hw + 1.1) - 0.08, sx * (hw + 1.1) + 0.08, y0 + 1, y1 - 1, z0 + 0.3, z0 + 1.6, bev=0)
                b.bx("White", sx * (hw + 0.6) - 0.6, sx * (hw + 0.6) + 0.6, y0 + 1, y1 - 1, z0, z0 + 0.3, bev=0)
        # front curve windows
        for j in range(9):
            a = PI + PI * (j + 0.5) / 9
            b.box("GlassDark", (math.cos(a) * hw * 1.002, y0 + math.sin(a) * hw * 1.002, (z0 + z1) / 2 + 0.3), (hw * 0.32, 0.25, z1 - z0 - 2.4), rz=a + PI / 2, bev=0)
    # bridge wings + wraparound bridge windows
    BZ = 38.0
    b.bx("White", -16.5, 16.5, -27.0, -21.0, BZ, BZ + 5.0)
    b.bx("GlassDark", -16.6, 16.6, -27.2, -26.9, BZ + 1.8, BZ + 4.2, bev=0)
    b.bx("White", -9.4, 9.4, -30.2, 8.0, 43.0, 43.6)
    # radar mast
    b.cylz("White", 0, -18.0, 43.6, 52.0, 0.6, 8)
    b.bx("White", -4, 4, -18.6, -17.4, 50.0, 50.6)
    b.cyl("DarkMetal", (-2.6, -18.0, 52.4), (2.6, -18.0, 52.4), 0.25, 6)
    b.bx("DarkMetal", -2.4, 2.4, -18.3, -17.7, 53.0, 53.5, rz=0.4)
    b.ball("NeonWhite", (0, -18.0, 52.6), 0.35, seg=(6, 4))
    # funnels
    for y in (34.0, 48.0):
        with b.at(T(0, y, 38.0)):
            b.lathe("Red", [(0, 0), (4.6, 0), (4.4, 9.0), (4.0, 12.0), (0, 12.0)], n=14, sc=(0.7, 1.3))
            b.lathe("Navy", [(3.95, 12.0), (4.15, 12.0), (3.9, 14.0), (0, 14.0)], n=14, sc=(0.7, 1.3), cap=True)
            b.lathe("White", [(4.48, 6.0), (4.6, 6.0), (4.6, 7.2), (4.45, 7.2)], n=14, sc=(0.7, 1.3), cap=False)
    # pool deck aft on deck 4 roof: pool, loungers, waterslide
    PZ = 38.0
    b.bx("Plank", -11.5, 11.5, 12.0, 55.0, PZ, PZ + 0.2, bev=0)
    b.bx("SkyBlue", -6.5, 6.5, 15.0, 27.0, PZ + 0.2, PZ + 0.8)
    b.bx("Water", -6.0, 6.0, 15.5, 26.5, PZ + 0.5, PZ + 0.95)
    for k in range(6):
        y = 15.5 + k * 2.2
        for sx in (-1, 1):
            with b.at(T(sx * 9.0, y, PZ + 0.2)):
                b.bx("White", -0.8, 0.8, -0.9, 0.9, 0.6, 0.9)
                b.box("White", (sx * -0.6, 0, 1.5), (0.3, 1.8, 1.4), ry=sx * 0.6, bev=0)
                b.bx(("Coral", "Lemon", "SkyBlue")[k % 3], -0.7, 0.7, -0.8, 0.8, 0.9, 1.0, bev=0)
    b.striped_canopy("Coral", "White", (7.6, 29.5), 2.6, 1.0, n=8, z=PZ + 4.0, scallop=False)
    b.cylz("White", 7.6, 29.5, PZ, PZ + 4.0, 0.12, 5)
    # waterslide: a spiral tube off a tower
    b.bx("Yellow", -10.5, -6.5, 50.0, 54.0, PZ, PZ + 12.0)
    pts = []
    for k in range(40):
        t = k / 39
        a = t * TAU * 1.5
        pts.append((-8.5 + math.cos(a) * 5.0 + t * 2, 44.0 + math.sin(a) * 5.0 - t * 6, PZ + 11.5 - t * 10.5))
    b.tube("Teal", pts, 1.0, 10)
    # lifeboats on davits along deck 1
    for sx in (-1, 1):
        for k in range(7):
            y = -38 + k * 13.0
            x = sx * 15.6
            b.ball("Orange", (x, y, 19.6), 1.0, seg=(12, 6), sc=(1.4, 4.0, 1.1))
            b.bx("White", x - 1.2, x + 1.2, y - 3.0, y + 3.0, 20.2, 20.7)
            for dy in (-2.6, 2.6):
                b.cyl("DarkMetal", (sx * 14.4, y + dy, 18.0), (sx * 14.4, y + dy, 23.0), 0.2, 5)
                b.cyl("DarkMetal", (sx * 14.4, y + dy, 23.0), (x, y + dy, 22.0), 0.2, 5)
    # bow deck: capstans + mooring
    for sx in (-1, 1):
        b.cylz("DarkMetal", sx * 4.0, -66.0, 18.0, 19.4, 1.0, 10)
    b.cylz("White", 0, -78.0, 18.0, 26.0, 0.3, 6)
    return b


def harbor_terminal():
    b = Builder("HarborTerminal", AREA)
    W, D = 60.0, 28.0
    b.bx("Concrete", -W / 2 - 2, W / 2 + 2, -D / 2 - 6, D / 2 + 2, 0, 1.0)
    b.bx("GlassDark", -W / 2, W / 2, -D / 2, D / 2, 1.0, 14.0)
    for k in range(16):
        x = -W / 2 + k * W / 15
        b.bx("White", x - 0.3, x + 0.3, -D / 2 - 0.4, -D / 2 + 0.2, 1.0, 14.0, bev=0)
    for z in (5.0, 9.5):
        b.bx("White", -W / 2, W / 2, -D / 2 - 0.4, -D / 2 + 0.2, z - 0.2, z + 0.2, bev=0)
    for sx in (-1, 1):
        b.bx("White", sx * W / 2 - 1.2, sx * W / 2 + 1.2, -D / 2 - 1.0, D / 2 + 1.0, 1.0, 14.0)
    # wave roof: slats following a swell
    n = 24
    for k in range(n):
        x = -W / 2 - 4 + (k + 0.5) * (W + 8) / n
        h = 18.4 + 3.4 * math.sin((k / n) * TAU * 1.0 + 0.5)
        h2 = 18.4 + 3.4 * math.sin(((k + 1) / n) * TAU * 1.0 + 0.5)
        with b.at(T(x, 0, (h + h2) / 2), R(0, -math.atan2(h2 - h, (W + 8) / n), 0)):
            b.box("White" if k % 6 else "SkyBlue", (0, 0, 0), ((W + 8) / n + 0.1, D + 10, 0.8))
    for x in (-W / 2 + 4, -10, 10, W / 2 - 4):
        b.cyl("White", (x, -D / 2 - 4.5, 1.0), (x, -D / 2 - 4.5, 18.4 + 3.4 * math.sin(((x + W / 2 + 4) / (W + 8)) * TAU + 0.5) - 0.4), 0.5, 8)
    # entrance + sign
    b.bx("Glass", -6, 6, -D / 2 - 0.6, -D / 2 - 0.3, 1.0, 8.0)
    b.bx("Navy", -10, 10, -D / 2 - 5.4, -D / 2 - 4.8, 8.6, 12.0)
    b.text("White", "CRUISE PORT", (0, -D / 2 - 5.5, 10.3), 2.0, depth=0.3, font="black")
    for x in (-8.5, 8.5):
        b.cyl("White", (x, -D / 2 - 5.0, 12.0), (x, -D / 2 - 4.6, 14.6), 0.15, 5)
    # flagpoles
    cols = ("Red", "Blue", "Yellow", "Green", "White", "Orange")
    for k, col in enumerate(cols):
        x = -W / 2 + 6 + k * 9.6
        b.cylz("White", x, -D / 2 - 10.0, 1.0, 16.0, 0.18, 6)
        b.ball("Gold", (x, -D / 2 - 10.0, 16.2), 0.3, seg=(6, 4))
        b.prism_y(col, [(x + 0.1, 15.8), (x + 3.8, 15.8), (x + 3.8, 13.4), (x + 0.1, 13.4)], -D / 2 - 10.05, -D / 2 - 9.95)
    # passenger bridge reaching out to the ship (to +X)
    with b.at(T(W / 2 + 1.2, 6, 0)):
        b.bx("White", 0, 24, -2.4, 2.4, 10.0, 14.6)
        b.bx("GlassDark", 0, 24, -2.6, -2.3, 11.0, 13.8, bev=0)
        b.bx("GlassDark", 0, 24, 2.3, 2.6, 11.0, 13.8, bev=0)
        for x in (8, 20):
            b.cylz("DarkMetal", x, 0, 1.0, 10.0, 0.7, 10)
            b.bx("DarkMetal", x - 1.6, x + 1.6, -1.6, 1.6, 0, 1.0)
        b.bx("Navy", 23.0, 25.4, -2.8, 2.8, 9.6, 15.2)
    # planters + benches out front
    for x in (-20, 20):
        b.bx("Concrete", x - 4, x + 4, -D / 2 - 7.5, -D / 2 - 5.5, 1.0, 2.2)
        for j in range(4):
            b.rock("Hedge", (x - 3 + j * 2, -D / 2 - 6.5, 2.6), 0.9, sc=(1, 1, 0.8), jitter=0.1)
    return b


def lighthouse():
    b = Builder("Lighthouse", AREA)
    rng = b.rng
    for k in range(14):
        a = TAU * k / 14
        b.rock("Rock" if k % 2 else "StoneDark", (math.cos(a) * 8.5, math.sin(a) * 8.5, 1.0), rng.uniform(2.2, 3.2), sc=(1.2, 1, 0.8))
    b.lathe("Stone", [(0, 0), (8.0, 0), (8.0, 2.6), (7.4, 3.0), (0, 3.0)], n=16)
    H = 44.0
    stripes = 6
    for k in range(stripes):
        z0 = 3.0 + k * H / stripes
        z1 = z0 + H / stripes
        r0 = 6.0 - 2.2 * (z0 - 3.0) / H
        r1 = 6.0 - 2.2 * (z1 - 3.0) / H
        b.lathe("Red" if k % 2 == 0 else "White", [(0, z0), (r0, z0), (r1, z1), (0, z1)], n=16)
    for z in (14.0, 26.0, 38.0):
        a = -PI / 2 + 0.3
        r = 6.0 - 2.2 * (z - 3.0) / H
        b.window("GlassDark", "White", (math.cos(a) * (r + 0.05), math.sin(a) * (r + 0.05), z), 1.2, 2.2, rz=a + PI / 2, ft=0.25, cross=False)
    top = 3.0 + H
    # corbels + gallery + railing
    for k in range(12):
        a = TAU * k / 12
        b.box("White", (math.cos(a) * 4.4, math.sin(a) * 4.4, top - 0.8), (1.2, 0.6, 1.6), rz=a)
    b.lathe("Charcoal", [(0, top), (6.0, top), (6.0, top + 0.6), (0, top + 0.6)], n=16)
    for k in range(24):
        a = TAU * k / 24
        b.cylz("Charcoal", math.cos(a) * 5.7, math.sin(a) * 5.7, top + 0.6, top + 3.0, 0.1, 4)
    b.torus("Charcoal", (0, 0, top + 3.0), 5.7, 0.14, 24, 4)
    b.torus("Charcoal", (0, 0, top + 1.8), 5.7, 0.08, 24, 3)
    # lantern room
    b.lathe("Red", [(0, top + 0.6), (3.6, top + 0.6), (3.6, top + 2.0), (0, top + 2.0)], n=12)
    b.lathe("Glass", [(0, top + 2.0), (3.3, top + 2.0), (3.3, top + 7.0), (0, top + 7.0)], n=12)
    for k in range(12):
        a = TAU * k / 12
        b.cylz("Charcoal", math.cos(a) * 3.35, math.sin(a) * 3.35, top + 2.0, top + 7.0, 0.12, 4)
    b.ball("NeonYellow", (0, 0, top + 4.5), 1.4, seg=(10, 8))
    b.cylz("Charcoal", 0, 0, top + 2.0, top + 3.4, 0.6, 8)
    b.lathe("Red", [(0, top + 7.0), (3.9, top + 7.0), (3.6, top + 7.6), (2.0, top + 9.6), (0.3, top + 10.4), (0, top + 10.4)], n=12)
    b.ball("Charcoal", (0, 0, top + 10.6), 0.4, seg=(8, 6))
    b.cylz("Charcoal", 0, 0, top + 10.8, top + 13.0, 0.08, 4)
    # keeper's cottage
    with b.at(T(0, -10.5, 0)):
        b.bx("White", -5.5, 5.5, -3.5, 3.5, 0, 6.5)
        b.gable_roof("Red", 0, 0, 6.5, 11, 7, 3.4, t=0.5, over=0.8)
        b.gable_end("White", -5.5, 0, 6.5, 7, 3.4)
        b.gable_end("White", 5.5, 0, 6.5, 7, 3.4)
        b.door("Navy", "White", (2.6, -3.6, 0), 2.0, 4.6)
        b.window("Glass", "White", (-2.2, -3.6, 3.4), 2.0, 2.0, shutters="Navy", sill="White")
        b.bx("Brick", -4.0, -2.6, 0.5, 1.9, 6.5, 11.0)
    return b


def cargo_crane():
    b = Builder("CargoCrane", AREA)
    Y = "Yellow"
    # rails + bogies
    for x in (-10, 10):
        b.bx("DarkMetal", x - 0.4, x + 0.4, -16, 16, 0, 0.5)
        for y in (-11, 11):
            b.bx(Y, x - 1.2, x + 1.2, y - 3.5, y + 3.5, 0.5, 2.4)
            for dy in (-2.2, 0, 2.2):
                b.cyl("DarkMetal", (x - 1.3, y + dy, 1.2), (x + 1.3, y + dy, 1.2), 0.75, 10)
    # legs + portal beams
    for x in (-10, 10):
        for y in (-11, 11):
            b.bx(Y, x - 0.9, x + 0.9, y - 0.9, y + 0.9, 2.4, 34)
        b.bx(Y, x - 1.0, x + 1.0, -12, 12, 30, 34)
        b.cyl(Y, (x, -11, 6), (x, 11, 26), 0.4, 6)
        b.cyl(Y, (x, 11, 6), (x, -11, 26), 0.4, 6)
    for y in (-11, 11):
        b.bx(Y, -11, 11, y - 1.0, y + 1.0, 30, 34)
        b.bx(Y, -11, 11, y - 0.6, y + 0.6, 8.0, 9.4)
    # machinery house + operator cab
    b.bx("White", -8, 8, 0, 14, 34, 41)
    b.bx("Navy", -8.1, 8.1, 0, 14, 39.6, 40.2, bev=0)
    b.text("Navy", "PORT 06", (0, -0.15, 37.4), 1.6, depth=0.15, font="black")
    # boom (lattice truss) reaching out over the water to -Y
    BL = 48.0
    for x in (-3.5, 3.5):
        b.bx(Y, x - 0.6, x + 0.6, -BL, 18, 34, 35.2)
        b.bx(Y, x - 0.6, x + 0.6, -BL, 18, 38.8, 40.0)
        n = 16
        for k in range(n):
            y0 = -BL + k * (BL + 18) / n
            y1 = y0 + (BL + 18) / n
            b.cyl(Y, (x, y0, 35.0), (x, y1, 39.0), 0.25, 5)
            b.cylz(Y, x, y0, 35.0, 39.2, 0.22, 5)
    for k in range(9):
        y = -BL + k * (BL + 18) / 8
        b.bx(Y, -4, 4, y - 0.3, y + 0.3, 39.2, 39.8)
    # A-frame + stays
    for x in (-3.5, 3.5):
        b.cyl(Y, (x, 8, 40), (x * 0.4, 4, 54), 0.5, 6)
        b.cyl(Y, (x, 0, 40), (x * 0.4, 4, 54), 0.5, 6)
        b.cyl("DarkMetal", (x * 0.4, 4, 54), (x, -BL + 2, 40), 0.15, 4)
        b.cyl("DarkMetal", (x * 0.4, 4, 54), (x, 17, 40), 0.15, 4)
    b.bx(Y, -2, 2, 3, 5, 53, 55)
    b.ball("NeonRed", (0, 4, 55.4), 0.4, seg=(6, 4))
    # trolley, cab, hoist ropes, spreader + a hanging container
    TY = -26.0
    b.bx("White", -3.0, 3.0, TY - 2.0, TY + 2.0, 32.4, 34.6)
    b.bx("GlassDark", -2.0, 2.0, TY - 2.1, TY - 1.9, 32.8, 34.2, bev=0)
    for dx in (-1.6, 1.6):
        for dy in (-1.2, 1.2):
            b.cylz("DarkMetal", dx, TY + dy, 20.0, 32.4, 0.08, 4)
    b.bx("Yellow", -5.5, 5.5, TY - 2.0, TY + 2.0, 19.2, 20.0)
    container(b, (0, TY, 10.6), "Red", rz=PI / 2, w=4.0, L=11.0, h=8.6)
    return b


def container(b, c, col, rz=0.0, L=20.0, w=8.0, h=8.5, doors=True):
    with b.at(T(c), R(0, 0, rz)):
        b.bx(col, -L / 2, L / 2, -w / 2, w / 2, 0, h)
        n = int(L / 1.0)
        for i in range(1, n):
            x = -L / 2 + i * L / n
            for sy in (-1, 1):
                b.bx(col, x - 0.22, x + 0.22, sy * w / 2 - 0.15, sy * w / 2 + 0.15, 0.6, h - 0.6, bev=0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.bx("DarkMetal", sx * L / 2 - 0.4 * sx - 0.4, sx * L / 2 - 0.4 * sx + 0.4, sy * w / 2 - 0.4 * sy - 0.4, sy * w / 2 - 0.4 * sy + 0.4, 0, h, bev=0.05)
        for zz in (0.3, h - 0.3):
            for sy in (-1, 1):
                b.bx("DarkMetal", -L / 2, L / 2, sy * w / 2 - 0.25, sy * w / 2 + 0.25, zz - 0.3, zz + 0.3, bev=0)
        if doors:
            for dy in (-w / 4, w / 4):
                b.bx(col, -L / 2 - 0.2, -L / 2, dy - w / 4 + 0.15, dy + w / 4 - 0.15, 0.6, h - 0.6, bev=0)
                for k in (-0.9, 0.9):
                    b.cyl("Metal", (-L / 2 - 0.35, dy + k, 0.8), (-L / 2 - 0.35, dy + k, h - 0.8), 0.1, 4)


def container_stack():
    b = Builder("ContainerStack", AREA)
    layout = [((0, -4.2, 0), "Red"), ((0, 4.2, 0), "Blue"), ((0.6, -4.2, 8.5), "Green"), ((-0.4, 4.2, 8.5), "Orange"),
              ((0.2, 0, 17.0), "Teal"), ((23.0, -4.2, 0), "Navy"), ((23.0, 4.2, 0), "Yellow"), ((23.5, 0.0, 8.5), "Red")]
    for (c, col) in layout:
        container(b, c, col, rz=0.0 if c[2] < 17 else 0.05)
    return b


def dock_pier():
    b = Builder("DockPier", AREA)
    W, L = 24.0, 60.0
    b.bx("Concrete", -W / 2, W / 2, -L / 2, L / 2, 0, 6.0)
    for k in range(int(L / 4)):
        y = -L / 2 + k * 4 + 2
        b.bx("Grey", W / 2 - 0.2, W / 2 + 0.3, y - 1.8, y + 1.8, 0.5, 5.5, bev=0.1)
    b.bx("Yellow", W / 2 - 1.8, W / 2 - 0.8, -L / 2, L / 2, 6.0, 6.08, bev=0)
    b.bx("Asphalt", -W / 2 + 0.4, W / 2 - 2.2, -L / 2, L / 2, 6.0, 6.06, bev=0)
    # tyre fenders + bollards + ladder
    for k in range(6):
        y = -L / 2 + 5 + k * (L - 10) / 5
        b.torus("Rubber", (W / 2 + 0.9, y, 3.6), 1.4, 0.6, 14, 6, ry=PI / 2)
        b.cyl("Rope", (W / 2 + 0.6, y, 5.0), (W / 2 + 0.2, y, 6.0), 0.1, 4)
        bx = W / 2 - 3.0
        b.lathe("Black", [(0, 6.0), (1.1, 6.0), (0.7, 6.6), (0.7, 7.9), (1.2, 8.4), (1.2, 8.9), (0, 8.9)], c=(bx, y + 2.5, 0), n=12)
    with b.at(T(W / 2 + 0.3, -3.0, 0)):
        for sy in (-0.9, 0.9):
            b.bx("DarkMetal", -0.15, 0.15, sy - 0.15, sy + 0.15, 0.5, 7.0)
        for k in range(8):
            b.cyl("DarkMetal", (0, -0.9, 1.0 + k * 0.75), (0, 0.9, 1.0 + k * 0.75), 0.1, 4)
    # coiled rope, crates, lamp posts
    for k in range(4):
        b.torus("Rope", (W / 2 - 6.0, 10.0, 6.25 + k * 0.32), 1.6 - k * 0.12, 0.2, 14, 5)
    for k, (x, y) in enumerate(((-6, -20), (-3.6, -20), (-4.8, -20))):
        z = 6.0 + (2.4 if k == 2 else 0)
        b.bx("WoodLight", x - 1.15, x + 1.15, y - 1.15, y + 1.15, z, z + 2.3)
        b.bx("WoodDark", x - 1.2, x + 1.2, y - 1.2, y + 1.2, z + 1.0, z + 1.3, bev=0)
    for y in (-18, 2, 22):
        b.lamp("Charcoal", "WindowGlow", (-W / 2 + 1.5, y, 6.0), h=10.0, arms=2)
    return b


def tugboat():
    b = Builder("Tugboat", AREA)
    L, BEAM = 26.0, 5.2
    rings = []
    for i in range(13):
        t = i / 12
        y = L / 2 - t * L
        hw = BEAM * (1.0 if t < 0.6 else max(0.25, math.cos((t - 0.6) / 0.4 * PI / 2) ** 0.6))
        rake = max(0, t - 0.75) / 0.25
        rings.append([(-hw, y, 6.5 + rake), (-hw * 0.95, y, 2.0), (-hw * 0.5, y, 0.3), (0, y, 0.0), (hw * 0.5, y, 0.3), (hw * 0.95, y, 2.0),
                      (hw, y, 6.5 + rake)])
    b.loft("Red", rings, closed=True)
    b.tube("Black", [(r[0][0] - 0.3, r[0][1], r[0][2] - 0.3) for r in rings] + [(-r[0][0] + 0.3, r[0][1], r[0][2] - 0.3) for r in rings[::-1]], 0.6, 6)
    b.tube("Black", [(r[1][0] * 1.06, r[1][1], 3.6) for r in rings[1:-1]], 0.35, 5)
    b.tube("Black", [(-r[1][0] * 1.06, r[1][1], 3.6) for r in rings[1:-1]], 0.35, 5)
    for k in range(5):
        y = L / 2 - 4 - k * 3.6
        for sx in (-1, 1):
            b.torus("Rubber", (sx * (BEAM + 0.5), y, 5.0), 0.9, 0.45, 12, 6, ry=PI / 2)
    b.ball("Rubber", (0, -L / 2 - 0.8, 6.0), 1.0, seg=(10, 6), sc=(2.6, 1.4, 1.2))
    b.bx("Plank", -BEAM + 0.6, BEAM - 0.6, -L / 2 + 3, L / 2 - 0.6, 6.4, 6.6, bev=0)
    # deckhouse + wheelhouse
    b.bx("White", -3.6, 3.6, -6, 6, 6.5, 10.5)
    for x in (-3.65, 3.65):
        for y in (-3.5, 0, 3.5):
            b.cyl("GlassDark", (x, y, 9.0), (x * 1.03, y, 9.0), 0.55, 8)
    b.bx("White", -3.2, 3.2, -5.5, -0.5, 10.5, 14.8)
    b.bx("GlassDark", -3.3, 3.3, -5.6, -0.4, 12.6, 14.2, bev=0)
    for x in (-2.0, 0.0, 2.0):
        b.bx("White", x - 0.15, x + 0.15, -5.7, -5.5, 12.6, 14.2, bev=0)
    b.bx("Navy", -3.8, 3.8, -6.2, 0.2, 14.8, 15.4)
    b.cylz("White", 0, -3.0, 15.4, 21.0, 0.2, 6)
    b.cyl("White", (-1.6, -3.0, 19.0), (1.6, -3.0, 19.0), 0.12, 5)
    for x in (-1.6, 1.6):
        b.ball("NeonRed" if x < 0 else "NeonGreen", (x, -3.0, 19.3), 0.25, seg=(6, 4))
    # funnel
    b.lathe("Red", [(0, 10.5), (1.6, 10.5), (1.6, 15.5), (0, 15.5)], c=(0, 2.6, 0), n=10, sc=(1, 1.3))
    b.lathe("Black", [(0, 15.5), (1.62, 15.5), (1.62, 16.6), (0, 16.6)], c=(0, 2.6, 0), n=10, sc=(1, 1.3))
    b.bx("White", -1.65, 1.65, 2.3, 2.9, 12.6, 13.4, bev=0)
    # towing bitt + winch aft
    b.cylz("Black", -1.2, 9.5, 6.5, 8.6, 0.6, 8)
    b.cylz("Black", 1.2, 9.5, 6.5, 8.6, 0.6, 8)
    b.cyl("Black", (-1.2, 9.5, 8.0), (1.2, 9.5, 8.0), 0.3, 6)
    b.cyl("DarkMetal", (-2.0, 7.4, 7.6), (2.0, 7.4, 7.6), 1.0, 12)
    for k in range(4):
        b.cyl("Rope", (-1.6 + k * 1.0, 7.4, 7.6), (-1.0 + k * 1.0, 7.4, 7.6), 1.12, 12)
    b.text("White", "TUG 12", (0, L / 2 + 0.1, 5.2), 1.0, depth=0.12, rz=PI, font="black")
    return b


def fish_market():
    b = Builder("FishMarket", AREA)
    W, D = 22.0, 10.0
    b.bx("Concrete", -W / 2 - 1, W / 2 + 1, -D / 2 - 3, D / 2 + 1, 0, 0.5)
    for x in (-W / 2, 0, W / 2):
        for y in (-D / 2, D / 2):
            b.cylz("White", x, y, 0.5, 9.5 if y > 0 else 8.5, 0.3, 8)
    with b.at(T(0, 0, 9.0), R(math.atan2(1.0, D), 0, 0)):
        for k in range(10):
            x = -W / 2 - 1 + (k + 0.5) * (W + 2) / 10
            b.box("Blue" if k % 2 else "White", (x, 0, 0), ((W + 2) / 10, D + 3, 0.3))
    for k in range(10):
        x = -W / 2 - 1 + (k + 0.5) * (W + 2) / 10
        pts = [(x - (W + 2) / 20, 0)] + [(x + math.cos(PI + PI * j / 6) * (W + 2) / 20, math.sin(PI + PI * j / 6) * 0.7) for j in range(1, 6)] + [(x + (W + 2) / 20, 0)]
        with b.at(T(0, -D / 2 - 1.45, 8.35), R(PI / 2, 0, 0)):
            b.extrude("Blue" if k % 2 else "White", [(p[0], p[1], 0) for p in pts], (0, 0, 0.15))
    # ice beds with fish
    for gx in (-6.5, 6.5):
        b.bx("WoodDark", gx - 4.5, gx + 4.5, -D / 2 + 0.5, -D / 2 + 5.0, 0.5, 3.6)
        with b.at(T(gx, -D / 2 + 2.75, 3.6), R(-0.25, 0, 0)):
            b.bx("White", -4.3, 4.3, -2.2, 2.2, 0, 0.5)
            for k in range(10):
                x = -3.5 + (k % 5) * 1.75
                y = -1.0 + (k // 5) * 2.0
                col = ("Metal", "Coral", "Metal", "SkyBlue", "Orange")[k % 5]
                with b.at(T(x, y, 0.75), R(0, 0, 0.3 * ((k % 3) - 1))):
                    b.ball(col, (0, 0, 0), 1.0, seg=(10, 6), sc=(0.55, 1.5, 0.35))
                    b.prism_x(col, [(1.3, 0), (2.0, 0.45), (2.0, -0.45)], -0.1, 0.1)
                    b.ball("Black", (0.28, -1.0, 0.12), 0.1, seg=(5, 3))
    # sign + hanging scale + buoys
    b.bx("Navy", -5.5, 5.5, -D / 2 - 1.8, -D / 2 - 1.4, 10.0, 12.6)
    b.text("White", "FISH MARKET", (0, -D / 2 - 1.85, 11.3), 1.3, depth=0.15, font="black")
    b.cylz("DarkMetal", 0, -D / 2 + 0.6, 6.4, 8.6, 0.06, 4)
    b.lathe("Metal", [(0, 0), (0.8, 0), (0.9, 0.3), (0, 0.3)], c=(0, -D / 2 + 0.6, 5.0), n=10)
    b.cylz("White", 0, -D / 2 + 0.6, 5.6, 6.6, 0.55, 10)
    for k, col in enumerate(("Red", "Orange", "Yellow", "Red")):
        x = W / 2 + 0.2
        y = -D / 2 + 1.5 + k * 2.2
        b.cylz("Rope", x, y, 6.0, 8.0, 0.06, 4)
        b.ball(col, (x, y, 5.4), 0.7, seg=(8, 6), sc=(1, 1, 1.3))
        b.cylz("White", x, y, 5.2, 5.6, 0.72, 8)
    # lobster pots + crates
    for k, (x, y, z) in enumerate(((-W / 2 - 2.0, 2.0, 0.5), (-W / 2 - 2.0, 5.2, 0.5), (-W / 2 - 2.0, 3.6, 3.1))):
        with b.at(T(x, y, z)):
            b.bx("WoodDark", -1.4, 1.4, -1.4, 1.4, 0, 0.25)
            for j in range(5):
                a = PI * j / 4
                b.cyl("WoodLight", (-1.4, math.cos(a) * 1.3, 0.2 + math.sin(a) * 2.2), (1.4, math.cos(a) * 1.3, 0.2 + math.sin(a) * 2.2), 0.1, 4)
            for j in range(3):
                b.torus("Rope", (-1.4 + j * 1.4, 0, 0.2), 1.3, 0.06, 10, 3, rx=PI / 2, rz=PI / 2, a0=0, a1=PI)
    return b


def anchor_monument():
    b = Builder("AnchorMonument", AREA)
    b.lathe("Stone", [(0, 0), (6.0, 0), (6.0, 1.0), (5.0, 1.0), (5.0, 3.0), (0, 3.0)], n=16)
    b.ring("Navy", (0, 0, 0), 5.1, 4.6, 2.2, 2.6, n=16)
    with b.at(T(0, 0, 3.0)):
        b.cylz("Charcoal", 0, 0, 2.0, 15.0, 0.75, 10)
        b.cyl("Charcoal", (-4.0, 0, 13.5), (4.0, 0, 13.5), 0.6, 8)
        for sx in (-1, 1):
            b.ball("Charcoal", (sx * 4.2, 0, 13.5), 0.8, seg=(8, 6))
        b.torus("Charcoal", (0, 0, 16.4), 1.4, 0.45, 14, 6, rx=PI / 2)
        b.torus("Charcoal", (0, 0, 6.5), 6.2, 0.75, 20, 8, rx=PI / 2, a0=PI + 0.35, a1=TAU - 0.35)
        for sx in (-1, 1):
            a = PI + 0.35 if sx < 0 else TAU - 0.35
            x, z = math.cos(a) * 6.2, 6.5 + math.sin(a) * 6.2
            with b.at(T(x, 0, z), R(0, sx * -0.9, 0)):
                b.prism_y("Charcoal", [(-1.3, -0.4), (1.3, -0.4), (0, 2.2)], -0.4, 0.4)
        b.prism_y("Charcoal", [(-1.2, 0.0), (1.2, 0.0), (0, -1.6)], -0.5, 0.5)
        # chain draped round the shank
        pts = [(math.cos(a) * 1.2, math.sin(a) * 1.2, 15.0 - a * 1.2) for a in [k * 0.4 for k in range(26)]]
        for k in range(len(pts) - 1):
            p0, p1 = V(pts[k]), V(pts[k + 1])
            m = (p0 + p1) / 2
            d = p1 - p0
            b.torus("Rust", tuple(m), 0.32, 0.1, 8, 4, rz=math.atan2(d.y, d.x), rx=(PI / 2 if k % 2 else 0))
    b.bx("Gold", -2.6, 2.6, -5.1, -4.9, 1.2, 2.0, bev=0)
    return b


def warehouse():
    b = Builder("Warehouse", AREA)
    W, D, H = 40.0, 26.0, 14.0
    b.bx("Concrete", -W / 2 - 1, W / 2 + 1, -D / 2 - 4, D / 2 + 1, 0, 1.4)
    b.bx("Brick", -W / 2, W / 2, -D / 2, D / 2, 1.4, H)
    for x in (-W / 2, -W / 6, W / 6, W / 2):
        b.bx("Brick", x - 1.0, x + 1.0, -D / 2 - 0.6, -D / 2 + 0.4, 1.4, H + 0.6)
    for z in (H - 1.2,):
        b.bx("Concrete", -W / 2 - 0.4, W / 2 + 0.4, -D / 2 - 0.5, D / 2 + 0.4, z, z + 0.8)
    for i, x in enumerate((-W / 3, 0, W / 3)):
        b.bx("Metal", x - 4.5, x + 4.5, -D / 2 - 0.3, -D / 2 + 0.1, 1.4, 10.0)
        for k in range(14):
            z = 1.8 + k * 0.6
            b.bx("Grey", x - 4.4, x + 4.4, -D / 2 - 0.42, -D / 2 - 0.3, z, z + 0.15, bev=0)
        b.bx("Concrete", x - 5.0, x + 5.0, -D / 2 - 0.6, -D / 2 + 0.2, 10.0, 10.8)
        b.bx("Yellow", x - 5.0, x - 4.5, -D / 2 - 0.8, -D / 2 - 0.3, 1.4, 10.0, bev=0)
        b.bx("Yellow", x + 4.5, x + 5.0, -D / 2 - 0.8, -D / 2 - 0.3, 1.4, 10.0, bev=0)
    b.bx("Navy", -5.0, 5.0, -D / 2 - 0.65, -D / 2 - 0.3, 11.0, 12.6)
    b.text("White", "WAREHOUSE 07", (0, -D / 2 - 0.7, 11.8), 1.0, depth=0.12, font="black")
    for sx in (-1, 1):
        for k in range(4):
            y = -D / 2 + 3.5 + k * (D - 7) / 3
            b.window("GlassDark", "Concrete", (sx * (W / 2 + 0.2), y, 8.0), 2.6, 3.4, rz=sx * PI / 2, cross=True)
    b.gable_roof("Rust", 0, 0, H, W, D, 6.0, t=0.45, over=1.0)
    with b.at(R(0, 0, 0)):
        for k in range(22):
            x = -W / 2 - 0.6 + k * (W + 1.2) / 21
            a = math.atan2(6.0, D / 2)
            for sy in (-1, 1):
                L = math.hypot(D / 2 + 1, 6.0 + math.tan(a))
                b.box("Rust", (x, sy * D / 4, H + 3.0 + 0.2), (0.3, L, 0.25), rx=-sy * a, bev=0)
    for x in (-W / 2, W / 2):
        b.gable_end("Brick", x, 0, H, D, 6.0, t=0.4)
    b.cyl("GlassDark", (W / 2 + 0.25, 0, H + 2.4), (W / 2 + 0.45, 0, H + 2.4), 1.6, 14)
    # pallets + forklift-free cargo
    for k, (x, y) in enumerate(((-16, -D / 2 - 3.0), (-12.5, -D / 2 - 3.0), (14, -D / 2 - 3.0))):
        b.bx("WoodLight", x - 1.6, x + 1.6, y - 1.6, y + 1.6, 1.4, 1.9)
        b.bx("Cream" if k % 2 else "Orange", x - 1.4, x + 1.4, y - 1.4, y + 1.4, 1.9, 4.2)
        b.bx("Glass", x - 1.45, x + 1.45, y - 1.45, y + 1.45, 2.2, 3.9, bev=0)
    return b


def nav_buoy():
    b = Builder("NavBuoy", AREA)
    b.lathe("Red", [(0, 0), (2.0, 0), (3.0, 1.6), (3.0, 3.2), (0, 3.2)], n=16)
    b.lathe("White", [(0, 3.2), (3.05, 3.2), (3.05, 3.8), (0, 3.8)], n=16)
    for k in range(4):
        a = TAU * k / 4
        b.cyl("Red", (math.cos(a) * 2.2, math.sin(a) * 2.2, 3.8), (math.cos(a) * 0.6, math.sin(a) * 0.6, 10.0), 0.3, 6)
    b.cylz("Red", 0, 0, 3.8, 10.0, 0.4, 8)
    b.bx("Red", -1.6, 1.6, -0.2, 0.2, 6.0, 9.0)
    b.bx("White", -1.0, 1.0, -0.25, 0.25, 6.6, 8.4, bev=0)
    b.lathe("DarkMetal", [(0, 10.0), (0.9, 10.0), (0.9, 10.4), (0, 10.4)], n=10)
    b.lathe("NeonRed", [(0, 10.4), (0.6, 10.4), (0.6, 11.4), (0, 11.4)], n=10)
    b.lathe("DarkMetal", [(0, 11.4), (0.8, 11.4), (0.2, 12.0), (0, 12.0)], n=10)
    b.torus("Rubber", (0, 0, 1.8), 3.05, 0.35, 18, 5)
    b.cylz("Water", 0, 0, 0, 1.0, 5.0, 20)
    return b


def harbor_gate():
    b = Builder("HarborGate", AREA)
    for sx in (-1, 1):
        x = sx * 10.5
        for dx in (-1.0, 1.0):
            b.cylz("WoodDark", x + dx, 0, 0, 21.0 + dx * sx * 1.5, 1.1, 10)
            b.cylz("Black", x + dx, 0, 21.0 + dx * sx * 1.5, 21.4 + dx * sx * 1.5, 1.15, 10)
        for k in range(5):
            b.torus("Rope", (x, 0, 3.0 + k * 0.4), 2.25, 0.2, 14, 5)
            b.torus("Rope", (x, 0, 16.0 + k * 0.4), 2.25, 0.2, 14, 5)
        b.torus("Red", (x, -2.4, 9.5), 1.6, 0.5, 16, 6, rx=PI / 2)
        for k in range(4):
            a = PI / 4 + k * PI / 2
            b.torus("White", (x, -2.4, 9.5), 1.6, 0.53, 3, 6, rx=PI / 2, a0=a - 0.32, a1=a + 0.32)
    # sign beam
    b.bx("WoodDark", -13.5, 13.5, -1.2, 1.2, 17.0, 18.8)
    b.bx("Navy", -8.5, 8.5, -1.6, -1.1, 11.6, 16.4)
    b.bx("White", -8.9, 8.9, -1.7, -1.0, 16.2, 16.7)
    b.bx("White", -8.9, 8.9, -1.7, -1.0, 11.3, 11.8)
    b.text("White", "HARBOR", (0, -1.75, 14.0), 2.6, depth=0.3, font="black")
    for x in (-7.0, 7.0):
        b.cyl("Rope", (x, -1.4, 16.6), (x, -1.4, 17.2), 0.12, 4)
    # ship's wheel on top
    with b.at(T(0, 0, 23.0), R(PI / 2, 0, 0)):
        b.torus("WoodRed", (0, 0, 0), 3.4, 0.35, 24, 6)
        b.cylz("Brass", 0, 0, -0.5, 0.5, 0.9, 12)
        for k in range(8):
            a = TAU * k / 8
            b.cyl("WoodRed", (0, 0, 0), (math.cos(a) * 4.6, math.sin(a) * 4.6, 0), 0.22, 6)
            b.ball("WoodRed", (math.cos(a) * 4.7, math.sin(a) * 4.7, 0), 0.35, seg=(6, 4))
    b.bx("WoodDark", -0.5, 0.5, -0.5, 0.5, 18.8, 20.0)
    # net draped between the posts
    pts = catenary((-9.0, -1.3, 10.5), (9.0, -1.3, 10.5), 2.6, 18)
    for k in range(4):
        b.tube("Rope", [(p.x, p.y, p.z - k * 0.7 + 0.2 * k * math.sin(p.x)) for p in pts], 0.06, 4)
    for k in range(0, 19, 2):
        p = pts[k]
        b.cyl("Rope", (p.x, p.y, p.z), (p.x, p.y, p.z - 2.1), 0.06, 4)
    for k, (x, col) in enumerate(((-5.0, "Orange"), (0.0, "Yellow"), (5.0, "Red"))):
        p = pts[int((x + 9) / 18 * 18)]
        b.ball(col, (x, -1.4, p.z - 2.4), 0.7, seg=(8, 6))
    return b


ASSETS = [cruise_ship, harbor_terminal, lighthouse, cargo_crane, container_stack, dock_pier, tugboat, fish_market,
          anchor_monument, warehouse, nav_buoy, harbor_gate]
