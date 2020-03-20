import sys
from abc import ABCMeta, abstractmethod as abstract_method
from argparse import ArgumentParser
from getpass import getpass as secure_input
from io import StringIO
from sys import exit
from typing import Any, Optional

from iota import Iota, __version__
from iota.crypto.types import Seed

__all__ = [
    'IotaCommandLineApp',
]


class IotaCommandLineApp(object, metaclass=ABCMeta):
    """
    Base functionality for a PyOTA-powered command-line application.
    """
    requires_seed = True
    """
    Whether the command requires the user to provide a seed.
    """

    def __init__(
            self,
            stdout: StringIO = sys.stdout,
            stderr: StringIO = sys.stderr,
            stdin: StringIO = sys.stdin
    ) -> None:
        super(IotaCommandLineApp, self).__init__()

        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin

    @abstract_method
    def execute(self, api: Iota, **arguments: Any) -> Optional[int]:
        """
        Executes the command and (optionally) returns an exit code (used by
        the shell to determine if the application exited cleanly).

        :param api:
            The API object used to communicate with the node.

        :param arguments:
            Command-line arguments parsed by the argument parser.
        """
        raise NotImplementedError(
            'Not implemented in {cls}.'.format(cls=type(self).__name__),
        )

    def main(self) -> None:
        """
        Executes the command from :py:data:`sys.argv` and exits.
        """
        exit(self.run_from_argv())

    def run_from_argv(self, argv: Optional[tuple] = None) -> int:
        """
        Executes the command from a collection of arguments (e.g.,
        :py:data`sys.argv`) and returns the exit code.

        :param argv:
            Arguments to pass to the argument parser.
            If ``None``, defaults to ``sys.argv[1:]``.
        """
        exit_code = self.execute(**self.parse_argv(argv))

        if exit_code is None:
            exit_code = 0

        return exit_code

    def parse_argv(self, argv: Optional[tuple] = None) -> dict:
        """
        Parses arguments for the command.

        :param argv:
            Arguments to pass to the argument parser.
            If ``None``, defaults to ``sys.argv[1:]``.
        """
        arguments = vars(self.create_argument_parser().parse_args(argv))

        seed = None
        if self.requires_seed:
            seed_filepath = arguments.pop('seed_file')

            seed = (
                self.seed_from_filepath(seed_filepath)
                if seed_filepath
                else self.prompt_for_seed()
            )

        arguments['api'] = Iota(
            adapter=arguments.pop('uri'),
            seed=seed,
            devnet=arguments.pop('devnet'),
        )

        return arguments

    def create_argument_parser(self) -> ArgumentParser:
        """
        Returns the argument parser that will be used to interpret
        arguments and options from argv.
        """
        parser = ArgumentParser(
            description=self.__doc__,
            epilog='PyOTA v{version}'.format(version=__version__),
        )

        parser.add_argument(
            '--uri',
            type=str,
            default='http://localhost:14265/',

            help=(
                'URI of the node to connect to '
                '(defaults to http://localhost:14265/).'
            ),
        )

        if self.requires_seed:
            parser.add_argument(
                '--seed-file',
                type=str,
                dest='seed_file',

                help=(
                    'Path to a file containing your seed in cleartext. '
                    'If not provided, you will be prompted to enter '
                    'your seed via stdin.'
                ),
            )

        parser.add_argument(
            '--devnet',
            action='store_true',
            default=False,
            help='If set, use devnet settings (e.g., for PoW).',
        )

        return parser

    @staticmethod
    def seed_from_filepath(filepath: str) -> Seed:
        """
        Reads a seed from the first line of a text file.

        Any lines after the first are ignored.
        """
        with open(filepath, 'rb') as f_:
            return Seed(f_.readline().strip())

    @staticmethod
    def prompt_for_seed() -> Seed:
        """
        Prompts the user to enter their seed via stdin.
        """
        seed = secure_input(
            'Enter seed and press return (typing will not be shown).\n'
            'If no seed is specified, a random one will be used instead.\n'
        )

        if isinstance(seed, str):
            seed = seed.encode('ascii')

        return Seed(seed) if seed else Seed.random()
