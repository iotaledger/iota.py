from unittest import TestCase
import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, Bundle, Iota, AsyncIota, TransactionHash
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.get_account_data import GetAccountDataCommand, \
  GetAccountDataRequestFilter
from iota.crypto.types import Seed
from iota.filters import Trytes
from test import mock
from test import patch, MagicMock, async_test


class GetAccountDataRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetAccountDataCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetAccountDataRequestFilterTestCase, self).setUp()

    # Define a few tryte sequences that we can re-use between tests.
    self.seed = b'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'seed':             Seed(self.seed),
      'start':            0,
      'stop':             10,
      'inclusionStates':  True,
      'security_level':   2
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
      # ``seed`` can be any value that is convertible into a
      # TryteString.
      'seed': bytes(self.seed),

      # These values must still be integers/bools, however.
      'start':            42,
      'stop':             86,
      'inclusionStates':  True,
      'security_level':   2
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':             Seed(self.seed),
        'start':            42,
        'stop':             86,
        'inclusionStates':  True,
        'security_level':   2
      },
    )

  def test_pass_optional_parameters_excluded(self):
    """
    The request contains only required parameters.
    """
    filter_ = self._filter({
      'seed': Seed(self.seed),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':             Seed(self.seed),
        'start':            0,
        'stop':             None,
        'inclusionStates':  False,
        'security_level':   2
      }
    )

  def test_fail_empty_request(self):
    """
    The request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'seed': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'seed': Seed(self.seed),

        # Your rules are really beginning to annoy me.
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_seed_null(self):
    """
    ``seed`` is null.
    """
    self.assertFilterErrors(
      {
        'seed': None,
      },

      {
        'seed': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_seed_wrong_type(self):
    """
    ``seed`` cannot be converted into a TryteString.
    """
    self.assertFilterErrors(
      {
        # Even if we did convert this into a seed, it wouldn't be very
        # secure, now would it?
        'seed': 42,
      },

      {
        'seed': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_seed_malformed(self):
    """
    ``seed`` has the correct type, but it contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'seed': b'not valid; seeds can only contain uppercase and "9".',
      },

      {
        'seed': [Trytes.CODE_NOT_TRYTES],
      },
    )

  def test_fail_start_string(self):
    """
    ``start`` is a string.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'start': '0',

        'seed': Seed(self.seed),
      },

      {
        'start': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_start_float(self):
    """
    ``start`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are not valid.
        # It's gotta be an int.
        'start': 8.0,

        'seed': Seed(self.seed),
      },

      {
        'start': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_start_too_small(self):
    """
    ``start`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'start': -1,

        'seed': Seed(self.seed),
      },

      {
        'start': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_stop_string(self):
    """
    ``stop`` is a string.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'stop': '0',

        'seed': Seed(self.seed),
      },

      {
        'stop': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_stop_float(self):
    """
    ``stop`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are not valid.
        # It's gotta be an int.
        'stop': 8.0,

        'seed': Seed(self.seed),
      },

      {
        'stop': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_stop_too_small(self):
    """
    ``stop`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'stop': -1,

        'seed': Seed(self.seed),
      },

      {
        'stop': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_stop_occurs_before_start(self):
    """
    ``stop`` is less than ``start``.
    """
    self.assertFilterErrors(
      {
        'start':  1,
        'stop':   0,

        'seed': Seed(self.seed),
      },

      {
        'start': [GetAccountDataRequestFilter.CODE_INTERVAL_INVALID],
      },
    )

  def test_fail_interval_too_large(self):
    """
    ``stop`` is way more than ``start``.
    """
    self.assertFilterErrors(
      {
        'start':  0,
        'stop':   GetAccountDataRequestFilter.MAX_INTERVAL + 1,

        'seed': Seed(self.seed),
      },

      {
        'stop':  [GetAccountDataRequestFilter.CODE_INTERVAL_TOO_BIG],
      },
    )

  def test_fail_inclusion_states_wrong_type(self):
    """
    ``inclusionStates`` is not a boolean.
    """
    self.assertFilterErrors(
      {
        'inclusionStates': '1',

        'seed': Seed(self.seed),
      },

      {
        'inclusionStates': [f.Type.CODE_WRONG_TYPE],
      },
    )

class AsyncIter:
  """
  Class for mocking async generators.

  Used here to mock the return values of `iter_used_addresses`.
  """
  def __init__(self, items):
    self.items = items

  async def __aiter__(self):
    for item in self.items:
      yield item

class GetAccountDataCommandTestCase(TestCase):
  def setUp(self):
    super(GetAccountDataCommandTestCase, self).setUp()

    self.adapter  = MockAdapter()
    self.command  = GetAccountDataCommand(self.adapter)

    # Define some tryte sequences we can re-use between tests.
    self.addy1 =\
      Address(
        b'TESTVALUEONE9DONTUSEINPRODUCTION99999YDZ'
        b'E9TAFAJGJA9CECKDAEPHBICDR9LHFCOFRBQDHC9IG',

        key_index = 0,
      )

    self.addy2 =\
      Address(
        b'TESTVALUETWO9DONTUSEINPRODUCTION99999TES'
        b'GINEIDLEEHRAOGEBMDLENFDAFCHEIHZ9EBZDD9YHL',

        key_index = 1,
      )

    self.hash1 =\
      TransactionHash(
        b'TESTVALUE9DONTUSEINPRODUCTION99999O99IDB'
        b'MBPAPDXBSDWAMHV9DASEGCOGHBV9VAF9UGRHFDPFJ'
      )

    self.hash2 =\
      TransactionHash(
        b'TESTVALUE9DONTUSEINPRODUCTION99999OCNCHC'
        b'TEPBHEPBJEWFXERHSCQCH9TAAANDBBCCHCIDEAVBV'
      )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.get_account_data.GetAccountDataCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.get_account_data()

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
    with patch('iota.commands.extended.get_account_data.GetAccountDataCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.get_account_data()

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_happy_path(self):
    """
    Loading account data for an account.
    """
    async def mock_iter_used_addresses(adapter, seed, start, security_level):
      """
      Mocks the ``iter_used_addresses`` function, so that we can
      simulate its functionality without actually connecting to the
      Tangle.

      References:
        - :py:func:`iota.commands.extended.utils.iter_used_addresses`
      """
      yield self.addy1, [self.hash1]
      yield self.addy2, [self.hash2]

    mock_get_balances = mock.Mock(return_value=async_return({'balances': [42, 0]}))

    # Not particularly realistic, but good enough to prove that the
    # mocked function was invoked correctly.
    bundles = [Bundle(), Bundle()]
    mock_get_bundles_from_transaction_hashes = mock.Mock(return_value=async_return(bundles))

    with mock.patch(
        'iota.commands.extended.get_account_data.iter_used_addresses',
        mock_iter_used_addresses,
    ):
      with mock.patch(
        'iota.commands.extended.get_account_data.get_bundles_from_transaction_hashes',
        mock_get_bundles_from_transaction_hashes,
      ):
        with mock.patch(
          'iota.commands.core.get_balances.GetBalancesCommand._execute',
          mock_get_balances,
        ):
          response = await self.command(seed=Seed.random())

    self.assertDictEqual(
      response,

      {
        'addresses':  [self.addy1, self.addy2],
        'balance':    42,
        'bundles':    bundles,
      },
    )

  @async_test
  async def test_no_transactions(self):
    """
    Loading account data for a seed that hasn't been used yet.
    """
    with mock.patch(
        'iota.commands.extended.get_account_data.iter_used_addresses',
        mock.Mock(return_value=AsyncIter([])),
    ):
      response = await self.command(seed=Seed.random())

    self.assertDictEqual(
      response,

      {
        'addresses':  [],
        'balance':    0,
        'bundles':    [],
      },
    )

  @async_test
  async def test_balance_is_found_for_address_without_transaction(self):
    """
    If an address has a balance, no transactions and was spent from, the
    balance should still be found and returned.
    """
    with mock.patch(
        'iota.commands.extended.get_account_data.iter_used_addresses',
        mock.Mock(return_value=AsyncIter([(self.addy1, [])])),
    ):
      self.adapter.seed_response('getBalances', {
        'balances': [42],
      })

      response = await self.command(seed=Seed.random())

    self.assertDictEqual(
      response,

      {
        'addresses':  [self.addy1],
        'balance':    42,
        'bundles':    [],
      },
    )
