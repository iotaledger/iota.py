# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.commands import FilterError
from iota.commands.broadcast_transactions import BroadcastTransactionsCommand
from iota.types import TryteString
from test.commands import BaseFilterCommandTestCase


# noinspection SpellCheckingInspection
class BroadcastTransactionsCommandTestCase(BaseFilterCommandTestCase):
  command_type = BroadcastTransactionsCommand

  def test_happy_path(self):
    """Successful invocation of `broadcastTransactions`."""
    self.assertCommandSuccess(
      expected_response = {},

      request = {
        'trytes': [
          # These values tend to get rather long, but for purposes of
          #   this test, we don't have to get too realistic.
          TryteString(b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQFCUSDXH'),
        ],
      },
    )

  def test_compatible_types(self):
    """
    Invoking `broadcastTransactions` with parameters that can be
      converted into the correct types.
    """
    self.assertCommandSuccess(
      expected_response = {},

      request = {
        'trytes': [
          b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQFCUSDXZHOFH',
        ],
      }
    )

  def test_error_trytes_invalid(self):
    """
    Attempting to call `broadcastTransactions` but `trytes` is invalid.
    """
    with self.assertRaises(FilterError):
      # This won't work; `trytes` has to be an array.
      self.command(
        trytes = TryteString(b'BYSWEAUTWXHXZ9YBZISEK9LUHWGMHXCGEVNZHRLUWQF'),
      )

    with self.assertRaises(FilterError):
      # Seriously, you haven't figured this out yet?
      self.command(trytes=['not a valid tryte string', 42])

    with self.assertRaises(FilterError):
      # Got everything set up, but nothing to broadcast?
      # Welcome to your first YouTube channel!
      self.command(trytes=[])
