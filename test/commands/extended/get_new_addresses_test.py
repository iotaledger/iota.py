from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, Iota, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.get_new_addresses import GetNewAddressesCommand
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class GetNewAddressesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetNewAddressesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetNewAddressesRequestFilterTestCase, self).setUp()

    # Define a few tryte sequences that we can re-use between tests.
    self.seed = 'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      'seed':           Seed(self.seed),
      'index':          1,
      'count':          1,
      'securityLevel':  2,
      'checksum':       False,
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_optional_parameters_excluded(self):
    """
    Request omits optional parameters.
    """
    filter_ = self._filter({
      'seed': Seed(self.seed),
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':           Seed(self.seed),
        'index':          0,
        'count':          None,
        'securityLevel':  AddressGenerator.DEFAULT_SECURITY_LEVEL,
        'checksum':       False,
      },
    )

  def test_pass_compatible_types(self):
    """
    Request contains values that can be converted to the expected
    types.
    """
    filter_ = self._filter({
      # ``seed`` can be any TrytesCompatible value.
      'seed': bytearray(self.seed.encode('ascii')),

      # These values must be integers, however.
      'index':          100,
      'count':          8,
      'securityLevel':  2,

      # ``checksum`` must be boolean.
      'checksum':       False,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':           Seed(self.seed),
        'index':          100,
        'count':          8,
        'securityLevel':  2,
        'checksum':       False,
      },
    )

  def test_fail_empty(self):
    """
    Request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'seed': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    Request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'seed':           Seed(self.seed),
        'index':          None,
        'count':          1,
        'securityLevel':  2,
        'checksum':       False,

        # Some men just want to watch the world burn.
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
        'seed': 42,
      },

      {
        'seed': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_seed_malformed(self):
    """
    ``seed`` has an allowed type, but it contains invalid characters.
    """
    self.assertFilterErrors(
      {
        'seed': b'not valid; seeds can only contain uppercase and "9".',
      },

      {
        'seed': [Trytes.CODE_NOT_TRYTES],
      },
    )

  def test_fail_count_string(self):
    """
    ``count`` is a string value.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'count': '42',

        'seed': Seed(self.seed),
      },

      {
        'count': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_count_float(self):
    """
    ``count`` is a float value.
    """
    self.assertFilterErrors(
      {
        # Not valid, even with an empty fpart; it must be an int.
        'count': 42.0,

        'seed': Seed(self.seed),
      },

      {
        'count': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_count_too_small(self):
    """
    ``count`` is less than 1.
    """
    self.assertFilterErrors(
      {
        'count':  0,
        'seed':   Seed(self.seed),
      },

      {
        'count': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_index_string(self):
    """
    ``index`` is a string value.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'index': '42',

        'seed': Seed(self.seed),
      },

      {
        'index': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_index_float(self):
    """
    ``index`` is a float value.
    """
    self.assertFilterErrors(
      {
        # Not valid, even with an empty fpart; it must be an int.
        'index': 42.0,

        'seed': Seed(self.seed),
      },

      {
        'index': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_index_too_small(self):
    """
    ``index`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'index':  -1,
        'seed':   Seed(self.seed),
      },

      {
        'index': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_security_level_too_small(self):
    """
    ``securityLevel`` is < 1.
    """
    self.assertFilterErrors(
      {
        'securityLevel':  0,
        'seed':           Seed(self.seed),
      },

      {
        'securityLevel': [f.Min.CODE_TOO_SMALL],
      },
    )

  def test_fail_security_level_too_big(self):
    """
    ``securityLevel`` is > 3.
    """
    self.assertFilterErrors(
      {
        'securityLevel':  4,
        'seed':           Seed(self.seed),
      },

      {
        'securityLevel': [f.Max.CODE_TOO_BIG],
      },
    )

  def test_fail_security_level_wrong_type(self):
    """
    ``securityLevel`` is not an int.
    """
    self.assertFilterErrors(
      {
        'securityLevel':  '2',
        'seed':           Seed(self.seed),
      },

      {
        'securityLevel': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_checksum_wrong_type(self):
    """
    ``checksum`` is not a boolean.
    """
    self.assertFilterErrors(
      {
        'checksum':       '2',
        'seed':           Seed(self.seed),
      },

      {
        'checksum': [f.Type.CODE_WRONG_TYPE],
      },
    )


class GetNewAddressesCommandTestCase(TestCase):
  def setUp(self):
    super(GetNewAddressesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetNewAddressesCommand(self.adapter)

    self.seed =\
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999ZDCCUF'
        b'CBBIQCLGMEXAVFQEOF9DRAB9VCEBAGXAF9VF9FLHP',
      )

    self.addy_1 =\
      Address(
        b'NYMWLBUJEISSACZZBRENC9HEHYQXHCGQHSNHVCEA'
        b'ZDCTEVNGSDUEKTSYBSQGMVJRIEDHWDYSEYCFAZAH9',
      )

    self.addy_2 =\
      Address(
        b'NTPSEVZHQITARYWHIRTSIFSERINLRYVXLGIQKKHY'
        b'IWYTLQUUHDWSOVXLIKVJTYZBFKLABWRBFYVSMD9NB',
      )

    self.addy_1_checksum =\
      Address(
        b'NYMWLBUJEISSACZZBRENC9HEHYQXHCGQHSNHVCEA'
        b'ZDCTEVNGSDUEKTSYBSQGMVJRIEDHWDYSEYCFAZAH'
        b'9T9FPJROTW',
      )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.get_new_addresses.GetNewAddressesCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.get_new_addresses('hashes')

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
    with patch('iota.commands.extended.get_new_addresses.GetNewAddressesCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.get_new_addresses('hashes')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_get_addresses_offline(self):
    """
    Generate addresses in offline mode (without filtering used
    addresses).
    """
    response =\
      await self.command(
        count = 2,
        index = 0,
        seed  = self.seed,
      )

    self.assertDictEqual(
      response,
      {'addresses': [self.addy_1, self.addy_2]},
    )

    # No API requests were made.
    self.assertListEqual(self.adapter.requests, [])

  @async_test
  async def test_security_level(self):
    """
    Generating addresses with a different security level.
    """
    response =\
      await self.command(
        count         = 2,
        index         = 0,
        securityLevel = 1,
        seed          = self.seed,
      )

    self.assertDictEqual(
      response,

      {
        'addresses':
          [
            Address(
              b'ERBTZTPT9SKDQEGETKMZLYNRQMZYZIDENGWCSGRF'
              b'9TLURIEFVKUBSWOIMLMWTWMWTTHSUREPISXDPLCQC',
            ),

            Address(
              b'QVHEMGYHVMCFAISJKTWPFSKDAFRZHXQZK9E9KOUQ'
              b'LOLVBN9BFAZDDY9O9EYYMHMDWZAKXI9OPBPEYM9FC',
            ),
          ],
      },
    )

  @async_test
  async def test_get_addresses_online_already_spent_from(self):
    """
    Generate address in online mode (filtering used addresses). Test if an
    address that was already spent from will not be returned.
    """
    # Pretend that ``self.addy1`` has no transactions but already been
    # spent from, but ``self.addy2`` is not used.

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [True],
    })

    self.adapter.seed_response('findTransactions', {
      'duration': 1,
      'hashes':   [],
    })

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })

    self.adapter.seed_response('findTransactions', {
      'duration': 1,
      'hashes':   [],
    })

    response =\
      await self.command(
        # If ``count`` is missing or ``None``, the command will operate
        # in online mode.
        # count = None,

        index = 0,
        seed  = self.seed,
      )

    # The command determined that ``self.addy1`` was already used, so
    # it skipped that one.
    self.assertDictEqual(response, {'addresses': [self.addy_2]})

    # Due to running WereAddressesSpentFromCommand and FindTransactionsCommand
    # with asyncio.gather, we can't infer their execution order. Therefore,
    # we need to assert if the contents of the two lists match by value,
    # regardless of their order:
    # https://docs.python.org/3.5/library/unittest.html#unittest.TestCase.assertCountEqual
    self.assertCountEqual(
      self.adapter.requests,
      [
        {
          'command': 'wereAddressesSpentFrom',
          'addresses':  [self.addy_1],
        },
        {
          'command': 'findTransactions',
          'addresses':  [self.addy_1],
        },
        {
          'command': 'wereAddressesSpentFrom',
          'addresses':  [self.addy_2],
        },
        {
          'command':    'findTransactions',
          'addresses':  [self.addy_2],
        },
      ],
    )

  @async_test
  async def test_get_addresses_online_has_transaction(self):
    """
    Generate address in online mode (filtering used addresses). Test if an
    address that has a transaction will not be returned.
    """
    # Pretend that ``self.addy1`` has a transaction, but
    # ``self.addy2`` is not used.
    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })
    self.adapter.seed_response('findTransactions', {
      'duration': 18,
      'hashes': [
        'TESTVALUE9DONTUSEINPRODUCTION99999ITQLQN'
        'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999',
      ],
    })

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })
    self.adapter.seed_response('findTransactions', {
      'hashes':   [],
    })

    response = await self.command(index=0, seed=self.seed)

    # The command determined that ``self.addy1`` was already used, so
    # it skipped that one.
    self.assertDictEqual(response, {'addresses': [self.addy_2]})

    self.assertCountEqual(
      self.adapter.requests,
      [
        {
          'command': 'wereAddressesSpentFrom',
          'addresses':  [self.addy_1],
        },
        {
          'command': 'findTransactions',
          'addresses': [self.addy_1],
        },
        {
          'command': 'wereAddressesSpentFrom',
          'addresses':  [self.addy_2],
        },
        {
          'command':    'findTransactions',
          'addresses':  [self.addy_2],
        },
      ],
    )

  @async_test
  async def test_new_address_checksum(self):
    """
    Generate address with a checksum.
    """
    response =\
      await self.command(
        checksum      = True,
        count         = 1,
        index         = 0,
        seed          = self.seed,
      )

    self.assertDictEqual(
      response,
      {'addresses': [self.addy_1_checksum]},
    )
