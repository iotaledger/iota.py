# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from filters.test import BaseFilterTestCase
from iota import Address, ProposedTransaction
from iota.adapter import MockAdapter
from iota.crypto.types import Digest
from iota.multisig import MultisigIota
from iota.multisig.commands import PrepareMultisigTransferCommand
from iota.multisig.types import MultisigAddress


class PrepareMultisigTransferRequestFilterTestCase(BaseFilterTestCase):
  filter_type = PrepareMultisigTransferCommand(MockAdapter()).get_request_filter
  maxDiff = None
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(PrepareMultisigTransferRequestFilterTestCase, self).setUp()

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

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'changeAddress':
        Address(self.trytes_1),

      'multisigInput':
        MultisigAddress(
          digests = [self.digest_1, self.digest_2],
          trytes  = self.trytes_2,
        ),

      'transfers':
        [
          ProposedTransaction(
            address = Address(self.trytes_3),
            value   = 42,
          ),
        ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    Request contains values that can be converted to the expected
    types.
    """
    txn =\
      ProposedTransaction(
        address = Address(self.trytes_3),
        value   = 42,
      ),

    filter_ =\
      self._filter({
        # ``changeAddress`` can be any value that resolves to an
        # :py:class:`Address`.
        'changeAddress': self.trytes_1,

        # It is recommended that you use a MultisigAddress for
        # ``multisigInput``, but it is not required.
        'multisigInput': self.trytes_2,

        # ``transfers`` must contain an array of
        # :py:class:`ProposedTransaction` objects, however.
        'transfers': [txn],
      })

    self.assertFilterPasses(filter_)

    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'changeAddress': Address(self.trytes_1),

        # We can't reconstruct the digests for the multisig address, so
        # we'll just have to trust that the user knows what they are
        # doing.
        'multisigInput': Address(self.trytes_2),

        'transfers': [txn],
      },
    )

  def test_pass_optional_parameters_excluded(self):
    """
    Request omits optional parameters.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transfers_null(self):
    """
    ``transfers`` is null.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transfers_wrong_type(self):
    """
    ``transfers`` is not an array.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transfers_empty(self):
    """
    ``transfers`` is an array, but it's empty.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transfers_contents_invalid(self):
    """
    ``transfers`` is an array, but it contains invalid values.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_multisigInput_null(self):
    """
    ``multisigInput`` is null.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_multisigInput_multiple(self):
    """
    ``multisigInput`` is an array.

    This is not valid; a bundle may only contain a single multisig
    input.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_multisigInput_wrong_type(self):
    """
    ``multisigInput`` is not a MultisigAddress.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_changeAddress_multisig_address(self):
    """
    ``changeAddress`` is allowed to be a MultisigAddress.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_changeAddress_wrong_type(self):
    """
    ``changeAddress`` is not an Address.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')


class PrepareMultisigTransferCommandTestCase(TestCase):
  def setUp(self):
    super(PrepareMultisigTransferCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = PrepareMultisigTransferCommand(self.adapter)

  def test_wireup(self):
    """
    Verifies the command is wired up correctly.
    """
    self.assertIsInstance(
      MultisigIota(self.adapter).prepareMultisigTransfer,
      PrepareMultisigTransferCommand,
    )

  def test_happy_path(self):
    """
    Preparing a bundle with a multisig input.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_unspent_inputs_with_change_address(self):
    """
    The bundle has unspent inputs, so it uses the provided change
    address.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_error_zero_iotas_transferred(self):
    """
    The bundle doesn't spend any IOTAs.

    This is considered an error case because
    :py:meth:`MultisigIota.prepare_multisig_transfer` is specialized
    for generating bundles that require multisig inputs.  Any bundle
    that doesn't require multisig functionality should be generated
    using :py:meth:`iota.api.Iota.prepare_transfer` instead.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_error_insufficient_inputs(self):
    """
    The multisig input does not contain sufficient IOTAs to cover the
    spends.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_error_unspent_inputs_no_change_address(self):
    """
    The bundle has unspent inputs, but no change address was specified.

    Unlike :py:meth:`iota.api.Iota.prepare_transfer` where all of the
    inputs are owned by the same seed, creating a multisig transfer
    usually involves multiple people.

    It would be unfair to the participants of the transaction if we
    were to automatically generate a change address using the seed of
    whoever happened to invoke the
    :py:meth:`MultisigIota.prepare_multisig_transfer` method!
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
