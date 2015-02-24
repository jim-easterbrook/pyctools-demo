De-interlacing
==============

This demonstration attempts to show the effectiveness of different methods of de-interlacing an interlaced video sequence.
`Wikipedia <http://en.wikipedia.org/wiki/Interlaced_video>`_ has a good introduction to interlace.

Stage 1
-------

This shows the effect of discarding half the lines to make an interlaced sequence, with and without a suitable pre-filter.
The hyperbolic zone plate's vertical frequency varies with horizontal position, reaching half sampling frequency at the centre.
If this is converted to interlace with no filtering, half sampling frequency is aliased to zero (spatial) frequency at half the temporal frequency.
This produces a lot of flicker, made particularly visible here by being displayed at 20Hz.

Many modern monitors have flicker suppression circuitry, so setting the display frame rates to match your monitor (probably 60Hz) may make the flicker invisible.

A low-pass vertical filter can be used to attenuate frequencies near half sampling, reducing flicker at the expense of a slight loss of vertical resolution.
This example uses the "well known HHI pre-filter".

Stage 2
-------

(Before running stage 2 you need to prepare a simple moving sequence from a still image.
Copy a still image (around 4000 x 3000 pixels) to ``video/still.jpg`` then run ``src/scripts/wobble_image.py`` to generate ``video/still_wobble.avi``.)

Stage 2 is identical to stage 1 but uses a real video clip instead of a zone plate.
If your source image is suitable you should see more artefacts in the unfiltered image than in the filtered one, but the latter still shows plenty of evidence of having been interlaced.

Stage 3
-------

The previous stages have converted the interlaced video to sequential (for display on a sequential monitor) by simple line repetition.
This is probably the worst way to do it.
This demonstration compares the line repeat de-interlacer with a multi-tap vertical filter.

Stage 4
-------

Better de-interlacing is possible by using information from more than one field.
This demonstration compares a multi-tap vertical filter with the "Weston 3 field" de-interlacer invented at BBC R&D.
You should see a worthwhile improvement in the picture quality.