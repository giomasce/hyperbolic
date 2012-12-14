#!/usr/bin/python
# -*- coding: utf-8 -*-

import mpmath as math

from hyperbolic import Point, InfPoint, Line, PointedVector


def draw_hexagon(ctx, pv, a, b, c):
    cosha, coshb, coshc = map(math.cosh, [a, b, c])
    sinha, sinhb, sinhc = map(math.sinh, [a, b, c])
    sides = [a,
             math.acosh((cosha * coshb + coshc) / (sinha * sinhb)),
             b,
             math.acosh((coshb * coshc + cosha) / (sinhb * sinhc)),
             c,
             math.acosh((coshc * cosha + coshb) / (sinhc * sinha))]

    for side in sides:
        pv.to_point().draw_poincare(ctx)
        pv.to_line().draw_poincare(ctx)
        pv = pv.advance(side)
        pv = pv.turn(0.5 * math.pi)
