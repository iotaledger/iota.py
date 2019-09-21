# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import filters as f

from iota.commands import FilterCommand, RequestFilter, ResponseFilter

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
        return GetNodeAPIConfigurationResponseFilter()


class GetNodeAPIConfigurationRequestFilter(RequestFilter):
    def __init__(self):
        # ``getNodeAPIConfiguration`` does not accept any parameters.
        # Using a filter here just to enforce that the request is empty.
        super(GetNodeAPIConfigurationRequestFilter, self).__init__({})


class GetNodeAPIConfigurationResponseFilter(ResponseFilter):
    def __init__(self):
        super(GetNodeAPIConfigurationResponseFilter, self).__init__({
            'maxFindTransactions': f.Type(int),
            'maxRequestsList': f.Type(int),
            'maxGetTrytes': f.Type(int),
            'maxBodyLength': f.Type(int),
            'testNet': f.Type(bool),
            'milestoneStartIndex': f.Type(int),
        })
