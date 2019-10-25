#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.colourspace.rgbtoy
import pyctools.components.io.plotdata
import pyctools.components.io.rawimagefilereader
import pyctools.components.photo.vignettecorrector

class Network(object):
    components = \
{   'analyse': {   'class': 'pyctools.components.photo.vignettecorrector.AnalyseVignetteExp',
                   'config': "{'mode': 'power'}",
                   'pos': (330.0, 430.0)},
    'divide': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                  'config': "{'func': 'pt_float(128) * data1 / data2'}",
                  'pos': (190.0, 430.0)},
    'input': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                 'config': "{'path': "
                           "'/home/jim/Pictures/from_camera/2019/2019_10_22/100D_IMG_5869.CR2', "
                           "'brightness': 2.0, 'highlight_mode': 'ignore'}",
                 'pos': (-90.0, 380.0)},
    'plot': {   'class': 'pyctools.components.io.plotdata.PlotData',
                'config': '{}',
                'pos': (470.0, 430.0)},
    'reference': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                     'config': "{'path': "
                               "'/home/jim/Pictures/from_camera/2019/2019_10_22/100D_IMG_5876.CR2', "
                               "'brightness': 2.0, 'highlight_mode': 'ignore'}",
                     'pos': (-90.0, 500.0)},
    'rgby_in': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                   'config': "{'matrix': '709'}",
                   'pos': (50.0, 380.0)},
    'rgby_ref': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                    'config': "{'matrix': '709'}",
                    'pos': (50.0, 500.0)}}
    linkages = \
{   ('analyse', 'function'): [('plot', 'input')],
    ('divide', 'output'): [('analyse', 'input')],
    ('input', 'output'): [('rgby_in', 'input')],
    ('reference', 'output'): [('rgby_ref', 'input')],
    ('rgby_in', 'output'): [('divide', 'input1')],
    ('rgby_ref', 'output'): [('divide', 'input2')]}

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
