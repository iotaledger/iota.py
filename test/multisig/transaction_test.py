# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address, ProposedTransaction
from iota.crypto.types import Digest
from iota.multisig.transaction import ProposedMultisigBundle
from iota.multisig.types import MultisigAddress


class ProposedMultisigBundleTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(ProposedMultisigBundleTestCase, self).setUp()

    self.bundle = ProposedMultisigBundle()

    # Define some tryte sequences that we can reuse between tests.
    self.digest_1 =\
      Digest(
        trytes =
          b'FWNEPVJNGUKTSHSBDO9AORBCVWWLVXC9KAMKYYNKPYNJDKSAUURI9ELKOEEYPKVTYP'
          b'CKOCJQESYFEMINIFKX9PDDGRBEEHYYXCJW9LHGWFZGHKCPVDBGMGQKIPCNKNITGMZT'
          b'DIWVUB9PCHCOPHMIWKSUKRHZOJPMAY',

        key_index = 0,
      )

    self.digest_2 =\
      Digest(
        trytes =
          b'PAIRLDJQY9XAUSKIGCTHRJHZVARBEY9NNHYJ9UI9HWWZXFSDWEZEGDCWNVVYSYDV9O'
          b'HTR9NGGZURISWTNECFTCMEWQQFJ9VKLFPDTYJYXC99OLGRH9OSFJLMEOGHFDHZYEAF'
          b'IMIZTJRBQUVCR9U9ZWTMUXTUEOUBLC',

        key_index = 0,
      )

    self.trytes_1 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999IIPEM9'
      b'LA9FLHEGHDACSA9DOBQHQCX9BBHCFDIIMACARHA9B'
    )

    self.trytes_2 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999BGUDVE'
      b'DGH9WFQDEDVETCOGEGCDI9RFHGFGXBI99EJICHNEM'
    )

    self.trytes_3 = (
      b'TESTVALUE9DONTUSEINPRODUCTION99999XBGEUC'
      b'LF9EIFXHM9KHQANBLBHFVGTEGBWHNAKFDGZHYGCHI'
    )

  def test_add_inputs_happy_path(self):
    """
    Adding a multisig input to a bundle.
    """
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(
      ProposedTransaction(
        address = Address(self.trytes_1),
        value   = 42,
      ),
    )

    self.bundle.add_inputs([
      MultisigAddress(
        trytes  = self.trytes_2,
        digests = [self.digest_1, self.digest_2],
        balance = 42,
      )
    ])

    # The multisig input requires a total of 4 transactions to store
    # all the signatures.  Including the spend, that makes 5
    # transactions in total.
    self.assertEqual(len(self.bundle), 5)

  def test_add_inputs_error_already_finalized(self):
    """
    Attempting to add inputs to a bundle that is already finalized.
    """
    self.bundle.add_transaction(
      ProposedTransaction(
        address = Address(self.trytes_1),
        value   = 0,
      ),
    )

    self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      self.bundle.add_inputs([])

  def test_add_inputs_error_digests_empty(self):
    """
    Adding a multisig input with unknown digests.
    """
    with self.assertRaises(ValueError):
      self.bundle.add_inputs([
        MultisigAddress(
          trytes  = self.trytes_1,
          digests = [],
        ),
      ])

  def test_add_inputs_error_balance_null(self):
    """
    Adding a multisig input with null balance.
    """
    with self.assertRaises(ValueError):
      self.bundle.add_inputs([
        MultisigAddress(
          trytes  = self.trytes_1,
          digests = [self.digest_1, self.digest_2],
          # balance = 42,
        ),
      ])

  def test_add_inputs_error_multiple(self):
    """
    Attempting to add multiple multisig inputs.

    This is not currently supported.
    """
    with self.assertRaises(ValueError):
      # noinspection SpellCheckingInspection
      self.bundle.add_inputs([
        MultisigAddress(
          trytes  = self.trytes_1,
          digests = [self.digest_1, self.digest_2],
          balance = 42,
        ),

        MultisigAddress(
          trytes  = self.trytes_2,
          digests = [self.digest_2, self.digest_1],
        ),
      ])

  def test_add_inputs_error_not_multisig(self):
    """
    Attempting to add a non-multisig input.

    This is not currently supported.
    """
    with self.assertRaises(TypeError):
      # noinspection SpellCheckingInspection,PyTypeChecker
      self.bundle.add_inputs([
        Address(
          trytes    = self.trytes_1,
          key_index = 0,
          balance   = 76,
        ),
      ])
