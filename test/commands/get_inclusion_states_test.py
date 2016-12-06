# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type

from iota.commands.get_inclusion_states import GetInclusionStatesRequestFilter
from iota.types import TransactionId


class GetInclusionStatesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetInclusionStatesRequestFilter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetInclusionStatesRequestFilterTestCase, self).setUp()

    self.trytes1 = (
      b'QHBYXQWRAHQJZEIARWSQGZJTAIITOZRMBFICIPAV'
      b'D9YRJMXFXBDPFDTRAHHHP9YPDUVTNOFWZGFGWMYHE'
    )

    self.trytes2 = (
      b'ZIJGAJ9AADLRPWNCYNNHUHRRAC9QOUDATEDQUMTN'
      b'OTABUVRPTSTFQDGZKFYUUIE9ZEBIVCCXXXLKX9999'
    )

  def test_pass_happy_path(self):
    """Typical `getInclusionStates` request."""
    request = {
      'transactions': [
        TransactionId(self.trytes1),
        TransactionId(self.trytes2),
      ],

      'tips': [
        # These values would normally be different from
        # ``transactions``, but for purposes of this unit test, we just
        # need to make sure the format is correct.
        TransactionId(self.trytes1),
        TransactionId(self.trytes2),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    The request contains values that can be converted to expected
      types.
    """
    filter_ = self._filter({
      'transactions': [
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],

      'tips': [
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'transactions': [
          TransactionId(self.trytes1),
          TransactionId(self.trytes2),
        ],

        'tips': [
          TransactionId(self.trytes1),
          TransactionId(self.trytes2),
        ],
      },
    )

  def test_fail_empty(self):
    """The incoming request is empty."""
    self.assertFilterErrors(
      {},

      {
        'transactions': [f.FilterMapper.CODE_MISSING_KEY],
        'tips':         [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """The incoming request contains unexpected parameters."""
    self.assertFilterErrors(
      {
        'transactions': [TransactionId(self.trytes1)],
        'tips':         [TransactionId(self.trytes2)],

        # I bring scientists, you bring a rock star.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transactions_null(self):
    """`transactions` is null."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transactions_wrong_type(self):
    """`transactions` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transactions_empty(self):
    """`transactions` is an array, but it is empty."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_transactions_contents_invalid(self):
    """`transactions` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tips_null(self):
    """`tips` is null"""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tips_wrong_type(self):
    """`tips` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tips_empty(self):
    """`tips` is an array, but it is empty."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tips_contents_invalid(self):
    """`tips` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
