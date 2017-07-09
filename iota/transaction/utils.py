# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from calendar import timegm as unix_timestamp
from datetime import datetime

from typing import Text

from iota import STANDARD_UNITS
from iota.exceptions import with_context

__all__ = [
  'convert_value_to_standard_unit',
  'get_current_timestamp',
]


def convert_value_to_standard_unit(value, symbol='i'):
  # type: (Text, Text) -> float
  """
    Converts between any two standard units of iota.

    :param value:
      Value (affixed) to convert. For example: '1.618 Mi'.

    :param symbol:
      Unit symbol of iota to convert to. For example: 'Gi'.

    :return:
      Float as units of given symbol to convert to.
  """
  try:
    # Get input value
    value_tuple = value.split()
    amount = float(value_tuple[0])
  except (ValueError, IndexError, AttributeError):
    raise with_context(ValueError('Value to convert is not valid.'),
      context = {
        'value': value,
      },
    )

  try:
    # Set unit symbols and find factor/multiplier.
    unit_symbol_from = value_tuple[1]
    unit_factor_from = float(STANDARD_UNITS[unit_symbol_from])
    unit_factor_to = float(STANDARD_UNITS[symbol])
  except (KeyError, IndexError):
    # Invalid symbol or no factor
    raise with_context(ValueError('Invalid IOTA unit.'),
      context = {
        'value': value,
        'symbol': symbol,
      },
    )

  return amount * (unit_factor_from /  unit_factor_to)

def get_current_timestamp():
  # type: () -> int
  """
  Returns the current timestamp, used to set ``timestamp`` for new
  :py:class:`ProposedTransaction` objects.

  Split out into a separate function so that it can be mocked during
  unit tests.
  """
  # Python 3.3 introduced a :py:meth:`datetime.timestamp` method, but
  # for compatibility with Python 2, we have to do it the old-fashioned
  # way.
  # http://stackoverflow.com/q/2775864/
  return unix_timestamp(datetime.utcnow().timetuple())
