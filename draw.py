#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import mpmath as math

import pygst
pygst.require("0.10")
import gst
import pygtk
import gtk
import cairo

import pygame
import pygame.gfxdraw
from pygame.locals import *

import euclidean
import hyperbolic
import teichmuller
from utils import get_actual_dimension

def draw_frame(cairo_ctx, size, param):

    # Settings
    cairo_ctx.set_line_width(get_actual_dimension(cairo_ctx, 1.5))
    cairo_ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    cairo_ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    # Everything white
    cairo_ctx.save()
    cairo_ctx.identity_matrix()
    cairo_ctx.rectangle(0, 0, size[0], size[1])
    cairo_ctx.set_source_rgb(255, 255, 255)
    cairo_ctx.fill()
    cairo_ctx.restore()

    # for i in xrange(10):
    #     cairo_ctx.set_source_rgb(float(i) / 10, float(i) / 10, float(i) / 10)

    #     turtle = turtle.advance(1.0)
    #     turtle.to_point().draw_poincare(cairo_ctx)
    #     turtle.to_line().draw_poincare(cairo_ctx)

    #     turtle = turtle.turn(0.1 * param * 0.5 * math.pi)

    cairo_ctx.set_source_rgb(0, 0, 0)
    turtle = hyperbolic.PointedVector(0.0, 0.0, 0.0)
    teichmuller.draw_hexagon(cairo_ctx, turtle, 1.0, 0.5, 2.0, color=True)

    # Draw hyperbolic circle
    cairo_ctx.arc(0, 0, 1, 0, 2 * math.pi)
    cairo_ctx.set_source_rgb(0, 0, 0)
    cairo_ctx.stroke()

def draw_overlay(overlay, ctx, timestamp, duration):

    ctx.set_source_rgb(255, 0, 0)
    ctx.move_to(0, 0)
    ctx.line_to(100, 100)
    ctx.stroke()

def gtk_animation():
    pipeline = gst.Pipeline("pipeline")

    videosrc = gst.element_factory_make("videotestsrc", "videosrc")
    pipeline.add(videosrc)

    convert1 = gst.element_factory_make("ffmpegcolorspace", "convert1")
    pipeline.add(convert1)
    videosrc.link(convert1)

    overlay = gst.element_factory_make("cairooverlay", "overlay")
    pipeline.add(overlay)
    convert1.link(overlay)

    convert2 = gst.element_factory_make("ffmpegcolorspace", "convert2")
    pipeline.add(convert2)
    overlay.link(convert2)

    videosink = gst.element_factory_make("autovideosink", "videosink")
    pipeline.add(videosink)
    convert2.link(videosink)

    overlay.connect("draw", draw_overlay)

    pipeline.set_state(gst.STATE_PLAYING)

    gtk.main()

def pygame_animation():

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

    while True:
        param = 0.001 * pygame.time.get_ticks()
        #param = 10.0

        draw_frame(cairo_ctx, size, param)

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
        fpsClock.tick(30)

def save_frames():
    fps = 30
    length = 40
    frames = int(fps * length)
    size = (1920, 1080)
    cairo_surf = cairo.ImageSurface(
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

    for frame in xrange(frames):
        print "Writing frame %d..." % (frame),

        # Draw the frame
        param = float(frame) / fps
        draw_frame(cairo_ctx, size, param)

        # Write it to a file
        with open('frames/frame_%05d.png' % (frame), 'w') as fout:
            cairo_surf.write_to_png(fout)

        print "done!"

if __name__ == '__main__':
    pygame_animation()
    #save_frames()
    #gtk_animation()
