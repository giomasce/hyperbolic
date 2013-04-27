#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import mpmath as math

#import pygst
#pygst.require("0.10")
#import gst
#import pygtk
#import gtk
import cairo as cairolib

import pygame
import pygame.gfxdraw
from pygame.locals import *

import euclidean
import hyperbolic
import teichmuller
import polygons
from utils import get_actual_dimension

def draw_frame(ctx, size, param):

    #pv = hyperbolic.PointedVector(param * 0.05 - 0.7, param * 0.04 - 0.7, param * 0.1 * math.pi)
    #pv = hyperbolic.PointedVector(0.0, 0.0, 0.0)
    #ctx.isom = pv.get_isometry()

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
    #     turtle.to_point().draw(ctx)
    #     turtle.to_line().draw(ctx)

    #     turtle = turtle.turn(0.1 * param * 0.5 * math.pi)

    ctx.cairo.set_source_rgb(0, 0, 0)
    turtle = hyperbolic.PointedVector(0.0, 0.0, 0.0)
    #teichmuller.draw_hexagon(ctx, turtle, 0.5, 0.25, 0.5, color=True)
    #teichmuller.draw_hexagon(ctx, turtle,
    #                         teichmuller.EQUILATERAL_HEXAGON,
    #                         teichmuller.EQUILATERAL_HEXAGON,
    #                         teichmuller.EQUILATERAL_HEXAGON,
    #                         color=True)
    #polygons.draw_polygon(ctx, polygons.build_polygon_with_center(5, 2.0, turtle))
    polygons.draw_polygon(ctx, polygons.build_polygon_with_angle(7, 2.0 * math.pi / 3, turtle))

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

def init_cairo(size):

    #pygame_surf = pygame.display.set_mode(size, pygame.FULLSCREEN, 32)
    #size = pygame_surf.get_size()
    pygame_surf = pygame.display.set_mode(size, pygame.RESIZABLE, 32)
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

    return cairo

def get_mouse_coords(ctx, event):
    user_coords = ctx.cairo.device_to_user(*event.pos)
    if user_coords[0]**2 + user_coords[1]**2 < 1.0:
        if ctx.poincare:
            return hyperbolic.Point.from_poincare_coords(*user_coords).get_coords()
        else:
            return user_coords
    else:
        return (None, None)

def pygame_animation():

    #math.mp.prec = 500

    # Initialize PyGame
    pygame.init()
    fpsClock = pygame.time.Clock()
    pygame.display.set_caption('Hyperbolic!')

    size = (640, 480)
    cairo = init_cairo(size)
    ctx = hyperbolic.HyperbolicContext(cairo, hyperbolic.Isometry(), poincare=True)

    # Movement tracking
    base_point = None
    base_isom = None

    while True:
        param = 0.001 * pygame.time.get_ticks()
        #param = 10.0

        draw_frame(ctx, size, param)

        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

                if event.key == K_m:
                    ctx.poincare = not ctx.poincare

            elif event.type == VIDEORESIZE:
                size = event.size
                cairo = init_cairo(size)
                ctx.cairo = cairo

            elif event.type == MOUSEBUTTONDOWN:
                x, y = get_mouse_coords(ctx, event)
                if x is not None:

                    # First button
                    if event.button == 1:
                        base_point = (x, y)
                        base_isom = ctx.isom

            elif event.type == MOUSEMOTION:
                x, y = get_mouse_coords(ctx, event)
                if x is not None:

                    if base_point is not None:
                        trans = hyperbolic.Isometry.translation(base_point[0], base_point[1], x, y)
                        ctx.isom = trans.compose(base_isom)

            elif event.type == MOUSEBUTTONUP:
                x, y = get_mouse_coords(ctx, event)
                if x is not None:
                    rot = None

                    # First button
                    if event.button == 1:
                        base_point = None
                        base_isom = None

                    # Scroll up
                    if event.button == 4:
                        rot = hyperbolic.Isometry.rotation(x, y, 0.1)

                    # Scroll down
                    elif event.button == 5:
                        rot = hyperbolic.Isometry.rotation(x, y, -0.1)

                    if rot is not None:
                        ctx.isom = rot.compose(ctx.isom)

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

    ctx = hyperbolic.HyperbolicContext(cairo, hyperbolic.Isometry(), poincare=True)

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
