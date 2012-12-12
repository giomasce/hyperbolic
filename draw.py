#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import mpmath as math

import cairo

import pygame
import pygame.gfxdraw
from pygame.locals import *

import euclidean
import hyperbolic

def main():

    #math.mp.prec = 500

    # Initialize PyGame
    pygame.init()
    fpsClock = pygame.time.Clock()
    pygame.display.set_caption('Hyperbolic!')

    # Initialize a shared buffer between PyGame and cairo
    size = (0, 0)
    pygame_surf = pygame.display.set_mode(size, pygame.FULLSCREEN, 32)
    size = pygame_surf.get_size()
    cairo_surf = cairo.ImageSurface.create_for_data(
        pygame.surfarray.pixels2d(pygame_surf),
        cairo.FORMAT_RGB24,
        size[0],
        size[1])

    # Inizialize cairo context
    cairo_ctx = cairo.Context(cairo_surf)

    # Set up a reasonable coordinate system
    versor_len = 0.45 * min(size)
    reflect = cairo.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
    cairo_ctx.transform(reflect)
    cairo_ctx.translate(size[0]/2, -size[1]/2)
    cairo_ctx.scale(versor_len, versor_len)

    cairo_ctx.set_line_width(1.5 / versor_len)
    cairo_ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    cairo_ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    while True:
        # Draw
        cairo_ctx.save()
        cairo_ctx.identity_matrix()
        cairo_ctx.rectangle(0, 0, size[0], size[1])
        cairo_ctx.set_source_rgb(255, 255, 255)
        cairo_ctx.fill()
        cairo_ctx.restore()

        # cairo_ctx.save()
        # cairo_ctx.rotate(0.0 * float(pygame.time.get_ticks()) / 1000)

        cairo_ctx.save()
        cairo_ctx.arc(0, 0, 1, 0, 2 * math.pi)
        cairo_ctx.set_line_width(1.5 / versor_len)
        cairo_ctx.set_source_rgb(0, 0, 0)
        cairo_ctx.stroke()
        cairo_ctx.restore()

        # cairo_ctx.set_source_rgb(255, 0, 0)
        # cairo_ctx.move_to(0, 0)
        # cairo_ctx.line_to(1, 0)
        # cairo_ctx.stroke()

        # cairo_ctx.set_source_rgb(0, 255, 0)
        # cairo_ctx.move_to(0, 0)
        # cairo_ctx.line_to(0, 1)
        # cairo_ctx.stroke()

        # p = hyperbolic.Point(0.5, 0.4)
        # cairo_ctx.set_source_rgb(0, 0, 0)
        # p.draw_klein(cairo_ctx)
        # q = hyperbolic.InfPoint(0.0 * math.pi * float(pygame.time.get_ticks()) / 1000)
        # q.draw_klein(cairo_ctx)

        # l = p.line_to(q)
        # l.draw_klein(cairo_ctx)

        # r = hyperbolic.Line(hyperbolic.InfPoint(1.0), hyperbolic.InfPoint(2.0))
        # r.draw_klein(cairo_ctx)

        # a = r.intersection(l)
        # if a is not None:
        #     a.draw_klein(cairo_ctx)

        # l = hyperbolic.Point(0.0, -0.4).line_to(hyperbolic.Point(-0.7, 0.1))
        # p = l.point_at_coordinate(-5.0 + float(pygame.time.get_ticks()) / 1000)
        # #print l.get_point_coordinate(p)
        # l.draw_klein(cairo_ctx)
        # p.draw_klein(cairo_ctx)

        # cairo_ctx.restore()

        cairo_ctx.set_source_rgb(0, 0, 0)
        turtle = hyperbolic.PointedVector(0.0, 0.0, 0.0)
        turtle.to_point().draw_klein(cairo_ctx)
        turtle.to_line().draw_klein(cairo_ctx)

        for i in xrange(10):

            cairo_ctx.set_source_rgb(float(i) / 10, float(i) / 10, float(i) / 10)

            turtle = turtle.advance(1.0)
            turtle.to_point().draw_klein(cairo_ctx)
            turtle.to_line().draw_klein(cairo_ctx)

            turtle = turtle.turn(0.1 * float(pygame.time.get_ticks()) / 1000 * 0.5 * math.pi)
            turtle.to_point().draw_klein(cairo_ctx)
            turtle.to_line().draw_klein(cairo_ctx)

        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

        # Finish
        pygame.display.flip()
        fpsClock.tick(24)

if __name__ == '__main__':
    main()
