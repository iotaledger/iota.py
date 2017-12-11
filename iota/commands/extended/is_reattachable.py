# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import filters as f
from iota import Address
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

__all__ = [
  'IsReattachableCommand',
]


class IsReattachableCommand(FilterCommand):
  """
  Executes ``isReattachable`` extended API command.
  """
  command = 'isReattachable'

  def get_request_filter(self):
    return IsReattachableRequestFilter()

  def get_response_filter(self):
    return IsReattachableResponseFilter()

  def _execute(self, request):
    pass


class IsReattachableRequestFilter(RequestFilter):
  def __init__(self):
    super(IsReattachableRequestFilter, self).__init__(
      {
        'addresses': (
          f.Required
          | f.Array
          | f.FilterRepeater(
            f.Required
            | Trytes(result_type=Address)
            | f.Unicode(encoding='ascii', normalize=False)
          )
        )
      }
    )


class IsReattachableResponseFilter(ResponseFilter):
  def __init__(self):
    super(IsReattachableResponseFilter, self).__init__({
      'reattachable': (
        f.Required
        | f.Array
        | f.FilterRepeater(f.Type(bool)))
    })
