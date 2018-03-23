#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.colourspace.rgbtoyuv
import pyctools.components.io.videofilereader
import pyctools.components.io.videofilewriter
import pyctools.components.pal.coder
import pyctools.components.pal.common
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'assemble': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                    'config': "{'func': '((data1 + data2 - pt_float(16.0)) "
                              "* pt_float(140.0 / 219.0)) + pt_float(64.0)'}",
                    'pos': (520.0, -50.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'framerate': 40}",
                   'pos': (650.0, 70.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': "
                                "'/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi'}",
                      'pos': (-260.0, -50.0)},
    'filewriter': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
                      'config': "{'path': "
                                "'/home/jim/Documents/projects/pyctools-demo/video/coded_pal.avi', "
                                "'encoder': '-c:v ffv1 -pix_fmt gray16le', "
                                "'16bit': 1}",
                      'pos': (650.0, -50.0)},
    'matrix': {   'class': 'pyctools.components.pal.coder.UVtoC',
                  'config': '{}',
                  'pos': (390.0, 30.0)},
    'modulator': {   'class': 'pyctools.components.pal.common.ModulateUV',
                     'config': '{}',
                     'pos': (260.0, 30.0)},
    'prefilter': {   'class': 'pyctools.components.pal.coder.PreFilterUV',
                     'config': '{}',
                     'pos': (130.0, 30.0)},
    'resample': {   'class': 'pyctools.components.pal.common.To4Fsc',
                    'config': "{'xup': 461, 'xdown': 351}",
                    'pos': (-130.0, -50.0)},
    'rgbyuv': {   'class': 'pyctools.components.colourspace.rgbtoyuv.RGBtoYUV',
                  'config': "{'matrix': '601', 'outframe_pool_len': 5}",
                  'pos': (0.0, -50.0)}}
    linkages = \
{   ('assemble', 'output'): [('display', 'input'), ('filewriter', 'input')],
    ('filereader', 'output'): [('resample', 'input')],
    ('matrix', 'output'): [('assemble', 'input2')],
    ('modulator', 'output'): [('matrix', 'input')],
    ('prefilter', 'output'): [('modulator', 'input')],
    ('resample', 'output'): [('rgbyuv', 'input')],
    ('rgbyuv', 'output_UV'): [('prefilter', 'input')],
    ('rgbyuv', 'output_Y'): [('assemble', 'input1')]}

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
