# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import filters as f

from iota import BadApiResponse, TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.extended.traverse_bundle import TraverseBundleCommand
from iota.exceptions import with_context
from iota.transaction.validator import BundleValidator
from iota.filters import Trytes

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

    def _execute(self, request):
        transaction_hashes = request['transactions']  # type: Iterable[TransactionHash]

        bundles = []

        # Fetch bundles one-by-one
        for tx_hash in transaction_hashes:
            bundle = TraverseBundleCommand(self.adapter)(
                transaction=tx_hash
            )['bundles'][0]  # Currently 1 bundle only

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

            bundles.append(bundle)

        return {
            'bundles': bundles,
        }

class GetBundlesRequestFilter(RequestFilter):
    def __init__(self):
        super(GetBundlesRequestFilter, self).__init__({
            'transactions':
                f.Required | f.Array | f.FilterRepeater(
                    f.Required | Trytes(TransactionHash)
                )
        })
