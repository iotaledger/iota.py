import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.filters import AddressNoChecksum

__all__ = [
    'WereAddressesSpentFromCommand',
]


class WereAddressesSpentFromCommand(FilterCommand):
    """
    Executes `wereAddressesSpentFrom` command.

    See :py:meth:`iota.api.StrictIota.were_addresses_spent_from`.
    """
    command = 'wereAddressesSpentFrom'

    def get_request_filter(self):
        return WereAddressesSpentFromRequestFilter()

    def get_response_filter(self):
        pass


class WereAddressesSpentFromRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(WereAddressesSpentFromRequestFilter, self).__init__({
            'addresses':
                f.Required | f.Array | f.FilterRepeater(
                    f.Required |
                    AddressNoChecksum() |
                    f.Unicode(encoding='ascii', normalize=False),
                ),
        })
