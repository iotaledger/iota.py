# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type

from iota import Bundle, Iota, TransactionHash, TransactionTrytes, BadApiResponse
from iota.adapter import MockAdapter
from iota.commands.extended.promote_transaction import PromoteTransactionCommand
from iota.filters import Trytes
from test import mock


class PromoteTransactionRequestFilterTestCase(BaseFilterTestCase):
  filter_type = PromoteTransactionCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(PromoteTransactionRequestFilterTestCase, self).setUp()

    self.trytes1 = (
      b'TESTVALUEONE9DONTUSEINPRODUCTION99999DAU'
      b'9WFSFWBSFT9QATCXFIIKDVFLHIIJGGFCDYENBEDCF'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'depth':              100,
      'minWeightMagnitude': 18,
      'transaction':        TransactionHash(self.trytes1),
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
      'depth':              100,
      'minWeightMagnitude': 18,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'depth':              100,
        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'depth':              [f.FilterMapper.CODE_MISSING_KEY],
        'minWeightMagnitude': [f.FilterMapper.CODE_MISSING_KEY],
        'transaction':        [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'depth':              100,
        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),

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

        'depth':              100,
        'minWeightMagnitude': 18,
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
        'transaction': 42,

        'depth':              100,
        'minWeightMagnitude': 18,
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

        'depth':              100,
        'minWeightMagnitude': 18,
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

        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
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

        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
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

        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
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

        'minWeightMagnitude': 18,
        'transaction':        TransactionHash(self.trytes1),
      },

      {
        'depth': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_min_weight_magnitude_null(self):
    """
    ``minWeightMagnitude`` is null.
    """
    self.assertFilterErrors(
      {
        'minWeightMagnitude': None,

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'minWeightMagnitude': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_min_weight_magnitude_string(self):
    """
    ``minWeightMagnitude`` is a string.
    """
    self.assertFilterErrors(
      {
        # It's gotta be an int!
        'minWeightMagnitude': '18',

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'minWeightMagnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_float(self):
    """
    ``minWeightMagnitude`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, float values are not valid.
        'minWeightMagnitude': 18.0,

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'minWeightMagnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_too_small(self):
    """
    ``minWeightMagnitude`` is < 1.
    """
    self.assertFilterErrors(
      {
        'minWeightMagnitude': 0,

        'depth':        100,
        'transaction':  TransactionHash(self.trytes1),
      },

      {
        'minWeightMagnitude': [f.Min.CODE_TOO_SMALL],
      },
    )


class PromoteTransactionCommandTestCase(TestCase):
  def setUp(self):
    super(PromoteTransactionCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = PromoteTransactionCommand(self.adapter)

    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

    self.hash1 = TransactionHash(
      b'TESTVALUE9DONTUSEINPRODUCTION99999TBPDM9'
      b'ADFAWCKCSFUALFGETFIFG9UHIEFE9AYESEHDUBDDF'
    )

  def test_wireup(self):
    """
    Verifies that the command is wired-up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).promoteTransaction,
      PromoteTransactionCommand,
    )

  def test_happy_path(self):
    """
    Successfully promoting a bundle.
    """

    self.adapter.seed_response('checkConsistency', {
      'state': True,
    })

    result_bundle = Bundle.from_tryte_strings([
      TransactionTrytes(self.trytes1),
      TransactionTrytes(self.trytes2),
    ])
    mock_send_transfer = mock.Mock(return_value={
      'bundle': result_bundle,
    })

    with mock.patch(
        'iota.commands.extended.send_transfer.SendTransferCommand._execute',
        mock_send_transfer,
    ):

      response = self.command(
        transaction=self.hash1,
        depth=3,
        minWeightMagnitude=16,
      )

    self.assertDictEqual(
      response,

      {
        'bundle': result_bundle,
      }
    )

  def test_not_promotable(self):
    """
    Bundle isn't promotable.
    """

    self.adapter.seed_response('checkConsistency', {
      'state': False,
    })

    with self.assertRaises(BadApiResponse):
      response = self.command(
        transaction=self.hash1,
        depth=3,
        minWeightMagnitude=16,
      )
