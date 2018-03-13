#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.colourspace.rgbtoy
import pyctools.components.photo.vignettecorrector
import pyctools.components.io.rawimagefilereader

class Network(object):
    components = \
{   'av': {   'class': 'pyctools.components.photo.vignettecorrector.AnalyseVignette',
              'config': "{'outframe_pool_len': 3, 'range': 'computer', "
                        "'order': 3, 'log_eps': -4.0}",
              'pos': (180.0, 300.0)},
    'rgby': {   'class': 'pyctools.components.colourspace.rgbtoy.RGBtoY',
                'config': "{'outframe_pool_len': 3, 'range': 'computer', "
                          "'matrix': 'auto'}",
                'pos': (50.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'path': "
                          "'/home/jim/Documents/projects/pyctools-demo/video/grey.CR2', "
                          "'wb_rgbg': '', 'gamma': 'linear', 'wb_auto': 0, "
                          "'noise_threshold': 0.0, 'highlight_mode': "
                          "'clip', 'wb_greybox': '', '16bit': 1, "
                          "'blue_scale': 1.0, 'brightness': 2.3, "
                          "'wb_camera': 1, 'colourspace': 'srgb', "
                          "'use_camera_profile': 0, 'interpolation': 'ahd', "
                          "'crop': 1, 'red_scale': 1.0}",
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
