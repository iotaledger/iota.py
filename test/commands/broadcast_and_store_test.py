# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f
from filters.test import BaseFilterTestCase
from iota.commands.broadcast_and_store import BroadcastAndStoreCommand
from iota.filters import Trytes
from iota.types import TryteString
from six import binary_type, text_type
from test import MockAdapter


class BroadcastAndStoreRequestFilterTestCase(BaseFilterTestCase):
  filter_type = BroadcastAndStoreCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(BroadcastAndStoreRequestFilterTestCase, self).setUp()

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """The incoming request is valid."""
    request = {
      'trytes': [
        TryteString(self.trytes1),
        TryteString(self.trytes2),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    The incoming request contains values that can be converted into the
      expected types.
    """
    # Any values that can be converted into TryteStrings are accepted.
    filter_ = self._filter({
      'trytes': [
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      # The values are converted into TryteStrings so that they can be
      #   sent to the node.
      {
        'trytes': [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],
      },
    )

  def test_fail_empty(self):
    """The incoming request is empty."""
    self.assertFilterErrors(
      {},

      {
        'trytes': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """The incoming value contains unexpected parameters."""
    self.assertFilterErrors(
      {
        'trytes': [TryteString(self.trytes1)],

        # Alright buddy, let's see some ID.
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

class BroadcastAndStoreResponseFilterTestCase(BaseFilterTestCase):
  filter_type = BroadcastAndStoreCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(BroadcastAndStoreResponseFilterTestCase, self).setUp()

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """The incoming response contains valid values."""
    # Responses from the node arrive as strings.
    filter_ = self._filter({
      'trytes': [
        text_type(self.trytes1, 'ascii'),
        text_type(self.trytes2, 'ascii'),
      ],
    })

    self.assertFilterPasses(filter_)

    # The filter converts them into TryteStrings.
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'trytes': [
          TryteString(self.trytes1),
          TryteString(self.trytes2),
        ],
      },
    )

  def test_pass_correct_types(self):
    """
    The incoming response already contains correct types.

    This scenario is highly unusual, but who's complaining?
    """
    response = {
      'trytes': [
        TryteString(self.trytes1),
        TryteString(self.trytes2),
      ]
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, response)
