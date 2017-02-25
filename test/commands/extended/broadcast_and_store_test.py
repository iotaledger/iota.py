# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from six import text_type

from iota import Iota, TransactionTrytes
from iota.adapter import MockAdapter
from iota.commands.extended.broadcast_and_store import BroadcastAndStoreCommand


class BroadcastAndStoreCommandTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(BroadcastAndStoreCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = BroadcastAndStoreCommand(self.adapter)

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).broadcastAndStore,
      BroadcastAndStoreCommand,
    )

  def test_happy_path(self):
    """
    Successful invocation of ``broadcastAndStore``.
    """
    self.adapter.seed_response('broadcastTransactions', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('storeTransactions', {})

    trytes = [
      TransactionTrytes(self.trytes1),
      TransactionTrytes(self.trytes2),
    ]

    response = self.command(trytes=trytes)

    self.assertDictEqual(response, {'trytes': trytes})
