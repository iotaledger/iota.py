# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from filters.test import BaseFilterTestCase

from iota.commands.get_tips import GetTipsResponseFilter
from iota.types import Address


class GetTipsResponseFilterTestCase(BaseFilterTestCase):
  filter_type = GetTipsResponseFilter
  skip_value_check = True

  # noinspection SpellCheckingInspection
  def test_pass_lots_of_hashes(self):
    """The response contains lots of hashes."""
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
    """The response doesn't contain any hashes."""
    response = {
      'hashes':   [],
      'duration': 4,
    }

    filter_ = self._filter(response)

    self.assertFilterPasses(filter_)
    self.assertDictEqual(filter_.cleaned_data, response)
