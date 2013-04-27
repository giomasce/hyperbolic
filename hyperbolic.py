#!/usr/bin/python
# -*- coding: utf-8 -*-

import mpmath as math
import mpmath

from euclidean import EuPoint, EuLine, EuCircle, crossratio
from utils import get_actual_dimension

def my_trunc(x):
    if x >= 0:
        return math.trunc(x)
    else:
        return math.trunc(x) - 1.0

POINT_RADIUS = 3.5
CIRCLE_LINE_THRESHOLD = 0.000001

class HyperbolicContext:

    def __init__(self, cairo, isom, poincare):
        self.cairo = cairo
        self.isom = isom
        self.poincare = poincare

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.poincare_coords = None
        self.metric = None

    def __repr__(self):
        return "Point(x=%f, y=%f)" % (self.x, self.y)

    def to_point(self):
        return self

    def to_eupoint(self):
        return EuPoint(self.x, self.y)

    def to_eupoint_poincare(self):
        x, y = self.get_poincare_coords()
        return EuPoint(x, y)

    @classmethod
    def from_eupoint(cls, point):
        return Point(point.x, point.y)

    def get_coords(self):
        return (self.x, self.y)

    def get_poincare_coords(self):
        if self.poincare_coords is None:
            mult = 1.0 / (1.0 + math.sqrt(1.0 - self.to_eupoint().sqnorm()))
            self.poincare_coords = (mult * self.x, mult * self.y)

        return self.poincare_coords

    @classmethod
    def from_poincare_coords(cls, x, y):
        mult = 2.0 / (1.0 + EuPoint(x, y).sqnorm())
        p = Point(mult * x, mult * y)
        p.poincare_coords = (x, y)
        return p

    def draw_klein(self, ctx):
        p = ctx.isom.map(self)
        ctx.cairo.arc(p.x, p.y, get_actual_dimension(ctx.cairo, POINT_RADIUS), 0, 2*math.pi)
        ctx.cairo.fill()
        #ctx.cairo.move_to(self.x, self.y)
        #ctx.cairo.line_to(self.x, self.y)
        #ctx.cairo.stroke()

    def draw_poincare(self, ctx):
        p = ctx.isom.map(self)
        #print p.x, p.y
        x, y = p.get_poincare_coords()
        #print x, y
        ctx.cairo.arc(x, y, get_actual_dimension(ctx.cairo, POINT_RADIUS), 0, 2*math.pi)
        ctx.cairo.fill()

    def draw(self, ctx):
        if ctx.poincare:
            self.draw_poincare(ctx)
        else:
            self.draw_klein(ctx)

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

    def segment_to(self, point):
        return Segment(self, point)

    def distance(self, point, line=None):
        if line is None:
            line = self.line_to(point)
        return 0.5 * math.log(crossratio(line.p1.to_eupoint(), line.p2.to_eupoint(),
                                         point.to_eupoint(), self.to_eupoint()))

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

    def angle(self, v1, v2):
        return math.acos(self.scal(self.normalize(v1), self.normalize(v2)))

    def normalize(self, v):
        factor = 1.0 / (math.sqrt(self.scal(v, v)))
        return (v[0]*factor, v[1]*factor)

class InfPoint:

    def __init__(self, alpha):
        self.alpha = alpha
        self.coords = None

    def __repr__(self):
        return "InfPoint(alpha=%f)" % (self.alpha)

    @classmethod
    def from_xy(self, x, y):
        return InfPoint(math.atan2(y, x))

    @classmethod
    def from_eupoint(self, point):
        return InfPoint.from_xy(point.x, point.y)

    @classmethod
    def from_point(self, point):
        return InfPoint.from_eupoint(point.to_eupoint())

    def line_to(self, inf_point):
        return Line(self, inf_point)

    def segment_to(self, inf_point):
        return Segment(self, inf_point)

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

    def to_eupoint_poincare(self):
        return self.to_eupoint()

    def draw_klein(self, ctx):
        x, y = ctx.isom.map(self.to_point()).get_coords()
        ctx.cairo.arc(x, y, get_actual_dimension(ctx.cairo, POINT_RADIUS), 0, 2*math.pi)
        ctx.cairo.fill()

    def draw(self, ctx):
        if ctx.poincare:
            self.draw_poincare(ctx)
        else:
            self.draw_klein(ctx)

    def draw_poincare(self, ctx):
        self.draw_klein(ctx)

    def line_to(self, point):
        return self.to_point().line_to(point)

class Segment:
    def __init__(self, p1, p2):
        """Two finite or infinite points (of the same type)."""
        self.p1 = p1
        self.p2 = p2

    def to_line(self):
        return p1.line_to(p2)

    def draw_klein(self, ctx):
        p1 = ctx.isom.map(self.p1)
        p2 = ctx.isom.map(self.p2)
        x1, y1 = p1.get_coords()
        x2, y2 = p2.get_coords()
        ctx.cairo.move_to(x1, y1)
        ctx.cairo.line_to(x2, y2)
        ctx.cairo.stroke()

    def draw_poincare(self, ctx):
        p1 = ctx.isom.map(self.p1)
        p2 = ctx.isom.map(self.p2)
        line = p1.line_to(p2)
        ref = line.ref_point()
        ref_klein = ref.to_eupoint()
        ref_poincare = ref.to_eupoint_poincare()
        sagitta = ref.to_eupoint().distance(ref_poincare)

        # If line is too near center, just treat is a line
        if sagitta < CIRCLE_LINE_THRESHOLD:
            ctx.cairo.move_to(*p1.to_eupoint_poincare().get_coords())
            ctx.cairo.line_to(*p2.to_eupoint_poincare().get_coords())
            ctx.cairo.stroke()

        # Else compute radius and center point and draw it
        else:
            semichord = line.p1.to_eupoint().distance(ref.to_eupoint())
            radius = (sagitta**2 + semichord**2) / (2 * sagitta)
            sagitta_versor = ref_klein.subtract(ref_poincare).normalize()
            center = ref_poincare.add(sagitta_versor.multiply(radius))
            angle1 = center.angle_to(p1.to_eupoint_poincare())
            angle2 = center.angle_to(p2.to_eupoint_poincare())
            if (angle2 - angle1) % (2*math.pi) > math.pi:
                angle1, angle2 = angle2, angle1
            ctx.cairo.arc(center.x, center.y, radius, angle1, angle2)
            ctx.cairo.stroke()

    def draw(self, ctx):
        if ctx.poincare:
            self.draw_poincare(ctx)
        else:
            self.draw_klein(ctx)

class Line:

    def __init__(self, p1, p2):
        """Two infinite points"""
        self.p1 = p1
        self.p2 = p2

    def draw(self, ctx):
        return self.to_segment().draw(ctx)

    def to_euline(self):
        x1, y1 = self.p1.get_coords()
        x2, y2 = self.p2.get_coords()
        return EuPoint(x1, y1).line_to(EuPoint(x2, y2))

    def to_segment(self):
        return self.p1.segment_to(self.p2)

    def reverse(self):
        return Line(self.p2, self.p1)

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

    def get_angle(self):
        p1 = self.p1.to_point()
        p2 = self.p2.to_point()
        return math.atan2(p2.y - p1.y, p2.x - p1.x)

    def to_pv(self, point=None):
        if point is None:
            point = self.ref_point()
        alpha = self.get_angle()
        return PointedVector(point.x, point.y, alpha)

    def angle_with(self, line, intersection=None):
        """Returns the absolute angle between the two lines."""
        if intersection is None:
            intersection = self.intersection(line)
        return self.to_pv(point=intersection).angle_with(line.to_pv(point=intersection))

class Isometry:

    def __init__(self, A=1.0, B=0.0, C=0.0, D=0.0, E=1.0, F=0.0, G=0.0, H=0.0, I=1.0):
        self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.H, self.I = \
            A, B, C, D, E, F, G, H, I

        self.inverse = None

    def to_matrix(self):
        return mpmath.matrix([[self.A, self.B, self.C],
                              [self.D, self.E, self.F],
                              [self.G, self.H, self.I]])

    @classmethod
    def from_matrix(cls, m):
        A, B, C, D, E, F, G, H, I = \
            m[(0,0)], m[(0,1)], m[(0,2)], \
            m[(1,0)], m[(1,1)], m[(1,2)], \
            m[(2,0)], m[(2,1)], m[(2,2)]
        return Isometry(A, B, C, D, E, F, G, H, I)

    def map(self, p):
        infpoint = False
        if isinstance(p, InfPoint):
            infpoint = True
        p = p.to_point()
        coeff = 1.0 / (self.G * p.x + self.H * p.y + self.I)
        new_x = coeff * (self.A * p.x + self.B * p.y + self.C)
        new_y = coeff * (self.D * p.x + self.E * p.y + self.F)
        if infpoint:
            return InfPoint.from_xy(new_x, new_y)
        else:
            return Point(new_x, new_y)

    def map_pv(self, pv):
        pass

    def get_inverse(self):
        if self.inverse is None:
            self.inverse = Isometry.from_matrix(self.to_matrix() ** -1)
            self.inverse.inverse = self

        return self.inverse

    def compose(self, a):
        m1 = self.to_matrix()
        m2 = a.to_matrix()
        return Isometry.from_matrix(m1 * m2)

    @classmethod
    def rotation(cls, x, y, alpha):
        pv1 = PointedVector(x, y, 0.0)
        pv2 = pv1.turn(alpha)
        return cls.from_pvs(pv1, pv2)

    @classmethod
    def translation(cls, x1, y1, x2, y2):
        alpha = math.atan2(y2 - y1, x2 - x1)
        pv1 = PointedVector(x1, y1, alpha)
        pv2 = PointedVector(x2, y2, alpha)
        return cls.from_pvs(pv1, pv2)

    @classmethod
    def reflection(cls, line):
        pv = line.to_pv()
        return cls.from_pvs_inverted(pv, pv)

    @classmethod
    def from_pvs(cls, pv1, pv2):
        return pv2.get_isometry().compose(pv1.get_isometry().get_inverse())

    @classmethod
    def from_pvs_inverted(cls, pv1, pv2):
        inversion = Isometry(1.0, 0.0, 0.0,
                             0.0, -1.0, 0.0,
                             0.0, 0.0, 1.0)
        return pv2.get_isometry().compose(inversion).compose(pv1.get_isometry().get_inverse())

class PointedVector:

    def __init__(self, x, y, alpha):
        self.x = x
        self.y = y
        self.alpha = alpha

        self.base = None
        self.isometry = None

    def get_metric(self):
        return self.to_point().get_metric()

    def scal(self, v1, v2):
        return self.to_point().scal(v1, v2)

    def angle(self, v1, v2):
        return self.to_point().angle(v1, v2)

    def normalize(self, v):
        return self.to_point().normalize(v)

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

    def get_isometry(self):
        """The projective matrix of the direct isometry that maps
        (0.0, 0.0, 0.0) to this PointedVector."""
        if self.isometry is None:
            # Transform the two cardinal lines of the circle
            l1 = self.to_line()
            l2 = self.turn(0.5 * math.pi).to_line()

            l1p2 = l1.p2.to_eupoint()
            l2p2 = l2.p2.to_eupoint()

            def calc_coeffs(l):
                eupoint = self.to_point().to_eupoint()
                k = l.p1.to_eupoint().distance(eupoint)
                h = l.p2.to_eupoint().distance(eupoint)
                coeff = 2.0 / (h + k)
                return k * coeff, h * coeff

            k1, h1 = calc_coeffs(l1)
            k2, h2 = calc_coeffs(l2)

            A, D, G = k1 * l1p2.x - self.x, k1 * l1p2.y - self.y, k1 - 1.0
            B, E, H = k2 * l2p2.x - self.x, k2 * l2p2.y - self.y, k2 - 1.0
            C, F, I = self.x, self.y, 1.0

            self.isometry = Isometry(A, B, C, D, E, F, G, H, I)

        return self.isometry

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

    def get_there(self):
        here = self.to_point()
        dist = 0.5 * (1.0 - here.to_eupoint().norm())
        there = Point(here.x + dist * math.cos(self.alpha),
                      here.y + dist * math.sin(self.alpha))
        return there

    def to_point(self):
        return Point(self.x, self.y)

    def to_line(self):
        here = self.to_point()
        return here.line_to(self.get_there())

    def angle_with(self, pv):
        """Get the angle between the tho PointedVectors, assuming that
        they're based in the same point. It is between 0 and pi."""
        return self.angle((math.cos(self.alpha), math.sin(self.alpha)),
                          (math.cos(pv.alpha), math.sin(pv.alpha)))
