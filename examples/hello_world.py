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

from requests.exceptions import ConnectionError
from six import text_type

from iota import BadApiResponse, StrictIota, __version__


def main(uri):
  # type: (Text) -> None
  api = StrictIota(uri)

  try:
    node_info = api.get_node_info()
  except ConnectionError as e:
    print("Hm.  {uri} isn't responding.  Is the node running?".format(uri=uri))
    print(e)
  except BadApiResponse as e:
    print("Looks like {uri} isn't very talkative today ):".format(uri=uri))
    print(e)
  else:
    print('Hello {uri}!'.format(uri=uri))
    pprint(node_info)


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

  main(**vars(parser.parse_args(argv[1:])))
