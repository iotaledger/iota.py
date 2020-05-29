from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Iota, TransactionHash, TryteString, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.get_inclusion_states import GetInclusionStatesCommand
from iota.filters import Trytes
from test import patch, MagicMock, async_test


class GetInclusionStatesRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetInclusionStatesCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def setUp(self):
    super(GetInclusionStatesRequestFilterTestCase, self).setUp()

    self.trytes1 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999GCXWZZ'
      'ZKNRIZENRRXGPAGJOSSWQQOJDD9VGQRMEFCOIFLQB'
    )

    self.trytes2 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999KGTGVN'
      'GEDAJAXCTEPOJKF9FCJXXDHISFANKOPFXY9IDPMKC'
    )

  def test_pass_happy_path(self):
    """
    Typical ``getInclusionStates`` request.
    """
    request = {
      # Raw trytes are extracted to match the IRI's JSON protocol.
      'transactions': [self.trytes1, self.trytes2],
    }

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_pass_compatible_types(self):
    """
    The request contains values that can be converted to expected
    types.
    """
    filter_ = self._filter({
      'transactions': [
        TransactionHash(self.trytes1),
        bytearray(self.trytes2.encode('ascii')),
      ],
    })

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'transactions': [self.trytes1, self.trytes2],
      },
    )

  def test_fail_empty(self):
    """
    The incoming request is empty.
    """
    self.assertFilterErrors(
      {},

      {
        'transactions': [f.FilterMapper.CODE_MISSING_KEY],
      },
    )

  def test_fail_unexpected_parameters(self):
    """
    The incoming request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        'transactions': [TransactionHash(self.trytes1)],

        # 'tips' deprecated in IRI 1.9.0
        'tips': [self.trytes1]
      },

      {
        'tips': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )

  def test_fail_transactions_null(self):
    """
    ``transactions`` is null.
    """
    self.assertFilterErrors(
      {
        'transactions': None,
      },

      {
        'transactions': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_transactions_wrong_type(self):
    """
    ``transactions`` is not an array.
    """
    self.assertFilterErrors(
      {
        # Has to be an array, even if we're only querying for one
        # transaction.
        'transactions': TransactionHash(self.trytes1),
      },

      {
        'transactions': [f.Type.CODE_WRONG_TYPE],
      },
    )

  def test_fail_transactions_empty(self):
    """
    ``transactions`` is an array, but it is empty.
    """
    self.assertFilterErrors(
      {
        'transactions': [],
      },

      {
        'transactions': [f.Required.CODE_EMPTY],
      },
    )

  def test_fail_transactions_contents_invalid(self):
    """
    ``transactions`` is a non-empty array, but it contains invalid
    values.
    """
    self.assertFilterErrors(
      {
        'transactions': [
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
        'transactions.0':  [f.Required.CODE_EMPTY],
        'transactions.1':  [f.Type.CODE_WRONG_TYPE],
        'transactions.2':  [f.Required.CODE_EMPTY],
        'transactions.3':  [Trytes.CODE_NOT_TRYTES],
        'transactions.5':  [f.Type.CODE_WRONG_TYPE],
        'transactions.6':  [Trytes.CODE_WRONG_FORMAT],
      },
    )


class GetInclusionStatesCommandTestCase(TestCase):
  def setUp(self):
    super(GetInclusionStatesCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

    self.trytes1 = (
      'TESTVALUE9DONTUSEINPRODUCTION99999GCXWZZ'
      'ZKNRIZENRRXGPAGJOSSWQQOJDD9VGQRMEFCOIFLQB'
    )

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.get_inclusion_states.GetInclusionStatesCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      # Don't need to call with proper args here.
      response = api.get_inclusion_states('transactions')

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
    with patch('iota.commands.core.get_inclusion_states.GetInclusionStatesCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      response = await api.get_inclusion_states('transactions')

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  def test_fail_on_tips(self):
    """
    Fail on provided 'tips' parameter.

    Deprecated in IRI 1.8.6
    """
    api = Iota(self.adapter)

    with self.assertRaises(TypeError):
      response = api.get_inclusion_states(
        transactions=[self.trytes1],
        tips=[self.trytes1]
      )
