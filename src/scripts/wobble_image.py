#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.io.videofilewriter
import pyctools.components.qt.qtdisplay
import pyctools.components.interp.resize
import pyctools.components.io.imagefilereader
import pyctools.components.demo.displace
import pyctools.components.fft.fft
import pyctools.components.interp.filtergenerator
import pyctools.components.io.dumpmetadata
import pyctools.components.framerepeat

class Network(object):
    components = \
{   'd': {   'class': 'pyctools.components.demo.displace.Displace',
             'config': "{'zlen': 100, 'yamp': 60.0, 'xamp': 60.0}",
             'pos': (650.0, 100.0)},
    'dm': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
              'config': '{}',
              'pos': (1550.0, 100.0)},
    'fft': {   'class': 'pyctools.components.fft.fft.FFT',
               'config': '{}',
               'pos': (350.0, 100.0)},
    'fg': {   'class': 'pyctools.components.interp.filtergenerator.FilterGenerator',
              'config': "{'xaperture': 16, 'xdown': 6}",
              'pos': (800.0, 250.0)},
    'fg0': {   'class': 'pyctools.components.interp.filtergenerator.FilterGenerator',
               'config': "{'ydown': 6, 'yaperture': 16}",
               'pos': (950.0, 250.0)},
    'fr': {   'class': 'pyctools.components.framerepeat.FrameRepeat',
              'config': "{'count': 100}",
              'pos': (500.0, 100.0)},
    'ifft': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'output': 'real', 'inverse': 'on'}",
                'pos': (800.0, 100.0)},
    'ifr': {   'class': 'pyctools.components.io.imagefilereader.ImageFileReader',
               'config': "{'path': '/home/jim/Documents/projects/pyctools-demo/video/still.jpg'}",
               'pos': (200.0, 100.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'repeat': 'on', 'sync': 'on'}",
              'pos': (1400.0, 100.0)},
    'r': {   'class': 'pyctools.components.interp.resize.Resize',
             'config': "{'xdown': 6}",
             'pos': (950.0, 100.0)},
    'r0': {   'class': 'pyctools.components.interp.resize.Resize',
              'config': "{'ydown': 6}",
              'pos': (1100.0, 100.0)},
    'vfw': {   'class': 'pyctools.components.io.videofilewriter.VideoFileWriter',
               'config': "{'path': '/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi'}",
               'pos': (1250.0, 100.0)}}
    linkages = \
{   ('d', 'output'): [('ifft', 'input')],
    ('fft', 'output'): [('fr', 'input')],
    ('fg', 'output'): [('r', 'filter')],
    ('fg0', 'output'): [('r0', 'filter')],
    ('fr', 'output'): [('d', 'input')],
    ('ifft', 'output'): [('r', 'input')],
    ('ifr', 'output'): [('fft', 'input')],
    ('qd', 'output'): [('dm', 'input')],
    ('r', 'output'): [('r0', 'input')],
    ('r0', 'output'): [('vfw', 'input')],
    ('vfw', 'output'): [('qd', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(**eval(component['config']))
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
