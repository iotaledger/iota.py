# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand
from iota.filters import NodeUri


class AddNeighborsCommand(FilterCommand):
  """
  Executes `addNeighbors` command.

  :see: iota.IotaApi.add_neighbors
  """
  command = 'addNeighbors'

  def get_request_filter(self):
    return f.FilterMapper(
      {
        'uris': f.Required | f.FilterRepeater(NodeUri),
      },

      allow_extra_keys    = False,
      allow_missing_keys  = False,
    )

  def get_response_filter(self):
    pass
