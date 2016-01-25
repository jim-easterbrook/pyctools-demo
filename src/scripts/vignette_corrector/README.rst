Vignette corrector
==================

This is a tool to remove vignetting (i.e. darkening of edges) from still images.
The process used is described in greater detail in my blog post `correcting vignetting in digital photographs <http://jim-jotting.blogspot.co.uk/2016/01/correcting-vignetting-in-digital.html>`_.

Setting the parameters
----------------------

The ``set_parameters.py`` script allows you to adjust the vignette corrector configuration to minimise vignetting with a specific lens (and lens settings).
First you need to set your camera to store raw images, then photograph an evenly illuminated grey card.
Place a copy of the raw image file in the ``video`` directory and name it ``grey`` (e.g. ``grey.CR2`` if you have a Canon camera).

Now use the ``pyctools-editor`` program to open the ``check_raw_read.py`` script.
This displays the image and its histogram.
Open the ``RawImageFileReader()`` config and make sure its ``path`` parameter matches your ``grey`` file name before running the script.
If the image is too bright or dark, adjust the ``brightness`` parameter to correct this.
Make a note of the correct ``brightness`` setting for your image file.

Load the ``set_parameters.py`` script and adjust the ``RawImageFileReader()`` ``path`` and ``brightness`` parameters if necessary.
If your camera's images are much larger or smaller than the 5184 x 3456 that I've been using you may want to adjust the ``xdown`` and ``ydown`` settings of the ``FilterGenerator()`` and ``Resize()`` components.
These reduce the image size to fit the computer monitor (and make processing a bit faster as well).

Open the configuration of the final ``Arithmetic()`` component (called ``contrast``) and set its ``func`` parameter to ::

   ((data - 64) * 4) + 128

Open the ``VignetteCorrector()`` configuration and set the ``r1``, ``r2`` and ``r3`` values to zero.
Keep these configurations open as you will need to adjust them when running the script.

When the script is run it should display a video window showing a contrast enhanced version of your grey image.
You may need to adjust the amount subtracted in the ``Arithmetic()`` component (initially 64) if this grey is too dark or too light.
Now you can adjust the ``VignetteCorrector()`` parameters to produce an even brightness grey image.
As you get closer to the correct settings you can increase the multiplier (initially 4) to enhance the contrast even more.

Using the vignette corrector
----------------------------

The scripts ``correct_raw.py`` and ``correct_jpeg.py`` can be used to correct vignetting in raw or JPEG image files.
You'll need to adjust the file reader, file writer and vignette corrector parameters to suit your image files and lens.