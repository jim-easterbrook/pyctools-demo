#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.zone.zoneplategenerator
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'clipper': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                   'config': "{'outframe_pool_len': 3, 'func': '16+((data > "
                             "180)*219)'}",
                   'pos': (200.0, 200.0)},
    'clipper2': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'outframe_pool_len': 3, 'func': '16+((data "
                              "> 230)*219)'}",
                    'pos': (200.0, 330.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'repeat': 1, 'sync': 1, 'stats': 0, 'expand': 1, "
                        "'outframe_pool_len': 3, 'framerate': 60, 'shrink': "
                        "1, 'title': ''}",
              'pos': (460.0, 200.0)},
    'stacker': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                   'config': "{'outframe_pool_len': 3, 'func': "
                             "'numpy.vstack((data1,data2))'}",
                   'pos': (330.0, 200.0)},
    'zpg': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
               'config': "{'looping': 'repeat', 'kx2': 0.0, 'zlen': 1000, "
                         "'kt2': 0.0, 'ky2': 0.0, 'outframe_pool_len': 3, "
                         "'ylen': 400, 'kyt': 0.0, 'ktx': 0.0, 'kxt': 0.0, "
                         "'kxy': 0.0, 'kx': 0.04, 'kyx': 0.0, 'k0': 0.0, "
                         "'ky': 0.0, 'kty': 0.0, 'kt': -0.34, 'xlen': 600}",
               'pos': (70.0, 200.0)},
    'zpg2': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
                'config': "{'looping': 'repeat', 'kx2': 0.0, 'zlen': 1000, "
                          "'kt2': 0.0, 'ky2': 0.0, 'outframe_pool_len': 3, "
                          "'ylen': 200, 'kyt': 0.0, 'ktx': 0.0, 'kxt': 0.0, "
                          "'kxy': 0.0, 'kx': 0.002, 'kyx': 0.0, 'k0': 0.0, "
                          "'ky': 0.0, 'kty': 0.0, 'kt': -0.017, 'xlen': 600}",
                'pos': (70.0, 330.0)}}
    linkages = \
{   ('clipper', 'output'): [('stacker', 'input1')],
    ('clipper2', 'output'): [('stacker', 'input2')],
    ('stacker', 'output'): [('qd', 'input')],
    ('zpg', 'output'): [('clipper', 'input')],
    ('zpg2', 'output'): [('clipper2', 'input')]}

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
