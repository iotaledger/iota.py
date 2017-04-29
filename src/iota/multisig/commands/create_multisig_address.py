# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from iota.commands import FilterCommand, RequestFilter
from iota.crypto.types import Digest
from iota.filters import Trytes

__all__ = [
  'CreateMultisigAddressCommand',
]


class CreateMultisigAddressCommand(FilterCommand):
  """
  Implements `createMultisigAddress` multisig command.

  References:
    - :py:meth:`iota.multisig.api.MultisigIota.create_multisig_address`
  """
  command = 'createMultisigAddress'

  def get_request_filter(self):
    return CreateMultisigAddressRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    raise NotImplementedError(
      'Not implemented in {cls}.'.format(cls=type(self).__name__),
    )


class CreateMultisigAddressRequestFilter(RequestFilter):
  def __init__(self):
    super(CreateMultisigAddressRequestFilter, self).__init__({
      'digests':
          f.Required
        | f.Array
        | f.FilterRepeater(f.Required | Trytes(result_type=Digest)),
    })
