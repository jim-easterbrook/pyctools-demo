#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
import sys

from PyQt5 import QtCore, QtWidgets

from pyctools.core.compound import Compound
import pyctools.components.colourspace.rgbtoy
import pyctools.components.io.plotdata
import pyctools.components.io.rawimagefilereader
import pyctools.components.photo.vignettecorrector

class Network(object):
    components = \
{   'analyse': {   'class': 'pyctools.components.photo.vignettecorrector.AnalyseVignette',
                   'config': "{'mode': 'power'}",
                   'pos': (190.0, 300.0)},
    'pd': {   'class': 'pyctools.components.io.plotdata.PlotData',
              'config': '{}',
              'pos': (320.0, 300.0)},
    'rgby': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                'config': '{}',
                'pos': (50.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': "
                          "'/home/jim/Pictures/from_camera/2019/2019_10_23/100D_IMG_5909.CR2', "
                          "'brightness': 2.0, 'highlight_mode': 'ignore'}",
                'pos': (-80.0, 300.0)}}
    linkages = \
{   ('analyse', 'function'): [('pd', 'input')],
    ('rgby', 'output'): [('analyse', 'input')],
    ('rifr', 'output'): [('rgby', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication(sys.argv)

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
