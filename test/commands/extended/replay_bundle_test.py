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

  # :todo: Unit tests.


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
