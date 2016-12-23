# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

# Define a few magic constants.
DEFAULT_PORT = 14265
"""
Default port to use when configuring an adapter, if the port is not
specified.
"""

TRITS_PER_TRYTE = 3
"""
Number of trits in a tryte.
Changing this will probably break everything, but there's a chance it
could create a sexy new altcoin instead.
In that way, it's kind of like toxic waste in a superhero story.
"""

# Activate TrytesCodec.
from .codecs import *

# Make some imports accessible from the top level of the package.
# Note that order is important, to prevent circular imports.
from .types import *
from .transaction import *
from .adapter import *
from .api import *

# :see: http://stackoverflow.com/a/2073599/
from pkg_resources import require
__version__ = require('PyOTA')[0].version
del require
