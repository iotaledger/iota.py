from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, BadApiResponse, Bundle, \
    Iota, AsyncIota, TransactionHash, TransactionTrytes
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class GetBundlesRequestFilterTestCase(BaseFilterTestCase):
    filter_type = GetBundlesCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    def setUp(self):
        super(GetBundlesRequestFilterTestCase, self).setUp()

        self.transactions = [
            (
                'TESTVALUE9DONTUSEINPRODUCTION99999KPZOTR'
                'VDB9GZDJGZSSDCBIX9QOK9PAV9RMDBGDXLDTIZTWQ'
            ),
            (
                'TESTVALUE9DONTUSEINPRODUCTION99999TAXQBF'
                'ZMUQLZ9RXRRXQOUSAMGAPEKTZNERIKSDYGHQA9999'
            ),
        ]

    def test_pass_happy_path(self):
        """
        Request is valid.
        """
        # Raw trytes are extracted to match the IRI's JSON protocol.
        request = {
            'transactions': self.transactions,
        }

        filter_ = self._filter(request)

        self.assertFilterPasses(filter_)
        self.assertDictEqual(filter_.cleaned_data, request)

    def test_pass_compatible_types(self):
        """
        Request contains values that can be converted to the expected
        types.
        """
        # Convert first to TranscationHash
        tx_hashes = []
        for tx in self.transactions:
            tx_hashes.append(TransactionHash(tx))

        filter_ = self._filter({
            # Any TrytesCompatible value will work here.
            'transactions': tx_hashes,
        })

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,

            {
                'transactions': self.transactions,
            },
        )

    def test_fail_empty(self):
        """
        Request is empty.
        """
        self.assertFilterErrors(
            {},

            {
                'transactions': [f.FilterMapper.CODE_MISSING_KEY],
            },
        )

    def test_fail_unexpected_parameters(self):
        """
        Request contains unexpected parameters.
        """
        self.assertFilterErrors(
            {
                'transactions': self.transactions,

                # SAY "WHAT" AGAIN!
                'what': 'augh!',
            },

            {
                'what': [f.FilterMapper.CODE_EXTRA_KEY],
            },
        )

    def test_fail_transaction_wrong_type(self):
        """
        ``transactions`` contains no TrytesCompatible value.
        """
        self.assertFilterErrors(
            {
                'transactions': [42],
            },

            {
                'transactions.0': [f.Type.CODE_WRONG_TYPE],
            },
        )

    def test_fail_transaction_not_trytes(self):
        """
        ``transactions`` contains invalid characters.
        """
        self.assertFilterErrors(
            {
                'transactions': [b'not valid; must contain only uppercase and "9"'],
            },

            {
                'transactions.0': [Trytes.CODE_NOT_TRYTES],
            },
        )

    def test_fail_no_list(self):
        """
        ``transactions`` has one hash rather than a list of hashes.
        """
        self.assertFilterErrors(
            {
                'transactions': self.transactions[0],
            },

            {
                'transactions': [f.Type.CODE_WRONG_TYPE],
            },
        )

    def test_fail_transactions_contents_invalid(self):
        """
        ``transactions`` is a non-empty array, but it contains invlaid values.
        """
        self.assertFilterErrors(
            {
                'transactions': [
                    b'',
                    True,
                    None,
                    b'not valid transaction hash',

                    # A valid tx hash, this should not produce error
                    TransactionHash(self.transactions[0]),

                    65498731,
                    b'9' * (TransactionHash.LEN +1),
                ],
            },

            {
                'transactions.0': [f.Required.CODE_EMPTY],
                'transactions.1': [f.Type.CODE_WRONG_TYPE],
                'transactions.2': [f.Required.CODE_EMPTY],
                'transactions.3': [Trytes.CODE_NOT_TRYTES],
                'transactions.5': [f.Type.CODE_WRONG_TYPE],
                'transactions.6': [Trytes.CODE_WRONG_FORMAT],
            },
        )

# Tests related to TraverseBundleCommand are moved to
# iota/test/commands/extended/traverse_bundle_test.py
# Here we only include one 'happy path' test, and focus on bundle validator
# problems.
class GetBundlesCommandTestCase(TestCase):
    def setUp(self):
        super(GetBundlesCommandTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.command = GetBundlesCommand(self.adapter)

        # Tail transaction hash
        self.tx_hash = TransactionHash(
            'TOYJPHKMLQNDVLDHDILARUJCCIUMQBLUSWPCTIVA'
            'DRXICGYDGSVPXFTILFFGAPICYHGGJ9OHXINFX9999'
        )

        self.bundle_trytes = [
            # Order is important if we don't convert to bundle representation.
            # Tail transaction should be the first.
            TransactionTrytes(
                'NBTCPCFDEACCPCBDVC9DTCQAJ9RBTC9D9DCDQAEAKDCDFD9DSCFAJ9VBCDJDTCQAJ9'
                'ZBMDYBCCKB99999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999SYRABNN9JD9PNDL'
                'IKUNCECUELTOHNLFMVD99999999999A99999999PDQWLVVDPUU9VIBODGMRIAZPGQX'
                'DOGSEXIHKIBWSLDAWUKZCZMK9Z9YZSPCKBDJSVDPRQLJSTKUMTNVSXFSEWUNJOEGNU'
                'I9QOCRFMYSIFAZLJHKZBPQZZYFG9ORYCRDX9TOMJPFCRB9R9KPUUGFPVOWYXFIWEW9'
                '999BGUEHHGAIWWQBCJZHZAQOWZMAIDAFUZBVMUVPWQJLUGGQKNKLMGTWXXNZKUCBJL'
                'EDAMYVRGABAWBY9999SYRABNN9JD9PNDLIKUNCECUELTOQZPSBDILVHJQVCEOICFAD'
                'YKZVGMOAXJRQNTCKMHGTAUMPGJJMX9LNF'
            ),

            TransactionTrytes(
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999'
                '999999999WUQXEGBVIECGIWO9IGSYKWWPYCIVUJJGSJPWGIAFJPYSF9NSQOHWAHS9P'
                '9PWQHOBXNNQIF9IRHVQXKPZW999999999999999999999999999XZUIENOTTBKJMDP'
                'RXWGQYG9PWGTHNLFMVD99A99999999A99999999PDQWLVVDPUU9VIBODGMRIAZPGQX'
                'DOGSEXIHKIBWSLDAWUKZCZMK9Z9YZSPCKBDJSVDPRQLJSTKUMTNVSXBGUEHHGAIWWQ'
                'BCJZHZAQOWZMAIDAFUZBVMUVPWQJLUGGQKNKLMGTWXXNZKUCBJLEDAMYVRGABAWBY9'
                '999MYIYBTGIOQYYZFJBLIAWMPSZEFFTXUZPCDIXSLLQDQSFYGQSQOGSPKCZNLVSZ9L'
                'MCUWVNGEN9EJEW9999XZUIENOTTBKJMDPRXWGQYG9PWGTXUO9AXMP9FLMDRMADLRPW'
                'CZCJBROYCDRJMYU9HDYJM9NDBFUPIZVTR'
            ),
        ]

        # Add a spam tx. When this is returned, traverse_bundle knows it hit a
        # different bundle and should stop.
        self.spam_trytes = TransactionTrytes(
            'SPAMSPAMSPAM999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999999999999999999'
            '999999999999999999999999999999999999999999999999999JECDITWO9999999'
            '999999999999ONLFMVD99999999999999999999VVCHSQSRVFKSBONDWB9EAQEMQOY'
            'YRBIZHTBJLYNAVDHZPUZAZ9LYHXWKBEJ9IPR9FAMFLT9EEOHVYWUPRHHSRCILCLWFD'
            'GBYBFFOKMCSAPVD9VGZZRRGBLGMZMXD9RMZQDBLMGN9BATWZGULRBCYQEIKIRBPHC9'
            '999KTLTRSYOWBD9HVNP9GCUABARNGMYXUZKXWRPGOPETZLKYYC9Z9EYXIWVARUBMBM'
            'BPXGORN9WPBLY99999ZRBVQWULRFXDNDYZKRKIXPZQT9JJJH9FZU9PVWZJWLXBPODP'
            'EHMKTTAGEPLPHUQCZNLDSHERONOMHJCOI'
        )

    def test_wireup(self):
        """
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = Iota(self.adapter)

            # Don't need to call with proper args here.
            response = api.get_bundles('transactions')

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
        with patch('iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = AsyncIota(self.adapter)

            # Don't need to call with proper args here.
            response = await api.get_bundles('transactions')

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )

    @async_test
    async def test_happy_path(self):
        """
        Get a bundle with multiple transactions.
        """
        for txn_trytes in self.bundle_trytes:
            self.adapter.seed_response('getTrytes', {
                'trytes': [txn_trytes],
            })

        self.adapter.seed_response('getTrytes', {
            'trytes': [self.spam_trytes],
        })

        response = await self.command(transactions = [self.tx_hash])

        self.maxDiff = None
        original_bundle = Bundle.from_tryte_strings(self.bundle_trytes)
        self.assertListEqual(
            response['bundles'][0].as_json_compatible(),
            original_bundle.as_json_compatible(),
        )

    @async_test
    async def test_happy_path_multiple_bundles(self):
        """
        Get two bundles with multiple transactions.
        """
        # We will fetch the same two bundle
        for _ in range(2):
            for txn_trytes in self.bundle_trytes:
                self.adapter.seed_response('getTrytes', {
                    'trytes': [txn_trytes],
                })

            self.adapter.seed_response('getTrytes', {
                'trytes': [self.spam_trytes],
            })

        response = await self.command(transactions = [self.tx_hash, self.tx_hash])

        self.maxDiff = None
        original_bundle = Bundle.from_tryte_strings(self.bundle_trytes)

        self.assertListEqual(
            response['bundles'][0].as_json_compatible(),
            original_bundle.as_json_compatible(),
        )

        self.assertListEqual(
            response['bundles'][1].as_json_compatible(),
            original_bundle.as_json_compatible(),
        )

    @async_test
    async def test_validator_error(self):
        """
        TraverseBundleCommand returns bundle but it is invalid.
        """
        # Make the returned bundle invalid
        bundle = Bundle.from_tryte_strings(self.bundle_trytes)
        bundle.transactions[0].value = 999  # Unbalanced bundle

        for txn in bundle.transactions:
            self.adapter.seed_response('getTrytes', {
                'trytes': [txn.as_tryte_string()],
        })

        self.adapter.seed_response('getTrytes', {
            'trytes': [self.spam_trytes],
        })

        with self.assertRaises(BadApiResponse):
            response = await self.command(transactions = [self.tx_hash])