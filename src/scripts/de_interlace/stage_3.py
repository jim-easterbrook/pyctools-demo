#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.deinterlace.hhiprefilter
import pyctools.components.deinterlace.intrafield
import pyctools.components.deinterlace.simple
import pyctools.components.io.videofilereader
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'title': 'line repeat', 'framerate': 20}",
                   'pos': (620.0, 150.0)},
    'display2': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                    'config': "{'title': 'intra-field', 'framerate': 20}",
                    'pos': (620.0, 280.0)},
    'hhipf': {   'class': 'pyctools.components.deinterlace.hhiprefilter.HHIPreFilter',
                 'config': '{}',
                 'pos': (230.0, 200.0)},
    'interlace': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                     'config': "{'inverse': 1}",
                     'pos': (360.0, 200.0)},
    'intra-field': {   'class': 'pyctools.components.deinterlace.intrafield.IntraField',
                       'config': "{'interp': {}, 'gain': {'func': 'data * "
                                 "pt_float(2)'}, 'deint': {}, 'filgen': "
                                 "{'yaperture': 8, 'ycut': 50}}",
                       'expanded': False,
                       'pos': (490.0, 280.0)},
    'line-repeat': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                       'config': "{'mode': 'repeatline'}",
                       'pos': (490.0, 150.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'title': 'Original', 'framerate': 20}",
              'pos': (230.0, 320.0)},
    'vfr': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi', "
                         "'looping': 'repeat'}",
               'pos': (100.0, 200.0)}}
    linkages = \
{   ('hhipf', 'output'): [('interlace', 'input')],
    ('interlace', 'output'): [   ('line-repeat', 'input'),
                                 ('intra-field', 'input')],
    ('intra-field', 'output'): [('display2', 'input')],
    ('line-repeat', 'output'): [('display', 'input')],
    ('vfr', 'output'): [('qd', 'input'), ('hhipf', 'input')]}

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
