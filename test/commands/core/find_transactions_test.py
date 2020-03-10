from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, Iota, Tag, BundleHash, TransactionHash, TryteString, \
  AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.find_transactions import FindTransactionsCommand, \
  FindTransactionsRequestFilter
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class FindTransactionsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = FindTransactionsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(FindTransactionsRequestFilterTestCase, self).setUp()

    # Define a few valid values that we can reuse across tests.
    self.trytes1 = 'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'
    self.trytes3 = '999999999999999999999999999'

  def test_pass_all_parameters(self):
    """
    The request contains valid values for all parameters.
    """
    # Raw trytes are extracted to match the IRI's JSON protocol.
    request = {
      'bundles': [
        str(BundleHash(self.trytes1)),
        str(BundleHash(self.trytes2)),
      ],

      'addresses': [
        str(Address(self.trytes1)),
        str(Address(self.trytes2)),
      ],

      'tags': [
        str(Tag(self.trytes1)),
        str(Tag(self.trytes3)),
      ],

      'approvees': [
        str(TransactionHash(self.trytes1)),
        str(TransactionHash(self.trytes3)),
      ],
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
      'bundles': [
        self.trytes1.encode('ascii'),
        BundleHash(self.trytes2),
      ],

      'addresses': [
        self.trytes1.encode('ascii'),
        Address(self.trytes2),
      ],

      'tags': [
        self.trytes1.encode('ascii'),
        Tag(self.trytes3),
      ],

      'approvees': [
        self.trytes1.encode('ascii'),
        TransactionHash(self.trytes3),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        # Raw trytes are extracted to match the IRI's JSON protocol.
        'bundles': [
          str(BundleHash(self.trytes1)),
          str(BundleHash(self.trytes2)),
        ],

        'addresses': [
          str(Address(self.trytes1)),
          str(Address(self.trytes2)),
        ],

        'tags': [
          str(Tag(self.trytes1)),
          str(Tag(self.trytes3)),
        ],

        'approvees': [
          str(TransactionHash(self.trytes1)),
          str(TransactionHash(self.trytes3)),
        ],
      },
    )

  def test_pass_bundles_only(self):
    """
    The request only includes bundles.
    """
    request = {
      'bundles': [
        BundleHash(self.trytes1),
        BundleHash(self.trytes2),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'bundles': [
          str(BundleHash(self.trytes1)),
          str(BundleHash(self.trytes2)),
        ],

        # Null criteria are not included in the request.
        # https://github.com/iotaledger/iota.py/issues/96
        # 'addresses':  [],
        # 'approvees':  [],
        # 'tags':       [],
      },
    )

  def test_pass_addresses_only(self):
    """
    The request only includes addresses.
    """
    request = {
      'addresses': [
        Address(self.trytes1),
        Address(self.trytes2),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'addresses': [
          str(Address(self.trytes1)),
          str(Address(self.trytes2)),
        ],

        # Null criteria are not included in the request.
        # https://github.com/iotaledger/iota.py/issues/96
        # 'approvees':  [],
        # 'bundles':    [],
        # 'tags':       [],
      },
    )

  def test_pass_tags_only(self):
    """
    The request only includes tags.
    """
    request = {
      'tags': [
        Tag(self.trytes1),
        Tag(self.trytes3),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'tags': [
          str(Tag(self.trytes1)),
          str(Tag(self.trytes3)),
        ],

        # Null criteria are not included in the request.
        # https://github.com/iotaledger/iota.py/issues/96
        # 'addresses':  [],
        # 'approvees':  [],
        # 'bundles':    [],
      },
    )

  def test_pass_approvees_only(self):
    """
    The request only includes approvees.
    """
    request = {
      'approvees': [
        TransactionHash(self.trytes1),
        TransactionHash(self.trytes3),
      ],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'approvees': [
          str(TransactionHash(self.trytes1)),
          str(TransactionHash(self.trytes3)),
        ],

        # Null criteria are not included in the request.
        # https://github.com/iotaledger/iota.py/issues/96
        # 'addresses':  [],
        # 'bundles':    [],
        # 'tags':       [],
      },
    )

  def test_fail_empty(self):
    """
    The request does not contain any parameters.
    """
    self.assertFilterErrors(
      {},

      {
        '': [FindTransactionsRequestFilter.CODE_NO_SEARCH_VALUES],
      },
    )

  def test_fail_all_parameters_null(self):
    """
    The request contains all parameters, but every one is null.
    """
    self.assertFilterErrors(
      {
        'addresses':  None,
        'approvees':  None,
        'bundles':    None,
        'tags':       None,
      },

      {
        '': [FindTransactionsRequestFilter.CODE_NO_SEARCH_VALUES],
      },
    )

  def test_success_all_parameters_empty(self):
    """
    All of the parameters are empty lists.

    This is technically valid, though probably not very useful.
    """
    self.assertFilterPasses(
      {
        'addresses':  [],
        'approvees':  [],
        'bundles':    [],
        'tags':       [],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'addresses':  [Address(self.trytes1)],
        'approvees':  [TransactionHash(self.trytes1)],
        'bundles':    [BundleHash(self.trytes1)],
        'tags':       [Tag(self.trytes1)],

        # Hey, you're not allowed in he-argh!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_bundles_wrong_type(self):
    """
    ``bundles`` is not an array.
    """
    self.assertFilterErrors(
      {
        'bundles': BundleHash(self.trytes1),
      },

      {
        'bundles': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_bundles_contents_invalid(self):
    """
    ``bundles`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'bundles': [
          b'',
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes2),

          2130706433,
          b'9' * 82,
        ],
      },

      {
        'bundles.0':  [f.Required.CODE_EMPTY],
        'bundles.1':  [f.Type.CODE_WRONG_TYPE],
        'bundles.2':  [f.Required.CODE_EMPTY],
        'bundles.3':  [Trytes.CODE_NOT_TRYTES],
        'bundles.5':  [f.Type.CODE_WRONG_TYPE],
        'bundles.6':  [Trytes.CODE_WRONG_FORMAT],
      },
    )

  def test_fail_addresses_wrong_type(self):
    """
    ``addresses`` is not an array.
    """
    self.assertFilterErrors(
      {
        'addresses':  Address(self.trytes1),
      },

      {
        'addresses': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_addresses_contents_invalid(self):
    """
    ``addresses`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'addresses': [
          b'',
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes2),

          2130706433,
          b'9' * 82,
        ],
      },

      {
        'addresses.0':  [f.Required.CODE_EMPTY],
        'addresses.1':  [f.Type.CODE_WRONG_TYPE],
        'addresses.2':  [f.Required.CODE_EMPTY],
        'addresses.3':  [Trytes.CODE_NOT_TRYTES],
        'addresses.5':  [f.Type.CODE_WRONG_TYPE],
        'addresses.6':  [Trytes.CODE_WRONG_FORMAT],
      },
    )

  def test_fail_tags_wrong_type(self):
    """
    ``tags`` is not an array.
    """
    self.assertFilterErrors(
      {
        'tags':  Tag(self.trytes1),
      },

      {
        'tags': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_tags_contents_invalid(self):
    """
    ``tags`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'tags': [
          b'',
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes1),

          2130706433,
          b'9' * 28,
        ],
      },

      {
        'tags.0':  [f.Required.CODE_EMPTY],
        'tags.1':  [f.Type.CODE_WRONG_TYPE],
        'tags.2':  [f.Required.CODE_EMPTY],
        'tags.3':  [Trytes.CODE_NOT_TRYTES],
        'tags.5':  [f.Type.CODE_WRONG_TYPE],
        'tags.6':  [Trytes.CODE_WRONG_FORMAT],
      },
    )

  def test_fail_approvees_wrong_type(self):
    """
    ``approvees`` is not an array.
    """
    self.assertFilterErrors(
      {
        'approvees': TransactionHash(self.trytes1),
      },

      {
        'approvees': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_approvees_contents_invalid(self):
    """
    ``approvees`` is an array, but it contains invalid values.
    """
    self.assertFilterErrors(
      {
        'approvees': [
          b'',
          True,
          None,
          b'not valid trytes',

          # This is actually valid; I just added it to make sure the
          # filter isn't cheating!
          TryteString(self.trytes2),

          2130706433,
          b'9' * 82,
        ],
      },

      {
        'approvees.0':  [f.Required.CODE_EMPTY],
        'approvees.1':  [f.Type.CODE_WRONG_TYPE],
        'approvees.2':  [f.Required.CODE_EMPTY],
        'approvees.3':  [Trytes.CODE_NOT_TRYTES],
        'approvees.5':  [f.Type.CODE_WRONG_TYPE],
        'approvees.6':  [Trytes.CODE_WRONG_FORMAT],
      },
    )


class FindTransactionsResponseFilterTestCase(BaseFilterTestCase):
  filter_type = FindTransactionsCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  def setUp(self):
    super(FindTransactionsResponseFilterTestCase, self).setUp()

    # Define a few valid values here that we can reuse across multiple
    # tests.
    self.trytes1 = b'RBTC9D9DCDQAEASBYBCCKBFA'
    self.trytes2 =\
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA'

  def test_no_results(self):
    """
    The incoming response contains no hashes.
    """
    response = {
      'hashes':   [],
      'duration': 42,
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, response)

  def test_search_results(self):
    """
    The incoming response contains lots of hashes.
    """
    filter_ = self._filter({
      'hashes': [
        'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFW'
        'YWZRE9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVA',

        'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
        'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999',
      ],

      'duration': 42,
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'hashes': [
          TransactionHash(
            b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFW'
            b'YWZRE9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVA',
          ),

          TransactionHash(
            b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
            b'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999',
          ),
        ],

        'duration': 42,
      },
    )


class FindTransactionsCommandTestCase(TestCase):
  def setUp(self):
    super(FindTransactionsCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.find_transactions.FindTransactionsCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      response = api.find_transactions('addresses')

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
    with patch('iota.commands.core.find_transactions.FindTransactionsCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      response = await api.find_transactions('addresses')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )