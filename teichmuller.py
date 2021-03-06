#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

from hyperbolic import Point, InfPoint, Line, PointedVector

HEXAGON_COLORS = [(155, 0, 0),
                  (155, 155, 0),
                  (0, 155, 0),
                  (0, 155, 155),
                  (0, 0, 155),
                  (155, 0, 155)]

EQUILATERAL_HEXAGON = math.acosh(2)

def hexagon_sides(a, b, c):
    cosha, coshb, coshc = map(math.cosh, [a, b, c])
    sinha, sinhb, sinhc = map(math.sinh, [a, b, c])
    sides = [a,
             math.acosh((cosha * coshb + coshc) / (sinha * sinhb)),
             b,
             math.acosh((coshb * coshc + cosha) / (sinhb * sinhc)),
             c,
             math.acosh((coshc * cosha + coshb) / (sinhc * sinha))]
    return sides

def draw_hexagon(ctx, pv, a, b, c, color=False):
    sides = hexagon_sides(a, b, c)

    points = []
    lines = []
    segments = []
    for side in sides:
        points.append(pv.to_point())
        lines.append(pv.to_line())
        pv = pv.advance(side)
        pv = pv.turn(0.5 * math.pi)
        segments.append(points[-1].segment_to(pv.to_point()))

    for line, segment, color in zip(lines, segments, HEXAGON_COLORS):
        ctx.cairo.set_source_rgb(*color)
        line.draw(ctx)

    ctx.cairo.set_source_rgb(0, 0, 0)
    for point in points:
        point.draw(ctx)

