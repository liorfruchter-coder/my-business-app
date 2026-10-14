"""Area 8 -- Pyramid Desert: sandstone, lapis-and-gold stripes, adobe, market cloth."""
import math

from kit import PI, TAU, Builder, R, T, V, catenary

AREA = "PyramidDesert"
GROUND = (232, 200, 130)


def date_palm(b, base, h=16.0, lean=(0.15, 0.05), fronds=9, seed=0.0):
    x0, y0, z0 = base
    pts = []
    for k in range(9):
        t = k / 8
        pts.append(V((x0 + lean[0] * h * t * t, y0 + lean[1] * h * t * t, z0 + h * t)))
    for k in range(8):
        r0 = 0.75 - 0.25 * k / 8
        b.cyl("Bark" if k % 2 else "WoodDark", pts[k], pts[k + 1], r0 + 0.12, 7, r2=r0)
    top = pts[-1]
    b.ball("WoodDark", tuple(top), 0.9, seg=(8, 6))
    for k in range(fronds):
        a = TAU * k / fronds + seed
        droop = 0.6 + 0.4 * ((k * 7) % 3) / 2
        prev = top
        for s in range(6):
            t = (s + 1) / 6
            p = top + V((math.cos(a) * 7.0 * t, math.sin(a) * 7.0 * t, 2.2 * math.sin(t * PI * 0.8) - droop * 4.5 * t * t))
            w = 1.6 * (1 - t * 0.7)
            d = p - prev
            rz = math.atan2(d.y, d.x)
            ry = -math.atan2(d.z, math.hypot(d.x, d.y))
            m = (p + prev) / 2
            b.box("LeafDark" if (s + k) % 2 else "Leaf", tuple(m), (d.length + 0.1, w, 0.18), rz=rz, ry=ry, bev=0)
            prev = p
    for k in range(5):
        a = TAU * k / 5 + 0.4
        b.ball("Orange", (top.x + math.cos(a) * 0.9, top.y + math.sin(a) * 0.9, top.z - 1.2), 0.45, seg=(6, 4), sc=(1, 1, 1.3))


def hiero_panel(b, c, w, h, rz=0.0, st="SandstoneDark"):
    """Rows of carved glyphs on a wall face (outside = local -Y)."""
    rng = b.rng
    with b.at(T(c), R(0, 0, rz)):
        rows = int(h / 1.3)
        cols = int(w / 1.1)
        for r in range(rows):
            z = -h / 2 + (r + 0.5) * h / rows
            for i in range(cols):
                x = -w / 2 + (i + 0.5) * w / cols
                kind = rng.randrange(5)
                if kind == 0:
                    b.box(st, (x, -0.1, z), (0.7, 0.2, 0.25), bev=0)
                elif kind == 1:
                    b.cyl(st, (x, 0, z), (x, -0.2, z), 0.3, 8)
                elif kind == 2:
                    b.prism_y(st, [(x - 0.35, z - 0.35), (x + 0.35, z - 0.35), (x, z + 0.35)], -0.2, 0.0)
                elif kind == 3:
                    b.box(st, (x, -0.1, z), (0.22, 0.2, 0.8), bev=0)
                else:
                    b.box(st, (x - 0.15, -0.1, z), (0.2, 0.2, 0.7), bev=0)
                    b.box(st, (x + 0.1, -0.1, z + 0.25), (0.5, 0.2, 0.2), bev=0)


def nemes_head(b, c, s=1.0, face="SandstoneLight", stripe_a="Gold", stripe_b="Navy", rz=0.0):
    """A pharaoh head in a striped nemes headdress, facing local -Y."""
    with b.at(T(c), R(0, 0, rz)):
        k = s
        # headdress: a flared hood in stripes
        for i in range(8):
            z0 = -3.0 * k + i * 0.95 * k
            z1 = z0 + 0.95 * k
            f0, f1 = 1 - i / 8, 1 - (i + 1) / 8
            w0 = 3.4 * k * (0.7 + 0.3 * f0) + (1.6 * k if i < 3 else 0) * (1 - i / 3)
            w1 = 3.4 * k * (0.7 + 0.3 * f1) + (1.6 * k if i < 2 else 0) * (1 - (i + 1) / 3)
            b.mesh(stripe_a if i % 2 else stripe_b,
                   [(-w0, -1.4 * k, z0), (w0, -1.4 * k, z0), (w0, 3.0 * k, z0), (-w0, 3.0 * k, z0),
                    (-w1, -1.2 * k, z1), (w1, -1.2 * k, z1), (w1, 2.8 * k, z1), (-w1, 2.8 * k, z1)],
                   [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
        b.ball(stripe_b, (0, 0.6 * k, 4.6 * k), 1.0, seg=(10, 6), sc=(2.6 * k, 2.6 * k, 1.2 * k))
        # face
        b.box(face, (0, -1.9 * k, 1.8 * k), (3.6 * k, 1.6 * k, 4.8 * k), bev=0.3 * k)
        b.box(face, (0, -2.2 * k, 4.3 * k), (3.8 * k, 1.2 * k, 0.6 * k))
        b.prism_x(face, [(-2.7 * k, 2.6 * k), (-3.5 * k, 1.2 * k), (-2.7 * k, 1.0 * k)], -0.45 * k, 0.45 * k)
        for sx in (-1, 1):
            b.box("Black", (sx * 0.95 * k, -2.75 * k, 3.1 * k), (1.0 * k, 0.15 * k, 0.32 * k), bev=0)
            b.box(stripe_b, (sx * 1.3 * k, -2.76 * k, 3.1 * k), (0.9 * k, 0.12 * k, 0.12 * k), bev=0)
            b.box(face, (sx * 2.0 * k, -1.6 * k, 2.6 * k), (0.4 * k, 0.9 * k, 1.4 * k))
        b.box("SandstoneDark", (0, -2.75 * k, 0.6 * k), (1.4 * k, 0.12 * k, 0.18 * k), bev=0)
        b.box(stripe_a, (0, -2.0 * k, -1.6 * k), (0.9 * k, 0.8 * k, 2.6 * k), bev=0.1 * k)
        for z in (-0.8, -1.6, -2.4):
            b.box(stripe_b, (0, -2.42 * k, z * k), (0.95 * k, 0.1 * k, 0.15 * k), bev=0)
        # uraeus cobra on the brow
        b.cyl("Gold", (0, -2.6 * k, 4.4 * k), (0, -2.9 * k, 5.6 * k), 0.3 * k, 6, r2=0.2 * k)
        b.ball("Gold", (0, -2.95 * k, 5.7 * k), 0.35 * k, seg=(6, 4), sc=(1.3, 1, 0.8))


def sphinx():
    b = Builder("Sphinx", AREA)
    b.bx("Sandstone", -14, 14, -38, 34, 0, 2.4)
    b.bx("SandstoneDark", -14.4, 14.4, -38.4, 34.4, 0, 0.8)
    for i in range(4):
        b.bx("Sandstone", -6, 6, -38 - (4 - i) * 1.2, -38, 0, 0.6 * (i + 1))
    Z = 2.4
    # recumbent lion body lofted from rounded sections, rump to chest
    prof = [(32, 4.0, 6.0), (29, 7.6, 10.0), (24, 8.6, 11.6), (16, 8.0, 11.0), (8, 7.8, 11.0), (1, 8.4, 12.6),
            (-4, 8.6, 14.6), (-8, 7.6, 15.2), (-10.5, 5.6, 14.2)]
    rings = []
    for y, w, h in prof:
        rings.append([(-w, y, Z), (w, y, Z), (w, y, Z + 0.62 * h), (0.8 * w, y, Z + 0.9 * h), (0.35 * w, y, Z + h),
                      (-0.35 * w, y, Z + h), (-0.8 * w, y, Z + 0.9 * h), (-w, y, Z + 0.62 * h)])
    b.loft("Sandstone", rings)
    # spine ridge + shoulder blades
    b.tube("SandstoneLight", [(0, 30, Z + 9.2), (0, 22, Z + 11.4), (0, 12, Z + 11.0), (0, 2, Z + 12.5), (0, -6, Z + 15.0)], 0.7, 6)
    for sx in (-1, 1):
        # haunch, rear paw, front leg, paw with toes
        b.ball("SandstoneLight", (sx * 7.6, 25, Z + 5.4), 1.0, seg=(12, 8), sc=(2.6, 7.4, 5.2))
        b.bx("SandstoneLight", sx * 8.2 - 2.4, sx * 8.2 + 2.4, 17, 31, Z, Z + 2.4)
        b.ball("SandstoneLight", (sx * 6.2, -5.0, Z + 6.4), 1.0, seg=(10, 8), sc=(2.8, 4.4, 5.8))
        b.bx("SandstoneLight", sx * 5.6 - 2.5, sx * 5.6 + 2.5, -32, -5, Z, Z + 4.4)
        b.bx("SandstoneLight", sx * 5.6 - 2.7, sx * 5.6 + 2.7, -33.6, -31.4, Z, Z + 2.4)
        for t in (-1.6, -0.55, 0.55, 1.6):
            b.cyl("SandstoneDark", (sx * 5.6 + t, -33.7, Z + 0.4), (sx * 5.6 + t, -33.7, Z + 2.2), 0.12, 4)
    b.tube("Sandstone", [(9.0, 31, Z + 1.0), (10.6, 24, Z + 0.8), (10.8, 14, Z + 0.8), (10.4, 6, Z + 1.2), (9.8, 2, Z + 2.0)], 0.9, 6)
    b.ball("Sandstone", (9.8, 1.4, Z + 2.2), 1.3, seg=(8, 6))
    # neck + head
    b.bx("Sandstone", -4.6, 4.6, -12.0, -4.0, Z + 13, Z + 20)
    nemes_head(b, (0, -10.0, Z + 25.0), s=1.85, face="SandstoneLight", stripe_a="Gold", stripe_b="Turquoise")
    # weathering cracks
    for (x, y, z, rz, ry) in ((8.4, 8, Z + 7, 0.2, 0.6), (-8.2, 14, Z + 6, -0.3, -0.4), (5.6, -26, Z + 4.5, 0.0, 1.57)):
        b.box("SandstoneDark", (x, y, z), (0.25, 3.0, 0.2), rz=rz, ry=ry, bev=0)
    # offering table + braziers
    b.bx("Sandstone", -2.6, 2.6, -29, -25, Z, Z + 3.0)
    b.bx("Gold", -2.2, 2.2, -28.6, -25.4, Z + 3.0, Z + 3.3, bev=0)
    for sx in (-1, 1):
        x = sx * 11.5
        b.cylz("Sandstone", x, -34, 0, 5.0, 1.0, 8)
        b.lathe("Gold", [(0, 0), (0.6, 0), (1.6, 0.8), (1.8, 1.2), (0, 1.1)], c=(x, -34, 5.0), n=10)
        b.cylz("Fire", x, -34, 6.1, 8.4, 1.3, 7, r2=0.0)
    return b


def temple_gate():
    b = Builder("TempleGate", AREA)
    H = 26.0
    for sx in (-1, 1):
        xc = sx * 13.0
        b.mesh("Sandstone", [(xc - 9, -5, 0), (xc + 9, -5, 0), (xc + 9, 5, 0), (xc - 9, 5, 0),
                             (xc - 7.2, -3.8, H), (xc + 7.2, -3.8, H), (xc + 7.2, 3.8, H), (xc - 7.2, 3.8, H)],
               [[3, 2, 1, 0], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7]])
        # torus roll on the edges + cavetto cornice
        b.prism_y("SandstoneLight", [(xc - 7.4, H), (xc + 7.4, H), (xc + 8.6, H + 2.6), (xc - 8.6, H + 2.6)], -4.8, 4.8)
        b.bx("Sandstone", xc - 8.6, xc + 8.6, -5.0, 5.0, H + 2.6, H + 3.4)
        for k in range(9):
            x = xc - 7.2 + k * 1.8
            b.bx("Turquoise" if k % 2 else "Gold", x - 0.8, x + 0.8, -4.85, -4.6, H + 0.4, H + 2.2, bev=0)
        # reliefs: a pharaoh figure band + glyph panel
        hiero_panel(b, (xc, -4.35 - 0.2, 8.0), 11.0, 8.0, rz=-0.05 * 0)
        for z in (14.0, 16.0):
            b.bx("Turquoise" if z < 15 else "Navy", xc - 7.6, xc + 7.6, -4.25 - (z - 14) * 0.03, -4.0, z, z + 0.8, bev=0)
        b.bx("SandstoneDark", xc - 6.0, xc + 6.0, -4.25, -4.0, 17.5, 23.5, bev=0)
        with b.at(T(xc, -4.3, 20.5)):
            b.ball("Gold", (0, -0.1, 1.2), 0.9, seg=(8, 6), sc=(1, 0.3, 1))
            b.box("Turquoise", (0, -0.15, -0.6), (1.8, 0.3, 2.6))
            for sx2 in (-1, 1):
                b.box("Gold", (sx2 * 1.9, -0.15, -0.2), (2.4, 0.3, 0.5), ry=sx2 * 0.4)
        # flagpole with pennant in front
        fx = xc - sx * 4.5
        b.cylz("WoodDark", fx, -6.5, 0, H + 10, 0.4, 8)
        b.cylz("Gold", fx, -6.5, H + 10, H + 11, 0.5, 8, r2=0.1)
        b.prism_y("Red", [(fx, H + 9.6), (fx + sx * -0.2 + 5.0 * -sx * -1, H + 8.6), (fx, H + 7.0)], -6.55, -6.45)
    # gateway: jambs, lintel, winged sun disk
    b.bx("SandstoneLight", -5.5, 5.5, -4.6, 4.6, 0, 1.0)
    for sx in (-1, 1):
        b.bx("SandstoneLight", sx * 4.6 - 1.0, sx * 4.6 + 1.0, -4.2, 4.2, 0, 17.0)
        hiero_panel(b, (sx * 4.6, -4.4, 8.5), 1.6, 14.0)
    b.bx("SandstoneLight", -6.6, 6.6, -4.4, 4.4, 17.0, 20.6)
    b.prism_y("SandstoneLight", [(-6.6, 20.6), (6.6, 20.6), (7.6, 22.0), (-7.6, 22.0)], -4.6, 4.6)
    b.cyl("Gold", (0, -4.5, 18.8), (0, -5.0, 18.8), 1.4, 16)
    for sx in (-1, 1):
        for k in range(4):
            b.prism_y("Turquoise" if k % 2 else "Gold",
                      [(sx * 1.4, 19.6 - k * 0.45), (sx * (5.6 - k * 0.6), 19.9 - k * 0.5), (sx * (5.6 - k * 0.6), 19.5 - k * 0.5), (sx * 1.4, 19.2 - k * 0.45)],
                      -4.75, -4.45)
    # braziers on the threshold
    for sx in (-1, 1):
        x = sx * 7.0
        b.cylz("Sandstone", x, -8.0, 0, 3.4, 0.8, 8)
        b.lathe("Gold", [(0, 0), (0.5, 0), (1.4, 0.7), (1.6, 1.1), (0, 1.0)], c=(x, -8.0, 3.4), n=10)
        b.cylz("Fire", x, -8.0, 4.4, 6.6, 1.1, 7, r2=0.0)
    return b


def bazaar_stalls():
    b = Builder("BazaarStalls", AREA)
    cloths = (("Red", "Cream"), ("Teal", "Cream"), ("Purple", "Yellow"))
    for i, (ca, cb) in enumerate(cloths):
        cx = (i - 1) * 13.0
        with b.at(T(cx, 0, 0)):
            for x in (-5.5, 5.5):
                for y in (-4.0, 4.0):
                    b.cylz("WoodDark", x, y, 0, 9.0 if y > 0 else 8.0, 0.25, 6)
            # sagging striped cloth roof
            n = 8
            for k in range(n):
                x0 = -6.2 + k * 12.4 / n
                x1 = x0 + 12.4 / n
                sag = lambda x: 0.6 * math.cos((x / 6.2) * PI / 2)
                st = ca if k % 2 else cb
                b.mesh(st, [(x0, -5.0, 8.2 - sag(x0)), (x1, -5.0, 8.2 - sag(x1)), (x1, 4.6, 9.2 - sag(x1)), (x0, 4.6, 9.2 - sag(x0)),
                            (x0, -5.0, 8.4 - sag(x0)), (x1, -5.0, 8.4 - sag(x1)), (x1, 4.6, 9.4 - sag(x1)), (x0, 4.6, 9.4 - sag(x0))],
                       [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [3, 2, 6, 7]])
            for k in range(8):
                x = -5.8 + k * 1.65
                b.prism_y(ca, [(x - 0.8, 8.2), (x + 0.8, 8.2), (x, 7.1)], -5.05, -4.95)
            # counter
            b.bx("WoodLight", -5.2, 5.2, -4.0, -1.6, 0, 3.4)
            b.bx("WoodDark", -5.4, 5.4, -4.2, -1.4, 3.4, 3.8)
            b.bx(ca, -5.0, 5.0, -4.15, -4.05, 0.4, 3.0, bev=0)
            for k in range(5):
                b.bx(cb, -4.6 + k * 2.1, -4.1 + k * 2.1, -4.2, -4.12, 0.6, 2.8, bev=0)
            if i == 0:
                # spice baskets
                for k, col in enumerate(("Orange", "Red", "Yellow", "Chocolate", "Green")):
                    x = -4.0 + k * 2.0
                    b.lathe("Thatch", [(0, 0), (0.8, 0), (0.95, 0.7), (0, 0.7)], c=(x, -2.8, 3.8), n=10)
                    b.cylz(col, x, -2.8, 4.4, 5.6, 0.85, 10, r2=0.0)
            elif i == 1:
                # pottery
                for k in range(5):
                    x = -4.0 + k * 2.0
                    col = ("Adobe", "Teal", "AdobeLight", "Navy", "Adobe")[k]
                    b.lathe(col, [(0, 0), (0.5, 0), (0.9, 0.6), (0.8, 1.3), (0.35, 1.7), (0.45, 2.0), (0, 2.0)], c=(x, -2.8, 3.8), n=10)
            else:
                # brass lamps + rugs
                for k in range(4):
                    x = -3.6 + k * 2.4
                    b.cylz("Rope", x, -3.0, 6.0, 8.0, 0.04, 3)
                    b.lathe("Brass", [(0, 0), (0.5, 0.2), (0.7, 0.8), (0.3, 1.4), (0, 1.6)], c=(x, -3.0, 4.6), n=8)
                    b.ball("Fire", (x, -3.0, 5.2), 0.25, seg=(6, 4))
                for k, col in enumerate(("Red", "Navy", "Purple")):
                    b.cyl(col, (-4 + k * 3.6, -2.4, 4.4), (-4 + k * 3.6 + 2.6, -2.8, 4.4), 0.55, 10)
            # hanging rug on the back
            b.bx(cloths[(i + 1) % 3][0], -4.0, 4.0, 3.9, 4.1, 1.5, 7.5)
            b.bx(cloths[(i + 2) % 3][1], -3.4, 3.4, 3.8, 3.9, 2.1, 6.9, bev=0)
            b.bx(cloths[(i + 1) % 3][0], -2.0, 2.0, 3.75, 3.8, 3.3, 5.7, bev=0)
            b.cyl("WoodDark", (-4.6, 4.0, 7.6), (4.6, 4.0, 7.6), 0.15, 5)
    # crates + sacks between
    for k, (x, y) in enumerate(((-19.5, -2.0), (-19.5, 1.0), (19.5, -1.0))):
        b.bx("WoodLight", x - 1.2, x + 1.2, y - 1.2, y + 1.2, 0, 2.2)
        b.bx("WoodDark", x - 1.25, x + 1.25, y - 1.25, y + 1.25, 0.9, 1.2, bev=0)
    for k in range(3):
        b.ball("Cream", (6.6 + k * 1.3, -5.6, 1.0), 1.0, seg=(8, 6), sc=(0.7, 0.6, 1.0))
    return b


def mud_brick_house():
    b = Builder("MudBrickHouse", AREA)
    b.bx("Adobe", -10, 6, -7, 7, 0, 10.0, bev=0.6)
    b.bx("AdobeLight", 6, 12, -4, 7, 0, 6.5, bev=0.5)
    b.bx("Adobe", -10, -1, -1, 7, 10.0, 16.0, bev=0.5)
    # parapets
    for (x0, x1, y0, y1, z) in ((-10, 6, -7, 7, 10.0), (-10, -1, -1, 7, 16.0), (6, 12, -4, 7, 6.5)):
        for (a0, a1, b0, b1) in ((x0, x1, y0, y0 + 0.6), (x0, x1, y1 - 0.6, y1), (x0, x0 + 0.6, y0, y1), (x1 - 0.6, x1, y0, y1)):
            b.bx("Adobe" if z != 6.5 else "AdobeLight", a0, a1, b0, b1, z, z + 1.4, bev=0.2)
    # vigas (roof beams poking out)
    for z, ys, xr in ((9.0, (-5, -2, 1, 4), (-10, 6)), (15.0, (1, 4), (-10, -1))):
        for y in ys:
            for x in xr:
                b.cyl("WoodDark", (x - (0.9 if x < 0 else -0.9), y, z), (x + (-0.4 if x < 0 else 0.4) * 0, y, z), 0.32, 6)
    for x in (-8, -5, -2, 1, 4):
        b.cyl("WoodDark", (x, -7.9, 9.0), (x, -6.6, 9.0), 0.32, 6)
    # domed room on the roof corner
    b.dome("AdobeLight", (2.5, 3.5, 10.0), 3.0, seg=14, rings=4)
    b.ball("Turquoise", (2.5, 3.5, 13.2), 0.35, seg=(6, 4))
    # arched turquoise door, small shuttered windows
    b.door("Turquoise", "AdobeLight", (-4.0, -7.1, 0), 3.2, 5.6, arch=True, knob="Brass", ft=0.6)
    for (x, z) in ((2.0, 5.5), (-8.0, 5.5), (-6.5, 13.0), (-3.0, 13.0)):
        y = -7.1 if z < 10 else -1.1
        b.box("Charcoal", (x, y, z), (1.6, 0.2, 1.8), bev=0)
        b.arch("AdobeLight", (x, y - 0.1, z + 0.9), 0.8, 1.2, 0.4, n=6)
        b.box("WoodDark", (x - 1.3, y - 0.15, z), (0.8, 0.2, 1.9), rz=0.25)
        b.box("WoodDark", (x + 1.3, y - 0.15, z), (0.8, 0.2, 1.9), rz=-0.25)
    # outside stair to the roof
    with b.at(T(7.9, -10.5, 0)):
        for i in range(10):
            b.bx("AdobeLight", -1.3, 1.3, i * 0.6, i * 0.6 + 0.6, 0, 1.0 * (i + 1), bev=0.15)
    # awning + jars + a mat
    with b.at(T(-4.0, -8.8, 6.6), R(-0.5, 0, 0)):
        for k in range(5):
            b.box("Red" if k % 2 else "Cream", (-2.4 + k * 1.2, 0, 0), (1.2, 3.4, 0.2), bev=0)
    for sx in (-1.8, 1.8):
        b.cyl("WoodDark", (-4.0 + sx * 1.5, -7.2, 6.2), (-4.0 + sx * 1.5, -10.0, 5.3), 0.1, 4)
    for k, (x, y) in enumerate(((-9.0, -8.6), (-7.6, -8.9), (3.5, -8.4))):
        b.lathe(("Adobe", "AdobeLight", "Teal")[k], [(0, 0), (0.6, 0), (1.1, 0.8), (1.0, 1.8), (0.45, 2.3), (0.55, 2.7), (0, 2.7)], c=(x, y, 0), n=10)
    b.bx("Purple", -6.0, -2.0, -11.0, -7.4, 0, 0.08, bev=0)
    b.bx("Yellow", -5.6, -2.4, -10.6, -7.8, 0.08, 0.1, bev=0)
    return b


def oasis_pool():
    b = Builder("OasisPool", AREA)
    rng = b.rng
    # irregular pond outline
    n = 22
    rad = [10.0 + 1.8 * math.sin(TAU * k / n * 2 + 0.5) + 1.1 * math.cos(TAU * k / n * 3) for k in range(n)]
    pts = [(math.cos(TAU * k / n) * rad[k] * 1.3, math.sin(TAU * k / n) * rad[k]) for k in range(n)]
    b.prism_z("Water", pts, 0.0, 0.6)
    b.prism_z("Grass", [(x * 1.18, y * 1.18) for x, y in pts], 0.0, 0.25)
    for k in range(n):
        if k % 2 == 0:
            x, y = pts[k]
            b.rock("Sandstone" if k % 4 else "SandstoneDark", (x * 1.08, y * 1.08, 0.4), rng.uniform(1.0, 1.8), sc=(1.3, 1, 0.6))
    for k in range(14):
        x, y = pts[rng.randrange(n)]
        f = rng.uniform(1.12, 1.3)
        for j in range(4):
            b.cyl("Grass" if j % 2 else "LeafDark", (x * f, y * f, 0.2), (x * f + rng.uniform(-0.5, 0.5), y * f + rng.uniform(-0.5, 0.5), rng.uniform(2.0, 3.6)), 0.12, 4, r2=0.02)
    date_palm(b, (pts[3][0] * 1.25, pts[3][1] * 1.25, 0), h=17, lean=(0.2, 0.1), seed=0.1)
    date_palm(b, (pts[9][0] * 1.22, pts[9][1] * 1.22, 0), h=14, lean=(-0.15, 0.05), seed=0.5)
    date_palm(b, (pts[15][0] * 1.24, pts[15][1] * 1.24, 0), h=19, lean=(0.05, -0.2), seed=0.9)
    date_palm(b, (pts[19][0] * 1.3, pts[19][1] * 1.3, 0), h=12, lean=(0.1, -0.1), seed=1.3)
    for (x, y) in ((-3, 2), (4, -3), (1, 5)):
        b.cylz("LeafLight", x, y, 0.6, 0.7, 0.9, 10)
        b.ball("Flower", (x + 0.3, y, 0.9), 0.3, seg=(6, 4))
    return b


def desert_well():
    b = Builder("DesertWell", AREA)
    b.ring("Sandstone", (0, 0, 0), 3.4, 2.4, 0, 3.4, n=16)
    b.ring("SandstoneLight", (0, 0, 0), 3.6, 2.3, 3.4, 3.9, n=16)
    b.cylz("Water", 0, 0, 1.6, 1.8, 2.4, 16)
    for k in range(16):
        a = TAU * k / 16 + (0.2 if k % 2 else 0)
        z = 0.6 + (k % 3) * 1.0
        b.box("SandstoneDark", (math.cos(a) * 3.45, math.sin(a) * 3.45, z), (1.2, 0.3, 0.6), rz=a + PI / 2, bev=0.05)
    for sx in (-1, 1):
        b.bx("WoodDark", sx * 3.0 - 0.3, sx * 3.0 + 0.3, -0.3, 0.3, 3.4, 9.5)
    b.cyl("WoodDark", (-3.6, 0, 8.0), (3.9, 0, 8.0), 0.3, 8)
    b.cyl("Rope", (-1.2, 0, 8.0), (1.2, 0, 8.0), 0.5, 10)
    b.cyl("WoodDark", (3.9, 0, 8.0), (3.9, 0, 6.8), 0.15, 5)
    b.cyl("WoodDark", (3.9, 0, 6.8), (4.6, 0, 6.8), 0.15, 5)
    b.cylz("Rope", 0, 0, 5.4, 7.6, 0.06, 4)
    b.lathe("WoodLight", [(0, 0), (0.7, 0), (0.85, 1.2), (0, 1.2)], c=(0, 0, 4.2), n=10)
    b.torus("DarkMetal", (0, 0, 4.9), 0.85, 0.08, 10, 3, rx=PI / 2)
    with b.at(R(0, 0, PI / 2)):
        b.gable_roof("WoodRed", 0, 0, 9.5, 2.0, 7.6, 2.0, t=0.3, over=0.6)
    b.lathe("Adobe", [(0, 0), (0.6, 0), (1.0, 0.8), (0.9, 1.8), (0.4, 2.2), (0.5, 2.5), (0, 2.5)], c=(4.6, -2.6, 0), n=10)
    return b


def colonnade():
    b = Builder("Colonnade", AREA)
    rng = b.rng
    b.bx("SandstoneDark", -16, 16, -4, 4, 0, 1.0)
    heights = (18.0, 18.0, 12.0, 18.0, 7.0, 18.0)
    for k, h in enumerate(heights):
        x = -12.5 + k * 5.0
        b.bx("Sandstone", x - 1.8, x + 1.8, -1.8, 1.8, 1.0, 2.0)
        nd = int((h - 2.0) / 2.0)
        for d in range(nd):
            z = 2.0 + d * 2.0
            b.cylz("Sandstone" if d % 2 else "SandstoneLight", x + rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), z, z + 2.0, 1.3, 12)
            if d % 3 == 1:
                b.torus("SandstoneDark", (x, 0, z + 1.0), 1.32, 0.1, 12, 3)
        if h >= 17:
            b.lathe("SandstoneLight", [(0, h), (1.3, h), (2.2, h + 1.4), (2.2, h + 1.8), (0, h + 1.8)], c=(x, 0, 0), n=12)
            for j in range(8):
                a = TAU * j / 8
                b.box("Turquoise" if j % 2 else "Gold", (x + math.cos(a) * 1.9, math.sin(a) * 1.9, h + 0.8), (0.5, 0.25, 1.2), rz=a + PI / 2, bev=0)
        else:
            b.rock("SandstoneLight", (x, 0, h + 0.2), 1.3, sc=(1.0, 1.0, 0.35), jitter=0.3)
    # lintels on the standing pairs
    for (i0, i1) in ((0, 1), (3, 5)):
        x0, x1 = -12.5 + i0 * 5.0, -12.5 + i1 * 5.0
        if i1 - i0 == 2:
            b.bx("SandstoneLight", x0 - 2.2, x1 + 2.2, -2.2, 2.2, 19.8, 22.2)
            hiero_panel(b, ((x0 + x1) / 2, -2.25, 21.0), x1 - x0 + 2, 1.6)
        else:
            b.bx("SandstoneLight", x0 - 2.2, x1 + 2.2, -2.2, 2.2, 19.8, 22.2)
            hiero_panel(b, ((x0 + x1) / 2, -2.25, 21.0), x1 - x0 + 2, 1.6)
    # fallen drums + broken lintel + sand drifts
    for k, (x, y, rz) in enumerate(((-7, -7.5, 0.3), (-3.5, -8.0, 0.1), (2.5, -7.0, -0.4), (9.0, 7.5, 1.2))):
        with b.at(T(x, y, 1.3), R(0, PI / 2, rz)):
            b.cylz("Sandstone", 0, 0, -1.0, 1.0, 1.3, 12)
    b.box("SandstoneLight", (13, -7.5, 1.0), (9.0, 4.4, 2.2), rz=0.35, ry=0.08)
    for (x, y) in ((-14, -5), (6, 5), (14, 4)):
        b.dome("Sand", (x, y, 0), 3.0, seg=12, rings=4, sc=(1.6, 1.0, 0.45))
    return b


def bedouin_tent():
    b = Builder("BedouinTent", AREA)
    W, D = 22.0, 14.0
    # tensioned roof: a grid sagging between the pole tops
    poles = [(-W / 2 + 2, 0, 9.0), (0, 0, 10.0), (W / 2 - 2, 0, 9.0)]
    nx, ny = 12, 8

    def roof_z(x, y):
        z = 5.0
        for (px, py, ph) in poles:
            d = math.hypot((x - px) / 5.5, (y - py) / 4.5)
            z = max(z, ph - 3.4 * d * d)
        edge = max(abs(x) / (W / 2), abs(y) / (D / 2))
        return min(z, 5.2 + (1 - edge) * 6.0) if edge > 0.85 else z
    for i in range(nx):
        for j in range(ny):
            x0 = -W / 2 + i * W / nx
            x1 = x0 + W / nx
            y0 = -D / 2 + j * D / ny
            y1 = y0 + D / ny
            st = "Chocolate" if (j + (i // 3)) % 2 else "WoodDark"
            if j in (2, 5):
                st = "Red" if i % 2 else "Cream"
            v = [(x0, y0, roof_z(x0, y0)), (x1, y0, roof_z(x1, y0)), (x1, y1, roof_z(x1, y1)), (x0, y1, roof_z(x0, y1))]
            v2 = [(p[0], p[1], p[2] - 0.15) for p in v]
            b.mesh(st, v + v2, [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]])
    for (px, py, ph) in poles:
        b.cylz("WoodLight", px, py, 0, ph, 0.25, 6)
    for x in (-W / 2, -W / 4, 0, W / 4, W / 2):
        for y in (-D / 2, D / 2):
            b.cylz("WoodLight", x, y, 0, roof_z(x, y), 0.18, 5)
            out = 3.2 if y > 0 else -3.2
            b.cyl("Rope", (x, y, roof_z(x, y)), (x, y + out, 0.2), 0.06, 3)
            b.cylz("WoodDark", x, y + out, 0, 0.8, 0.15, 4)
    # back + side walls, open front
    b.bx("Chocolate", -W / 2, W / 2, D / 2 - 0.2, D / 2, 0, 5.2, bev=0)
    for sx in (-1, 1):
        b.bx("Chocolate", sx * W / 2 - 0.1, sx * W / 2 + 0.1, -D / 2 + 3, D / 2, 0, 5.2, bev=0)
    # rugs, cushions, a low table, lantern
    b.bx("Red", -8, 8, -5, 6, 0, 0.1, bev=0)
    b.bx("Navy", -6.5, 6.5, -3.6, 4.6, 0.1, 0.14, bev=0)
    b.bx("Yellow", -4.5, 4.5, -2.0, 3.0, 0.14, 0.17, bev=0)
    for k, col in enumerate(("Purple", "Orange", "Teal", "Red", "Yellow")):
        x = -6 + k * 3.0
        b.ball(col, (x, 4.8, 0.9), 1.0, seg=(10, 6), sc=(1.3, 0.9, 0.7))
    b.cylz("WoodDark", 0, 0.5, 0.17, 1.4, 0.3, 6)
    b.cylz("Brass", 0, 0.5, 1.4, 1.6, 2.2, 14)
    b.lathe("Brass", [(0, 0), (0.4, 0), (0.6, 0.6), (0.3, 1.0), (0.12, 1.6), (0, 1.6)], c=(0.6, 0.5, 1.6), n=8)
    for k in range(3):
        b.cylz("White", -0.8 + k * 0.5, 0.0, 1.6, 2.0, 0.2, 6)
    b.cylz("Rope", 0, 0, 7.0, 9.6, 0.04, 3)
    b.lathe("Brass", [(0, 0), (0.5, 0.2), (0.7, 0.8), (0.3, 1.4), (0, 1.6)], c=(0, 0, 5.4), n=8)
    b.ball("Fire", (0, 0, 6.0), 0.3, seg=(6, 4))
    return b


def pharaoh_statue():
    b = Builder("PharaohStatue", AREA)
    b.bx("SandstoneDark", -6, 6, -9, 7, 0, 2.0)
    hiero_panel(b, (0, -9.0, 1.0), 10.0, 1.4)
    Z = 2.0
    # throne
    b.bx("Sandstone", -5, 5, -1, 6.5, Z, Z + 7.5)
    b.bx("Sandstone", -5, 5, 4.0, 6.5, Z + 7.5, Z + 16.0)
    for sx in (-1, 1):
        b.bx("Turquoise", sx * 5.0 - 0.15, sx * 5.0 + 0.15, 0, 5.5, Z + 1.0, Z + 6.5, bev=0)
        b.bx("Gold", sx * 5.0 - 0.2, sx * 5.0 + 0.2, 0.5, 5.0, Z + 1.5, Z + 6.0, bev=0)
    # seated figure: shins, thighs, torso, arms on knees
    for sx in (-1, 1):
        x = sx * 2.0
        b.bx("SandstoneLight", x - 1.5, x + 1.5, -7.0, -4.0, Z, Z + 7.5)
        b.bx("SandstoneLight", x - 1.6, x + 1.6, -8.4, -3.8, Z, Z + 1.0)
        b.bx("SandstoneLight", x - 1.6, x + 1.6, -7.2, 1.0, Z + 7.5, Z + 10.2)
        b.bx("SandstoneLight", x * 1.9 - 0.9, x * 1.9 + 0.9, -3.5, 2.0, Z + 10.0, Z + 17.5)
        b.bx("SandstoneLight", x * 1.9 - 1.0, x * 1.9 + 1.0, -6.6, -2.0, Z + 10.0, Z + 11.6)
        b.box("SandstoneLight", (x * 1.6, -6.4, Z + 11.0), (1.6, 1.6, 1.4), bev=0.2)
    b.bx("Cream", -3.7, 3.7, -7.4, -2.0, Z + 6.8, Z + 10.3)
    for k in range(7):
        x = -3.0 + k * 1.0
        b.bx("Gold", x - 0.2, x + 0.2, -7.5, -7.3, Z + 7.0, Z + 10.2, bev=0)
    b.bx("SandstoneLight", -3.0, 3.0, -2.5, 3.0, Z + 10.0, Z + 18.0)
    b.bx("Turquoise", -3.1, 3.1, -2.7, -2.4, Z + 15.0, Z + 17.5)
    for k in range(4):
        b.bx("Gold" if k % 2 else "Navy", -3.1, 3.1, -2.75, -2.45, Z + 15.0 + k * 0.6, Z + 15.3 + k * 0.6, bev=0)
    nemes_head(b, (0, -0.5, Z + 21.0), s=1.0, face="SandstoneLight", stripe_a="Gold", stripe_b="Navy")
    # double crown on top
    b.lathe("White", [(0, 0), (1.6, 0), (1.2, 2.6), (0.7, 3.6), (0, 3.9)], c=(0, -0.2, Z + 25.6), n=10)
    b.ball("White", (0, -0.2, Z + 29.6), 0.55, seg=(8, 6))
    return b


def pottery_cart():
    b = Builder("PotteryCart", AREA)
    for sx in (-1, 1):
        b.cyl("WoodDark", (sx * 3.6, 0, 2.6), (sx * 4.0, 0, 2.6), 2.6, 14)
        b.cyl("WoodLight", (sx * 3.55, 0, 2.6), (sx * 4.05, 0, 2.6), 0.6, 8)
        for k in range(8):
            a = TAU * k / 8
            b.cyl("WoodLight", (sx * 3.8, 0, 2.6), (sx * 3.8, math.cos(a) * 2.3, 2.6 + math.sin(a) * 2.3), 0.12, 4)
        b.torus("DarkMetal", (sx * 3.8, 0, 2.6), 2.55, 0.12, 16, 4, ry=PI / 2)
    b.cyl("WoodDark", (-3.6, 0, 2.6), (3.6, 0, 2.6), 0.25, 6)
    b.bx("Plank", -3.3, 3.3, -4.0, 4.0, 3.2, 3.7)
    for sx in (-1, 1):
        b.bx("WoodLight", sx * 3.3 - 0.2, sx * 3.3 + 0.2, -4.0, 4.0, 3.7, 5.0)
    b.bx("WoodLight", -3.3, 3.3, 3.8, 4.0, 3.7, 5.0)
    for sx in (-1, 1):
        b.cyl("WoodDark", (sx * 1.6, -4.0, 3.4), (sx * 1.2, -10.0, 1.6), 0.18, 5)
    b.cyl("WoodDark", (-1.4, -9.6, 1.7), (1.4, -9.6, 1.7), 0.12, 4)
    cols = ("Adobe", "AdobeLight", "Teal", "Adobe", "Navy", "AdobeLight")
    for k in range(6):
        x = -2.0 + (k % 3) * 2.0
        y = -2.0 + (k // 3) * 3.2
        h = 2.4 + (k % 2) * 0.8
        b.lathe(cols[k], [(0, 0), (0.6, 0), (1.0, h * 0.35), (0.9, h * 0.7), (0.4, h * 0.9), (0.55, h), (0, h)], c=(x, y, 3.7), n=10)
    b.cyl("Red", (-3.0, 3.0, 6.2), (3.0, 3.0, 6.2), 0.7, 10)
    b.torus("Yellow", (3.0, 3.0, 6.2), 0.5, 0.15, 8, 4, ry=PI / 2)
    b.torus("Yellow", (-3.0, 3.0, 6.2), 0.5, 0.15, 8, 4, ry=PI / 2)
    return b


ASSETS = [sphinx, temple_gate, bazaar_stalls, mud_brick_house, oasis_pool, desert_well, colonnade,
          bedouin_tent, pharaoh_statue, pottery_cart]
