#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.decoder
import pyctools.components.pal.common
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.arithmetic
import pyctools.components.qt.qtdisplay
import pyctools.components.io.videofilereader

class Network(object):
    components = \
{   'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': '{}',
                 'pos': (500.0, 500.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'repeat': 'on', 'sync': 'on'}",
                   'pos': (1100.0, 350.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-demo/video/coded_pal.avi', '16bit': 'on', 'type': 'Y', 'looping': 'repeat'}",
                      'pos': (50.0, 350.0)},
    'filterUV': {   'class': 'pyctools.components.pal.decoder.PostFilterUV',
                    'config': '{}',
                    'pos': (650.0, 500.0)},
    'filterY': {   'class': 'pyctools.components.pal.decoder.PostFilterY',
                   'config': '{}',
                   'pos': (350.0, 350.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.FromPAL',
                  'config': '{}',
                  'pos': (350.0, 500.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'xdown': 461, 'xup': 351}",
                    'pos': (950.0, 350.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - pt_float(64)) * pt_float(219.0 / 140.0)) + pt_float(16)'}",
                    'pos': (200.0, 350.0)},
    'yuvrgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                  'config': "{'matrix': '601'}",
                  'pos': (800.0, 350.0)}}
    linkages = \
{   ('demod', 'output'): [('filterUV', 'input')],
    ('filereader', 'output'): [('setlevel', 'input')],
    ('filterUV', 'output'): [('yuvrgb', 'input_UV')],
    ('filterY', 'output'): [('yuvrgb', 'input_Y')],
    ('matrix', 'output'): [('demod', 'input')],
    ('resample', 'output'): [('display', 'input')],
    ('setlevel', 'output'): [('matrix', 'input'), ('filterY', 'input')],
    ('yuvrgb', 'output'): [('resample', 'input')]}

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
