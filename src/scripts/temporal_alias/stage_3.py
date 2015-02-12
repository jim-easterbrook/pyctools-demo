#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.zone.zoneplategenerator
import pyctools.components.qt.qtdisplay

class Network(object):
    def __init__(self):
        self.components = \
{   'clipper': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                   'config': "{'func': '16+((data > 180)*219)'}",
                   'pos': (200.0, 200.0)},
    'clipper2': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '16+((data > 230)*219)'}",
                    'pos': (200.0, 350.0)},
    'clipper3': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '16+((data > 230)*219)'}",
                    'pos': (200.0, 50.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'repeat': 'on', 'framerate': 60, 'sync': 'on'}",
              'pos': (650.0, 50.0)},
    'stacker': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                   'config': "{'func': 'numpy.vstack((data1,data2))'}",
                   'pos': (350.0, 200.0)},
    'stacker2': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                    'config': "{'func': 'numpy.vstack((data1,data2))'}",
                    'pos': (500.0, 50.0)},
    'zpg': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
               'config': "{'zlen': 1000, 'looping': 'repeat', 'xlen': 600, 'kt': -0.34, 'ylen': 400, 'kx': 0.04}",
               'pos': (50.0, 200.0)},
    'zpg2': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
                'config': "{'zlen': 1000, 'looping': 'repeat', 'xlen': 600, 'kt': -0.017, 'ylen': 200, 'kx': 0.002}",
                'pos': (50.0, 350.0)},
    'zpg3': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
                'config': "{'zlen': 1000, 'looping': 'repeat', 'xlen': 600, 'kt': -0.033, 'ylen': 200, 'kx': -0.002}",
                'pos': (50.0, 50.0)}}
        self.linkages = \
{   ('clipper', 'output'): ('stacker', 'input1'),
    ('clipper2', 'output'): ('stacker', 'input2'),
    ('clipper3', 'output'): ('stacker2', 'input1'),
    ('stacker', 'output'): ('stacker2', 'input2'),
    ('stacker2', 'output'): ('qd', 'input'),
    ('zpg', 'output'): ('clipper', 'input'),
    ('zpg2', 'output'): ('clipper2', 'input'),
    ('zpg3', 'output'): ('clipper3', 'input')}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])()
            cnf = comps[name].get_config()
            for key, value in eval(component['config']).items():
                cnf[key] = value
            comps[name].set_config(cnf)
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
