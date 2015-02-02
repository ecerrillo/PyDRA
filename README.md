PyDRA
=====

1. Introduction

  PyDRA is acronym for Python Digital Rock Art. It is a provsional codename, since the software cannot be considered as a definitive realese and much work needs to be done in order to get the application working properly.

  PyDRA consist of a GUI and several algorithms for processing rock paintings. Most of them are published common methods, meanwhile some others are being currently experimented.

  This piece software was initially written by Enrique Cerrillo Cuenca and José Ángel Martínez del Pozo, from the Institute of Archaeology - Mérida (CSIC, Spanish Council for Scientific Research). Currently, this repository is being mantained by Enrique Cerrillo Cuenca.

  Some papers has been published up to the date describing the basic processes:

  http://link.springer.com/article/10.1007%2Fs12520-013-0147-2
  http://www.sciencedirect.com/science/article/pii/S0305440315000199


2. Installation and dependencies
 
  As long as you can manage to solve the dependencies you will be able to run PyDRA in any platform. At the current time it has been executed in Mac OS X (10.8+) and Ubuntu. We are far from distribute a standalone version, so an additional effort should be done to get all dependencies installed.

  In order to install PyDRA you will need to install the followings libraries (the list might not be definitive, and not listed libraries might be required):

      - Python (2.7) and the following libraries: Numpy, Scipy, PyQt4 (maybe PyQt5), formlayout, scikit-learn, reportlab, gdal, pillow (former PIL), pylab, pyqtgraph

      - OpenCV (with Python support)

      - gphoto2 (optional)

      - dcraw


3. Running PyDRA

  Open a terminal/console window
  
  Point to the folder where you have forked this repository
  
  Simply run: python pydra.py
  
  A GUI should be opened with a blank workspace


4. Instructions

  PyDRA pretends to be an intuitive GUI for analysing images, however a strong re-writting of the code should be done to achieve this goal. Basically, when a image is loaded the menus get active, letting the user to perform several analysis.

  PyDRA supports all the image formats implemented in GDAL library. This allow the support for 16 bit images. RAW files can also be used, although only NEF files can be read at the current PyDRA state. This last option can be easly modified for accepting other RAW formats.


5. Improvements

  The GUI can be improved significantly and perhaps moved to wxpython, which seems to be a more appropiate platform.

  Several algorithms can be also improved.
