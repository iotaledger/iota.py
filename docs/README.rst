.. image:: https://travis-ci.org/iotaledger/iota.py.svg?branch=master
   :target: https://travis-ci.org/iotaledger/iota.py

.. image:: https://readthedocs.org/projects/pyota/badge/?version=latest
   :target: http://pyota.readthedocs.io/en/latest/?badge=latest

=====
PyOTA
=====
This is the official Python library for the IOTA Core.

It implements both the `official API`_, as well as newly-proposed functionality
(such as signing, bundles, utilities and conversion).

Join the Discussion
===================
If you want to get involved in the community, need help with getting setup,
have any issues related with the library or just want to discuss Blockchain,
Distributed Ledgers and IoT with other people, feel free to join our `Discord`_.

If you encounter any issues while using PyOTA, please report them using the
`PyOTA Bug Tracker`_.

============
Dependencies
============
PyOTA is compatible with Python 3.7 and 3.6.

=============
Install PyOTA
=============
To install the latest version::

  pip install pyota

Optional C Extension
====================
PyOTA has an optional C extension that improves the performance of its
cryptography features significantly (speedups of **60x** are common!).

To install this extension, use the following command::

   pip install pyota[ccurl]

Optional Local Pow
==================
To perform proof-of-work locally without relying on a node,
you can install an extension module called `PyOTA-PoW`_ .

Specifiy the ``local_pow=True`` argument when creating an
api instance, that will redirect all ``attach_to_tangle``
API calls to an interface function in the ``pow`` package.

To install this extension, use the following command::

   pip install pyota[pow]

Alternativley you can take a look on the repository
`Ccurl.interface.py`_  to install Pyota-PoW.
Follow the steps depicted in the repo's README file.

Installing from Source
======================

#. `Create virtualenv`_ (recommended, but not required).
#. ``git clone https://github.com/iotaledger/iota.py.git``
#. ``pip install -e .``

Running Unit Tests
------------------
To run unit tests after installing from source::

  python setup.py test

PyOTA is also compatible with `tox`_, which will run the unit tests in different
virtual environments (one for each supported version of Python).

To run the unit tests, it is recommended that you use the ``-p`` argument.
This speeds up the tests by running them in parallel.

Install PyOTA with the ``test-runner`` extra to set up the necessary
dependencies, and then you can run the tests with the ``tox`` command::

  pip install -e .[test-runner]
  tox -v -p all

=============
Documentation
=============
PyOTA's documentation is available on `ReadTheDocs`_.

If you are installing from source (see above), you
can also build the documentation locally:

#. Install extra dependencies (you only have to do this once)::

      pip install .[docs-builder]

   .. tip::

      To install the CCurl extension and the documentation builder tools
      together, use the following command::

         pip install .[ccurl,docs-builder]

#. Switch to the ``docs`` directory::

      cd docs

#. Build the documentation::

      make html

.. _Create virtualenv: https://realpython.com/blog/python/python-virtual-environments-a-primer/
.. _Discord: https://discord.iota.org/
.. _PyOTA Bug Tracker: https://github.com/iotaledger/iota.py/issues
.. _ReadTheDocs: https://pyota.readthedocs.io/
.. _official API: https://docs.iota.org/docs/node-software/0.1/iri/references/api-reference
.. _tox: https://tox.readthedocs.io/
.. _Ccurl.interface.py: https://github.com/iotaledger/ccurl.interface.py
.. _PyOTA-PoW: https://pypi.org/project/PyOTA-PoW/
