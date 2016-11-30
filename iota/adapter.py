# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import json
from abc import ABCMeta, abstractmethod as abstract_method
from inspect import isabstract as is_abstract
from socket import getdefaulttimeout as get_default_timeout
from typing import Dict, Text, Tuple

import requests
from six import with_metaclass

from iota import DEFAULT_PORT

__all__ = [
  'BadApiResponse',
  'InvalidUri',
]


class BadApiResponse(ValueError):
  """
  Indicates that a non-success response was received from the node.
  """
  pass

class InvalidUri(ValueError):
  """
  Indicates that an invalid URI was provided to `resolve_adapter`.
  """
  pass


adapter_registry = {} # type: Dict[Text, BaseAdapter]
"""Keeps track of available adapters and their supported protocols."""


def resolve_adapter(uri):
  # type: (Text) -> BaseAdapter
  """Given a URI, returns a properly-configured adapter instance."""
  try:
    protocol, _ = uri.split('://', 1)
  except ValueError:
    raise InvalidUri('URI must begin with "<protocol>://" (e.g., "udp://").')

  try:
    adapter_type = adapter_registry[protocol]
  except KeyError:
    raise InvalidUri('Unrecognized protocol {protocol!r}.'.format(
      protocol = protocol,
    ))

  return adapter_type.configure(uri)


class AdapterMeta(ABCMeta):
  """
  Automatically registers new adapter classes in `adapter_registry`.
  """
  # noinspection PyShadowingBuiltins
  def __init__(cls, what, bases=None, dict=None):
    super(AdapterMeta, cls).__init__(what, bases, dict)

    if not is_abstract(cls):
      for protocol in getattr(cls, 'supported_protocols', ()):
        adapter_registry[protocol] = cls


class BaseAdapter(with_metaclass(AdapterMeta)):
  """
  Interface for IOTA API adapters.

  Adapters make it easy to customize the way an IotaApi instance
    communicates with a node.
  """
  supported_protocols = () # type: Tuple[Text]
  """
  Protocols that `resolve_adapter` can use to identify this adapter
    type.
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

  @classmethod
  def configure(cls, uri):
    # type: (Text) -> BaseAdapter
    """
    Creates a new instance using the specified URI.
    """
    return cls(uri)


class HttpAdapter(BaseAdapter):
  """
  Sends standard HTTP requests.
  """
  supported_protocols = ('udp', 'http',)

  @classmethod
  def configure(cls, uri):
    # type: (Text) -> HttpAdapter
    """
    Creates a new instance using the specified URI.

    :param uri: E.g., `udp://localhost:14265/`
    """
    try:
      protocol, config = uri.split('://', 1)
    except ValueError:
      raise InvalidUri('No protocol specified in URI {uri!r}.'.format(uri=uri))
    else:
      if protocol not in cls.supported_protocols:
        raise InvalidUri('Unsupported protocol {protocol!r}.'.format(
          protocol = protocol,
        ))

    try:
      server, path = config.split('/', 1)
    except ValueError:
      server  = config
      path    = '/'
    else:
      # Restore the '/' delimiter that we used to split the string.
      path = '/' + path

    try:
      host, port = server.split(':', 1)
    except ValueError:
      host = server

      if protocol == 'http':
        port = 80
      else:
        port = DEFAULT_PORT

    if not host:
      raise InvalidUri('Empty hostname in URI {uri!r}.'.format(uri=uri))

    try:
      port = int(port)
    except ValueError:
      raise InvalidUri('Non-numeric port in URI {uri!r}.'.format(uri=uri))

    return cls(host, port, path)


  def __init__(self, host, port=DEFAULT_PORT, path='/'):
    # type: (Text, int) -> None
    super(HttpAdapter, self).__init__()

    self.host = host
    self.port = port
    self.path = path

  @property
  def node_url(self):
    # type: () -> Text
    """Returns the node URL."""
    return 'http://{host}:{port}{path}'.format(
      host = self.host,
      port = self.port,
      path = self.path,
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