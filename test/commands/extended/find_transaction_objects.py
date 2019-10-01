# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from unittest import TestCase

import mock

from iota import Iota, MockAdapter, Transaction
from iota.commands.extended import FindTransactionObjectsCommand


class FindTransactionObjectsCommandTestCase(TestCase):
    # noinspection SpellCheckingInspection
    def setUp(self):
        super(FindTransactionObjectsCommandTestCase, self).setUp()

        self.adapter = MockAdapter()
        self.command = FindTransactionObjectsCommand(self.adapter)

        # Define values that we can reuse across tests.
        self.address = 'A' * 81
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
        Verify that the command is wired up correctly.
        """
        self.assertIsInstance(
            Iota(self.adapter).findTransactionObjects,
            FindTransactionObjectsCommand,
        )

    def test_transaction_found(self):
        """
        A transaction is found with the inputs. A transaction object is
        returned
        """
        with mock.patch(
            'iota.commands.core.find_transactions.FindTransactionsCommand.'
            '_execute',
            mock.Mock(return_value={'hashes': [self.transaction_hash, ]}),
        ):
            with mock.patch(
                'iota.commands.core.get_trytes.GetTrytesCommand._execute',
                mock.Mock(return_value={'trytes': [self.trytes, ]}),
            ):
                response = self.command(addresses=[self.address])

        self.assertEqual(len(response['transactions']), 1)
        transaction = response['transactions'][0]
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.address, self.address)

    def test_no_transactions_fround(self):
        """
        No transaction is found with the inputs. An empty list is returned
        """
        with mock.patch(
            'iota.commands.core.find_transactions.FindTransactionsCommand.'
            '_execute',
            mock.Mock(return_value={'hashes': []}),
        ):
            response = self.command(addresses=[self.address])

        self.assertDictEqual(
            response,
            {
                'transactions': [],
            },
        )
