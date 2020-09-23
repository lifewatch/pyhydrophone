pyhydrophone |version|
======================

Description
-----------
pyhydrophone helps keeping together all the information of the recorder.
It makes it easier to read different hydrophones' output files and extract the information.

Each class represents a different hydrophone. The available ones now are (others will be added):

* SoundTrap (OceanInstruments)
* Seiche (Seiche)
* AMAR (JASCO)
* B&K Nexus (Bruel & Kjaer)

They all inherit from the main class Hydrophone.
If a certain recorder provides an output different than a regular wav file, functions to read and understand the output
are provided.
Functions to read the metadata are also provided (which is often encoded in the file name).


.. toctree::
  :maxdepth: 1
  :caption: User Guide

  Data Structures <data_structures>

.. toctree::
  :maxdepth: 1
  :caption: Reference Guide

  Classes, Attributes and Methods <reference>

Contact
------------

For any questions please relate to clea.parcerisas@vliz.be



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


