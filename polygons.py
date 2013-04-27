#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import mpmath as math
from scipy import optimize

from hyperbolic import Point, PointedVector, Line

MAX_SEARCH = 100.0

def get_angle_from_radius(num, radius):
    origin = PointedVector(0.0, 0.0, 0.0)
    p1 = origin.advance(radius)
    p2 = origin.turn(2 * math.pi / float(num)).advance(radius)
    ray_line = origin.to_line().reverse()
    side_line = p1.to_point().line_to(p2.to_point())
    angle = ray_line.angle_with(side_line, intersection=p1)
    return 2.0 * angle

def get_side_from_radius(num, radius):
    origin = PointedVector(0.0, 0.0, 0.0)
    p1 = origin.advance(radius)
    p2 = origin.turn(2 * math.pi / float(num)).advance(radius)
    side = p1.to_point().distance(p2.to_point())
    return side

def get_radius_from_side(num, side):
    func = lambda x: get_side_from_radius(num, x) - side
    radius, root_results = optimize.brentq(func, 0.0, MAX_SEARCH, full_output=True)
    if root_results.converged:
        return radius
    else:
        raise Exception("Could not compute radius")

def get_radius_from_angle(num, angle):
    func = lambda x: get_angle_from_radius(num, x) - angle
    radius, root_results = optimize.brentq(func, 0.0, MAX_SEARCH, full_output=True)
    if root_results.converged:
        return radius
    else:
        raise Exception("Could not compute radius")

def build_polygon_with_center(num, radius, pv):
    return [pv.turn(2 * math.pi * float(k) / float(num)).advance(radius).to_point() for k in xrange(num)]

def draw_polygon(ctx, points):
    for i in xrange(len(points)):
        points[i].segment_to(points[(i+1) % len(points)]).draw(ctx)
