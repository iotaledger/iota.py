import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.filters import StringifiedTrytesArray

__all__ = [
    'GetInclusionStatesCommand',
]


class GetInclusionStatesCommand(FilterCommand):
    """
    Executes ``getInclusionStates`` command.

    See :py:meth:`iota.api.StrictIota.get_inclusion_states`.
    """
    command = 'getInclusionStates'

    def get_request_filter(self):
        return GetInclusionStatesRequestFilter()

    def get_response_filter(self):
        pass


class GetInclusionStatesRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetInclusionStatesRequestFilter, self).__init__(
            {
                # Required parameters.
                'transactions':
                    StringifiedTrytesArray(TransactionHash) | f.Required,

                # Optional parameters.
                'tips':
                    StringifiedTrytesArray(TransactionHash) |
                    f.Optional(default=[]),
            },

            allow_missing_keys={
                'tips',
            },
        )
