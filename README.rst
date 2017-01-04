.. image:: https://travis-ci.org/iotaledger/iota.lib.py.svg?branch=develop
   :target: https://travis-ci.org/iotaledger/iota.lib.py

=====
PyOTA
=====
This is the official Python library for the IOTA Core.

It implements both the `official API`_, as well as newly-proposed functionality
(such as signing, bundles, utilities and conversion).

.. warning::
   This is pre-release software!
   There may be performance and stability issues.

   Please report any issues using the `PyOTA Bug Tracker`_.

Join the Discussion
===================
If you want to get involved in the community, need help with getting setup,
have any issues related with the library or just want to discuss Blockchain,
Distributed Ledgers and IoT with other people, feel free to join our `Slack`_.

You can also ask questions on our `dedicated forum`_.

============
Dependencies
============
PyOTA is compatible with Python 3.6, 3.5 and 2.7.

============
Installation
============
To install the latest version::

  pip install --pre pyota

**Important:** PyOTA is currently pre-release software.
There may be performance and stability issues.

Please report any issues using the `PyOTA Bug Tracker`_.

Installing from Source
======================

1. `Create virtualenv`_ (recommended, but not required).
2. ``git clone https://github.com/iotaledger/iota.lib.py.git``
3. ``pip install -e .``

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
.. _SWIG: http://www.swig.org/download.html
.. _Slack: http://slack.iotatoken.com/
.. _dedicated forum: https://forum.iotatoken.com/
.. _official API: https://iota.readme.io/
.. _PyOTA Bug Tracker: https://github.com/iotaledger/iota.lib.py/issues
.. _tox: https://tox.readthedocs.io/
