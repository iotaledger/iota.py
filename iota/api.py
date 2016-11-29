# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Callable, Text

from iota.adapter import BaseAdapter

__all__ = [
  'IotaApi',
]


class IotaApi(object):
  """
  API to send HTTP requests for communicating with an IOTA node.

  :see: https://iota.readme.io/docs/getting-started
  """
  def __init__(self, adapter):
    # type: (BaseAdapter) -> None
    super(IotaApi, self).__init__()

    self.adapter = adapter # type: BaseAdapter

  def __getattr__(self, command):
    # type: (Text, dict) -> Callable[[...], dict]
    """
    Sends an arbitrary API command to the node.

    This method is useful for invoking unsupported or experimental
      methods, or if you just want to troll your node for awhile.

    :param command: The name of the command to send.

    :return: Decoded response from the node.
    :raise: BadApiResponse if the node sends back an error response.
    """
    def command_sender(**kwargs):
      return self.adapter.send_request(dict(command=command, **kwargs))
    return command_sender

  def get_node_info(self):
    """
    Returns information about the node.

    :see: https://iota.readme.io/docs/getnodeinfo
    """
    return self.__getattr__('getNodeInfo')()
