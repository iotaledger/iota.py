# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand, RequestFilter, ResponseFilter


class GetTransactionsToApproveCommand(FilterCommand):
  """
  Executes ``getTransactionsToApprove`` command.

  See :py:method:`iota.api.IotaApi.get_transactions_to_approve`.
  """
  command = 'getTransactionsToApprove'

  def get_request_filter(self):
    return GetTransactionsToApproveRequestFilter()

  def get_response_filter(self):
    return GetTransactionsToApproveResponseFilter()


class GetTransactionsToApproveRequestFilter(RequestFilter):
  def __init__(self):
    super(GetTransactionsToApproveRequestFilter, self).__init__({
      'depth': f.Type(int) | f.Min(1),
    })


class GetTransactionsToApproveResponseFilter(ResponseFilter):
  def __init__(self):
    super(GetTransactionsToApproveResponseFilter, self).__init__({

    })
