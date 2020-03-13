from iota.commands import FilterCommand, RequestFilter

__all__ = [
    'GetNodeAPIConfigurationCommand',
]


class GetNodeAPIConfigurationCommand(FilterCommand):
    """
    Executes `getNodeAPIConfiguration` command.

    See :py:meth:`iota.api.StrictIota.get_node_api_configuration`.
    """
    command = 'getNodeAPIConfiguration'

    def get_request_filter(self):
        return GetNodeAPIConfigurationRequestFilter()

    def get_response_filter(self):
        pass


class GetNodeAPIConfigurationRequestFilter(RequestFilter):
    def __init__(self) -> None:
        # ``getNodeAPIConfiguration`` does not accept any parameters.
        # Using a filter here just to enforce that the request is empty.
        super(GetNodeAPIConfigurationRequestFilter, self).__init__({})
