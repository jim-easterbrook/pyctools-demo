#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.qt.qtdisplay
import pyctools.components.interp.filtergenerator
import pyctools.components.colourspace.rgbtoy
import pyctools.components.photo.vignettecorrector
import pyctools.components.io.rawimagefilereader
import pyctools.components.arithmetic
import pyctools.components.interp.resize
import pyctools.components.framerepeat

class Network(object):
    components = \
{   'contrast': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - 50) * 64) + 128', "
                              "'outframe_pool_len': 3}",
                    'pos': (830.0, 300.0)},
    'fg': {   'class': 'pyctools.components.interp.filtergenerator.FilterGenerator',
              'config': "{'xaperture': 16, 'yaperture': 16, 'ydown': 5, "
                        "'xcut': 100, 'yup': 1, 'xdown': 5, 'ycut': 100, "
                        "'xup': 1}",
              'pos': (50.0, 420.0)},
    'fr': {   'class': 'pyctools.components.framerepeat.FrameRepeat',
              'config': "{'outframe_pool_len': 3, 'count': 1000}",
              'pos': (570.0, 300.0)},
    'lr_average': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                      'config': "{'func': '(data + "
                                "data[::,-1::-1,::])/2.0', "
                                "'outframe_pool_len': 3}",
                      'pos': (310.0, 300.0)},
    'qd': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
              'config': "{'title': '', 'outframe_pool_len': 3, 'stats': 0, "
                        "'framerate': 5, 'sync': 1, 'repeat': 1, 'shrink': "
                        "1, 'expand': 1}",
              'pos': (960.0, 300.0)},
    'r': {   'class': 'pyctools.components.interp.resize.Resize',
             'config': "{'yup': 1, 'xdown': 5, 'ydown': 5, "
                       "'outframe_pool_len': 3, 'xup': 1}",
             'pos': (180.0, 300.0)},
    'rgby': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                'config': "{'range': 'computer', 'outframe_pool_len': 3, "
                          "'matrix': 'auto'}",
                'pos': (50.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'gamma': 'linear', 'crop': 1, 'wb_camera': 1, "
                          "'path': "
                          "'/home/jim/Documents/projects/pyctools-demo/video/grey.CR2', "
                          "'wb_rgbg': '', 'use_camera_profile': 0, "
                          "'highlight_mode': 'clip', 'blue_scale': 1.0, "
                          "'noise_threshold': 0.0, 'colourspace': 'srgb', "
                          "'16bit': 1, 'interpolation': 'ahd', "
                          "'wb_greybox': '', 'wb_auto': 0, 'brightness': "
                          "2.3, 'red_scale': 1.0}",
                'pos': (-80.0, 300.0)},
    'tb_average': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                      'config': "{'func': '(data + "
                                "data[-1::-1,::,::])/2.0', "
                                "'outframe_pool_len': 3}",
                      'pos': (440.0, 300.0)},
    'vc': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrector',
              'config': "{'outframe_pool_len': 3, 'r6': 0.0, 'r2': 0.17, "
                        "'r8': 0.0, 'range': 'computer', 'r4': 0.12}",
              'pos': (700.0, 300.0)}}
    linkages = \
{   ('contrast', 'output'): [('qd', 'input')],
    ('fg', 'output'): [('r', 'filter')],
    ('fr', 'output'): [('vc', 'input')],
    ('lr_average', 'output'): [('tb_average', 'input')],
    ('r', 'output'): [('lr_average', 'input')],
    ('rgby', 'output'): [('r', 'input')],
    ('rifr', 'output'): [('rgby', 'input')],
    ('tb_average', 'output'): [('fr', 'input')],
    ('vc', 'output'): [('contrast', 'input')]}

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
