# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from filters.test import BaseFilterTestCase
from iota import Iota
from iota.commands.extended.get_latest_inclusion import \
  GetLatestInclusionCommand
from test import MockAdapter


class GetLatestInclusionRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetLatestInclusionCommand(MockAdapter()).get_request_filter
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

  def test_fail_hashes_null(self):
    """
    ``hashes`` is null.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_hashes_wrong_type(self):
    """
    ``hashes`` is not an array.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_hashes_empty(self):
    """
    ``hashes`` is an array, but it is empty.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_hashes_contents_invalid(self):
    """
    ``hashes`` is a non-empty array, but it contains invalid values.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')


class GetLatestInclusionCommandTestCase(TestCase):
  def setUp(self):
    super(GetLatestInclusionCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetLatestInclusionCommand(self.adapter)

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getLatestInclusion,
      GetLatestInclusionCommand,
    )

  def test_happy_path(self):
    """
    Successfully requesting latest inclusion state.
    """
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
