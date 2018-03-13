#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.common
import pyctools.components.modulate
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.deinterlace.halfsize
import pyctools.components.pal.transform
import pyctools.components.fft.fft
import pyctools.components.fft.window
import pyctools.components.fft.tile
import pyctools.components.subtracter
import pyctools.components.io.videofilereader
import pyctools.components.qt.qtdisplay
import pyctools.components.arithmetic
import pyctools.components.pal.decoder

class Network(object):
    components = \
{   'deinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'topfirst': 1, 'inverse': 0, "
                                 "'outframe_pool_len': 3}",
                       'pos': (330.0, -40.0)},
    'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': "{'outframe_pool_len': 3}",
                 'pos': (1530.0, -40.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'expand': 2, 'outframe_pool_len': 3, "
                             "'shrink': 1, 'sync': 1, 'title': '', "
                             "'repeat': 1, 'framerate': 25, 'stats': 1}",
                   'pos': (2020.0, -150.0)},
    'fft': {   'class': 'pyctools.components.fft.fft.FFT',
               'config': "{'ytile': 16, 'xtile': 32, 'outframe_pool_len': "
                         "3, 'inverse': 0, 'output': 'complex'}",
               'pos': (690.0, -40.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': "
                                "'/home/jim/Documents/projects/pyctools-demo/video/coded_pal.avi', "
                                "'looping': 'repeat', 'type': 'Y', "
                                "'outframe_pool_len': 3, '16bit': 1}",
                      'pos': (80.0, -150.0)},
    'filterUV': {   'class': 'pyctools.components.pal.transform.FTFilterUV',
                    'config': "{'ytile': 16, 'mode': 'thresh', 'xtile': 32, "
                              "'outframe_pool_len': 3, 'threshold': 0.8}",
                    'pos': (810.0, -40.0)},
    'ifft': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'ytile': 16, 'xtile': 32, 'outframe_pool_len': "
                          "3, 'inverse': 1, 'output': 'real'}",
                'pos': (930.0, -40.0)},
    'inv_win_func': {   'class': 'pyctools.components.fft.window.InverseWindow',
                        'config': "{'ytile': 16, 'xoff': 16, 'xtile': 32, "
                                  "'fade': 'minsnr', 'yoff': 8}",
                        'pos': (930.0, 80.0)},
    'invwindow': {   'class': 'pyctools.components.modulate.Modulate',
                     'config': "{'outframe_pool_len': 3}",
                     'pos': (1050.0, -40.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.FromPAL',
                  'config': "{'outframe_pool_len': 3}",
                  'pos': (1410.0, -40.0)},
    'postfilter': {   'class': 'pyctools.components.pal.transform.PostFilterUV',
                      'config': "{'xdown': 1, 'xup': 1, "
                                "'outframe_pool_len': 3, 'ydown': 1, 'yup': "
                                '1}',
                      'pos': (1650.0, -40.0)},
    'reinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'topfirst': 1, 'inverse': 1, "
                                 "'outframe_pool_len': 3}",
                       'pos': (1290.0, -40.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'xdown': 461, 'xup': 351, "
                              "'outframe_pool_len': 3, 'ydown': 1, 'yup': 1}",
                    'pos': (1900.0, -150.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - 64.0) * (219.0 / 140.0)) "
                              "+ 16.0', 'outframe_pool_len': 12}",
                    'pos': (200.0, -150.0)},
    'subtract': {   'class': 'pyctools.components.subtracter.Subtracter',
                    'config': "{'outframe_pool_len': 3}",
                    'pos': (1410.0, -150.0)},
    'tile': {   'class': 'pyctools.components.fft.tile.Tile',
                'config': "{'ytile': 16, 'xoff': 16, 'xtile': 32, "
                          "'outframe_pool_len': 3, 'yoff': 8}",
                'pos': (450.0, -40.0)},
    'untile': {   'class': 'pyctools.components.fft.tile.UnTile',
                  'config': "{'outframe_pool_len': 3}",
                  'pos': (1170.0, -40.0)},
    'win_func': {   'class': 'pyctools.components.fft.window.Kaiser',
                    'config': "{'ytile': 16, 'xtile': 32, 'alpha': 0.9}",
                    'pos': (450.0, 80.0)},
    'window': {   'class': 'pyctools.components.modulate.Modulate',
                  'config': "{'outframe_pool_len': 3}",
                  'pos': (570.0, -40.0)},
    'yuvtorgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                    'config': "{'matrix': '601', 'outframe_pool_len': 3, "
                              "'range': 'studio'}",
                    'pos': (1780.0, -150.0)}}
    linkages = \
{   ('deinterlace', 'output'): [('tile', 'input')],
    ('demod', 'output'): [('postfilter', 'input')],
    ('fft', 'output'): [('filterUV', 'input')],
    ('filereader', 'output'): [('setlevel', 'input')],
    ('filterUV', 'output'): [('ifft', 'input')],
    ('ifft', 'output'): [('invwindow', 'input')],
    ('inv_win_func', 'inv_window'): [('invwindow', 'cell')],
    ('invwindow', 'output'): [('untile', 'input')],
    ('matrix', 'output'): [('demod', 'input')],
    ('postfilter', 'output'): [('yuvtorgb', 'input_UV')],
    ('reinterlace', 'output'): [('matrix', 'input'), ('subtract', 'input1')],
    ('resample', 'output'): [('display', 'input')],
    ('setlevel', 'output'): [('subtract', 'input0'), ('deinterlace', 'input')],
    ('subtract', 'output'): [('yuvtorgb', 'input_Y')],
    ('tile', 'output'): [('window', 'input')],
    ('untile', 'output'): [('reinterlace', 'input')],
    ('win_func', 'output'): [('window', 'cell'), ('inv_win_func', 'input')],
    ('window', 'output'): [('fft', 'input')],
    ('yuvtorgb', 'output'): [('resample', 'input')]}

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
