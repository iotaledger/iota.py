from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Iota, TransactionTrytes, TryteString, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.store_transactions import StoreTransactionsCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class StoreTransactionsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = StoreTransactionsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(StoreTransactionsRequestFilterTestCase, self).setUp()

    # Define a few valid values here that we can reuse across multiple
    # tests.
    self.trytes1 = 'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_pass_happy_path(self):
    """
    The incoming request is valid.
    """
    request = {
      # Raw trytes are extracted to match the IRI's JSON protocol.
      'trytes': [
        str(TransactionTrytes(self.trytes1)),
        str(TransactionTrytes(self.trytes2)),
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
    filter_ = self._filter({
      # Any value that can be converted into an ASCII representation of
      # a TryteString is allowed here.
      'trytes': [
        TransactionTrytes(self.trytes1),
        bytearray(self.trytes2.encode('ascii')),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        # Raw trytes are extracted to match the IRI's JSON protocol.
        'trytes': [
          str(TransactionTrytes(self.trytes1)),
          str(TransactionTrytes(self.trytes2)),
        ],
      },
    )

  def test_fail_empty(self):
    """
    The incoming request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'trytes': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The incoming value contains unexpected parameters.
    """
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
    """
    ``trytes`` is null.
    """
    self.assertFilterErrors(
      {
        'trytes': None,
      },

      {
        'trytes': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_trytes_wrong_type(self):
    """
    ``trytes`` is not an array.
    """
    self.assertFilterErrors(
      {
        # ``trytes`` has to be an array, even if there's only one
        # TryteString.
        'trytes': TryteString(self.trytes1),
      },

      {
        'trytes': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_trytes_empty(self):
    """
    ``trytes`` is an array, but it's empty.
    """
    self.assertFilterErrors(
      {
        'trytes': [],
      },

      {
        'trytes': [f.Required.CODE_EMPTY],
      },
    )

  def test_trytes_contents_invalid(self):
    """
    ``trytes`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'trytes': [
          b'',
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes2),

          2130706433,

          b'9' * (TransactionTrytes.LEN + 1),
        ],
      },

      {
        'trytes.0': [f.NotEmpty.CODE_EMPTY],
        'trytes.1': [f.Type.CODE_WRONG_TYPE],
        'trytes.2': [f.Required.CODE_EMPTY],
        'trytes.3': [Trytes.CODE_NOT_TRYTES],
        'trytes.5': [f.Type.CODE_WRONG_TYPE],
        'trytes.6': [Trytes.CODE_WRONG_FORMAT],
      },
    )


class StoreTransactionsCommandTestCase(TestCase):
  def setUp(self):
    super(StoreTransactionsCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.store_transactions.StoreTransactionsCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      response = api.store_transactions('trytes')

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
    with patch('iota.commands.core.store_transactions.StoreTransactionsCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      response = await api.store_transactions('trytes')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )