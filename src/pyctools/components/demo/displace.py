#!/usr/bin/env python
#  Pyctools-demo - examples of things you can do with pyctools.
#  http://github.com/jim-easterbrook/pyctools-demo
#  Copyright (C) 2015  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
#  This program is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.

"""Displacement fuction generator.

Multiplies the FT of an image by a time-varying function to make (the FT
of) an elliptically moving image.

Config:

=============  =====  ====
``xamp``       float  Horizontal peak displacement.
``yamp``       float  Vertical peak displacement.
``zlen``       int    Number of frames in a complete cycle.
=============  =====  ====

"""

from __future__ import print_function

__all__ = ['Displace']
__docformat__ = 'restructuredtext en'

import cmath
import math
import time
import sys

import numpy

from pyctools.core.config import ConfigFloat, ConfigInt
from pyctools.core.base import Transformer
from pyctools.core.frame import Frame
from pyctools.core.types import pt_complex, pt_float

class Displace(Transformer):
    def initialise(self):
        self.config['xamp'] = ConfigFloat(min_value=0)
        self.config['yamp'] = ConfigFloat(min_value=0)
        self.config['zlen'] = ConfigInt(min_value=1)

    def transform(self, in_frame, out_frame):
        self.update_config()
        xamp = self.config['xamp']
        yamp = self.config['yamp']
        zlen = self.config['zlen']
        phase = 2.0 * math.pi * float(in_frame.frame_no) / float(zlen)
        x_disp = xamp * math.cos(phase)
        y_disp = yamp * math.sin(phase)
        in_data = in_frame.as_numpy()
        out_data = numpy.empty(in_data.shape, dtype=pt_complex)
        if x_disp != 0.0:
            xlen = in_data.shape[1]
            mul = numpy.ones((xlen, 1), dtype=pt_complex)
            for x in range(1, (xlen + 1) // 2):
                phase = x_disp * 2.0 * math.pi * float(x) / float(xlen)
                mul[x] = cmath.rect(1.0, phase)
                mul[xlen - x] = mul[x].conj()
            for y in range(in_data.shape[0]):
                out_data[y] = in_data[y] * mul
        else:
            for y in range(in_data.shape[0]):
                out_data[y] = in_data[y]
        if y_disp != 0.0:
            ylen = in_data.shape[0]
            mul = numpy.ones((ylen, 1), dtype=pt_complex)
            for y in range(1, (ylen + 1) // 2):
                phase = y_disp * 2.0 * math.pi * float(y) / float(ylen)
                mul[y] = cmath.rect(1.0, phase)
                mul[ylen - y] = mul[y].conj()
            for x in range(in_data.shape[1]):
                out_data[:,x] *= mul
        audit = out_frame.metadata.get('audit')
        audit += 'data = DisplaceFT(data)\n'
        audit += '    amplitude: {} x {}\n'.format(yamp, xamp)
        audit += '    zlen: {}\n'.format(zlen)
        out_frame.metadata.set('audit', audit)
        out_frame.data = out_data
        return True
