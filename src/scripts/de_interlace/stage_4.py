#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.deinterlace.hhiprefilter
import pyctools.components.deinterlace.intrafield
import pyctools.components.deinterlace.simple
import pyctools.components.deinterlace.weston3field
import pyctools.components.io.videofilereader
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'Weston': {   'class': 'pyctools.components.deinterlace.weston3field.Weston3Field',
                  'config': "{'mode': 1}",
                  'pos': (610.0, 270.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'title': 'intra-field', 'framerate': 20}",
                   'pos': (740.0, 150.0)},
    'display2': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                    'config': "{'title': 'Weston', 'framerate': 20}",
                    'pos': (740.0, 270.0)},
    'hhipf': {   'class': 'pyctools.components.deinterlace.hhiprefilter.HHIPreFilter',
                 'config': '{}',
                 'pos': (350.0, 200.0)},
    'interlace': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                     'config': "{'inverse': 1}",
                     'pos': (480.0, 200.0)},
    'intra-field': {   'class': 'pyctools.components.deinterlace.intrafield.IntraField',
                       'config': "{'interp': {}, 'gain': {'func': 'data * "
                                 "pt_float(2)'}, 'deint': {}, 'filgen': "
                                 "{'yaperture': 8, 'ycut': 50}}",
                       'expanded': False,
                       'pos': (610.0, 150.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'title': 'Original', 'framerate': 20}",
              'pos': (350.0, 320.0)},
    'vfr': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi', "
                         "'looping': 'repeat'}",
               'pos': (220.0, 200.0)}}
    linkages = \
{   ('Weston', 'output'): [('display2', 'input')],
    ('hhipf', 'output'): [('interlace', 'input')],
    ('interlace', 'output'): [('intra-field', 'input'), ('Weston', 'input')],
    ('intra-field', 'output'): [('display', 'input')],
    ('vfr', 'output'): [('hhipf', 'input'), ('qd', 'input')]}

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
