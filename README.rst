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
Distributed Ledgers and IoT with other people, feel free to join our `Slack`_.

You can also ask questions on our `dedicated forum`_.

============
Dependencies
============
PyOTA requires Python v3.5 or v2.7.

============
Installation
============
To install the latest stable version::

  pip install pyota

To install the development version::

  pip install https://github.com/iotaledger/pyota/archive/develop.zip

Installing from Source
======================
PyOTA uses the `curl extension`_, which requires `SWIG`_ in order to build.

1. `Create virtualenv`_ (recommended, but not required).
2. ``git clone https://github.com/iotaledger/pyota.git``
3. ``git submodule init --recursive``
4. ``pip install -e .``
   - This step will fail if `SWIG`_ is not installed.

Running Unit Tests
------------------
To run unit tests after installing from source::

  python setup.py test

PyOTA is also compatible with `tox`_::

  pip install tox
  tox

=============
Documentation
=============
For the full documentation of this library, please refer to the
`official API`_


.. _Create virtualenv: https://virtualenvwrapper.readthedocs.io/
.. _curl extension: https://github.com/iotaledger/ccurl
.. _dedicated forum: http://forum.iotatoken.com/
.. _official API: https://iota.readme.io/
.. _Slack: http://slack.iotatoken.com/
.. _SWIG: http://www.swig.org/download.html
.. _tox: https://tox.readthedocs.io/
