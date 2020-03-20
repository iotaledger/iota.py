#!/usr/bin/env python
"""
Launches a Python shell with a configured API client ready to go.
"""
from argparse import ArgumentParser
from logging import basicConfig, getLogger, DEBUG
from sys import stderr

from typing import Any
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

    def execute(self, api: Iota, **arguments: Any) -> int:
        debug_requests = arguments['debug_requests']
        pow_uri = arguments['pow_uri']

        # If ``pow_uri`` is specified, route POW requests to a separate
        # node.
        if pow_uri:
            pow_adapter = resolve_adapter(pow_uri)

            api.adapter = RoutingWrapper(api.adapter)
            api.adapter.add_route('attachToTangle', pow_adapter)
            api.adapter.add_route('interruptAttachingToTangle', pow_adapter)

        # If ``debug_requests`` is specified, log HTTP requests/responses.
        if debug_requests:
            # Inject a logger into the IOTA HTTP adapter.
            # This will turn on logging for underlying httpx client as well
            basicConfig(level=DEBUG, stream=stderr)

            logger = getLogger(__name__)
            logger.setLevel(DEBUG)

            api.adapter.set_logger(logger)

        try:
            self._start_repl(api)
        except KeyboardInterrupt:
            pass

        return 0

    def create_argument_parser(self) -> ArgumentParser:
        parser = super(IotaReplCommandLineApp, self).create_argument_parser()

        parser.add_argument(
            '--pow-uri',
            type=str,
            default=None,
            dest='pow_uri',
            help='URI of node to send POW requests to.'
        )

        parser.add_argument(
            '--debug',
            action='store_true',
            default=False,
            dest='debug_requests',
            help='If set, log HTTP requests to stderr.'
        )

        return parser

    @staticmethod
    def _start_repl(api: Iota) -> None:
        """
        Starts the REPL.
        """
        banner = (
            'IOTA API client for {uri} ({devnet}) '
            'initialized as variable `api`.\n'
            'Type `help(api)` for list of API commands.'.format(
                devnet='devnet' if api.devnet else 'mainnet',
                uri=api.adapter.get_uri(),
            )
        )

        scope_vars = {'api': api}

        try:
            import IPython
        except ImportError:
            # IPython not available; use regular Python REPL.
            from code import InteractiveConsole
            InteractiveConsole(locals=scope_vars).interact(banner, '')
        else:
            print(banner)
            IPython.start_ipython(argv=[], user_ns=scope_vars)


def main():
    """
    Entry point for ``setup.py``.
    """
    IotaReplCommandLineApp().main()


if __name__ == '__main__':
    main()
