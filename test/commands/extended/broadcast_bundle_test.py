from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, BadApiResponse, Bundle, BundleHash, Fragment, Hash, \
  Iota, AsyncIota, Tag, Transaction, TransactionHash, TransactionTrytes, Nonce
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.broadcast_bundle import BroadcastBundleCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


# RequestFilterTestCase code reused from get_bundles_test.py
class BroadcastBundleRequestFilterTestCase(BaseFilterTestCase):
  filter_type = BroadcastBundleCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(BroadcastBundleRequestFilterTestCase, self).setUp()

    self.transaction = (
      'TESTVALUE9DONTUSEINPRODUCTION99999KPZOTR'
      'VDB9GZDJGZSSDCBIX9QOK9PAV9RMDBGDXLDTIZTWQ'
    )

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    # Raw trytes are extracted to match the IRI's JSON protocol.
    request = {
      'tail_hash': self.transaction,
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
      'tail_hash': TransactionHash(self.transaction),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'tail_hash': self.transaction,
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'tail_hash': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'tail_hash': TransactionHash(self.transaction),

        # SAY "WHAT" AGAIN!
        'what': 'augh!',
      },

      {
        'what': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transaction_wrong_type(self):
    """
    ``tail_hash`` is not a TrytesCompatible value.
    """
    self.assertFilterErrors(
      {
        'tail_hash': 42,
      },

      {
        'tail_hash': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_transaction_not_trytes(self):
    """
    ``tail_hash`` contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'tail_hash': b'not valid; must contain only uppercase and "9"',
      },

      {
        'tail_hash': [Trytes.CODE_NOT_TRYTES],
      },
    )

class BroadcastBundleCommandTestCase(TestCase):
  def setUp(self):
    super(BroadcastBundleCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = BroadcastBundleCommand(self.adapter)

    self.tail = (
      'TESTVALUE9DONTUSEINPRODUCTION99999999999'
    )

    self.trytes = [
      'TESTVALUE9DONTUSEINPRODUCTION99999TRYTESFORTRANSACTION1',
      'TESTVALUE9DONTUSEINPRODUCTION99999TRYTESFORTRANSACTION2'
    ]

    self.trytes_dummy = [
      'TESTVALUE9DONTUSEINPRODUCTION99999TRYTESFORTRANSACTION3',
      'TESTVALUE9DONTUSEINPRODUCTION99999TRYTESFORTRANSACTION4'
    ]
    
  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.broadcast_bundle.BroadcastBundleCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.broadcast_bundle('trytes')

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
    with patch('iota.commands.extended.broadcast_bundle.BroadcastBundleCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.broadcast_bundle('trytes')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )
    
  @async_test
  async def test_happy_path(self):
    """
    Test command flow executes as expected.
    """
    # Call the command with a tail hash.
    # Let's mock away GetBundlesCommand, and we don't do
    # BroadcastTransactionsCommand either.
    # We could seed a response to our MockAdapter, but then we shall provide
    # valid values to pass GetBundlesRequestFilter. Instead we mock away the
    # whole command, so no filter is applied. It is safe because it is tested
    # elsewhere.
    with patch('iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
               MagicMock(return_value=async_return([self.trytes]))) as mocked_get_bundles:
      # We could seed a reponse to our MockAdapter, but then the returned value
      # from `GetBundlesCommand` shall be valid to pass
      # BroadcastTransactionRequestFilter.
      # Anyway, nature loves symmetry and so do we.
      with patch('iota.commands.core.BroadcastTransactionsCommand.__call__',
                 MagicMock(return_value=async_return([]))) as mocked_broadcast:

        response = await self.command(tail_hash=self.tail)

        self.assertEqual(
          response['trytes'],
          self.trytes
        )

  @async_test
  async def test_happy_path_multiple_bundle(self):
    """
    Test if command returns the correct bundle if underlying `get_bundles`
    returns multiple bundles.
    """
    # Call the command with a tail hash.
    # Let's mock away GetBundlesCommand, and we don't do
    # BroadcastTransactionsCommand either.
    # Note that GetBundlesCommand returns multiple bundles!
    with patch('iota.commands.extended.get_bundles.GetBundlesCommand.__call__',
               MagicMock(return_value=async_return([self.trytes, self.trytes_dummy]))
              ) as mocked_get_bundles:
      with patch('iota.commands.core.BroadcastTransactionsCommand.__call__',
                 MagicMock(return_value=async_return([]))) as mocked_broadcast:

        response = await self.command(tail_hash=self.tail)

        # Expect only the first bundle
        self.assertEqual(
          response['trytes'],
          self.trytes
        )