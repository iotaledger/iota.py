# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, TransactionHash
from iota.commands.extended.replay_bundle import ReplayBundleCommand
from iota.filters import Trytes
from six import binary_type, text_type
from test import MockAdapter


class ReplayBundleRequestFilterTestCase(BaseFilterTestCase):
  filter_type = ReplayBundleCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(ReplayBundleRequestFilterTestCase, self).setUp()

    self.trytes1 = (
      b'TESTVALUEONE9DONTUSEINPRODUCTION99999DAU'
      b'9WFSFWBSFT9QATCXFIIKDVFLHIIJGGFCDYENBEDCF'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'depth':                100,
      'min_weight_magnitude': 18,
      'transaction':          TransactionHash(self.trytes1),
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
      # This can be any TrytesCompatible value.
      'transaction': binary_type(self.trytes1),

      # These values must still be ints, however.
      'depth':                100,
      'min_weight_magnitude': 18,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'depth':                100,
        'min_weight_magnitude': 18,
        'transaction':          TransactionHash(self.trytes1),
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'depth':                [f.FilterMapper.CODE_MISSING_KEY],
        'min_weight_magnitude': [f.FilterMapper.CODE_MISSING_KEY],
        'transaction':          [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'depth':                100,
        'min_weight_magnitude': 18,
        'transaction':          TransactionHash(self.trytes1),

        # That's a real nasty habit you got there.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transaction_null(self):
    """
    ``transaction`` is null.
    """
    self.assertFilterErrors(
      {
        'transaction': None,

        'depth':                100,
        'min_weight_magnitude': 18,
      },

      {
        'transaction': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_transaction_wrong_type(self):
    """
    ``transaction`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'transaction': text_type(self.trytes1, 'ascii'),

        'depth':                100,
        'min_weight_magnitude': 18,
      },

      {
        'transaction': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_transaction_not_trytes(self):
    """
    ``transaction`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'transaction': b'not valid; must contain only uppercase and "9"',

        'depth':                100,
        'min_weight_magnitude': 18,
      },

      {
        'transaction': [Trytes.CODE_NOT_TRYTES],
      },
    )

  def test_fail_depth_null(self):
    """
    ``depth`` is null.
    """
    self.assertFilterErrors(
      {
        'depth': None,

        'min_weight_magnitude': 18,
        'transaction':          TransactionHash(self.trytes1),
      },

      {
        'depth': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_depth_string(self):
    """
    ``depth`` is a string.
    """
    self.assertFilterErrors(
      {
        # Too ambiguous; it's gotta be an int.
        'depth': '4',

        'min_weight_magnitude': 18,
        'transaction':          TransactionHash(self.trytes1),
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_float(self):
    """
    ``depth`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, float value is not valid.
        'depth': 8.0,

        'min_weight_magnitude': 18,
        'transaction':          TransactionHash(self.trytes1),
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_too_small(self):
    """
    ``depth`` is < 1.
    """
    self.assertFilterErrors(
      {
        'depth': 0,

        'min_weight_magnitude': 18,
        'transaction':          TransactionHash(self.trytes1),
      },

      {
        'depth': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_min_weight_magnitude_null(self):
    """
    ``min_weight_magnitude`` is null.
    """
    self.assertFilterErrors(
      {
        'min_weight_magnitude': None,

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'min_weight_magnitude': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_min_weight_magnitude_string(self):
    """
    ``min_weight_magnitude`` is a string.
    """
    self.assertFilterErrors(
      {
        # It's gotta be an int!
        'min_weight_magnitude': '18',

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'min_weight_magnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_float(self):
    """
    ``min_weight_magnitude`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, float values are not valid.
        'min_weight_magnitude': 18.0,

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'min_weight_magnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_too_small(self):
    """
    ``min_weight_magnitude`` is < 1.
    """
    self.assertFilterErrors(
      {
        'min_weight_magnitude': 0,

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'min_weight_magnitude': [f.Min.CODE_TOO_SMALL],
      },
    )


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
