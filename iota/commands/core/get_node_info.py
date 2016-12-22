# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

__all__ = [
  'GetNodeInfoCommand',
]


class GetNodeInfoCommand(FilterCommand):
  """
  Executes `getNodeInfo` command.

  See :py:meth:`iota.api.StrictIota.get_node_info`.
  """
  command = 'getNodeInfo'

  def get_request_filter(self):
    return GetNodeInfoRequestFilter()

  def get_response_filter(self):
    return GetNodeInfoResponseFilter()


class GetNodeInfoRequestFilter(RequestFilter):
  def __init__(self):
    # `getNodeInfo` does not accept any parameters.
    # Using a filter here just to enforce that the request is empty.
    super(GetNodeInfoRequestFilter, self).__init__({})


class GetNodeInfoResponseFilter(ResponseFilter):
  def __init__(self):
    super(GetNodeInfoResponseFilter, self).__init__({
      'latestMilestone':
        f.ByteString(encoding='ascii') | Trytes(result_type=TransactionHash),

      'latestSolidSubtangleMilestone':
        f.ByteString(encoding='ascii') | Trytes(result_type=TransactionHash),
    })
