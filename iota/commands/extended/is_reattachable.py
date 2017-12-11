# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from iota.commands import FilterCommand

__all__ = [
  'isReattachableCommand',
]


class isReattachableCommand(FilterCommand):
  """
  Executes ``isReattachable`` extended API command.
  """
  command = 'isReattachable'

  def get_request_filter(self):
    pass

  def get_response_filter(self):
    pass

  def _execute(self, request):
    pass
