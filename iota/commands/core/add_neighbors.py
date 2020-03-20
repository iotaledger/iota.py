import filters as f

from iota.commands import FilterCommand, RequestFilter
from iota.filters import NodeUri

__all__ = [
    'AddNeighborsCommand',
]


class AddNeighborsCommand(FilterCommand):
    """
    Executes `addNeighbors` command.

    See :py:meth:`iota.api.StrictIota.add_neighbors`.
    """
    command = 'addNeighbors'

    def get_request_filter(self):
        return AddNeighborsRequestFilter()

    def get_response_filter(self):
        pass


class AddNeighborsRequestFilter(RequestFilter):
    def __init__(self) -> None:
        super(AddNeighborsRequestFilter, self).__init__({
            'uris':
                f.Required | f.Array | f.FilterRepeater(f.Required | NodeUri),
        })
