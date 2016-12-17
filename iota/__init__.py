# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

DEFAULT_PORT = 14265

# Activate TrytesCodec.
from .codecs import *

# Make some imports accessible from the top level of the package.
# Note that order is important, to prevent circular imports.
from .types import *
from .adapter import *
from .api import *

# Load Curl implementation.
import iota.pycurl as curl

# :see: http://stackoverflow.com/a/2073599/
from pkg_resources import require
__version__ = require('PyOTA')[0].version
del require
