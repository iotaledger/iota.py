# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from importlib import import_module
from inspect import isabstract as is_abstract
from pkgutil import walk_packages
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, Optional, Text, Union

from filters import BaseFilter, FilterRunner
from six import with_metaclass, text_type, string_types

from iota.adapter import BaseAdapter
from iota.types import TryteString

__all__ = [
  'BaseCommand',
  'CustomCommand',
  'command_registry',
]


command_registry = {} # type: Dict[Text, CommandMeta]
"""Registry of commands, indexed by command name."""


def discover_commands(package, recursively=True):
  # type: (Union[ModuleType, Text], bool) -> None
  """
  Automatically discover commands in the specified package.

  :param package: Package path or reference.
  :param recursively: If True, will descend recursively into
    sub-packages.
  """
  # :see: http://stackoverflow.com/a/25562415/
  if isinstance(package, string_types):
    package = import_module(package) # type: ModuleType

  for _, name, is_package in walk_packages(package.__path__):
    # Loading the module is good enough; the CommandMeta metaclass will
    #   ensure that any commands in the module get registered.
    sub_package = import_module(package.__name__ + '.' + name)

    if recursively and is_package:
      discover_commands(sub_package)


class CommandMeta(ABCMeta):
  """Automatically register new commands."""
  # noinspection PyShadowingBuiltins
  def __init__(cls, what, bases=None, dict=None):
    super(CommandMeta, cls).__init__(what, bases, dict)

    if not is_abstract(cls):
      command = getattr(cls, 'command')
      if command:
        command_registry[command] = cls


class BaseCommand(with_metaclass(CommandMeta)):
  """An API command ready to send to the node."""
  command = None # Text

  def __init__(self, adapter):
    # type: (BaseAdapter) -> None
    self.adapter  = adapter

    self.called   = False
    self.request  = None # type: dict
    self.response = None # type: dict

  def __call__(self, **kwargs):
    # type: (dict) -> dict
    """Sends the command to the node."""
    if self.called:
      raise RuntimeError('Command has already been called.')

    self.request = kwargs

    replacement = self._prepare_request(self.request)
    if replacement is not None:
      self.request = replacement

    self.request['command'] = self.command

    self.response = self.adapter.send_request(self.request)

    replacement = self._prepare_response(self.response)
    if replacement is not None:
      self.response = replacement

    self.called = True

    return self.response

  @abstract_method
  def _prepare_request(self, request):
    # type: (dict) -> Optional[dict]
    """
    Modifies the request before sending it to the node.

    If this method returns a dict, it will replace the request
      entirely.

    Note:  the `command` parameter will be injected later; it is
      not necessary for this method to include it.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

  @abstract_method
  def _prepare_response(self, response):
    # type: (dict) -> Optional[dict]
    """
    Modifies the response from the node.

    If this method returns a dict, it will replace the response
      entirely.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

  @staticmethod
  def _convert_response_values(response, keys, converter):
    # type: (dict, Iterable[Text], Callable[Any, Any]) -> None
    """
    Converts non-null response values at the specified keys to the
      specified type.
    """
    for k in keys:
      value = response.get(k)
      if value is not None:
        response[k] = converter(value)

  def _convert_to_tryte_strings(self, response, keys, type_=TryteString):
    # type: (dict, Iterable[Text], type) -> None
    """
    Converts non-null response values at the specified keys to
      TryteStrings.
    """
    def converter(value):
      if isinstance(value, text_type):
        return type_(value.encode('ascii'))

      elif isinstance(value, Iterable):
        return list(map(converter, value))

    self._convert_response_values(response, keys, converter)


class CustomCommand(BaseCommand):
  """Used to execute experimental/undocumented commands."""
  def __init__(self, adapter, command):
    # type: (BaseAdapter, Text) -> None
    super(CustomCommand, self).__init__(adapter)

    self.command = command

  def _prepare_request(self, request):
    pass

  def _prepare_response(self, response):
    pass


class FilterError(ValueError):
  """
  Indicates that the request or response passed to a FilterCommand
    failed one or more filters.
  """
  def __init__(self, message, filter_runner):
    # type: (Text, FilterRunner) -> None
    super(FilterError, self).__init__(message)

    self.context = {
      'filter_errors': filter_runner.get_errors(with_context=True),
    }


class FilterCommand(with_metaclass(ABCMeta, BaseCommand)):
  """Uses filters to manipulate request/response values."""
  @abstract_method
  def get_request_filter(self):
    # type: () -> Optional[BaseFilter]
    """Returns the filter that should be applied to the request."""

  @abstract_method
  def get_response_filter(self):
    # type: () -> Optional[BaseFilter]
    """Returns the filter that should be applied to the response."""

  def _prepare_request(self, request):
    return self._apply_filter(
      value           = request,
      filter_         = self.get_request_filter(),
      failure_message = 'Request failed validation',
    )

  def _prepare_response(self, response):
    return self._apply_filter(
      value           = response,
      filter_         = self.get_response_filter(),
      failure_message = 'Response failed validation',
    )

  @staticmethod
  def _apply_filter(value, filter_, failure_message):
    if filter_:
      runner = FilterRunner(filter_, value)

      if runner.is_valid():
        return runner.cleaned_data
      else:
        raise FilterError(
          message =
            '{message} ({error_codes}) '
            '(`exc.context["filter_errors"]` '
            'contains more information).'.format(
              message     = failure_message,
              error_codes = runner.error_codes,
            ),

          filter_runner = runner,
        )

    return value


# Autodiscover commands in this package.
discover_commands(__name__)
