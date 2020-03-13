from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, TransactionHash, TryteString, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.get_trytes import GetTrytesCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class GetTrytesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetTrytesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetTrytesRequestFilterTestCase, self).setUp()

    # Define some valid tryte sequences that we can re-use between
    # tests.
    self.trytes1 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999DLPDTB'
      'XBXYOMQ9IWPKCDPNWBENBGHCSZDLRLZZ9VZEOHPLC'
    )

    self.trytes2 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999HEXCAN'
      'LFTVWRDZJHDWJGVOOUWBXAHKVWDNNOCICGXXBKAEN'
    )

  def test_pass_happy_path(self):
    """
    The request is valid.
    """
    request = {
      # Raw trytes are extracted to match the IRI's JSON protocol.
      'hashes': [self.trytes1, self.trytes2],
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
      # Any sequence that can be converted into an ASCII representation
      # of a TransactionHash is valid.
      'hashes': [
        TransactionHash(self.trytes1),
        bytearray(self.trytes2.encode('ascii')),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'hashes': [self.trytes1, self.trytes2],
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
        'hashes.2': [f.Required.CODE_EMPTY],
        'hashes.3': [Trytes.CODE_NOT_TRYTES],
        'hashes.5': [f.Type.CODE_WRONG_TYPE],
        'hashes.6': [Trytes.CODE_WRONG_FORMAT],
      },
    )


class GetTrytesResponseFilter(BaseFilterTestCase):
  filter_type = GetTrytesCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  def setUp(self):
    super(GetTrytesResponseFilter, self).setUp()

    # Define some valid tryte sequences that we can re-use between
    # tests.
    self.trytes1 = 'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_transactions(self):
    """
    The response contains data for multiple transactions.
    """
    filter_ = self._filter({
      'trytes': [
        # In real life, these values would be a lot longer, but for the
        # purposes of this test, any sequence of trytes will do.
        self.trytes1,
        self.trytes2,
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
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.get_trytes.GetTrytesCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      response = api.get_trytes('hashes')

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
    with patch('iota.commands.core.get_trytes.GetTrytesCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      response = await api.get_trytes('hashes')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )