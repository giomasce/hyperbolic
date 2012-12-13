#!/usr/bin/python
# -*- coding: utf-8 -*-

import mpmath as math

from euclidean import EuPoint, EuLine, EuCircle, crossratio

def my_trunc(x):
    if x >= 0:
        return math.trunc(x)
    else:
        return math.trunc(x) - 1.0

POINT_RADIUS = 0.015
CIRCLE_LINE_THRESHOLD = 0.000001

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.poincare_coords = None

    def to_point(self):
        return self

    def to_eupoint(self):
        return EuPoint(self.x, self.y)

    def to_eupoint_poincare(self):
        x, y = self.get_poincare_coords()
        return EuPoint(x, y)

    @classmethod
    def from_eupoint(self, point):
        return Point(point.x, point.y)

    def get_coords(self):
        return (self.x, self.y)

    def get_poincare_coords(self):
        if self.poincare_coords is None:
            mult = 1.0 / (1.0 + math.sqrt(1.0 - self.to_eupoint().sqnorm()))
            self.poincare_coords = (mult * self.x, mult * self.y)

        return self.poincare_coords

    def draw_klein(self, ctx):
        ctx.arc(self.x, self.y, POINT_RADIUS, 0, 2*math.pi)
        ctx.fill()
        #ctx.move_to(self.x, self.y)
        #ctx.line_to(self.x, self.y)
        #ctx.stroke()

    def draw_poincare(self, ctx):
        x, y = self.get_poincare_coords()
        ctx.arc(x, y, POINT_RADIUS, 0, 2*math.pi)
        ctx.fill()

    def line_to(self, point):
        point = point.to_point()
        eu1 = EuPoint(self.x, self.y)
        eu2 = EuPoint(point.x, point.y)
        euline = eu1.line_to(eu2)
        extrema = euline.intersection_circle(EuCircle(0.0, 0.0, 1.0))
        p1, p2 = map(lambda p: InfPoint.from_xy(p.x, p.y), extrema)

        # Fix the order; probably it would be better to implement
        # oriented EuLines
        if p1.to_point().to_eupoint().sqdistance(eu1) > \
                p1.to_point().to_eupoint().sqdistance(eu2):
            p1, p2 = p2, p1

        return Line(p1, p2)

    def distance(self, point, line=None):
        if line is None:
            line = self.line_to(point)
        return 0.5 * math.log(crossratio(line.p1.to_eupoint(), line.p2.to_eupoint(),
                                         point.to_eupoint(), self.to_eupoint()))

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

    def get_poincare_coords(self):
        return self.get_coords()

    def to_point(self):
        x, y = self.get_coords()
        return Point(x, y)

    def to_eupoint(self):
        return self.to_point().to_eupoint()

    def draw_klein(self, ctx):
        x, y = self.get_coords()
        ctx.arc(x, y, POINT_RADIUS, 0, 2*math.pi)
        ctx.fill()

    def draw_poincare(self, ctx):
        self.draw_klein(ctx)

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

    def draw_poincare(self, ctx):
        ref = self.ref_point()
        ref_klein = ref.to_eupoint()
        ref_poincare = ref.to_eupoint_poincare()
        sagitta = ref.to_eupoint().distance(ref_poincare)

        # If line is too near center, just treat is a line
        if sagitta < CIRCLE_LINE_THRESHOLD:
            ctx.move_to(*self.p1.get_coords())
            ctx.line_to(*self.p2.get_coords())
            ctx.stroke()

        # Else compute radius and center point and draw it
        else:
            semichord = self.p1.to_eupoint().distance(ref.to_eupoint())
            radius = (sagitta**2 + semichord**2) / (2 * sagitta)
            sagitta_versor = ref_klein.subtract(ref_poincare).normalize()
            center = ref_poincare.add(sagitta_versor.multiply(radius))
            ctx.save()
            ctx.new_path()
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.clip()
            ctx.arc(center.x, center.y, radius, 0.0, 2 * math.pi)
            ctx.stroke()
            ctx.restore()

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

    def point_at_coordinate(self, d):
        k = 1.0 + math.exp(2 * d)
        p1 = self.p1.to_point()
        p2 = self.p2.to_point()
        x = p2.x + (p1.x - p2.x) / k
        y = p2.y + (p1.y - p2.y) / k
        return Point(x, y)

    def ref_point(self):
        """Like point_at_coordinate(0.0), but quicker"""
        x1, y1 = self.p1.get_coords()
        x2, y2 = self.p2.get_coords()
        x = 0.5 * (x1 + x2)
        y = 0.5 * (y1 + y2)
        return Point(x, y)

    def get_point_coordinate(self, point):
        return self.ref_point().distance(point, line=self)

class PointedVector:

    def __init__(self, x, y, alpha):
        self.x = x
        self.y = y
        self.alpha = alpha

        self.metric = None
        self.base = None

    def get_metric(self):
        if self.metric is None:
            denom = 1.0 - self.x**2 - self.y**2
            g11 = (1.0 - self.y**2) / denom
            g12 = (self.x * self.y) / denom
            g22 = (1.0 - self.x**2) / denom
            self.metric = (g11, g12, g22)

        return self.metric

    def scal(self, v1, v2):
        g11, g12, g22 = self.get_metric()
        return v1[0]*v2[0]*g11 + (v1[0]*v2[1] + v1[1]*v2[0])*g12 + v1[1]*v2[1]*g22

    def normalize(self, v):
        factor = 1.0 / (math.sqrt(self.scal(v, v)))
        return (v[0]*factor, v[1]*factor)

    def get_base(self):
        """The y component of the first vector is zero."""
        if self.base is None:
            g11, g12, g22 = self.get_metric()
            v1 = self.normalize((1.0, 0.0))
            v2 = self.normalize((-g12, g11))
            # Choose v2 so that (v1, v2) is oriented
            if v2[1] < 0:
                v2 = (-v2[0], -v2[1])
            self.base = (v1, v2)

        return self.base

    def turn(self, beta):
        v1, v2 = self.get_base()
        euclidean = (math.cos(self.alpha), math.sin(self.alpha))
        # Compute the coordinates of the euclidean direction in the
        # orthonormal base (v1, v2)
        c2 = euclidean[1] / v2[1]
        c1 = (euclidean[0] - v2[0] * c2) / v1[0]
        new_angle = beta + math.atan2(c2, c1)
        new_c1 = math.cos(new_angle)
        new_c2 = math.sin(new_angle)
        # Convert back the coordinates to the euclidean global
        # reference
        new_euclidean = (v1[0]*new_c1 + v2[0]*new_c2,
                         v1[1]*new_c1 + v2[1]*new_c2)
        new_alpha = math.atan2(new_euclidean[1], new_euclidean[0])

        return PointedVector(self.x, self.y, new_alpha)

    def advance(self, dist):
        point = self.to_point()
        line = self.to_line()
        coord = line.get_point_coordinate(point)
        new_point = line.point_at_coordinate(coord + dist)
        return PointedVector(new_point.x, new_point.y, self.alpha)

    def to_point(self):
        return Point(self.x, self.y)

    def to_line(self):
        here = self.to_point()
        dist = 0.5 * (1.0 - here.to_eupoint().norm())
        there = Point(here.x + dist * math.cos(self.alpha),
                      here.y + dist * math.sin(self.alpha))
        return here.line_to(there)
