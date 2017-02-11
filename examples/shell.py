# coding=utf-8
"""
Launches a Python shell with a configured API client ready to go.
"""
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from argparse import ArgumentParser
from getpass import getpass as secure_input
from logging import DEBUG, basicConfig, getLogger
from sys import argv, stderr

from six import text_type

# Import all IOTA symbols into module scope, so that it's more
# convenient for the user.
from iota import *

from iota import __version__
from iota.adapter import resolve_adapter
from iota.adapter.wrappers import RoutingWrapper
from iota.crypto.addresses import AddressGenerator, MemoryAddressCache


def main(uri, testnet, pow_uri, debug_requests):
  # type: (Text, bool, Text, bool) -> None
  seed = secure_input(
    'Enter seed and press return (typing will not be shown).\n'
    'If no seed is specified, a random one will be used instead.\n'
  )

  if isinstance(seed, text_type):
    seed = seed.encode('ascii')

  adapter_ = resolve_adapter(uri)

  # If ``pow_uri`` is specified, route POW requests to a separate node.
  if pow_uri:
    pow_adapter = resolve_adapter(pow_uri)

    adapter_ =\
      RoutingWrapper(adapter_)\
        .add_route('attachToTangle', pow_adapter)\
        .add_route('interruptAttachingToTangle', pow_adapter)

  # If ``debug_requests`` is specified, log HTTP requests/responses.
  if debug_requests:
    basicConfig(level=DEBUG, stream=stderr)

    logger = getLogger(__name__)
    logger.setLevel(DEBUG)

    adapter_.set_logger(logger)

  iota = Iota(adapter_, seed=seed, testnet=testnet)

  # To speed up certain operations, install an address cache.
  AddressGenerator.cache = MemoryAddressCache()

  _banner = (
    'IOTA API client for {uri} ({testnet}) initialized as variable `iota`.\n'
    'Type `help(iota)` for help.'.format(
      testnet = 'testnet' if testnet else 'mainnet',
      uri     = uri,
    )
  )

  start_shell(iota, _banner)


def start_shell(iota, _banner):
  """
  Starts the shell with limited scope.
  """
  try:
    # noinspection PyUnresolvedReferences
    import IPython
  except ImportError:
    # IPython not available; use regular Python REPL.
    from code import InteractiveConsole
    InteractiveConsole(locals={'iota': iota}).interact(_banner)
  else:
    # Launch IPython REPL.
    IPython.embed(header=_banner)


if __name__ == '__main__':
  parser = ArgumentParser(
    description = __doc__,
    epilog      = 'PyOTA v{version}'.format(version=__version__),
  )

  parser.add_argument(
    '--uri',
      type    = text_type,
      default = 'http://localhost:14265/',

      help =
        'URI of the node to connect to '
        '(defaults to http://localhost:14265/).',
  )

  parser.add_argument(
    '--pow-uri',
      type    = text_type,
      default = None,
      dest    = 'pow_uri',
      help    = 'URI of node to send POW requests to.'
  )

  parser.add_argument(
    '--testnet',
      action  = 'store_true',
      default = False,
      help    = 'If set, use testnet settings (e.g., for PoW).',
  )

  parser.add_argument(
    '--debug',
      action  = 'store_true',
      default = False,
      dest    = 'debug_requests',
      help    = 'If set, log HTTP requests to stderr.'
  )

  main(**vars(parser.parse_args(argv[1:])))
