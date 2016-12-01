# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.api import BaseCommand
from iota.types import TryteString


class GetNodeInfoCommand(BaseCommand):
  """
  Executes `getNodeInfo` command.

  :see: iota.IotaApi.get_node_info
  """
  command = 'getNodeInfo'

  def _prepare_response(self, response):
    for key in ('latestMilestone', 'latestSolidSubtangleMilestone'):
      trytes = response.get(key)
      if trytes:
        response[key] = TryteString(trytes.encode('ascii'))


