#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.colourspace.gammacorrection
import pyctools.components.io.imagedisplay
import pyctools.components.io.imagefilepil
import pyctools.components.photo.vignettecorrector
import pyctools.components.colourspace.quantise
import pyctools.components.io.rawimagefilereader

class Network(object):
    components = \
{   'efq': {   'class': 'pyctools.components.colourspace.quantise.ErrorFeedbackQuantise',
               'config': "{'outframe_pool_len': 3}",
               'pos': (460.0, 300.0)},
    'gc': {   'class': 'pyctools.components.colourspace.gammacorrection.GammaCorrect',
              'config': "{'knee_point': 0.9, 'knee': 0, 'black': 0.0, "
                        "'outframe_pool_len': 3, 'white': 255.0, "
                        "'knee_slope': 0.25, 'gamma': 'srgb', 'range': "
                        "'computer', 'inverse': 0}",
              'pos': (330.0, 300.0)},
    'id': {   'class': 'pyctools.components.io.imagedisplay.ImageDisplay',
              'config': "{'outframe_pool_len': 3}",
              'pos': (590.0, 420.0)},
    'ifw': {   'class': 'pyctools.components.io.imagefilepil.ImageFileWriterPIL',
               'config': "{'path': "
                         "'/home/jim/Documents/projects/pyctools-demo/video/vignette_corr.jpg', "
                         '\'options\': \'"quality":95\', \'format\': \'\', '
                         "'outframe_pool_len': 3}",
               'pos': (590.0, 300.0)},
    'rifr': {   'class': 'pyctools.components.io.rawimagefilereader.RawImageFileReader',
                'config': "{'wb_greybox': '', 'path': "
                          "'/home/jim/Documents/projects/pyctools-demo/video/vignette.CR2', "
                          "'16bit': 1, 'brightness': 2.3, 'highlight_mode': "
                          "'clip', 'gamma': 'linear', 'colourspace': "
                          "'srgb', 'noise_threshold': 0.0, "
                          "'use_camera_profile': 0, 'interpolation': 'ahd', "
                          "'blue_scale': 1.0, 'wb_auto': 0, 'red_scale': "
                          "1.0, 'wb_rgbg': '', 'wb_camera': 1, 'crop': 1}",
                'pos': (70.0, 300.0)},
    'vc': {   'class': 'pyctools.components.photo.vignettecorrector.VignetteCorrector',
              'config': "{'outframe_pool_len': 3, 'r8': 0.0, 'r2': 0.17, "
                        "'r6': 0.0, 'r4': 0.12, 'range': 'computer'}",
              'pos': (200.0, 300.0)}}
    linkages = \
{   ('efq', 'output'): [('ifw', 'input'), ('id', 'input')],
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
