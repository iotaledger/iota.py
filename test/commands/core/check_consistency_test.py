from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, AsyncIota, TransactionHash, TryteString
from iota.adapter import MockAdapter, async_return
from iota.commands.core.check_consistency import CheckConsistencyCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class CheckConsistencyRequestFilterTestCase(BaseFilterTestCase):
    filter_type = CheckConsistencyCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    def setUp(self):
        super(CheckConsistencyRequestFilterTestCase, self).setUp()

        self.hash1 = (
            'TESTVALUE9DONTUSEINPRODUCTION99999DXSCAD'
            'YBVDCTTBLHFYQATFZPYPCBG9FOUKIGMYIGLHM9NEZ'
        )

        self.hash2 = (
            'TESTVALUE9DONTUSEINPRODUCTION99999EMFYSM'
            'HWODIAPUTTFDLQRLYIDAUIPJXXEXZZSBVKZEBWGAN'
        )

    def test_pass_happy_path(self):
        """
        Request is valid.
        """
        request = {
            # Raw trytes are extracted to match the IRI's JSON protocol.
            'tails': [self.hash1, self.hash2],
        }

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, request)

    def test_pass_compatible_types(self):
        """
        Request contains values that can be converted to the expected
        types.
        """
        filter_ = self._filter({
            'tails': [
                # Any TrytesCompatible value can be used here.
                TransactionHash(self.hash1),
                bytearray(self.hash2.encode('ascii')),
            ],
        })

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,

            {
                # Raw trytes are extracted to match the IRI's JSON protocol.
                'tails': [self.hash1, self.hash2],
            },
        )

    def test_fail_empty(self):
        """
        Request is empty.
        """
        self.assertFilterErrors(
            {},

            {
                'tails': [f.FilterMapper.CODE_MISSING_KEY],
            },
        )

    def test_fail_unexpected_parameters(self):
        """
        Request contains unexpected parameters.
        """
        self.assertFilterErrors(
            {
                'tails': [TransactionHash(self.hash1)],
                'foo': 'bar',
            },

            {
                'foo': [f.FilterMapper.CODE_EXTRA_KEY],
            },
        )

    def test_fail_tails_null(self):
        """
        ``tails`` is null.
        """
        self.assertFilterErrors(
            {
                'tails': None,
            },

            {
                'tails': [f.Required.CODE_EMPTY],
            },
        )

    def test_fail_tails_wrong_type(self):
        """
        ``tails`` is not an array.
        """
        self.assertFilterErrors(
            {
                # It's gotta be an array, even if there's only one hash.
                'tails': TransactionHash(self.hash1),
            },

            {
                'tails': [f.Type.CODE_WRONG_TYPE],
            },
        )

    def test_fail_tails_empty(self):
        """
        ``tails`` is an array, but it is empty.
        """
        self.assertFilterErrors(
            {
                'tails': [],
            },

            {
                'tails': [f.Required.CODE_EMPTY],
            },
        )

    def test_fail_tails_contents_invalid(self):
        """
        ``tails`` is a non-empty array, but it contains invalid values.
        """
        self.assertFilterErrors(
            {
                'tails': [
                    b'',
                    True,
                    None,
                    b'not valid trytes',

                    # This is actually valid; I just added it to make sure the
                    #   filter isn't cheating!
                    TryteString(self.hash1),

                    2130706433,
                    b'9' * 82,
                    ],
            },

            {
                'tails.0':  [f.Required.CODE_EMPTY],
                'tails.1':  [f.Type.CODE_WRONG_TYPE],
                'tails.2':  [f.Required.CODE_EMPTY],
                'tails.3':  [Trytes.CODE_NOT_TRYTES],
                'tails.5':  [f.Type.CODE_WRONG_TYPE],
                'tails.6':  [Trytes.CODE_WRONG_FORMAT],
            },
        )


class CheckConsistencyCommandTestCase(TestCase):
    def setUp(self):
        super(CheckConsistencyCommandTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.command = CheckConsistencyCommand(self.adapter)

        # Define some tryte sequences that we can re-use across tests.
        self.milestone = \
            TransactionHash(
                b'TESTVALUE9DONTUSEINPRODUCTION99999W9KDIH'
                b'BALAYAFCADIDU9HCXDKIXEYDNFRAKHN9IEIDZFWGJ'
            )

        self.hash1 = \
            TransactionHash(
                b'TESTVALUE9DONTUSEINPRODUCTION99999TBPDM9'
                b'ADFAWCKCSFUALFGETFIFG9UHIEFE9AYESEHDUBDDF'
            )

        self.hash2 = \
            TransactionHash(
                b'TESTVALUE9DONTUSEINPRODUCTION99999CIGCCF'
                b'KIUFZF9EP9YEYGQAIEXDTEAAUGAEWBBASHYCWBHDX'
            )

    def test_wireup(self):
        """
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.core.check_consistency.CheckConsistencyCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = Iota(self.adapter)

            response = api.check_consistency('tails')

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
        with patch('iota.commands.core.check_consistency.CheckConsistencyCommand.__call__',
                   MagicMock(return_value=async_return('You found me!'))
                  ) as mocked_command:

            api = AsyncIota(self.adapter)

            response = await api.check_consistency('tails')

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )

    @async_test
    async def test_happy_path(self):
        """
        Successfully checking consistency.
        """

        self.adapter.seed_response('checkConsistency', {
            'state': True,
        })

        response = await self.command(tails=[self.hash1, self.hash2])

        self.assertDictEqual(
            response,

            {
                'state': True,
            }
        )

    @async_test
    async def test_info_with_false_state(self):
        """
        `info` field exists when `state` is False.
        """

        self.adapter.seed_response('checkConsistency', {
            'state': False,
            'info': 'Additional information',
        })

        response = await self.command(tails=[self.hash1, self.hash2])

        self.assertDictEqual(
            response,

            {
                'state': False,
                'info': 'Additional information',
            }
        )