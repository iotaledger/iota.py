# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address, ProposedTransaction
from iota.multisig.transaction import ProposedMultisigBundle
from iota.multisig.types import MultisigAddress


class ProposedMultisigBundleTestCase(TestCase):
  def setUp(self):
    super(ProposedMultisigBundleTestCase, self).setUp()

    self.bundle = ProposedMultisigBundle()

  def test_add_inputs_error_already_finalized(self):
    """
    Attempting to add inputs to a bundle that is already finalized.
    """
    # noinspection SpellCheckingInspection
    self.bundle.add_transaction(
      ProposedTransaction(
        address =
          Address(
            b'TESTVALUE9DONTUSEINPRODUCTION99999XE9IVG'
            b'EFNDOCQCMERGUATCIEGGOHPHGFIAQEZGNHQ9W99CH'
          ),

        value = 0,
      ),
    )

    self.bundle.finalize()

    with self.assertRaises(RuntimeError):
      self.bundle.add_inputs([])

  def test_add_inputs_error_multiple(self):
    """
    Attempting to add multiple multisig inputs.

    This is not currently supported.
    """
    with self.assertRaises(ValueError):
      # noinspection SpellCheckingInspection
      self.bundle.add_inputs([
        MultisigAddress(
          trytes =
            b'TESTVALUE9DONTUSEINPRODUCTION99999XDIFTE'
            b'RCA9CHWGBEJHZGXENCDHUCADDEMDP9PAG9BBA9AAC',

          digests = [],
        ),

        MultisigAddress(
          trytes =
            b'TESTVALUE9DONTUSEINPRODUCTION99999Y9EHHI'
            b'9GD9OCRGDDVFGEQCN9QFNATAKARCOBV99BJDGEADT',

          digests = [],
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
          trytes =
            b'TESTVALUE9DONTUSEINPRODUCTION99999QGSEW9'
            b'DADCMCFICIZCTDUCKI9CJAAHNCEHBIHBPFQB9G9FS',

          key_index = 0,
          balance   = 76,
        )
      ])
