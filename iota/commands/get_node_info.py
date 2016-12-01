# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.api import BaseCommand


class GetNodeInfoCommand(BaseCommand):
  """
  Executes `getNodeInfo` command.

  :see: iota.IotaApi.get_node_info
  """
  command = 'getNodeInfo'

  def _prepare_request(self, request):
    pass

  def _prepare_response(self, response):
    self._convert_to_tryte_strings(
      response  = response,
      keys      = ('latestMilestone', 'latestSolidSubtangleMilestone'),
    )


