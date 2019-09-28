# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, TransactionHash
from iota.adapter import MockAdapter
from iota.commands.core import GetMissingTransactionsCommand


class GetMissingTransactionsRequestFilterTestCase(BaseFilterTestCase):
    filter_type = \
        GetMissingTransactionsCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    def test_pass_empty(self):
        """
        The incoming request is (correctly) empty.
        """
        request = {}

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, request)

    def test_fail_unexpected_parameters(self):
        """
        The incoming request contains unexpected parameters.
        """
        self.assertFilterErrors(
            {
                # All you had to do was nothing!  How did you screw that up?!
                'foo': 'bar',
            },

            {
                'foo': [f.FilterMapper.CODE_EXTRA_KEY],
            },
        )


class GetMissingTransactionsResponseFilterTestCase(BaseFilterTestCase):
    filter_type = \
        GetMissingTransactionsCommand(MockAdapter()).get_response_filter
    skip_value_check = True

    # noinspection SpellCheckingInspection
    def test_no_results(self):
        """
        The incoming response contains no hashes.
        """
        response = {
            'hashes': [],
        }

        filter_ = self._filter(response)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, response)

    # noinspection SpellCheckingInspection
    def test_search_results(self):
        """
        The incoming response contains lots of hashes.
        """
        filter_ = self._filter({
            'hashes': [
                'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFW'
                'YWZRE9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVA',

                'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
                'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999',
            ],

        })

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,

            {
                'hashes': [
                    TransactionHash(
                        b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFW'
                        b'YWZRE9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVA',
                    ),

                    TransactionHash(
                        b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
                        b'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999',
                    ),
                ],

            },
        )


class GetMissingTransactionsCommandTestCase(TestCase):
    def setUp(self):
        super(GetMissingTransactionsCommandTestCase, self).setUp()

        self.adapter = MockAdapter()

    def test_wireup(self):
        """
        Verify that the command is wired up correctly.
        """
        self.assertIsInstance(
            Iota(self.adapter).getMissingTransactions,
            GetMissingTransactionsCommand,
        )
