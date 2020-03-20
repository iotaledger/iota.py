from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, BadApiResponse, Iota, AsyncIota, TransactionHash
from iota.adapter import MockAdapter, async_return
from iota.commands.extended.get_inputs import GetInputsCommand, GetInputsRequestFilter
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed
from iota.filters import Trytes
from test import mock
from test import patch, MagicMock, async_test


class GetInputsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetInputsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetInputsRequestFilterTestCase, self).setUp()

    # Define a few tryte sequences that we can re-use between tests.
    self.seed = 'HELLOIOTA'

  def test_pass_happy_path(self):
    """
    Request is valid.
    """
    request = {
      # Raw trytes are extracted to match the IRI's JSON protocol.
      'seed': self.seed,

      'start':      0,
      'stop':       10,
      'threshold':  100,
      "securityLevel": 3,
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
      # ``seed`` can be any value that is convertible into an ASCII
      # representation of a TryteString.
      'seed': bytearray(self.seed.encode('ascii')),

      # These values must still be integers, however.
      'start':      42,
      'stop':       86,
      'threshold':  99,
      "securityLevel": 3,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'seed':       Seed(self.seed),
        'start':      42,
        'stop':       86,
        'threshold':  99,
        "securityLevel": 3,
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
        'seed':       Seed(self.seed),
        'start':      0,
        'stop':       None,
        'threshold':  None,
        "securityLevel": AddressGenerator.DEFAULT_SECURITY_LEVEL,
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

        # Told you I did. Reckless is he. Now, matters are worse.
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
        'start': [GetInputsRequestFilter.CODE_INTERVAL_INVALID],
      },
    )

  def test_fail_interval_too_large(self):
    """
    ``stop`` is way more than ``start``.
    """
    self.assertFilterErrors(
      {
        'start':  0,
        'stop':   GetInputsRequestFilter.MAX_INTERVAL + 1,

        'seed': Seed(self.seed),
      },

      {
        'stop':  [GetInputsRequestFilter.CODE_INTERVAL_TOO_BIG],
      },
    )

  def test_fail_threshold_string(self):
    """
    ``threshold`` is a string.
    """
    self.assertFilterErrors(
      {
        # Not valid; it must be an int.
        'threshold': '0',

        'seed': Seed(self.seed),
      },

      {
        'threshold': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_threshold_float(self):
    """
    ``threshold`` is a float.
    """
    self.assertFilterErrors(
      {
        # Even with an empty fpart, floats are not valid.
        # It's gotta be an int.
        'threshold': 8.0,

        'seed': Seed(self.seed),
      },

      {
        'threshold': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_threshold_too_small(self):
    """
    ``threshold`` is less than 0.
    """
    self.assertFilterErrors(
      {
        'threshold': -1,

        'seed': Seed(self.seed),
      },

      {
        'threshold': [f.Min.CODE_TOO_SMALL],
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


class GetInputsCommandTestCase(TestCase):
  def setUp(self):
    super(GetInputsCommandTestCase, self).setUp()

    self.adapter = MockAdapter()
    self.command = GetInputsCommand(self.adapter)

    # Define some valid tryte sequences that we can reuse between
    # tests.
    self.addy0 =\
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999FIODSG'
          b'IC9CCIFCNBTBDFIEHHE9RBAEVGK9JECCLCPBIINAX',

        key_index = 0,
      )

    self.addy1 =\
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION999999EPCNH'
          b'MBTEH9KDVFMHHESDOBTFFACCGBFGACEDCDDCGICIL',

        key_index = 1,
      )

    self.addy2 =\
      Address(
        trytes =
          b'TESTVALUE9DONTUSEINPRODUCTION99999YDOHWF'
          b'U9PFOFHGKFACCCBGDALGI9ZBEBABFAMBPDSEQ9XHJ',

        key_index = 2,
      )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.extended.get_inputs.GetInputsCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.get_inputs()

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
    with patch('iota.commands.extended.get_inputs.GetInputsCommand.__call__',
              MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      # Don't need to call with proper args here.
      response = await api.get_inputs()

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  @async_test
  async def test_stop_threshold_met(self):
    """
    ``stop`` provided, balance meets ``threshold``.
    """
    self.adapter.seed_response('getBalances', {
      'balances': [42, 29],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    mock_address_generator = mock.Mock(return_value=[self.addy0, self.addy1])

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.get_addresses',
        mock_address_generator,
    ):
      response = await self.command(
        seed      = Seed.random(),
        stop      = 2,
        threshold = 71,
      )

    self.assertEqual(response['totalBalance'], 71)
    self.assertEqual(len(response['inputs']), 2)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)

    self.assertEqual(input0, self.addy0)
    self.assertEqual(input0.balance, 42)
    self.assertEqual(input0.key_index, 0)

    input1 = response['inputs'][1]
    self.assertIsInstance(input1, Address)

    self.assertEqual(input1, self.addy1)
    self.assertEqual(input1.balance, 29)
    self.assertEqual(input1.key_index, 1)

  @async_test
  async def test_stop_threshold_not_met(self):
    """
    ``stop`` provided, balance does not meet ``threshold``.
    """
    self.adapter.seed_response('getBalances', {
      'balances': [42, 29],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    mock_address_generator = mock.Mock(return_value=[self.addy0, self.addy1])

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.get_addresses',
        mock_address_generator,
    ):
      with self.assertRaises(BadApiResponse):
        await self.command(
          seed      = Seed.random(),
          stop      = 2,
          threshold = 72,
        )

  @async_test
  async def test_stop_threshold_zero(self):
    """
    ``stop`` provided, ``threshold`` is 0.
    """
    # Note that the first address has a zero balance.
    self.adapter.seed_response('getBalances', {
      'balances': [0, 1],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    mock_address_generator = mock.Mock(return_value=[self.addy0, self.addy1])

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.get_addresses',
        mock_address_generator,
    ):
      response = await self.command(
        seed      = Seed.random(),
        stop      = 2,
        threshold = 0,
      )

    self.assertEqual(response['totalBalance'], 1)
    self.assertEqual(len(response['inputs']), 1)

    # Address 0 was skipped because it has a zero balance.
    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)

    self.assertEqual(input0, self.addy1)
    self.assertEqual(input0.balance, 1)
    self.assertEqual(input0.key_index, 1)

  @async_test
  async def test_stop_no_threshold(self):
    """
    ``stop`` provided, no ``threshold``.
    """
    self.adapter.seed_response('getBalances', {
      'balances': [42, 29],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    mock_address_generator = mock.Mock(return_value=[self.addy0, self.addy1])

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.get_addresses',
        mock_address_generator,
    ):
      response = await self.command(
        seed      = Seed.random(),
        start     = 0,
        stop      = 2,
      )

    self.assertEqual(response['totalBalance'], 71)
    self.assertEqual(len(response['inputs']), 2)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)

    self.assertEqual(input0, self.addy0)
    self.assertEqual(input0.balance, 42)
    self.assertEqual(input0.key_index, 0)

    input1 = response['inputs'][1]
    self.assertIsInstance(input1, Address)

    self.assertEqual(input1, self.addy1)
    self.assertEqual(input1.balance, 29)
    self.assertEqual(input1.key_index, 1)

  @async_test
  async def test_no_stop_threshold_met(self):
    """
    No ``stop`` provided, balance meets ``threshold``.
    """

    # ``getInputs`` uses ``findTransactions`` and
    # ``wereAddressesSpentFrom`` to identify unused addresses.
    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999WBL9KD'
          b'EIZDMEDFPEYDIIA9LEMEUCC9MFPBY9TEVCUGSEGGN'
        ),
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999YFXGOD'
          b'GISBJAX9PDJIRDMDV9DCRDCAEG9FN9KECCBDDFZ9H'
        ),
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'hashes': [],
    })

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })

    self.adapter.seed_response('getBalances', {
      'balances': [42, 29],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    def mock_address_generator(ag, start, step=1):
      for addy in [self.addy0, self.addy1, self.addy2][start::step]:
        yield addy

    # When ``stop`` is None, the command uses a generator internally.
    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        mock_address_generator,
    ):
      response = await self.command(
        seed      = Seed.random(),
        threshold = 71,
      )

    self.assertEqual(response['totalBalance'], 71)
    self.assertEqual(len(response['inputs']), 2)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)

    self.assertEqual(input0, self.addy0)
    self.assertEqual(input0.balance, 42)
    self.assertEqual(input0.key_index, 0)

    input1 = response['inputs'][1]
    self.assertIsInstance(input1, Address)

    self.assertEqual(input1, self.addy1)
    self.assertEqual(input1.balance, 29)
    self.assertEqual(input1.key_index, 1)

  @async_test
  async def test_no_stop_threshold_not_met(self):
    """
    No ``stop`` provided, balance does not meet ``threshold``.
    """
    self.adapter.seed_response('getBalances', {
      'balances': [42, 29, 0],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    def mock_address_generator(ag, start, step=1):
      for addy in [self.addy0, self.addy1, self.addy2][start::step]:
        yield addy

    # When ``stop`` is None, the command uses a generator internally.
    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        mock_address_generator,
    ):
      with self.assertRaises(BadApiResponse):
        await self.command(
          seed      = Seed.random(),
          threshold = 72,
        )

  @async_test
  async def test_no_stop_threshold_zero(self):
    """
    No ``stop`` provided, ``threshold`` is 0.
    """

    # ``getInputs`` uses ``findTransactions`` and
    # ``wereAddressesSpentFrom`` to identify unused addresses.
    # addresses.
    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999WBL9KD'
          b'EIZDMEDFPEYDIIA9LEMEUCC9MFPBY9TEVCUGSEGGN'
        ),
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999YFXGOD'
          b'GISBJAX9PDJIRDMDV9DCRDCAEG9FN9KECCBDDFZ9H'
        ),
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'hashes': [],
    })

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })

    # Note that the first address has a zero balance.
    self.adapter.seed_response('getBalances', {
      'balances': [0, 1],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    def mock_address_generator(ag, start, step=1):
      for addy in [self.addy0, self.addy1, self.addy2][start::step]:
        yield addy

    # When ``stop`` is None, the command uses a generator internally.
    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        mock_address_generator,
    ):
      response = await self.command(
        seed      = Seed.random(),
        threshold = 0,
      )

    self.assertEqual(response['totalBalance'], 1)
    self.assertEqual(len(response['inputs']), 1)

    # Because the first address had a zero balance, it was skipped.
    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)

    self.assertEqual(input0, self.addy1)
    self.assertEqual(input0.balance, 1)
    self.assertEqual(input0.key_index, 1)

  @async_test
  async def test_no_stop_no_threshold(self):
    """
    No ``stop`` provided, no ``threshold``.
    """

    # ``getInputs`` uses ``findTransactions`` and
    # ``wereAddressesSpentFrom`` to identify unused addresses.
    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999WBL9KD'
          b'EIZDMEDFPEYDIIA9LEMEUCC9MFPBY9TEVCUGSEGGN'
        ),
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999YFXGOD'
          b'GISBJAX9PDJIRDMDV9DCRDCAEG9FN9KECCBDDFZ9H'
        ),
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'hashes': [],
    })

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })

    self.adapter.seed_response('getBalances', {
      'balances': [42, 29],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    def mock_address_generator(ag, start, step=1):
      for addy in [self.addy0, self.addy1, self.addy2][start::step]:
        yield addy

    # When ``stop`` is None, the command uses a generator internally.
    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        mock_address_generator,
    ):
      response = await self.command(
        seed = Seed.random(),
      )

    self.assertEqual(response['totalBalance'], 71)
    self.assertEqual(len(response['inputs']), 2)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)

    self.assertEqual(input0, self.addy0)
    self.assertEqual(input0.balance, 42)
    self.assertEqual(input0.key_index, 0)

    input1 = response['inputs'][1]
    self.assertIsInstance(input1, Address)

    self.assertEqual(input1, self.addy1)
    self.assertEqual(input1.balance, 29)
    self.assertEqual(input1.key_index, 1)

  @async_test
  async def test_start(self):
    """
    Using ``start`` to offset the key range.
    """

    # ``getInputs`` uses ``findTransactions`` and
    # ``wereAddressesSpentFrom`` to identify unused addresses.
    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999YFXGOD'
          b'GISBJAX9PDJIRDMDV9DCRDCAEG9FN9KECCBDDFZ9H'
        ),
      ],
    })

    self.adapter.seed_response('findTransactions', {
      'hashes': [],
    })

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })

    self.adapter.seed_response('getBalances', {
      'balances': [86],
    })

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.
    def mock_address_generator(ag, start, step=1):
      # If ``start`` has the wrong value, return garbage to make the
      # test asplode.
      for addy in [None, self.addy1, self.addy2][start::step]:
        yield addy

    # When ``stop`` is None, the command uses a generator internally.
    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        mock_address_generator,
    ):
      response = await self.command(
        seed  = Seed.random(),
        start = 1,
      )

    self.assertEqual(response['totalBalance'], 86)
    self.assertEqual(len(response['inputs']), 1)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)

    self.assertEqual(input0, self.addy1)
    self.assertEqual(input0.balance, 86)
    self.assertEqual(input0.key_index, 1)

  @async_test
  async def test_start_stop(self):
    """
    Using ``start`` and ``stop`` at once.
    Checking if correct number of addresses is returned. Must be stop - start
    """

    # To keep the unit test nice and speedy, we will mock the address
    # generator.  We already have plenty of unit tests for that
    # functionality, so we can get away with mocking it here.

    def mock_address_generator(ag, start, step=1):
      # returning up to 3 addresses, depending on stop value
      for addy in [self.addy0, self.addy1, self.addy2][start::step]:
        yield addy

    self.adapter.seed_response('getBalances', {
      'balances': [11, 11],
    })

    with mock.patch(
        'iota.crypto.addresses.AddressGenerator.create_iterator',
        mock_address_generator,
    ):
      response = await self.command(
        seed  = Seed.random(),
        start = 1,
        stop = 3,
      )

    self.assertEqual(len(response['inputs']), 2)  # 3 - 1 = 2 addresses expected
    self.assertEqual(response['totalBalance'], 22)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)
    self.assertEqual(input0, self.addy1)
    self.assertEqual(input0.balance, 11)
    self.assertEqual(input0.key_index, 1)

    input1 = response['inputs'][1]
    self.assertIsInstance(input1, Address)
    self.assertEqual(input1, self.addy2)
    self.assertEqual(input1.balance, 11)
    self.assertEqual(input1.key_index, 2)


  @async_test
  async def test_security_level_1_no_stop(self):
    """
    Testing GetInputsCoommand:
      - with security_level = 1 (non default)
      - without `stop` parameter
    """

    # one address with index 0 for selected security levels for the random seed.
    # to check with respective outputs from command
    seed = Seed.random()
    address = AddressGenerator(seed, security_level=1).get_addresses(0)[0]

    # ``getInputs`` uses ``findTransactions`` and
    # ``wereAddressesSpentFrom`` to identify unused addresses.
    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999YFXGOD'
          b'GISBJAX9PDJIRDMDV9DCRDCAEG9FN9KECCBDDFZ9H'
        ),
      ],
    })
    self.adapter.seed_response('findTransactions', {
      'hashes': [],
    })

    self.adapter.seed_response('wereAddressesSpentFrom', {
      'states': [False],
    })

    self.adapter.seed_response('getBalances', {
      'balances': [86],
    })

    response = await GetInputsCommand(self.adapter)(
      seed=seed,
      securityLevel=1,
    )

    self.assertEqual(response['totalBalance'], 86)
    self.assertEqual(len(response['inputs']), 1)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)
    self.assertEqual(input0, address)
    self.assertEqual(input0.balance, 86)
    self.assertEqual(input0.key_index, 0)

  @async_test
  async def test_security_level_1_with_stop(self):
    """
    Testing GetInputsCoommand:
      - with security_level = 1 (non default)
      - with `stop` parameter
    """

    # one address with index 0 for selected security levels for the random seed.
    # to check with respective outputs from command
    seed = Seed.random()
    address = AddressGenerator(seed, security_level=1).get_addresses(0)[0]

    self.adapter.seed_response('getBalances', {
      'balances': [86],
    })
    # ``getInputs`` uses ``findTransactions`` to identify unused
    # addresses.
    self.adapter.seed_response('findTransactions', {
      'hashes': [
        TransactionHash(
          b'TESTVALUE9DONTUSEINPRODUCTION99999YFXGOD'
          b'GISBJAX9PDJIRDMDV9DCRDCAEG9FN9KECCBDDFZ9H'
        ),
      ],
    })
    self.adapter.seed_response('findTransactions', {
      'hashes': [],
    })

    response = await GetInputsCommand(self.adapter)(
      seed=seed,
      securityLevel=1,
      stop=1,    # <<<<< here
    )

    self.assertEqual(response['totalBalance'], 86)
    self.assertEqual(len(response['inputs']), 1)

    input0 = response['inputs'][0]
    self.assertIsInstance(input0, Address)
    self.assertEqual(input0, address)
    self.assertEqual(input0.balance, 86)
    self.assertEqual(input0.key_index, 0)

