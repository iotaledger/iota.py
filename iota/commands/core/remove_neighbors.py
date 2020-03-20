import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.filters import NodeUri

__all__ = [
    'RemoveNeighborsCommand',
]


class RemoveNeighborsCommand(FilterCommand):
    """
    Executes ``removeNeighbors`` command.

    See :py:meth:`iota.api.StrictIota.remove_neighbors`.
    """
    command = 'removeNeighbors'

    def get_request_filter(self):
        return RemoveNeighborsRequestFilter()

    def get_response_filter(self):
        pass


class RemoveNeighborsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(RemoveNeighborsRequestFilter, self).__init__({
            'uris': f.Required | f.Array | f.FilterRepeater(
                f.Required |
                NodeUri,
            ),
        })
