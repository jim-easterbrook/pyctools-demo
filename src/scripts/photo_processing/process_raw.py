#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import math
import os
import sys

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

from pyctools.core.compound import Compound
from pyctools.components.arithmetic import Arithmetic
from pyctools.components.colourspace.rgbtoyuv import RGBtoYUV
from pyctools.components.colourspace.yuvtorgb import YUVtoRGB
from pyctools.components.colourspace.gammacorrection import GammaCorrect
from pyctools.components.colourspace.quantise import ErrorFeedbackQuantise
from pyctools.components.io.imagefilepil import ImageFileWriterPIL
from pyctools.components.io.rawimagefilereader2 import RawImageFileReader2
from pyctools.components.photo.unsharpmask import UnsharpMask
from pyctools.components.photo.vignettecorrector import VignetteCorrector


chromatic_aberration_data = {
    'Canon_10_18':  ((10, 1.00025, 1.00060),
                     (18, 1.00010, 1.00075)),
    'Canon_18_55':  ((18, 1.00040, 1.00025),
                     (21, 1.00040, 1.00025),
                     (24, 1.00050, 1.00025),
                     (29, 1.00040, 1.00020),
                     (35, 1.00030, 1.00020),
                     (41, 1.00020, 1.00020),
                     (46, 1.00010, 1.00030),
                     (55, 0.99995, 1.00040)),
    'Samyang_500':  ((500, 1.00035, 0.99970),),
    'Sigma_70_300': (( 70, 1.00000, 1.00030),
                     ( 81, 1.00000, 1.00025),
                     (100, 1.00000, 1.00025),
                     (119, 1.00000, 1.00005),
                     (133, 1.00000, 1.00000),
                     (168, 1.00000, 0.99990),
                     (190, 1.00000, 0.99970),
                     (238, 1.00000, 0.99965),
                     (300, 1.00000, 0.99950)),
    }

def get_chromatic_aberration_params(lens, focal_length):
    data = chromatic_aberration_data[lens]
    hi = 0
    while data[hi][0] < focal_length:
        hi += 1
    lo = hi
    while data[lo][0] > focal_length:
        lo -= 1
    if lo == hi:
        return {'red_scale': data[lo][1], 'blue_scale': data[lo][2]}
    alpha = (data[hi][0] - focal_length) / (data[hi][0] - data[lo][0])
    beta = 1.0 - alpha
    return {'red_scale': (data[lo][1] * alpha) + (data[hi][1] * beta),
            'blue_scale': (data[lo][2] * alpha) + (data[hi][2] * beta)}


vignette_data = {
    'Canon_10_18': {
        '4.5':  ((10, 0.8839996388487251,   2.265047525570409),
                 (11, 0.767305206518114,    2.0505392176248605)),
        '5.0':  ((10, 0.7313883471440182,   2.9109566477075464),
                 (11, 0.767305206518114,    2.0505392176248605),
                 (12, 0.7287102126526653,   2.0688589821991887),
                 (13, 0.6811163348911445,   2.08052826786169),
                 (14, 0.6406275912442517,   2.0964795062675665),
                 (15, 0.5986783633399443,   2.099951772609432)),
        '5.6':  ((10, 0.48648428896573576,  5.428553176718565),
                 (11, 0.3689019896081984,   3.7688584868465598),
                 (12, 0.4573944538492364,   3.2221084422683846),
                 (13, 0.41556380830680345,  3.3825441451242857),
                 (14, 0.49646033817118695,  2.7537146623183753),
                 (15, 0.5986783633399443,   2.099951772609432),
                 (16, 0.5631044038621943,   2.120913507881276),
                 (17, 0.5407854337189197,   2.122352012775894),
                 (18, 0.5218333890796527,   2.139324445688214)),
        '6.3':  ((10, 0.3676002029815745,  11.558743874690617),
                 (11, 0.16046534261981804,  5.77288129414415),
                 (12, 0.20709732934540187,  5.29420712106921),
                 (13, 0.17641565395630063,  5.927269756117529),
                 (14, 0.21495120891444766,  5.367532376352033),
                 (15, 0.2331010130418333,   5.033283647202551),
                 (16, 0.3122029970686444,   3.896384748268746),
                 (17, 0.29314593281715384,  4.071016635810844),
                 (18, 0.2821632249145314,   4.13510191033811)),
        '7.1':  ((10, 0.34054622229660847, 17.300169320037742),
                 (11, 0.08515288154506302,  8.03279590375696),
                 (12, 0.10374370178812159,  7.338861262526284),
                 (13, 0.083744432698752,    9.362651162260219),
                 (14, 0.09315598433401384,  8.243037850734982),
                 (15, 0.12633566878838443,  7.426503341104818),
                 (16, 0.16333864191300687,  6.356894989770828),
                 (17, 0.14989462246039192,  6.7501978698234275),
                 (18, 0.14079759189244528,  7.181698391819725)),
        '8.0':  ((10, 0.2747687173172329,  25.94848759933366),),
        '9.0':  ((10, 0.2075118650269473,  35.926930725799494),),
        '10.0': ((10, 0.15243152849161024, 45.37833421646404),),
        },
    'Canon_18_55': {
        '3.5': ((18, 0.88624173033358,  2.11825581590007),
                (24, 0.73337754698513,  1.78434838352626)),
        '4.0': ((18, 0.718204567453966, 3.07255881829491),
                (24, 0.73337754698513,  1.78434838352626),
                (29, 0.619279915811931, 1.72838554062168),
                (35, 0.548455170483698, 1.75795853372662)),
        '4.5': ((18, 0.47460100847059,  4.21240894885769),
                (24, 0.387250219602687, 3.38176580344774),
                (29, 0.4028296620155,   2.81108754346194),
                (35, 0.548455170483698, 1.75795853372662),
                (42, 0.487615828039291, 1.75980220215528)),
        '5.0': ((18, 0.372135743575759, 5.35372089492215),
                (24, 0.262405590132763, 4.18611334314644),
                (29, 0.240222136114106, 3.85421809160327),
                (35, 0.311995694921236, 3.26436984513428),
                (42, 0.487615828039291, 1.75980220215528),
                (47, 0.444116161581636, 1.7477563536108),
                (55, 0.381097683120294, 1.77825800526327)),
        '5.6': ((18, 0.302269880974864, 9.33376988844939),
                (24, 0.147221646154257, 6.61206166005077),
                (29, 0.122602480561643, 6.45389888754673),
                (35, 0.110830396823395, 5.74777149258949),
                (42, 0.324821616913179, 2.98446343588015),
                (47, 0.381439383524004, 2.19460006239618),
                (55, 0.381097683120294, 1.77825800526327)),
        '6.3': ((18, 0.283424657281517, 18.9696385155763),
                (29, None),
                (42, 0.120249471711361, 6.57495700480806),
                (47, 0.146929717045544, 6.1352424040477),
                (55, 0.217506097573489, 3.96964885709353)),
        '7.1': ((18, 0.257135196775155, 27.5917104420898),
                (35, None),
                (55, 0.120450968175937, 9.0770024501268)),
        '8.0': ((18, 0.195815520534901, 36.3934336021627),),
        },
    'Samyang_500': {
        '6.3': ((500, 0.41, 2.1),),
        },
    'Sigma_70_300': {
        '4.0': ((70, 0.29678948434660857, 1.9096306007517116),
                (81, 0.2961031690256165, 1.8928014922495042),
                (100, 0.29083163742923246, 1.8413662138647289),
                (119, 0.2855845030037146, 1.817882886241485),
                (133, 0.2874895348175259, 1.8805273621246315)),
        '4.5': ((70, 0.18596865781923694, 3.1969097335422183),
                (81, 0.18243108421775403, 3.225763446915508),
                (100, 0.21792865311424836, 2.5365177957472707),
                (119, 0.1919337367434957, 2.8390115126728284),
                (133, 0.2874895348175259, 1.8805273621246315),
                (168, 0.3179185544482765, 2.2879262852721993)),
        '5.0': ((100, 0.09554712018756144, 5.485612510609851),
                (119, 0.0930403291911718, 5.533909937705882),
                (133, 0.17284513937876253, 3.7700266098752127),
                (168, 0.3179185544482765, 2.2879262852721993),
                (190, 0.37833132145527987, 2.510218184360429),
                (238, 0.4298013309656642, 2.134656181254472)),
        '5.6': ((133, 0.04062004890263861, 20.85149085536861),
                (168, 0.14000128999327552, 8.304494885670014),
                (190, 0.27015324501460053, 4.291718686314952),
                (238, 0.4298013309656642, 2.134656181254472),
                (300, 0.4467888388391162, 1.615305905549952)),
        '6.3': ((168, 0.051119447752981266, 16.483163682363962),
                (190, 0.08438800268174257, 9.314736863102901),
                (238, 0.21067147278524095, 4.238878943956006),
                (300, 0.31307871646825636, 2.4058828522430407)),
        '7.1': ((190, 0.04689517086625718, 13.374502135627894),
                (238, 0.10153312593834889, 6.27696272736195),
                (300, 0.13058730385462564, 4.033917136814781)),
        '8.0': ((238, 0.034752382957704775, 14.807845177505822),
                (300, 0.07146331149096524, 6.6411915776638715)),
        },
    }


def get_vignette_params(lens, aperture, focal_length):
    data = vignette_data[lens]
    if str(aperture) not in data:
        return None
    data_points = data[str(aperture)]
    hi = 0
    while data_points[hi][0] < focal_length:
        hi += 1
        if hi >= len(data_points):
            return None
    lo = hi
    while data_points[lo][0] > focal_length:
        lo -= 1
        if lo < 0:
            return None
    if data_points[lo][1] is None or data_points[hi][1] is None:
        return None
    if lo == hi:
        return {'param_0': data_points[lo][1],
                'param_1': data_points[lo][2]}
    alpha = ((data_points[hi][0] - focal_length) /
             (data_points[hi][0] - data_points[lo][0]))
    beta = 1.0 - alpha
    p0_lo = data_points[lo][1]
    p0_hi = data_points[hi][1]
    p1_lo = data_points[lo][2]
    p1_hi = data_points[hi][2]
    return {'param_0': (p0_lo * alpha) + (p0_hi * beta),
            'param_1': p1_lo * p1_hi / ((p1_hi * alpha) + (p1_lo * beta))}


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--audit', action='store_true',
                        help='show processing audit trail')
    parser.add_argument('-g', '--gamma', action='store_true',
                        help='plot gamma correction curve')
    parser.add_argument('--histogram', action='store_true',
                        help='plot histogram of output')
    parser.add_argument('-e', '--exposure', default=0, type=float, metavar='x',
                        help='adjust exposure by x stops')
    parser.add_argument('-c', '--colour', default=1.0, type=float, metavar='x',
                        help='multiply colour by x')
    parser.add_argument('-s', '--sharpen', nargs=3, type=float,
                        metavar=('a', 'r', 't'),
                        help='sharpen with amount a, radius r, threshold t')
    parser.add_argument('file', nargs='+', help='raw files to be processed')
    args = parser.parse_args()
    if args.gamma or args.histogram:
        from PyQt5 import QtCore, QtWidgets
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
        app = QtWidgets.QApplication(sys.argv)
        app.lastWindowClosed.connect(app.quit)
    if args.gamma:
        from pyctools.components.io.plotdata import PlotData
    if args.histogram:
        from pyctools.components.qt.showhistogram import ShowHistogram
    for in_file in args.file:
        if not os.path.exists(in_file):
            continue
        print(in_file)
        in_file = os.path.abspath(in_file)
        base, ext = os.path.splitext(in_file)
        if ext != '.CR2':
            print('Skip non raw')
            continue
        out_file = base + 'p.jpg'
        if os.path.exists(out_file):
            print('Skip existing', os.path.basename(out_file))
            continue
        md = GExiv2.Metadata()
        md.open_path(in_file)
        lens = md.get_tag_string('Exif.Photo.LensModel')
        aperture = md.get_fnumber()
        focal_length = md.get_focal_length()
        iso = md.get_iso_speed()
        if '10-18' in lens:
            lens = 'Canon_10_18'
        elif '18-55' in lens:
            lens = 'Canon_18_55'
        elif '70-300' in lens:
            lens = 'Sigma_70_300'
        elif '50' in lens:
            lens = 'Samyang_500'
            aperture = 6.3
            focal_length = 500
        else:
            print('Skip lens', md.lens_model)
            continue
        ca_params = get_chromatic_aberration_params(lens, focal_length)
        comps = {
            'reader': RawImageFileReader2(
                path=in_file, highlight_mode='Blend',
                demosaic_algorithm='DCB', dcb_iterations=0, dcb_enhance=False,
                noise_thr=200, fbdd_noise_reduction='Off', **ca_params),
            'rgbtoyuv': RGBtoYUV(matrix='709'),
            'sharpen': UnsharpMask(amount=0.3, radius=2.5, threshold=1.0),
            'yuvtorgb': YUVtoRGB(matrix='709'),
            'gamma': GammaCorrect(
                gamma='hybrid_log', black=1.5,
                white=100.0 / (2 ** args.exposure), scale=5),
            'quantise': ErrorFeedbackQuantise(),
            'writer': ImageFileWriterPIL(
                path=out_file, options='"quality":95', set_thumbnail=True),
            }
        if iso >= 6400:
            comps['reader'].set_config({'noise_thr': 800})
        elif iso >= 800:
            comps['reader'].set_config({'noise_thr': 400})
        if lens == 'Samyang_500':
            comps['sharpen'].set_config({'amount': 0.5})
        linkages = {
            ('reader',     'output'):    [('rgbtoyuv', 'input')],
            ('rgbtoyuv',   'output_Y'):  [('sharpen',  'input')],
            ('rgbtoyuv',   'output_UV'): [('yuvtorgb', 'input_UV')],
            ('sharpen',    'output'):    [('yuvtorgb', 'input_Y')],
            ('yuvtorgb',   'output'):    [('gamma',    'input')],
            ('gamma',      'output'):    [('quantise', 'input')],
            ('quantise',   'output'):    [('writer',   'input'),
                                          ('self',     'output')],
            }
        vignette_params = get_vignette_params(lens, aperture, focal_length)
        if vignette_params:
            comps['vignette'] = VignetteCorrector(
                mode='power', **vignette_params)
            linkages[('vignette', 'output')] = linkages[('reader', 'output')]
            linkages[('reader', 'output')] = [('vignette', 'input')]
        if args.gamma:
            comps['plot'] = PlotData()
            linkages[('gamma', 'function')] = [('plot', 'input')]
        if args.histogram:
            comps['histogram'] = ShowHistogram()
            linkages[('gamma', 'output')].append(('histogram', 'input'))
        if args.colour != 1.0:
            comps['colour'] = Arithmetic(
                func='data * pt_float({})'.format(args.colour))
            linkages[('colour', 'output')] = linkages[('rgbtoyuv', 'output_UV')]
            linkages[('rgbtoyuv', 'output_UV')] = [('colour', 'input')]
        if args.sharpen:
            a, r, t = args.sharpen
            comps['sharpen2'] = UnsharpMask(
                amount=a, radius=r, threshold=t, denoise=True)
            linkages[('sharpen2', 'output')] = linkages[('yuvtorgb', 'output')]
            linkages[('yuvtorgb', 'output')] = [('sharpen2', 'input')]
        graph = Compound(linkages=linkages, **comps)
        graph.start()
        if args.gamma or args.histogram:
            app.exec_()
        else:
            try:
                graph.join(end_comps=True)
            except KeyboardInterrupt:
                pass
            graph.stop()
        graph.join()
        if os.path.exists(out_file):
            # set modified timestamp
            md = GExiv2.Metadata()
            md.open_path(out_file)
            now = datetime.now()
            tz_offset = (now - datetime.utcnow()).total_seconds() / 60
            tz_offset = int(round(tz_offset / 15, 0) * 15)
            if tz_offset < 0:
                sign = '-'
                tz_offset = -tz_offset
            else:
                sign = '+'
            md.set_tag_string(
                'Exif.Image.DateTime', now.strftime('%Y:%m:%d %H:%M:%S'))
            md.clear_tag('Exif.Photo.SubSecTime')
            md.set_tag_string(
                'Xmp.xmp.ModifyDate', now.strftime('%Y-%m-%dT%H:%M:%S') +
                sign + '{:02d}:{:02d}'.format(tz_offset // 60, tz_offset % 60))
            md.save_file(out_file)
            if args.audit:
                print(md.get_tag_string('Xmp.pyctools.audit'))


if __name__ == '__main__':
    sys.exit(main())
