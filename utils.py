#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def get_actual_dimension(ctx, d):
    x, y = ctx.device_to_user_distance(d, 0.0)
    return math.sqrt(x**2 + y**2)
