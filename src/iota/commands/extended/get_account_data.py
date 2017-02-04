# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterCommand

__all__ = [
  'GetAccountDataCommand',
]


class GetAccountDataCommand(FilterCommand):
  """
  Executes ``getAccountData`` extended API command.

  See :py:meth:`iota.api.Iota.get_account_data` for more info.
  """
  command = 'getAccountData'

  def get_request_filter(self):
    pass

  def get_response_filter(self):
    pass

  def _execute(self, request):
    pass
