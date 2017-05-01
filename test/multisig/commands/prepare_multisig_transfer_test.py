# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from filters.test import BaseFilterTestCase
from iota.adapter import MockAdapter
from iota.multisig import MultisigIota
from iota.multisig.commands import PrepareMultisigTransferCommand


class PrepareMultisigTransferRequestFilterTestCase(BaseFilterTestCase):
  filter_type = PrepareMultisigTransferCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_compatible_types(self):
    """
    Request contains values that can be converted to the expected
    types.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

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
