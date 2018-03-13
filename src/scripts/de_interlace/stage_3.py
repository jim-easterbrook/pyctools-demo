#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.qt.qtdisplay
import pyctools.components.deinterlace.simple
import pyctools.components.deinterlace.hhiprefilter
import pyctools.components.deinterlace.intrafield
import pyctools.components.io.videofilereader

class Network(object):
    components = \
{   'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'outframe_pool_len': 3, 'shrink': 1, 'sync': "
                             "1, 'framerate': 20, 'repeat': 1, 'title': "
                             "'line repeat', 'expand': 1, 'stats': 0}",
                   'pos': (620.0, 150.0)},
    'display2': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                    'config': "{'outframe_pool_len': 3, 'shrink': 1, "
                              "'sync': 1, 'framerate': 20, 'repeat': 1, "
                              "'title': 'intra-field', 'expand': 1, "
                              "'stats': 0}",
                    'pos': (620.0, 280.0)},
    'hhipf': {   'class': 'pyctools.components.deinterlace.hhiprefilter.HHIPreFilter',
                 'config': "{'outframe_pool_len': 3, 'xup': 1, 'xdown': 1, "
                           "'yup': 1, 'ydown': 1}",
                 'pos': (230.0, 200.0)},
    'interlace': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                     'config': "{'outframe_pool_len': 3, 'inverse': 1, "
                               "'topfirst': 1, 'mode': 'insertzero'}",
                     'pos': (360.0, 200.0)},
    'intra-field': {   'class': 'pyctools.components.deinterlace.intrafield.IntraField',
                       'config': "{'deint': {'outframe_pool_len': 3, "
                                 "'inverse': 0, 'topfirst': 1, 'mode': "
                                 "'insertzero'}, 'interp': "
                                 "{'outframe_pool_len': 3, 'xup': 1, "
                                 "'xdown': 1, 'yup': 1, 'ydown': 1}, "
                                 "'gain': {'outframe_pool_len': 3, 'func': "
                                 "'data * pt_float(2)'}, 'filgen': {'xcut': "
                                 "100, 'ycut': 50, 'yup': 1, 'xaperture': "
                                 "1, 'xup': 1, 'xdown': 1, 'ydown': 1, "
                                 "'yaperture': 8}}",
                       'expanded': False,
                       'pos': (490.0, 280.0)},
    'line-repeat': {   'class': 'pyctools.components.deinterlace.simple.SimpleDeinterlace',
                       'config': "{'outframe_pool_len': 3, 'inverse': 0, "
                                 "'topfirst': 1, 'mode': 'repeatline'}",
                       'pos': (490.0, 150.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'outframe_pool_len': 3, 'shrink': 1, 'sync': 1, "
                        "'framerate': 20, 'repeat': 1, 'title': 'Original', "
                        "'expand': 1, 'stats': 0}",
              'pos': (230.0, 320.0)},
    'vfr': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
               'config': "{'outframe_pool_len': 3, 'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/still_wobble.avi', "
                         "'looping': 'repeat', 'type': 'RGB', '16bit': 0}",
               'pos': (100.0, 200.0)}}
    linkages = \
{   ('hhipf', 'output'): [('interlace', 'input')],
    ('interlace', 'output'): [   ('intra-field', 'input'),
                                 ('line-repeat', 'input')],
    ('intra-field', 'output'): [('display2', 'input')],
    ('line-repeat', 'output'): [('display', 'input')],
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
