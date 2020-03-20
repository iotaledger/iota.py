from unittest import TestCase

from iota import Iota, AsyncIota, MockAdapter, Transaction
from iota.commands.extended import GetTransactionObjectsCommand
from iota.adapter import async_return
from test import patch, MagicMock, mock, async_test


class GetTransactionObjectsCommandTestCase(TestCase):
    def setUp(self):
        super(GetTransactionObjectsCommandTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.command = GetTransactionObjectsCommand(self.adapter)

        # Define values that we can reuse across tests.
        self.transaction_hash = \
            b'BROTOVRCAEMFLRWGPVWDPDTBRAMLHVCHQDEHXLCWH' \
            b'KKXLVDFCPIJEUZTPPFMPQQ9KOHAEUAMMVJN99999'
        self.trytes = \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999999999999999999999999999999999999999999999999' \
            b'99999999999999999AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
            b'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA99999999999999999999999999' \
            b'9QC9999999999999999999999999PQYJHAD99999999999999999999WHIUDFV' \
            b'IFXNBJVEHYPLDADIDINGAWMHYIJNPYUDWXCAWL9GSKTUIZLJGGFIXEIYTJEDQZ' \
            b'TIYRXHC9PBWBDSOTEJTQTYYSZLVTFLDQMZSGLHKLYVJOLMXIJJRTGS9RYBXLAT' \
            b'ZJXBVBCPUGWRUKZJYLBGPKRKWIA9999FPYHMFFWMMKOHTSAPMMATZQLWXJSPMT' \
            b'JSRQIPMDCQXFFMXMHCYDKVJCFSRECAVALCOFIYCJLNRZZZ9999999999999999' \
            b'999999999999999KITCXNZOF999999999MMMMMMMMMEA9999F9999999999999' \
            b'9999999'

    def test_wireup(self):
        """
        Verify that the command is wired up correctly. (sync)

        The API method indeed calls the appropiate command.
        """
        with patch('iota.commands.extended.get_transaction_objects.GetTransactionObjectsCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = Iota(self.adapter)

            # Don't need to call with proper args here.
            response = api.get_transaction_objects('hashes')

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
        with patch('iota.commands.extended.get_transaction_objects.GetTransactionObjectsCommand.__call__',
                MagicMock(return_value=async_return('You found me!'))
                ) as mocked_command:

            api = AsyncIota(self.adapter)

            # Don't need to call with proper args here.
            response = await api.get_transaction_objects('hashes')

            self.assertTrue(mocked_command.called)

            self.assertEqual(
                response,
                'You found me!'
            )

    @async_test
    async def test_transaction_found(self):
        """
        A transaction is found with the inputs. A transaction object is
        returned
        """
        with mock.patch(
            'iota.commands.core.get_trytes.GetTrytesCommand._execute',
            mock.Mock(return_value=async_return({'trytes': [self.trytes, ]})),
        ):
            response = await self.command(hashes=[self.transaction_hash])

        self.assertEqual(len(response['transactions']), 1)
        transaction = response['transactions'][0]
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.hash, self.transaction_hash)

    @async_test
    async def test_no_transactions_fround(self):
        """
        No transaction is found with the inputs. An empty list is returned
        """
        with mock.patch(
            'iota.commands.core.get_trytes.GetTrytesCommand._execute',
            mock.Mock(return_value=async_return({'trytes': []})),
        ):
            response = await self.command(hashes=[self.transaction_hash])

        self.assertDictEqual(
            response,
            {
                'transactions': [],
            },
        )
