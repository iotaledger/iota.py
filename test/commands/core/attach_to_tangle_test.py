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
      'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999'
    )

    self.trytes1 = 'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """
    The incoming request is valid.
    """
    request = {
      'trunkTransaction':   text_type(TransactionHash(self.txn_id)),
      'branchTransaction':  text_type(TransactionHash(self.txn_id)),
      'minWeightMagnitude': 20,

      'trytes': [
        # Raw trytes are extracted to match the IRI's JSON protocol.
        text_type(TransactionTrytes(self.trytes1)),
        text_type(TransactionTrytes(self.trytes2)),
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
      # Any value that can be converted into an ASCII representation of
      # a TransactionHash is valid here.
      'trunkTransaction':   TransactionHash(self.txn_id),
      'branchTransaction':  bytearray(self.txn_id.encode('ascii')),

      'trytes': [
        # ``trytes`` can contain any value that can be converted into a
        # TryteString.
        binary_type(TransactionTrytes(self.trytes1)),

        # This is probably wrong (s/b :py:class:`TransactionTrytes`),
        # but technically it's valid.
        TransactionHash(
          b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA',
        ),
      ],

      # This still has to be an int, however.
      'minWeightMagnitude': 30,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      # After running through the filter, all of the values have been
      # converted to the correct types.
      {
        'trunkTransaction':   self.txn_id,
        'branchTransaction':  self.txn_id,
        'minWeightMagnitude': 30,

        'trytes':               [
          text_type(TransactionTrytes(self.trytes1)),

          text_type(TransactionTrytes(
            b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHD'
            b'WCTCEAKDCDFD9DSCSA99999999999999999999999',
          )),
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
        'branchTransaction':  [f.FilterMapper.CODE_MISSING_KEY],
        'minWeightMagnitude': [f.FilterMapper.CODE_MISSING_KEY],
        'trunkTransaction':   [f.FilterMapper.CODE_MISSING_KEY],
        'trytes':             [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The incoming request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'branchTransaction':  TransactionHash(self.txn_id),
        'minWeightMagnitude': 20,
        'trunkTransaction':   TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],

        # Hey, how'd that get in there?
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_trunk_transaction_null(self):
    """
    ``trunkTransaction`` is null.
    """
    self.assertFilterErrors(
      {
        'trunkTransaction':  None,

        'branchTransaction':  TransactionHash(self.txn_id),
        'minWeightMagnitude': 13,
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'trunkTransaction': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_trunk_transaction_wrong_type(self):
    """
    ``trunkTransaction`` can't be converted to a TryteString.
    """
    self.assertFilterErrors(
      {
        # What do you get when you multiply 0-+ by 00+?
        'trunkTransaction': 42,

        'branchTransaction':  TransactionHash(self.txn_id),
        'minWeightMagnitude': 13,
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'trunkTransaction': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_branch_transaction_null(self):
    """
    ``branchTransaction`` is null.
    """
    self.assertFilterErrors(
      {
        'branchTransaction': None,

        'minWeightMagnitude': 13,
        'trunkTransaction':   TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'branchTransaction': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_branch_transaction_wrong_type(self):
    """
    ``branchTransaction`` can't be converted to a TryteString.
    """
    self.assertFilterErrors(
      {
        # What do you get when you multiply 0-+ by 00+?
        'branchTransaction': 42,

        'minWeightMagnitude': 13,
        'trunkTransaction':   TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'branchTransaction': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_null(self):
    """
    ``minWeightMagnitude`` is null.
    """
    self.assertFilterErrors(
      {
        'minWeightMagnitude': None,

        'branchTransaction':  TransactionHash(self.txn_id),
        'trunkTransaction':   TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'minWeightMagnitude': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_min_weight_magnitude_float(self):
    """
    ``minWeightMagnitude`` is a float.
    """
    self.assertFilterErrors(
      {
        # I don't care if the fpart is empty; it's still not an int!
        'minWeightMagnitude': 20.0,

        'branchTransaction':  TransactionHash(self.txn_id),
        'trunkTransaction':   TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'minWeightMagnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_string(self):
    """
    ``minWeightMagnitude`` is a string.
    """
    self.assertFilterErrors(
      {
        # For want of an int cast, the transaction was lost.
        'minWeightMagnitude': '20',

        'branchTransaction':  TransactionHash(self.txn_id),
        'trunkTransaction':   TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'minWeightMagnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_too_small(self):
    """
    ``minWeightMagnitude`` is less than 1.
    """
    self.assertFilterErrors(
      {
        'minWeightMagnitude': 0,

        'branchTransaction':  TransactionHash(self.txn_id),
        'trunkTransaction':   TransactionHash(self.txn_id),
        'trytes':             [TryteString(self.trytes1)],
      },

      {
        'minWeightMagnitude': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_trytes_null(self):
    """
    ``trytes`` is null.
    """
    self.assertFilterErrors(
      {
        'trytes': None,

        'branchTransaction':  TransactionHash(self.txn_id),
        'minWeightMagnitude': 13,
        'trunkTransaction':   TransactionHash(self.txn_id),
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

        'branchTransaction':  TransactionHash(self.txn_id),
        'minWeightMagnitude': 13,
        'trunkTransaction':   TransactionHash(self.txn_id),
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

        'branchTransaction':  TransactionHash(self.txn_id),
        'minWeightMagnitude': 13,
        'trunkTransaction':   TransactionHash(self.txn_id),
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
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes2),

          2130706433,

          b'9' * (TransactionTrytes.LEN + 1),
        ],

        'branchTransaction':  TransactionHash(self.txn_id),
        'minWeightMagnitude': 13,
        'trunkTransaction':   TransactionHash(self.txn_id),
      },

      {
        'trytes.0': [f.NotEmpty.CODE_EMPTY],
        'trytes.1': [f.Type.CODE_WRONG_TYPE],
        'trytes.2': [f.Required.CODE_EMPTY],
        'trytes.3': [Trytes.CODE_NOT_TRYTES],
        'trytes.5': [f.Type.CODE_WRONG_TYPE],
        'trytes.6': [Trytes.CODE_WRONG_FORMAT],
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
    self.trytes1 = 'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """
    The incoming response contains valid values.
    """
    filter_ = self._filter({
      # Trytes arrive from the node as strings.
      'trytes': [
        self.trytes1,
        self.trytes2,
      ],

      'duration': 42,
    })

    self.assertFilterPasses(filter_)

    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'trytes': [
          TransactionTrytes(self.trytes1),
          TransactionTrytes(self.trytes2),
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
