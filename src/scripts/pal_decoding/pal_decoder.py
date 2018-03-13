#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.decoder
import pyctools.components.qt.qtdisplay
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.arithmetic
import pyctools.components.pal.common
import pyctools.components.io.videofilereader

class Network(object):
    components = \
{   'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': "{'outframe_pool_len': 3}",
                 'pos': (480.0, 470.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'outframe_pool_len': 3, 'shrink': 1, 'sync': "
                             "1, 'title': '', 'repeat': 1, 'expand': 1, "
                             "'stats': 0, 'framerate': 25}",
                   'pos': (1000.0, 350.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'16bit': 1, 'outframe_pool_len': 3, "
                                "'path': "
                                "'/home/jim/Documents/projects/pyctools-demo/video/coded_pal.avi', "
                                "'type': 'Y', 'looping': 'repeat'}",
                      'pos': (90.0, 350.0)},
    'filterUV': {   'class': 'pyctools.components.pal.decoder.PostFilterUV',
                    'config': "{'xdown': 1, 'outframe_pool_len': 3, "
                              "'ydown': 1, 'xup': 1, 'yup': 1}",
                    'pos': (610.0, 470.0)},
    'filterY': {   'class': 'pyctools.components.pal.decoder.PostFilterY',
                   'config': "{'xdown': 1, 'outframe_pool_len': 3, 'ydown': "
                             "1, 'xup': 1, 'yup': 1}",
                   'pos': (350.0, 350.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.FromPAL',
                  'config': "{'outframe_pool_len': 3}",
                  'pos': (350.0, 470.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'xdown': 461, 'outframe_pool_len': 3, "
                              "'ydown': 1, 'xup': 351, 'yup': 1}",
                    'pos': (870.0, 350.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'outframe_pool_len': 3, 'func': '((data - "
                              'pt_float(64)) * pt_float(219.0 / 140.0)) + '
                              "pt_float(16)'}",
                    'pos': (220.0, 350.0)},
    'yuvrgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                  'config': "{'outframe_pool_len': 3, 'matrix': '601', "
                            "'range': 'studio'}",
                  'pos': (740.0, 350.0)}}
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
    from PyQt5 import QtCore, QtWidgets
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
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
