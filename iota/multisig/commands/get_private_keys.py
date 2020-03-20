from typing import Optional

import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.crypto.signing import KeyGenerator
from iota.crypto.types import Seed
from iota.filters import SecurityLevel, Trytes

__all__ = [
    'GetPrivateKeysCommand',
]


class GetPrivateKeysCommand(FilterCommand):
    """
    Implements `get_private_keys` multisig API command.

    References:

      - :py:meth:`iota.multisig.MultisigIota.get_private_key`
      - https://github.com/iotaledger/wiki/blob/master/multisigs.md
    """
    command = 'getPrivateKeys'

    def get_request_filter(self) -> 'GetPrivateKeysRequestFilter':
        return GetPrivateKeysRequestFilter()

    def get_response_filter(self):
        pass

    # There is no async operation going on here, but the base class is async,
    # so from the outside, we have to act like we are doing async.
    async def _execute(self, request: dict) -> dict:
        count: Optional[int] = request['count']
        index: int = request['index']
        seed: Seed = request['seed']
        security_level: int = request['securityLevel']

        generator = KeyGenerator(seed)

        return {
            'keys': generator.get_keys(
                start=index,
                count=count,
                iterations=security_level,
            ),
        }


class GetPrivateKeysRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetPrivateKeysRequestFilter, self).__init__(
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
