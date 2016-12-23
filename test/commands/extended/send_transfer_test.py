# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from filters.test import BaseFilterTestCase
from iota import Iota
from iota.commands.extended.send_transfer import SendTransferCommand
from test import MockAdapter


class SendTransferRequestFilterTestCase(BaseFilterTestCase):
  filter_type = SendTransferCommand(MockAdapter()).get_request_filter
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

  def test_pass_optional_parameters_omitted(self):
    """
    Request omits optional parameters.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_empty(self):
    """
    Request is empty.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_seed_null(self):
    """
    ``seed`` is null.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_seed_wrong_type(self):
    """
    ``seed`` is not a TrytesCompatible value.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_seed_not_trytes(self):
    """
    ``seed`` contains invalid characters.
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
    ``transfers`` is an array, but it is empty.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transfers_contents_invalid(self):
    """
    ``transfers`` is a non-empty array, but it contains invalid values.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_change_address_wrong_type(self):
    """
    ``change_address`` is not a TrytesCompatible value.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_change_address_not_trytes(self):
    """
    ``change_address`` contains invalid characters.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_inputs_wrong_type(self):
    """
    ``inputs`` is not an array.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_inputs_empty(self):
    """
    ``inputs`` is an array, but it is empty.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_inputs_contents_invalid(self):
    """
    ``inputs`` is a non-empty array, but it contains invalid values.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_depth_string(self):
    """
    ``depth`` is a string.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_depth_float(self):
    """
    ``depth`` is a float.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_depth_too_small(self):
    """
    ``depth`` is < 1.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_min_weight_magnitude_string(self):
    """
    ``min_weight_magnitude`` is a string.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_min_weight_magnitude_float(self):
    """
    ``min_weight_magnitude`` is a float.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_min_weight_magnitude_too_small(self):
    """
    ``min_weight_magnitude`` is < 18.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')


class SendTransferCommandTestCase(TestCase):
  def setUp(self):
    super(SendTransferCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verifies that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).sendTransfer,
      SendTransferCommand,
    )
