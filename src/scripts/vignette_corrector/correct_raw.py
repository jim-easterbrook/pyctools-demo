#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.colourspace.gammacorrection
import pyctools.components.colourspace.quantise
import pyctools.components.io.imagedisplay
import pyctools.components.io.imagefilepil
import pyctools.components.io.rawimagefilereader
import pyctools.components.photo.vignettecorrector

class Network(object):
    components = \
{   'efq': {   'class': 'pyctools.components.colourspace.quantise.ErrorFeedbackQuantise',
               'config': '{}',
               'pos': (460.0, 300.0)},
    'gc': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
              'config': "{'range': 'computer', 'gamma': 'srgb'}",
              'pos': (330.0, 300.0)},
    'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': '{}',
              'pos': (590.0, 420.0)},
    'ifw': {   'class': 'pyctools.components.io.imagefilepil.ImageFileWriterPIL',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/vignette_corr.jpg', "
                         '\'options\': \'"quality":95\'}',
               'pos': (590.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': "
                          "'/home/jim/Documents/projects/pyctools-demo/video/vignette.CR2', "
                          "'brightness': 2.3}",
                'pos': (70.0, 300.0)},
    'vc': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrector',
              'config': "{'range': 'computer', 'r2': 0.17, 'r4': 0.12}",
              'pos': (200.0, 300.0)}}
    linkages = \
{   ('efq', 'output'): [('id', 'input'), ('ifw', 'input')],
    ('gc', 'output'): [('efq', 'input')],
    ('rifr', 'output'): [('vc', 'input')],
    ('vc', 'output'): [('gc', 'input')]}

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
