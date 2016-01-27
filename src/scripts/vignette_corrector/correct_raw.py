#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.colourspace.quantise
import pyctools.components.io.rawimagefilereader
import pyctools.components.colourspace.gammacorrection
import pyctools.components.io.imagedisplay
import pyctools.components.photo.vignettecorrector
import pyctools.components.io.imagefilewriter

class Network(object):
    components = \
{   'efq': {   'class': 'pyctools.components.colourspace.quantise.ErrorFeedbackQuantise',
               'config': '{}',
               'pos': (500.0, 300.0)},
    'gc': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
              'config': "{'gamma': 'srgb', 'range': 'computer'}",
              'pos': (350.0, 300.0)},
    'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': '{}',
              'pos': (650.0, 450.0)},
    'ifw': {   'class': 'pyctools.components.io.imagefilewriter.ImageFileWriter',
               'config': "{'path': 'video/vignette_corr.jpg', 'options': "
                         '\'"quality":95\'}',
               'pos': (650.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'brightness': 2.3, 'path': "
                          "'video/vignette.CR2', 'interpolation': 'ahd', "
                          "'16bit': 'on'}",
                'pos': (50.0, 300.0)},
    'vc': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrector',
              'config': "{'r2': 0.12, 'range': 'computer', 'r1': 0.17}",
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
