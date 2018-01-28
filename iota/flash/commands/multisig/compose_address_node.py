# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Iterable

import filters as f

from iota import Address
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.crypto.types import Digest
from iota.filters import Trytes
from iota.multisig.commands import CreateMultisigAddressCommand

__all__ = [
  'ComposeAddressNodeCommand',
]


# ToDo: TEST
class ComposeAddressNodeCommand(FilterCommand):
  """
  Composes address for Flash channels
  """

  command = 'composeAddressNode'

  def get_request_filter(self):
    return ComposeAddressNodeRequestFilter()

  def get_response_filter(self):
    return ComposeAddressNodeResponseFilter()

  def _execute(self, request):
    digests = request['digests']  # type: Iterable[Digest]

    address = CreateMultisigAddressCommand(self.adapter)(digests=digests)['address']

    return {
      'address': address,
      'children': [],
      'bundles': []
    }


class ComposeAddressNodeRequestFilter(RequestFilter):
  def __init__(self):
    super(ComposeAddressNodeRequestFilter, self).__init__({
      'digests': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes(result_type=Digest))
    })


class ComposeAddressNodeResponseFilter(ResponseFilter):
  def __init__(self):
    super(ComposeAddressNodeResponseFilter, self).__init__({
      'address': f.Required | Trytes(result_type=Address),
      'children': f.Array,
      'bundles': f.Array
    })
