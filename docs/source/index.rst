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
* RESEA (RTSys)
* uPAM (Seiche)
* EARS
* MTE AURAL (MTE)


They all inherit from the main class Hydrophone.
If a certain recorder provides an output different than a regular wav file, functions to read and understand the output
are provided.
Functions to read the metadata are also provided (which is often encoded in the file name).


.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   install
   quickstart

.. toctree::
   :caption: Hydrophone objects
   :maxdepth: 1

   data_structures

.. toctree::
   :maxdepth: 2
   :caption: Example Gallery

   _auto_examples/index


Citing pyhydrophone
~~~~~~~~~~~~~~~~~~~

.. note::
  If you find this package useful in your research, we would appreciate citations to:

Parcerisas (2023). lifewatch/pyhydrophone: A package to deal with hydrophone data. Zenodo.
https://doi.org/10.5281/zenodo.7588428


About the project
~~~~~~~~~~~~~~~~~
This project has been funded by `LifeWatch Belgium <https://www.lifewatch.be/>`_.

.. image:: _static/lw_logo.png


For any questions please relate to clea.parcerisas@vliz.be


Indices and tables
~~~~~~~~~~~~~~~~~~

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`