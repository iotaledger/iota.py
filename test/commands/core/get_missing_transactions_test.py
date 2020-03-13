from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, TransactionHash, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core import GetMissingTransactionsCommand
from test import patch, MagicMock, async_test


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
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.core.get_missing_transactions.GetMissingTransactionsCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = Iota(self.adapter)

            response = api.get_missing_transactions()

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )

    @async_test
    async def test_wireup_async(self):
        """
        Verify that the command is wired up correctly. (async)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.core.get_missing_transactions.GetMissingTransactionsCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = AsyncIota(self.adapter)

            response = await api.get_missing_transactions()

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )