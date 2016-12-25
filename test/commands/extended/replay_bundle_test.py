# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from filters.test import BaseFilterTestCase
from iota import Iota
from iota.commands.extended.replay_bundle import ReplayBundleCommand
from test import MockAdapter


class ReplayBundleRequestFilterTestCase(BaseFilterTestCase):
  filter_type = ReplayBundleCommand(MockAdapter()).get_request_filter
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

  def test_fail_transaction_null(self):
    """
    ``transaction`` is null.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transaction_wrong_type(self):
    """
    ``transaction`` is not a TrytesCompatible value.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transaction_not_trytes(self):
    """
    ``transaction`` contains invalid characters.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_depth_null(self):
    """
    ``depth`` is null.
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


class ReplayBundleCommandTestCase(TestCase):
  def setUp(self):
    super(ReplayBundleCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verifies that the command is wired-up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).replayBundle,
      ReplayBundleCommand,
    )

  # :todo: Unit tests.
