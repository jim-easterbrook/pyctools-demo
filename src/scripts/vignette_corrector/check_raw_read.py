#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.qt.showhistogram
import pyctools.components.io.rawimagefilereader
import pyctools.components.io.imagedisplay

class Network(object):
    components = \
{   'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': "{'outframe_pool_len': 3}",
              'pos': (-20.0, 340.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': "
                          "'/home/jim/Documents/projects/pyctools-demo/video/grey.CR2', "
                          "'wb_rgbg': '', 'gamma': 'srgb', 'wb_auto': 0, "
                          "'noise_threshold': 0.0, 'highlight_mode': "
                          "'clip', 'wb_greybox': '', '16bit': 1, "
                          "'blue_scale': 1.0, 'brightness': 2.3, "
                          "'wb_camera': 1, 'colourspace': 'srgb', "
                          "'use_camera_profile': 0, 'interpolation': 'ahd', "
                          "'crop': 1, 'red_scale': 1.0}",
                'pos': (-150.0, 400.0)},
    'sh': {   'class': 'pyctools.components.qt.showhistogram.ShowHistogram',
              'config': "{'title': '', 'outframe_pool_len': 3, 'log': 0}",
              'pos': (-20.0, 460.0)}}
    linkages = \
{('rifr', 'output'): [('id', 'input'), ('sh', 'input')]}

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
