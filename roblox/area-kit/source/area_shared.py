"""Shared -- pieces for the shadow walls between areas (any area's palette)."""
import math

from kit import PI, TAU, Builder, R, T, V

AREA = "Shared"
GROUND = (120, 124, 140)


def border_pylon():
    """Stands at the ends and along a shadow wall; its glow strip is Accent so each wall can take its area's colour."""
    b = Builder("BorderPylon", AREA)
    b.lathe("Charcoal", [(0, 0), (3.2, 0), (3.2, 1.0), (2.4, 1.6), (0, 1.6)], n=8)
    b.lathe("DarkMetal", [(0, 1.6), (1.6, 1.6), (1.2, 26.0), (0, 26.0)], n=8)
    for k in range(4):
        a = TAU * k / 4 + PI / 8
        b.box("Accent", (math.cos(a) * 1.35, math.sin(a) * 1.35, 14.0), (0.35, 0.35, 22.0), rz=a, bev=0)
    for z in (4.0, 25.0):
        b.ring("Metal", (0, 0, 0), 1.7 - z * 0.015, 1.1, z, z + 0.6, n=8)
    b.lathe("Accent", [(0, 26.0), (1.4, 26.0), (0, 29.0)], n=8)
    return b


def price_plaque():
    """Hangs on a shadow wall. Put a SurfaceGui on its Screen part for the price; the lock sits above it."""
    b = Builder("PricePlaque", AREA)
    W, H = 20.0, 9.0
    b.bx("Charcoal", -W / 2, W / 2, -0.6, 0.6, 0, H)
    b.bx("Accent", -W / 2 - 0.5, W / 2 + 0.5, -0.8, 0.8, -0.5, 0)
    b.bx("Accent", -W / 2 - 0.5, W / 2 + 0.5, -0.8, 0.8, H, H + 0.5)
    for sx in (-1, 1):
        b.bx("Accent", sx * (W / 2 + 0.25) - 0.25, sx * (W / 2 + 0.25) + 0.25, -0.8, 0.8, -0.5, H + 0.5)
    b.bx("Black", -W / 2 + 0.8, W / 2 - 0.8, -0.75, -0.6, 0.8, H - 0.8, bev=0)
    # padlock on top
    with b.at(T(0, 0, H + 0.5)):
        b.bx("Gold", -2.2, 2.2, -1.0, 1.0, 0.4, 4.0)
        b.torus("Metal", (0, 0, 4.0), 1.4, 0.4, 16, 6, rx=PI / 2, a0=0, a1=PI)
        b.cyl("Black", (0, -1.0, 2.6), (0, -1.15, 2.6), 0.5, 10)
        b.bx("Black", -0.18, 0.18, -1.15, -1.0, 1.3, 2.4, bev=0)
    return b


ASSETS = [border_pylon, price_plaque]
