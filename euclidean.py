#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def det2(a, b, c, d):
    return a*d - b*c

def solve_poly2(a, b, c):
    delta = b*b - 4*a*c
    if delta < 0:
        return []
    else:
        sqrtdelta = math.sqrt(delta)
        if delta > 0:
            return [(-b-sqrtdelta)/(2*a),
                    (-b+sqrtdelta)/(2*a)]
        else:
            return [-b/(2*a)]

class EuPoint:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def sqdistance(self, point):
        return (self.x - point.x)**2 + (self.y - point.y)**2

    def distance(self, point):
        return math.sqrt(self.sqdistance(point))

    def line_to(self, point):
        deltay = point.y - self.y
        deltax = point.x - self.x
        if abs(deltax) > abs(deltay):
            m = deltay / deltax
            q = self.y - m * self.x
            return EuLine(m, -1.0, q)
        else:
            m = deltax / deltay
            q = self.x - m * self.y
            return EuLine(-1.0, m, q)

    def circle_to(self, point):
        return EuCircle(self.x, self.y, self.distance(point))

class EuLine:

    def __init__(self, a, b, c):
        """ax + by + c = 0"""
        self.a = a
        self.b = b
        self.c = c

    def intersection_line(self, line):
        denom = - det2(self.a, self.b, line.a, line.b)
        x = det2(self.c, self.b, line.c, line.b) / denom
        y = det2(self.a, self.c, line.a, line.c) / denom
        return EuPoint(x, y)

    def intersection_circle(self, circle):
        return circle.intersection_line(self)

class EuCircle:

    def __init__(self, xx, yy, r):
        """(x-xx)^2 + (y-yy)^2 = r^2"""
        self.xx = xx
        self.yy = yy
        self.r = r

    def intersection_line(self, line):
        a, b, c = line.a, line.b, line.c
        xx, yy, r = self.xx, self.yy, self.r

        inverted = False
        if abs(a) > abs(b):
            a, b = b, a
            xx, yy = yy, xx
            inverted = True

        coeff2 = 1 + a**2 / b**2
        tmp = c / b + yy
        coeff1 = -2 * (xx + tmp * a / b)
        coeff0 = xx**2 + tmp**2 - r**2
        xs = solve_poly2(coeff2, coeff1, coeff0)
        ys = map(lambda x: -(c+a*x)/b, xs)

        if inverted:
            xs, ys = ys, xs

        return map(lambda (x, y): EuPoint(x, y), zip(xs, ys))

    def polar(self, circle):
        a = -2 * x * (self.xx - circle.xx)
        b = -2 * y * (self.yy - circle.yy)
        c = self.xx**2 + self.yy**2 - self.r**2 - (circle.xx**2 + circle.yy**2 - circle.r**2)
        return EuLine(a, b, c)

    def intersection_circle(self, circle):
        return self.intersection_line(self.polar(circle))
