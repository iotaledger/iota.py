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
