from abc import ABCMeta, abstractmethod as abstract_method
from typing import Any, Mapping, Optional

import filters as f

from iota.adapter import BaseAdapter
from iota.exceptions import with_context

__all__ = [
  'BaseCommand',
  'CustomCommand',
  'FilterCommand',
  'RequestFilter',
  'ResponseFilter',
]


class BaseCommand(object, metaclass=ABCMeta):
  """
  An API command ready to send to the node.
  """
  command: str = None

  def __init__(self, adapter: BaseAdapter) -> None:
    """
    :param adapter:
      Adapter that will send request payloads to the node.
    """
    self.adapter = adapter

    self.called: bool = False
    self.request: Optional[dict] = None
    self.response: Optional[dict] = None

  async def __call__(self, **kwargs: Any) -> dict:
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

    self.response = await self._execute(self.request)

    replacement = self._prepare_response(self.response)
    if replacement is not None:
      self.response = replacement

    self.called = True

    return self.response

  def reset(self) -> None:
    """
    Resets the command, allowing it to be called again.
    """
    self.called = False
    self.request = None
    self.response = None

  async def _execute(self, request: dict) -> dict:
    """
    Sends the request object to the adapter and returns the response.

    The command name will be automatically injected into the request
    before it is sent (note: this will modify the request object).
    """
    request['command'] = self.command
    return await self.adapter.send_request(request)

  @abstract_method
  def _prepare_request(self, request: dict) -> Optional[dict]:
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
  def _prepare_response(self, response: dict) -> Optional[dict]:
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
  def __init__(self, adapter: BaseAdapter, command: str) -> None:
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


class FilterCommand(BaseCommand, metaclass=ABCMeta):
  """
  Uses filters to manipulate request/response values.
  """

  @abstract_method
  def get_request_filter(self) -> Optional[RequestFilter]:
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
  def get_response_filter(self) -> Optional[ResponseFilter]:
    """
    Returns the filter that should be applied to the response (if any).

    Generally, this filter should be less concerned with validation and
    more concerned with ensuring the response values have the correct
    types, since we can't control what the node sends us.
    """
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )

  def _prepare_request(self, request: dict) -> dict:
    return self._apply_filter(
      value           = request,
      filter_         = self.get_request_filter(),
      failure_message = 'Request failed validation',
    )

  def _prepare_response(self, response: dict) -> dict:
    return self._apply_filter(
      value           = response,
      filter_         = self.get_response_filter(),
      failure_message = 'Response failed validation',
    )

  @staticmethod
  def _apply_filter(
          value: dict,
          filter_: Optional[f.BaseFilter],
          failure_message: str
  ) -> dict:
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
