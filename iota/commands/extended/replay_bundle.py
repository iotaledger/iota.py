import filters as f

from iota import Bundle, TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.commands.extended.send_trytes import SendTrytesCommand
from iota.filters import Trytes

__all__ = [
    'ReplayBundleCommand',
]


class ReplayBundleCommand(FilterCommand):
    """
    Executes ``replayBundle`` extended API command.

    See :py:meth:`iota.api.Iota.replay_bundle` for more information.
    """
    command = 'replayBundle'

    def get_request_filter(self):
        return ReplayBundleRequestFilter()

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        depth: int = request['depth']
        min_weight_magnitude: int = request['minWeightMagnitude']
        transaction: TransactionHash = request['transaction']

        gb_response = await GetBundlesCommand(self.adapter)(transactions=[transaction])

        # Note that we only replay the first bundle returned by
        # ``getBundles``.
        bundle: Bundle = gb_response['bundles'][0]

        return await SendTrytesCommand(self.adapter)(
            depth=depth,
            minWeightMagnitude=min_weight_magnitude,
            trytes=bundle.as_tryte_strings(),
        )


class ReplayBundleRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(ReplayBundleRequestFilter, self).__init__({
            'depth': f.Required | f.Type(int) | f.Min(1),
            'transaction': f.Required | Trytes(TransactionHash),

            # Loosely-validated; devnet nodes require a different value
            # than mainnet.
            'minWeightMagnitude': f.Required | f.Type(int) | f.Min(1),
        })
