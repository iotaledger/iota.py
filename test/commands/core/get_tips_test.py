from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase

from iota import Address, Iota, AsyncIota
from iota.adapter import MockAdapter, async_return
from iota.commands.core.get_tips import GetTipsCommand
from iota.transaction.types import TransactionHash
from test import patch, MagicMock, async_test


class GetTipsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetTipsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_empty(self):
    """
    The incoming request is (correctly) empty.
    """
    request = {}

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_fail_unexpected_parameters(self):
    """
    The incoming request contains unexpected parameters.
    """
    self.assertFilterErrors(
      {
        # All you had to do was nothing!  How did you screw that up?!
        'foo': 'bar',
      },

      {
        'foo': [f.FilterMapper.CODE_EXTRA_KEY],
      },
    )


class GetTipsResponseFilterTestCase(BaseFilterTestCase):
  filter_type = GetTipsCommand(MockAdapter()).get_response_filter
  skip_value_check = True

  def test_pass_lots_of_hashes(self):
    """
    The response contains lots of hashes.
    """
    response = {
      'hashes':  [
        'YVXJOEOP9JEPRQUVBPJMB9MGIB9OMTIJJLIUYPM9'
        'YBIWXPZ9PQCCGXYSLKQWKHBRVA9AKKKXXMXF99999',

        'ZUMARCWKZOZRMJM9EEYJQCGXLHWXPRTMNWPBRCAG'
        'SGQNRHKGRUCIYQDAEUUEBRDBNBYHAQSSFZZQW9999',

        'QLQECHDVQBMXKD9YYLBMGQLLIQ9PSOVDRLYCLLFM'
        'S9O99XIKCUHWAFWSTARYNCPAVIQIBTVJROOYZ9999',
      ],

      'duration': 4
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(
      filter_.cleaned_data,

      {
        'hashes': [
          Address(
            b'YVXJOEOP9JEPRQUVBPJMB9MGIB9OMTIJJLIUYPM9'
            b'YBIWXPZ9PQCCGXYSLKQWKHBRVA9AKKKXXMXF99999'
          ),

          Address(
            b'ZUMARCWKZOZRMJM9EEYJQCGXLHWXPRTMNWPBRCAG'
            b'SGQNRHKGRUCIYQDAEUUEBRDBNBYHAQSSFZZQW9999'
          ),

          Address(
            b'QLQECHDVQBMXKD9YYLBMGQLLIQ9PSOVDRLYCLLFM'
            b'S9O99XIKCUHWAFWSTARYNCPAVIQIBTVJROOYZ9999'
          ),
        ],

        'duration': 4,
      }
    )

  def test_pass_no_hashes(self):
    """
    The response doesn't contain any hashes.
    """
    response = {
      'hashes':   [],
      'duration': 4,
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, response)


class GetTipsCommandTestCase(TestCase):
  def setUp(self):
    super(GetTipsCommandTestCase, self).setUp()

    self.adapter = MockAdapter()

  def test_wireup(self):
    """
    Verify that the command is wired up correctly. (sync)

    The API method indeed calls the appropiate command.
    """
    with patch('iota.commands.core.get_tips.GetTipsCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = Iota(self.adapter)

      response = api.get_tips()

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
    with patch('iota.commands.core.get_tips.GetTipsCommand.__call__',
               MagicMock(return_value=async_return('You found me!'))
              ) as mocked_command:

      api = AsyncIota(self.adapter)

      response = await api.get_tips()

      self.assertTrue(mocked_command.called)

      self.assertEqual(
        response,
        'You found me!'
      )

  def test_type_coercion(self):
    """
    The result is coerced to the proper type.

    https://github.com/iotaledger/iota.py/issues/130
    """
    self.adapter.seed_response('getTips', {
      'duration': 42,
      'hashes': [
        'TESTVALUE9DONTUSEINPRODUCTION99999ANSVWB'
        'CZ9ABZYUK9YYXFRLROGMCMQHRARDQPNMHHZSZ9999',

        'TESTVALUE9DONTUSEINPRODUCTION99999HCZURL'
        'NFWEDRFCYHWTYGUEMJLJ9ZIJTFASAVSEAZJGA9999',
      ],
    })

    gt_response = Iota(self.adapter).get_tips()

    self.assertEqual(
      list(map(type, gt_response['hashes'])),
      [TransactionHash] * 2,
    )
