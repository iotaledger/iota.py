# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter, ResponseFilter
from iota.filters import Trytes

__all__ = [
    'CheckConsistencyCommand',
]


class CheckConsistencyCommand(FilterCommand):
    """
    Executes ``checkConsistency`` extended API command.

    See :py:meth:`iota.api.Iota.check_consistency` for more info.
    """
    command = 'checkConsistency'

    def get_request_filter(self):
        return CheckConsistencyRequestFilter()

    def get_response_filter(self):
        return CheckConsistencyResponseFilter()


class CheckConsistencyRequestFilter(RequestFilter):
    def __init__(self):
        super(CheckConsistencyRequestFilter, self).__init__({
            'tails':
                f.Required |
                f.Array |
                f.FilterRepeater(f.Required | Trytes(TransactionHash)),
        })


class CheckConsistencyResponseFilter(ResponseFilter):
    def __init__(self):
        super(CheckConsistencyResponseFilter, self).__init__({
            'state': f.Required | f.Type(bool),
        })
