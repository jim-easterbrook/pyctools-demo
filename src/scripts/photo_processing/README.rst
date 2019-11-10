Photo processing
================

This is a script (still being developed) I use to process "raw" files from my Canon DSLR.
Note that it cannot be run with the `pyctools-editor`_ GUI.
It is a command line script, with some optional parameters.

The processing pipeline is as follows:

1. RawImageFileReader2_ is used to read the image with no gamma correction.
2. VignetteCorrector_ corrects any darkening of image corners if required.
3. RGBtoYUV_ is used to convert from RGB to Y (luminance) and "UV" (actually CbCr) colour difference signals.
4. The Y signal is sharpened with UnsharpMask_ and the UV signal is increased with Arithmetic_ - this increases the colour saturation a bit.
5. The Y & UV signals are converted back to RGB with YUVtoRGB_.
6. GammaCorrect_ converts the "linear light" signal to "gamma corrected" form as stored in most image file formats.
7. ErrorFeedbackQuantise_ truncates the result to integers without introducing banding effects. (All the processing so far uses floating point numbers.)
8. ImageFileWriterPIL_ saves the result to a JPEG file.

Command line options can be used to add a ShowHistogram_ component to show the histogram of the final image, or a PlotData_ component to show the gamma curve used.
Other command line options allow tweaking of the exposure or adding an extra UnsharpMask_ between stages 5 & 6.

Chromatic aberration correction
-------------------------------

The RawImageFileReader2_ component uses LibRaw_ - a powerful library with a lot of options.
It can enlarge or reduce the red and blue signals to minimise the visibility of lateral chromatic aberration.
By taking many pictures of a suitable test chart I've found the best settings for each of my lenses, at a variety of focal lengths in the case of the zoom lenses.
This data is included in the script.
If you copy my script you'll need to supply your own data!

Vignette correction
-------------------

I've also measured the vignetting (or "peripheral illumination error") of each of my lenses at a variety of focal lengths and apertures.
I've been able to fit different power law functions to each of these measurements.
The script contains all this data and interpolates corrections for other focal lengths and apertures.

Gamma correction
----------------

Some of the above processing (such as vignette correction) has to be done on "linear light" signals.
This is what raw files store - the camera's sensor output is proportional to the intensity of the light hitting it (except when completely saturated, of course).
Before display images need to be "gamma corrected".
This uses a non-linear transfer function so that the signal is roughly proportional to perceived brightness.
There are many transfer functions available, from simple power laws to more complicated logarithmic functions.
I've settled on using "Hybrid Log-Gamma", a proposal from my former colleagues at BBC Research.


.. _Arithmetic: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.arithmetic.html#pyctools.components.arithmetic.Arithmetic

.. _ErrorFeedbackQuantise: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.colourspace.quantise.html

.. _GammaCorrect: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.colourspace.gammacorrection.html#pyctools.components.colourspace.gammacorrection.GammaCorrect

.. _ImageFileWriterPIL: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.io.imagefilepil.html

.. _LibRaw: https://www.libraw.org/

.. _PlotData: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.io.plotdata.html

.. _pyctools-editor: https://pyctools.readthedocs.io/en/latest/api/tools/pyctools.tools.editor.html

.. _RawImageFileReader2: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.io.rawimagefilereader2.html

.. _RGBtoYUV: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.colourspace.rgbtoyuv.html

.. _ShowHistogram: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.qt.showhistogram.html

.. _UnsharpMask: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.photo.unsharpmask.html

.. _VignetteCorrector: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.photo.vignettecorrector.html#pyctools.components.photo.vignettecorrector.VignetteCorrector

.. _YUVtoRGB: https://pyctools.readthedocs.io/en/latest/api/components/pyctools.components.colourspace.yuvtorgb.html
