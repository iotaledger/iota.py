# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from filters.test import BaseFilterTestCase

from iota.commands.find_transactions import FindTransactionsRequestFilter


class FindTransactionsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = FindTransactionsRequestFilter
  skip_value_check = True

  def test_pass_all_parameters(self):
    """The request contains valid values for all parameters."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_bundles_only(self):
    """The request only includes bundles."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_addresses_only(self):
    """The request only includes addresses."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_tags_only(self):
    """The request only includes tags."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_approvees_only(self):
    """The request only includes approvees."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_empty(self):
    """The request does not contain any parameters."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_all_parameters_empty(self):
    """The request contains all parameters, but every one is empty."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_unexpected_parameters(self):
    """The request contains unexpected parameters."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_bundles_wrong_type(self):
    """`bundles` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_bundles_contents_invalid(self):
    """`bundles` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_addresses_wrong_type(self):
    """`addresses` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_addresses_contents_invalid(self):
    """`addresses` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tags_wrong_type(self):
    """`tags` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tags_contents_invalid(self):
    """`tags` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_approvees_wrong_type(self):
    """`approvees` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_approvees_contents_invalid(self):
    """`approvees` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
