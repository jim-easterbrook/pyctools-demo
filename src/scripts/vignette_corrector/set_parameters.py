#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.colourspace.rgbtoy
import pyctools.components.photo.vignettecorrector
import pyctools.components.io.rawimagefilereader
import pyctools.components.interp.filtergenerator
import pyctools.components.qt.qtdisplay
import pyctools.components.arithmetic
import pyctools.components.interp.resize
import pyctools.components.framerepeat

class Network(object):
    components = \
{   'contrast': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - 50) * 64) + 128'}",
                    'pos': (950.0, 300.0)},
    'fg': {   'class': 'pyctools.components.interp.filtergenerator.FilterGenerator',
              'config': "{'ydown': 5, 'xaperture': 16, 'yaperture': 16, 'xdown': 5}",
              'pos': (50.0, 450.0)},
    'fr': {   'class': 'pyctools.components.framerepeat.FrameRepeat',
              'config': "{'count': 1000}",
              'pos': (650.0, 300.0)},
    'lr_average': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                      'config': "{'func': '(data + data[::,-1::-1,::])/2.0'}",
                      'pos': (350.0, 300.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'repeat': 'on', 'framerate': 5, 'sync': 'on'}",
              'pos': (1100.0, 300.0)},
    'r': {   'class': 'pyctools.components.interp.resize.Resize',
             'config': "{'ydown': 5, 'xdown': 5}",
             'pos': (200.0, 300.0)},
    'rgby': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                'config': "{'range': 'computer'}",
                'pos': (50.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': u'video/grey.CR2', '16bit': 'on', 'interpolation': 'ahd', 'brightness': 2.3}",
                'pos': (-100.0, 300.0)},
    'tb_average': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                      'config': "{'func': '(data + data[-1::-1,::,::])/2.0'}",
                      'pos': (500.0, 300.0)},
    'vc': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrector',
              'config': "{'range': 'computer', 'r1': 0.17, 'r2': 0.12}",
              'pos': (800.0, 300.0)}}
    linkages = \
{   ('contrast', 'output'): [('qd', 'input')],
    ('fg', 'output'): [('r', 'filter')],
    ('fr', 'output'): [('vc', 'input')],
    ('lr_average', 'output'): [('tb_average', 'input')],
    ('r', 'output'): [('lr_average', 'input')],
    ('rgby', 'output'): [('r', 'input')],
    ('rifr', 'output'): [('rgby', 'input')],
    ('tb_average', 'output'): [('fr', 'input')],
    ('vc', 'output'): [('contrast', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from pyctools.core.qt import Qt, QtWidgets
    QtWidgets.QApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication([])

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
