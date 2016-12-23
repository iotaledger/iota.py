# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterCommand, RequestFilter

__all__ = [
  'SendTransferCommand',
]


class SendTransferCommand(FilterCommand):
  """
  Executes ``sendTransfer`` extended API command.

  See :py:meth:`iota.api.Iota.send_transfer` for more info.
  """
  command = 'sendTransfer'

  def get_request_filter(self):
    return SendTransferRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class SendTransferRequestFilter(RequestFilter):
  def __init__(self):
    super(SendTransferRequestFilter, self).__init__(
      {

      },

      allow_missing_keys = {

      },
    )
