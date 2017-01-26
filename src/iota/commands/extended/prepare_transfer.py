# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import List, Optional

import filters as f
from iota import Address, BadApiResponse, ProposedBundle, \
  ProposedTransaction
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.get_balances import GetBalancesCommand
from iota.commands.extended.get_inputs import GetInputsCommand
from iota.commands.extended.get_new_addresses import GetNewAddressesCommand
from iota.crypto.signing import KeyGenerator
from iota.crypto.types import Seed
from iota.exceptions import with_context
from iota.filters import GeneratedAddress, Trytes

__all__ = [
  'PrepareTransferCommand',
]


class PrepareTransferCommand(FilterCommand):
  """
  Executes ``prepareTransfer`` extended API command.

  See :py:meth:`iota.api.Iota.prepare_transfer` for more info.
  """
  command = 'prepareTransfer'

  def get_request_filter(self):
    return PrepareTransferRequestFilter()

  def get_response_filter(self):
    pass

  def _execute(self, request):
    # Required parameters.
    seed      = request['seed'] # type: Seed
    bundle    = ProposedBundle(request['transfers'])

    # Optional parameters.
    change_address  = request.get('changeAddress') # type: Optional[Address]
    proposed_inputs = request.get('inputs') # type: Optional[List[Address]]

    want_to_spend = bundle.balance
    if want_to_spend > 0:
      # We are spending inputs, so we need to gather and sign them.
      if proposed_inputs is None:
        # No inputs provided.  Scan addresses for unspent inputs.
        gi_response = GetInputsCommand(self.adapter)(
          seed      = seed,
          threshold = want_to_spend,
        )

        confirmed_inputs = gi_response['inputs']
      else:
        # Inputs provided.  Check to make sure we have sufficient
        # balance.
        available_to_spend  = 0
        confirmed_inputs    = [] # type: List[Address]

        gb_response = GetBalancesCommand(self.adapter)(
          addresses = [i.address for i in proposed_inputs],
        )

        for i, balance in enumerate(gb_response.get('balances') or []):
          input_ = proposed_inputs[i]

          if balance > 0:
            available_to_spend += balance

            # Update the address balance from the API response, just in
            # case somebody tried to cheat.
            input_.balance = balance
            confirmed_inputs.append(input_)

        if available_to_spend < want_to_spend:
          raise with_context(
            exc = BadApiResponse(
              'Insufficient balance; found {found}, need {need} '
              '(``exc.context`` has more info).'.format(
                found = available_to_spend,
                need  = want_to_spend,
              ),
            ),

            context = {
              'available_to_spend': available_to_spend,
              'confirmed_inputs':   confirmed_inputs,
              'request':            request,
              'want_to_spend':      want_to_spend,
            },
          )

      bundle.add_inputs(confirmed_inputs)

      if bundle.balance < 0:
        if not change_address:
          change_address =\
            GetNewAddressesCommand(self.adapter)(seed=seed)['addresses'][0]

        bundle.send_unspent_inputs_to(change_address)

      bundle.finalize()

      if confirmed_inputs:
        bundle.sign_inputs(KeyGenerator(seed))
    else:
      bundle.finalize()

    return {
      'trytes': bundle.as_tryte_strings(),
    }


class PrepareTransferRequestFilter(RequestFilter):
  def __init__(self):
    super(PrepareTransferRequestFilter, self).__init__(
      {
        # Required parameters.
        'seed': f.Required | Trytes(result_type=Seed),

        'transfers': (
            f.Required
          | f.Array
          | f.FilterRepeater(f.Required | f.Type(ProposedTransaction))
        ),

        # Optional parameters.
        'changeAddress': Trytes(result_type=Address),

        # Note that ``inputs`` is allowed to be an empty array.
        'inputs':
          f.Array | f.FilterRepeater(f.Required | GeneratedAddress),
      },

      allow_missing_keys = {
        'changeAddress',
        'inputs',
      },
    )
