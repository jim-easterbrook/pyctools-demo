#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import os
import sys

import exiv2

from pyctools.core.compound import Compound
from pyctools.components.arithmetic import Arithmetic
from pyctools.components.colourspace.rgbtoyuv import RGBtoYUV
from pyctools.components.colourspace.yuvtorgb import YUVtoRGB
from pyctools.components.colourspace.gammacorrection import GammaCorrect
from pyctools.components.colourspace.quantise import ErrorFeedbackQuantise
from pyctools.components.io.imagefilepil import ImageFileWriterPIL
from pyctools.components.io.rawimagefilereader2 import RawImageFileReader2
from pyctools.components.photo.reorient import Reorient
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
    'Sigma_18_200': (( 18, 1.00065, 1.00045),
                     ( 21, 1.00045, 1.00045),
                     ( 28, 1.00035, 1.00045),
                     ( 33, 1.00025, 1.00045),
                     ( 39, 1.00020, 1.00045),
                     ( 46, 1.00015, 1.00040),
                     ( 54, 1.00010, 1.00035),
                     ( 63, 1.00008, 1.00030),
                     ( 75, 1.00005, 1.00020),
                     ( 89, 0.99995, 1.00020),
                     (106, 0.99990, 1.00020),
                     (125, 0.99985, 1.00020),
                     (147, 0.99980, 1.00020),
                     (170, 0.99970, 1.00015),
                     (200, 0.99970, 1.00010)),
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
    'Sigma_18_200': {
        '3.5':  ((18,  0.191603, 0.845672, 1.017831, 1.171789, 1.457623),
                 (200, 0.191603, 0.845672, 1.017831, 1.171789, 1.457623)
                 ),
        '4.0':  ((18,  0.443971, 0.876140, 1.001543, 1.083026, 1.257010),
                 (21,  0.144785, 0.951488, 1.008929, 1.182630, 1.363204),
                 (28,  0.143489, 0.930867, 1.010137, 1.168593, 1.492611),
                 (200, 0.143489, 0.930867, 1.010137, 1.168593, 1.492611),
                 ),
        '4.5':  ((18,  0.789118, 0.933520, 1.003268, 1.015749, 1.070867),
                 (21,  0.631484, 0.969139, 0.999105, 1.043597, 1.129712),
                 (28,  0.400068, 0.942782, 1.000226, 1.092102, 1.348511),
                 (33,  0.130422, 0.912872, 1.008586, 1.152600, 1.491283),
                 (39,  0.128040, 0.906847, 1.008555, 1.141092, 1.493164),
                 (200, 0.128040, 0.906847, 1.008555, 1.141092, 1.493164),
                 ),
        '5.0':  ((21,  0.565203, 0.917650, 0.998812, 1.001913, 1.034889),
                 (28,  0.665542, 0.948856, 1.000224, 1.035675, 1.203327),
                 (33,  0.501765, 0.917822, 1.000765, 1.059703, 1.279012),
                 (39,  0.468142, 0.921721, 1.000390, 1.064255, 1.330766),
                 (54,  0.146395, 0.890679, 1.012981, 1.132420, 1.490866),
                 (200, 0.146395, 0.890679, 1.012981, 1.132420, 1.490866),
                 ),
        '5.6':  ((28,  0.702983, 0.953627, 1.000360, 0.999064, 1.094250),
                 (33,  0.710998, 0.949483, 1.000276, 1.003730, 1.137054),
                 (39,  0.526643, 0.932154, 0.999183, 1.002507, 1.149823),
                 (54,  0.481320, 0.896403, 1.001508, 1.051237, 1.301956),
                 (63,  0.164298, 0.870664, 1.014279, 1.120954, 1.501688),
                 (75,  0.186024, 0.828426, 1.016072, 1.106186, 1.546209),
                 (89,  0.168677, 0.793698, 1.013101, 1.097132, 1.560497),
                 (106, 0.165923, 0.752453, 1.011879, 1.088029, 1.608575),
                 (200, 0.165923, 0.752453, 1.011879, 1.088029, 1.608575),
                 ),
        '6.3':  ((28,              0.969905,           1.000244, 1.054224),
                 (33,              0.954609,           1.000201, 1.070933),
                 (39,              0.949951,           1.000318, 1.094866),
                 (54,              0.929109,           1.001772, 1.154334),
                 (63,              0.907095,           1.002624, 1.201798),
                 (74.9,            0.834156,           1.013815, 1.314239),
                 (75,    0.603583, 0.852843, 1.001311, 1.024207, 1.325848),
                 (89,    0.566313, 0.827677, 1.001341, 1.030145, 1.373551),
                 (106,   0.583750, 0.790051, 1.001215, 1.023179, 1.404825),
                 (106.1,           0.771598,           1.011404, 1.398856),
                 (125,             0.685060,           1.079280, 1.669043),
                 (147,             0.640434,           1.073432, 1.699695),
                 (170,             0.579095,           1.065622, 1.729200),
                 (200,             0.485247,           1.052013, 1.761800),
                 ),
        '7.1':  ((33,  0.967743, 1.000268, 1.064282),
                 (39,  0.965409, 1.001255, 1.072426),
                 (54,  0.942104, 1.001598, 1.132279),
                 (63,  0.925490, 1.002437, 1.153277),
                 (75,  0.887689, 1.001633, 1.205474),
                 (89,  0.861494, 1.003008, 1.252228),
                 (106, 0.824758, 1.002067, 1.280511),
                 (125, 0.729560, 1.003595, 1.412241),
                 (147, 0.692354, 1.002285, 1.430388),
                 (170, 0.647526, 1.002900, 1.452442),
                 (200, 0.582503, 1.004591, 1.475844),
                 ),
        '8.0':  ((54,  0.963181, 0.999742, 1.073697),
                 (63,  0.946707, 1.001932, 1.089412),
                 (75,  0.921257, 1.001869, 1.143048),
                 (89,  0.887852, 1.001727, 1.185566),
                 (106, 0.853453, 1.000834, 1.212885),
                 (125, 0.807640, 1.001396, 1.265480),
                 (147, 0.781950, 1.001770, 1.282772),
                 (170, 0.744447, 1.001926, 1.295934),
                 (200, 0.690925, 1.001013, 1.305138),
                 ),
        '9.0':  ((75,  0.941405, 1.001198, 1.095137),
                 (89,  0.914626, 1.000970, 1.106548),
                 (106, 0.904861, 1.001182, 1.139048),
                 (125, 0.865721, 1.001100, 1.182148),
                 (147, 0.844578, 1.001216, 1.196191),
                 (170, 0.814092, 1.000830, 1.204672),
                 (200, 0.782583, 1.001330, 1.214902),
                 ),
        '10.0': ((75,  0.949186, 1.000735, 1.050847),
                 (89,  0.931576, 1.000657, 1.073926),
                 (106, 0.925395, 1.001075, 1.099613),
                 (125, 0.875100, 1.000138, 1.146153),
                 (147, 0.864363, 1.001026, 1.165457),
                 (170, 0.843018, 1.001218, 1.175854),
                 (200, 0.808864, 1.000189, 1.179866),
                 ),
        '11.0': ((106, 0.946136, 1.000759, 1.057715),
                 (125, 0.914910, 0.999754, 1.076507),
                 (147, 0.909922, 1.000104, 1.092782),
                 (170, 0.901233, 1.001085, 1.101896),
                 (200, 0.875118, 1.000025, 1.100532),
                 ),
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
    lo = list(data_points[lo])
    hi = list(data_points[hi])
    if lo[1] is None or hi[1] is None:
        return None
    if lens != 'Sigma_18_200':
        result = {'mode': 'power'}
    elif len(lo) >= 6:
        result = {'mode': 'invlin3'}
    else:
        result = {'mode': 'invlin2'}
    if lo == hi:
        interp = lo
    else:
        alpha = (hi[0] - focal_length) / (hi[0] - lo[0])
        beta = 1.0 - alpha
        if result['mode'] == 'power':
            # interpolate inverse of 2nd param
            lo[2] = 1.0 / lo[2]
            hi[2] = 1.0 / hi[2]
        interp = []
        for a, b in zip(lo, hi):
            interp.append((a * alpha) + (b * beta))
        if result['mode'] == 'power':
            interp[2] = 1.0 / interp[2]
    for n, param in enumerate(interp[1:]):
        result['param_{}'.format(n)] = param
    return result


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--audit', action='store_true',
                        help='show processing audit trail')
    parser.add_argument('-g', '--gamma', action='store_true',
                        help='plot gamma correction curve')
    parser.add_argument('--histogram', action='store_true',
                        help='plot histogram of output')
    parser.add_argument('-l', '--linear', action='store_true',
                        help='save "linear light" (not gamma corrected) image')
    parser.add_argument('--astro', action='store_true',
                        help='set defaults for astrophotography')
    parser.add_argument('-e', '--exposure', default=0, type=float, metavar='x',
                        help='adjust exposure by x stops')
    parser.add_argument('-o', '--offset', default=1.7, type=float, metavar='x',
                        help='offset black level by x')
    parser.add_argument('-c', '--colour', default=1.07, type=float, metavar='x',
                        help='multiply colour by x')
    parser.add_argument('-f', '--filter_colour', default=0, type=float, metavar='x',
                        help='set colour smoothing radius to x')
    parser.add_argument('-n', '--noise', default=0, type=float, metavar='x',
                        help='set wavelet denoising threshold to x')
    parser.add_argument('-r', '--reorient', action='store_true',
                        help='rotate/reflect image data')
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
        md = exiv2.ImageFactory.open(in_file)
        md.readMetadata()
        md = md.exifData()
        lens = md['Exif.Photo.LensModel'].toString()
        aperture = exiv2.fNumber(md).toFloat()
        focal_length = exiv2.focalLength(md).toFloat()
        iso = exiv2.isoSpeed(md).toFloat()
        if '10-18' in lens:
            lens = 'Canon_10_18'
        elif '18-55' in lens:
            lens = 'Canon_18_55'
        elif '18-200' in lens:
            lens = 'Sigma_18_200'
        elif '70-300' in lens:
            lens = 'Sigma_70_300'
        elif '50' in lens:
            lens = 'Samyang_500'
            aperture = 6.3
            focal_length = 500
        else:
            print('Skip lens', lens)
            continue
        ca_params = get_chromatic_aberration_params(lens, focal_length)
        comps = {
            'reader': RawImageFileReader2(
                path=in_file, highlight_mode='Blend',
                demosaic_algorithm='DCB', dcb_iterations=0, dcb_enhance=False,
                fbdd_noise_reduction='Off', **ca_params),
            'rgbtoyuv': RGBtoYUV(matrix='709'),
            'sharpen': UnsharpMask(amount=0.3, radius=2.5, threshold=1.0),
            'yuvtorgb': YUVtoRGB(matrix='709'),
            'gamma': GammaCorrect(
                gamma='hybrid_log', scale=5,
                black=args.offset, white=100.0 / (2 ** args.exposure)),
            'quantise': ErrorFeedbackQuantise(),
            'writer': ImageFileWriterPIL(
                path=out_file, options='"quality":95', set_thumbnail=True),
            }
        if iso >= 3200:
            comps['reader'].set_config({
                'fbdd_noise_reduction': 'Full', 'noise_thr': 400})
        elif iso >= 1600:
            comps['reader'].set_config({
                'fbdd_noise_reduction': 'Full', 'noise_thr': 200})
        elif iso >= 400:
            comps['reader'].set_config({
                'fbdd_noise_reduction': 'Full', 'noise_thr': 100})
        if args.astro:
            comps['reader'].set_config({
                'fbdd_noise_reduction': 'Full',
                'noise_thr': 300,
                # force daylight white balance
                'use_camera_wb': False,
                'user_wb': '2123,1024,1531,1024',
                })
            comps['sharpen'].set_config({'amount': 0.9})
        if args.noise:
            comps['reader'].set_config({'noise_thr': args.noise})
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
        if args.reorient:
            comps['reorient'] = Reorient(orientation='auto')
            linkages[('reorient', 'output')] = linkages[('reader', 'output')]
            linkages[('reader', 'output')] = [('reorient', 'input')]
        vignette_params = get_vignette_params(lens, aperture, focal_length)
        if vignette_params:
            comps['vignette'] = VignetteCorrector(**vignette_params)
            linkages[('vignette', 'output')] = linkages[('reader', 'output')]
            linkages[('reader', 'output')] = [('vignette', 'input')]
        if args.gamma:
            comps['plot'] = PlotData()
            linkages[('gamma', 'function')] = [('plot', 'input')]
        if args.histogram:
            comps['histogram'] = ShowHistogram()
            linkages[('gamma', 'output')].append(('histogram', 'input'))
        if args.linear:
            from pyctools.components.io.imagefilecv import ImageFileWriterCV
            comps['lin_writer'] = ImageFileWriterCV(path=base + 'l.tiff')
            comps['lin_writer'].set_config({'16bit': True})
            linkages[('yuvtorgb', 'output')].append(('lin_writer', 'input'))
        if args.colour != 1.0:
            comps['colour'] = Arithmetic(
                func='data * pt_float({})'.format(args.colour))
            linkages[('colour', 'output')] = linkages[('rgbtoyuv', 'output_UV')]
            linkages[('rgbtoyuv', 'output_UV')] = [('colour', 'input')]
        if args.filter_colour > 0:
            comps['filter'] = UnsharpMask(
                amount=-1, radius=args.filter_colour, denoise=False)
            linkages[('filter', 'output')] = linkages[('rgbtoyuv', 'output_UV')]
            linkages[('rgbtoyuv', 'output_UV')] = [('filter', 'input')]
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
            im = exiv2.ImageFactory.open(out_file)
            im.readMetadata()
            exif_data = im.exifData()
            xmp_data = im.xmpData()
            now = datetime.now()
            tz_offset = (now - datetime.utcnow()).total_seconds() / 60
            tz_offset = int(round(tz_offset / 15, 0) * 15)
            if tz_offset < 0:
                sign = '-'
                tz_offset = -tz_offset
            else:
                sign = '+'
            exif_data['Exif.Image.DateTime'] = now.strftime('%Y:%m:%d %H:%M:%S')
            del exif_data['Exif.Photo.SubSecTime']
            xmp_data['Xmp.xmp.ModifyDate'] = (
                now.strftime('%Y-%m-%dT%H:%M:%S') +
                sign + '{:02d}:{:02d}'.format(tz_offset // 60, tz_offset % 60))
            # set audit trail
            audit = xmp_data['Xmp.pyctools.audit'].value().toString()
            audit += '{} = process_raw({})\n'.format(
                os.path.basename(out_file), os.path.basename(in_file))
            params = []
            for key, value in vars(args).items():
                if key not in ('audit', 'file', 'gamma', 'histogram'):
                    params.append('{}: {}'.format(key, value))
            if params:
                audit += '    ' + ', '.join(params) + '\n'
            xmp_data['Xmp.pyctools.audit'] = audit
            im.writeMetadata()
            if args.audit:
                print(audit)


if __name__ == '__main__':
    sys.exit(main())
