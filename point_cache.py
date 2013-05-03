#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

class TrivialPointCache:

    def __init__(self, epsilon):
        self.epsilon = epsilon
        self.points = []

    def store(self, point):
        self.points.append(point)

    def query(self, point):
        for p in self.points:
            if point.distance(p) < self.epsilon:
                return True
        return False

class GridApproximationPointCache:

    def __init__(self, epsilon):
        self.epsilon = epsilon
        self.points = {}

    def approximate(self, point):
        x = int(math.floor(point.x / self.epsilon))
        y = int(math.floor(point.y / self.epsilon))
        return (x, y)

    def store(self, point):
        self.points[self.approximate(point)] = True

    def query(self, point):
        x, y = self.approximate(point)
        for x1 in [x-1, x, x+1]:
            for y1 in [y-1, y, y+1]:
                if (x1, y1) in self.points:
                    return True
        return False

class GridApproximationSegmentCache:

    def __init__(self, epsilon):
        self.epsilon = epsilon
        self.segments = {}

    def approximate(self, p1, p2):
        return tuple(map(lambda x: int(math.floor(x / self.epsilon)), [p1.x, p1.y, p2.x, p2.y]))

    def store(self, p1, p2):
        self.segments[self.approximate(p1, p2)] = True

    def query(self, p1, p2):
        x1, y1, x2, y2 = self.approximate(p1, p2)
        for x1t in [x1, x1-1, x1+1]:
            for y1t in [y1, y1-1, y1+1]:
                for x2t in [x2, x2-1, x2+1]:
                    for y2t in [y2, y2-1, y2+1]:
                        if (x1t, y1t, x2t, y2t) in self.segments:
                            return True
                        if (x2t, y2t, x1t, y1t) in self.segments:
                            return True
        return False

    # def store(self, p1, p2):
    #     (x1, y1, x2, y2) = self.approximate(p1, p2)
    #     for x1t in [x1, x1-1, x1+1]:
    #         for y1t in [y1, y1-1, y1+1]:
    #             for x2t in [x2, x2-1, x2+1]:
    #                 for y2t in [y2, y2-1, y2+1]:
    #                     self.segments[(x1, y1, x2, y2)] = True

    # def query(self, p1, p2):
    #     return self.approximate(p1, p2) in self.segments

    def clear(self):
        self.segments = {}
