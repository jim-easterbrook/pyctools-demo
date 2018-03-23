#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.colourspace.rgbtoy
import pyctools.components.io.rawimagefilereader
import pyctools.components.photo.vignettecorrector

class Network(object):
    components = \
{   'av': {   'class': 'pyctools.components.photo.vignettecorrector.AnalyseVignette',
              'config': "{'range': 'computer'}",
              'pos': (180.0, 300.0)},
    'rgby': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                'config': "{'range': 'computer'}",
                'pos': (50.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': "
                          "'/home/jim/Documents/projects/pyctools-demo/video/grey.CR2', "
                          "'brightness': 2.3}",
                'pos': (-80.0, 300.0)}}
    linkages = \
{   ('rgby', 'output'): [('av', 'input')],
    ('rifr', 'output'): [('rgby', 'input')]}

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
