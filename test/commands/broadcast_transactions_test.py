# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota.commands.broadcast_transactions import BroadcastTransactionsCommand
from iota.types import TryteString
from test import MockAdapter


# noinspection SpellCheckingInspection
class BroadcastTransactionsCommandTestCase(TestCase):
  def setUp(self):
    super(BroadcastTransactionsCommandTestCase, self).setUp()

    self.adapter  = MockAdapter()
    self.command  = BroadcastTransactionsCommand(self.adapter)

  def test_happy_path(self):
    """Successful invocation of `broadcastTransactions`."""
    expected_response = {}

    self.adapter.response = expected_response

    response = self.command(
      trytes = [
        # These values tend to get rather long, but for purposes of
        #   this test, we don't have to get too realistic.
        TryteString(b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQFCUSDXZHOFH'),
      ],
    )

    self.assertDictEqual(response, expected_response)

    self.assertListEqual(
      self.adapter.requests,

      [(
        {
          'command': 'broadcastTransactions',

          'trytes': [
            b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQFCUSDXZHOFH',
          ],
        },

        {},
      )]
    )

  def test_compatible_types(self):
    """
    Invoking `broadcastTransactions` with parameters that can be
      converted into the correct types.
    """
    self.command(
      trytes = [
        b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQFCUSDXZHOFH',
      ],
    )

    self.assertListEqual(
      self.adapter.requests,

      [(
        {
          'command': 'broadcastTransactions',

          'trytes': [
            b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQFCUSDXZHOFH',
          ],
        },

        {},
      )]
    )

  def test_error_trytes_invalid(self):
    """
    Attempting to call `broadcastTransactions` but `trytes` is invalid.
    """
    with self.assertRaises(TypeError):
      # This won't work; `trytes` has to be an array.
      self.command(
        trytes = TryteString(b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQF'),
      )

    with self.assertRaises(TypeError):
      # Seriously, you haven't figured this out yet?
      self.command(trytes=['not a valid tryte string', 42])

    with self.assertRaises(ValueError):
      # Got everything set up, but nothing to broadcast?
      # Welcome to your first YouTube channel!
      self.command(trytes=[])
