"""Area 4 -- Theme Park: candy colours, white trim, striped canopies, bulb lights."""
import math

from mathutils import Matrix

from kit import PI, TAU, Builder, R, T, V, catenary, rmf_frames

AREA = "ThemePark"
GROUND = (232, 170, 200)
BULB = "NeonYellow"


def frame_matrix(p, fr):
    t, n, bn = fr
    return Matrix(((bn.x, t.x, n.x, p.x), (bn.y, t.y, n.y, p.y), (bn.z, t.z, n.z, p.z), (0, 0, 0, 1)))


def catmull_closed(ctrl, per=10):
    pts = []
    n = len(ctrl)
    for i in range(n):
        p0, p1, p2, p3 = ctrl[i - 1], ctrl[i], ctrl[(i + 1) % n], ctrl[(i + 2) % n]
        for k in range(per):
            t = k / per
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    return pts


def resample_closed(pts, step):
    L = [0.0]
    for i in range(1, len(pts) + 1):
        L.append(L[-1] + (pts[i % len(pts)] - pts[i - 1]).length)
    total = L[-1]
    n = int(total / step)
    out = []
    j = 0
    for k in range(n):
        s = k * total / n
        while L[j + 1] < s:
            j += 1
        f = (s - L[j]) / max(L[j + 1] - L[j], 1e-9)
        out.append(pts[j].lerp(pts[(j + 1) % len(pts)], f))
    return out


def closed_frames(pts):
    fr = rmf_frames(pts, closed=True)
    t0, n0, _ = fr[0]
    tN, nN, bN = fr[-1]
    # carry the last frame one step on and measure the twist against the first
    ang = math.atan2(nN.cross(n0).dot(t0), nN.dot(n0))
    out = []
    N = len(pts)
    for i, (t, n, bn) in enumerate(fr):
        a = ang * i / N
        q = Matrix.Rotation(a, 3, t)
        n2 = (q @ n).normalized()
        out.append((t, n2, t.cross(n2).normalized()))
    return out


def roller_coaster():
    b = Builder("RollerCoaster", AREA)
    ctrl = [V(p) for p in [
        (22, -14, 5.0), (8, -14, 5.0), (-6, -14, 5.0), (-20, -14, 5.5),
        (-32, -10, 8), (-38, 0, 13), (-32, 11, 19),
        (-22, 14, 27), (-12, 14, 36), (-4, 14, 41), (3, 14, 40), (9, 14, 30), (14, 14, 16), (19, 14, 7), (24, 14, 4.2)]]
    cx, zb, Rl = 34.0, 4.0, 11.0
    for k in range(1, 12):
        th = TAU * k / 12
        ctrl.append(V((cx - 2 + Rl * math.sin(th) + 4 * k / 12 - 2, 14 - 4.5 * k / 12, zb + Rl * (1 - math.cos(th)))))
    ctrl += [V(p) for p in [(42, 9.5, 4.2), (50, 8.5, 5.5), (58, 2, 8), (57, -8, 9), (48, -14, 8), (36, -14, 6)]]
    path = resample_closed(catmull_closed(ctrl, 12), 0.9)
    frames = closed_frames(path)
    N = len(path)
    rails = {-1: [], 1: []}
    spine = []
    for p, fr in zip(path, frames):
        t, n, bn = fr
        for s in (-1, 1):
            rails[s].append(p + bn * (s * 1.25))
        spine.append(p - n * 0.95)
    for s in (-1, 1):
        b.tube("HotPink", rails[s], 0.28, 6, closed=True, frames=frames)
    b.tube("White", spine, 0.42, 6, closed=True, frames=frames)
    for i in range(0, N, 2):
        with b.at(frame_matrix(path[i], frames[i])):
            b.box("White", (0, 0, -0.45), (2.9, 0.32, 0.3), bev=0)
            b.box("White", (0, 0, -0.75), (0.3, 0.3, 0.6), bev=0)
    # supports: columns from the ground to the spine where nothing passes underneath
    placed = []
    for i in range(0, N, 7):
        p = spine[i]
        if p.z < 2.2:
            continue
        clear = True
        for j in range(N):
            q = path[j]
            if abs(j - i) < 6 or abs(j - i) > N - 6:
                continue
            if (q.xy - p.xy).length < 3.2 and q.z < p.z - 0.5:
                clear = False
                break
        if not clear or any((p.xy - c).length < 5.0 for c in placed):
            continue
        placed.append(p.xy.copy())
        r = 0.55 if p.z < 20 else 0.75
        b.cylz("Lemon", p.x, p.y, 0, p.z - 0.3, r, 8)
        b.cylz("White", p.x, p.y, 0, 0.8, r + 0.6, 8)
        if p.z > 14:
            for k in range(int(p.z / 9)):
                z = 6 + k * 9
                b.torus("White", (p.x, p.y, z), r + 0.05, 0.15, 10, 4)
    # station: platform, roof on posts, sign, queue rail
    b.bx("White", -18, 22, -21.5, -16.0, 0, 3.6)
    b.bx("Mint", -18.4, 22.4, -21.9, -15.6, 3.6, 4.0)
    for x in (-16, -4, 8, 20):
        b.cylz("White", x, -20.5, 4.0, 13.5, 0.45, 8)
        b.cylz("White", x, -8.0, 4.0, 13.5, 0.45, 8)
    b.gable_roof("HotPink", 2, -14.2, 13.5, 40, 14.5, 3.6, t=0.5, over=1.0, ridge="White")
    for x in range(-18, 23, 4):
        b.ball(BULB, (x, -22.6, 13.2), 0.3, seg=(6, 4))
    b.bx("Purple", -6, 10, -23.2, -22.6, 14.6, 18.6)
    b.text("Lemon", "COASTER", (2, -23.35, 16.6), 2.4, depth=0.3, font="black")
    b.stairs("White", (-24, -18.8, 0), 4.2, 6, 0.6, 1.0, rz=-PI / 2)
    for k in range(5):
        x = -17 + k * 8
        b.cylz("Gold", x, -26.0, 0, 3.0, 0.2, 6)
        b.ball("Gold", (x, -26.0, 3.1), 0.32, seg=(6, 4))
    for k in range(4):
        x = -17 + k * 8
        b.tube("Red", catenary((x, -26.0, 2.7), (x + 8, -26.0, 2.7), 0.6, 6), 0.12, 5)
    # a three-car train parked in the station
    i0 = min(range(N), key=lambda i: (path[i] - V((6, -14, 5))).length)
    for c in range(3):
        i = (i0 + c * 5) % N
        with b.at(frame_matrix(path[i], frames[i])):
            b.box("HotPink", (0, 0, 0.9), (3.2, 4.0, 1.6))
            b.box("White", (0, 0, 1.9), (3.3, 4.1, 0.3))
            b.box("Charcoal", (0, 0.4, 1.7), (2.6, 1.4, 0.5), bev=0)
            b.box("Purple", (0, -0.7, 2.4), (2.8, 0.5, 1.6))
            for sx in (-1, 1):
                b.cyl("Charcoal", (sx * 1.25, -1.3, 0.2), (sx * 1.25, -1.3, -0.2), 0.45, 8)
                b.cyl("Charcoal", (sx * 1.25, 1.3, 0.2), (sx * 1.25, 1.3, -0.2), 0.45, 8)
            if c == 0:
                b.ball("HotPink", (0, 2.0, 0.9), 1.0, seg=(10, 6), sc=(1.6, 1.2, 0.8))
                for sx in (-0.8, 0.8):
                    b.ball(BULB, (sx, 2.9, 1.2), 0.3, seg=(6, 4))
    return b


def horse(b, col, mane, c, rz, bob=0.0):
    with b.at(T(c), R(0, 0, rz)):
        z = 4.6 + bob
        b.ball(col, (0, 0, z), 1.0, seg=(12, 8), sc=(2.3, 0.95, 1.05))
        b.cyl(col, (1.6, 0, z + 0.4), (2.4, 0, z + 2.0), 0.6, 8, r2=0.48)
        b.ball(col, (2.75, 0, z + 2.2), 1.0, seg=(10, 6), sc=(1.0, 0.55, 0.62), ry=0.5)
        b.ball("Black", (2.8, -0.45, z + 2.55), 0.13, seg=(6, 4))
        b.ball("Black", (2.8, 0.45, z + 2.55), 0.13, seg=(6, 4))
        for sy in (-0.25, 0.25):
            b.cyl(col, (2.35, sy, z + 2.6), (2.25, sy, z + 3.2), 0.16, 5, r2=0.02)
        for k in range(6):
            t = k / 5
            b.ball(mane, (1.35 + t * 1.0, 0, z + 1.2 + t * 1.3), 0.32, seg=(6, 4), sc=(1, 0.8, 1.2))
        b.tube(mane, [(-2.1, 0, z + 0.3), (-2.8, 0, z - 0.2), (-3.0, 0, z - 1.2)], 0.28, 6)
        legs = [((1.3, -0.45), (2.3, -0.45), 0.7), ((1.3, 0.45), (1.9, 0.45), 1.2), ((-1.4, -0.45), (-2.4, -0.45), -0.6),
                ((-1.4, 0.45), (-2.0, 0.45), -1.0)]
        for (hx, hy), (fx, fy), lift in legs:
            knee = (fx * 0.6 + hx * 0.4, hy, z - 1.3 + abs(lift) * 0.2)
            b.cyl(col, (hx, hy, z - 0.4), knee, 0.3, 6)
            b.cyl(col, knee, (fx, fy, z - 2.1 + abs(lift) * 0.5), 0.26, 6)
            b.cylz("Gold", fx, fy, z - 2.35 + abs(lift) * 0.5, z - 2.05 + abs(lift) * 0.5, 0.3, 6)
        b.box("Red", (0, 0, z + 0.95), (1.5, 2.0, 0.35))
        b.box("Gold", (0, 0, z + 0.85), (1.6, 2.1, 0.12), bev=0)
        for sy in (-1.05, 1.05):
            b.box("Gold", (0.1, sy, z - 0.3), (0.12, 0.1, 1.6), bev=0)
            b.box("Gold", (0.1, sy, z - 1.1), (0.5, 0.2, 0.12), bev=0)


def carousel():
    b = Builder("Carousel", AREA)
    b.lathe("White", [(0, 0), (14.0, 0), (14.0, 0.8), (13.0, 0.8), (13.0, 1.6), (0, 1.6)], n=32)
    b.ring("Pink", (0, 0, 0), 13.1, 12.6, 1.6, 2.0, n=32)
    for k in range(32):
        a = TAU * (k + 0.5) / 32
        if k % 2 == 0:
            b.mesh("Lilac", [(0, 0, 1.62), (math.cos(a - TAU / 64) * 12.4, math.sin(a - TAU / 64) * 12.4, 1.62),
                             (math.cos(a + TAU / 64) * 12.4, math.sin(a + TAU / 64) * 12.4, 1.62)], [[0, 1, 2]])
    # centre drum with mirror panels
    b.lathe("Mint", [(0, 1.6), (3.6, 1.6), (3.6, 17.0), (0, 17.0)], n=12)
    for k in range(12):
        a = TAU * (k + 0.5) / 12
        with b.at(T(math.cos(a) * 3.5, math.sin(a) * 3.5, 0), R(0, 0, a + PI / 2)):
            b.bx("Gold", -0.7, 0.7, -0.3, 0.05, 3.0, 15.5)
            b.bx("Glass", -0.5, 0.5, -0.4, -0.2, 3.4, 15.0, bev=0)
    # crown band + canopy
    b.ring("Purple", (0, 0, 0), 14.0, 13.2, 15.2, 17.4, n=32)
    b.ring("Gold", (0, 0, 0), 14.25, 13.0, 17.4, 17.8, n=32)
    b.ring("Gold", (0, 0, 0), 14.25, 13.0, 14.9, 15.2, n=32)
    for k in range(32):
        a = TAU * k / 32
        b.ball(BULB, (math.cos(a) * 14.25, math.sin(a) * 14.25, 16.3), 0.32, seg=(6, 4))
        if k % 2 == 0:
            b.box("Pink", (math.cos(a) * 14.15, math.sin(a) * 14.15, 16.3), (0.6, 2.2, 1.6), rz=a)
    b.striped_canopy("HotPink", "White", (0, 0), 15.0, 7.0, n=16, z=17.8)
    b.cylz("Gold", 0, 0, 24.4, 26.0, 0.9, 10, r2=0.4)
    b.ball("Gold", (0, 0, 26.4), 0.8, seg=(10, 8))
    b.cylz("White", 0, 0, 26.6, 30.0, 0.12, 6)
    b.prism_y("Lemon", [(0.1, 29.9), (0.1, 28.0), (2.8, 29.0)], -0.08, 0.08)
    # poles + horses (two rings, alternate heights)
    cols = ("White", "Pink", "SkyBlue", "Lilac", "Lemon", "Mint")
    manes = ("HotPink", "Purple", "Lemon", "Pink", "Orange", "SkyBlue")
    for ring_i, (rr, n, off) in enumerate(((10.4, 12, 0.0), (7.0, 8, 0.4))):
        for k in range(n):
            a = TAU * k / n + off
            x, y = math.cos(a) * rr, math.sin(a) * rr
            bob = 0.8 * math.sin(k * 1.7)
            b.cylz("Gold", x, y, 1.6, 15.2, 0.16, 6)
            for j in range(10):
                z = 2.4 + j * 1.3
                b.torus("Gold", (x, y, z), 0.2, 0.07, 6, 3, rx=0.5, rz=a)
            horse(b, cols[(k + ring_i) % 6], manes[(k + ring_i) % 6], (x, y, 1.6 - 2.2), a + PI / 2, bob)
    # entry steps + queue posts
    b.stairs("White", (0, -16.0, 0), 5.0, 2, 0.8, 1.0, rz=0)
    return b


def castle_gate():
    b = Builder("CastleGate", AREA)
    # wall with a big arched opening
    W, D = 30.0, 6.0
    b.bx("Cream", -W / 2, -7.0, -D / 2, D / 2, 0, 22)
    b.bx("Cream", 7.0, W / 2, -D / 2, D / 2, 0, 22)
    b.bx("Cream", -7.0, 7.0, -D / 2, D / 2, 15.0, 22)
    pts = [(-7.0, 15.0)] + [(math.cos(PI - PI * i / 12) * 7.0, 8.0 + math.sin(PI - PI * i / 12) * 7.0) for i in range(13)] + [(7.0, 15.0)]
    b.prism_y("Cream", pts, -D / 2, D / 2)
    b.arch("Pink", (0, -D / 2 - 0.2, 8.0), 7.0, 8.6, 0.8, n=14)
    for sx in (-1, 1):
        b.bx("Pink", sx * 7.8 - 0.8, sx * 7.8 + 0.8, -D / 2 - 0.6, -D / 2 + 0.2, 0, 8.0)
    for k in range(15):
        a = PI * k / 14
        b.ball(BULB, (math.cos(a) * 9.1, -D / 2 - 0.65, 8.0 + math.sin(a) * 9.1), 0.32, seg=(6, 4))
    for k in range(5):
        b.ball(BULB, (-9.1, -D / 2 - 0.65, 0.8 + k * 1.6), 0.32, seg=(6, 4))
        b.ball(BULB, (9.1, -D / 2 - 0.65, 0.8 + k * 1.6), 0.32, seg=(6, 4))
    # stone bands + crenellations
    for z in (6.0, 12.0):
        for (x0, x1) in ((-W / 2, -8.6), (8.6, W / 2)):
            b.bx("White", x0, x1, -D / 2 - 0.25, D / 2 + 0.25, z, z + 0.6)
    b.bx("White", -W / 2 - 0.3, W / 2 + 0.3, -D / 2 - 0.4, D / 2 + 0.4, 21.6, 22.6)
    for k in range(8):
        x = -12.8 + k * 3.66
        b.bx("Cream", x - 0.9, x + 0.9, -D / 2 - 0.3, -D / 2 + 1.2, 22.6, 24.8)
        b.bx("Cream", x - 0.9, x + 0.9, D / 2 - 1.2, D / 2 + 0.3, 22.6, 24.8)
    # banner over the gate
    b.bx("Purple", -9.5, 9.5, -D / 2 - 0.9, -D / 2 - 0.4, 17.0, 20.8)
    b.bx("Gold", -9.9, 9.9, -D / 2 - 1.0, -D / 2 - 0.3, 20.8, 21.3)
    b.bx("Gold", -9.9, 9.9, -D / 2 - 1.0, -D / 2 - 0.3, 16.5, 17.0)
    b.text("Lemon", "FUN PARK", (0, -D / 2 - 1.05, 18.9), 2.6, depth=0.35, font="black")
    # round towers with cone roofs
    for sx in (-1, 1):
        x = sx * (W / 2 + 4.0)
        b.lathe("Lilac", [(0, 0), (6.4, 0), (6.4, 1.0), (6.0, 1.0), (6.0, 27.0), (0, 27.0)], c=(x, 0, 0), n=16)
        for z in (8.0, 17.0):
            b.ring("White", (x, 0, 0), 6.3, 5.8, z, z + 0.6, n=16)
        b.ring("White", (x, 0, 0), 7.0, 5.6, 27.0, 28.2, n=16)
        for k in range(10):
            a = TAU * k / 10
            b.box("Lilac", (x + math.cos(a) * 6.4, math.sin(a) * 6.4, 29.4), (1.6, 1.3, 2.4), rz=a)
        b.lathe("HotPink", [(0, 28.2), (5.6, 28.2), (5.4, 29.0), (0.25, 41.0), (0, 41.0)], c=(x, 0, 0), n=16)
        b.ring("Gold", (x, 0, 0), 5.7, 5.2, 29.0, 29.5, n=16)
        b.cylz("White", x, 0, 41.0, 45.6, 0.14, 6)
        b.prism_y("Lemon" if sx < 0 else "Mint", [(x + 0.1, 45.4), (x + 0.1, 43.2), (x + 3.6, 44.3)], -0.08, 0.08)
        for z in (12.0, 21.5):
            a = -PI / 2 - sx * 0.35
            b.window("Glass", "White", (x + math.cos(a) * 6.05, math.sin(a) * 6.05, z), 1.8, 3.0, rz=a + PI / 2, arch=True, cross=False)
        b.door("Purple", "White", (x - sx * 0.0, -6.0, 0), 3.0, 5.6, rz=0, arch=True)
    # pennant bunting between the towers
    for sag, z in ((3.0, 27.0),):
        pts = catenary((-W / 2 - 4, -6.6, z), (W / 2 + 4, -6.6, z), sag, 26)
        b.tube("White", pts, 0.08, 4)
        cols = ("HotPink", "Lemon", "SkyBlue", "Mint", "Purple")
        for k in range(1, 26):
            p = pts[k]
            b.prism_y(cols[k % 5], [(p.x - 0.7, p.z), (p.x + 0.7, p.z), (p.x, p.z - 1.6)], p.y - 0.05, p.y + 0.05)
    # planters
    for sx in (-1, 1):
        b.bx("White", sx * 11.5 - 2.0, sx * 11.5 + 2.0, -D / 2 - 3.4, -D / 2 - 0.4, 0, 1.8)
        b.foliage("Hedge", (sx * 11.5, -D / 2 - 1.9, 2.4), 1.2, n=3, styles=["Hedge", "Leaf"])
        for k in range(4):
            b.ball("Flower" if k % 2 else "Lemon", (sx * 11.5 - 1.4 + k * 0.9, -D / 2 - 3.0, 2.3), 0.35, seg=(6, 4))
    return b


def drop_tower():
    b = Builder("DropTower", AREA)
    H = 78.0
    b.lathe("White", [(0, 0), (9.0, 0), (9.0, 1.2), (0, 1.2)], n=24)
    b.ring("Purple", (0, 0, 0), 9.2, 8.6, 0, 1.6, n=24)
    h = 2.4
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.cylz("White", sx * h, sy * h, 1.2, H, 0.5, 8)
    lv = 4.0
    k = 0
    z = 1.2
    while z + lv <= H:
        for rz in (0, PI / 2, PI, -PI / 2):
            with b.at(R(0, 0, rz)):
                b.cyl("HotPink" if k % 2 else "Lilac", (-h, -h, z), (h, -h, z + lv), 0.18, 5)
                b.cyl("HotPink" if k % 2 else "Lilac", (h, -h, z), (-h, -h, z + lv), 0.18, 5)
                b.cyl("White", (-h, -h, z + lv), (h, -h, z + lv), 0.2, 5)
        k += 1
        z += lv
    # neon stripe up the front
    b.bx("NeonPink", -0.25, 0.25, -h - 0.45, -h - 0.25, 6, H - 4)
    # top crown
    b.lathe("Purple", [(0, H), (5.5, H), (6.0, H + 1.5), (5.0, H + 3.5), (0, H + 3.5)], n=12)
    for kk in range(12):
        a = TAU * kk / 12
        b.ball(BULB, (math.cos(a) * 6.05, math.sin(a) * 6.05, H + 1.5), 0.4, seg=(6, 4))
    b.lathe("HotPink", [(0, H + 3.5), (3.8, H + 3.5), (0.2, H + 9.0), (0, H + 9.0)], n=12)
    b.cylz("White", 0, 0, H + 9, H + 12.5, 0.15, 6)
    b.ball("NeonRed", (0, 0, H + 12.6), 0.4, seg=(6, 4))
    # the seat ring, sitting at the bottom
    RZ = 5.6
    b.torus("HotPink", (0, 0, RZ), 4.8, 0.9, 20, 8)
    for kk in range(4):
        a = TAU * kk / 4 + PI / 4
        b.cyl("White", (math.cos(a) * 3.5, math.sin(a) * 3.5, RZ), (math.cos(a) * 4.2, math.sin(a) * 4.2, RZ), 0.6, 6)
    for kk in range(12):
        a = TAU * kk / 12
        with b.at(T(math.cos(a) * 6.0, math.sin(a) * 6.0, RZ - 3.0), R(0, 0, a + PI / 2)):
            b.box("Lemon", (0, 0.4, 1.5), (1.4, 0.4, 3.0))
            b.box("Lemon", (0, -0.3, 0.5), (1.4, 1.4, 0.35))
            b.torus("Charcoal", (0, -0.35, 2.4), 0.55, 0.14, 8, 4, rx=PI / 2 + 0.4)
    # ticket fence round the base
    for kk in range(16):
        a = TAU * kk / 16
        if -PI / 2 - 0.3 < (a - TAU if a > PI else a) < -PI / 2 + 0.3:
            continue
        x, y = math.cos(a) * 11.0, math.sin(a) * 11.0
        b.cylz("White", x, y, 0, 3.4, 0.18, 6)
        a2 = TAU * (kk + 1) / 16
        b.cyl("Purple", (x, y, 3.2), (math.cos(a2) * 11.0, math.sin(a2) * 11.0, 3.2), 0.14, 5)
        b.cyl("Purple", (x, y, 1.6), (math.cos(a2) * 11.0, math.sin(a2) * 11.0, 1.6), 0.1, 5)
    return b


def ticket_booth():
    b = Builder("TicketBooth", AREA)
    b.bx("White", -5.0, 5.0, -4.5, 4.5, 0, 0.8)
    X = 3.8
    b.bx("Cream", -X, X, -X, X, 0.8, 9.0)
    for rz in (0, PI / 2, PI, -PI / 2):
        with b.at(R(0, 0, rz)):
            for k in range(9):
                if k % 2 == 0:
                    x = -X + 0.42 + k * (2 * X - 0.84) / 8
                    b.bx("Red", x - 0.42, x + 0.42, -X - 0.15, -X + 0.05, 0.8, 4.4, bev=0)
    b.bx("White", -X - 0.3, X + 0.3, -X - 0.3, X + 0.3, 4.4, 5.0)
    b.bx("Charcoal", -2.8, 2.8, -X - 0.1, -X + 0.2, 5.0, 8.0)
    b.box("Glass", (0, -X - 0.15, 6.6), (5.4, 0.15, 2.8))
    b.bx("White", -3.4, 3.4, -X - 1.2, -X, 4.4, 4.9)
    b.bx("White", -X - 0.3, X + 0.3, -X - 0.3, X + 0.3, 9.0, 9.6)
    b.bx("SkyBlue", -3.4, 3.4, -X - 0.6, -X - 0.3, 9.7, 11.3)
    b.text("White", "TICKETS", (0, -X - 0.65, 10.5), 1.0, depth=0.12, font="black")
    b.striped_canopy("Red", "White", (0, 0), 5.8, 4.6, n=12, z=11.4)
    b.lathe("White", [(0, 9.6), (4.2, 9.6), (4.2, 11.4), (0, 11.4)], n=12)
    b.ball("Gold", (0, 0, 16.2), 0.5, seg=(8, 6))
    b.cylz("White", 0, 0, 16.0, 18.6, 0.1, 5)
    b.prism_y("Red", [(0.1, 18.5), (0.1, 17.2), (2.0, 17.85)], -0.06, 0.06)
    # queue line posts + velvet rope
    for k in range(4):
        x = -4 + k * 2.8
        b.cylz("Gold", x, -8.0, 0, 3.0, 0.2, 6)
        b.cylz("Gold", x, -8.0, 0, 0.3, 0.6, 8)
        b.ball("Gold", (x, -8.0, 3.1), 0.3, seg=(6, 4))
    for k in range(3):
        x = -4 + k * 2.8
        b.tube("RedDark", catenary((x, -8.0, 2.8), (x + 2.8, -8.0, 2.8), 0.5, 6), 0.1, 5)
    return b


def teacup_ride():
    b = Builder("TeacupRide", AREA)
    b.lathe("White", [(0, 0), (15.0, 0), (15.0, 1.0), (0, 1.0)], n=36)
    b.lathe("Mint", [(0, 1.0), (13.6, 1.0), (13.6, 1.25), (0, 1.25)], n=36)
    for k in range(12):
        a0, a1 = TAU * k / 12, TAU * (k + 1) / 12
        if k % 2 == 0:
            b.mesh("SkyBlue", [(0, 0, 1.27), (math.cos(a0) * 13.4, math.sin(a0) * 13.4, 1.27), (math.cos(a1) * 13.4, math.sin(a1) * 13.4, 1.27)], [[0, 1, 2]])
    # centre teapot
    b.lathe("Pink", [(0, 1.2), (3.2, 1.2), (4.6, 3.0), (4.9, 5.0), (4.3, 7.2), (2.6, 8.4), (0, 8.6)], n=16)
    b.lathe("White", [(0, 8.4), (2.7, 8.4), (2.4, 9.2), (0.9, 9.8), (0, 9.8)], n=16)
    b.ball("Lemon", (0, 0, 10.2), 0.6, seg=(8, 6))
    b.cyl("Pink", (4.0, 0, 4.0), (6.8, 0, 7.4), 0.85, 10, r2=0.45)
    b.torus("Pink", (-4.6, 0, 5.4), 1.7, 0.45, 14, 6, rx=PI / 2)
    for k in range(10):
        a = TAU * k / 10
        b.ball("White", (math.cos(a) * 4.75, math.sin(a) * 4.75, 5.0), 0.45, seg=(6, 4), sc=(0.4, 1, 1))
    # six teacups on saucers
    cols = ("HotPink", "Lemon", "SkyBlue", "Mint", "Lilac", "Orange")
    for k in range(6):
        a = TAU * k / 6 + 0.25
        x, y = math.cos(a) * 9.5, math.sin(a) * 9.5
        col = cols[k]
        b.lathe("White", [(0, 1.25), (3.6, 1.25), (3.9, 1.7), (3.4, 1.8), (0, 1.75)], c=(x, y, 0), n=16)
        b.lathe(col, [(0, 1.8), (1.6, 1.8), (2.9, 3.0), (3.3, 5.2), (3.1, 5.3), (2.7, 3.3), (0, 2.6)], c=(x, y, 0), n=16)
        b.ring("White", (x, y, 0), 3.35, 3.0, 4.9, 5.35, n=16)
        ah = a + PI / 2
        b.torus(col, (x + math.cos(ah) * 3.6, y + math.sin(ah) * 3.6, 3.8), 0.9, 0.28, 10, 5, rx=PI / 2, rz=ah)
        for j in range(6):
            aa = TAU * j / 6
            b.ball("White", (x + math.cos(aa) * 3.0, y + math.sin(aa) * 3.0, 3.7), 0.38, seg=(6, 4), sc=(0.35, 1, 1), rz=aa)
        b.lathe("White", [(0, 3.0), (2.85, 3.0), (3.04, 4.85), (0, 4.85)], c=(x, y, 0), n=16)
        b.lathe(col, [(0, 4.9), (2.2, 4.9), (2.2, 5.4), (0, 5.4)], c=(x, y, 0), n=16, a0=PI * 0.15, a1=PI * 0.85)
        b.cylz("Charcoal", x, y, 4.9, 5.6, 0.35, 8)
        b.torus("Charcoal", (x, y, 5.75), 0.7, 0.12, 10, 4)
    # low fence
    for k in range(24):
        a = TAU * k / 24
        if -PI / 2 - 0.2 < (a - TAU if a > PI else a) < -PI / 2 + 0.2:
            continue
        b.cylz("White", math.cos(a) * 15.6, math.sin(a) * 15.6, 0, 3.0, 0.18, 6)
        a2 = TAU * (k + 1) / 24
        b.cyl("HotPink", (math.cos(a) * 15.6, math.sin(a) * 15.6, 2.8), (math.cos(a2) * 15.6, math.sin(a2) * 15.6, 2.8), 0.15, 5)
    return b


def game_stall():
    b = Builder("GameStall", AREA)
    W, D = 16.0, 9.0
    b.bx("Plank", -W / 2, W / 2, -D / 2, D / 2, 0, 0.6)
    b.bx("Lilac", -W / 2, W / 2, D / 2 - 1.0, D / 2, 0.6, 11.0)
    for sx in (-1, 1):
        b.bx("Lilac", sx * W / 2 - 0.5 * sx - 0.5, sx * W / 2 - 0.5 * sx + 0.5, -D / 2, D / 2, 0.6, 11.0)
    b.bx("White", -W / 2 + 1, W / 2 - 1, -D / 2, -D / 2 + 1.6, 0.6, 4.0)
    for k in range(8):
        x = -W / 2 + 1.9 + k * 1.75
        b.bx("Red" if k % 2 else "White", x - 0.85, x + 0.85, -D / 2 - 0.1, -D / 2 + 0.1, 0.8, 3.8, bev=0)
    b.bx("WoodLight", -W / 2 + 0.8, W / 2 - 0.8, -D / 2 - 0.4, -D / 2 + 1.8, 4.0, 4.4)
    # bottle pyramids on the counter
    for gx in (-4.0, 0.0, 4.0):
        for r, cnt in ((0, 3), (1, 2), (2, 1)):
            for i in range(cnt):
                x = gx - (cnt - 1) * 0.55 + i * 1.1
                z = 4.4 + r * 1.55
                b.cylz("GlassDark", x, -D / 2 + 0.8, z, z + 1.1, 0.42, 8)
                b.cylz("GlassDark", x, -D / 2 + 0.8, z + 1.1, z + 1.5, 0.18, 6)
    for k in range(5):
        b.torus(("Lemon", "Mint", "HotPink", "SkyBlue", "Orange")[k], (-6.5 + k * 0.3, -D / 2 + 0.5, 4.55 + k * 0.18), 0.6, 0.12, 10, 4)
    # prizes: plush bears on shelves
    def bear(c, col, s=1.0):
        x, y, z = c
        b.ball(col, (x, y, z + 0.9 * s), 0.85 * s, seg=(10, 6), sc=(1, 0.85, 1.05))
        b.ball(col, (x, y - 0.05, z + 2.15 * s), 0.62 * s, seg=(10, 6))
        for sx in (-1, 1):
            b.ball(col, (x + sx * 0.5 * s, y, z + 2.65 * s), 0.25 * s, seg=(6, 4))
            b.ball(col, (x + sx * 0.75 * s, y - 0.3 * s, z + 1.1 * s), 0.3 * s, seg=(6, 4))
            b.ball(col, (x + sx * 0.45 * s, y - 0.45 * s, z + 0.25 * s), 0.32 * s, seg=(6, 4))
            b.ball("Black", (x + sx * 0.22 * s, y - 0.58 * s, z + 2.3 * s), 0.08 * s, seg=(5, 3))
        b.ball("Cream", (x, y - 0.55 * s, z + 2.0 * s), 0.22 * s, seg=(6, 4))
    for z in (6.0, 8.6):
        b.bx("WoodLight", -W / 2 + 1, W / 2 - 1, D / 2 - 2.2, D / 2 - 1.0, z - 0.3, z)
    for k in range(6):
        bear((-6.0 + k * 2.4, D / 2 - 1.6, 6.0), ("Pink", "SkyBlue", "Lemon", "Mint", "Lilac", "Orange")[k], 0.8)
    for k in range(4):
        bear((-4.8 + k * 3.2, D / 2 - 1.6, 8.6), ("Purple", "HotPink", "Teal", "Coral")[k], 0.95)
    # awning, sign with bulbs
    with b.at(T(0, -D / 2 - 0.8, 11.0), R(-0.45, 0, 0)):
        for k in range(10):
            x = -W / 2 - 0.4 + (k + 0.5) * (W + 0.8) / 10
            b.box("Red" if k % 2 else "White", (x, 0, 0), ((W + 0.8) / 10, 4.0, 0.3))
            pts = [(x - (W + 0.8) / 20, 0)] + [(x + math.cos(PI + PI * j / 6) * (W + 0.8) / 20, math.sin(PI + PI * j / 6) * 0.6) for j in range(1, 6)] + [(x + (W + 0.8) / 20, 0)]
            with b.at(T(0, -2.0, -0.15), R(PI / 2, 0, 0)):
                b.extrude("Red" if k % 2 else "White", [(p[0], p[1], 0) for p in pts], (0, 0, 0.2))
    b.bx("White", -W / 2, W / 2, -D / 2, D / 2, 11.0, 11.6)
    b.bx("HotPink", -5, 5, -D / 2 - 0.5, -D / 2, 12.0, 15.4)
    b.text("Lemon", "WIN!", (0, -D / 2 - 0.55, 13.7), 2.4, depth=0.3, font="black")
    for k in range(11):
        b.ball(BULB, (-5 + k, -D / 2 - 0.55, 15.6), 0.25, seg=(6, 4))
        b.ball(BULB, (-5 + k, -D / 2 - 0.55, 11.8), 0.25, seg=(6, 4))
    return b


def popcorn_cart():
    b = Builder("PopcornCart", AREA)
    for sx in (-1, 1):
        b.cyl("Charcoal", (sx * 2.9, 0.8, 1.6), (sx * 3.4, 0.8, 1.6), 1.6, 14)
        b.cyl("Gold", (sx * 3.45, 0.8, 1.6), (sx * 3.55, 0.8, 1.6), 0.45, 8)
        for k in range(6):
            a = TAU * k / 6
            b.cyl("Gold", (sx * 3.4, 0.8, 1.6), (sx * 3.4, 0.8 + math.cos(a) * 1.4, 1.6 + math.sin(a) * 1.4), 0.08, 4)
    b.cyl("DarkMetal", (-2.9, 0.8, 1.6), (2.9, 0.8, 1.6), 0.18, 6)
    b.cylz("DarkMetal", 0, -2.6, 0, 1.6, 0.18, 6)
    b.bx("Red", -2.8, 2.8, -2.0, 2.4, 1.8, 5.2)
    b.bx("Gold", -2.95, 2.95, -2.15, 2.55, 5.2, 5.5)
    b.bx("Gold", -2.95, 2.95, -2.15, 2.55, 1.6, 1.9)
    b.bx("Lemon", -2.0, 2.0, -2.12, -2.0, 2.4, 4.6, bev=0)
    b.text("Red", "POPCORN", (0, -2.18, 3.5), 0.6, depth=0.1, font="black")
    # glass case full of popcorn
    b.bx("Glass", -2.6, 2.6, -1.8, 2.2, 5.5, 9.0)
    for x in (-2.6, 2.6):
        for y in (-1.8, 2.2):
            b.bx("Gold", x - 0.15, x + 0.15, y - 0.15, y + 0.15, 5.5, 9.0)
    for k in range(70):
        x, y = b.rng.uniform(-2.3, 2.3), b.rng.uniform(-1.5, 1.9)
        z = 5.7 + b.rng.uniform(0, 1.5) + (0.8 if abs(x) < 1 else 0)
        b.ball("Lemon" if k % 4 else "White", (x, y, z), 0.32, seg=(5, 3))
    b.bx("Red", -2.9, 2.9, -2.1, 2.5, 9.0, 9.4)
    b.cylz("Metal", 0.6, 0.2, 7.6, 9.0, 0.08, 4)
    b.lathe("Metal", [(0, 0), (0.6, 0), (0.8, 0.8), (0, 0.8)], c=(0.6, 0.2, 7.2), n=8)
    # canopy on four poles
    for x in (-2.7, 2.7):
        for y in (-1.9, 2.3):
            b.cylz("Gold", x, y, 9.4, 12.8, 0.1, 5)
    with b.at(T(0, 0.2, 12.8)):
        for k in range(8):
            x = -3.4 + (k + 0.5) * 0.85
            b.mesh("Red" if k % 2 else "White", [(x - 0.425, -3.0, 0), (x + 0.425, -3.0, 0), (x + 0.425, 3.0, 0), (x - 0.425, 3.0, 0),
                                                (x - 0.425, -1.0, 1.4), (x + 0.425, -1.0, 1.4), (x + 0.425, 1.0, 1.4), (x - 0.425, 1.0, 1.4)],
                   [[0, 1, 5, 4], [3, 7, 6, 2], [4, 5, 6, 7], [0, 4, 7, 3], [1, 2, 6, 5], [0, 3, 2, 1]])
    # pull handle
    b.cyl("DarkMetal", (2.8, 2.4, 4.0), (2.8, 4.6, 4.4), 0.12, 6)
    b.cyl("DarkMetal", (-2.8, 2.4, 4.0), (-2.8, 4.6, 4.4), 0.12, 6)
    b.cyl("WoodDark", (-3.0, 4.6, 4.4), (3.0, 4.6, 4.4), 0.2, 6)
    # paper bags
    for k, x in enumerate((-1.4, 0.0, 1.4)):
        b.bx("White", x - 0.45, x + 0.45, -2.6, -2.0, 5.5, 6.9)
        b.bx("Red", x - 0.47, x + 0.47, -2.62, -2.0, 5.9, 6.3, bev=0)
        for j in range(3):
            b.ball("Lemon", (x - 0.2 + j * 0.2, -2.3, 7.05), 0.25, seg=(5, 3))
    return b


def swing_ride():
    b = Builder("SwingRide", AREA)
    b.lathe("White", [(0, 0), (6.0, 0), (6.0, 1.4), (0, 1.4)], n=20)
    b.ring("Lilac", (0, 0, 0), 6.2, 5.6, 0, 1.8, n=20)
    b.lathe("Lilac", [(0, 1.4), (2.6, 1.4), (2.0, 4.0), (1.6, 20.0), (0, 20.0)], n=12)
    for z in (6.0, 11.0, 16.0):
        b.torus("Lemon", (0, 0, z), 1.9 - z * 0.012, 0.25, 12, 4)
    # tilted spinning top
    TZ = 22.0
    tilt = 0.12
    with b.at(T(0, 0, TZ), R(tilt, 0, 0)):
        b.lathe("Lemon", [(0, -2.4), (2.4, -2.4), (2.6, 0), (0, 0)], n=12)
        b.striped_canopy("Purple", "Lemon", (0, 0), 13.0, 4.0, n=16, z=0.0)
        b.ring("White", (0, 0, 0), 13.2, 12.4, -1.4, 0.0, n=32)
        for k in range(32):
            a = TAU * k / 32
            b.ball(BULB, (math.cos(a) * 13.25, math.sin(a) * 13.25, -0.7), 0.28, seg=(6, 4))
        b.ball("Gold", (0, 0, 4.4), 0.8, seg=(8, 6))
        b.cylz("White", 0, 0, 4.4, 7.6, 0.12, 5)
        b.prism_y("HotPink", [(0.1, 7.5), (0.1, 6.0), (2.4, 6.75)], -0.07, 0.07)
    # swings flung out on chains
    swing_a = 0.62
    chain = 11.0
    cols = ("HotPink", "SkyBlue", "Lemon", "Mint")
    for k in range(16):
        a = TAU * k / 16
        top = V((math.cos(a) * 11.6, math.sin(a) * 11.6, TZ - 1.4 + math.sin(a) * 11.6 * math.tan(tilt) * -1))
        out = V((math.cos(a), math.sin(a), 0))
        seat = top + out * (math.sin(swing_a) * chain) - V((0, 0, math.cos(swing_a) * chain))
        tang = V((-math.sin(a), math.cos(a), 0))
        for s in (-0.7, 0.7):
            b.cyl("Metal", top + tang * s, seat + tang * s + V((0, 0, 1.3)), 0.07, 4)
        with b.at(T(seat), R(0, 0, a - PI / 2), R(swing_a, 0, 0)):
            b.box(cols[k % 4], (0, 0, 0.0), (1.6, 1.4, 0.3))
            b.box(cols[k % 4], (0, 0.75, 0.9), (1.6, 0.25, 1.8))
            b.box("Charcoal", (0, -0.75, 0.6), (1.4, 0.15, 0.15), bev=0)
    # fence ring with gap
    for k in range(28):
        a = TAU * k / 28
        if -PI / 2 - 0.15 < (a - TAU if a > PI else a) < -PI / 2 + 0.15:
            continue
        x, y = math.cos(a) * 20.0, math.sin(a) * 20.0
        b.cylz("White", x, y, 0, 3.2, 0.18, 6)
        a2 = TAU * (k + 1) / 28
        b.cyl("Lilac", (x, y, 3.0), (math.cos(a2) * 20.0, math.sin(a2) * 20.0, 3.0), 0.14, 5)
    return b


def bumper_cars():
    b = Builder("BumperCars", AREA)
    W, D = 38.0, 26.0
    b.bx("White", -W / 2 - 1, W / 2 + 1, -D / 2 - 1, D / 2 + 1, 0, 0.8)
    b.bx("Charcoal", -W / 2, W / 2, -D / 2, D / 2, 0.8, 1.0)
    # rubber bumper wall
    pts = [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)]
    for i in range(4):
        p0, p1 = V((pts[i][0], pts[i][1], 1.8)), V((pts[(i + 1) % 4][0], pts[(i + 1) % 4][1], 1.8))
        b.cyl("Rubber", p0, p1, 0.9, 8)
        b.cyl("Lemon", p0 + V((0, 0, 1.0)), p1 + V((0, 0, 1.0)), 0.2, 6)
    # posts + ceiling grid + roof
    for x in (-W / 2, -W / 6, W / 6, W / 2):
        for y in (-D / 2, D / 2):
            b.cylz("Purple", x, y, 0.8, 11.0, 0.55, 8)
    b.bx("Purple", -W / 2 - 0.8, W / 2 + 0.8, -D / 2 - 0.8, D / 2 + 0.8, 11.0, 12.2)
    for k in range(10):
        x = -W / 2 + (k + 0.5) * W / 10
        b.bx("DarkMetal", x - 0.08, x + 0.08, -D / 2, D / 2, 10.85, 11.0, bev=0)
    for k in range(7):
        y = -D / 2 + (k + 0.5) * D / 7
        b.bx("DarkMetal", -W / 2, W / 2, y - 0.08, y + 0.08, 10.85, 11.0, bev=0)
    with b.at(T(0, 0, 12.2)):
        for k in range(12):
            x = -W / 2 - 1 + (k + 0.5) * (W + 2) / 12
            b.mesh("HotPink" if k % 2 else "White", [(x - (W + 2) / 24, -D / 2 - 1, 0), (x + (W + 2) / 24, -D / 2 - 1, 0),
                                                     (x + (W + 2) / 24, D / 2 + 1, 0), (x - (W + 2) / 24, D / 2 + 1, 0),
                                                     (x - (W + 2) / 24, 0, 4.0), (x + (W + 2) / 24, 0, 4.0)],
                   [[0, 1, 4], [1, 5, 4], [3, 4, 5], [3, 5, 2], [0, 4, 3], [1, 2, 5], [0, 3, 2, 1]])
    for k in range(20):
        x = -W / 2 + k * W / 19
        b.ball(BULB, (x, -D / 2 - 0.9, 11.6), 0.28, seg=(6, 4))
    b.bx("SkyBlue", -9, 9, -D / 2 - 1.2, -D / 2 - 0.8, 12.4, 15.6)
    b.text("White", "BUMPER CARS", (0, -D / 2 - 1.25, 14.0), 2.0, depth=0.3, font="black")
    # cars
    cols = ("Red", "Blue", "Lemon", "Mint", "HotPink", "Orange")
    spots = ((-12, -6, 0.4), (-3, 4, 2.4), (8, -5, -0.6), (13, 6, 3.6), (-14, 7, 1.2), (2, -8, 4.4))
    for (x, y, rz), col in zip(spots, cols):
        with b.at(T(x, y, 1.0), R(0, 0, rz)):
            b.ball(col, (0, 0, 1.1), 1.0, seg=(14, 6), sc=(2.4, 3.4, 0.9))
            b.torus("Rubber", (0, 0, 0.8), 1.0, 0.45, 18, 6)
            b.ring("Rubber", (0, 0, 0), 3.2, 2.4, 0.3, 1.2, n=18)
            b.bx("Charcoal", -1.4, 1.4, 0.0, 2.0, 1.6, 2.1)
            b.bx(col, -1.4, 1.4, 1.6, 2.2, 2.1, 3.8)
            b.cyl("Charcoal", (0, -0.6, 2.2), (0, -1.1, 3.2), 0.12, 5)
            b.torus("Charcoal", (0, -1.15, 3.25), 0.55, 0.12, 10, 4, rx=-0.6)
            b.cylz("DarkMetal", 0, 2.3, 2.0, 10.8, 0.12, 5)
            b.ball("NeonYellow", (0, 2.3, 10.8), 0.25, seg=(6, 4))
    return b


ASSETS = [roller_coaster, carousel, castle_gate, drop_tower, ticket_booth, teacup_ride, game_stall,
          popcorn_cart, swing_ride, bumper_cars]
