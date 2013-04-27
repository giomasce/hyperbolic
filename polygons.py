#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import math
from scipy import optimize

from hyperbolic import Point, PointedVector, Line
from point_cache import GridApproximationPointCache

MIN_SEARCH = 0.00000001
MAX_SEARCH = 10.0

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

RADIUS_FROM_SIDE_CACHE = {}
RADIUS_FROM_ANGLE_CACHE = {}

def get_radius_from_side(num, side):
    if (num, side) not in RADIUS_FROM_SIDE_CACHE:
        func = lambda x: get_side_from_radius(num, x) - side
        radius, root_results = optimize.brentq(func, MIN_SEARCH, MAX_SEARCH, full_output=True)
        if root_results.converged:
            RADIUS_FROM_SIDE_CACHE[(num, side)] = radius
        else:
            raise Exception("Could not compute radius")
    return RADIUS_FROM_SIDE_CACHE[(num, side)]

def get_radius_from_angle(num, angle):
    if (num, angle) not in RADIUS_FROM_ANGLE_CACHE:
        func = lambda x: get_angle_from_radius(num, x) - angle
        radius, root_results = optimize.brentq(func, MIN_SEARCH, MAX_SEARCH, full_output=True)
        if root_results.converged:
            RADIUS_FROM_ANGLE_CACHE[(num, angle)] = radius
        else:
            raise Exception("Could not compute radius")
    return RADIUS_FROM_ANGLE_CACHE[(num, angle)]

def flush_inversion_caches():
    RADIUS_FROM_SIDE_CACHE = {}
    RADIUS_FROM_ANGLE_CACHE = {}

def build_polygon_with_center(num, center, pv):
    return [pv.turn(2 * math.pi * float(k) / float(num)).advance(radius).to_point() for k in xrange(num)]

def build_polygon_with_side(num, side, pv):
    radius = get_radius_from_side(num, side)
    angle = get_angle_from_radius(num, radius)
    points = []
    for i in xrange(num):
        pv = pv.advance(side)
        points.append(pv.reverse())
        pv = pv.turn(math.pi - angle)
    return points

def build_polygon_with_angle(num, angle, pv):
    radius = get_radius_from_angle(num, angle)
    side = get_side_from_radius(num, radius)
    points = []
    for i in xrange(num):
        pv = pv.advance(side)
        points.append(pv.reverse())
        pv = pv.turn(math.pi - angle)
    return points

def get_center_with_side(num, side, pv):
    radius = get_radius_from_side(num, side)
    angle = get_angle_from_radius(num, radius)
    pv.turn(0.5 * angle)
    pv.advance(radius)
    return pv.to_point()

def get_center_with_angle(num, angle, pv):
    radius = get_radius_from_angle(num, angle)
    pv.turn(0.5 * angle)
    pv.advance(radius)
    return pv.to_point()

def draw_polygon(ctx, points):
    for i in xrange(len(points)):
        points[i].to_point().segment_to(points[(i+1) % len(points)].to_point()).draw(ctx)

def draw_polygons(ctx, polygons):
    for points in polygons:
        draw_polygon(ctx, points)

CACHE_EPSILON = 0.0000001
FAR_FIELD_EPSILON = 0.0001

def build_regular_tessellation(side_num, valence_num, pv, point_cache=None, polygons=None):
    if point_cache is None:
        point_cache = GridApproximationPointCache(CACHE_EPSILON)
    if polygons is None:
        polygons = []

    angle = 2.0 * math.pi / float(valence_num)
    center = get_center_with_angle(side_num, angle, pv)

    if point_cache.query(center):
        return
    else:
        point_cache.store(center)
        pvs = build_polygon_with_angle(side_num, angle, pv)
        polygons.append(pvs)
        #draw_polygon(ctx, pvs)
        if min(map(lambda x: x.to_point().to_eupoint().sqnorm(), pvs)) > 1.0 - FAR_FIELD_EPSILON:
            return
        for pv in pvs:
            build_regular_tessellation(side_num, valence_num, pv, point_cache=point_cache, polygons=polygons)

    return polygons
