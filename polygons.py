#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import mpmath as math

from hyperbolic import Point, PointedVector, Line

def get_angle_side(num, radius):
    origin = PointedVector(0.0, 0.0, 0.0)
    p1 = origin.advance(radius)
    p2 = origin.turn(2 * math.pi / float(num)).advance(radius)
    ray_line = origin.to_line().reverse()
    side_line = p1.to_point().line_to(p2.to_point())
    angle = ray_line.angle_with(side_line, intersection=p1)
    side = p1.to_point().distance(p2, line=side_line)
    return 2.0 * angle, side

def build_polygon_with_center(num, radius, pv):
    return [pv.turn(2 * math.pi * float(k) / float(num)).advance(radius).to_point() for k in xrange(num)]

def draw_polygon(ctx, points):
    for i in xrange(len(points)):
        points[i].segment_to(points[(i+1) % len(points)]).draw(ctx)
