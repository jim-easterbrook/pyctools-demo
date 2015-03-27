PAL decoding
============

This demonstration compares two different methods of decoding a PAL composite video sequence.
Before running them you need to prepare a simple moving sequence from a still image.
Copy a still image (around 4000 x 3000 pixels) to ``video/still.jpg`` then run ``src/scripts/wobble_image.py`` to generate ``video/still_wobble.avi``.

PAL coder
---------

Run this first to generate a PAL file for the decoders to work with.

The source video is horizontally re-sampled to (approximately) 4Fsc (4 x the colour sub-carrier frequency) which is the standard sampling rate for digital PAL processing.
It is then converted from RGB to YUV format.

The U & V signals are pre-filtered before being modulated by the U & V sub-carriers.
The modulated signals are scaled and added together to form the chrominance signal which is then added to the luminance to form the PAL signal.
This is then scaled to fit in the range 0..255 before being saved to a 16-bit file.

PAL decoder
-----------

This is a simple PAL decoder with rather poor quality filters.

The luminance (Y) is obtained by passing the PAL signal through a notch filter to attenuate the colour sub-carrier.
The U & V signals are obtained by demodulating and low-pass filtering the PAL signal.

PAL FFT decoder
---------------

This is a simplified (2-D) version of the `BBC Transform PAL decoder <http://www.jim-easterbrook.me.uk/pal/>`_.
Its operation is too complex to describe here.