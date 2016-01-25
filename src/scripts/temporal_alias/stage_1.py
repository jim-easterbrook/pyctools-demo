#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.zone.zoneplategenerator
import pyctools.components.qt.qtdisplay
import pyctools.components.arithmetic

class Network(object):
    components = \
{   'clipper': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                   'config': "{'func': '16+((data > 180)*219)'}",
                   'pos': (200.0, 200.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'repeat': 'on', 'framerate': 60, 'sync': 'on'}",
              'pos': (350.0, 200.0)},
    'zpg': {   'class': 'pyctools.components.zone.zoneplategenerator.ZonePlateGenerator',
               'config': "{'zlen': 1000, 'looping': 'repeat', 'xlen': 600, 'kt': -0.34, 'ylen': 400, 'kx': 0.04}",
               'pos': (50.0, 200.0)}}
    linkages = \
{   ('clipper', 'output'): [('qd', 'input')],
    ('zpg', 'output'): [('clipper', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from pyctools.core.qt import Qt, QtWidgets
    QtWidgets.QApplication.setAttribute(Qt.AA_X11InitThreads)
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
