# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from filters.test import BaseFilterTestCase
from six import binary_type

from iota.commands.find_transactions import FindTransactionsRequestFilter
from iota.types import Address, Tag, TransactionId


class FindTransactionsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = FindTransactionsRequestFilter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(FindTransactionsRequestFilterTestCase, self).setUp()

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'
    self.trytes3 = b'999999999999999999999999999'

  def test_pass_all_parameters(self):
    """The request contains valid values for all parameters."""
    request = {
      'bundles': [
        TransactionId(self.trytes1),
        TransactionId(self.trytes2),
      ],

      'addresses': [
        Address(self.trytes1),
        Address(self.trytes2),
      ],

      'tags': [
        Tag(self.trytes1),
        Tag(self.trytes3),
      ],

      'approvees': [
        TransactionId(self.trytes1),
        TransactionId(self.trytes3),
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
      'bundles': [
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],

      'addresses': [
        binary_type(self.trytes1),
        bytearray(self.trytes2),
      ],

      'tags': [
        binary_type(self.trytes1),
        bytearray(self.trytes3),
      ],

      'approvees': [
        binary_type(self.trytes1),
        bytearray(self.trytes3),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'bundles': [
          TransactionId(self.trytes1),
          TransactionId(self.trytes2),
        ],

        'addresses': [
          Address(self.trytes1),
          Address(self.trytes2),
        ],

        'tags': [
          Tag(self.trytes1),
          Tag(self.trytes3),
        ],

        'approvees': [
          TransactionId(self.trytes1),
          TransactionId(self.trytes3),
        ],
      },
    )

  def test_pass_bundles_only(self):
    """The request only includes bundles."""
    request = {
      'bundles': [
        TransactionId(self.trytes1),
        TransactionId(self.trytes2),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'bundles': [
          TransactionId(self.trytes1),
          TransactionId(self.trytes2),
        ],

        'addresses':  [],
        'approvees':  [],
        'tags':       [],
      },
    )

  def test_pass_addresses_only(self):
    """The request only includes addresses."""
    request = {
      'addresses': [
        Address(self.trytes1),
        Address(self.trytes2),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'addresses': [
          Address(self.trytes1),
          Address(self.trytes2),
        ],

        'approvees':  [],
        'bundles':    [],
        'tags':       [],
      },
    )

  def test_pass_tags_only(self):
    """The request only includes tags."""
    request = {
      'tags': [
        Tag(self.trytes1),
        Tag(self.trytes3),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'tags': [
          Tag(self.trytes1),
          Tag(self.trytes3),
        ],

        'addresses':  [],
        'approvees':  [],
        'bundles':    [],
      },
    )

  def test_pass_approvees_only(self):
    """The request only includes approvees."""
    request = {
      'approvees': [
        TransactionId(self.trytes1),
        TransactionId(self.trytes3),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'approvees': [
          TransactionId(self.trytes1),
          TransactionId(self.trytes3),
        ],

        'addresses':  [],
        'bundles':    [],
        'tags':       [],
      },
    )

  def test_fail_empty(self):
    """The request does not contain any parameters."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_all_parameters_empty(self):
    """The request contains all parameters, but every one is empty."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_unexpected_parameters(self):
    """The request contains unexpected parameters."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_bundles_wrong_type(self):
    """`bundles` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_bundles_contents_invalid(self):
    """`bundles` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_addresses_wrong_type(self):
    """`addresses` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_addresses_contents_invalid(self):
    """`addresses` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tags_wrong_type(self):
    """`tags` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_tags_contents_invalid(self):
    """`tags` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_approvees_wrong_type(self):
    """`approvees` is not an array."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')

  def test_fail_approvees_contents_invalid(self):
    """`approvees` is an array, but it contains invalid values."""
    # :todo: Implement test.
    self.skipTest('Not implemented yet.')
