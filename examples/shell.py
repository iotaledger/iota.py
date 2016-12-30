# coding=utf-8
"""
Launches a Python shell with a configured API client ready to go.
"""
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from argparse import ArgumentParser
from getpass import getpass as secure_input
from sys import argv

from iota import __version__
from six import text_type

# Import all IOTA symbols into module scope, so that it's more
# convenient for the user.
from iota import *


def main(uri, testnet):
  seed = secure_input(
    'Enter seed and press return (typing will not be shown).\n'
    'If no seed is specified, a random one will be used instead.\n'
  )

  if isinstance(seed, text_type):
    seed = seed.encode('ascii')

  iota = Iota(uri, seed=seed, testnet=testnet)

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
      default = 'udp://localhost:14265/',

      help =
        'URI of the node to connect to '
        '(defaults to udp://localhost:14265/).',
  )

  parser.add_argument(
    '--testnet',
      action  = 'store_true',
      default = False,
      help    = 'If specified, use testnet settings (e.g., for PoW).',
  )

  main(**vars(parser.parse_args(argv[1:])))
