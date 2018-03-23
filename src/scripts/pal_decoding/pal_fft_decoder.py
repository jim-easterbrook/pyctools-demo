#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.deinterlace.halfsize
import pyctools.components.fft.fft
import pyctools.components.fft.tile
import pyctools.components.fft.window
import pyctools.components.io.videofilereader
import pyctools.components.modulate
import pyctools.components.pal.common
import pyctools.components.pal.decoder
import pyctools.components.pal.transform
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'deinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': '{}',
                       'pos': (330.0, -40.0)},
    'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': '{}',
                 'pos': (1530.0, -40.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'expand': 2, 'stats': 1}",
                   'pos': (2020.0, -150.0)},
    'fft': {   'class': 'pyctools.components.fft.fft.FFT',
               'config': "{'xtile': 32, 'ytile': 16}",
               'pos': (690.0, -40.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': "
                                "'/home/jim/Documents/projects/pyctools-demo/video/coded_pal.avi', "
                                "'looping': 'repeat', 'type': 'Y', '16bit': "
                                '1}',
                      'pos': (80.0, -150.0)},
    'filterUV': {   'class': 'pyctools.components.pal.transform.FTFilterUV',
                    'config': "{'xtile': 32, 'ytile': 16, 'mode': 'thresh', "
                              "'threshold': 0.8}",
                    'pos': (810.0, -40.0)},
    'ifft': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'xtile': 32, 'ytile': 16, 'inverse': 1, "
                          "'output': 'real'}",
                'pos': (930.0, -40.0)},
    'inv_win_func': {   'class': 'pyctools.components.fft.window.InverseWindow',
                        'config': "{'xtile': 32, 'ytile': 16, 'xoff': 16, "
                                  "'yoff': 8, 'fade': 'minsnr'}",
                        'pos': (930.0, 80.0)},
    'invwindow': {   'class': 'pyctools.components.modulate.Modulate',
                     'config': '{}',
                     'pos': (1050.0, -40.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.FromPAL',
                  'config': '{}',
                  'pos': (1410.0, -40.0)},
    'postfilter': {   'class': 'pyctools.components.pal.transform.PostFilterUV',
                      'config': '{}',
                      'pos': (1650.0, -40.0)},
    'reinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'inverse': 1}",
                       'pos': (1290.0, -40.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'xup': 351, 'xdown': 461}",
                    'pos': (1900.0, -150.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - 64.0) * (219.0 / 140.0)) "
                              "+ 16.0', 'outframe_pool_len': 12}",
                    'pos': (200.0, -150.0)},
    'subtract': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                    'config': "{'func': 'data1 - data2'}",
                    'pos': (1410.0, -150.0)},
    'tile': {   'class': 'pyctools.components.fft.tile.Tile',
                'config': "{'xtile': 32, 'ytile': 16, 'xoff': 16, 'yoff': 8}",
                'pos': (450.0, -40.0)},
    'untile': {   'class': 'pyctools.components.fft.tile.UnTile',
                  'config': '{}',
                  'pos': (1170.0, -40.0)},
    'win_func': {   'class': 'pyctools.components.fft.window.Kaiser',
                    'config': "{'xtile': 32, 'ytile': 16, 'alpha': 0.9}",
                    'pos': (450.0, 80.0)},
    'window': {   'class': 'pyctools.components.modulate.Modulate',
                  'config': '{}',
                  'pos': (570.0, -40.0)},
    'yuvtorgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                    'config': "{'matrix': '601'}",
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
    ('reinterlace', 'output'): [('subtract', 'input2'), ('matrix', 'input')],
    ('resample', 'output'): [('display', 'input')],
    ('setlevel', 'output'): [('subtract', 'input1'), ('deinterlace', 'input')],
    ('subtract', 'output'): [('yuvtorgb', 'input_Y')],
    ('tile', 'output'): [('window', 'input')],
    ('untile', 'output'): [('reinterlace', 'input')],
    ('win_func', 'output'): [('inv_win_func', 'input'), ('window', 'cell')],
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
