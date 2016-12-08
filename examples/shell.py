# coding=utf-8
"""Launches a Python shell with a configured API client ready to go."""

from __future__ import absolute_import, division, print_function, \
  unicode_literals

from argparse import ArgumentParser
from sys import argv
from typing import Text

from six import text_type as text

from iota import Iota, __version__


def main(uri):
  # type: (Text) -> None
  iota = Iota(uri)

  _banner = (
    'IOTA API client for {uri} initialized as variable `iota`. '
    'Type `help(iota)` for help.'.format(
      uri = uri,
    )
  )

  try:
      # noinspection PyUnresolvedReferences
      import IPython
  except ImportError:
      from code import InteractiveConsole
      InteractiveConsole(locals={'iota': iota}).interact(_banner)
  else:
    IPython.embed(header=_banner)


if __name__ == '__main__':
  parser = ArgumentParser(
    description = __doc__,
    epilog      = 'PyOTA v{version}'.format(version=__version__),
  )

  parser.add_argument(
    '--uri',
      type    = text,
      default = 'udp://localhost:14265/',

      help =
        'URI of the node to connect to '
        '(defaults to udp://localhost:14265/).',
  )

  main(**vars(parser.parse_args(argv[1:])))

