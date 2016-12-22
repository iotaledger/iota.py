# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import BadApiResponse, Iota, TryteString
from iota.commands.extended.broadcast_and_store import BroadcastAndStoreCommand
from six import text_type
from test import MockAdapter


class BroadcastAndStoreCommandTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
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
    Successful invocation of `broadcastAndStore`.
    """
    self.adapter.seed_response('broadcastTransactions', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('storeTransactions', {})

    trytes = [
      TryteString(self.trytes1),
      TryteString(self.trytes2),
    ]

    response = self.command(trytes=trytes)

    self.assertDictEqual(response, {})

    self.assertListEqual(
      self.adapter.requests,

      [
        {
          'command':  'broadcastTransactions',
          'trytes':   trytes,
        },

        {
          'command':  'storeTransactions',
          'trytes':   trytes,
        },
      ],
    )

  def test_broadcast_transactions_fails(self):
    """
    The `broadcastTransactions` command fails.
    """
    self.adapter.seed_response('broadcastTransactions', {
      'error': "I'm a teapot.",
    })

    with self.assertRaises(BadApiResponse):
      self.command(trytes=[TryteString(self.trytes1)])

    # The command stopped after the first request failed.
    self.assertListEqual(
      self.adapter.requests,

      [{
        'command':  'broadcastTransactions',
        'trytes':   [TryteString(self.trytes1)],
      }],
    )

  def test_store_transactions_fails(self):
    """
    The `storeTransactions` command fails.
    """
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
      self.command(trytes=[TryteString(self.trytes1)])

    # The `broadcastTransactions` command was still executed; there is
    # no way to execute these commands atomically.
    self.assertListEqual(
      self.adapter.requests,

      [
        {
          'command':  'broadcastTransactions',
          'trytes':   [TryteString(self.trytes1)],
        },

        {
          'command':  'storeTransactions',
          'trytes':   [TryteString(self.trytes1)],
        },
      ],
    )
