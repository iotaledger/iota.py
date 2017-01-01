# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterCommand, RequestFilter

__all__ = [
  'GetNeighborsCommand',
]


class GetNeighborsCommand(FilterCommand):
  """
  Executes ``getNeighbors`` command.

  See :py:meth:`iota.api.StrictIota.get_neighbors`.
  """
  command = 'getNeighbors'

  def get_request_filter(self):
    return GetNeighborsRequestFilter()

  def get_response_filter(self):
    pass


class GetNeighborsRequestFilter(RequestFilter):
  def __init__(self):
    # `getNeighbors` does not accept any parameters.
    # Using a filter here just to enforce that the request is empty.
    super(GetNeighborsRequestFilter, self).__init__({})
