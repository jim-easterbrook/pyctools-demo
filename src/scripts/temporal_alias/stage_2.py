#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.qt.qtdisplay
import pyctools.components.zone.zoneplategenerator

class Network(object):
    components = \
{   'clipper': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                   'config': "{'func': '16+((data > 180)*219)'}",
                   'pos': (200.0, 200.0)},
    'clipper2': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '16+((data > 230)*219)'}",
                    'pos': (200.0, 330.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'framerate': 60}",
              'pos': (460.0, 200.0)},
    'stacker': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                   'config': "{'func': 'numpy.vstack((data1,data2))'}",
                   'pos': (330.0, 200.0)},
    'zpg': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
               'config': "{'kx': 0.04, 'kt': -0.34, 'xlen': 600, 'ylen': "
                         "400, 'zlen': 1000, 'looping': 'repeat'}",
               'pos': (70.0, 200.0)},
    'zpg2': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
                'config': "{'kx': 0.002, 'kt': -0.017, 'xlen': 600, 'ylen': "
                          "200, 'zlen': 1000, 'looping': 'repeat'}",
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
