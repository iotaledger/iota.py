# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand
from iota.filters import Trytes

__all__ = [
  'GetNodeInfoCommand',
]


class GetNodeInfoCommand(FilterCommand):
  """
  Executes `getNodeInfo` command.

  :see: iota.IotaApi.get_node_info
  """
  command = 'getNodeInfo'

  def get_request_filter(self):
    # `getNodeInfo` does not accept any parameters.
    # Using a filter here just to enforce that the request is empty.
    return f.FilterMapper(
      {
      },

      allow_extra_keys    = False,
      allow_missing_keys  = False,
    )

  def get_response_filter(self):
    return f.FilterMapper(
      {
        'latestMilestone': f.ByteString(encoding='ascii') | Trytes,

        'latestSolidSubtangleMilestone':
          f.ByteString(encoding='ascii') | Trytes,
      },

      allow_extra_keys    = True,
      allow_missing_keys  = True,
    )
