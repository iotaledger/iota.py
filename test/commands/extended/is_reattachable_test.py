# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from six import text_type

from iota import Address, Iota
from iota.adapter import MockAdapter
from iota.commands.extended.is_reattachable import IsReattachableCommand


class IsReattachableRequestFilterTestCase(BaseFilterTestCase):
  filter_type = IsReattachableCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(IsReattachableRequestFilterTestCase, self).setUp()

    # Define a few valid values that we can reuse across tests.
    self.address_1 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999EKJZZT'
      'SOGJOUNVEWLDPKGTGAOIZIPMGBLHC9LMQNHLGXGYX'
    )

    self.address_2 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999FDCDTZ'
      'ZWLL9MYGUTLSYVSIFJ9NGALTRMCQVIIOVEQOITYTE'
    )

  def test_pass_happy_path(self):
    """
    Filter for list of valid string addresses
    """

    request = {
      # Raw trytes are extracted to match the IRI's JSON protocol.
      'addresses': [
        self.address_1,
        Address(self.address_2)
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)

    self.assertDictEqual(
      filter_.cleaned_data,
      {
        'addresses': [
          text_type(Address(self.address_1)),
          text_type(Address(self.address_2))
        ],
      },
    )

  def test_pass_compatible_types(self):
    """
    The incoming request contains values that can be converted to the
    expected types.
    """
    request = {
      'addresses': [
        Address(self.address_1),
        bytearray(self.address_2.encode('ascii')),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,
      {
        'addresses': [self.address_1, self.address_2],
      },
    )

  def test_pass_incompatible_types(self):
    """
    The incoming request contains values that can NOT be converted to the
    expected types.
    """
    request = {
      'addresses': [
        1234234,
        False
      ],
    }

    self.assertFilterErrors(
      request,
      {
        'addresses.0': [f.Type.CODE_WRONG_TYPE],
        'addresses.1': [f.Type.CODE_WRONG_TYPE]
      },
    )

  def test_fail_empty(self):
    """
    The incoming request is empty.
    """
    self.assertFilterErrors(
      {},
      {
        'addresses': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_single_address(self):
    """
    The incoming request contains a single address
    """
    request = {
      'addresses': Address(self.address_1)
    }

    self.assertFilterErrors(
      request,
      {
        'addresses': [f.Type.CODE_WRONG_TYPE],
      }
    )


# noinspection SpellCheckingInspection
class IsReattachableResponseFilterTestCase(BaseFilterTestCase):
  filter_type = IsReattachableCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(IsReattachableResponseFilterTestCase, self).setUp()

    # Define a few valid values that we can reuse across tests.
    self.addresses_1 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999EKJZZT'
      'SOGJOUNVEWLDPKGTGAOIZIPMGBLHC9LMQNHLGXGYX'
    )

  def test_pass_happy_path(self):
    """
    Typical ``IsReattachable`` request.
    """
    response = {
      'reattachable': [True, False]
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, response)

  def test_fail_empty(self):
    """
    The incoming response is empty.
    """
    self.assertFilterErrors(
      {},
      {
        'reattachable': [f.Required.CODE_EMPTY],
      },
    )

  def test_pass_incompatible_types(self):
    """
    The response contains values that can NOT be converted to the
    expected types.
    """
    request = {
      'reattachable': [
        1234234,
        b'',
        'test'
      ],
    }

    self.assertFilterErrors(
      request,
      {
        'reattachable.0': [f.Type.CODE_WRONG_TYPE],
        'reattachable.1': [f.Type.CODE_WRONG_TYPE],
        'reattachable.2': [f.Type.CODE_WRONG_TYPE]
      },
    )


class IsReattachableCommandTestCase(TestCase):
  def setUp(self):
    super(IsReattachableCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).isReattachable,
      IsReattachableCommand,
    )
