#!/usr/bin/python
# -*- coding: utf-8 -*-

import mpmath as math

from hyperbolic import Point, InfPoint, Line, PointedVector


HEXAGON_COLORS = [(155, 0, 0),
                  (155, 155, 0),
                  (0, 155, 0),
                  (0, 155, 155),
                  (0, 0, 155),
                  (155, 0, 155)]

def draw_hexagon(ctx, pv, a, b, c, color=False):
    cosha, coshb, coshc = map(math.cosh, [a, b, c])
    sinha, sinhb, sinhc = map(math.sinh, [a, b, c])
    sides = [a,
             math.acosh((cosha * coshb + coshc) / (sinha * sinhb)),
             b,
             math.acosh((coshb * coshc + cosha) / (sinhb * sinhc)),
             c,
             math.acosh((coshc * cosha + coshb) / (sinhc * sinha))]

    points = []
    lines = []
    for side in sides:
        points.append(pv.to_point())
        lines.append(pv.to_line())
        pv = pv.advance(side)
        pv = pv.turn(0.5 * math.pi)

    for line, color in zip(lines, HEXAGON_COLORS):
        ctx.set_source_rgb(*color)
        line.draw_poincare(ctx)

    ctx.set_source_rgb(0, 0, 0)
    for point in points:
        point.draw_poincare(ctx)
