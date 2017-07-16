#!/usr/bin/env python
# coding=utf-8
"""
Launches a Python shell with a configured API client ready to go.
"""
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from argparse import ArgumentParser
from logging import DEBUG, basicConfig, getLogger
from sys import stderr

from six import text_type

# Import all IOTA symbols into module scope, so that it's more
# convenient for the user.
from iota import *

from iota.adapter import resolve_adapter
from iota.adapter.wrappers import RoutingWrapper
from iota.bin import IotaCommandLineApp


class IotaReplCommandLineApp(IotaCommandLineApp):
  """
  Creates an IOTA API instance and drops the user into a REPL.
  """
  def execute(self, api, **arguments):
    # type: (Iota, ...) -> int
    debug_requests  = arguments['debug_requests']
    pow_uri         = arguments['pow_uri']

    # If ``pow_uri`` is specified, route POW requests to a separate
    # node.
    if pow_uri:
      pow_adapter = resolve_adapter(pow_uri)

      api.adapter =\
        RoutingWrapper(api.adapter)\
          .add_route('attachToTangle', pow_adapter)\
          .add_route('interruptAttachingToTangle', pow_adapter)

    # If ``debug_requests`` is specified, log HTTP requests/responses.
    if debug_requests:
      basicConfig(level=DEBUG, stream=stderr)

      logger = getLogger(__name__)
      logger.setLevel(DEBUG)

      api.adapter.set_logger(logger)

    try:
      self._start_repl(api)
    except KeyboardInterrupt:
      pass

    return 0

  def create_argument_parser(self):
    # type: () -> ArgumentParser
    parser = super(IotaReplCommandLineApp, self).create_argument_parser()

    parser.add_argument(
      '--pow-uri',
        type    = text_type,
        default = None,
        dest    = 'pow_uri',
        help    = 'URI of node to send POW requests to.'
    )

    parser.add_argument(
      '--debug',
        action  = 'store_true',
        default = False,
        dest    = 'debug_requests',
        help    = 'If set, log HTTP requests to stderr.'
    )

    return parser

  @staticmethod
  def _start_repl(api):
    # type: (Iota) -> None
    """
    Starts the REPL.
    """
    _banner = (
      'IOTA API client for {uri} ({testnet}) initialized as variable `api`.\n'
      'Type `help(api)` for list of API commands.'.format(
        testnet = 'testnet' if api.testnet else 'mainnet',
        uri     = api.adapter.get_uri(),
      )
    )

    try:
      # noinspection PyUnresolvedReferences
      import IPython
    except ImportError:
      # IPython not available; use regular Python REPL.
      from code import InteractiveConsole
      InteractiveConsole(locals={'api': api}).interact(_banner)
    else:
      # Launch IPython REPL.
      IPython.embed(header=_banner)


def main():
  """
  Entry point for ``setup.py``.
  """
  IotaReplCommandLineApp().main()


if __name__ == '__main__':
  main()
