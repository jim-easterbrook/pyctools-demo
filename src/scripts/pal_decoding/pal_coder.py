#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.coder
import pyctools.components.qt.qtdisplay
import pyctools.components.io.videofilewriter
import pyctools.components.arithmetic
import pyctools.components.io.videofilereader
import pyctools.components.pal.common
import pyctools.components.adder
import pyctools.components.colourspace.rgbtoyuv

class Network(object):
    components = \
{   'adder': {   'class': 'pyctools.components.adder.Adder',
                 'config': '{}',
                 'pos': (600.0, -50.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'repeat': 'on', 'framerate': 40, 'sync': 'on'}",
                   'pos': (900.0, 150.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi'}",
                      'pos': (-300.0, -50.0)},
    'filewriter': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-demo/video/coded_pal.avi', '16bit': 'on', 'encoder': '-c:v ffv1 -pix_fmt gray16le'}",
                      'pos': (900.0, -50.0)},
    'matrix': {   'class': 'pyctools.components.pal.coder.UVtoC',
                  'config': '{}',
                  'pos': (450.0, 150.0)},
    'modulator': {   'class': 'pyctools.components.pal.common.ModulateUV',
                     'config': '{}',
                     'pos': (300.0, 150.0)},
    'prefilter': {   'class': 'pyctools.components.pal.coder.PreFilterUV',
                     'config': '{}',
                     'pos': (150.0, 150.0)},
    'resample': {   'class': 'pyctools.components.pal.common.To4Fsc',
                    'config': "{'xdown': 351, 'xup': 461}",
                    'pos': (-150.0, -50.0)},
    'rgbyuv': {   'class': 'pyctools.components.colourspace.rgbtoyuv.RGBtoYUV',
                  'config': "{'outframe_pool_len': 5, 'matrix': '601'}",
                  'pos': (0.0, -50.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - pt_float(16.0)) * pt_float(140.0 / 219.0)) + pt_float(64.0)'}",
                    'pos': (750.0, -50.0)}}
    linkages = \
{   ('adder', 'output'): [('setlevel', 'input')],
    ('filereader', 'output'): [('resample', 'input')],
    ('matrix', 'output'): [('adder', 'input1')],
    ('modulator', 'output'): [('matrix', 'input')],
    ('prefilter', 'output'): [('modulator', 'input')],
    ('resample', 'output'): [('rgbyuv', 'input')],
    ('rgbyuv', 'output_UV'): [('prefilter', 'input')],
    ('rgbyuv', 'output_Y'): [('adder', 'input0')],
    ('setlevel', 'output'): [('display', 'input'), ('filewriter', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from PyQt4 import QtGui
    from PyQt4.QtCore import Qt
    QtGui.QApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QtGui.QApplication([])

    comp = Network().make()
    cnf = comp.get_config()
    parser = argparse.ArgumentParser()
    cnf.parser_add(parser)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase verbosity of log messages')
    args = parser.parse_args()
    logging.basicConfig(level=logging.ERROR - (args.verbose * 10))
    del args.verbose
    cnf.parser_set(args)
    comp.set_config(cnf)
    comp.start()
    app.exec_()

    comp.stop()
    comp.join()
