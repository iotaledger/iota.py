import filters as f

from iota import TransactionHash, TransactionTrytes
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes
from iota.adapter import async_return

__all__ = [
    'AttachToTangleCommand',
]


class AttachToTangleCommand(FilterCommand):
    """
    Executes ``attachToTangle`` command.

    See :py:meth:`iota.api.StrictIota.attach_to_tangle` for more info.
    """
    command = 'attachToTangle'

    def get_request_filter(self):
        return AttachToTangleRequestFilter()

    def get_response_filter(self):
        return AttachToTangleResponseFilter()

    async def _execute(self, request: dict) -> dict:
        if self.adapter.local_pow is True:
            from pow import ccurl_interface
            powed_trytes = ccurl_interface.attach_to_tangle(
                request['trytes'],
                request['branchTransaction'],
                request['trunkTransaction'],
                request['minWeightMagnitude']
            )
            return await async_return({'trytes': powed_trytes})
        else:
            return await super(FilterCommand, self)._execute(request)


class AttachToTangleRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(AttachToTangleRequestFilter, self).__init__({
            'branchTransaction': f.Required | Trytes(TransactionHash),
            'trunkTransaction': f.Required | Trytes(TransactionHash),

            'trytes':
                f.Required |
                f.Array |
                f.FilterRepeater(
                    f.Required | Trytes(result_type=TransactionTrytes),
                ),

            # Loosely-validated; devnet nodes require a different value
            # than mainnet.
            'minWeightMagnitude': f.Required | f.Type(int) | f.Min(1),
        })


class AttachToTangleResponseFilter(ResponseFilter):
    def __init__(self) -> None:
        super(AttachToTangleResponseFilter, self).__init__({
            'trytes':
                f.FilterRepeater(
                    f.ByteString(encoding='ascii') |
                    Trytes(TransactionTrytes),
                ),
        })
