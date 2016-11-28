# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from socket import getdefaulttimeout as get_default_timeout
from typing import Text

import requests
from six import with_metaclass

from iota import DEFAULT_PORT

__all__ = [
  'BadApiResponse',
  'HttpAdapter',
]


class BadApiResponse(ValueError):
  """
  Indicates that a non-success response was received from the node.
  """
  pass


class BaseAdapter(with_metaclass(ABCMeta)):
  """
  Interface for IOTA API adapters.

  Adapters make it easy to customize the way an IotaApi instance
    communicates with a node.
  """
  @abstract_method
  def send_request(self, payload):
    # type: (dict) -> dict
    """
    Sends an API request to the node.

    :param payload: JSON payload.

    :return: Decoded response from the node.
    :raise: BadApiResponse if a non-success response was received.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class HttpAdapter(BaseAdapter):
  """
  Sends standard HTTP requests.
  """
  def __init__(self, host, port=DEFAULT_PORT):
    # type: (Text, int) -> None
    super(HttpAdapter, self).__init__()

    self.host = host
    self.port = port

  @property
  def node_url(self):
    # type: () -> Text
    """Returns the node URL."""
    return 'http://{host}:{port}/'.format(
      host = self.host,
      port = self.port,
    )

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    kwargs.setdefault('timeout', get_default_timeout())
    response = requests.post(self.node_url, json=payload, **kwargs)
    return response.json()
