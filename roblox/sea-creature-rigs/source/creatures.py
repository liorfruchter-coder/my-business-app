"""The eleven sea creature rigs.

Body parts keep the blocky R15 layout (standard_body). Markings are painted, not
stuck on: crisp shapes drawn in a front, back or side view and projected onto
the faces that look that way, plus wrap-around bands. Fins (char.fin4, shapes in
FINS) are drawn like bat-wing fin accessories: bony ribs to sharp points, a thin
membrane cut back between them and a rolled spine on the leading edge. Tails
grow out of the lower back, curve down and end in a tail fin or flukes.
Anything that sticks out lives in "<BodyPart>__<Piece>" objects that Roblox
welds on; the Head stays the regular Roblox head and its pieces keep clear of
the face. The fish, sharks, eel, orca, octopus and squid wear their head as a
hood (char.Hood) with the face looking out through the mouth. Each body has its own shape
(FISH_BODY, SHARK_BODY ...) on the same R15 layout.
"""
import math

from mathutils import Matrix

from char import ARM_X, LEG_X, CharBuilder, Hood, smooth_outline, standard_body
from kit import PI, TAU, R, T, V

W = (250, 250, 252)
K = (22, 22, 28)
EYES = {"EyeWhite": dict(color=W, grad=0, light=False), "Pupil": dict(color=K, grad=0, rough=0.15, light=False),
        "Brow": dict(color=(36, 30, 46), grad=0, rough=0.4), "Blush": dict(color=(255, 128, 162), grad=0, light=False)}

# eyebrow shapes: height offset (degrees up the hood) along the brow, t = -1 at the inner end, 1 at the outer
MOODS = {"angry": lambda t: 7 * t - 1, "happy": lambda t: 4 - 5 * t * t, "surprised": lambda t: 9 - 7 * t * t,
         "sad": lambda t: 2 - 6 * t, "grumpy": lambda t: 3 * t - 2, "cheeky": lambda t: 5 - 4 * (t - 0.3) ** 2}


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


# Fin shapes for char.fin4, in the style of bat-wing / dragon-fin accessories: (root line, points).
# u runs along the root (the first point is the leading spine), v away from the body.
FINS = {
    "crest": (((-0.34, 0), (0.3, 0)), [(0.12, 0.95), (0.55, 0.7), (0.84, 0.42), (0.95, 0.12)]),
    "ear": (((-0.16, 0), (0.16, 0)), [(0.1, 0.62), (0.48, 0.5), (0.62, 0.22)]),
    "dorsal": (((0.55, 0), (-0.55, 0)), [(0.95, 0.66), (0.5, 0.62), (0.05, 0.54), (-0.38, 0.4), (-0.7, 0.2)]),
    "arm": (((-0.22, 0), (0.22, 0)), [(0.05, 0.66), (0.42, 0.56), (0.62, 0.3)]),
    "calf": (((-0.16, 0), (0.16, 0)), [(0.05, 0.46), (0.34, 0.36), (0.44, 0.16)]),
    "fork": (((-0.12, 0), (0.12, 0)), [(-0.85, 0.8), (-0.32, 0.52), (0.0, 0.4), (0.32, 0.52), (0.85, 0.8)]),
    "round_tail": (((-0.12, 0), (0.12, 0)), [(-0.66, 0.56), (-0.3, 0.7), (0.0, 0.72), (0.3, 0.7), (0.66, 0.56)]),
    # a clownfish's tail: a rounded fan with a gently wavy edge
    "clown_tail": (((-0.14, 0), (0.14, 0)), [(-0.6, 0.46), (-0.52, 0.68), (-0.28, 0.82), (0.0, 0.86), (0.28, 0.82),
                                             (0.52, 0.68), (0.6, 0.46)]),
    "shark": (((-0.55, 0), (0.45, 0)), [(0.5, 1.05), (0.7, 0.5), (0.62, 0.2)]),
    "shark_tail": (((0.16, 0), (-0.16, 0)), [(0.95, 0.9), (0.42, 0.48), (0.0, 0.4), (-0.42, 0.58)]),
    "pec": (((-0.26, 0), (0.24, 0)), [(0.1, 0.78), (0.48, 0.58), (0.6, 0.24)]),
    "pelvic": (((-0.14, 0), (0.14, 0)), [(0.08, 0.42), (0.34, 0.3), (0.4, 0.12)]),
    "flukes": (((-0.14, 0), (0.14, 0)), [(-0.95, 0.52), (-0.42, 0.42), (0.0, 0.3), (0.42, 0.42), (0.95, 0.52)]),
    "orca": (((-0.45, 0), (0.35, 0)), [(0.16, 1.45), (0.4, 0.62), (0.36, 0.22)]),
    "paddle": (((-0.24, 0), (0.24, 0)), [(-0.02, 0.86), (0.34, 0.64), (0.42, 0.3)]),
    "squid": (((-0.45, 0), (0.42, 0)), [(-0.3, 0.6), (0.08, 0.52), (0.36, 0.22)]),
    "eel_crest": (((-0.32, 0), (0.7, 0)), [(-0.1, 0.42), (0.25, 0.42), (0.55, 0.34), (0.82, 0.16)]),
    "ridge": (((-0.6, 0), (1.6, 0)), [(-0.7, 0.3), (-0.2, 0.36), (0.3, 0.38), (0.8, 0.36), (1.3, 0.34), (1.75, 0.2)]),
}
SYMMETRIC = {"fork", "round_tail", "clown_tail", "flukes"}


def fin(b, st, shape, M, scale=1.0, **kw):
    """A fin from FINS (or a (root, points) pair), scaled, in frame M (see Fm)."""
    root, tips = FINS[shape] if isinstance(shape, str) else shape
    root = tuple((u * scale, v * scale) for u, v in root)
    tips = [(u * scale, v * scale) for u, v in tips]
    if isinstance(shape, str) and shape in SYMMETRIC and "bend" not in kw:
        # the two outer spines bow outwards, the middle ones stay straight
        mid = (root[0][0] + root[1][0]) / 2
        L = [math.hypot(u - mid, v) for u, v in tips]
        kw["bend"] = [0.08 * L[0]] + [0.0] * (len(tips) - 2) + [-0.08 * L[-1]]
    kw.setdefault("thick", 0.05 * max(0.7, scale))
    kw.setdefault("spine", 0.05 * scale)
    kw.setdefault("rib", 0.026 * scale)
    b.fin4(st, root, tips, M, **kw)


def tail(b, st, ctrl, r0, r1, per=8):
    """A tail: a tube through ctrl (it starts inside the body) tapering from r0 to r1.
    Returns the path, its radii and the direction at the tip."""
    path = spline(ctrl, per)
    radii = taper(len(path), r0, r1, 0.85)
    b.ttube(st, path, radii, n=18, grad=False)
    return path, radii, (path[-1] - path[-3]).normalized()


def back_y(b, part, z, x=0.0):
    """How far back the surface of a body part is at height z."""
    return b.hit(part, (x, 3, z), (0, -1, 0))[0].y


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


# body shapes per creature (see char.BODY): still the R15 parts, but each reads as that animal
FISH_BODY = dict(chest=(2.0, 1.12), chest_bot=(0.9, 0.92), shoulder=0.28, chest_bev=0.26, arm=0.9, arm_bot=0.8, leg=0.94, leg_bot=0.8,
                 limb_bev=0.2, hand="mitt", foot="flipper")
SHARK_BODY = dict(chest=(2.0, 1.06), chest_bot=(0.88, 0.9), shoulder=0.28, chest_bev=0.2, arm=0.9, arm_bot=0.8, leg=0.96, leg_bot=0.8,
                  limb_bev=0.18, hand="mitt", foot="flipper")
ORCA_BODY = dict(chest=(2.0, 1.16), chest_bot=(0.9, 0.92), shoulder=0.28, chest_bev=0.32, arm=0.9, arm_bot=0.8, leg=0.98, leg_bot=0.8,
                 limb_bev=0.24, belly=(0.8, 0.2, 0.76), hand="mitt", foot="flipper")
PUFFER_BODY = dict(chest=(2.0, 1.0), chest_bot=(0.92, 0.96), chest_bev=0.42, shoulder=0.3, belly=(0.96, 0.36, 0.82),
                   back=(0.9, 0.3, 0.78), arm=0.9, arm_bot=0.8, leg=0.92, leg_bot=0.8, limb_bev=0.26, hand="mitt")
CRAB_BODY = dict(chest=(2.0, 1.0), chest_bot=(0.88, 0.9), shoulder=0.28, chest_bev=0.1, arm=0.9, arm_bot=0.8, leg=0.9, leg_bot=0.8,
                 limb_bev=0.1)
JELLY_BODY = dict(chest=(2.0, 1.0), chest_bot=(0.92, 0.94), shoulder=0.28, chest_bev=0.36, arm=0.9, arm_bot=0.8, leg=0.92, leg_bot=0.8,
                  limb_bev=0.3, hand="mitt")
OCTO_BODY = dict(chest=(2.0, 1.06), chest_bot=(1.02, 1.04), shoulder=0.28, chest_bev=0.4, arm=0.9, arm_bot=0.8, leg=0.96, leg_bot=0.8,
                 limb_bev=0.32)
EEL_BODY = dict(chest=(2.0, 0.94), chest_bot=(0.86, 0.94), shoulder=0.28, chest_bev=0.26, arm=0.9, arm_bot=0.8, leg=0.88, leg_bot=0.8,
                limb_bev=0.22, hand="mitt", foot="flipper")
SQUID_BODY = dict(chest=(2.0, 1.0), chest_bot=(0.84, 0.9), shoulder=0.28, chest_bev=0.34, arm=0.9, arm_bot=0.8, leg=0.9, leg_bot=0.8,
                  limb_bev=0.28)

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


def _dir(th, ph):
    t, p = math.radians(th), math.radians(ph)
    return V((math.cos(p) * math.cos(t), math.cos(p) * math.sin(t), math.sin(p)))


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


def tooth(b, st, base, aim, face, w=0.11, L=0.15, t=0.05, curve=0.025):
    """A cartoon tooth: a flat triangular blade that bends back a little toward its point.
    base: centre of the root (sunk in the gum), aim: where the point goes, face: the side its flat
    face shows to."""
    d = V(aim).normalized()
    o = V(face)
    o = (o - d * o.dot(d)).normalized()
    sw = d.cross(o).normalized()
    base = V(base)
    n = 10
    rings = []
    for f, ws, ts in ((0.0, 1.0, 1.0), (0.45, 0.62, 0.78), (0.78, 0.26, 0.45)):
        c = base + d * L * f - o * curve * f * f
        rings.append([c + sw * (w / 2) * ws * math.cos(TAU * k / n) + o * (t / 2) * ts * math.sin(TAU * k / n)
                      for k in range(n)])
    tip = base + d * L - o * curve
    verts = [p for ring in rings for p in ring] + [tip, base - d * 0.01]
    faces = []
    for r in range(len(rings) - 1):
        for k in range(n):
            k2 = (k + 1) % n
            faces.append((r * n + k, r * n + k2, (r + 1) * n + k2, (r + 1) * n + k))
    it, ib = len(verts) - 2, len(verts) - 1
    last = (len(rings) - 1) * n
    for k in range(n):
        faces.append((last + k, last + (k + 1) % n, it))
        faces.append(((k + 1) % n, k, ib))
    b.mesh_styled(verts, faces, [st] * len(faces))


def brow_over(b, center, r, mood, sx, lift=1.08, span=0.95, up=(0, 0, 1), front=(0, -1, 0)):
    """An eyebrow that sits on a ball of radius r around center (an eye or the ball it sits on),
    just above the front of it. sx = +1 for the character's left eye (inner end toward -x)."""
    c, upv, fr = V(center), V(up).normalized(), V(front).normalized()
    side = fr.cross(upv).normalized() * -1      # character's left
    pts = []
    for i in range(7):
        t = -1 + 2 * i / 6
        a_side = sx * t * span * 0.62
        a_up = 0.82 + math.radians(MOODS[mood](t)) * 1.6
        d = (fr * math.cos(a_up) * math.cos(a_side) + upv * math.sin(a_up) + side * math.cos(a_up) * math.sin(a_side))
        pts.append(c + d.normalized() * r * lift)
    rr = r * 0.17
    b.ttube("Brow", pts, [rr * (0.55 + 0.45 * math.sin(math.pi * i / 6) ** 0.5) for i in range(7)], n=10, grad=False)


def wear_hood(b, hood, st="Hood", lining="Lining", lip="Lip", fat_lip=0.0, teeth=None, eye_r=0.2, eye_at=(42, 30),
              eyes=True, brows=None, blush=False):
    """Put a creature hood on the head: the shell, optional fat lips (gums) round the mouth,
    teeth = (style, width, length, spacing) along the top and bottom of the mouth, a pair of big
    cartoon eyes, eyebrows (a MOODS name, or one per eye: (left, right)) and blush on the cheeks."""
    eye_r *= 1.15
    with b.part("Head__Hood"):
        ring = hood.build(b, st, lining, lip)
        if fat_lip:
            b.ttube(lip, ring + [ring[0]], [fat_lip] * (len(ring) + 1), n=12, cap=False, grad=False)
        if teeth:
            tst, w, L, gap = teeth
            hc = hood.surf(-90, hood.phc)
            sx_, sz_ = math.sin(math.radians(hood.hth)), math.sin(math.radians(hood.hph))
            # walk round the gum line and set a tooth every `gap` studs on the upper and lower jaw
            run, next_at = 0.0, gap / 2
            loop = ring + [ring[0]]
            for p, q in zip(loop, loop[1:]):
                seg = (q - p).length
                while next_at <= run + seg:
                    pt = p.lerp(q, (next_at - run) / seg)
                    next_at += gap
                    off = pt - hc
                    ang = math.atan2(off.z / sz_, off.x / sx_)
                    up = abs(math.sin(ang))
                    if up < 0.5:
                        continue
                    th = math.degrees(math.atan2(pt.y - hood.c.y, pt.x - hood.c.x))
                    ph = math.degrees(math.asin(max(-1.0, min(1.0, (pt.z - hood.c.z) / ((pt - hood.c).length or 1)))))
                    face = hood.normal(th, ph)
                    aim = ((hc - pt).normalized() + (hood.c - pt).normalized() * 0.3).normalized()
                    k = 0.72 + 0.28 * (up - 0.5) / 0.5
                    tooth(b, tst, pt + aim * 0.01, aim, face, w * (0.85 + 0.15 * k), L * k)
                run += seg
        if eyes:
            for sx in (-1, 1):
                P, N = hood.point(-90 + sx * eye_at[0], eye_at[1])
                b.eye(tuple(P + N * eye_r * 0.3), eye_r, look=tuple((N * 0.6 + V((0, -1, 0.1))).normalized()))
        if blush:
            for sx in (-1, 1):
                P, N = hood.point(-90 + sx * (hood.hth + 15), hood.phc - 6)
                e = N.to_track_quat("Z", "Y").to_euler()
                b.ball("Blush", tuple(P + N * 0.005), 1.0, seg=(16, 8), sc=(0.15, 0.1, 0.03), rx=e.x, ry=e.y, rz=e.z)
    if eyes and brows:
        with b.part("Head__Hood"):
            ae = math.degrees(eye_r / ((hood.r[0] + hood.r[2]) / 2))
            for k, sx in enumerate((1, -1)):
                mood = MOODS[brows[k] if isinstance(brows, (tuple, list)) else brows]
                th0, ph0 = -90 + sx * eye_at[0], eye_at[1] + ae * 1.45
                pts = []
                for i in range(7):
                    t = -1 + 2 * i / 6
                    P, N = hood.point(th0 + sx * t * ae * 1.15, ph0 + mood(t))
                    pts.append(P + N * eye_r * 0.1)
                rr = eye_r * 0.2
                b.ttube("Brow", pts, [rr * (0.55 + 0.45 * math.sin(math.pi * i / 6) ** 0.5) for i in range(7)], n=10, grad=False)
    return ring


def fish_fins(b, fin_st, body, tail_shape="fork", dorsal=True, forearm=True, calf=True, crest=True, ears=True,
              scale=0.8, crest_o=(0, -0.02, 5.1), ear_o=(0.52, 0.12, 4.5), head_scale=0.5, tail_scale=1.15, tail=True,
              scallop=None):
    """The shared fin set for the fish-type rigs, and the tail (scallop: how deep the edge is cut
    back between the points; smaller is smoother)."""
    kw = {} if scallop is None else dict(scallop=scallop)
    if crest:
        with b.part("Head__Crest"):
            fin(b, fin_st, "crest", Fm(crest_o, (0, 1, 0), (0, 0, 1)), scale=head_scale, **kw)
    if ears:
        with b.part("Head__Fins"):
            for sx in (-1, 1):
                fin(b, fin_st, "ear", Fm((sx * ear_o[0], ear_o[1], ear_o[2]), (0, 0.35, 1), (sx, 0.5, 0.3)), scale=head_scale * 1.25,
                    **kw)
    if dorsal:
        with b.part("UpperTorso__DorsalFin"):
            fin(b, fin_st, "dorsal", Fm((0, back_y(b, "UpperTorso", 3.15) - 0.02, 3.15), (0, 0, 1), (0, 1, 0.3)), scale=scale,
                **kw)
    if tail:
        fish_tail(b, fin_st, body, tail_shape, tail_scale, scallop)
    for side, sx in (("Left", 1), ("Right", -1)):
        if forearm:
            with b.part(f"{side}LowerArm__Fin"):
                fin(b, fin_st, "arm",
                    Fm((sx * (ARM_X + b.half_width(f"{side}LowerArm", 2.72) - 0.02), 0.16, 2.72), (0, 0.25, -1), (sx, 0.75, 0.1)),
                    scale=scale, **kw)
        if calf:
            with b.part(f"{side}LowerLeg__Fin"):
                fin(b, fin_st, "calf",
                    Fm((sx * (LEG_X + b.half_width(f"{side}LowerLeg", 0.8) - 0.02), 0.18, 0.8), (0, 0.25, -1), (sx, 0.8, 0.1)),
                    scale=scale, **kw)


def fish_tail(b, fin_st, body, shape="fork", scale=1.15, scallop=None):
    """A fish's tail: the back end of a fish, thick where it leaves the lower back and narrowing
    to a slim stalk, then a big upright tail fin (like a real fish, not a shark's crescent)."""
    yb = back_y(b, "LowerTorso", 2.22)
    with b.part("LowerTorso__Tail"):
        path, radii, d = tail(b, body, [(0, yb - 0.22, 2.3), (0, yb + 0.2, 2.18), (0, yb + 0.54, 2.1), (0, yb + 0.8, 2.12)],
                              0.42, 0.15)
        up = V((0, -d.z, d.y)).normalized()
        kw = {} if scallop is None else dict(scallop=scallop)
        fin(b, fin_st, shape, Fm(tuple(path[-1] - d * 0.08), tuple(up), d), scale=scale, **kw)
    return path, radii


# ---------------------------------------------------------------------------
# 1  Tiny Fish
# ---------------------------------------------------------------------------

def tiny_fish():
    paint = [("front", (112, 196, 255), [shield()]),
             ("back", (26, 84, 196), [("smooth", [(-0.32, 4.0), (0.32, 4.0), (0.42, 3.0), (0.3, 2.0), (-0.3, 2.0), (-0.42, 3.0)])])]
    scales = [("scales", 1.4, (30, 96, 198))]
    styles = dict(EYES,
                  Body=dict(color=(38, 118, 232), grad=0.12, patterns=[("scales", 1.5, (26, 84, 188))], paint=paint),
                  Belly=dict(color=(132, 212, 255), grad=0.1, rough=0.35),
                  Glove=dict(color=(255, 208, 56), grad=0.1, rough=0.35),
                  Limb=dict(color=(36, 114, 228), grad=0.16, patterns=[("scales", 1.6, (26, 84, 188))]),
                  Dark=dict(color=(26, 86, 192), grad=0.12, patterns=[("scales", 1.8, (18, 62, 150))]),
                  Head=dict(color=(44, 128, 238), grad=0.08),
                  Hood=dict(color=(44, 128, 238), grad=0.1, rough=0.4, patterns=scales,
                            paint=[("front", (132, 212, 255), [("rect", (-1.2, 3.8, 1.2, 4.16))]), ("side", (22, 70, 170), gills(0.16, 4.5))]),
                  Lining=dict(color=(18, 50, 126), grad=0.1),
                  Lip=dict(color=(255, 196, 70), grad=0.05, rough=0.35),
                  Fin=dict(color=(255, 214, 60), tip=(255, 138, 30), tip_from=0.3, grad=0, rough=0.4, root=((40, 120, 234), 0.3, 0.62),
                           rays=((214, 112, 18), 0.75), edge=((255, 228, 150), 0.94)))
    b = CharBuilder("TinyFish", styles)
    standard_body(b, dict(head="Head", chest="Body", waist="Body", arm="Limb", forearm="Limb", hand="Glove",
                          thigh="Limb", shin="Limb", foot="Glove"), shape=FISH_BODY)
    belly_plates(b, "Belly")
    wear_hood(b, Hood(bumps=[(-90, -10, 0.07, 30)]), fat_lip=0.07, brows="happy", blush=True)
    fish_fins(b, "Fin", "Body", crest_o=(0, 0.02, 5.42), ear_o=(0.86, 0.16, 4.5))
    return b


def belly_plates(b, st, rows=((3.6, 0.36, 0.98), (3.18, 0.36, 1.06), (2.76, 0.36, 1.0)), low=(2.21, 0.3, 0.84)):
    """Raised belly scutes down the front of the torso, half sunk into it."""
    for part, rr in (("UpperTorso", rows), ("LowerTorso", [low] if low else [])):
        for z, h, w in rr:
            p, _ = b.hit(part, (0, -3, z), (0, 1, 0))
            with b.part(part):
                b.rbox(st, (0, p.y - 0.01, z), (w, 0.14, h), bot=(0.94, 1.0), bev=0.05, segs=3)


# ---------------------------------------------------------------------------
# 2  Pufferfish
# ---------------------------------------------------------------------------

def pufferfish():
    yel = (255, 204, 54)
    spots = [("spots", 4.2, (196, 126, 40), 0.17), ("spots", 9, (206, 140, 44), 0.11)]
    styles = dict(EYES,
                  Body=dict(color=yel, grad=0.1, patterns=spots,
                            paint=[("front", (255, 240, 192), [("ellipse", (0, 3.08, 0.86, 0.74))])]),
                  Limb=dict(color=(255, 200, 50), grad=0.16, patterns=spots),
                  Dark=dict(color=(242, 170, 40), grad=0.12, patterns=[("spots", 6, (196, 120, 36), 0.14)]),
                  Head=dict(color=(255, 208, 60), grad=0.08),
                  Hood=dict(color=(255, 206, 58), grad=0.1, rough=0.4, patterns=spots,
                            paint=[("front", (255, 240, 192), [("rect", (-1.2, 3.8, 1.2, 4.16))])]),
                  Lining=dict(color=(150, 96, 24), grad=0.1),
                  Lip=dict(color=(255, 150, 112), grad=0.05, rough=0.35),
                  Spike=dict(color=(255, 236, 170), tip=(176, 108, 40), tip_from=0.15, grad=0),
                  Glove=dict(color=(255, 146, 40), grad=0.1, rough=0.35),
                  Fin=dict(color=(255, 186, 56), tip=(244, 116, 32), tip_from=0.3, grad=0, rough=0.4, root=(255, 204, 54),
                           rays=((206, 104, 26), 0.7), edge=((255, 214, 140), 0.94)))
    b = CharBuilder("Pufferfish", styles)
    standard_body(b, dict(head="Head", chest="Body", waist="Body", arm="Limb", forearm="Limb", hand="Glove",
                          thigh="Limb", shin="Limb", foot="Glove"), shape=PUFFER_BODY)
    with b.part("UpperTorso__Spikes"):
        # spikes all over the puffed-up body, leaving the neck and the shoulders free
        n = 96
        c0 = V((0, 0, 3.18))
        for k in range(n):
            zc = 1 - 2 * (k + 0.5) / n
            rr = math.sqrt(1 - zc * zc)
            a = k * 2.39996
            d = V((math.cos(a) * rr, math.sin(a) * rr * 0.8, zc * 0.9)).normalized()
            if d.z > 0.62 or (abs(d.x) > 0.6 and d.z > -0.2) or d.z < -0.7:
                continue
            p, nrm = b.hit("UpperTorso", c0 + d * 4, -d)
            if p is None or not 2.5 < p.z < 3.9:
                continue
            spike(b, "Spike", p - nrm * 0.02, (nrm + d).normalized(), 0.3 if d.y < 0 else 0.36, 0.085)
    hood = Hood(c=(0, 0.1, 4.64), r=(1.0, 1.0, 0.9), t=0.12, bumps=[(-90, -10, 0.06, 30)])
    wear_hood(b, hood, fat_lip=0.1, eye_r=0.24, eye_at=(40, 32), brows="surprised", blush=True)
    with b.part("Head__Spikes"):
        for ph, step, ph0 in ((-20, 30, 0), (8, 30, 15), (36, 30, 0), (62, 45, 22)):
            for k in range(int(360 / step)):
                th = ph0 + k * step
                if math.degrees(math.acos(max(-1.0, min(1.0, _dir(th, ph).dot(_dir(-90, -2)))))) < 58:
                    continue
                P, N = hood.point(th, ph)
                spike(b, "Spike", P - N * 0.03, N, 0.34, 0.09)
        P, N = hood.point(0, 90)
        spike(b, "Spike", P - N * 0.03, N, 0.38, 0.1)
    fish_fins(b, "Fin", "Body", crest=False, calf=False, ear_o=(0.94, 0.16, 4.5), tail_shape="round_tail")
    for side, sx in (("Left", 1), ("Right", -1)):
        for part, cx, zs in (("UpperArm", ARM_X, (3.2, 3.68)), ("LowerArm", ARM_X, (2.5, 2.82)),
                             ("UpperLeg", LEG_X, (1.36, 1.76)), ("LowerLeg", LEG_X, (0.6, 0.92))):
            with b.part(f"{side}{part}__Spikes"):
                for z in zs:
                    for dvec in ((sx, -0.45, 0.1), (sx, 0.45, 0.1), (sx * 0.2, -1, 0.0)):
                        d = V(dvec).normalized()
                        o = V((sx * cx, 0, z))
                        p, nrm = b.hit(f"{side}{part}", o + d * 3, -d)
                        if p is not None:
                            spike(b, "Spike", p - nrm * 0.02, (nrm + d).normalized(), 0.22, 0.065)
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
                          thigh="Shell", shin="Shell", foot="ShellDark"), hands=False, shape=CRAB_BODY)
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
            w = 2 * b.half_width(f"{side}UpperArm", 3.1) + 0.08
            b.rbox("ShellDark", (x, 0, 3.1), (w, w, 0.12), bev=0.05, segs=2)
            for y in (-0.25, 0.25):
                spike(b, "ClawTip", (x, y, 3.98), (sx * 0.3, y, 1), 0.18, 0.07)
        with b.part(f"{side}LowerArm"):
            for z in (2.55, 2.85):
                spike(b, "ClawTip", (x + sx * 0.46, 0, z), (sx, 0, 0.25), 0.16, 0.06)
        with b.part(f"{side}LowerLeg"):
            w = 2 * b.half_width(f"{side}LowerLeg", 1.0) + 0.08
            b.rbox("ShellDark", (sx * LEG_X, 0, 1.0), (w, w, 0.1), bev=0.04, segs=2)
    with b.part("Head__EyeStalks"):
        for sx in (-1, 1):
            pts = [(sx * 0.26, 0.0, 5.1), (sx * 0.34, -0.04, 5.48), (sx * 0.43, -0.08, 5.78)]
            b.ttube("Shell", spline(pts, 5), taper(11, 0.11, 0.085), n=12, grad=False)
            b.ball("ShellDark", (sx * 0.34, -0.04, 5.46), 0.13, seg=(12, 8))
            b.ball("Shell", (sx * 0.44, -0.08, 5.94), 0.27, seg=(16, 12))
            b.eye((sx * 0.45, -0.14, 5.98), 0.24, look=(sx * 0.15, -1, 0.05))
            brow_over(b, (sx * 0.44, -0.08, 5.94), 0.27, "angry", sx)
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
                  GlowPink=dict(color=(255, 140, 232), grad=0, light=False),
                  Glove=dict(color=(196, 150, 255), grad=0.08, rough=0.25))
    b = CharBuilder("Jellyfish", styles)
    standard_body(b, dict(head="Head", chest="Jelly", waist="Jelly", arm="Jelly", forearm="Jelly", hand="Glove",
                          thigh="Jelly", shin="Jelly", foot="Glove"), shape=JELLY_BODY)
    # the bell sits on the crown, tipped back so its front rim stays above the face
    BZ, BR, BH, TILT = 4.84, 1.08, 0.78, math.radians(-16)
    rot = Matrix.Rotation(TILT, 4, "X")

    def bell(x, y, z):
        return tuple(V((0, 0, BZ)) + rot @ V((x, y, z - BZ)))
    with b.part("Head__BellGlass"):
        with b.grad(lambda co: (co.z - BZ) / BH):
            b.dome("BellGlass", (0, 0, BZ), BR, seg=40, rings=12, sc=(1, 1, BH / BR), rx=TILT)
        for k in range(18):
            a = TAU * k / 18
            # scalloped skirt round the rim
            b.ball("BellGlass", bell(math.cos(a) * (BR - 0.02), math.sin(a) * (BR - 0.02), BZ - 0.04), 0.2,
                   seg=(12, 8), sc=(1, 1, 0.5), rx=TILT)
    with b.part("Head__BellGlow"):
        for k in range(4):
            a = TAU * k / 4 + PI / 4
            r = 0.44
            zt = BZ + BH * math.sqrt(1 - (r / BR) ** 2) - 0.2        # inside the bell, seen through the jelly
            b.torus("GlowPink", bell(math.cos(a) * r, math.sin(a) * r, zt), 0.17, 0.045, 16, 6,
                    rx=TILT, rz=a + PI / 2, a0=0, a1=PI * 1.4)
        for k in range(18):
            a = TAU * (k + 0.5) / 18
            b.ball("Glow", bell(math.cos(a) * (BR + 0.02), math.sin(a) * (BR + 0.02), BZ - 0.02), 0.05, seg=(6, 4))
    with b.part("Head__Tentacles"):
        for k in range(14):
            a = math.radians(-30 + k * 18)
            if abs(((math.degrees(a) - 270) + 180) % 360 - 180) < 78:
                continue
            x0, y0 = math.cos(a) * (BR - 0.08), math.sin(a) * (BR - 0.08)
            back = math.sin(a) > 0.35
            L = 1.6 if back else 0.6
            pts = []
            for i in range(10):
                t = i / 9
                w = math.sin(t * PI * 2.6 + k) * 0.07
                pts.append(bell(x0 * (1 + 0.12 * t) + w * math.sin(a), y0 * (1 + 0.18 * t) + w * math.cos(a), BZ - 0.06 - L * t))
            b.ttube("Frill", pts, taper(10, 0.06, 0.018), n=7)
    with b.part("LowerTorso__Tentacles"):
        # long trailing tentacles growing out of the lower back
        for k, x in enumerate((-0.66, -0.4, -0.14, 0.12, 0.38, 0.64)):
            yb = b.hit("LowerTorso", (x, 3, 2.25), (0, -1, 0))[0].y
            pts = [(x, yb - 0.12, 2.3)]
            for i in range(15):
                t = i / 14
                pts.append((x + math.sin(t * 7 + k) * 0.1, yb + 0.1 + 0.3 * t + math.cos(t * 5 + k) * 0.06, 2.22 - 2.1 * t))
            if k % 2 == 0:
                b.ttube("Frill", pts, taper(16, 0.17, 0.04), n=10, flat_b=0.3)
            else:
                b.ttube("Frill", pts, taper(16, 0.07, 0.02), n=7)
            b.ball("Glow", tuple(V(pts[-1])), 0.08, seg=(8, 6))
    with b.part("UpperTorso__Tentacles"):
        # glowing ribbons growing out of the chest under the bell
        for k, x0 in enumerate((-0.6, -0.3, 0.0, 0.3, 0.6)):
            L = (1.5, 1.9, 2.2, 1.9, 1.5)[k]
            yf = b.hit("UpperTorso", (x0, -3, 3.72), (0, 1, 0))[0].y
            pts = [(x0, yf + 0.14, 3.78)]
            for i in range(13):
                t = i / 12
                pts.append((x0 * (1 + 0.15 * t) + math.sin(t * 6.5 + k * 1.7) * 0.06, yf - 0.06 - 0.12 * t - 0.08 * math.sin(t * PI),
                            3.66 - L * t))
            if k % 2 == 0:
                b.ttube("Frill", pts, taper(14, 0.11, 0.03), n=10, flat_b=0.35)
            else:
                b.ttube("Frill", pts, taper(14, 0.055, 0.018), n=7)
            b.ball("Glow", tuple(V(pts[-1])), 0.065, seg=(8, 6))
    for side, sx in (("Left", 1), ("Right", -1)):
        with b.part(f"{side}Hand__Frills"):
            # short stinging frills hanging from the hands
            for k, (dx, dy) in enumerate(((0.22, -0.2), (-0.18, 0.14), (0.1, 0.26), (-0.06, -0.24))):
                x = sx * ARM_X + dx
                pts = [(x + math.sin(i * 0.9 + k) * 0.06, dy, 2.12 - i * 0.12) for i in range(9)]
                b.ttube("Frill", pts, taper(9, 0.06, 0.02), n=6)
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
                  Glove=dict(color=(250, 160, 214), grad=0.1, rough=0.35),
                  Head=dict(color=(176, 116, 236), grad=0.08),
                  Hood=dict(color=(150, 76, 220), grad=0.12, rough=0.4, patterns=[("mottle", 5, (112, 46, 176), 0.6),
                                                                                   ("spots", 6, (190, 130, 246), 0.14)]),
                  Lining=dict(color=(70, 26, 110), grad=0.1),
                  Lip=dict(color=(196, 140, 244), grad=0.05, rough=0.35))
    b = CharBuilder("Octopus", styles)
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Skin", forearm="Skin", hand="Skin",
                          thigh="Skin", shin="Skin", foot="Glove"), hands=False, shape=OCTO_BODY)
    # the octopus head is a hood whose mantle swells up and back into a soft bulb
    hood = Hood(r=(0.94, 0.96, 0.88), bumps=[(90, 52, 0.62, 36), (-90, 50, 0.14, 30), (0, 80, 0.12, 40)])
    wear_hood(b, hood, fat_lip=0.045, eye_r=0.19, eye_at=(30, 40), brows="happy", blush=True)
    with b.part("Head__Hood"):
        for th, ph, r in ((60, 40, 0.07), (120, 44, 0.08), (90, 66, 0.09), (40, 62, 0.06), (140, 62, 0.07), (70, 82, 0.06),
                          (110, 80, 0.07), (165, 30, 0.06), (15, 28, 0.06)):
            P, N = hood.point(th, ph)
            b.ball("Bump", tuple(P - N * r * 0.35), r, seg=(10, 8), sc=(1, 1, 0.6))
    with b.part("Head__Curls"):
        # little tentacles curling out from under the back of the hood
        for th in (20, 55, 90, 125, 160):
            P, N = hood.point(th, -44)
            out = V((N.x, N.y, 0)).normalized()
            pts = [P - N * 0.06 + V((0, 0, 0.04)), P + out * 0.12 - V((0, 0, 0.1)), P + out * 0.32 - V((0, 0, 0.16)),
                   P + out * 0.46 - V((0, 0, 0.04)), P + out * 0.4 + V((0, 0, 0.08)), P + out * 0.3 + V((0, 0, 0.04))]
            tentacle(b, "Arm", pts, 0.09, 0.025, sucker="Sucker", per=5, rows=1, face=(0, 0, -1), every=3)
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
                    p, nrm = b.hit(f"{side}LowerArm", (x + sx * 3, y, z), (-sx, 0, 0))
                    b.cyl("Sucker", tuple(p - nrm * 0.04), tuple(p + nrm * 0.05), 0.1, 10)
    return b


# ---------------------------------------------------------------------------
# 6  Moray Eel
# ---------------------------------------------------------------------------

def moray_eel():
    teal = (24, 112, 140)
    spots = [("spots", 6.5, (228, 210, 74), 0.17), ("spots", 12, (200, 198, 86), 0.1)]
    styles = dict(EYES,
                  Skin=dict(color=teal, grad=0.16, patterns=spots,
                            paint=[("front", (206, 216, 96), [shield(3.96, 2.02, 0.3, 0.5, 0.36, 3.1)])]),
                  Limb=dict(color=(28, 88, 118), grad=0.16, patterns=spots),
                  Dark=dict(color=(20, 66, 92), grad=0.12, patterns=[("spots", 8, (196, 186, 74), 0.12)]),
                  Fin=dict(color=(34, 102, 128), tip=(196, 206, 92), tip_from=0.55, grad=0, rough=0.4,
                           patterns=[("spots", 10, (210, 200, 80), 0.12)], rays=((18, 62, 86), 0.55), edge=((226, 224, 100), 0.88)),
                  FinRim=dict(color=(220, 220, 96), grad=0),
                  Glove=dict(color=(214, 222, 96), grad=0.1, rough=0.35),
                  Tail=dict(color=teal, grad=0.0, patterns=spots),
                  Head=dict(color=(34, 100, 130), grad=0.08),
                  Hood=dict(color=(34, 100, 130), grad=0.1, rough=0.4, patterns=spots,
                            paint=[("front", (206, 216, 96), [("rect", (-1.2, 3.7, 1.2, 4.14))]),
                                   ("side", (14, 40, 58), gills(0.2, 4.42, 1, 0.13, 0.44, 0.06))]),
                  Lining=dict(color=(72, 18, 30), grad=0.1),
                  Lip=dict(color=(160, 50, 66), grad=0.05, rough=0.35),
                  Tooth=dict(color=(255, 252, 236), tip=(240, 236, 210), tip_from=0.5, grad=0, rough=0.3))
    b = CharBuilder("MorayEel", styles)
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Limb", forearm="Limb", hand="Glove",
                          thigh="Limb", shin="Limb", foot="Dark"), shape=EEL_BODY)
    hood = Hood(r=(0.88, 0.96, 0.9), bumps=[(-90, 30, 0.2, 26), (-90, -40, 0.12, 24)])
    wear_hood(b, hood, fat_lip=0.05, teeth=("Tooth", 0.07, 0.2, 0.15), eye_r=0.17, eye_at=(38, 36), brows="grumpy")
    with b.part("Head__Crest"):
        # the long eel dorsal fin starts on the crown and runs down the back
        fin(b, "Fin", "eel_crest", Fm((0, -0.12, 5.48), (0, 1, -0.45), (0, 0.4, 1)), scale=0.75)
    with b.part("UpperTorso__DorsalFin"):
        fin(b, "Fin", "ridge", Fm((0, back_y(b, "UpperTorso", 3.0) - 0.02, 2.36), (0, 0, 1), (0, 1, 0.04)), scale=0.95)
    yb = back_y(b, "LowerTorso", 2.22)
    with b.part("LowerTorso__Tail"):
        # a long eel tail that drops to the floor and curls round, with a spiky ridge along its top
        pts = [(0, yb - 0.16, 2.28), (0, yb + 0.3, 2.06), (0.08, yb + 0.78, 1.5), (0.3, yb + 1.08, 0.82), (0.8, yb + 1.22, 0.4),
               (1.4, yb + 1.02, 0.3), (1.78, yb + 0.6, 0.3), (1.76, yb + 0.22, 0.34)]
        path, radii, d = tail(b, "Tail", pts, 0.4, 0.07, per=10)
        up = V((0, 0, 1))
        i = 6
        while i < len(path) - 6:
            seg = path[i + 5] - path[i]
            L = seg.length
            r = radii[i]
            h = 0.12 + 0.32 * radii[i] / radii[0]
            u = seg.normalized()
            o = path[i] + up * r * 0.75
            fin(b, "Fin", (((0, 0), (L, 0)), [(0.35 * L, h), (1.1 * L, h * 0.55)]), Fm(tuple(o), tuple(u), (0, 0, 1)),
                thick=0.04, spine=0.03, rib=0.02, sink=0.04)
            i += 5
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
                Head=dict(color=skin, grad=0.08, rough=0.38),
                Hood=dict(color=skin, grad=0.1, rough=0.38,
                          paint=[("front", white, [("rect", (-1.2, 3.7, 1.2, 4.18))]),
                                 ("side", tuple(int(c * 0.5) for c in dark), gills(0.2, 4.5, 3, 0.12, 0.38, 0.05))]),
                Lining=dict(color=(96, 24, 38), grad=0.1),
                Lip=dict(color=(214, 86, 104), grad=0.05, rough=0.35),
                Tooth=dict(color=(255, 255, 250), grad=0, rough=0.25))


def _shark_body(b, dorsal=True):
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Limb", forearm="Limb", hand="White",
                          thigh="Limb", shin="Limb", foot="White"), shape=SHARK_BODY)
    if dorsal:
        with b.part("UpperTorso__DorsalFin"):
            fin(b, "Fin", "shark", Fm((0, back_y(b, "UpperTorso", 3.5) - 0.02, 3.5), (0, 0.42, -1), (0, 1, 0.42)), scale=0.62)
    shark_tail(b, "Skin", "Fin", "shark_tail")
    for side, sx in (("Left", 1), ("Right", -1)):
        with b.part(f"{side}UpperArm__Fin"):
            fin(b, "Fin", "pec",
                Fm((sx * (ARM_X + b.half_width(f"{side}UpperArm", 3.46) - 0.02), 0.0, 3.46), (0, 1, 0.3), (sx * 0.55, 0.45, -1)),
                scale=0.8)
    with b.part("LowerTorso__Fins"):
        for sx in (-1, 1):
            fin(b, "Fin", "pelvic", Fm((sx * 0.56, back_y(b, "LowerTorso", 2.14, sx * 0.56) - 0.02, 2.14), (0, 0, 1),
                                       (sx * 0.5, 1, -0.5)), scale=0.9)


def shark_tail(b, body, fin_st, shape, scale=1.25, flukes=False):
    """A long, thick tail that curves back and down from the lower back. Sharks end in a tall
    tail fin (upright), orcas in flat flukes."""
    yb = back_y(b, "LowerTorso", 2.22)
    with b.part("LowerTorso__Tail"):
        path, radii, d = tail(b, body, [(0, yb - 0.22, 2.32), (0, yb + 0.3, 2.18), (0, yb + 0.8, 2.04), (0, yb + 1.24, 2.08),
                                        (0, yb + 1.56, 2.3)], 0.44, 0.13)
        if flukes:
            fin(b, fin_st, shape, Fm(tuple(path[-1] - d * 0.08), (1, 0, 0), d), scale=scale)
        else:
            up = V((0, -d.z, d.y)).normalized()
            fin(b, fin_st, shape, Fm(tuple(path[-1] - d * 0.08), tuple(up), d), scale=scale)
            # a small second dorsal fin on top of the tail
            k = int(len(path) * 0.55)
            dk = (path[k + 1] - path[k - 1]).normalized()
            upk = V((0, -dk.z, dk.y)).normalized()
            fin(b, fin_st, "pelvic", Fm(tuple(path[k] + upk * radii[k] * 0.7), tuple(-dk), tuple(upk)), scale=0.75)


def shark():
    b = CharBuilder("Shark", _shark_styles((78, 128, 196), (52, 90, 150), (72, 120, 190), (46, 80, 136)))
    _shark_body(b)
    # the shark's head is a hood: snout over the face, the face in its jaws
    hood = Hood(r=(0.92, 0.96, 0.88), bumps=[(-90, 34, 0.24, 26), (-90, -42, 0.1, 22)])
    wear_hood(b, hood, fat_lip=0.055, teeth=("Tooth", 0.135, 0.2, 0.125), eye_r=0.15, eye_at=(54, 24), brows="angry")
    with b.part("Head__Fin"):
        fin(b, "Fin", "shark", Fm((0, 0.06, 5.46), (0, 1, 0), (0, 0, 1)), scale=0.56)
    return b


def hammerhead():
    st = _shark_styles((84, 150, 214), (56, 108, 168), (78, 142, 206), (50, 98, 156))
    st["Hammer"] = dict(color=(84, 150, 214), grad=0, rough=0.38, patterns=[("zgrad", 5.2, 5.25, (236, 242, 248))])
    b = CharBuilder("HammerheadShark", st)
    _shark_body(b)
    hood = Hood(r=(0.92, 0.96, 0.88), bumps=[(-90, 30, 0.14, 26), (-90, -42, 0.1, 22)])
    wear_hood(b, hood, fat_lip=0.055, teeth=("Tooth", 0.135, 0.2, 0.125), eyes=False)
    with b.part("Head__Hammer"):
        # the hammer: a flat, wide wing across the crown, swept forward, with round eye lobes at its tips
        secs = []
        n = 41
        for i in range(n):
            t = -1 + 2 * i / (n - 1)
            x = 1.42 * t
            k = abs(t)
            end = math.sqrt(max(0.0, 1 - ((k - 0.8) / 0.2) ** 2)) if k > 0.8 else 1.0
            lobe = math.exp(-((k - 0.86) / 0.1) ** 2)          # the eye lobe swells a little
            d = (0.46 - 0.1 * k + 0.06 * lobe) * (0.35 + 0.65 * end)
            th = (0.2 + 0.04 * k + 0.06 * lobe) * (0.35 + 0.65 * end)
            yc = 0.02 - 0.2 * k * k
            zc = 5.3 + 0.02 * k
            secs.append([(x, yc + d * math.cos(a), zc + th * math.sin(a) * (1.0 if math.sin(a) > 0 else 0.75))
                         for a in (TAU * j / 28 for j in range(28))])
        b.skin_rings("Hammer", secs)
        for sx in (-1, 1):
            b.eye((sx * 1.3, -0.26, 5.36), 0.24, look=(sx * 1.0, -0.8, 0.1))
            brow_over(b, (sx * 1.3, -0.26, 5.36), 0.24, "surprised" if sx > 0 else "happy", sx, front=(sx * 0.5, -1, 0))
            for dy in (-0.05, 0.05):
                b.ball("Dark", (sx * 0.62, -0.38 + dy * 0.2, 5.33 + dy), 0.035, seg=(8, 6))
    with b.part("Head__Fin"):
        fin(b, "Fin", "shark", Fm((0, 0.12, 5.52), (0, 1, 0), (0, 0, 1)), scale=0.46)
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
    eye = ("smooth", [(-0.3, 4.86), (-0.12, 5.06), (0.2, 5.16), (0.52, 5.1), (0.62, 4.98), (0.4, 4.88), (0.08, 4.82),
                      (-0.18, 4.78)])
    styles = dict(EYES,
                  Black=dict(color=black, grad=0.06, rough=0.28,
                             paint=[("front", white, [belly]), ("side", white, [flank]), ("back", (132, 138, 152), [saddle])]),
                  Limb=dict(color=black, grad=0.08, rough=0.28, paint=[("side", white, [("ellipse", (0.02, 3.42, 0.26, 0.2))])]),
                  White=dict(color=white, grad=0.04),
                  Fin=dict(color=(30, 30, 38), tip=(52, 54, 66), tip_from=0.6, grad=0, rough=0.28),
                  Head=dict(color=(238, 238, 244), grad=0.05, rough=0.3),   # white face inside the hood so the face reads
                  Hood=dict(color=(30, 30, 38), grad=0.06, rough=0.26,
                            paint=[("side", white, [eye]), ("front", white, [("rect", (-1.2, 3.7, 1.2, 4.18))]),
                                   ("back", (120, 126, 140), [("ellipse", (0, 4.3, 0.5, 0.18))])]),
                  Lining=dict(color=(92, 30, 44), grad=0.1),
                  Lip=dict(color=(222, 112, 132), grad=0.05, rough=0.35),
                  Tooth=dict(color=(255, 255, 250), grad=0, rough=0.25))
    b = CharBuilder("Orca", styles)
    standard_body(b, dict(head="Head", chest="Black", waist="Black", arm="Limb", forearm="Limb", hand="White",
                          thigh="Limb", shin="Limb", foot="White"), shape=ORCA_BODY)
    hood = Hood(r=(0.94, 0.96, 0.88), bumps=[(-90, 34, 0.2, 30), (-90, -44, 0.08, 24), (0, 85, 0.06, 40)])
    wear_hood(b, hood, fat_lip=0.05, teeth=("Tooth", 0.08, 0.11, 0.1), eye_r=0.14, eye_at=(58, 14), brows="cheeky")
    with b.part("Head__Fin"):
        # the tall orca dorsal fin
        fin(b, "Fin", "orca", Fm((0, 0.08, 5.46), (0, 1, 0), (0, 0, 1)), scale=0.5)
    with b.part("UpperTorso__DorsalFin"):
        fin(b, "Fin", "shark", Fm((0, back_y(b, "UpperTorso", 3.5) - 0.02, 3.5), (0, 0.4, -1), (0, 1, 0.4)), scale=0.5)
    shark_tail(b, "Black", "Fin", "flukes", scale=1.15, flukes=True)
    for side, sx in (("Left", 1), ("Right", -1)):
        with b.part(f"{side}UpperArm__Paddle"):
            fin(b, "Fin", "paddle",
                Fm((sx * (ARM_X + b.half_width(f"{side}UpperArm", 3.3) - 0.02), 0.12, 3.3), (0, 1, 0), (sx * 0.9, 0.35, -0.6)),
                scale=0.85, scallop=0.12)
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
                  Glove=dict(color=(255, 170, 190), grad=0.1, rough=0.35),
                  Sucker=dict(color=(255, 172, 196), grad=0),
                  SuckerIn=dict(color=(230, 100, 140), grad=0),
                  Head=dict(color=(246, 120, 132), grad=0.08),
                  Hood=dict(color=(228, 50, 62), grad=0.1, rough=0.4, patterns=pat,
                            paint=[("front", (246, 118, 130), [("rect", (-1.2, 3.7, 1.2, 4.16))])]),
                  Lining=dict(color=(110, 20, 34), grad=0.1),
                  Lip=dict(color=(250, 140, 156), grad=0.05, rough=0.35))
    b = CharBuilder("GiantSquid", styles)
    standard_body(b, dict(head="Head", chest="Skin", waist="Skin", arm="Skin", forearm="Skin", hand="Skin",
                          thigh="Skin", shin="Skin", foot="Glove"), hands=False, shape=SQUID_BODY)
    # the squid head is a hood that rises into a pointed mantle
    hood = Hood(r=(0.92, 0.96, 0.88), bumps=[(0, 90, 0.62, 22), (0, 90, 0.34, 40), (90, 40, 0.1, 40)])
    wear_hood(b, hood, fat_lip=0.045, eye_r=0.2, eye_at=(56, 18), brows="angry")
    top = hood.surf(0, 90)
    with b.part("Head__Fins"):
        for sx in (-1, 1):
            P, N = hood.point(90 - 90 * sx, 72)
            fin(b, "Mantle", "squid", Fm(tuple(P - N * 0.02), (0, 0, 1), (sx, 0, -0.25)), scale=0.95)
    with b.part("Head__Hood"):
        b.ball("Mantle", tuple(top - V((0, 0, 0.06))), 0.1, seg=(12, 8))
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
    hood_band = [((0, 0.24, 4.6), (9, 0.2, 9), black, 0.02), ((0, 0.24, 4.6), (9, 0.14, 9), white, 0.02)]
    styles = dict(EYES,
                  Orange=dict(color=orange, grad=0.12, patterns=[("scales", 1.4, (208, 82, 14))], regions=bands(3.18, 0.17)),
                  Limb=dict(color=(248, 110, 24), grad=0.16, patterns=[("scales", 1.5, (208, 82, 14))], regions=bands(3.18, 0.17)),
                  Dark=dict(color=(226, 90, 18), grad=0.14, patterns=[("scales", 1.7, (186, 68, 12))]),
                  White=dict(color=white, grad=0.04),
                  Black=dict(color=black, grad=0, rough=0.35),
                  Fin=dict(color=(255, 136, 36), tip=(255, 104, 22), tip_from=0.3, grad=0, rough=0.4,
                           rays=((206, 76, 12), 0.6), edge=(black, 0.84)),
                  Head=dict(color=(252, 120, 30), grad=0.08),
                  Hood=dict(color=(252, 118, 28), grad=0.1, rough=0.4, patterns=[("scales", 1.3, (212, 86, 16))], regions=hood_band),
                  Lining=dict(color=(150, 60, 22), grad=0.1),
                  Lip=dict(color=(236, 124, 146), grad=0.05, rough=0.35))
    b = CharBuilder("Clownfish", styles)
    standard_body(b, dict(head="Head", chest="Orange", waist="Orange", arm="Limb", forearm="Limb", hand="White",
                          thigh="Limb", shin="Limb", foot="Dark"), shape=dict(FISH_BODY, belly=(0.78, 0.2, 0.72)))
    hood = Hood(bumps=[(-90, -10, 0.08, 30)])
    wear_hood(b, hood, fat_lip=0.075, eye_r=0.21, brows="cheeky", blush=True)
    # clownfish fins are soft and rounded: only a slight wave between the rays
    fish_fins(b, "Fin", "Orange", crest_o=(0, 0.02, 5.42), ear_o=(0.86, 0.16, 4.5), tail=False, scallop=0.08)
    path, radii = fish_tail(b, "Fin", "Orange", "clown_tail", scale=1.15, scallop=0.06)
    with b.part("LowerTorso__Tail"):
        # the white band with black edges round the tail
        k = len(path) // 3
        d = (path[k + 1] - path[k - 1]).normalized()
        c, r = path[k], radii[k] * 1.07
        b.cyl("White", tuple(c - d * 0.08), tuple(c + d * 0.08), r, 20)
        for o in (-0.1, 0.1):
            b.cyl("Black", tuple(c + d * (o - 0.025)), tuple(c + d * (o + 0.025)), r * 1.02, 20)
    return b


CREATURES = [tiny_fish, pufferfish, crab, jellyfish, octopus, moray_eel, shark, hammerhead, orca, giant_squid, clownfish]
NAMES = {"TinyFish": "Tiny Fish", "Pufferfish": "Pufferfish", "Crab": "Crab", "Jellyfish": "Jellyfish", "Octopus": "Octopus",
         "MorayEel": "Moray Eel", "Shark": "Shark", "HammerheadShark": "Hammerhead Shark", "Orca": "Orca",
         "GiantSquid": "Giant Squid", "Clownfish": "Clownfish"}
