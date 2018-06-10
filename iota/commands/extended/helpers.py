# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from iota.transaction.types import TransactionHash


class Helpers(object):
    """
    Adds additional helper functions that aren't part of the core or
    extended API.

    See https://github.com/iotaledger/iota.lib.py/pull/124 for more
    context.
    """

    def __init__(self, api):
        self.api = api

    def is_promotable(self, tail):
        # type: (TransactionHash) -> bool
        """
        Determines if a tail transaction is promotable.

        :param tail:
            Transaction hash. Must be a tail transaction.
        """
        return self.api.check_consistency(tails=[tail])['state']
