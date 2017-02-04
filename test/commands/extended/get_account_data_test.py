# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Iota
from iota.adapter import MockAdapter
from iota.commands.extended.get_account_data import GetAccountDataCommand


class GetAccountDataTestCase(TestCase):
  def setUp(self):
    super(GetAccountDataTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getAccountData,
      GetAccountDataCommand,
    )
