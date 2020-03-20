from typing import Optional

import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.crypto.types import Seed
from iota.filters import SecurityLevel, Trytes
from iota.multisig.commands.get_private_keys import GetPrivateKeysCommand

__all__ = [
    'GetDigestsCommand',
]


class GetDigestsCommand(FilterCommand):
    """
    Implements `getDigests` multisig API command.

    References:

    - :py:meth:`iota.multisig.api.MultisigIota.get_digests`
    """
    command = 'getDigests'

    def get_request_filter(self) -> 'GetDigestsRequestFilter':
        return GetDigestsRequestFilter()

    def get_response_filter(self):
        pass

    # There is no async operation going on here, but the base class is async,
    # so from the outside, we have to act like we are doing async.
    async def _execute(self, request: dict) -> dict:
        count: Optional[int] = request['count']
        index: int = request['index']
        seed: Seed = request['seed']
        security_level: int = request['securityLevel']

        gpk_result = await GetPrivateKeysCommand(self.adapter)(
            seed=seed,
            count=count,
            index=index,
            securityLevel=security_level,
        )

        return {
            'digests': [key.get_digest() for key in gpk_result['keys']],
        }


class GetDigestsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetDigestsRequestFilter, self).__init__(
            {
                # Optional Parameters
                'count': f.Type(int) | f.Min(1) | f.Optional(default=1),
                'index': f.Type(int) | f.Min(0) | f.Optional(default=0),
                'securityLevel': SecurityLevel,

                # Required Parameters
                'seed': f.Required | Trytes(Seed),
            },

            allow_missing_keys={
                'count',
                'index',
                'securityLevel',
            },
        )
