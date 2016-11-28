# coding=utf-8
"""
Simple "Hello, world!" example that sends a `getNodeInfo` command to
  your friendly neighborhood node.
"""

from __future__ import absolute_import, division, print_function, \
  unicode_literals

from argparse import ArgumentParser
from pprint import pprint
from sys import argv
from typing import Text

from six import text_type as text

from iota import BadApiResponse, DEFAULT_PORT, HttpAdapter, IotaApi, \
  __version__


def main(host, port):
  # type: (Text, int) -> None
  api = IotaApi(HttpAdapter(host, port))

  try:
    node_info = api.get_node_info()
  except BadApiResponse as e:
    print("Looks like {host}:{port} isn't very talkative today ):")
    print(e)
  else:
    print('Hello {host}:{port}!'.format(host=host, port=port))
    pprint(node_info)


if __name__ == '__main__':
  parser = ArgumentParser(
    description = __doc__,
    epilog      = 'PyOTA v{version}'.format(version=__version__),
  )

  parser.add_argument(
    '--host',
      type    = text,
      default = 'localhost',

      help =
        'Hostname or IP address of the node to connect to '
        '(defaults to localhost).',
  )

  parser.add_argument(
    '--port',
      type    = int,
      default = DEFAULT_PORT,

      help = 'Port number to connect to (defaults to {default}).'.format(
        default = DEFAULT_PORT,
      ),
  )

  main(**vars(parser.parse_args(argv[1:])))
