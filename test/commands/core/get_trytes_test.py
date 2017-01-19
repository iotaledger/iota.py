# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, TransactionHash, TryteString
from iota.adapter import MockAdapter
from iota.commands.core.get_trytes import GetTrytesCommand
from iota.filters import Trytes
from six import binary_type, text_type


class GetTrytesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetTrytesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetTrytesRequestFilterTestCase, self).setUp()

    # Define some valid tryte sequences that we can re-use between
    # tests.
    self.trytes1 = (
      b'OAATQS9VQLSXCLDJVJJVYUGONXAXOFMJOZNSYWRZ'
      b'SWECMXAQQURHQBJNLD9IOFEPGZEPEMPXCIVRX9999'
    )

    self.trytes2 = (
      b'ZIJGAJ9AADLRPWNCYNNHUHRRAC9QOUDATEDQUMTN'
      b'OTABUVRPTSTFQDGZKFYUUIE9ZEBIVCCXXXLKX9999'
    )

  def test_pass_happy_path(self):
    """
    The request is valid.
    """
    request = {
      'hashes': [
        TransactionHash(self.trytes1),
        TransactionHash(self.trytes2),
      ],
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
      'hashes': [
        # Any sequence that can be converted into a TransactionHash is
        # valid.
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'hashes': [
          TransactionHash(self.trytes1),
          TransactionHash(self.trytes2),
        ],
      },
    )

  def test_fail_empty(self):
    """
    The request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'hashes': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'hashes': [TransactionHash(self.trytes1)],

        # This is why we can't have nice things!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_hashes_null(self):
    """
    ``hashes`` is null.
    """
    self.assertFilterErrors(
      {
        'hashes': None,
      },

      {
        'hashes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_hashes_wrong_type(self):
    """
    ``hashes`` is not an array.
    """
    self.assertFilterErrors(
      {
        # ``hashes`` must be an array, even if we're only querying
        # against a single transaction.
        'hashes': TransactionHash(self.trytes1),
      },

      {
        'hashes': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_hashes_empty(self):
    """
    ``hashes`` is an array, but it is empty.
    """
    self.assertFilterErrors(
      {
        'hashes': [],
      },

      {
        'hashes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_hashes_contents_invalid(self):
    """
    ``hashes`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'hashes': [
          b'',
          text_type(self.trytes1, 'ascii'),
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes1),

          2130706433,
          b'9' * 82,
        ],
      },

      {
        'hashes.0': [f.Required.CODE_EMPTY],
        'hashes.1': [f.Type.CODE_WRONG_TYPE],
        'hashes.2': [f.Type.CODE_WRONG_TYPE],
        'hashes.3': [f.Required.CODE_EMPTY],
        'hashes.4': [Trytes.CODE_NOT_TRYTES],
        'hashes.6': [f.Type.CODE_WRONG_TYPE],
        'hashes.7': [Trytes.CODE_WRONG_FORMAT],
      },
    )


class GetTrytesResponseFilter(BaseFilterTestCase):
  filter_type = GetTrytesCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(GetTrytesResponseFilter, self).setUp()

    # Define some valid tryte sequences that we can re-use between
    # tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_transactions(self):
    """
    The response contains data for multiple transactions.
    """
    filter_ = self._filter({
      'trytes': [
        # In real life, these values would be a lot longer, but for the
        # purposes of this test, any sequence of trytes will do.
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

  def test_pass_no_transactions(self):
    """
    The response does not contain any transactions.
    """
    response = {
      'trytes': [],
      'duration': 42,
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, response)


class GetTrytesCommandTestCase(TestCase):
  def setUp(self):
    super(GetTrytesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getTrytes,
      GetTrytesCommand,
    )
