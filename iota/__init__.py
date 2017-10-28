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

STANDARD_UNITS = {
    # Valid IOTA unit suffixes. Example value '-273.15 Ki'
    'i': 1,
    'Ki': 1000,
    'Mi': 1000000,
    'Gi': 1000000000,
    'Ti': 1000000000000,
    'Pi': 1000000000000000
}


# Activate codecs.
from .codecs import *

# Make some imports accessible from the top level of the package.
# Note that order is important, to prevent circular imports.
from .types import *
from .transaction import *
from .adapter import *
from .api import *
from .trits import *

# :see: http://stackoverflow.com/a/2073599/
from pkg_resources import require
__version__ = require('PyOTA')[0].version
del require
