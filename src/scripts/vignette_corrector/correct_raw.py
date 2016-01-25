#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.io.imagedisplay
import pyctools.components.io.rawimagefilereader
import pyctools.components.photo.vignettecorrector
import pyctools.components.colourspace.gammacorrection
import pyctools.components.io.imagefilewriter

class Network(object):
    components = \
{   'gc': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
              'config': "{'range': 'computer', 'gamma': 'srgb'}",
              'pos': (350.0, 300.0)},
    'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': '{}',
              'pos': (650.0, 300.0)},
    'ifw': {   'class': 'pyctools.components.io.imagefilewriter.ImageFileWriter',
               'config': '{\'path\': u\'video/vignette_corr.jpg\', \'options\': \'"quality":95\'}',
               'pos': (500.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': u'video/vignette.CR2', '16bit': 'on', 'interpolation': 'ahd', 'brightness': 2.3}",
                'pos': (50.0, 300.0)},
    'vc': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrector',
              'config': "{'range': 'computer', 'r1': 0.17, 'r2': 0.12}",
              'pos': (200.0, 300.0)}}
    linkages = \
{   ('gc', 'output'): [('ifw', 'input')],
    ('ifw', 'output'): [('id', 'input')],
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
