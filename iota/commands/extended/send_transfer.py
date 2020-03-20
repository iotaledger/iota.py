from typing import List, Optional

import filters as f

from iota import Address, Bundle, ProposedTransaction, TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.extended.prepare_transfer import PrepareTransferCommand
from iota.commands.extended.send_trytes import SendTrytesCommand
from iota.crypto.types import Seed
from iota.filters import SecurityLevel, Trytes

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

    async def _execute(self, request: dict) -> dict:
        change_address: Optional[Address] = request['changeAddress']
        depth: int = request['depth']
        inputs: Optional[List[Address]] = request['inputs']
        min_weight_magnitude: int = request['minWeightMagnitude']
        seed: Seed = request['seed']
        transfers: List[ProposedTransaction] = request['transfers']
        reference: Optional[TransactionHash] = request['reference']
        security_level: int = request['securityLevel']

        pt_response = await PrepareTransferCommand(self.adapter)(
            changeAddress=change_address,
            inputs=inputs,
            seed=seed,
            transfers=transfers,
            securityLevel=security_level,
        )

        st_response = await SendTrytesCommand(self.adapter)(
            depth=depth,
            minWeightMagnitude=min_weight_magnitude,
            trytes=pt_response['trytes'],
            reference=reference,
        )

        return {
            'bundle': Bundle.from_tryte_strings(st_response['trytes']),
        }


class SendTransferRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(SendTransferRequestFilter, self).__init__(
            {
                # Required parameters.
                'depth': f.Required | f.Type(int) | f.Min(1),
                'seed': f.Required | Trytes(result_type=Seed),

                # Loosely-validated; devnet nodes require a different
                # value than mainnet.
                'minWeightMagnitude': f.Required | f.Type(int) | f.Min(1),

                'transfers':
                    f.Required | f.Array | f.FilterRepeater(
                        f.Required | f.Type(ProposedTransaction),
                    ),

                # Optional parameters.
                'changeAddress': Trytes(result_type=Address),
                'securityLevel': SecurityLevel,

                # Note that ``inputs`` is allowed to be an empty array.
                'inputs':
                    f.Array | f.FilterRepeater(f.Required | Trytes(Address)),

                'reference': Trytes(TransactionHash),
            },

            allow_missing_keys={
                'changeAddress',
                'inputs',
                'reference',
                'securityLevel',
            },
        )
