#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

from euclidean import EuPoint, EuLine, EuCircle

def my_trunc(x):
    if x >= 0:
        return math.trunc(x)
    else:
        return math.trunc(x) - 1.0

POINT_RADIUS = 0.015

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_point(self):
        return self

    @classmethod
    def from_eupoint(self, point):
        return Point(point.x, point.y)

    def draw_klein(self, ctx):
        ctx.arc(self.x, self.y, POINT_RADIUS, 0, 2*math.pi)
        ctx.fill()
        #ctx.move_to(self.x, self.y)
        #ctx.line_to(self.x, self.y)
        #ctx.stroke()

    def line_to(self, point):
        point = point.to_point()
        euline = EuPoint(self.x, self.y).line_to(EuPoint(point.x, point.y))
        extrema = euline.intersection_circle(EuCircle(0.0, 0.0, 1.0))
        p1, p2 = map(lambda p: InfPoint.from_xy(p.x, p.y), extrema)
        return Line(p1, p2)

class InfPoint:

    def __init__(self, alpha):
        self.alpha = alpha
        self.coords = None

    @classmethod
    def from_xy(self, x, y):
        return InfPoint(math.atan2(y, x))

    @classmethod
    def from_eupoint(self, point):
        return InfPoint.from_xy(point.x, point.y)

    def normalize(self):
        self.alpha = self.alpha - 2*math.pi * my_trunc(self.alpha / (2*math.pi))

    def get_coords(self):
        if self.coords is None:
            self.coords = (math.cos(self.alpha), math.sin(self.alpha))
        return self.coords

    def to_point(self):
        x, y = self.get_coords()
        return Point(x, y)

    def draw_klein(self, ctx):
        x, y = self.get_coords()
        ctx.arc(x, y, POINT_RADIUS, 0, 2*math.pi)
        ctx.fill()

    def line_to(self, point):
        return self.to_point().line_to(point)

class Line:

    def __init__(self, p1, p2):
        """Two infinite points"""
        self.p1 = p1
        self.p2 = p2

    def draw_klein(self, ctx):
        x1, y1 = self.p1.get_coords()
        x2, y2 = self.p2.get_coords()
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    def to_euline(self):
        x1, y1 = self.p1.get_coords()
        x2, y2 = self.p2.get_coords()
        return EuPoint(x1, y1).line_to(EuPoint(x2, y2))

    def intersection(self, line):
        try:
            p = Point.from_eupoint(self.to_euline().intersection_line(line.to_euline()))
            if p.x**2 + p.y**2 > 1:
                return None
            else:
                return p
        except ZeroDivisionError:
            return None
