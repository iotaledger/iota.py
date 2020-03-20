from unittest import TestCase

from iota import Iota, AsyncIota, TransactionTrytes
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.broadcast_and_store import BroadcastAndStoreCommand
from test import patch, MagicMock, async_test

class BroadcastAndStoreCommandTestCase(TestCase):
  def setUp(self):
    super(BroadcastAndStoreCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = BroadcastAndStoreCommand(self.adapter)

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.broadcast_and_store.BroadcastAndStoreCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.broadcast_and_store('trytes')

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
    with patch('iota.commands.extended.broadcast_and_store.BroadcastAndStoreCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.broadcast_and_store('trytes')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_happy_path(self):
    """
    Successful invocation of ``broadcastAndStore``.
    """
    self.adapter.seed_response('broadcastTransactions', {
      'trytes': [
        str(self.trytes1, 'ascii'),
        str(self.trytes2, 'ascii'),
      ],
    })

    self.adapter.seed_response('storeTransactions', {})

    trytes = [
      TransactionTrytes(self.trytes1),
      TransactionTrytes(self.trytes2),
    ]

    response = await self.command(trytes=trytes)

    self.assertDictEqual(response, {'trytes': trytes})
