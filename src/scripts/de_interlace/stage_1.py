#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.qt.qtdisplay
import pyctools.components.deinterlace.simple
import pyctools.components.deinterlace.hhiprefilter
import pyctools.components.zone.zoneplategenerator

class Network(object):
    components = \
{   'deinterlace': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                       'config': "{'outframe_pool_len': 3, 'inverse': 0, "
                                 "'topfirst': 1, 'mode': 'repeatline'}",
                       'pos': (510.0, 170.0)},
    'deinterlace2': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                        'config': "{'outframe_pool_len': 3, 'inverse': 0, "
                                  "'topfirst': 1, 'mode': 'repeatline'}",
                        'pos': (510.0, 300.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'outframe_pool_len': 3, 'shrink': 1, 'sync': "
                             "1, 'framerate': 20, 'repeat': 1, 'title': "
                             "'Interlaced, filtered', 'expand': 1, 'stats': "
                             '0}',
                   'pos': (640.0, 170.0)},
    'display2': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                    'config': "{'outframe_pool_len': 3, 'shrink': 1, "
                              "'sync': 1, 'framerate': 20, 'repeat': 1, "
                              "'title': 'Interlaced, unfiltered', 'expand': "
                              "1, 'stats': 0}",
                    'pos': (640.0, 300.0)},
    'hhipf': {   'class': 'pyctools.components.deinterlace.hhiprefilter.HHIPreFilter',
                 'config': "{'outframe_pool_len': 3, 'xup': 1, 'xdown': 1, "
                           "'yup': 1, 'ydown': 1}",
                 'pos': (250.0, 170.0)},
    'interlace': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                     'config': "{'outframe_pool_len': 3, 'inverse': 1, "
                               "'topfirst': 1, 'mode': 'insertzero'}",
                     'pos': (380.0, 170.0)},
    'interlace2': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                      'config': "{'outframe_pool_len': 3, 'inverse': 1, "
                                "'topfirst': 1, 'mode': 'insertzero'}",
                      'pos': (380.0, 300.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'outframe_pool_len': 3, 'shrink': 1, 'sync': 1, "
                        "'framerate': 20, 'repeat': 1, 'title': 'Original', "
                        "'expand': 1, 'stats': 0}",
              'pos': (250.0, 430.0)},
    'zpg': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
               'config': "{'kyt': 0.0, 'ky2': 0.0, 'ky': 0.0, 'kt2': 0.0, "
                         "'xlen': 400, 'kx2': 0.0, 'zlen': 100, "
                         "'outframe_pool_len': 3, 'kt': 0.02, 'kx': 0.5, "
                         "'kyx': 0.0, 'kxt': 0.0, 'looping': 'repeat', "
                         "'kty': 0.0, 'kxy': 1.0, 'ylen': 400, 'k0': 0.0, "
                         "'ktx': 0.0}",
               'pos': (100.0, 300.0)}}
    linkages = \
{   ('deinterlace', 'output'): [('display', 'input')],
    ('deinterlace2', 'output'): [('display2', 'input')],
    ('hhipf', 'output'): [('interlace', 'input')],
    ('interlace', 'output'): [('deinterlace', 'input')],
    ('interlace2', 'output'): [('deinterlace2', 'input')],
    ('zpg', 'output'): [   ('hhipf', 'input'),
                           ('interlace2', 'input'),
                           ('qd', 'input')]}

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
