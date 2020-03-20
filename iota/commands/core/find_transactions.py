import filters as f

from iota import BundleHash, Tag, TransactionHash
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import AddressNoChecksum, StringifiedTrytesArray, Trytes

__all__ = [
    'FindTransactionsCommand',
]


class FindTransactionsCommand(FilterCommand):
    """
    Executes `findTransactions` command.

    See :py:meth:`iota.api.StrictIota.find_transactions`.
    """
    command = 'findTransactions'

    def get_request_filter(self):
        return FindTransactionsRequestFilter()

    def get_response_filter(self):
        return FindTransactionsResponseFilter()


class FindTransactionsRequestFilter(RequestFilter):
    CODE_NO_SEARCH_VALUES = 'no_search_values'

    templates = {
        CODE_NO_SEARCH_VALUES: 'No search values specified.',
    }

    def __init__(self) -> None:
        super(FindTransactionsRequestFilter, self).__init__(
            {
                'addresses':
                    f.Array | f.FilterRepeater(
                        f.Required |
                        AddressNoChecksum() |
                        f.Unicode(encoding='ascii', normalize=False),
                    ),

                'approvees': StringifiedTrytesArray(TransactionHash),
                'bundles': StringifiedTrytesArray(BundleHash),
                'tags': StringifiedTrytesArray(Tag),
            },

            # Technically, all of the parameters for this command are
            # optional, so long as at least one of them is present and
            # not empty.
            allow_missing_keys=True,
        )

    def _apply(self, value):
        value: dict = super(FindTransactionsRequestFilter, self)._apply(
            value
        )

        if self._has_errors:
            return value

        # Remove null search terms.
        # Note: We will assume that empty lists are intentional.
        # https://github.com/iotaledger/iota.py/issues/96
        search_terms = {
            term: query
            for term, query in value.items()
            if query is not None
        }

        # At least one search term is required.
        if not search_terms:
            # Include unfiltered ``value`` in filter error context.
            return self._invalid_value(value, self.CODE_NO_SEARCH_VALUES)

        return search_terms


class FindTransactionsResponseFilter(ResponseFilter):
    def __init__(self) -> None:
        super(FindTransactionsResponseFilter, self).__init__({
            'hashes':
                f.FilterRepeater(
                    f.ByteString(encoding='ascii') |
                    Trytes(TransactionHash)
                ) |
                f.Optional(default=[]),
        })
