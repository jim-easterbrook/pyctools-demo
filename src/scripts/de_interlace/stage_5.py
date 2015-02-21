#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.io.videofilereader
import pyctools.components.qt.qtdisplay
import pyctools.components.deinterlace.simple
import pyctools.components.deinterlace.hhiprefilter
import pyctools.components.deinterlace.intrafield
import pyctools.components.deinterlace.weston3field

class Network(object):
    components = \
{   'Weston': {   'class': 'pyctools.components.deinterlace.weston3field.Weston3Field',
                  'config': "{'topfirst': 'on', 'mode': 1}",
                  'pos': (550.0, 300.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'repeat': 'on', 'framerate': 60, 'sync': 'on', 'title': 'intra-field'}",
                   'pos': (700.0, 150.0)},
    'display2': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                    'config': "{'repeat': 'on', 'framerate': 60, 'sync': 'on', 'title': 'Weston'}",
                    'pos': (700.0, 300.0)},
    'hhipf': {   'class': 'pyctools.components.deinterlace.hhiprefilter.HHIPreFilter',
                 'config': '{}',
                 'pos': (250.0, 200.0)},
    'interlace': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                     'config': "{'inverse': 'on', 'topfirst': 'on'}",
                     'pos': (400.0, 200.0)},
    'intra-field': {   'class': 'pyctools.components.deinterlace.intrafield.IntraField',
                       'config': '{}',
                       'pos': (550.0, 150.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'repeat': 'on', 'framerate': 60, 'sync': 'on', 'title': 'Original'}",
              'pos': (250.0, 350.0)},
    'vfr': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
               'config': "{'path': '/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi', 'looping': 'repeat'}",
               'pos': (100.0, 200.0)}}
    linkages = \
{   ('Weston', 'output'): ['display2', 'input'],
    ('hhipf', 'output'): ['interlace', 'input'],
    ('interlace', 'output'): ['intra-field', 'input', 'Weston', 'input'],
    ('intra-field', 'output'): ['display', 'input'],
    ('vfr', 'output'): ['hhipf', 'input', 'qd', 'input']}

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
