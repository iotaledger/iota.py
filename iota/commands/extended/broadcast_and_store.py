from iota.commands import FilterCommand
from iota.commands.core.broadcast_transactions import \
    BroadcastTransactionsCommand
from iota.commands.core.store_transactions import StoreTransactionsCommand
import asyncio

__all__ = [
    'BroadcastAndStoreCommand',
]


class BroadcastAndStoreCommand(FilterCommand):
    """
    Executes ``broadcastAndStore`` extended API command.

    See :py:meth:`iota.api.Iota.broadcast_and_store` for more info.
    """
    command = 'broadcastAndStore'

    def get_request_filter(self):
        pass

    def get_response_filter(self):
        pass

    async def _execute(self, request: dict) -> dict:
        # Submit the two coroutines to the already running event loop
        await asyncio.gather(
            BroadcastTransactionsCommand(self.adapter)(**request),
            StoreTransactionsCommand(self.adapter)(**request),
        )

        return {
            'trytes': request['trytes'],
        }
