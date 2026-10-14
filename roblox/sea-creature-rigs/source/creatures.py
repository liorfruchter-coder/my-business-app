"""The eleven sea creature rigs.

Body parts keep the blocky R15 layout (standard_body). Markings are painted, not
stuck on: crisp shapes drawn in a front, back or side view and projected onto
the faces that look that way, plus wrap-around bands. Fins are fin2 surfaces
that thin toward the edge, curve, carry a base-to-tip colour and a darker rim.
Anything that sticks out lives in "<BodyPart>__<Piece>" objects that Roblox
welds on; the Head stays the regular Roblox head and its pieces keep clear of
the face.
"""
import math

from mathutils import Matrix

from char import ARM_X, LEG_X, CharBuilder, smooth_outline, standard_body
from kit import PI, TAU, R, T, V

W = (250, 250, 252)
K = (22, 22, 28)
EYES = {"EyeWhite": dict(color=W, grad=0, light=False), "Pupil": dict(color=K, grad=0, rough=0.15, light=False)}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def Fm(o, u, v):
    """A frame at o: local x along u, local z along v (fin height), local y = thickness."""
    u = V(u).normalized()
    v = V(v)
    v = (v - u * v.dot(u)).normalized()
    y = v.cross(u).normalized()
    return Matrix(((u.x, y.x, v.x, o[0]), (u.y, y.y, v.y, o[1]), (u.z, y.z, v.z, o[2]), (0, 0, 0, 1)))


def spline(pts, per=8):
    P = [V(p) for p in pts]
    n = len(P)
    out = []
    for i in range(n - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, n - 1)]
        for k in range(per):
            t = k / per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(P[-1])
    return out


def taper(n, r0, r1, power=1.0):
    return [r0 + (r1 - r0) * (i / max(n - 1, 1)) ** power for i in range(n)]


def fin(b, st, ctrl, M, thick=0.14, curl=0.0, cup=0.0, rays=0, pleat=None, scallop=None, scale=1.0, flare=1.3, per=6):
    """A chunky cartoon fin grown out of the body from its base line ctrl[0] -> ctrl[1]. With rays
    it is a fish fin (soft ridges, a gently wavy edge); without, a smooth shark / orca fin."""
    ctrl = [(u * scale, v * scale) for u, v in ctrl]
    b.fin3(st, ctrl, M, thick=thick, rays=rays,
           pleat=(0.014 if rays else 0.0) if pleat is None else pleat,
           scallop=(0.05 if rays else 0.0) if scallop is None else scallop,
           curl=curl, cup=cup, per=per, flare=flare)


def tentacle(b, st, pts, r0, r1, sucker=None, sucker_in=None, per=8, side=1.0, every=2, flat=1.0, power=0.9, rows=2, face=None):
    path = spline(pts, per)
    radii = taper(len(path), r0, r1, power)
    _, frames = b.ttube(st, path, radii, n=12, flat=flat)
    if sucker:
        for i in range(2, len(path) - 3, every):
            p = path[i]
            t, nrm, bn = frames[i]
            r = radii[i]
            d = (nrm * side).normalized()
            if face is not None:
                f = V(face)
                d = (f - t * f.dot(t)).normalized()
                bn = t.cross(d).normalized()
            offs = (-0.32, 0.32) if rows == 2 and r > 0.12 else (0.0,)
            for o in offs:
                oo = o if (i // every) % 2 == 0 else o * 0.8
                c = p + d * r * flat * 0.86 + bn * r * oo
                rr = r * (0.3 if len(offs) == 2 else 0.42)
                b.cyl(sucker, c - d * 0.03, c + d * 0.06, rr, 10)
                if sucker_in:
                    b.cyl(sucker_in, c + d * 0.055, c + d * 0.075, rr * 0.5, 8)
    return path, radii, frames


def spike(b, st, p, n, L=0.3, r=0.08):
    p, n = V(p), V(n).normalized()
    with b.grad(lambda co: (co - p).dot(n) / L):
        b.cyl(st, p - n * 0.07, p + n * L, r, 8, r2=0.0)


# painted shapes (studs; front view u = x, side view u = y with the front at -y)
def shield(top=3.92, bot=2.04, wt=0.42, wm=0.7, wb=0.5, zm=3.25):
    """A belly shield down the front of the torso."""
    return ("smooth", [(-wt, top), (0, top + 0.02), (wt, top), (wm, zm + 0.25), (wm * 0.98, zm - 0.3), (wb + 0.06, bot + 0.45),
                       (wb, bot), (0, bot - 0.02), (-wb, bot), (-wb - 0.06, bot + 0.45), (-wm * 0.98, zm - 0.3), (-wm, zm + 0.25)])


def gills(y0=-0.06, z=4.6, n=2, step=0.13, h=0.4, w=0.045):
    """Curved gill slits on the side of the head (side view), bulging backwards."""
    out = []
    R = h * 0.75
    for i in range(n):
        yc = y0 + i * step
        outer, inner = [], []
        for k in range(13):
            t = -1 + 2 * k / 12
            a = math.radians(42) * t
            ww = w * (1 - 0.75 * t * t)
            outer.append((yc - R + R * math.cos(a), z + R * math.sin(a)))
            inner.append((yc - R + (R - ww) * math.cos(a), z + (R - ww * 0.3) * math.sin(a)))
        out.append(("poly", outer + inner[::-1]))
    return out


def head_ring_points(z, step_deg=30, skip_front=60, r=0.6, phase=0.0):
    out = []
    a = phase
    while a < 360 + phase:
        d = abs(((a - 270) + 180) % 360 - 180)
        if d > skip_front:
            ar = math.radians(a)
            out.append(((math.cos(ar) * r, math.sin(ar) * r, z), (math.cos(ar), math.sin(ar), 0.0)))
        a += step_deg
    return out


def fish_fins(b, fin_st, body, head="Head", tail_ctrl=None, dorsal=True, forearm=True, calf=True, crest=True, ears=True,
              pleat=0.014, scale=0.78):
    """The shared fin set for the fish-type rigs (scale shrinks or grows them all)."""
    if crest:
        with b.part("Head__Crest"):
            fin(b, fin_st, [(-0.46, -0.04), (0.5, -0.04), (0.88, 0.3), (1.04, 0.74), (0.92, 1.1), (0.58, 1.22), (0.2, 1.06),
                            (-0.1, 0.74), (-0.32, 0.36)],
                Fm((0, -0.02, 5.1), (0, 1, 0), (0, 0, 1)), thick=0.15, rays=6, pleat=pleat, scale=scale)
    if ears:
        with b.part("Head__Fins"):
            for sx in (-1, 1):
                fin(b, fin_st, [(-0.22, -0.04), (0.3, -0.04), (0.64, 0.24), (0.72, 0.56), (0.48, 0.74), (0.16, 0.66), (-0.08, 0.36)],
                    Fm((sx * 0.52, 0.12, 4.5), (0, 0.35, 1), (sx, 0.5, 0.3)), thick=0.12, rays=4, pleat=pleat * 0.8, scale=scale)
    if dorsal:
        with b.part("UpperTorso__DorsalFin"):
            fin(b, fin_st, [(-0.8, -0.04), (0.74, -0.04), (1.0, 0.3), (0.84, 0.74), (0.36, 0.94), (-0.2, 0.82), (-0.56, 0.48)],
                Fm((0, 0.46, 3.15), (0, 0, 1), (0, 1, 0.3)), thick=0.15, rays=6, pleat=pleat, scale=scale)
    with b.part("LowerTorso__Tail"):
        tube = spline([(0, 0.36, 2.24), (0, 0.78, 2.14), (0, 1.12, 2.02)], 6)
        b.ttube(body, tube, taper(len(tube), 0.36, 0.16, 0.8), n=18, grad=False)
        fin(b, fin_st, tail_ctrl or [(-0.2, -0.04), (0.2, -0.04), (0.7, 0.42), (1.2, 1.0), (1.02, 1.08), (0.6, 0.86), (0.2, 0.7),
                                     (0, 0.66), (-0.2, 0.7), (-0.6, 0.86), (-1.02, 1.08), (-1.2, 1.0), (-0.7, 0.42)],
            Fm((0, 1.04, 2.04), (1, 0, 0), (0, 0.8, -0.6)), thick=0.15, rays=8, pleat=pleat, cup=0.05, scale=scale)
    for side, sx in (("Left", 1), ("Right", -1)):
        if forearm:
            with b.part(f"{side}LowerArm__Fin"):
                fin(b, fin_st, [(-0.3, -0.04), (0.42, -0.04), (0.66, 0.3), (0.52, 0.66), (0.16, 0.78), (-0.16, 0.58)],
                    Fm((sx * 1.94, 0.18, 2.72), (0, 0.25, -1), (sx, 0.75, 0.1)), thick=0.12, rays=4, pleat=pleat * 0.8, scale=scale)
        if calf:
            with b.part(f"{side}LowerLeg__Fin"):
                fin(b, fin_st, [(-0.24, -0.04), (0.3, -0.04), (0.44, 0.28), (0.24, 0.5), (-0.06, 0.4)],
                    Fm((sx * 0.94, 0.2, 0.8), (0, 0.25, -1), (sx, 0.8, 0.1)), thick=0.11, rays=3, pleat=pleat * 0.7, scale=scale)


# ---------------------------------------------------------------------------
# 1  Tiny Fish
# ---------------------------------------------------------------------------

def tiny_fish():
    paint = [("front", (112, 196, 255), [shield()]),
             ("back", (26, 84, 196), [("smooth", [(-0.32, 4.0), (0.32, 4.0), (0.42, 3.0), (0.3, 2.0), (-0.3, 2.0), (-0.42, 3.0)])])]
    styles = dict(EYES,
                  Body=dict(color=(38, 118, 232), grad=0.12, patterns=[("scales", 1.5, (26, 84, 188))], paint=paint),
                  Belly=dict(color=(132, 212, 255), grad=0.1, rough=0.35),
                  Limb=dict(color=(36, 114, 228), grad=0.16, patterns=[("scales", 1.6, (26, 84, 188))]),
                  Dark=dict(color=(26, 86, 192), grad=0.12, patterns=[("scales", 1.8, (18, 62, 150))]),
                  Head=dict(color=(44, 128, 238), grad=0.08, front_clean=True, patterns=[("scales", 1.4, (30, 96, 198))],
                            paint=[("side", (22, 70, 170), gills())]),
                  Fin=dict(color=(255, 214, 60), tip=(255, 138, 30), tip_from=0.3, grad=0, rough=0.4, root=((40, 120, 234), 0.3, 0.62),
                           rays=((214, 112, 18), 0.75), edge=((255, 228, 150), 0.94)))
    b = CharBuilder("TinyFish", styles)
    standard_body(b, dict(head="Head", chest="Body", waist="Body", arm="Limb", forearm="Limb", hand="Dark",
                          thigh="Limb", shin="Limb", foot="Dark"))
    belly_plates(b, "Belly")
    fish_fins(b, "Fin", "Body")
    return b


def belly_plates(b, st, rows=((3.6, 0.36, 0.98), (3.18, 0.36, 1.06), (2.76, 0.36, 1.0)), low=(2.21, 0.3, 0.84), y=-0.5):
    """Raised belly scutes down the front of the torso."""
    with b.part("UpperTorso"):
        for z, h, w in rows:
            b.rbox(st, (0, y, z), (w, 0.12, h), bot=(0.94, 1.0), bev=0.05, segs=3)
    if low:
        with b.part("LowerTorso"):
            z, h, w = low
            b.rbox(st, (0, y, z), (w, 0.12, h), bot=(0.9, 1.0), bev=0.05, segs=3)


# ---------------------------------------------------------------------------
# 2  Pufferfish
# ---------------------------------------------------------------------------

def pufferfish():
    yel = (255, 204, 54)
    spots = [("spots", 4.2, (196, 126, 40), 0.17), ("spots", 9, (206, 140, 44), 0.11)]
    styles = dict(EYES,
                  Body=dict(color=yel, grad=0.12, patterns=spots,
                            paint=[("front", (255, 240, 192), [shield(3.9, 2.04, 0.52, 0.84, 0.64)])]),
                  Limb=dict(color=(255, 200, 50), grad=0.16, patterns=spots),
                  Dark=dict(color=(242, 170, 40), grad=0.12, patterns=[("spots", 6, (196, 120, 36), 0.14)]),
                  Belly=dict(color=(255, 240, 192), grad=0.06),
                  Head=dict(color=(255, 208, 60), grad=0.08, front_clean=True, patterns=spots),
                  Spike=dict(color=(255, 236, 170), tip=(176, 108, 40), tip_from=0.15, grad=0),
                  Fin=dict(color=(255, 186, 56), tip=(244, 116, 32), tip_from=0.3, grad=0, rough=0.4, root=(255, 204, 54),
                           rays=((206, 104, 26), 0.7), edge=((255, 214, 140), 0.94)))
    b = CharBuilder("Pufferfish", styles)
    standard_body(b, dict(head="Head", chest="Body", waist="Body", arm="Limb", forearm="Limb", hand="Dark",
                          thigh="Limb", shin="Limb", foot="Dark"))
    with b.part("UpperTorso"):
        b.ball("Belly", (0, -0.4, 3.1), 1.0, seg=(32, 20), sc=(0.86, 0.26, 0.8))
        b.ball("Body", (0, 0.4, 3.2), 1.0, seg=(32, 20), sc=(0.86, 0.24, 0.76))
    with b.part("UpperTorso__Spikes"):
        # puffed belly: spikes radiate from the bulge
        for x in (-0.66, -0.22, 0.22, 0.66):
            for z in (2.6, 3.0, 3.4, 3.78):
                e = (x / 0.86) ** 2 + ((z - 3.1) / 0.8) ** 2
                if e < 1.0:
                    y = -0.4 - 0.26 * math.sqrt(max(0.0, 1 - e))
                    spike(b, "Spike", (x * 0.98, y + 0.03, z), (x * 0.7, -1, (z - 3.1) * 0.8), 0.34, 0.09)
        for x in (-0.44, 0.0, 0.44):
            for z in (2.8, 3.2, 3.6):
                e = (x / 0.86) ** 2 + ((z - 3.1) / 0.8) ** 2
                y = -0.4 - 0.26 * math.sqrt(max(0.0, 1 - e))
                spike(b, "Spike", (x, y + 0.03, z), (x * 0.7, -1, (z - 3.1) * 0.8), 0.3, 0.085)
        for x in (-0.66, -0.22, 0.22, 0.66):
            for z in (2.7, 3.15, 3.6):
                e = (x / 0.86) ** 2 + ((z - 3.2) / 0.76) ** 2
                y = 0.4 + 0.24 * math.sqrt(max(0.0, 1 - e))
                spike(b, "Spike", (x, y - 0.03, z), (x * 0.6, 1, (z - 3.2) * 0.6), 0.4, 0.1)
        for sx in (-1, 1):
            for z in (2.62, 3.1, 3.58):
                for y in (-0.26, 0.26):
                    spike(b, "Spike", (sx * 0.96, y, z), (sx, y * 0.5, 0.1), 0.32, 0.085)
        for x in (-0.66, -0.22, 0.22, 0.66):
            spike(b, "Spike", (x, 0.0, 3.97), (x * 0.4, 0.1, 1), 0.3, 0.085)
    with b.part("Head__Spikes"):
        for z, ph in ((4.34, 0), (4.68, 15), (4.98, 0)):
            for p, n in head_ring_points(z, 30, 64, phase=ph):
                spike(b, "Spike", p, n, 0.36, 0.09)
        for a in range(0, 360, 45):
            ar = math.radians(a + 22)
            p = (math.cos(ar) * 0.32, math.sin(ar) * 0.32, 5.19)
            spike(b, "Spike", p, (math.cos(ar) * 0.5, math.sin(ar) * 0.5, 1), 0.34, 0.09)
        spike(b, "Spike", (0, 0.02, 5.19), (0, 0, 1), 0.4, 0.1)
    fish_fins(b, "Fin", "Body", crest=False, calf=False,
              tail_ctrl=[(-0.2, -0.04), (0.2, -0.04), (0.62, 0.36), (0.86, 0.78), (0.52, 0.88), (0, 0.72), (-0.52, 0.88),
                         (-0.86, 0.78), (-0.62, 0.36)])
    for side, sx in (("Left", 1), ("Right", -1)):
        for part, zs in (("UpperArm", (3.2, 3.68)), ("LowerArm", (2.5, 2.82))):
            with b.part(f"{side}{part}__Spikes"):
                for z in zs:
                    for y in (-0.24, 0.24):
                        spike(b, "Spike", (sx * 1.96, y, z), (sx, y * 0.5, 0.15), 0.26, 0.075)
                    spike(b, "Spike", (sx * 1.5, -0.46, z - 0.1), (sx * 0.2, -1, 0.1), 0.24, 0.07)
        for part, zs in (("UpperLeg", (1.36, 1.76)), ("LowerLeg", (0.6, 0.92))):
            with b.part(f"{side}{part}__Spikes"):
                for z in zs:
                    spike(b, "Spike", (sx * 0.96, 0, z), (sx, 0, 0.1), 0.24, 0.07)
                    spike(b, "Spike", (sx * 0.5, -0.46, z - 0.1), (sx * 0.2, -1, 0.1), 0.22, 0.065)
    return b


# ---------------------------------------------------------------------------
# 3  Crab
# ---------------------------------------------------------------------------

def claw(b, x, sx):
    """A big pincer hanging from the wrist, opening forward."""
    b.ball("Claw", (x, -0.04, 1.98), 1.0, seg=(22, 16), sc=(0.58, 0.56, 0.52))
    b.rbox("ShellDark", (x, 0, 2.36), (0.92, 0.92, 0.16), bev=0.06, segs=2)
    for k in range(4):
        a = -0.6 + k * 0.4
        spike(b, "ClawTip", (x + sx * 0.5 * math.cos(a), 0.3 * math.sin(a) - 0.05, 2.18), (sx * math.cos(a), math.sin(a), 0.6), 0.16, 0.06)
    upper = [(x, -0.22, 1.82), (x, -0.58, 1.64), (x, -0.88, 1.36), (x, -0.98, 1.08)]
    lower = [(x, 0.1, 1.58), (x, -0.16, 1.28), (x, -0.44, 1.04), (x, -0.62, 0.95)]
    for pts, r0 in ((upper, 0.32), (lower, 0.29)):
        path = spline(pts, 6)
        radii = taper(len(path), r0, 0.04, 1.1)
        b.ttube("Claw", path, radii, n=14, flat=0.78)
        n = len(path)
        mid = V((x, -0.42, 1.3))
        for i in range(3, n - 3, 2):
            p = path[i]
            d = mid - p
            d.x = 0
            d = d.normalized()
            spike(b, "ClawTip", p + d * radii[i] * 0.5, d, radii[i] * 0.5 + 0.1, 0.045)


def crab():
    red = (226, 58, 42)
    shell = [("mottle", 6, (182, 34, 28), 0.6), ("spots", 7, (190, 40, 30), 0.1)]
    styles = dict(EYES,
                  Shell=dict(color=red, grad=0.16, patterns=shell,
                             paint=[("front", (236, 182, 128), [shield(3.96, 2.04, 0.56, 0.78, 0.6)])]),
                  ShellDark=dict(color=(168, 32, 28), grad=0.1),
                  Belly=dict(color=(240, 192, 140), grad=0.12, patterns=[("mottle", 9, (218, 160, 108), 0.5)]),
                  Head=dict(color=(230, 62, 46), grad=0.08, front_clean=True, patterns=shell),
                  Claw=dict(color=(232, 64, 44), tip=(120, 34, 26), tip_from=0.55, grad=0.1, patterns=shell),
                  ClawTip=dict(color=(250, 226, 190), tip=(70, 36, 30), tip_from=0.1, grad=0))
    b = CharBuilder("Crab", styles)
    standard_body(b, dict(head="Head", chest="Shell", waist="Shell", arm="Shell", forearm="Shell", hand="Shell",
                          thigh="Shell", shin="Shell", foot="ShellDark"), hands=False)
    with b.part("UpperTorso"):
        for z in (2.74, 3.14, 3.54):
            for sx in (-1, 1):
                b.rbox("Belly", (sx * 0.34, -0.5, z), (0.62, 0.16, 0.36), bev=0.06, segs=3)
        b.rbox("Belly", (0, -0.5, 3.86), (1.3, 0.16, 0.22), bev=0.06, segs=3)
        b.dome("Shell", (0, 0.44, 3.22), 1.0, seg=32, rings=8, sc=(1.02, 0.8, 0.34), rx=-PI / 2)
        for (x, z) in ((-0.5, 3.6), (0.5, 3.6), (0.0, 3.5), (-0.3, 2.9), (0.3, 2.9), (0.68, 3.18), (-0.68, 3.18), (0.0, 3.0)):
            b.ball("ShellDark", (x, 0.72, z), 0.1, seg=(10, 8), sc=(1, 0.7, 1))
    with b.part("LowerTorso"):
        b.rbox("Belly", (0, -0.48, 2.2), (1.3, 0.12, 0.3), bev=0.05, segs=3)
    with b.part("LowerTorso__Legs"):
        for sx in (-1, 1):
            for i in range(3):
                pts = [(sx * 0.84, 0.42 + 0.14 * i, 2.3 - 0.04 * i), (sx * 1.45, 0.8 + 0.22 * i, 2.66 - 0.1 * i),
                       (sx * 1.82, 1.0 + 0.28 * i, 1.92 - 0.2 * i), (sx * 1.94, 1.08 + 0.3 * i, 1.24 - 0.25 * i)]
                path = spline(pts, 6)
                radii = taper(len(path), 0.15, 0.03, 1.2)
                b.ttube("Claw", path, radii, n=10)
                b.ball("ShellDark", tuple(V(pts[1])), 0.14, seg=(10, 8))
    for side, sx in (("Left", 1), ("Right", -1)):
        x = sx * ARM_X
        with b.part(f"{side}Hand"):
            claw(b, x, sx)
        with b.part(f"{side}UpperArm"):
            b.rbox("ShellDark", (x, 0, 3.1), (1.08, 1.08, 0.12), bev=0.05, segs=2)
            for y in (-0.25, 0.25):
                spike(b, "ClawTip", (x, y, 3.98), (sx * 0.3, y, 1), 0.18, 0.07)
        with b.part(f"{side}LowerArm"):
            for z in (2.55, 2.85):
                spike(b, "ClawTip", (x + sx * 0.46, 0, z), (sx, 0, 0.25), 0.16, 0.06)
        with b.part(f"{side}LowerLeg"):
            b.rbox("ShellDark", (sx * LEG_X, 0, 1.12), (1.08, 1.08, 0.1), bev=0.04, segs=2)
    with b.part("Head__EyeStalks"):
        for sx in (-1, 1):
            pts = [(sx * 0.26, 0.0, 5.1), (sx * 0.34, -0.04, 5.48), (sx * 0.43, -0.08, 5.78)]
            b.ttube("Shell", spline(pts, 5), taper(11, 0.11, 0.085), n=12, grad=False)
            b.ball("ShellDark", (sx * 0.34, -0.04, 5.46), 0.13, seg=(12, 8))
            b.ball("Shell", (sx * 0.44, -0.08, 5.94), 0.27, seg=(16, 12))
            b.eye((sx * 0.45, -0.14, 5.98), 0.24, look=(sx * 0.15, -1, 0.05))
            ant = [(sx * 0.1, -0.34, 5.12), (sx * 0.18, -0.52, 5.5), (sx * 0.38, -0.66, 5.86)]
            b.ttube("ShellDark", spline(ant, 4), taper(9, 0.04, 0.015), n=6, grad=False)
    return b


# ---------------------------------------------------------------------------
# 4  Jellyfish
# ---------------------------------------------------------------------------

def jellyfish():
    zg = ("zgrad", 0.2, 4.0, (134, 106, 240))
    dots = ("dots", 9, (196, 238, 255), 0.12)
    styles = dict(EYES,
                  Jelly=dict(color=(112, 178, 255), grad=0.08, rough=0.25, patterns=[zg, dots],
                             paint=[("front", (166, 218, 255), [shield(3.9, 2.06, 0.46, 0.7, 0.5)])]),
                  Head=dict(color=(124, 184, 255), grad=0.06, front_clean=True, patterns=[dots]),
                  BellGlass=dict(color=(150, 196, 255), tip=(200, 160, 255), tip_from=0.0, grad=0.1),
                  Frill=dict(color=(180, 160, 255), tip=(120, 230, 255), tip_from=0.2, grad=0),
                  Glow=dict(color=(140, 242, 255), grad=0, light=False),
                  GlowPink=dict(color=(255, 140, 232), grad=0, light=False))
    b = CharBuilder("Jellyfish", styles)
    standard_body(b, dict(head="Head", chest="Jelly", waist="Jelly", arm="Jelly", forearm="Jelly", hand="Jelly",
                          thigh="Jelly", shin="Jelly", foot="Jelly"))
    BZ = 4.9
    with b.part("Head__BellGlass"):
        with b.grad(lambda co: (co.z - BZ) / 0.75):
            b.dome("BellGlass", (0, 0.06, BZ), 0.94, seg=40, rings=12, sc=(1, 1, 0.8))
        for k in range(24):
            a = TAU * k / 24
            b.ball("BellGlass", (math.cos(a) * 0.9, 0.06 + math.sin(a) * 0.9, BZ - 0.03), 0.14, seg=(10, 6), sc=(1, 1, 0.55))
    with b.part("Head__BellGlow"):
        for k in range(4):
            a = TAU * k / 4 + PI / 4
            b.torus("GlowPink", (math.cos(a) * 0.32, 0.06 + math.sin(a) * 0.32, BZ + 0.62), 0.16, 0.05, 16, 6,
                    rz=a + PI / 2, a0=0, a1=PI * 1.4)
        for k in range(24):
            a = TAU * (k + 0.5) / 24
            b.ball("Glow", (math.cos(a) * 0.93, 0.06 + math.sin(a) * 0.93, BZ + 0.02), 0.05, seg=(6, 4))
    with b.part("Head__Tentacles"):
        for k in range(14):
            a = math.radians(-30 + k * 18)
            if abs(((math.degrees(a) - 270) + 180) % 360 - 180) < 78:
                continue
            x0, y0 = math.cos(a) * 0.8, 0.06 + math.sin(a) * 0.8
            back = math.sin(a) > 0.35
            L = 1.4 if back else 0.5
            pts = []
            for i in range(10):
                t = i / 9
                w = math.sin(t * PI * 2.6 + k) * 0.07
                pts.append((x0 * (1 + 0.12 * t) + w * math.sin(a), y0 * (1 + 0.18 * t) + w * math.cos(a), BZ - 0.06 - L * t))
            b.ttube("Frill", pts, taper(10, 0.06, 0.018), n=7)
    with b.part("LowerTorso__Tentacles"):
        for k, x in enumerate((-0.78, -0.5, -0.2, 0.1, 0.4, 0.7)):
            pts = []
            for i in range(16):
                t = i / 15
                pts.append((x + math.sin(t * 7 + k) * 0.12, 0.6 + 0.3 * t + math.cos(t * 5 + k) * 0.07, 2.5 - 2.38 * t))
            if k % 2 == 0:
                b.ttube("Frill", pts, taper(16, 0.17, 0.04), n=10, flat_b=0.3)
            else:
                b.ttube("Frill", pts, taper(16, 0.065, 0.02), n=7)
            b.ball("Glow", tuple(V(pts[-1])), 0.08, seg=(8, 6))
    with b.part("UpperTorso__Tentacles"):
        # glowing ribbons hanging down the front from under the bell
        for k, x0 in enumerate((-0.6, -0.3, 0.0, 0.3, 0.6)):
            L = (1.7, 2.1, 2.4, 2.1, 1.7)[k]
            pts = []
            for i in range(14):
                t = i / 13
                pts.append((x0 * (1 + 0.15 * t) + math.sin(t * 6.5 + k * 1.7) * 0.06, -0.56 - 0.12 * t - 0.1 * math.sin(t * PI),
                            3.98 - L * t))
            if k % 2 == 0:
                b.ttube("Frill", pts, taper(14, 0.11, 0.03), n=10, flat_b=0.35)
            else:
                b.ttube("Frill", pts, taper(14, 0.05, 0.018), n=7)
            b.ball("Glow", tuple(V(pts[-1])), 0.065, seg=(8, 6))
    for side, sx in (("Left", 1), ("Right", -1)):
        with b.part(f"{side}LowerArm__Frills"):
            for k, (dx, dy) in enumerate(((0.26, -0.22), (-0.2, 0.16), (0.12, 0.32), (-0.05, -0.3))):
                x = sx * ARM_X + dx
                pts = [(x + math.sin(i * 0.9 + k) * 0.07, dy, 2.25 - i * 0.12) for i in range(9)]
                b.ttube("Frill", pts, taper(9, 0.055, 0.02), n=6)
                b.ball("Glow", pts[-1], 0.06, seg=(6, 4))
    return b


# ---------------------------------------------------------------------------
# 5  Octopus  /  10  Giant Squid share the tentacle hand
# ---------------------------------------------------------------------------

def tentacle_hand(b, x, sx, skin, sucker, sucker_in):
    pts = [(x, 0, 2.36), (x, -0.04, 1.95), (x, -0.24, 1.6), (x, -0.48, 1.52), (x, -0.6, 1.72), (x, -0.45, 1.88), (x, -0.33, 1.74)]
    tentacle(b, skin, pts, 0.42, 0.07, sucker=sucker, sucker_in=sucker_in, per=6, side=-1, rows=2)


def octopus():
    pur = (146, 72, 216)
    pat = [("mottle", 5, (112, 46, 176), 0.7), ("spots", 8, (114, 48, 180), 0.12)]
    styles = dict(EYES,
                  Skin=dict(color=pur, grad=0.14, patterns=pat,
                            paint=[("front", (192, 138, 242), [shield(3.9, 2.04, 0.46, 0.72, 0.52)])]),
                  Arm=dict(color=(150, 76, 220), tip=(206, 150, 246), tip_from=0.55, grad=0.06, patterns=pat),
                  Sucker=dict(color=(252, 168, 220), grad=0),
                  SuckerIn=dict(color=(218, 100, 176), grad=0),
                  Bump=dict(color=(196, 140, 244), grad=0),
                  Head=dict(color=(152, 80, 222), grad=0.08, front_clean=True, patterns=pat))
    b = CharBuilder("Octopus", styles)
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Skin", forearm="Skin", hand="Skin",
                          thigh="Skin", shin="Skin", foot="Skin"), hands=False)
    with b.part("Head__Mantle"):
        b.ball("Skin", (0, 0.34, 5.58), 1.0, seg=(40, 26), sc=(0.84, 0.8, 0.98))
        for (x, y, z, r) in ((0.36, -0.02, 6.25, 0.1), (-0.3, 0.08, 6.36, 0.09), (0.0, 0.5, 6.45, 0.11), (0.58, 0.5, 5.86, 0.09),
                             (-0.56, 0.46, 5.9, 0.1), (0.2, 0.75, 6.1, 0.08), (-0.25, 0.8, 5.8, 0.08)):
            b.ball("Bump", (x, y, z), r, seg=(10, 8), sc=(1, 1, 0.55))
    with b.part("LowerTorso__Tentacles"):
        for sx in (-1, 1):
            pts = [(sx * 0.7, 0.4, 2.26), (sx * 1.45, 0.78, 2.0), (sx * 2.25, 0.72, 2.25), (sx * 2.72, 0.48, 2.85),
                   (sx * 2.7, 0.18, 3.28), (sx * 2.45, 0.12, 3.25), (sx * 2.38, 0.28, 3.05)]
            tentacle(b, "Arm", pts, 0.32, 0.05, sucker="Sucker", sucker_in="SuckerIn", per=8, side=-1)
            pts = [(sx * 0.35, 0.45, 2.2), (sx * 0.6, 1.0, 1.6), (sx * 0.9, 1.4, 0.7), (sx * 1.3, 1.55, 0.2),
                   (sx * 1.75, 1.4, 0.18), (sx * 1.85, 1.15, 0.35), (sx * 1.65, 1.1, 0.42)]
            tentacle(b, "Arm", pts, 0.26, 0.05, sucker="Sucker", sucker_in="SuckerIn", per=8, side=-1)
    with b.part("UpperTorso__Tentacles"):
        for sx in (-1, 1):
            pts = [(sx * 0.6, 0.46, 3.62), (sx * 1.3, 0.92, 3.92), (sx * 2.2, 0.98, 4.22), (sx * 2.78, 0.72, 4.72),
                   (sx * 2.84, 0.36, 5.12), (sx * 2.58, 0.3, 5.16), (sx * 2.52, 0.48, 4.96)]
            tentacle(b, "Arm", pts, 0.28, 0.045, sucker="Sucker", sucker_in="SuckerIn", per=8, side=-1)
    for side, sx in (("Left", 1), ("Right", -1)):
        x = sx * ARM_X
        with b.part(f"{side}Hand"):
            tentacle_hand(b, x, sx, "Arm", "Sucker", "SuckerIn")
        with b.part(f"{side}LowerArm"):
            for z in (2.48, 2.8):
                for y in (-0.18, 0.18):
                    b.cyl("Sucker", (x + sx * 0.46, y, z), (x + sx * 0.54, y, z), 0.11, 10)
    return b


# ---------------------------------------------------------------------------
# 6  Moray Eel
# ---------------------------------------------------------------------------

def moray_eel():
    teal = (30, 94, 124)
    spots = [("spots", 6.5, (228, 210, 74), 0.17), ("spots", 12, (200, 198, 86), 0.1)]
    styles = dict(EYES,
                  Skin=dict(color=teal, grad=0.16, patterns=spots,
                            paint=[("front", (206, 216, 96), [shield(3.96, 2.02, 0.3, 0.5, 0.36, 3.1)])]),
                  Limb=dict(color=(28, 88, 118), grad=0.16, patterns=spots),
                  Dark=dict(color=(20, 66, 92), grad=0.12, patterns=[("spots", 8, (196, 186, 74), 0.12)]),
                  Fin=dict(color=(34, 102, 128), tip=(196, 206, 92), tip_from=0.55, grad=0, rough=0.4,
                           patterns=[("spots", 10, (210, 200, 80), 0.12)], rays=((18, 62, 86), 0.55), edge=((226, 224, 100), 0.88)),
                  FinRim=dict(color=(220, 220, 96), grad=0),
                  Tail=dict(color=teal, grad=0.0, patterns=spots),
                  Head=dict(color=(34, 100, 130), grad=0.08, front_clean=True, patterns=spots,
                            paint=[("side", (14, 40, 58), gills(-0.02, 4.55, 1, 0.13, 0.42, 0.06))]))
    b = CharBuilder("MorayEel", styles)
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Limb", forearm="Limb", hand="Dark",
                          thigh="Limb", shin="Limb", foot="Dark"))
    with b.part("Head__Crest"):
        # the long eel dorsal fin starts on the crown and runs down the back
        fin(b, "Fin", [(-0.36, -0.04), (0.76, -0.04), (0.9, 0.14), (0.74, 0.4), (0.34, 0.54), (-0.06, 0.5), (-0.28, 0.28)],
            Fm((0, -0.16, 5.12), (0, 1, -0.38), (0, 0.3, 1)), thick=0.15, rays=8, pleat=0.012, scallop=0.04, scale=1.15)
    with b.part("UpperTorso__DorsalFin"):
        fin(b, "Fin", [(-0.56, -0.04), (1.62, -0.04), (1.66, 0.18), (1.3, 0.38), (0.7, 0.44), (0.1, 0.42), (-0.4, 0.3)],
            Fm((0, 0.46, 2.36), (0, 0, 1), (0, 1, 0.04)), thick=0.14, rays=11, pleat=0.012, scallop=0.04)
    with b.part("LowerTorso__Tail"):
        pts = [(0, 0.38, 2.25), (0, 0.95, 1.92), (0.1, 1.35, 1.22), (0.45, 1.58, 0.5), (1.1, 1.62, 0.24), (1.72, 1.32, 0.22),
               (2.05, 0.94, 0.26), (2.0, 0.66, 0.34)]
        path = spline(pts, 8)
        radii = taper(len(path), 0.44, 0.05, 0.8)
        b.ttube("Tail", path, radii, n=16, grad=False)
        b.ttube("Fin", path, [r * 0.62 for r in radii], n=10, flat=1.0, flat_b=0.14, lift=1.2)
        b.ttube("FinRim", path, [r * 0.62 for r in radii], n=6, flat=0.2, flat_b=0.18, lift=2.5, grad=False)
    return b


# ---------------------------------------------------------------------------
# 7  Shark  /  8  Hammerhead
# ---------------------------------------------------------------------------

def _shark_styles(skin, dark, fin_c, fin_tip):
    white = (238, 242, 248)
    belly = ("smooth", [(-0.4, 3.98), (0.4, 3.98), (0.64, 3.62), (0.5, 3.44), (0.74, 3.14), (0.56, 2.94), (0.68, 2.62),
                        (0.5, 2.36), (0.54, 2.02), (-0.54, 2.02), (-0.5, 2.36), (-0.68, 2.62), (-0.56, 2.94), (-0.74, 3.14),
                        (-0.5, 3.44), (-0.64, 3.62)])
    back = ("smooth", [(-0.5, 4.02), (0.5, 4.02), (0.6, 3.2), (0.42, 2.4), (-0.42, 2.4), (-0.6, 3.2)])
    return dict(EYES,
                Skin=dict(color=skin, grad=0.1, rough=0.38, patterns=[("mottle", 3, dark, 0.12)],
                          paint=[("front", white, [belly]), ("back", dark, [back])]),
                Limb=dict(color=skin, grad=0.14, rough=0.38, patterns=[("mottle", 3, dark, 0.12)]),
                Dark=dict(color=dark, grad=0.1, rough=0.38),
                White=dict(color=white, grad=0.05, rough=0.38),
                Fin=dict(color=fin_c, tip=fin_tip, tip_from=0.4, grad=0, rough=0.36, root=skin),
                Head=dict(color=skin, grad=0.08, rough=0.38,
                          paint=[("side", tuple(int(c * 0.5) for c in dark), gills(-0.06, 4.58, 3, 0.13, 0.42, 0.055))]))


# the cartoon shark fin: convex front edge sweeping back to a rounded tip, concave back edge
SHARK_FIN = [(-0.55, -0.04), (0.45, -0.04), (0.5, 0.12), (0.52, 0.32), (0.6, 0.56), (0.74, 0.82), (0.9, 1.04), (0.93, 1.14),
             (0.85, 1.2), (0.72, 1.16), (0.48, 0.98), (0.2, 0.7), (-0.1, 0.42), (-0.36, 0.16)]


def _shark_body(b, dorsal=True):
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Limb", forearm="Limb", hand="Limb",
                          thigh="Limb", shin="Limb", foot="White"))
    if dorsal:
        with b.part("UpperTorso__DorsalFin"):
            fin(b, "Fin", [(x * 0.8, y * 0.8) for x, y in SHARK_FIN], Fm((0, 0.46, 3.5), (0, 0.42, -1), (0, 1, 0.42)),
                thick=0.2, scale=0.8)
    with b.part("LowerTorso__Tail"):
        tube = spline([(0, 0.36, 2.24), (0, 0.86, 2.16), (0, 1.22, 2.1)], 6)
        b.ttube("Skin", tube, taper(len(tube), 0.36, 0.14, 0.8), n=18, grad=False)
        # heterocercal tail: the upper lobe is the big one
        fin(b, "Fin", [(-0.22, -0.04), (0.26, -0.04), (0.66, 0.2), (1.12, 0.46), (1.5, 0.7), (1.38, 0.82), (0.9, 0.62),
                       (0.4, 0.5), (0.04, 0.5), (-0.34, 0.58), (-0.72, 0.68), (-0.82, 0.58), (-0.5, 0.22)],
            Fm((0, 1.16, 2.1), (0, 0.3, 1), (0, 1, -0.3)), thick=0.2, scale=0.8)
    for side, sx in (("Left", 1), ("Right", -1)):
        with b.part(f"{side}UpperArm__Fin"):
            fin(b, "Fin", [(-0.34, -0.04), (0.32, -0.04), (0.42, 0.2), (0.54, 0.46), (0.62, 0.7), (0.52, 0.8), (0.36, 0.7),
                           (0.08, 0.4), (-0.18, 0.18)],
                Fm((sx * 1.95, 0.0, 3.46), (0, 1, 0.3), (sx * 0.55, 0.45, -1)), thick=0.17, scale=0.72, flare=1.6)
    with b.part("LowerTorso__Fins"):
        for sx in (-1, 1):
            fin(b, "Fin", [(-0.2, -0.04), (0.22, -0.04), (0.34, 0.26), (0.38, 0.4), (0.2, 0.36), (-0.02, 0.18)],
                Fm((sx * 0.62, 0.44, 2.14), (0, 0, 1), (sx * 0.5, 1, -0.5)), thick=0.13, scale=0.85)


def shark():
    b = CharBuilder("Shark", _shark_styles((92, 128, 178), (62, 90, 138), (84, 120, 172), (56, 80, 124)))
    _shark_body(b)
    with b.part("Head__Fin"):
        # the big head fin, with a cartoon bite taken out of its back edge
        bitten = SHARK_FIN[:4] + [(0.47, 0.42), (0.53, 0.5)] + SHARK_FIN[4:]
        fin(b, "Fin", [(x * 1.18, y * 1.2) for x, y in bitten], Fm((0, -0.06, 5.12), (0, 1, 0), (0, 0, 1)),
            thick=0.22, scale=0.82)
    return b


def hammerhead():
    st = _shark_styles((90, 142, 200), (60, 102, 158), (84, 134, 192), (54, 92, 146))
    st["Hammer"] = dict(color=(90, 142, 200), grad=0, rough=0.38, patterns=[("zgrad", 5.12, 5.17, (236, 242, 248))])
    b = CharBuilder("HammerheadShark", st)
    _shark_body(b)
    with b.part("Head__Hammer"):
        # the hammer: a chunky wing across the crown, swept forward, bulging at the eye ends
        secs = []
        n = 41
        for i in range(n):
            t = -1 + 2 * i / (n - 1)
            x = 1.7 * t
            k = abs(t)
            end = math.sqrt(max(0.0, 1 - ((k - 0.84) / 0.16) ** 2)) if k > 0.84 else 1.0
            d = (0.56 - 0.14 * k) * (0.3 + 0.7 * end)
            th = (0.3 + 0.06 * k * k) * (0.3 + 0.7 * end)
            yc = 0.08 - 0.24 * k * k
            zc = 5.26 + 0.04 * k
            secs.append([(x, yc + d * math.cos(a), zc + th * math.sin(a) * (1.0 if math.sin(a) > 0 else 0.8))
                         for a in (TAU * j / 28 for j in range(28))])
        b.skin_rings("Hammer", secs)
        for sx in (-1, 1):
            b.eye((sx * 1.56, -0.22, 5.32), 0.3, look=(sx * 1.0, -0.75, 0.05))
    with b.part("Head__Fin"):
        fin(b, "Fin", [(x * 0.95, y * 0.95) for x, y in SHARK_FIN], Fm((0, 0.1, 5.5), (0, 1, 0), (0, 0, 1)),
            thick=0.21, scale=0.82)
    return b


# ---------------------------------------------------------------------------
# 9  Orca
# ---------------------------------------------------------------------------

def orca():
    black, white = (26, 26, 34), (246, 246, 250)
    belly = ("smooth", [(-0.5, 3.98), (0.5, 3.98), (0.74, 3.5), (0.6, 3.0), (0.4, 2.72), (0.56, 2.32), (0.5, 2.02),
                        (-0.5, 2.02), (-0.56, 2.32), (-0.4, 2.72), (-0.6, 3.0), (-0.74, 3.5)])
    flank = ("smooth", [(-0.3, 2.2), (0.1, 2.12), (0.5, 2.3), (0.56, 2.62), (0.3, 2.86), (0.12, 2.6), (-0.2, 2.5)])
    saddle = ("smooth", [(-0.62, 3.0), (0, 2.86), (0.62, 3.0), (0.4, 3.3), (0, 3.36), (-0.4, 3.3)])
    eye = ("smooth", [(-0.3, 4.74), (-0.12, 4.9), (0.16, 4.92), (0.3, 4.84), (0.1, 4.76), (-0.12, 4.72)])
    styles = dict(EYES,
                  Black=dict(color=black, grad=0.06, rough=0.28,
                             paint=[("front", white, [belly]), ("side", white, [flank]), ("back", (132, 138, 152), [saddle])]),
                  Limb=dict(color=black, grad=0.08, rough=0.28, paint=[("side", white, [("ellipse", (0.02, 3.42, 0.26, 0.2))])]),
                  White=dict(color=white, grad=0.04),
                  Fin=dict(color=(30, 30, 38), tip=(52, 54, 66), tip_from=0.6, grad=0, rough=0.28),
                  Head=dict(color=(30, 30, 38), grad=0.05, rough=0.28, paint=[("side", white, [eye])]))
    b = CharBuilder("Orca", styles)
    standard_body(b, dict(head="Head", chest="Black", waist="Black", arm="Limb", forearm="Limb", hand="Limb",
                          thigh="Limb", shin="Limb", foot="White"))
    with b.part("Head__Fin"):
        # the tall orca dorsal fin, leaning back a little
        fin(b, "Fin", [(-0.52, -0.04), (0.4, -0.04), (0.38, 0.4), (0.36, 0.86), (0.38, 1.3), (0.34, 1.62), (0.2, 1.6),
                       (0.02, 1.14), (-0.22, 0.62)],
            Fm((0, -0.04, 5.12), (0, 1, 0), (0, 0, 1)), thick=0.22, scale=0.8)
    with b.part("UpperTorso__DorsalFin"):
        fin(b, "Fin", [(-0.5, -0.04), (0.5, -0.04), (0.5, 0.3), (0.5, 0.62), (0.36, 0.78), (0.12, 0.6), (-0.2, 0.3)],
            Fm((0, 0.46, 3.5), (0, 0.4, -1), (0, 1, 0.4)), thick=0.18, scale=0.85)
    with b.part("LowerTorso__Flukes"):
        tube = spline([(0, 0.36, 2.25), (0, 0.92, 2.17), (0, 1.3, 2.12)], 5)
        b.ttube("Black", tube, taper(len(tube), 0.38, 0.16), n=16, grad=False)
        fin(b, "Fin", [(-0.22, -0.04), (0.22, -0.04), (0.7, 0.16), (1.14, 0.46), (1.08, 0.64), (0.56, 0.54), (0.0, 0.42),
                       (-0.56, 0.54), (-1.08, 0.64), (-1.14, 0.46), (-0.7, 0.16)],
            Fm((0, 1.18, 2.1), (1, 0, 0), (0, 1, 0.08)), thick=0.18, cup=0.05, scale=0.82)
    for side, sx in (("Left", 1), ("Right", -1)):
        with b.part(f"{side}UpperArm__Paddle"):
            fin(b, "Fin", [(-0.3, -0.04), (0.3, -0.04), (0.44, 0.36), (0.36, 0.8), (0.02, 1.0), (-0.3, 0.8), (-0.42, 0.36)],
                Fm((sx * 1.94, 0.12, 3.3), (0, 1, 0), (sx * 0.9, 0.35, -0.6)), thick=0.18, curl=0.05, scale=0.78)
    return b


# ---------------------------------------------------------------------------
# 10  Giant Squid
# ---------------------------------------------------------------------------

def giant_squid():
    red = (226, 48, 60)
    pat = [("mottle", 6, (176, 26, 46), 0.6), ("spots", 9, (172, 24, 44), 0.12)]
    styles = dict(EYES,
                  Skin=dict(color=red, grad=0.14, patterns=pat,
                            paint=[("front", (244, 118, 130), [shield(3.9, 2.04, 0.46, 0.72, 0.52)])]),
                  Arm=dict(color=(228, 52, 64), tip=(250, 130, 150), tip_from=0.6, grad=0.05, patterns=pat),
                  Mantle=dict(color=(228, 50, 62), tip=(176, 26, 46), tip_from=0.3, grad=0, patterns=pat),
                  Light=dict(color=(246, 116, 130), grad=0.08),
                  Sucker=dict(color=(255, 172, 196), grad=0),
                  SuckerIn=dict(color=(230, 100, 140), grad=0),
                  Head=dict(color=(230, 54, 66), grad=0.08, front_clean=True, patterns=pat))
    b = CharBuilder("GiantSquid", styles)
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Skin", forearm="Skin", hand="Skin",
                          thigh="Skin", shin="Skin", foot="Skin"), hands=False)
    with b.part("Head__Mantle"):
        with b.grad(lambda co: (co.z - 5.0) / 2.5):
            b.lathe("Mantle", [(0, 4.98), (0.7, 4.98), (0.72, 5.3), (0.66, 5.9), (0.52, 6.5), (0.32, 7.0), (0.1, 7.38), (0, 7.45)],
                    c=(0, 0.04, 0), n=36)
        for sx in (-1, 1):
            fin(b, "Mantle", [(-0.74, -0.04), (0.5, -0.04), (0.42, 0.3), (0.16, 0.62), (-0.2, 0.78), (-0.52, 0.52)],
                Fm((sx * 0.34, 0.04, 6.74), (0, 0, 1), (sx, 0, -0.2)), thick=0.16, curl=0.04, scale=0.85)
    with b.part("LowerTorso__Arms"):
        for k, deg in enumerate((20, 58, 122, 160)):
            a = math.radians(deg)
            c, s = math.cos(a), math.sin(a)
            pts = [(c * 0.92, s * 0.48, 2.3), (c * 1.2, s * 0.8, 1.6), (c * 1.42, s * 1.02, 0.8), (c * 1.64, s * 1.2, 0.34),
                   (c * 1.94, s * 1.32, 0.36), (c * 2.04, s * 1.28, 0.62), (c * 1.9, s * 1.18, 0.7)]
            tentacle(b, "Arm", pts, 0.27, 0.045, sucker="Sucker", sucker_in="SuckerIn", per=7, side=-1)
    with b.part("UpperTorso__Tentacles"):
        # arms hanging down the front from under the chin, tips curling out
        for k, x0 in enumerate((-0.64, -0.32, 0.0, 0.32, 0.64)):
            sg = (-1, -1, 1, 1, 1)[k] if x0 else 1
            L = (1.75, 2.05, 2.3, 2.05, 1.75)[k]
            z1 = 3.98 - L
            pts = [(x0, -0.36, 3.98), (x0 * 1.04, -0.62, 3.7), (x0 * 1.1, -0.68, 3.0), (x0 * 1.18, -0.72, z1 + 0.5),
                   (x0 * 1.24 + sg * 0.12, -0.8, z1 + 0.06), (x0 * 1.24 + sg * 0.34, -0.9, z1 + 0.1),
                   (x0 * 1.22 + sg * 0.36, -0.95, z1 + 0.3), (x0 * 1.2 + sg * 0.22, -0.93, z1 + 0.34)]
            tentacle(b, "Arm", pts, 0.17, 0.035, sucker="Sucker", sucker_in="SuckerIn", per=6, rows=1, face=(0, -1, 0.2))
        for sx in (-1, 1):
            # the two long feeding tentacles trail behind with club ends
            pts = [(sx * 0.5, 0.42, 3.5), (sx * 0.86, 1.0, 2.6), (sx * 1.0, 1.28, 1.4), (sx * 1.02, 1.36, 0.66)]
            tentacle(b, "Arm", pts, 0.13, 0.1, per=7)
            b.ball("Arm", (sx * 1.02, 1.36, 0.5), 1.0, seg=(16, 12), sc=(0.24, 0.24, 0.42))
            for i in range(5):
                b.cyl("Sucker", (sx * 0.81, 1.36, 0.32 + i * 0.12), (sx * 0.76, 1.36, 0.32 + i * 0.12), 0.055, 8)
    for side, sx in (("Left", 1), ("Right", -1)):
        x = sx * ARM_X
        with b.part(f"{side}Hand"):
            tentacle_hand(b, x, sx, "Arm", "Sucker", "SuckerIn")
    return b


# ---------------------------------------------------------------------------
# 11  Clownfish
# ---------------------------------------------------------------------------

def clownfish():
    orange, white, black = (250, 112, 24), (252, 252, 252), (24, 20, 24)

    def bands(zc, half):
        # a white band with black edges painted round everything at height zc
        return [((0, 0, zc), (9, 9, half + 0.06), black, 0.02), ((0, 0, zc), (9, 9, half), white, 0.02)]
    styles = dict(EYES,
                  Orange=dict(color=orange, grad=0.12, patterns=[("scales", 1.4, (208, 82, 14))], regions=bands(3.18, 0.17),
),
                  Limb=dict(color=(248, 110, 24), grad=0.16, patterns=[("scales", 1.5, (208, 82, 14))], regions=bands(3.18, 0.17)),
                  Dark=dict(color=(226, 90, 18), grad=0.14, patterns=[("scales", 1.7, (186, 68, 12))]),
                  White=dict(color=white, grad=0.04),
                  Black=dict(color=black, grad=0, rough=0.35),
                  Fin=dict(color=(255, 136, 36), tip=(255, 104, 22), tip_from=0.3, grad=0, rough=0.4,
                           rays=((206, 76, 12), 0.6), edge=(black, 0.84)),
                  Head=dict(color=(252, 120, 30), grad=0.08, front_clean=True, patterns=[("scales", 1.3, (212, 86, 16))],
                            regions=[((0, 0.26, 4.6), (0.9, 0.22, 1.2), black, 0.02),
                                     ((0, 0.26, 4.6), (0.9, 0.15, 1.2), white, 0.02)]))
    b = CharBuilder("Clownfish", styles)
    standard_body(b, dict(head="Head", chest="Orange", waist="Orange", arm="Limb", forearm="Limb", hand="Dark",
                          thigh="Limb", shin="Limb", foot="Dark"))
    fish_fins(b, "Fin", "Orange",
              tail_ctrl=[(-0.2, -0.04), (0.2, -0.04), (0.66, 0.4), (0.88, 0.84), (0.62, 1.04), (0, 1.0), (-0.62, 1.04),
                         (-0.88, 0.84), (-0.66, 0.4)])
    with b.part("LowerTorso__Tail"):
        b.cyl("White", (0, 0.68, 2.2), (0, 0.86, 2.19), 0.31, 16)
        for y in (0.64, 0.9):
            b.cyl("Black", (0, y - 0.03, 2.2), (0, y + 0.03, 2.19), 0.32, 16)
    return b


CREATURES = [tiny_fish, pufferfish, crab, jellyfish, octopus, moray_eel, shark, hammerhead, orca, giant_squid, clownfish]
NAMES = {"TinyFish": "Tiny Fish", "Pufferfish": "Pufferfish", "Crab": "Crab", "Jellyfish": "Jellyfish", "Octopus": "Octopus",
         "MorayEel": "Moray Eel", "Shark": "Shark", "HammerheadShark": "Hammerhead Shark", "Orca": "Orca",
         "GiantSquid": "Giant Squid", "Clownfish": "Clownfish"}
