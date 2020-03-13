from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, Iota, TryteString, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.get_balances import GetBalancesCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class GetBalancesRequestFilterTestCase(BaseFilterTestCase):
    filter_type = GetBalancesCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    def setUp(self):
        super(GetBalancesRequestFilterTestCase, self).setUp()

        # Define a few valid values that we can reuse across tests.
        self.trytes1 = (
            'TESTVALUE9DONTUSEINPRODUCTION99999EKJZZT'
            'SOGJOUNVEWLDPKGTGAOIZIPMGBLHC9LMQNHLGXGYX'
        )

        self.trytes2 = (
            'TESTVALUE9DONTUSEINPRODUCTION99999FDCDTZ'
            'ZWLL9MYGUTLSYVSIFJ9NGALTRMCQVIIOVEQOITYTE'
        )

        self.trytes3 = (
            'TESTVALUE9DONTUSEINPRODUCTION99999FDCDTZ'
            'ASKDFJWOEFJSKLDJFWEIOFFJSKDJFWIOEFJSKDF9E'
        )

    def test_pass_happy_path(self):
        """
        Typical invocation of ``getBalances``.
        """
        request = {
            # Raw trytes are extracted to match the IRI's JSON protocol.
            'addresses': [self.trytes1, self.trytes2],

            'threshold': 80,
        }

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, request)

    def test_pass_happy_path_with_tips(self):
        """
        Typical invocation of ``getBalances`` with tips.
        """
        request = {
            'addresses': [self.trytes1, self.trytes2],

            'threshold': 80,

            'tips': [self.trytes3],
        }

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, request)

    def test_pass_compatible_types(self):
        """
        The incoming request contains values that can be converted to the
        expected types.
        """
        request = {
            'addresses': [
                Address(self.trytes1),
                bytearray(self.trytes2.encode('ascii')),
            ],

            'threshold': 80,
        }

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,

            {
                'addresses': [self.trytes1, self.trytes2],
                'threshold': 80,
            },
        )

    def test_pass_threshold_optional(self):
        """
        The incoming request does not contain a ``threshold`` value, so the
        default value is assumed.
        """
        request = {
            'addresses': [Address(self.trytes1)],
        }

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,

            {
                'addresses': [Address(self.trytes1)],
                'threshold': 100,
            },
        )

    def test_fail_empty(self):
        """
        The incoming request is empty.
        """
        self.assertFilterErrors(
            {},

            {
                'addresses': [f.FilterMapper.CODE_MISSING_KEY],
            },
        )

    def test_fail_unexpected_parameters(self):
        """
        The incoming request contains unexpected parameters.
        """
        self.assertFilterErrors(
            {
                'addresses': [Address(self.trytes1)],

                # I've had a perfectly wonderful evening.
                # But this wasn't it.
                'foo': 'bar',
            },

            {
                'foo': [f.FilterMapper.CODE_EXTRA_KEY],
            },
        )

    def test_fail_addresses_wrong_type(self):
        """
        ``addresses`` is not an array.
        """
        self.assertFilterErrors(
            {
                'addresses': Address(self.trytes1),
            },

            {
                'addresses': [f.Type.CODE_WRONG_TYPE],
            },
        )

    def test_fail_addresses_empty(self):
        """
        ``addresses`` is an array, but it's empty.
        """
        self.assertFilterErrors(
            {
                'addresses': [],
            },

            {
                'addresses': [f.Required.CODE_EMPTY],
            },
        )

    def test_fail_addresses_contents_invalid(self):
        """
        ``addresses`` is an array, but it contains invalid values.
        """
        self.assertFilterErrors(
            {
                'addresses': [
                    b'',
                    True,
                    None,
                    b'not valid trytes',

                    # This is actually valid; I just added it to make sure the
                    # filter isn't cheating!
                    TryteString(self.trytes2),

                    2130706433,
                    b'9' * 82,
                    ],
            },

            {
                'addresses.0':  [f.Required.CODE_EMPTY],
                'addresses.1':  [f.Type.CODE_WRONG_TYPE],
                'addresses.2':  [f.Required.CODE_EMPTY],
                'addresses.3':  [Trytes.CODE_NOT_TRYTES],
                'addresses.5':  [f.Type.CODE_WRONG_TYPE],
                'addresses.6':  [Trytes.CODE_WRONG_FORMAT],
            },
        )

    def test_fail_threshold_float(self):
        """
        `threshold` is a float.
        """
        self.assertFilterErrors(
            {
                # Even with an empty fpart, floats are not accepted.
                'threshold': 86.0,

                'addresses': [Address(self.trytes1)],
            },

            {
                'threshold': [f.Type.CODE_WRONG_TYPE],
            },
        )

    def test_fail_threshold_string(self):
        """
        ``threshold`` is a string.
        """
        self.assertFilterErrors(
            {
                'threshold': '86',

                'addresses': [Address(self.trytes1)],
            },

            {
                'threshold': [f.Type.CODE_WRONG_TYPE],
            },
        )

    def test_fail_threshold_too_small(self):
        """
        ``threshold`` is less than 0.
        """
        self.assertFilterErrors(
            {
                'threshold': -1,

                'addresses': [Address(self.trytes1)],
            },

            {
                'threshold': [f.Min.CODE_TOO_SMALL],
            },
        )

    def test_fail_threshold_too_big(self):
        """
        ``threshold`` is greater than 100.
        """
        self.assertFilterErrors(
            {
                'threshold': 101,

                'addresses': [Address(self.trytes1)],
            },

            {
                'threshold': [f.Max.CODE_TOO_BIG],
            },
        )

    def test_fail_tips_contents_invalid(self):
        """
        ``tips`` is an array, but it contains invalid values.
        """
        self.assertFilterErrors(
            {
                'addresses': [self.trytes1],
                'tips': [
                    b'',
                    True,
                    None,
                    b'not valid trytes',

                    # This is actually valid; I just added it to make sure the
                    # filter isn't cheating!
                    TryteString(self.trytes2),

                    2130706433,
                    b'9' * 82,
                    ],
            },

            {
                'tips.0':  [f.Required.CODE_EMPTY],
                'tips.1':  [f.Type.CODE_WRONG_TYPE],
                'tips.2':  [f.Required.CODE_EMPTY],
                'tips.3':  [Trytes.CODE_NOT_TRYTES],
                'tips.5':  [f.Type.CODE_WRONG_TYPE],
                'tips.6':  [Trytes.CODE_WRONG_FORMAT],
            },
        )


class GetBalancesResponseFilterTestCase(BaseFilterTestCase):
    filter_type = GetBalancesCommand(MockAdapter()).get_response_filter
    skip_value_check = True

    def setUp(self):
        super(GetBalancesResponseFilterTestCase, self).setUp()

        # Define a few valid values that we can reuse across tests.
        self.trytes1 = (
            'TESTVALUE9DONTUSEINPRODUCTION99999EKJZZT'
            'SOGJOUNVEWLDPKGTGAOIZIPMGBLHC9LMQNHLGXGYX'
        )

    def test_balances(self):
        """
        Typical ``getBalances`` response.
        """
        filter_ = self._filter({
            'balances':       ['114544444', '0', '8175737'],
            'duration':       42,
            'milestoneIndex': 128,
            'references':     [self.trytes1]
        })

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,

            {
                'balances':       [114544444, 0, 8175737],
                'duration':       42,
                'milestoneIndex': 128,
                'references':     [self.trytes1]
            },
        )


class GetBalancesCommandTestCase(TestCase):
    def setUp(self):
        super(GetBalancesCommandTestCase, self).setUp()

        self.adapter = MockAdapter()

    def test_wireup(self):
        """
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.core.get_balances.GetBalancesCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = Iota(self.adapter)

            response = api.get_balances('addresses')

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
        with patch('iota.commands.core.get_balances.GetBalancesCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = AsyncIota(self.adapter)

            response = await api.get_balances('addresses')

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )