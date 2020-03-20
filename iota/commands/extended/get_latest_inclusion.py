from typing import List

import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.core.get_inclusion_states import GetInclusionStatesCommand
from iota.commands.core.get_node_info import GetNodeInfoCommand
from iota.filters import Trytes

__all__ = [
    'GetLatestInclusionCommand',
]


class GetLatestInclusionCommand(FilterCommand):
    """
    Executes ``getLatestInclusion`` extended API command.

    See :py:meth:`iota.api.Iota.get_latest_inclusion` for more info.
    """
    command = 'getLatestInclusion'

    def get_request_filter(self):
        return GetLatestInclusionRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        hashes: List[TransactionHash] = request['hashes']

        gni_response = await GetNodeInfoCommand(self.adapter)()

        gis_response = await GetInclusionStatesCommand(self.adapter)(
            transactions=hashes,
            tips=[gni_response['latestSolidSubtangleMilestone']],
        )

        return {
            'states': dict(zip(hashes, gis_response['states'])),
        }


class GetLatestInclusionRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(GetLatestInclusionRequestFilter, self).__init__({
            'hashes':
                f.Required | f.Array | f.FilterRepeater(
                    f.Required | Trytes(TransactionHash),
                ),
        })
