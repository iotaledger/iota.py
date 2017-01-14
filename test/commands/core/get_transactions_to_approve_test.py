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


class GetTransactionsToApproveRequestFilterTestCase(BaseFilterTestCase):
  filter_type =\
    GetTransactionsToApproveCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'depth': 100,
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
