#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.qt.showhistogram
import pyctools.components.io.imagedisplay
import pyctools.components.io.rawimagefilereader

class Network(object):
    components = \
{   'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': '{}',
              'pos': (50.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': u'video/grey.CR2', '16bit': 'on', 'interpolation': 'ahd', 'gamma': 'srgb', 'brightness': 2.3}",
                'pos': (-150.0, 400.0)},
    'sh': {   'class': 'pyctools.components.qt.showhistogram.ShowHistogram',
              'config': '{}',
              'pos': (50.0, 450.0)}}
    linkages = \
{   ('rifr', 'output'): [('sh', 'input'), ('id', 'input')]}

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
