Pyctools-demo
=============

Examples of things you can do with Pyctools.

This uses `Pyctools <https://github.com/jim-easterbrook/pyctools>`_ to illustrate a few features of video processing.

Requirements
------------

* `Pyctools <https://github.com/jim-easterbrook/pyctools>`_ and its requirements.

Installation
------------

Use of Pyctools-demo requires easy access to the source files, so installation with ``pip`` is not really appropriate.
You should clone the GitHub repository, or download and extract a zip or tar.gz archive from the GitHub releases page, and then use ``setup.py`` to install the demo components::

  git clone https://github.com/jim-easterbrook/pyctools-demo.git
  cd pyctools-demo
  python setup.py build
  sudo python setup.py install

Use
---

The ``src/scripts`` directory contains everal sets of files that can be loaded into the Pyctools graph editor or run directly.
Many of them need a source video to work with.
Create a file (or link) called ``example.avi`` in the ``video`` directory.

Licence
-------

| Pyctools-demo - examples of things you can do with pyctools.
| http://github.com/jim-easterbrook/pyctools-demo
| Copyright (C) 2015  Jim Easterbrook  jim@jim-easterbrook.me.uk

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.
