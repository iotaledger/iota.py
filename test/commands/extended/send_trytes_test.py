# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import binary_type, text_type

from iota import Iota, TransactionTrytes, TryteString
from iota.adapter import MockAdapter
from iota.commands.extended.send_trytes import SendTrytesCommand
from iota.filters import Trytes


class SendTrytesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = SendTrytesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(SendTrytesRequestFilterTestCase, self).setUp()

    # These values would normally be a lot longer (2187 trytes, to be
    # exact), but for purposes of this test, we just need a non-empty
    # value.
    self.trytes1 = b'TRYTEVALUEHERE'
    self.trytes2 = b'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'depth':              100,
      'minWeightMagnitude': 18,

      'trytes': [
        TransactionTrytes(self.trytes1),
        TransactionTrytes(self.trytes2),
      ],
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
      # This can accept any TrytesCompatible values.
      'trytes': [
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],

      # These still have to be ints, however.
      'depth':              100,
      'minWeightMagnitude': 18,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'depth':              100,
        'minWeightMagnitude': 18,

        'trytes': [
          TransactionTrytes(self.trytes1),
          TransactionTrytes(self.trytes2),
        ],
      },
    )

  def test_fail_request_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'depth':              [f.FilterMapper.CODE_MISSING_KEY],
        'minWeightMagnitude': [f.FilterMapper.CODE_MISSING_KEY],
        'trytes':             [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_request_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'depth':              100,
        'minWeightMagnitude': 18,
        'trytes':             [TryteString(self.trytes1)],

        # Oh, bother.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
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
        'trytes':             [TryteString(self.trytes1)],
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
        'trytes':             [TryteString(self.trytes1)],
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
        'trytes':             [TryteString(self.trytes1)],
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
        'trytes':             [TryteString(self.trytes1)],
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

        'depth':  100,
        'trytes': [TryteString(self.trytes1)],
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

        'depth':  100,
        'trytes': [TryteString(self.trytes1)],
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

        'depth':  100,
        'trytes': [TryteString(self.trytes1)],
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

        'depth':  100,
        'trytes': [TryteString(self.trytes1)],
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

        'depth':              100,
        'minWeightMagnitude': 18,
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
        # Must be an array, even if there's only one TryteString to
        # send.
        'trytes': TryteString(self.trytes1),

        'depth':              100,
        'minWeightMagnitude': 18,
      },

      {
        'trytes': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_trytes_empty(self):
    """
    ``trytes`` is an array, but it is empty.
    """
    self.assertFilterErrors(
      {
        'trytes': [],

        'depth':              100,
        'minWeightMagnitude': 18,
      },

      {
        'trytes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_trytes_contents_invalid(self):
    """
    ``trytes`` is a non-empty array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'trytes': [
          b'',
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          #   filter isn't cheating!
          TryteString(self.trytes1),

          2130706433,

          b'9' * (TransactionTrytes.LEN + 1),
        ],

        'depth':              100,
        'minWeightMagnitude': 18,
      },

      {
        'trytes.0': [f.Required.CODE_EMPTY],
        'trytes.1': [f.Type.CODE_WRONG_TYPE],
        'trytes.2': [f.Required.CODE_EMPTY],
        'trytes.3': [Trytes.CODE_NOT_TRYTES],
        'trytes.5': [f.Type.CODE_WRONG_TYPE],
        'trytes.6': [Trytes.CODE_WRONG_FORMAT],
      },
    )


class SendTrytesCommandTestCase(TestCase):
  # noinspection SpellCheckingInspection
  def setUp(self):
    super(SendTrytesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = SendTrytesCommand(self.adapter)

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

    self.transaction1 = (
      b'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
      b'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999'
    )

    self.transaction2 = (
      b'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
      b'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999'
    )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).sendTrytes,
      SendTrytesCommand,
    )

  def test_happy_path(self):
    """
    Successful invocation of ``sendTrytes``.
    """
    self.adapter.seed_response('getTransactionsToApprove', {
      'trunkTransaction':   text_type(self.transaction1, 'ascii'),
      'branchTransaction':  text_type(self.transaction2, 'ascii'),
    })

    self.adapter.seed_response('attachToTangle', {
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('broadcastTransactions', {})
    self.adapter.seed_response('storeTransactions', {})

    trytes = [
      TransactionTrytes(self.trytes1),
      TransactionTrytes(self.trytes2),
    ]

    response = self.command(
      trytes              = trytes,
      depth               = 100,
      minWeightMagnitude  = 18,
    )

    self.assertDictEqual(response, {'trytes': trytes})
