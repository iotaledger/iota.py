# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Iota, TransactionHash
from iota.adapter import MockAdapter


class HelpersTestCase(TestCase):
  def setUp(self):
    super(HelpersTestCase, self).setUp()

    self.api = api = Iota('mock://')
    self.api.adapter = MockAdapter()

    # noinspection SpellCheckingInspection
    self.transaction = (
      'TESTVALUE9DONTUSEINPRODUCTION99999KPZOTR'
      'VDB9GZDJGZSSDCBIX9QOK9PAV9RMDBGDXLDTIZTWQ'
    )

  def test_positive_is_promotable(self):
    """
    Transaction is promotable
    """

    self.api.adapter.seed_response('checkConsistency', {
      'state': True,
    })

    self.assertTrue(self.api.helpers.is_promotable(tail=self.transaction))

  def test_negative_is_promotable(self):
    """
    Transaction is not promotable
    """

    self.api.adapter.seed_response('checkConsistency', {
      'state': False,
      'info': 'Inconsistent state',
    })

    self.assertFalse(self.api.helpers.is_promotable(tail=self.transaction))
