#!/usr/bin/env python

from codecs import StreamReader, open
from distutils.version import LooseVersion

import setuptools

##
# Because of the way PyOTA declares its dependencies, it requires a
# more recent version of setuptools.
# https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
if LooseVersion(setuptools.__version__) < LooseVersion('24.2'):
    import sys

    sys.exit('Installation failed: Upgrade setuptools to version 24.2 or later')

##
# Load long description for PyPI.
with open('docs/README.rst', 'r', 'utf-8') as f:  # type: StreamReader
    long_description = f.read()

##
# Declare test dependencies separately, so that they can be installed
# either automatically (``python setup.py test``) or manually
# (``pip install -e .[test-runner]``).
tests_require = [
    'aiounittest',
    'nose',
]

##
# Off we go!
setuptools.setup(
    name='PyOTA',
    description='IOTA API library for Python',
    url='https://github.com/iotaledger/iota.py',
    version='3.0.0b1',

    long_description=long_description,

    packages=setuptools.find_packages('.', exclude=(
        'examples', 'examples.*',
        'test', 'test.*',
    )),

    include_package_data=True,

    # http://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
    entry_points={
        'console_scripts': [
            'pyota-cli=iota.bin.repl:main',
        ],
    },

    # Tell setuptools which python versions to support. Will include metadata
    # in the built sdist and wheel that tells pypi to tell pip about supported
    # python versions.
    # 'python_requires' works from setuptools 24.2.0 (previous versions ignore
    # it with a warning), pip understands it from 9.0.0.
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.6, <4',

    # filters is no longer maintained and does not support Python 3.7
    # phx-filters is a fork that supports 3.7 and 3.8 but not 2.7

    install_requires=[
        'httpx',
        'phx-filters',
        'pysha3',
    ],

    extras_require={
        'ccurl': ['pyota-ccurl'],
        'docs-builder': ['sphinx >= 2.4.2', 'sphinx_rtd_theme >= 0.4.3'],
        'pow': ['pyota-pow >= 1.0.2'],
        # tox is able to run the tests in parallel since version 3.7
        'test-runner': ['tox >= 3.7'] + tests_require,
    },

    test_suite='test',
    test_loader='nose.loader:TestLoader',
    tests_require=tests_require,

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords=(
        'iota,tangle,iot,internet of things,api,library,cryptocurrency,'
        'balanced ternary'
    ),

    author='Phoenix Zerin',
    author_email='phx@phx.ph',
)
