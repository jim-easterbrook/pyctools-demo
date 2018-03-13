#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.io.imagefilepil
import pyctools.components.io.imagedisplay
import pyctools.components.colourspace.quantise
import pyctools.components.photo.vignettecorrector
import pyctools.components.colourspace.gammacorrection

class Network(object):
    components = \
{   'efq': {   'class': 'pyctools.components.colourspace.quantise.ErrorFeedbackQuantise',
               'config': "{'outframe_pool_len': 3}",
               'pos': (440.0, 300.0)},
    'gc': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
              'config': "{'knee_slope': 0.25, 'gamma': 'srgb', "
                        "'outframe_pool_len': 3, 'white': 255.0, 'inverse': "
                        "0, 'knee_point': 0.9, 'black': 0.0, 'range': "
                        "'computer', 'knee': 0}",
              'pos': (310.0, 300.0)},
    'gc0': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
               'config': "{'knee_slope': 0.25, 'gamma': 'srgb', "
                         "'outframe_pool_len': 3, 'white': 255.0, "
                         "'inverse': 1, 'knee_point': 0.9, 'black': 0.0, "
                         "'range': 'computer', 'knee': 0}",
               'pos': (50.0, 300.0)},
    'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': "{'outframe_pool_len': 3}",
              'pos': (570.0, 420.0)},
    'ifr': {   'class': 'pyctools.components.io.imagefilepil.ImageFileReaderPIL',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/vignette.jpg'}",
               'pos': (-80.0, 300.0)},
    'ifw': {   'class': 'pyctools.components.io.imagefilepil.ImageFileWriterPIL',
               'config': '{\'options\': \'"quality":95\', \'path\': '
                         "'/home/jim/Documents/projects/pyctools-demo/video/vignette_corr.jpg', "
                         "'format': '', 'outframe_pool_len': 3}",
               'pos': (570.0, 300.0)},
    'vc': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrector',
              'config': "{'r6': 0.0, 'r2': 0.17, 'range': 'computer', 'r8': "
                        "0.0, 'outframe_pool_len': 3, 'r4': 0.12}",
              'pos': (180.0, 300.0)}}
    linkages = \
{   ('efq', 'output'): [('ifw', 'input'), ('id', 'input')],
    ('gc', 'output'): [('efq', 'input')],
    ('gc0', 'output'): [('vc', 'input')],
    ('ifr', 'output'): [('gc0', 'input')],
    ('vc', 'output'): [('gc', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':

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

    try:
        comp.join(end_comps=True)
    except KeyboardInterrupt:
        pass

    comp.stop()
    comp.join()
