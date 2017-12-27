# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, TransactionHash
from iota.adapter import MockAdapter
from iota.commands.extended.is_promotable import IsPromotableCommand
from iota.filters import Trytes


class IsPromotableRequestFilterTestCase(BaseFilterTestCase):
  filter_type = IsPromotableCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(IsPromotableRequestFilterTestCase, self).setUp()

    # noinspection SpellCheckingInspection
    self.transaction = (
      'TESTVALUE9DONTUSEINPRODUCTION99999KPZOTR'
      'VDB9GZDJGZSSDCBIX9QOK9PAV9RMDBGDXLDTIZTWQ'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    # Raw trytes are extracted to match the IRI's JSON protocol.
    request = {
      'tail': self.transaction,
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    Request contains values that can be converted to the expected
    types.
    """
    filter_ = self._filter({
      # Any TrytesCompatible value will work here.
      'tail': TransactionHash(self.transaction),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'tail': self.transaction,
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'tail': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'tail': TransactionHash(self.transaction),

        # SAY "WHAT" AGAIN!
        'what': 'augh!',
      },

      {
        'what': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transaction_wrong_type(self):
    """
    ``tail`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'tail': 42,
      },

      {
        'tail': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_transaction_not_trytes(self):
    """
    ``tail`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'tail': b'not valid; must contain only uppercase and "9"',
      },

      {
        'tail': [Trytes.CODE_NOT_TRYTES],
      },
    )


# noinspection SpellCheckingInspection
class IsPromotableCommandTestCase(TestCase):
  def setUp(self):
    super(IsPromotableCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = IsPromotableCommand(self.adapter)

    # noinspection SpellCheckingInspection
    self.transaction = (
      'TESTVALUE9DONTUSEINPRODUCTION99999KPZOTR'
      'VDB9GZDJGZSSDCBIX9QOK9PAV9RMDBGDXLDTIZTWQ'
    )

  def test_wireup(self):
    """
    Verifies that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).isPromotable,
      IsPromotableCommand,
    )

  def test_positive_is_promotable(self):
    """
    Transaction is promotable
    """

    self.adapter.seed_response('checkConsistency', {
      'state': True,
    })

    response = self.command(tail=self.transaction)
    self.assertTrue(response)

  def test_negative_is_promotable(self):
    """
    Transaction is not promotable
    """

    self.adapter.seed_response('checkConsistency', {
      'state': False,
      'info': 'Inconsistent state',
    })

    response = self.command(tail=self.transaction)
    self.assertFalse(response)
