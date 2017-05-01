# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterCommand, RequestFilter

__all__ = [
  'PrepareMultisigTransferCommand',
]


class PrepareMultisigTransferCommand(FilterCommand):
  """
  Implements `prepare_multisig_transfer` multisig API command.

  References:
    - :py:meth:`iota.multisig.api.MultisigIota.prepare_multisig_transfer`
  """
  command = 'prepareMultisigTransfer'

  def get_request_filter(self):
    return PrepareMultisigTransferRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class PrepareMultisigTransferRequestFilter(RequestFilter):
  def __init__(self):
    super(PrepareMultisigTransferRequestFilter, self).__init__({

    })
