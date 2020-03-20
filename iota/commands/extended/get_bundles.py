from typing import Iterable

import filters as f

from iota import BadApiResponse, TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.extended.traverse_bundle import TraverseBundleCommand
from iota.exceptions import with_context
from iota.transaction.validator import BundleValidator
from iota.filters import Trytes
import asyncio

__all__ = [
    'GetBundlesCommand',
]


class GetBundlesCommand(FilterCommand):
    """
    Executes ``getBundles`` extended API command.

    See :py:meth:`iota.api.Iota.get_bundles` for more info.
    """
    command = 'getBundles'

    def get_request_filter(self):
        return GetBundlesRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        transaction_hashes: Iterable[TransactionHash] = request['transactions']

        async def fetch_and_validate(tx_hash):
            bundle = (await TraverseBundleCommand(self.adapter)(
                transaction=tx_hash
            ))['bundles'][0]  # Currently 1 bundle only

            validator = BundleValidator(bundle)

            if not validator.is_valid():
                raise with_context(
                    exc=BadApiResponse(
                        'Bundle failed validation (``exc.context`` has more info).',
                    ),

                    context={
                        'bundle': bundle,
                        'errors': validator.errors,
                    },
                )

            return bundle

        # Fetch bundles asynchronously
        bundles = await asyncio.gather(
            *[fetch_and_validate(tx_hash) for tx_hash in transaction_hashes]
        )

        return {
            'bundles': bundles,
        }


class GetBundlesRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetBundlesRequestFilter, self).__init__({
            'transactions':
                f.Required | f.Array | f.FilterRepeater(
                    f.Required | Trytes(TransactionHash)
                )
        })
