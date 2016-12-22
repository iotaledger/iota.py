# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import BadApiResponse, Iota, TransactionHash, TryteString
from iota.commands.extended.send_trytes import SendTrytesCommand
from six import text_type
from test import MockAdapter


class SendTrytesCommandTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(SendTrytesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = SendTrytesCommand(self.adapter)

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

    self.transaction1 = (
      b'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
      b'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999'
    )

    self.transaction2 = (
      b'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
      b'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999'
    )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).sendTrytes,
      SendTrytesCommand,
    )

  def test_happy_path(self):
    """
    Successful invocation of `sendTrytes`.
    """
    self.adapter.seed_response('getTransactionsToApprove', {
      'trunkTransaction':   text_type(self.transaction1, 'ascii'),
      'branchTransaction':  text_type(self.transaction2, 'ascii'),
    })

    self.adapter.seed_response('attachToTangle', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('broadcastTransactions', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('storeTransactions', {})

    response = self.command(
      trytes = [
        TryteString(self.trytes1),
        TryteString(self.trytes2),
      ],

      depth = 100,
      min_weight_magnitude = 18,
    )

    self.assertDictEqual(response, {})

    self.assertListEqual(
      self.adapter.requests,

      [
        {
          'command':  'getTransactionsToApprove',
          'depth':    100,
        },

        {
          'command': 'attachToTangle',

          'trunk_transaction':    TransactionHash(self.transaction1),
          'branch_transaction':   TransactionHash(self.transaction2),
          'min_weight_magnitude': 18,

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },

        {
          'command': 'broadcastTransactions',

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },

        {
          'command': 'storeTransactions',

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },
      ],
    )

  def test_get_transactions_to_approve_fails(self):
    """
    The `getTransactionsToApprove` call fails.
    """
    self.adapter.seed_response('getTransactionsToApprove', {
      'error': "I'm a teapot.",
    })

    with self.assertRaises(BadApiResponse):
      self.command(
        trytes = [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],

        depth = 100,
        min_weight_magnitude = 18,
      )

    # As soon as a request fails, the process halts.
    # Note that this operation is not atomic!
    self.assertListEqual(
      self.adapter.requests,

      [
        {
          'command':  'getTransactionsToApprove',
          'depth':    100,
        },
      ],
    )

  def test_attach_to_tangle_fails(self):
    """
    The `attachToTangle` call fails.
    """
    self.adapter.seed_response('getTransactionsToApprove', {
      'trunkTransaction':   text_type(self.transaction1, 'ascii'),
      'branchTransaction':  text_type(self.transaction2, 'ascii'),
    })

    self.adapter.seed_response('attachToTangle', {
      'error': "I'm a teapot.",
    })

    with self.assertRaises(BadApiResponse):
      self.command(
        trytes = [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],

        depth = 100,
        min_weight_magnitude = 18,
      )

    # As soon as a request fails, the process halts.
    # Note that this operation is not atomic!
    self.assertListEqual(
      self.adapter.requests,

      [
        {
          'command':  'getTransactionsToApprove',
          'depth':    100,
        },

        {
          'command': 'attachToTangle',

          'trunk_transaction':    TransactionHash(self.transaction1),
          'branch_transaction':   TransactionHash(self.transaction2),
          'min_weight_magnitude': 18,

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },
      ],
    )

  def test_broadcast_transactions_fails(self):
    """
    The `broadcastTransactions` call fails.
    """
    self.adapter.seed_response('getTransactionsToApprove', {
      'trunkTransaction':   text_type(self.transaction1, 'ascii'),
      'branchTransaction':  text_type(self.transaction2, 'ascii'),
    })

    self.adapter.seed_response('attachToTangle', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('broadcastTransactions', {
      'error': "I'm a teapot.",
    })

    with self.assertRaises(BadApiResponse):
      self.command(
        trytes = [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],

        depth = 100,
        min_weight_magnitude = 18,
      )

    # As soon as a request fails, the process halts.
    # Note that this operation is not atomic!
    self.assertListEqual(
      self.adapter.requests,

      [
        {
          'command':  'getTransactionsToApprove',
          'depth':    100,
        },

        {
          'command': 'attachToTangle',

          'trunk_transaction':    TransactionHash(self.transaction1),
          'branch_transaction':   TransactionHash(self.transaction2),
          'min_weight_magnitude': 18,

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },

        {
          'command': 'broadcastTransactions',

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },
      ],
    )

  def test_store_transactions_fails(self):
    """
    The `storeTransactions` call fails.
    """
    self.adapter.seed_response('getTransactionsToApprove', {
      'trunkTransaction':   text_type(self.transaction1, 'ascii'),
      'branchTransaction':  text_type(self.transaction2, 'ascii'),
    })

    self.adapter.seed_response('attachToTangle', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('broadcastTransactions', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('storeTransactions', {
      'error': "I'm a teapot.",
    })

    with self.assertRaises(BadApiResponse):
      self.command(
        trytes = [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],

        depth = 100,
        min_weight_magnitude = 18,
      )

    self.assertListEqual(
      self.adapter.requests,

      [
        {
          'command':  'getTransactionsToApprove',
          'depth':    100,
        },

        {
          'command': 'attachToTangle',

          'trunk_transaction':    TransactionHash(self.transaction1),
          'branch_transaction':   TransactionHash(self.transaction2),
          'min_weight_magnitude': 18,

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },

        {
          'command': 'broadcastTransactions',

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },

        {
          'command': 'storeTransactions',

          'trytes': [
            TryteString(self.trytes1),
            TryteString(self.trytes2),
          ],
        },
      ],
    )
