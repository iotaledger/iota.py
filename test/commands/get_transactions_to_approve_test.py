# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from filters.test import BaseFilterTestCase

from iota.commands.get_transactions_to_approve import \
  GetTransactionsToApproveRequestFilter, GetTransactionsToApproveResponseFilter


class GetTransactionsToApproveRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetTransactionsToApproveRequestFilter
  skip_value_check = True

  def test_pass_happy_path(self):
    """Typical `getTransactionsToApprove` request."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_pass_empty(self):
    """
    Request is empty, so default values are used for all parameters.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_unexpected_parameters(self):
    """Request contains unexpected parameters."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_depth_float(self):
    """`depth` is a float."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_depth_string(self):
    """`depth` is a string."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_depth_too_small(self):
    """`depth` is less than 1."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')


class GetTransactionsToApproveResponseFilterTestCase(BaseFilterTestCase):
  filter_type = GetTransactionsToApproveResponseFilter
  skip_value_check = True

  def test_pass_happy_path(self):
    """Typical `getTransactionsToApprove` response."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
