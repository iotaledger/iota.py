# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, TransactionHash, TransactionTrytes, TryteString
from iota.adapter import MockAdapter
from iota.commands.core.attach_to_tangle import AttachToTangleCommand
from iota.filters import Trytes
from six import binary_type, text_type


class AttachToTangleRequestFilterTestCase(BaseFilterTestCase):
  filter_type = AttachToTangleCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(AttachToTangleRequestFilterTestCase, self).setUp()

    # Define a few valid values here that we can reuse across multiple
    # tests.
    self.txn_id = (
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
    )

    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """
    The incoming request is valid.
    """
    request = {
      'trunk_transaction':    TransactionHash(self.txn_id),
      'branch_transaction':   TransactionHash(self.txn_id),
      'min_weight_magnitude': 20,

      'trytes':               [
        TransactionTrytes(self.trytes1),
        TransactionTrytes(self.trytes2),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  # noinspection SpellCheckingInspection
  def test_pass_compatible_types(self):
    """
    Incoming values can be converted into the expected types.
    """
    filter_ = self._filter({
      # Any value that can be converted into a TransactionHash is valid
      #   here.
      'trunk_transaction':    binary_type(self.txn_id),
      'branch_transaction':   bytearray(self.txn_id),

      'trytes': [
        # ``trytes`` can contain any value that can be converted into a
        # TryteString.
        binary_type(self.trytes1),

        # This is probably wrong, but technically it's valid.
        TransactionHash(
          b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA',
        ),
      ],

      # This still has to be an int, however.
      'min_weight_magnitude': 30,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      # After running through the filter, all of the values have been
      # converted to the correct types.
      {
        'trunk_transaction':    TransactionHash(self.txn_id),
        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 30,

        'trytes':               [
          TransactionTrytes(self.trytes1),

          TransactionTrytes(
            b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHD'
            b'WCTCEAKDCDFD9DSCSA99999999999999999999999',
          ),
        ],
      }
    )

  def test_fail_empty(self):
    """
    The incoming request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'branch_transaction':   [f.FilterMapper.CODE_MISSING_KEY],
        'min_weight_magnitude': [f.FilterMapper.CODE_MISSING_KEY],
        'trunk_transaction':    [f.FilterMapper.CODE_MISSING_KEY],
        'trytes':               [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The incoming request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 20,
        'trunk_transaction':    TransactionHash(self.txn_id),
        'trytes':               [TryteString(self.trytes1)],

        # Hey, how'd that get in there?
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_trunk_transaction_null(self):
    """
    ``trunk_transaction`` is null.
    """
    self.assertFilterErrors(
      {
        'trunk_transaction':  None,

        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 13,
        'trytes':               [TryteString(self.trytes1)],
      },

      {
        'trunk_transaction': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_trunk_transaction_wrong_type(self):
    """
    ``trunk_transaction`` can't be converted to a TryteString.
    """
    self.assertFilterErrors(
      {
        # Strings are not valid tryte sequences.
        'trunk_transaction':  text_type(self.txn_id, 'ascii'),

        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 13,
        'trytes':               [TryteString(self.trytes1)],
      },

      {
        'trunk_transaction': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_branch_transaction_null(self):
    """
    ``branch_transaction`` is null.
    """
    self.assertFilterErrors(
      {
        'branch_transaction': None,

        'min_weight_magnitude': 13,
        'trunk_transaction':    TransactionHash(self.txn_id),
        'trytes':               [TryteString(self.trytes1)],
      },

      {
        'branch_transaction': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_branch_transaction_wrong_type(self):
    """
    ``branch_transaction`` can't be converted to a TryteString.
    """
    self.assertFilterErrors(
      {
        # Strings are not valid tryte sequences.
        'branch_transaction': text_type(self.txn_id, 'ascii'),

        'min_weight_magnitude': 13,
        'trunk_transaction':    TransactionHash(self.txn_id),
        'trytes':               [TryteString(self.trytes1)],
      },

      {
        'branch_transaction': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_null(self):
    """
    ``min_weight_magnitude`` is null.
    """
    self.assertFilterErrors(
      {
        'min_weight_magnitude': None,

        'branch_transaction': TransactionHash(self.txn_id),
        'trunk_transaction':  TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'min_weight_magnitude': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_min_weight_magnitude_float(self):
    """
    ``min_weight_magnitude`` is a float.
    """
    self.assertFilterErrors(
      {
        # I don't care if the fpart is empty; it's still not an int!
        'min_weight_magnitude': 20.0,

        'branch_transaction': TransactionHash(self.txn_id),
        'trunk_transaction':  TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'min_weight_magnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_string(self):
    """
    ``min_weight_magnitude`` is a string.
    """
    self.assertFilterErrors(
      {
        # For want of an int cast, the transaction was lost.
        'min_weight_magnitude': '20',

        'branch_transaction': TransactionHash(self.txn_id),
        'trunk_transaction':  TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'min_weight_magnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_too_small(self):
    """
    ``min_weight_magnitude`` is less than 1.
    """
    self.assertFilterErrors(
      {
        'min_weight_magnitude': 0,

        'branch_transaction': TransactionHash(self.txn_id),
        'trunk_transaction':  TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'min_weight_magnitude': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_trytes_null(self):
    """
    ``trytes`` is null.
    """
    self.assertFilterErrors(
      {
        'trytes': None,

        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 13,
        'trunk_transaction':    TransactionHash(self.txn_id),
      },

      {
        'trytes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_trytes_wrong_type(self):
    """
    ``trytes`` is not an array.
    """
    self.assertFilterErrors(
      {
        # You have to specify an array, even if you only want to attach
        # a single tryte sequence.
        'trytes': TryteString(self.trytes1),

        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 13,
        'trunk_transaction':    TransactionHash(self.txn_id),
      },

      {
        'trytes': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_trytes_empty(self):
    """
    ``trytes`` is an array, but it's empty.
    """
    self.assertFilterErrors(
      {
        # Ok, you got the list part down, but you have to put something
        # inside it.
        'trytes': [],

        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 13,
        'trunk_transaction':    TransactionHash(self.txn_id),
      },

      {
        'trytes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_trytes_contents_invalid(self):
    """
    ``trytes`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'trytes':             [
          b'',
          text_type(self.trytes1, 'ascii'),
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes2),

          2130706433,

          b'9' * (TransactionTrytes.LEN + 1),
        ],

        'branch_transaction':   TransactionHash(self.txn_id),
        'min_weight_magnitude': 13,
        'trunk_transaction':    TransactionHash(self.txn_id),
      },

      {
        'trytes.0': [f.NotEmpty.CODE_EMPTY],
        'trytes.1': [f.Type.CODE_WRONG_TYPE],
        'trytes.2': [f.Type.CODE_WRONG_TYPE],
        'trytes.3': [f.Required.CODE_EMPTY],
        'trytes.4': [Trytes.CODE_NOT_TRYTES],
        'trytes.6': [f.Type.CODE_WRONG_TYPE],
        'trytes.7': [Trytes.CODE_WRONG_FORMAT],
      },
    )


class AttachToTangleResponseFilterTestCase(BaseFilterTestCase):
  filter_type = AttachToTangleCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(AttachToTangleResponseFilterTestCase, self).setUp()

    # Define a few valid values here that we can reuse across multiple
    #   tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """The incoming response contains valid values."""
    filter_ = self._filter({
      # Trytes arrive from the node as strings.
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],

      'duration': 42,
    })

    self.assertFilterPasses(filter_)

    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'trytes': [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],

        'duration': 42,
      },
    )


class AttachToTangleCommandTestCase(TestCase):
  def setUp(self):
    super(AttachToTangleCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).attachToTangle,
      AttachToTangleCommand,
    )
