from unittest import TestCase
from iota.commands.extended.utils import iter_used_addresses, \
    get_bundles_from_transaction_hashes
from iota.adapter import MockAdapter, async_return
from iota.crypto.types import Seed
from test import mock, async_test, MagicMock
from iota import TransactionTrytes, TransactionHash, Bundle, BadApiResponse


class IterUsedAddressesTestCase(TestCase):
    def setUp(self):
        super(IterUsedAddressesTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.seed = Seed(trytes='S' * 81)
        self.address0 = 'A' * 81
        self.address1 = 'B' * 81
        self.address2 = 'C' * 81
        self.address3 = 'D' * 81

        # To speed up the tests, we will mock the address generator.
        def address_generator(ag, start, step=1):
            for addy in [self.address0, self.address1, self.address2,
                         self.address3][start::step]:
                yield addy
        self.mock_address_generator = address_generator

    def seed_unused_address(self):
        self.adapter.seed_response('findTransactions', {
            'hashes': [],
        })
        self.adapter.seed_response('wereAddressesSpentFrom', {
            'states': [False],
        })

    async def get_all_used_addresses(self, start=0):
        # `iter_used_addresses` is an async generator, so we have to use `async for`
        return [address async for address, _
                in iter_used_addresses(self.adapter, self.seed, start)]

    @async_test
    async def test_first_address_is_not_used(self):
        """
        The very first address is not used. No address is returned.
        """
        # Address 0
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([], await self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address0],
                },
            ]
        )

    @async_test
    async def test_transactions_are_considered_used(self):
        """
        An address with a transaction is considered used.
        """
        # Address 0
        self.adapter.seed_response('findTransactions', {
            'hashes': ['T' * 81],
        })

        # Address 1
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address0], await self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address1],
                },
            ]
        )

    @async_test
    async def test_spent_from_is_considered_used(self):
        """
        An address that was spent from is considered used.
        """
        # Address 0
        self.adapter.seed_response('findTransactions', {
            'hashes': [],
        })
        self.adapter.seed_response('wereAddressesSpentFrom', {
            'states': [True],
        })

        # Address 1
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address0], await self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address0],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address1],
                },
            ]
        )

    @async_test
    async def test_start_parameter_is_given(self):
        """
        The correct address is returned if a start parameter is given.
        """
        # Address 1
        self.adapter.seed_response('findTransactions', {
            'hashes': ['T' * 81],
        })

        # Address 2
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address1],
                             await self.get_all_used_addresses(start=1))

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address2],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address2],
                },
            ]
        )

    @async_test
    async def test_multiple_addresses_return(self):
        """
        A larger test that combines multiple cases and more than one address
        should be returned.
        Address 0: Was spent from
        Address 1: Has a transaction
        Address 2: Is not used. Should not be returned
        """

        # Address 0
        self.adapter.seed_response('findTransactions', {
            'hashes': [],
        })
        self.adapter.seed_response('wereAddressesSpentFrom', {
            'states': [True],
        })

        # Address 1
        self.adapter.seed_response('findTransactions', {
            'hashes': ['T' * 81],
        })

        # Address 2
        self.seed_unused_address()

        with mock.patch(
                'iota.crypto.addresses.AddressGenerator.create_iterator',
                self.mock_address_generator,
        ):
            self.assertEqual([self.address0, self.address1],
                             await self.get_all_used_addresses())

        self.assertListEqual(
            self.adapter.requests,
            [
                {
                    'command': 'findTransactions',
                    'addresses': [self.address0],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address0],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address1],
                },
                {
                    'command': 'findTransactions',
                    'addresses': [self.address2],
                },
                {
                    'command': 'wereAddressesSpentFrom',
                    'addresses': [self.address2],
                },
            ]
        )


class GetBundlesFromTransactionHashesTestCase(TestCase):
    def setUp(self) -> None:
        # Need two valid bundles
        super().setUp()
        self.adapter = MockAdapter()

        self.single_bundle = Bundle.from_tryte_strings([
            TransactionTrytes(
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
                '999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999POALVTTGQHJFGINKJ9'
                'EWRJZBQLLWMMNMNRUT9VFWDDMDWHPJMNDOFZXUQUABGCXZRH9OI9NWEUSHVYXDO'
                '999999999999999999999999999C99999999999999999999999999RIGEHBD99'
                '999999999999999999RPCKQTYDOV9IYVYYALBTBLHRFCLFMTCC9ZLOKKGENTDFY'
                'COKFUITXUIUJLBNWAEKBJKBYDSRLVHSGELCCCZGNHCYEAKJ9OPRZFIBYEEBTRFT'
                'QTWJUKRDKNSEESICPJRTDNZQQYNXOFVXI9CPRNBO9APJMEXATA9999CZGNHCYEA'
                'KJ9OPRZFIBYEEBTRFTQTWJUKRDKNSEESICPJRTDNZQQYNXOFVXI9CPRNBO9APJM'
                'EXATA9999C99999999999999999999999999FQFFNIHPF999999999MMMMMMMMM'
                'BCDJOVFVODAQEPAXIWDRFKCTOFI'
            )
        ])

        self.three_tx_bundle = Bundle.from_tryte_strings(([
            TransactionTrytes(
                'PBXCFDGDHDEAHDFDPCBDGDPCRCHDXCCDBDEAXCBDEAHDWCTCEAQCIDBDSC9DTCS'
                'A99999999999999999999999999999999999999999999999999999999999999'
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
                '999999999999999999999999999999999999999999999M9OVNPOWKUNQYDHFN9'
                'YAL9WIQJDVAFKBU9ZPIHSGTZLGFJODRZINZMDALS9ERTNAJ9VTENWYLBSYALQQL'
                '999999999999999999999999999EYOTA9TESTS9999999999999999BOPIHBD99'
                '999999999B99999999JWFDGHYGEQIKSPCWEAHHQACOYHQWINSA9GELCEZNQEUHV'
                'DH9UAYJVSTIIKW9URTHHIJYGWXGE9AEWISYWZSLPKSJETGKZEQVPISQSNDHIAXQ'
                'RZVFJXFOXZAVMRUGALCQRHUEZPDFNLCIKQGWEKDJURLZLMUZVA99999BSJCSWTG'
                'RTJSGZPOXRPICUDATCLCVTF9BEDHSZZRLSH9IRMTFRVAMSSHC9TRYZGHPWRDVTX'
                'EXWTZ9999PYOTA9TESTS9999999999999999OSZRBMHPF999999999MMMMMMMMM'
                'IVL9PTSTAIRGJLGXFQGIWOJHBKF'
            ),
            TransactionTrytes(
                'BCTCRCCDBDSCEAHDFDPCBDGDPCRCHDXCCDBDEAXCBDEAHDWCTCEAQCIDBDSC9DT'
                'CSA999999999999999999999999999999999999999999999999999999999999'
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
                '999999999999999999999999999999999999999999999LSTTHILAJWQEXWVOJQ'
                'GRANRLNHQLKYXVQFBYJ9QDFRISQR9WJYMSSZUBOCVLXF9TACHKGQUEGMJPICXVY'
                '999999999999999999999999999PYOTA9TESTS9999999999999999BOPIHBD99'
                'A99999999B99999999JWFDGHYGEQIKSPCWEAHHQACOYHQWINSA9GELCEZNQEUHV'
                'DH9UAYJVSTIIKW9URTHHIJYGWXGE9AEWISYWQQAWNWHDSGZWFTKTYSV99PJIFFM'
                'OPFWONAOTRBUEDGLORTHNMXM9EZNILYEIWCQIAVMAGDBHYWWOA99999BSJCSWTG'
                'RTJSGZPOXRPICUDATCLCVTF9BEDHSZZRLSH9IRMTFRVAMSSHC9TRYZGHPWRDVTX'
                'EXWTZ9999PYOTA9TESTS9999999999999999EMSRBMHPF999999999MMMMMMMMM'
                'NXTVOIJXAAJUS9SRVJEVDVOSIUE'
            ),
            TransactionTrytes(
                'CCWCXCFDSCEAHDFDPCBDGDPCRCHDXCCDBDEAXCBDEAHDWCTCEAQCIDBDSC9DTCS'
                'A99999999999999999999999999999999999999999999999999999999999999'
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
                '999999999999999999999999999999999999999999999FSXLFSGAHTGSFPK9FH'
                'HURWZJAWQDQCRIFUHMSZWUTNRAIDNGEHGPHLNJOEAIDGLYQRCYSCYDTBZQFDGQK'
                '999999999999999999999999999PYOTA9TESTS9999999999999999BOPIHBD99'
                'B99999999B99999999JWFDGHYGEQIKSPCWEAHHQACOYHQWINSA9GELCEZNQEUHV'
                'DH9UAYJVSTIIKW9URTHHIJYGWXGE9AEWISYW9BSJCSWTGRTJSGZPOXRPICUDATC'
                'LCVTF9BEDHSZZRLSH9IRMTFRVAMSSHC9TRYZGHPWRDVTXEXWTZ99999BSJCSWTG'
                'RTJSGZPOXRPICUDATCLCVTF9BEDHSZZRLSH9IRMTFRVAMSSHC9TRYZGHPWRDVTX'
                'EXWTZ9999PYOTA9TESTS9999999999999999LUSRBMHPF999999999MMMMMMMMM'
                'BOCWSYQAKMZXDR9ZPHXTXZORELC'
            ),
        ]))

    @async_test
    async def test_happy_path(self):
        """
        A bundle is successfully fetched with inclusion state.
        """
        self.adapter.seed_response(
                'getTrytes',
                {
                    'trytes': self.single_bundle.as_tryte_strings()
                }
        )

        with mock.patch(
                'iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand.__call__',
                MagicMock(return_value=async_return({
                    'states': {self.single_bundle.tail_transaction.hash: True}}))
        ) as mocked_glis:
            with mock.patch(
                'iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
                MagicMock(return_value=async_return({'bundles': [self.single_bundle]}))
            ) as mocked_get_bundles:
                response = await get_bundles_from_transaction_hashes(
                        adapter=self.adapter,
                        transaction_hashes=[self.single_bundle.tail_transaction.hash],
                        inclusion_states=True,
                )

                self.assertListEqual(
                        response,
                        [self.single_bundle],
                )

                mocked_glis.assert_called_once_with(
                        hashes=[self.single_bundle.tail_transaction.hash]
                )

                mocked_get_bundles.assert_called_once_with(
                        transactions=[self.single_bundle.tail_transaction.hash]
                )

                self.assertTrue(
                        response[0].is_confirmed
                )

    @async_test
    async def test_happy_path_no_inclusion(self):
        """
        A bundle is successfully fetched without inclusion states.
        """
        self.adapter.seed_response(
                'getTrytes',
                {
                    'trytes': self.single_bundle.as_tryte_strings()
                }
        )

        with mock.patch(
                'iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand.__call__',
                MagicMock(return_value=async_return({'states': {
                    self.single_bundle.tail_transaction.hash: True
                }}))
        ) as mocked_glis:
            with mock.patch(
                'iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
                MagicMock(return_value=async_return({'bundles': [self.single_bundle]}))
            ) as mocked_get_bundles:
                response = await get_bundles_from_transaction_hashes(
                        adapter=self.adapter,
                        transaction_hashes=[self.single_bundle.tail_transaction.hash],
                        inclusion_states=False,
                )

                self.assertListEqual(
                        response,
                        [self.single_bundle],
                )

                self.assertFalse(
                        mocked_glis.called
                )

                mocked_get_bundles.assert_called_once_with(
                        transactions=[self.single_bundle.tail_transaction.hash]
                )

                self.assertFalse(
                        response[0].is_confirmed
                )

    @async_test
    async def test_empty_list(self):
        """
        Called with empty list of hashes.
        """
        response = await get_bundles_from_transaction_hashes(
                adapter=self.adapter,
                transaction_hashes=[],
                inclusion_states=True,
        )

        self.assertListEqual(
                response,
                []
        )

    @async_test
    async def test_no_transaction_trytes(self):
        """
        Node doesn't have the requested transaction trytes.
        """
        self.adapter.seed_response(
                'getTrytes',
                {
                    'trytes': [
                        self.single_bundle.tail_transaction.as_tryte_string(),
                        TransactionTrytes(''),
                    ]
                }
        )
        with self.assertRaises(BadApiResponse):
            response = await get_bundles_from_transaction_hashes(
                    adapter=self.adapter,
                    transaction_hashes=[
                        self.single_bundle.tail_transaction.hash,
                        TransactionHash('')
                    ],
                    inclusion_states=False,
            )

    @async_test
    async def test_multiple_tail_transactions(self):
        """
        Multiple tail transactions are requested.
        """
        self.adapter.seed_response(
                'getTrytes',
                {
                    'trytes': [
                        self.single_bundle.tail_transaction.as_tryte_string(),
                        self.three_tx_bundle.tail_transaction.as_tryte_string(),
                    ]
                }
        )

        with mock.patch(
                'iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand.__call__',
                MagicMock(return_value=async_return({'states': {
                    self.single_bundle.tail_transaction.hash: True,
                    self.three_tx_bundle.tail_transaction.hash: True
                }}))
        ) as mocked_glis:
            with mock.patch(
                'iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
                MagicMock(return_value=async_return({
                    'bundles': [
                        self.single_bundle,
                        self.three_tx_bundle,
                    ]
                }))
            ) as mocked_get_bundles:
                response = await get_bundles_from_transaction_hashes(
                        adapter=self.adapter,
                        transaction_hashes=[
                            self.single_bundle.tail_transaction.hash,
                            self.three_tx_bundle.tail_transaction.hash
                        ],
                        inclusion_states=True,
                )

                self.assertListEqual(
                        response,
                        [
                            self.single_bundle,
                            self.three_tx_bundle,
                        ],
                )

                # Check if it was called only once
                mocked_glis.assert_called_once()

                # Get the keyword arguments from that call
                _, _, mocked_glis_kwargs = mocked_glis.mock_calls[0]

                # 'hashes' keyword's value should be a list of hashes it was called
                # with. Due to the set -> list conversion in the src code, we can't
                # be sure of the order of the elements, so we check by value.
                self.assertCountEqual(
                        mocked_glis_kwargs.get('hashes'),
                        [
                            self.three_tx_bundle.tail_transaction.hash,
                            self.single_bundle.tail_transaction.hash,
                        ]
                )

                mocked_get_bundles.assert_called_once_with(
                        transactions=[
                            self.single_bundle.tail_transaction.hash,
                            self.three_tx_bundle.tail_transaction.hash,
                        ]
                )

                self.assertTrue(
                        response[0].is_confirmed
                )
                self.assertTrue(
                        response[1].is_confirmed
                )

    @async_test
    async def test_non_tail(self):
        """
        Called with a non-tail transaction.
        """
        # For mocking GetTrytesCommand call
        self.adapter.seed_response(
                'getTrytes',
                {
                    # Tx with ID=1
                    'trytes': [self.three_tx_bundle[1].as_tryte_string()]
                }
        )

        # For mocking FindTransactionObjectsCommand call
        self.adapter.seed_response(
                'findTransactions',
                {
                    'hashes': [tx.hash for tx in self.three_tx_bundle]
                }
        )

        self.adapter.seed_response(
                'getTrytes',
                {
                    'trytes': [tx.as_tryte_string() for tx in self.three_tx_bundle]
                }
        )

        with mock.patch(
                'iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand.__call__',
                MagicMock(return_value=async_return({'states': {
                    self.three_tx_bundle.tail_transaction.hash: True
                }}))
        ) as mocked_glis:
            with mock.patch(
                'iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
                MagicMock(return_value=async_return({
                    'bundles': [
                        self.three_tx_bundle,
                    ]
                }))
            ) as mocked_get_bundles:
                response = await get_bundles_from_transaction_hashes(
                        adapter=self.adapter,
                        transaction_hashes=[self.three_tx_bundle[1].hash],
                        inclusion_states=True,
                )

                self.assertListEqual(
                        response,
                        [
                            self.three_tx_bundle,
                        ],
                )

                self.assertTrue(
                        response[0].is_confirmed
                )

                mocked_glis.assert_called_once_with(
                        hashes=[self.three_tx_bundle.tail_transaction.hash]
                )

                mocked_get_bundles.assert_called_once_with(
                        transactions=[
                            self.three_tx_bundle.tail_transaction.hash
                        ]
                )

    @async_test
    async def test_ordered_by_timestamp(self):
        """
        Returned bundles are sorted by tail transaction timestamp.
        """
        self.adapter.seed_response(
                'getTrytes',
                {
                    'trytes': [
                        self.three_tx_bundle.tail_transaction.as_tryte_string(),
                        self.single_bundle.tail_transaction.as_tryte_string(),
                    ]
                }
        )

        with mock.patch(
                'iota.commands.extended.get_latest_inclusion.GetLatestInclusionCommand.__call__',
                MagicMock(return_value=async_return({'states': {
                    self.three_tx_bundle.tail_transaction.hash: True,
                    self.single_bundle.tail_transaction.hash: True,
                }}))
        ) as mocked_glis:
            with mock.patch(
                'iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
                MagicMock(return_value=async_return({
                    'bundles': [
                        self.three_tx_bundle,
                        self.single_bundle,
                    ]
                }))
            ) as mocked_get_bundles:
                response = await get_bundles_from_transaction_hashes(
                        adapter=self.adapter,
                        # three_tx_bundle is the first now, which should be newer
                        # than single_bundle
                        transaction_hashes=[
                            self.three_tx_bundle.tail_transaction.hash,
                            self.single_bundle.tail_transaction.hash
                        ],
                        inclusion_states=True,
                )

                self.assertListEqual(
                        response,
                        [
                            # Response is sorted in ascending order based on timestamp!
                            # (single_bundle is older than three_tx_bundle)
                            self.single_bundle,
                            self.three_tx_bundle,
                        ],
                )

                # Check if it was called only once
                mocked_glis.assert_called_once()

                # Get the keyword arguments from that call
                _, _, mocked_glis_kwargs = mocked_glis.mock_calls[0]

                # 'hashes' keyword's value should be a list of hashes it was called
                # with. Due to the set -> list conversion in the src code, we can't
                # be sure of the order of the elements, so we check by value.
                self.assertCountEqual(
                        mocked_glis_kwargs.get('hashes'),
                        [
                            self.three_tx_bundle.tail_transaction.hash,
                            self.single_bundle.tail_transaction.hash,
                        ]
                )

                mocked_get_bundles.assert_called_once_with(
                        transactions=[
                            self.three_tx_bundle.tail_transaction.hash,
                            self.single_bundle.tail_transaction.hash,
                        ]
                )

                self.assertTrue(
                        response[0].is_confirmed
                )
                self.assertTrue(
                        response[1].is_confirmed
                )