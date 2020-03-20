from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, TransactionHash, TryteString, TransactionTrytes, \
    Transaction, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.is_promotable import IsPromotableCommand, \
    get_current_ms, is_within_depth, MILESTONE_INTERVAL, ONE_WAY_DELAY
from iota.filters import Trytes
from test import mock
from test import patch, MagicMock, async_test

class IsPromotableRequestFilterTestCase(BaseFilterTestCase):
    filter_type = IsPromotableCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    def setUp(self):
        super(IsPromotableRequestFilterTestCase, self).setUp()

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


class IsPromotableCommandTestCase(TestCase):
    def setUp(self):
        super(IsPromotableCommandTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.command = IsPromotableCommand(self.adapter)

        # Define some tryte sequences that we can re-use across tests.
        self.trytes1 = TransactionTrytes(
            'CCGCVADBEACCWCXCGDEAXCGDEAPCEAHDTCGDHDEAHDFDPCBDGDPCRCHDXCCDBDE'
            'ACDBD9DMDSA9999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999ETTEXDKDEUALTLRJVX'
            'RHCPRJDLGPJCEQBJOMOAGBZWZCWLNUEWHAUSYJMYPEZPYNBTPSPGUIPQ9VOUNQ9'
            '999999999999999999999999999JVPROMOTABLETEST99999999999USHRPBD99'
            '999999999999999999XFVLEXEJPTYI9TUA9ULFNHXBGDUCOEPDIBKSZFXEBO9HF'
            'EGLENBCOVKHZ99IWZVCVSTUGKTIBEOVFBJPCDYHBDEIIBLHRVQX9KVVRTUIQMOF'
            'XUUETRIQCCCLSMVREZSNEXLIZCIUYIYRBJIBOKNJCQAJTAHGNZ9999DYHBDEIIB'
            'LHRVQX9KVVRTUIQMOFXUUETRIQCCCLSMVREZSNEXLIZCIUYIYRBJIBOKNJCQAJT'
            'AHGNZ9999ISPROMOTABLETEST9999999999999BFQOIOF999999999MMMMMMMMM'
            'EL999999999AG99999999999999'
        )

        self.hash1 = TransactionHash(
            'MHNBILKFU9CADOPNWSFYOMILGKJAHEU9GSSOYUEAPBGOOLAIKGBYSACXMFQRJZE'
            'PBSHI9SDKMBRK99999'
        )

        self.trytes2 = TransactionTrytes(
           'CCGCVADBEACCWCXCGDEAXCGDEAPCEAHDTCGDHDEAHDFDPCBDGDPCRCHDXCCDBDEA'
           'CDBD9DMDSA999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '9999999999999999999999999999999999999999999999999999999999999999'
           '99999999999ETTEXDKDEUALTLRJVXRHCPRJDLGPJCEQBJOMOAGBZWZCWLNUEWHAU'
           'SYJMYPEZPYNBTPSPGUIPQ9VOUNQ9999999999999999999999999999JVPROMOTA'
           'BLETEST99999999999USHRPBD99999999999999999999XFVLEXEJPTYI9TUA9UL'
           'FNHXBGDUCOEPDIBKSZFXEBO9HFEGLENBCOVKHZ99IWZVCVSTUGKTIBEOVFBJPCDA'
           'WCMHRLDQPBBGISNENMIXOGGYSRYXGAFEJC9FOLXLYIQVUHFCMVRPBIEAXDUYYPYN'
           'EZPHH9KB9HZ9999DAWCMHRLDQPBBGISNENMIXOGGYSRYXGAFEJC9FOLXLYIQVUHF'
           'CMVRPBIEAXDUYYPYNEZPHH9KB9HZ9999ISPROMOTABLETEST99999999999IOCFQ'
           'OIOF999999999MMMMMMMMMCAA9999999UYA99999999999999'
        )

        self.hash2 = TransactionHash(
            'FLNPRAOEYMBIXZBBFMQGCEWLRKTZTMWWTVUQRNUNMZR9EMVKETRMWHRMBFWHJHX'
            'ZOIMUWZALX9IVZ9999'
        )

        # Tuesday, October 29, 2019 4:19:43.600 PM GMT+01:00
        self.valid_now = 1572362383600
        """
        Timestamp that is just greater than the later timestamp in self.trytes.
        """

    def test_wireup(self):
        """
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.extended.is_promotable.IsPromotableCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = Iota(self.adapter)

            # Don't need to call with proper args here.
            response = api.is_promotable('tails')

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
        with patch('iota.commands.extended.is_promotable.IsPromotableCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = AsyncIota(self.adapter)

            # Don't need to call with proper args here.
            response = await api.is_promotable('tails')

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )

    @async_test
    async def test_happy_path(self):
        """
        Successfully checking promotability.
        """

        self.adapter.seed_response('checkConsistency', {
            'state': True,
        })
        self.adapter.seed_response('getTrytes', {
            'trytes': [self.trytes1, self.trytes2]
        })
        
        with mock.patch('iota.commands.extended.is_promotable.get_current_ms',
            mock.MagicMock(return_value=self.valid_now)):
            response = await self.command(tails=[self.hash1, self.hash2])

            self.assertDictEqual(
                response,

                {
                    'promotable': True,
                }
            )

    @async_test
    async def test_not_consistent(self):
        """
        One of the tails is not consistent.
        """

        self.adapter.seed_response('checkConsistency', {
            'state': False,
            'info': 'Oops, something went wrong.',
        })

        # No need for mokcing `getTrytes` becasue we should not
        # reach that part

        response = await self.command(tails=[self.hash1, self.hash2])

        self.assertDictEqual(
            response,

            {
                'promotable': False,
                'info': 'Oops, something went wrong.',
            }
        )
    
    @async_test
    async def test_one_timestamp_invalid(self):
        """
        Test invalid timestamp in one of the transactions.
        """
        # Note that self.trytes2 will have the original and
        # therefore invalid (too old) timestamp
        tx = Transaction.from_tryte_string(self.trytes1)
        tx.attachment_timestamp = get_current_ms()
        self.trytes1 = tx.as_tryte_string()

        self.adapter.seed_response('checkConsistency', {
            'state': True,
        })
        self.adapter.seed_response('getTrytes', {
            'trytes': [self.trytes1, self.trytes2]
        })

        # Here we don`t mock get_current_ms.
        # Tx 1 will have updated, passing timestamp.
        # Tx 2 has the old one, so should fail.
        response = await self.command(tails=[self.hash1, self.hash2])

        self.assertDictEqual(
            response,

            {
                'promotable': False,
                'info': ['Transaction {tx_hash} is above max depth.'.format(
                    tx_hash=self.hash2
                )],
            }
        )

    def test_is_within_depth(self):
        """
        Test ``is_within_depth`` helper method.
        """
        # Timestamp is too old (depth=6)
        now = get_current_ms()
        old_timestamp = now - (6 * MILESTONE_INTERVAL - ONE_WAY_DELAY)

        self.assertEqual(
            is_within_depth(old_timestamp, now),
            False
        )

        # Timestamp points to the future (any number would do)
        future_timestamp = now + 10

        self.assertEqual(
            is_within_depth(future_timestamp, now),
            False
        )

        # Timestamp is valid ( appr. one second 'old')
        timestamp = now - 1000

        self.assertEqual(
            is_within_depth(timestamp, now),
            True
        )