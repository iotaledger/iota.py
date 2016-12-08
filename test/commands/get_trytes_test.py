# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from filters.test import BaseFilterTestCase

from iota.commands.get_trytes import GetTrytesCommand
from test import MockAdapter


class GetTrytesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetTrytesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_happy_path(self):
    """The request is valid."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_compatible_types(self):
    """
    The request contains values that can be converted to the expected
    types.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_empty(self):
    """The request is empty."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_unexpected_parameters(self):
    """The request contains unexpected parameters."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_hashes_null(self):
    """`hashes` is null."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_hashes_wrong_type(self):
    """`hashes` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_hashes_empty(self):
    """`hashes` is an array, but it is empty."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_hashes_contents_invalid(self):
    """`hashes` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')


class GetTrytesResponseFilter(BaseFilterTestCase):
  filter_type = GetTrytesCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  def test_pass_transactions(self):
    """The response contains data for multiple transactions."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_no_transactions(self):
    """The response does not contain any transactions."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
