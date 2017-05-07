# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f
from iota import Address, ProposedTransaction
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core import GetBalancesCommand
from iota.exceptions import with_context
from iota.filters import Trytes
from iota.multisig.transaction import ProposedMultisigBundle
from iota.multisig.types import MultisigAddress

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
    change_address  = request['changeAddress'] # type: Optional[Address]
    multisig_input  = request['multisigInput'] # type: MultisigAddress
    transfers       = request['transfers'] # type: List[ProposedTransaction]

    bundle = ProposedMultisigBundle(transfers)

    want_to_spend = bundle.balance
    if want_to_spend > 0:
      gb_response =\
        GetBalancesCommand(self.adapter)(
          addresses = [multisig_input],
        )

      multisig_input.balance = gb_response['balances'][0]

      if multisig_input.balance < want_to_spend:
        raise with_context(
          exc =
            ValueError(
              'Insufficient balance; found {found}, need {need} '
              '(``exc.context`` has more info).'.format(
                found = multisig_input.balance,
                need  = want_to_spend,
              ),
            ),

          # The structure of this context object is intended to match
          # the one from ``PrepareTransferCommand``.
          context = {
            'available_to_spend': multisig_input.balance,
            'confirmed_inputs':   multisig_input,
            'request':            request,
            'want_to_spend':      want_to_spend,
          },
        )

      bundle.add_inputs([multisig_input])

      if bundle.balance < 0:
        if change_address:
          bundle.send_unspent_inputs_to(change_address)
    else:
      raise with_context(
        exc =
          ValueError(
            'Use ``prepare_transfer`` '
            'to create a bundle without spending IOTAs.',
          ),

        context = request,
      )

    bundle.finalize()

    # Return the bundle with inputs unsigned.
    return {
      'bundle': bundle,
    }


class PrepareMultisigTransferRequestFilter(RequestFilter):
  def __init__(self):
    super(PrepareMultisigTransferRequestFilter, self).__init__(
      {
        'changeAddress':
          Trytes(result_type=Address),

        'multisigInput':
            f.Required
          | f.Type(MultisigAddress),

        'transfers':
            f.Required
          | f.Array
          | f.FilterRepeater(f.Required | f.Type(ProposedTransaction)),
      },

      allow_missing_keys = {
        'changeAddress',
      },
    )
