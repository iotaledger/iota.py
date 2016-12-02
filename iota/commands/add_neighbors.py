# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.api import BaseCommand


class AddNeighborsCommand(BaseCommand):
  """
  Executes `addNeighbors` command.

  :see: iota.IotaApi.add_neighbors
  """
  command = 'addNeighbors'

  def _prepare_request(self, request):
    pass

  def _prepare_response(self, response):
    pass
