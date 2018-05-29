#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.demo.displace
import pyctools.components.fft.fft
import pyctools.components.framerepeat
import pyctools.components.interp.imageresizer
import pyctools.components.io.dumpmetadata
import pyctools.components.io.imagefilepil
import pyctools.components.io.videofilewriter
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'd': {   'class': 'pyctools.components.demo.displace.Displace',
             'config': "{'xamp': 60.0, 'yamp': 60.0, 'zlen': 100}",
             'pos': (830.0, 100.0)},
    'dm': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
              'config': '{}',
              'pos': (1430.0, 100.0)},
    'fft': {   'class': 'pyctools.components.fft.fft.FFT',
               'config': '{}',
               'pos': (590.0, 100.0)},
    'fr': {   'class': 'pyctools.components.framerepeat.FrameRepeat',
              'config': "{'count': 100}",
              'pos': (710.0, 100.0)},
    'ifft': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'inverse': 1, 'output': 'real'}",
                'pos': (950.0, 100.0)},
    'ifr': {   'class': 'pyctools.components.io.imagefilepil.ImageFileReaderPIL',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/still.jpg'}",
               'pos': (470.0, 100.0)},
    'ird': {   'class': 'pyctools.components.interp.imageresizer.ImageResizer2D',
               'config': "{'xdown': 6, 'xaperture': 16, 'ydown': 6, "
                         "'yaperture': 16}",
               'expanded': False,
               'pos': (1070.0, 100.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': '{}',
              'pos': (1310.0, 100.0)},
    'vfw': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi'}",
               'pos': (1190.0, 100.0)}}
    linkages = \
{   ('d', 'output'): [('ifft', 'input')],
    ('fft', 'output'): [('fr', 'input')],
    ('fr', 'output'): [('d', 'input')],
    ('ifft', 'output'): [('ird', 'input')],
    ('ifr', 'output'): [('fft', 'input')],
    ('ird', 'output'): [('vfw', 'input')],
    ('qd', 'output'): [('dm', 'input')],
    ('vfw', 'output'): [('qd', 'input')]}

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
