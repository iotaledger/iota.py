# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from logging import INFO, Logger

from iota.adapter import AdapterSpec, BaseAdapter, resolve_adapter
from six import with_metaclass

__all__ = [
  'LogWrapper',
]


class BaseWrapper(with_metaclass(ABCMeta)):
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
