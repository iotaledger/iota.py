# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from collections import Iterable

from iota import Address, Bundle
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes
from iota.flash.commands.multisig import update_leaf_to_root
from iota.flash.types import FlashUser


class CreateFlashTransactionCommand(FilterCommand):
  """
  Helper for creating a transaction within a Flash channel
  """
  command = 'createFlashTransaction'

  def get_request_filter(self):
    return CreateFlashTransactionRequestFilter()

  def get_response_filter(self):
    pass
    # return CreateFlashTransactionResponseFilter()

  def _execute(self, request):
    user = request['user']  # type: FlashUser
    transactions = request['transactions']  # type: Iterable[dict]
    close = request['close']  # type: bool

    # From the LEAF recurse up the tree to the root
    # and find how many new addresses need to be generated if any.
    to_use, to_generate = update_leaf_to_root(root=user.flash.root)
    if to_generate != 0:
      # TODO: handle this case
      pass

    return []


class CreateFlashTransactionRequestFilter(RequestFilter):
  def __init__(self):
    super(CreateFlashTransactionRequestFilter, self).__init__({
      'user': f.Required | f.Type(FlashUser),
      'transactions': f.Required |
                      f.Array |
                      f.FilterRepeater(f.Required |
                                       f.FilterMapper({
                                         'value': f.Type(int) | f.Min(0),
                                         'address': f.Required | Trytes(result_type=Address)
                                       })),
      'close': f.Type(bool) | f.Optional(default=False)
    })


class CreateFlashTransactionResponseFilter(ResponseFilter):
  def __init__(self):
    super(CreateFlashTransactionResponseFilter, self).__init__({
      'bundles': f.Required | f.Array | f.FilterRepeater(f.Required | Trytes(result_type=Bundle))
    })
