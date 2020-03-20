from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Address, Iota, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.is_reattachable import IsReattachableCommand
from test import patch, MagicMock, async_test


class IsReattachableRequestFilterTestCase(BaseFilterTestCase):
  filter_type = IsReattachableCommand(MockAdapter()).get_request_filter
  skip_value_check = True

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
          str(Address(self.address_1)),
          str(Address(self.address_2))
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


class IsReattachableResponseFilterTestCase(BaseFilterTestCase):
  filter_type = IsReattachableCommand(MockAdapter()).get_response_filter
  skip_value_check = True

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
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.is_reattachable.IsReattachableCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.is_reattachable('addresses')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_wireup_async(self):
    """
    Verify that the command is wired up correctly. (async)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.is_reattachable.IsReattachableCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.is_reattachable('addresses')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )