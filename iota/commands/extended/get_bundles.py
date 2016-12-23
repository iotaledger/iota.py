# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
  'GetBundlesCommand',
]


class GetBundlesCommand(FilterCommand):
  """
  Executes ``getBundles`` extended API command.

  See :py:meth:`iota.api.Iota.get_bundles` for more info.
  """
  command = 'getBundles'

  def get_request_filter(self):
    return GetBundlesRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class GetBundlesRequestFilter(RequestFilter):
  def __init__(self):
    super(GetBundlesRequestFilter, self).__init__({
      'transaction': f.Required | Trytes(result_type=TransactionHash),
    })
