# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from logging import INFO, Logger
from typing import Dict, Text

from six import with_metaclass

from iota.adapter import AdapterSpec, BaseAdapter, resolve_adapter

__all__ = [
  'LogWrapper',
  'RoutingWrapper',
]


class BaseWrapper(with_metaclass(ABCMeta, BaseAdapter)):
  """
  Base functionality for "adapter wrappers", used to extend the
  functionality of IOTA adapters.
  """
  def __init__(self, adapter):
    # type: (AdapterSpec) -> None
    super(BaseWrapper, self).__init__()

    if not isinstance(adapter, BaseAdapter):
      adapter = resolve_adapter(adapter)

    self.adapter = adapter # type: BaseAdapter

  @abstract_method
  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class LogWrapper(BaseWrapper):
  """
  Wrapper that sends all adapter requests and responses to a logger.

  To use it, "wrap" the real adapter instance/spec::

     logger = getLogger('...')
     api    = Iota(LogWrapper('http://localhost:14265', logger))
  """
  def __init__(self, adapter, logger, level=INFO):
    # type: (AdapterSpec, Logger, int) -> None
    super(LogWrapper, self).__init__(adapter)

    self.logger   = logger
    self.level    = level

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    command = payload.get('command') or 'command'

    self.logger.log(self.level, 'Sending {command}: {request!r}'.format(
      command = command,
      request = payload,
    ))

    response = self.adapter.send_request(payload, **kwargs)

    self.logger.log(self.level, 'Receiving {command}: {response!r}'.format(
      command   = command,
      response  = response,
    ))

    return response


class RoutingWrapper(BaseWrapper):
  """
  Routes commands to different nodes.

  This allows you to, for example, send POW requests to a local node,
  while routing all other requests to a remote one.

  Example::

     # Route POW to localhost, everything else to 12.34.56.78.
     iota = Iota(
       RoutingWrapper('http://12.34.56.78:14265')
         .add_route('attachToTangle', 'http://localhost:14265')
         .add_route('interruptAttachingToTangle', 'http://localhost:14265')
       ),
     )
  """
  def __init__(self, default_adapter):
    # type: (AdapterSpec) -> None
    """
    :param default_adapter:
      Adapter to use for any routes not listed in ``routes``.
    """
    super(RoutingWrapper, self).__init__(default_adapter)

    # Try to limit the number of distinct adapter instances we create
    # when resolving URIs.
    self.adapter_aliases = {} # type: Dict[AdapterSpec, BaseAdapter]

    self.routes = {} # type: Dict[Text, BaseAdapter]

  def add_route(self, command, adapter):
    # type: (Text, AdapterSpec) -> RoutingWrapper
    """
    Adds a route to the wrapper.

    :param command:
      The name of the command to route (e.g., "attachToTangle").

    :param adapter:
      The adapter object or URI to route requests to.
    """
    if not isinstance(adapter, BaseAdapter):
      try:
        adapter = self.adapter_aliases[adapter]
      except KeyError:
        self.adapter_aliases[adapter] = adapter = resolve_adapter(adapter)

    self.routes[command] = adapter

    return self

  def get_adapter(self, command):
    # type: (Text) -> BaseAdapter
    """
    Return the adapter for the specified command.
    """
    return self.routes.get(command, self.adapter)

  def send_request(self, payload, **kwargs):
    # type: (dict, dict) -> dict
    command = payload.get('command')

    return self.get_adapter(command).send_request(payload, **kwargs)
