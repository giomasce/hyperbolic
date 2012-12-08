#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import pygame
from pygame.locals import *

import euclidean

class PyGameCartRef(euclidean.CartRef):

    def draw_point(self, x, y):
        center = self.to_scr(x, y)
        corn = (center[0] - 5, center[1] - 5)
        pygame.draw.ellipse(self.surf, self.color, (corn[0], corn[1], 11, 11), 0)

def main():
    pygame.init()
    fpsClock = pygame.time.Clock()
    surf = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption('Hyperbolic!')

    white = pygame.Color(255, 255, 255)
    black = pygame.Color(0, 0, 0)
    red = pygame.Color(255, 0, 0)

    ref = PyGameCartRef((1024/2, 768/2), (100, 0), (0, 100), (1024, 768), diffs=True)
    ref.surf = surf
    ref.color = black
    euclidean.EuLine(0.5, -1.0, 1.0)

    while True:
        # Draw
        surf.fill(white)
        ref.draw_point(0, 0)

        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Finish
        pygame.display.update()
        fpsClock.tick(25)

if __name__ == '__main__':
    main()
