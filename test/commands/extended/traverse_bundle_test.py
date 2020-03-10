from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, BadApiResponse, Bundle, BundleHash, Fragment, Hash, \
    Iota, AsyncIota, Tag, Transaction, TransactionHash, TransactionTrytes, Nonce
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.traverse_bundle import TraverseBundleCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test

# Same tests as for GetBundlesRequestFilter (it is the same filter)
class TraverseBundleRequestFilterTestCase(BaseFilterTestCase):
    filter_type = TraverseBundleCommand(MockAdapter()).get_request_filter
    skip_value_check = True

    def setUp(self):
        super(TraverseBundleRequestFilterTestCase, self).setUp()

        self.transaction = (
            'TESTVALUE9DONTUSEINPRODUCTION99999KPZOTR'
            'VDB9GZDJGZSSDCBIX9QOK9PAV9RMDBGDXLDTIZTWQ'
        )

    def test_pass_happy_path(self):
        """
        Request is valid.
        """
        # Raw trytes are extracted to match the IRI's JSON protocol.
        request = {
            'transaction': self.transaction,
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
            # Any TrytesCompatible value will work here.
            'transaction': TransactionHash(self.transaction),
        })

        self.assertFilterPasses(filter_)
        self.assertDictEqual(
            filter_.cleaned_data,

            {
                'transaction': self.transaction,
            },
        )

    def test_fail_empty(self):
        """
        Request is empty.
        """
        self.assertFilterErrors(
            {},

            {
                'transaction': [f.FilterMapper.CODE_MISSING_KEY],
            },
        )

    def test_fail_unexpected_parameters(self):
        """
        Request contains unexpected parameters.
        """
        self.assertFilterErrors(
            {
                'transaction': TransactionHash(self.transaction),

                # SAY "WHAT" AGAIN!
                'what': 'augh!',
            },

            {
                'what': [f.FilterMapper.CODE_EXTRA_KEY],
            },
        )

    def test_fail_transaction_wrong_type(self):
        """
        ``transaction`` is not a TrytesCompatible value.
        """
        self.assertFilterErrors(
            {
                'transaction': 42,
            },

            {
                'transaction': [f.Type.CODE_WRONG_TYPE],
            },
        )

    def test_fail_transaction_not_trytes(self):
        """
        ``transaction`` contains invalid characters.
        """
        self.assertFilterErrors(
            {
                'transaction': b'not valid; must contain only uppercase and "9"',
            },

            {
                'transaction': [Trytes.CODE_NOT_TRYTES],
            },
        )


class TraverseBundleCommandTestCase(TestCase):
    def setUp(self):
        super(TraverseBundleCommandTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.command = TraverseBundleCommand(self.adapter)

    def test_wireup(self):
        """
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.extended.traverse_bundle.TraverseBundleCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = Iota(self.adapter)

            # Don't need to call with proper args here.
            response = api.traverse_bundle('tail')

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )

    @async_test
    async def test_wireup(self):
        """
        Verify that the command is wired up correctly. (async)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.extended.traverse_bundle.TraverseBundleCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = AsyncIota(self.adapter)

            # Don't need to call with proper args here.
            response = await api.traverse_bundle('tail')

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )

    @async_test
    async def test_single_transaction(self):
        """
        Getting a bundle that contains a single transaction.
        """
        transaction =\
            Transaction(
                    current_index                     = 0,
                    last_index                        = 0,
                    tag                               = Tag(b''),
                    timestamp                         = 1484960990,
                    value                             = 0,
                    attachment_timestamp              = 1484960990,
                    attachment_timestamp_lower_bound  = 12,
                    attachment_timestamp_upper_bound  = 0,

                    # These values are not relevant for 0-value transactions.
                    nonce                       = Nonce(b''),
                    signature_message_fragment  = Fragment(b''),

                    # This value is computed automatically, so it has to be real.
                    hash_ =
                        TransactionHash(
                            b'XPJIYZWPF9LBCYZPNBFARDRCSUGJGF9TWZT9K9PX'
                            b'VYDFPZOZBGXUCKLTJEUCFBEKQQ9VCSQVQDMMJQAY9',
                        ),

                    address =
                        Address(
                            b'TESTVALUE9DONTUSEINPRODUCTION99999OCSGVF'
                            b'IBQA99KGTCPCZ9NHR9VGLGADDDIEGGPCGBDEDDTBC',
                        ),

                    bundle_hash =
                        BundleHash(
                            b'TESTVALUE9DONTUSEINPRODUCTION99999DIOAZD' 
                            b'M9AIUHXGVGBC9EMGI9SBVBAIXCBFJ9EELCPDRAD9U',
                        ),

                    branch_transaction_hash =
                        TransactionHash(
                            b'TESTVALUE9DONTUSEINPRODUCTION99999BBCEDI'
                            b'ZHUDWBYDJEXHHAKDOCKEKDFIMB9AMCLFW9NBDEOFV',
                        ),

                    trunk_transaction_hash =
                        TransactionHash(
                            b'TESTVALUE9DONTUSEINPRODUCTION999999ARAYA'
                            b'MHCB9DCFEIWEWDLBCDN9LCCBQBKGDDAECFIAAGDAS',
                        ),
                )

        self.adapter.seed_response('getTrytes', {
            'trytes': [transaction.as_tryte_string()],
        })

        response = await self.command(transaction=transaction.hash)

        bundle = response['bundles'][0] # type: Bundle
        self.assertEqual(len(bundle), 1)

        self.maxDiff = None
        self.assertDictEqual(
            bundle[0].as_json_compatible(),
            transaction.as_json_compatible(),
        )

    @async_test
    async def test_multiple_transactions(self):
        """
        Getting a bundle that contains multiple transactions.
        """
        bundle = Bundle.from_tryte_strings([
            TransactionTrytes(
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999WUQXEGBVIECGIWO9IGSYKWWPYCIVUJJGSJPWGIAFJPYSF9NSQOHWAHS9P'
                b'9PWQHOBXNNQIF9IRHVQXKPZW999999999999999999999999999XZUIENOTTBKJMDP'
                b'RXWGQYG9PWGTHNLFMVD99A99999999A99999999PDQWLVVDPUU9VIBODGMRIAZPGQX'
                b'DOGSEXIHKIBWSLDAWUKZCZMK9Z9YZSPCKBDJSVDPRQLJSTKUMTNVSXBGUEHHGAIWWQ'
                b'BCJZHZAQOWZMAIDAFUZBVMUVPWQJLUGGQKNKLMGTWXXNZKUCBJLEDAMYVRGABAWBY9'
                b'999MYIYBTGIOQYYZFJBLIAWMPSZEFFTXUZPCDIXSLLQDQSFYGQSQOGSPKCZNLVSZ9L'
                b'MCUWVNGEN9EJEW9999XZUIENOTTBKJMDPRXWGQYG9PWGTXUO9AXMP9FLMDRMADLRPW'
                b'CZCJBROYCDRJMYU9HDYJM9NDBFUPIZVTR'
            ),

            # Well, it was bound to happen sooner or later... the ASCII
            # representation of this tryte sequence contains a very naughty
            # phrase.  But I don't feel like doing another POW, so... enjoy.
            TransactionTrytes(
                b'NBTCPCFDEACCPCBDVC9DTCQAJ9RBTC9D9DCDQAEAKDCDFD9DSCFAJ9VBCDJDTCQAJ9'
                b'ZBMDYBCCKB99999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999SYRABNN9JD9PNDL'
                b'IKUNCECUELTOHNLFMVD99999999999A99999999PDQWLVVDPUU9VIBODGMRIAZPGQX'
                b'DOGSEXIHKIBWSLDAWUKZCZMK9Z9YZSPCKBDJSVDPRQLJSTKUMTNVSXFSEWUNJOEGNU'
                b'I9QOCRFMYSIFAZLJHKZBPQZZYFG9ORYCRDX9TOMJPFCRB9R9KPUUGFPVOWYXFIWEW9'
                b'999BGUEHHGAIWWQBCJZHZAQOWZMAIDAFUZBVMUVPWQJLUGGQKNKLMGTWXXNZKUCBJL'
                b'EDAMYVRGABAWBY9999SYRABNN9JD9PNDLIKUNCECUELTOQZPSBDILVHJQVCEOICFAD'
                b'YKZVGMOAXJRQNTCKMHGTAUMPGJJMX9LNF'
            ),
        ])

        for txn in bundle:
            self.adapter.seed_response('getTrytes', {
                'trytes': [txn.as_tryte_string()],
            })

        self.adapter.seed_response('getTrytes', {
            'trytes': [
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
            ],
        })

        response = await self.command(
            transaction =
                TransactionHash(
                    b'TOYJPHKMLQNDVLDHDILARUJCCIUMQBLUSWPCTIVA'
                    b'DRXICGYDGSVPXFTILFFGAPICYHGGJ9OHXINFX9999'
                ),
        )
        self.maxDiff = None
        self.assertListEqual(
            response['bundles'][0].as_json_compatible(),
            bundle.as_json_compatible(),
        )

    @async_test
    async def test_non_tail_transaction(self):
        """
        Trying to get a bundle for a non-tail transaction.

        This is not valid; you have to start with a tail transaction.
        """
        self.adapter.seed_response('getTrytes', {
            'trytes': [
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999999999999999999999999999999999999999999999999999999999999'
                b'999999999WUQXEGBVIECGIWO9IGSYKWWPYCIVUJJGSJPWGIAFJPYSF9NSQOHWAHS9P'
                b'9PWQHOBXNNQIF9IRHVQXKPZW999999999999999999999999999999999999999999'
                b'999999999999HNLFMVD99A99999999A99999999PDQWLVVDPUU9VIBODGMRIAZPGQX'
                b'DOGSEXIHKIBWSLDAWUKZCZMK9Z9YZSPCKBDJSVDPRQLJSTKUMTNVSXBGUEHHGAIWWQ'
                b'BCJZHZAQOWZMAIDAFUZBVMUVPWQJLUGGQKNKLMGTWXXNZKUCBJLEDAMYVRGABAWBY9'
                b'999MYIYBTGIOQYYZFJBLIAWMPSZEFFTXUZPCDIXSLLQDQSFYGQSQOGSPKCZNLVSZ9L'
                b'MCUWVNGEN9EJEW9999XZUIENOTTBKJMDPRXWGQYG9PWGTXUO9AXMP9FLMDRMADLRPW'
                b'CZCJBROYCDRJMYU9HDYJM9NDBFUPIZVTR'
            ],
        })

        with self.assertRaises(BadApiResponse):
            await self.command(
                transaction =
                    TransactionHash(
                        b'FSEWUNJOEGNUI9QOCRFMYSIFAZLJHKZBPQZZYFG9'
                        b'ORYCRDX9TOMJPFCRB9R9KPUUGFPVOWYXFIWEW9999'
                    ),
            )

    @async_test
    async def test_missing_transaction(self):
        """
        Unable to find the requested transaction.
        """
        self.adapter.seed_response('getTrytes', {'trytes': []})

        with self.assertRaises(BadApiResponse):
            await self.command(
                transaction =
                    TransactionHash(
                        b'FSEWUNJOEGNUI9QOCRFMYSIFAZLJHKZBPQZZYFG9'
                        b'ORYCRDX9TOMJPFCRB9R9KPUUGFPVOWYXFIWEW9999'
                    ),
            )

    @async_test
    async def test_missing_transaction_zero_trytes(self):
        """
        Unable to find the requested transaction.
        getTrytes returned only zeros, no tx was found.
        """
        zero_trytes = TransactionTrytes('')
        self.adapter.seed_response('getTrytes', {'trytes': [zero_trytes]})

        with self.assertRaises(BadApiResponse):
            await self.command(
                transaction =
                    TransactionHash(
                        b'FSEWUNJOEGNUI9QOCRFMYSIFAZLJHKZBPQZZYFG9'
                        b'ORYCRDX9TOMJPFCRB9R9KPUUGFPVOWYXFIWEW9999'
                    ),
            )