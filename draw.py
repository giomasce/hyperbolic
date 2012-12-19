#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import mpmath as math

import pygst
pygst.require("0.10")
import gst
import pygtk
import gtk
import cairo as cairolib

import pygame
import pygame.gfxdraw
from pygame.locals import *

import euclidean
import hyperbolic
import teichmuller
from utils import get_actual_dimension

def draw_frame(ctx, size, param):

    pv = hyperbolic.PointedVector(param * 0.05 - 0.2, 0.0, param * 0.0 * math.pi)
    #pv = hyperbolic.PointedVector(0.0, 0.0, 0.0)
    ctx.isom = pv.get_isometry()

    # Settings
    ctx.cairo.set_line_width(get_actual_dimension(ctx.cairo, 1.5))
    ctx.cairo.set_line_join(cairolib.LINE_JOIN_ROUND)
    ctx.cairo.set_line_cap(cairolib.LINE_CAP_ROUND)

    # Everything white
    ctx.cairo.save()
    ctx.cairo.identity_matrix()
    ctx.cairo.rectangle(0, 0, size[0], size[1])
    ctx.cairo.set_source_rgb(255, 255, 255)
    ctx.cairo.fill()
    ctx.cairo.restore()

    # for i in xrange(10):
    #     ctx.cairo.set_source_rgb(float(i) / 10, float(i) / 10, float(i) / 10)

    #     turtle = turtle.advance(1.0)
    #     turtle.to_point().draw_poincare(ctx)
    #     turtle.to_line().draw_poincare(ctx)

    #     turtle = turtle.turn(0.1 * param * 0.5 * math.pi)

    ctx.cairo.set_source_rgb(0, 0, 0)
    turtle = hyperbolic.PointedVector(0.0, 0.0, 0.0)
    teichmuller.draw_hexagon(ctx, turtle, 1.0, 0.5, 2.0, color=True)

    # Draw hyperbolic circle
    ctx.cairo.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.cairo.set_source_rgb(0, 0, 0)
    ctx.cairo.stroke()

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
    cairo_surf = cairolib.ImageSurface.create_for_data(
        pygame.surfarray.pixels2d(pygame_surf),
        cairolib.FORMAT_RGB24,
        size[0],
        size[1])

    # Inizialize cairo context
    cairo = cairolib.Context(cairo_surf)

    # Set up a reasonable coordinate system
    versor_len = 0.45 * min(size)
    reflect = cairolib.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
    cairo.transform(reflect)
    cairo.translate(size[0]/2, -size[1]/2)
    cairo.scale(versor_len, versor_len)

    ctx = hyperbolic.HyperbolicContext(cairo, hyperbolic.Isometry())

    while True:
        param = 0.001 * pygame.time.get_ticks()
        #param = 10.0

        draw_frame(ctx, size, param)

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
    cairo_surf = cairolib.ImageSurface(
        cairolib.FORMAT_RGB24,
        size[0],
        size[1])

    # Inizialize cairo context
    cairo = cairolib.Context(cairo_surf)

    # Set up a reasonable coordinate system
    versor_len = 0.45 * min(size)
    reflect = cairolib.Matrix(1.0, 0.0, 0.0, -1.0, 0.0, 0.0)
    cairo.transform(reflect)
    cairo.translate(size[0]/2, -size[1]/2)
    cairo.scale(versor_len, versor_len)

    cairo.set_line_width(1.5 / versor_len)
    cairo.set_line_join(cairolib.LINE_JOIN_ROUND)
    cairo.set_line_cap(cairolib.LINE_CAP_ROUND)

    ctx = hyperbolic.HyperbolicContext(cairo, hyperbolic.Isometry())

    for frame in xrange(frames):
        print "Writing frame %d..." % (frame),

        # Draw the frame
        param = float(frame) / fps
        draw_frame(ctx, size, param)

        # Write it to a file
        with open('frames/frame_%05d.png' % (frame), 'w') as fout:
            cairo_surf.write_to_png(fout)

        print "done!"

if __name__ == '__main__':
    pygame_animation()
    #save_frames()
    #gtk_animation()
