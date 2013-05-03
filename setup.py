#!/usr/bin/python

from distutils.core import setup, Extension

module1 = Extension('chyperbolic', sources=['chyperbolic.c'])

setup(name='Chyperbolic', version='0.1', description='', ext_modules=[module1])
