# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from filters.test import BaseFilterTestCase
from iota import Iota
from iota.commands.extended.prepare_transfers import PrepareTransfersCommand
from test import MockAdapter


class PrepareTransfersRequestFilterTestCase(BaseFilterTestCase):
  filter_type = PrepareTransfersCommand(MockAdapter()).get_request_filter
  skip_value_check = True


class PrepareTransfersCommandTestCase(TestCase):
  def setUp(self):
    super(PrepareTransfersCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).prepareTransfers,
      PrepareTransfersCommand,
    )
