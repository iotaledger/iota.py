# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.check_consistency import CheckConsistencyCommand
from iota.filters import Trytes

__all__ = [
  'IsPromotableCommand',
]


class IsPromotableCommand(FilterCommand):
  """
  Executes ``isPromotable`` extended API command.

  See :py:meth:`iota.api.Iota.is_promotable` for more info.
  """
  command = 'isPromotable'

  def get_request_filter(self):
    return IsPromotableRequestFilter()

  def get_response_filter(self):
    pass

  def _prepare_response(self, response):
    pass

  def _execute(self, request):
    tail = request['tail'] # type: TransactionHash

    return CheckConsistencyCommand(self.adapter)(tails=[tail])['state']


class IsPromotableRequestFilter(RequestFilter):
  def __init__(self):
    super(IsPromotableRequestFilter, self).__init__({
      'tail': f.Required | Trytes(result_type=TransactionHash),
    })
