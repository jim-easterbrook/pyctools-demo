#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
import sys

from PyQt5 import QtCore, QtWidgets

from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.colourspace.rgbtoy
import pyctools.components.framerepeat
import pyctools.components.interp.filtergenerator
import pyctools.components.interp.resize
import pyctools.components.io.rawimagefilereader
import pyctools.components.photo.vignettecorrector
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'contrast': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - 15) * 16) + 128'}",
                    'pos': (830.0, 300.0)},
    'fg': {   'class': 'pyctools.components.interp.filtergenerator.FilterGenerator',
              'config': "{'xdown': 5, 'xaperture': 16, 'ydown': 5, "
                        "'yaperture': 16}",
              'pos': (50.0, 420.0)},
    'fr': {   'class': 'pyctools.components.framerepeat.FrameRepeat',
              'config': "{'count': 1000}",
              'pos': (570.0, 300.0)},
    'lr_average': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                      'config': "{'func': '(data + data[::,-1::-1,::])/2.0'}",
                      'pos': (310.0, 300.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'framerate': 5}",
              'pos': (960.0, 300.0)},
    'r': {   'class': 'pyctools.components.interp.resize.Resize',
             'config': "{'xdown': 5, 'ydown': 5}",
             'pos': (180.0, 300.0)},
    'rgby': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                'config': "{'matrix': '709'}",
                'pos': (50.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': "
                          "'/home/jim/Documents/projects/pyctools-demo/video/grey.CR2', "
                          "'brightness': 2.3, 'highlight_mode': 'ignore'}",
                'pos': (-80.0, 300.0)},
    'tb_average': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                      'config': "{'func': '(data + data[-1::-1,::,::])/2.0'}",
                      'pos': (440.0, 300.0)},
    'vce': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrectorExp',
               'config': "{'mode': 'poly2', 'param_0': 0.6, 'param_1': -0.3}",
               'pos': (700.0, 300.0)}}
    linkages = \
{   ('contrast', 'output'): [('qd', 'input')],
    ('fg', 'output'): [('r', 'filter')],
    ('fr', 'output'): [('vce', 'input')],
    ('lr_average', 'output'): [('tb_average', 'input')],
    ('r', 'output'): [('lr_average', 'input')],
    ('rgby', 'output'): [('r', 'input')],
    ('rifr', 'output'): [('rgby', 'input')],
    ('tb_average', 'output'): [('fr', 'input')],
    ('vce', 'output'): [('contrast', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication(sys.argv)

    comp = Network().make()
    cnf = comp.get_config()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
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
