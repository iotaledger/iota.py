# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, TransactionHash
from iota.adapter import MockAdapter
from iota.commands.extended.get_bundles import GetBundlesCommand
from iota.filters import Trytes
from six import binary_type, text_type


class GetBundlesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetBundlesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetBundlesRequestFilterTestCase, self).setUp()

    # noinspection SpellCheckingInspection
    self.transaction = (
      b'ORLSCIMM9ZONOUSPYYWLOEMXQZLYEHCBEDQSHZOG'
      b'OPZCZCDZYTDPGEEUXWUZ9FQYCT9OGS9PICOOX9999'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'transaction': TransactionHash(self.transaction)
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
      # Any TrytesCompatible value will work here.
      'transaction': binary_type(self.transaction),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'transaction': TransactionHash(self.transaction),
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'transaction': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'transaction': TransactionHash(self.transaction),

        # SAY "WHAT" AGAIN!
        'what': 'augh!',
      },

      {
        'what': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transaction_wrong_type(self):
    """
    ``transaction`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'transaction': text_type(self.transaction, 'ascii'),
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
      },

      {
        'transaction': [Trytes.CODE_NOT_TRYTES],
      },
    )


class GetBundlesCommandTestCase(TestCase):
  def setUp(self):
    super(GetBundlesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verifies that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getBundles,
      GetBundlesCommand,
    )

  # :todo: Unit tests.
