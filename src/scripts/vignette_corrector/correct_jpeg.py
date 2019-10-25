#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging

from pyctools.core.compound import Compound
import pyctools.components.colourspace.gammacorrection
import pyctools.components.colourspace.quantise
import pyctools.components.io.dumpmetadata
import pyctools.components.io.imagedisplay
import pyctools.components.io.imagefilepil
import pyctools.components.photo.vignettecorrector

class Network(object):
    components = \
{   'dm': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
              'config': '{}',
              'pos': (570.0, 180.0)},
    'efq': {   'class': 'pyctools.components.colourspace.quantise.ErrorFeedbackQuantise',
               'config': '{}',
               'pos': (440.0, 300.0)},
    'gc': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
              'config': "{'gamma': 'srgb'}",
              'pos': (310.0, 300.0)},
    'gc0': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
               'config': "{'gamma': 'srgb', 'inverse': 1}",
               'pos': (50.0, 300.0)},
    'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': '{}',
              'pos': (570.0, 420.0)},
    'ifr': {   'class': 'pyctools.components.io.imagefilepil.ImageFileReaderPIL',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/vignette.jpg'}",
               'pos': (-80.0, 300.0)},
    'ifw': {   'class': 'pyctools.components.io.imagefilepil.ImageFileWriterPIL',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/vignette_corr.jpg', "
                         '\'options\': \'"quality":95\'}',
               'pos': (570.0, 300.0)},
    'vce': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrectorExp',
               'config': "{'param_0': 0.463292, 'param_1': 1.37891}",
               'pos': (180.0, 300.0)}}
    linkages = \
{   ('efq', 'output'): [('dm', 'input'), ('ifw', 'input'), ('id', 'input')],
    ('gc', 'output'): [('efq', 'input')],
    ('gc0', 'output'): [('vce', 'input')],
    ('ifr', 'output'): [('gc0', 'input')],
    ('vce', 'output'): [('gc', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':

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

    try:
        comp.join(end_comps=True)
    except KeyboardInterrupt:
        pass

    comp.stop()
    comp.join()
