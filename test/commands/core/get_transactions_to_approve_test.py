# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, TransactionHash
from iota.adapter import MockAdapter
from iota.commands.core.get_transactions_to_approve import \
  GetTransactionsToApproveCommand
from iota.filters import Trytes


class GetTransactionsToApproveRequestFilterTestCase(BaseFilterTestCase):
  filter_type =\
    GetTransactionsToApproveCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetTransactionsToApproveRequestFilterTestCase, self).setUp()

    # Define some tryte sequences that we can reuse between tests.
    self.trytes1 = (
      b'TESTVALUEONE9DONTUSEINPRODUCTION99999JBW'
      b'GEC99GBXFFBCHAEJHLC9DX9EEPAI9ICVCKBX9FFII'
    )

  def test_pass_happy_path_without_reference(self):
    """
    Request is valid without reference.
    """
    request = {
      'depth': 100,
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_happy_path_with_reference(self):
    """
    Request is valid with reference.
    """
    request = {
      'depth': 100,
      'reference': TransactionHash(self.trytes1),
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'depth': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'depth': 100,

        # I knew I should have taken that left turn at Albuquerque.
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
      },

      {
        'depth': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_depth_float(self):
    """
    ``depth`` is a float.
    """
    self.assertFilterErrors(
      {
        'depth': 100.0,
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_string(self):
    """
    ``depth`` is a string.
    """
    self.assertFilterErrors(
      {
        'depth': '100',
      },

      {
        'depth': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_depth_too_small(self):
    """
    ``depth`` is less than 1.
    """
    self.assertFilterErrors(
      {
        'depth': 0,
      },

      {
        'depth': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_reference_wrong_type(self):
    """
    ``reference`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'reference': 42,

        'depth': 100,
      },

      {
        'reference': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_reference_not_trytes(self):
    """
    ``reference`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'reference': b'not valid; must contain only uppercase and "9"',

        'depth': 100,
      },

      {
        'reference': [Trytes.CODE_NOT_TRYTES],
      },
    )


class GetTransactionsToApproveResponseFilterTestCase(BaseFilterTestCase):
  filter_type =\
    GetTransactionsToApproveCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def test_pass_happy_path(self):
    """
    Typical ``getTransactionsToApprove`` response.
    """
    response = {
      'trunkTransaction':
        'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
        'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999',

      'branchTransaction':
        'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
        'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999',

      'duration': 936,
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'trunkTransaction':
          TransactionHash(
            b'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
            b'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999'
          ),

        'branchTransaction':
          TransactionHash(
            b'TKGDZ9GEI9CPNQGHEATIISAKYPPPSXVCXBSR9EIW'
            b'CTHHSSEQCD9YLDPEXYERCNJVASRGWMAVKFQTC9999'
          ),

        'duration': 936,
      },
    )


class GetTransactionsToApproveTestCase(TestCase):
  def setUp(self):
    super(GetTransactionsToApproveTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getTransactionsToApprove,
      GetTransactionsToApproveCommand,
    )
