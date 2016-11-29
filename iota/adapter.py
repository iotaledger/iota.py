# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
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
  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    """
    Sends an API request to the node.

    :param payload: JSON payload.
    :param kwargs: Additional keyword arguments for the adapter.

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
    response = self._send_http_request(payload, **kwargs)

    raw_content = response.text
    if not raw_content:
      raise BadApiResponse('Empty response from node.')

    try:
      decoded = json.loads(raw_content) # type: dict
    # :bc: py2k doesn't have JSONDecodeError
    except ValueError:
      raise BadApiResponse('Non-JSON response from node: ' + raw_content)

    try:
      # Response always has 200 status, even for errors, so the only way
      #   to check for success is to inspect the response body.
      # :see: https://github.com/iotaledger/iri/issues/9
      error = decoded.get('error')
    except AttributeError:
      raise BadApiResponse('Invalid response from node: ' + raw_content)

    if error:
      raise BadApiResponse(error)

    return decoded

  def _send_http_request(self, payload, **kwargs):
    # type: (dict, dict) -> requests.Response
    """
    Sends the actual HTTP request.

    Split into its own method so that it can be mocked during unit
      tests.
    """
    kwargs.setdefault('timeout', get_default_timeout())
    return requests.post(self.node_url, json=payload, **kwargs)
