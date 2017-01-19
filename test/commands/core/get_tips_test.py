# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

import filters as f
from filters.test import BaseFilterTestCase
from iota import Address, Iota
from iota.adapter import MockAdapter
from iota.commands.core.get_tips import GetTipsCommand


class GetTipsRequestFilterTestCase(BaseFilterTestCase):
  filter_type = GetTipsCommand(MockAdapter()).get_request_filter
  skip_value_check = True

  def test_pass_empty(self):
    """
    The incoming response is (correctly) empty.
    """
    request = {}

    filter_ = self._filter(request)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, request)

  def test_fail_unexpected_parameters(self):
    """
    The incoming response contains unexpected parameters.
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

  # noinspection SpellCheckingInspection
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
    Verify that the command is wired up correctly.
    """
    self.assertIsInstance(
      Iota(self.adapter).getTips,
      GetTipsCommand,
    )
