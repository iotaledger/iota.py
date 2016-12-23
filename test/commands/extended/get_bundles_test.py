# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from filters.test import BaseFilterTestCase
from iota import Iota
from iota.commands.extended.get_bundles import GetBundlesCommand
from test import MockAdapter


class GetBundlesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetBundlesCommand(MockAdapter()).get_request_filter
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


class GetBundlesCommandTestCase(TestCase):
  def setUp(self):
    super(GetBundlesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verifies that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getBundles,
      GetBundlesCommand,
    )
