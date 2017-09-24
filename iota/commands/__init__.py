# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from abc import ABCMeta, abstractmethod as abstract_method
from importlib import import_module
from inspect import getmembers as get_members, isabstract as is_abstract, \
  isclass as is_class
from pkgutil import walk_packages
from types import ModuleType
from typing import Any, Dict, Mapping, Optional, Text, Union

import filters as f
from six import string_types, with_metaclass

from iota.adapter import BaseAdapter
from iota.exceptions import with_context

__all__ = [
  'BaseCommand',
  'CustomCommand',
  'command_registry',
]

command_registry = {} # type: Dict[Text, CommandMeta]
"""
Registry of commands, indexed by command name.
"""


def discover_commands(package, recursively=True):
  # type: (Union[ModuleType, Text], bool) -> Dict[Text, 'CommandMeta']
  """
  Automatically discover commands in the specified package.

  :param package:
    Package path or reference.

  :param recursively:
    If True, will descend recursively into sub-packages.

  :return:
    All commands discovered in the specified package, indexed by
    command name (note: not class name).
  """
  # http://stackoverflow.com/a/25562415/
  if isinstance(package, string_types):
    package = import_module(package) # type: ModuleType

  commands = {}

  for _, name, is_package in walk_packages(package.__path__, package.__name__ + '.'):
    # Loading the module is good enough; the CommandMeta metaclass will
    # ensure that any commands in the module get registered.

    # Prefix in name module move to function "walk_packages" for fix
    # conflict with names importing packages
    # Bug https://github.com/iotaledger/iota.lib.py/issues/63
    sub_package = import_module(name)

    # Index any command classes that we find.
    for (_, obj) in get_members(sub_package):
      if is_class(obj) and isinstance(obj, CommandMeta):
        command_name = getattr(obj, 'command')
        if command_name:
          commands[command_name] = obj

    if recursively and is_package:
      commands.update(discover_commands(sub_package))

  return commands

class CommandMeta(ABCMeta):
  """
  Automatically register new commands.
  """
  # noinspection PyShadowingBuiltins
  def __init__(cls, what, bases=None, dict=None):
    super(CommandMeta, cls).__init__(what, bases, dict)

    if not is_abstract(cls):
      command = getattr(cls, 'command')
      if command:
        command_registry[command] = cls


class BaseCommand(with_metaclass(CommandMeta)):
  """
  An API command ready to send to the node.
  """
  command = None # Text

  def __init__(self, adapter):
    # type: (BaseAdapter, bool) -> None
    """
    :param adapter:
      Adapter that will send request payloads to the node.
    """
    self.adapter  = adapter

    self.called   = False
    self.request  = None # type: dict
    self.response = None # type: dict

  def __call__(self, **kwargs):
    # type: (**Any) -> dict
    """
    Sends the command to the node.
    """
    if self.called:
      raise with_context(
        exc = RuntimeError('Command has already been called.'),

        context = {
          'last_request':   self.request,
          'last_response':  self.response,
        },
      )

    self.request = kwargs

    replacement = self._prepare_request(self.request)
    if replacement is not None:
      self.request = replacement

    self.response = self._execute(self.request)

    replacement = self._prepare_response(self.response)
    if replacement is not None:
      self.response = replacement

    self.called = True

    return self.response

  def reset(self):
    # type: () -> None
    """
    Resets the command, allowing it to be called again.
    """
    self.called   = False
    self.request  = None # type: dict
    self.response = None # type: dict

  def _execute(self, request):
    # type: (dict) -> dict
    """
    Sends the request object to the adapter and returns the response.

    The command name will be automatically injected into the request
    before it is sent (note: this will modify the request object).
    """
    request['command'] = self.command
    return self.adapter.send_request(request)

  @abstract_method
  def _prepare_request(self, request):
    # type: (dict) -> Optional[dict]
    """
    Modifies the request before sending it to the node.

    If this method returns a dict, it will replace the request
    entirely.

    Note:  the `command` parameter will be injected later; it is
    not necessary for this method to include it.

    :param request:
      Guaranteed to be a dict, but it might be empty.
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

    :param response:
      Guaranteed to be a dict, but it might be empty.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class CustomCommand(BaseCommand):
  """
  Sends an arbitrary command to the node, with no request/response
  validation.

  Useful for executing experimental/undocumented commands.
  """
  def __init__(self, adapter, command):
    # type: (BaseAdapter, Text) -> None
    super(CustomCommand, self).__init__(adapter)

    self.command = command

  def _prepare_request(self, request):
    pass

  def _prepare_response(self, response):
    pass


class RequestFilter(f.FilterChain):
  """
  Template for filter applied to API requests.
  """
  # Be more strict about missing/extra keys for requests, since they
  # tend to come from code that the developer has control over.
  def __init__(
      self,
      filter_map,
      allow_missing_keys  = False,
      allow_extra_keys    = False,
  ):
    super(RequestFilter, self).__init__(
        f.Type(Mapping)
      | f.FilterMapper(filter_map, allow_missing_keys, allow_extra_keys)
    )

  def _apply_none(self):
    # Some commands do accept/require empty requests, but in those
    # cases, the request must be an empty object, not ``None``.
    return self._filter(None, f.Required)


class ResponseFilter(f.FilterChain):
  """
  Template for filter applied to API responses.
  """
  # Be a little looser about missing/extra keys for responses, since we
  # can't control what the node sends us back.
  def __init__(
      self,
      filter_map,
      allow_missing_keys  = True,
      allow_extra_keys    = True,
  ):
    super(ResponseFilter, self).__init__(
        f.Type(Mapping)
      | f.FilterMapper(filter_map, allow_missing_keys, allow_extra_keys)
    )

  def _apply_none(self):
    # If for some reason we don't get a response from the node, and the
    # adapter didn't complain, pretend like the response was an empty
    # object.
    return self._apply({})


class FilterCommand(with_metaclass(ABCMeta, BaseCommand)):
  """
  Uses filters to manipulate request/response values.
  """
  @abstract_method
  def get_request_filter(self):
    # type: () -> Optional[RequestFilter]
    """
    Returns the filter that should be applied to the request (if any).

    Generally, this filter should be strict about validating/converting
    the values in the request, to minimize the chance of an error
    response from the node.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

  @abstract_method
  def get_response_filter(self):
    # type: () -> Optional[ResponseFilter]
    """
    Returns the filter that should be applied to the response (if any).

    Generally, this filter should be less concerned with validation and
    more concerned with ensuring the response values have the correct
    types, since we can't control what the node sends us.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

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
    # type: (dict, Optional[f.BaseFilter], Text) -> dict
    """
    Applies a filter to a value.  If the value does not pass the
    filter, an exception will be raised with lots of contextual info
    attached to it.
    """
    if filter_:
      runner = f.FilterRunner(filter_, value)

      if runner.is_valid():
        return runner.cleaned_data
      else:
        raise with_context(
          exc = ValueError(
            '{message} ({error_codes}) '
            '(`exc.context["filter_errors"]` '
            'contains more information).'.format(
              message     = failure_message,
              error_codes = runner.error_codes,
            ),
          ),

          context = {
            'filter_errors': runner.get_errors(with_context=True),
          },
        )

    return value


# Autodiscover commands in this package.
discover_commands(__name__)
