# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from filters.test import BaseFilterTestCase
from iota.commands.send_trytes import SendTrytesCommand
from iota.filters import Trytes
from iota.types import TryteString
from six import binary_type, text_type
from test import MockAdapter


class SendTrytesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = SendTrytesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(SendTrytesRequestFilterTestCase, self).setUp()

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """
    The incoming request is valid.
    """
    request = {
      'trytes': [
        TryteString(self.trytes1),
        TryteString(self.trytes2),
      ],

      'depth': 100,
      'min_weight_magnitude': 18,
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    The request contains values that can be converted to the expected
    types.
    """
    filter_ = self._filter({
      'trytes': [
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],

      # These values still have to be ints.
      'depth': 100,
      'min_weight_magnitude': 18,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'trytes': [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],

        'depth': 100,
        'min_weight_magnitude': 18,
      },
    )

  def test_pass_min_weight_magnitude_missing(self):
    """
    ``min_weight_magnitude`` is optional.
    """
    filter_ = self._filter({
      'trytes': [TryteString(self.trytes1)],
      'depth':  100,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'trytes': [TryteString(self.trytes1)],
        'depth':  100,

        # Default value is used if not included in request.
        'min_weight_magnitude': 18,
      }
    )

  def test_fail_empty(self):
    """
    The request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'trytes': [f.FilterMapper.CODE_MISSING_KEY],
        'depth':  [f.FilterMapper.CODE_MISSING_KEY],
      }
    )

  def test_fail_unexpected_parameters(self):
    """The incoming value contains unexpected parameters."""
    self.assertFilterErrors(
      {
        'trytes': [TryteString(self.trytes1)],
        'depth':  100,
        'min_weight_magnitude': 18,

        # Aw, and you were doing so well!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_trytes_null(self):
    """`trytes` is null."""
    self.assertFilterErrors(
      {
        'trytes': None,
        'depth':  100,
      },

      {
        'trytes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_trytes_wrong_type(self):
    """`trytes` is not an array."""
    self.assertFilterErrors(
      {
        # `trytes` has to be an array, even if there's only one
        #   TryteString.
        'trytes': TryteString(self.trytes1),
        'depth':  100,
      },

      {
        'trytes': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_trytes_empty(self):
    """`trytes` is an array, but it's empty."""
    self.assertFilterErrors(
      {
        'trytes': [],
        'depth':  100,
      },

      {
        'trytes': [f.Required.CODE_EMPTY],
      },
    )

  def test_trytes_contents_invalid(self):
    """`trytes` is an array, but it contains invalid values."""
    self.assertFilterErrors(
      {
        'trytes': [
          b'',
          text_type(self.trytes1, 'ascii'),
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          #   filter isn't cheating!
          TryteString(self.trytes2),

          2130706433,
        ],

        'depth': 100,
      },

      {
        'trytes.0': [f.NotEmpty.CODE_EMPTY],
        'trytes.1': [f.Type.CODE_WRONG_TYPE],
        'trytes.2': [f.Type.CODE_WRONG_TYPE],
        'trytes.3': [f.Required.CODE_EMPTY],
        'trytes.4': [Trytes.CODE_NOT_TRYTES],
        'trytes.6': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_float(self):
    """`depth` is a float."""
    self.assertFilterErrors(
      {
        'depth':  100.0,
        'trytes': [TryteString(self.trytes1)],
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_string(self):
    """`depth` is a string."""
    self.assertFilterErrors(
      {
        'depth':  '100',
        'trytes': [TryteString(self.trytes1)],
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_too_small(self):
    """`depth` is less than 1."""
    self.assertFilterErrors(
      {
        'depth':  0,
        'trytes': [TryteString(self.trytes1)],
      },

      {
        'depth': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_min_weight_magnitude_float(self):
    """`min_weight_magnitude` is a float."""
    self.assertFilterErrors(
      {
        # I don't care if the fpart is empty; it's still not an int!
        'min_weight_magnitude': 20.0,

        'depth':  100,
        'trytes': [TryteString(self.trytes1)],
      },

      {
        'min_weight_magnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_string(self):
    """`min_weight_magnitude` is a string."""
    self.assertFilterErrors(
      {
        # For want of an int cast, the transaction was lost.
        'min_weight_magnitude': '20',

        'depth':  100,
        'trytes': [TryteString(self.trytes1)],
      },

      {
        'min_weight_magnitude': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_min_weight_magnitude_too_small(self):
    """`min_weight_magnitude` is less than 18."""
    self.assertFilterErrors(
      {
        'min_weight_magnitude': 17,

        'depth':  100,
        'trytes': [TryteString(self.trytes1)],
      },

      {
        'min_weight_magnitude': [f.Min.CODE_TOO_SMALL],
      },
    )
