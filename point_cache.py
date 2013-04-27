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
