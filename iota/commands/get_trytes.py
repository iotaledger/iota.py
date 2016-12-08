# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterCommand, RequestFilter, ResponseFilter


class GetTrytesCommand(FilterCommand):
  """
  Executes ``getTrytes`` command.

  See :py:method:`iota.api.IotaApi.get_trytes`.
  """
  command = 'getTrytes'

  def get_request_filter(self):
    return GetTrytesRequestFilter()

  def get_response_filter(self):
    return GetTrytesResponseFilter()


class GetTrytesRequestFilter(RequestFilter):
  def __init__(self):
    super(GetTrytesRequestFilter, self).__init__({

    })


class GetTrytesResponseFilter(ResponseFilter):
  def __init__(self):
    super(GetTrytesResponseFilter, self).__init__({

    })
