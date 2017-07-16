# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota import TransactionHash
from iota.commands import FilterCommand, RequestFilter
from iota.filters import Trytes

__all__ = [
  'GetInclusionStatesCommand',
]


class GetInclusionStatesCommand(FilterCommand):
  """
  Executes ``getInclusionStates`` command.

  See :py:meth:`iota.api.StrictIota.get_inclusion_states`.
  """
  command = 'getInclusionStates'

  def get_request_filter(self):
    return GetInclusionStatesRequestFilter()

  def get_response_filter(self):
    pass


class GetInclusionStatesRequestFilter(RequestFilter):
  def __init__(self):
    super(GetInclusionStatesRequestFilter, self).__init__(
      {
        # Required parameters.
        'transactions': (
            f.Required
          | f.Array
          | f.FilterRepeater(
                f.Required
              | Trytes(result_type=TransactionHash)
              | f.Unicode(encoding='ascii', normalize=False)
            )
        ),

        # Optional parameters.
        'tips': (
            f.Array
          | f.FilterRepeater(
                f.Required
              | Trytes(result_type=TransactionHash)
              | f.Unicode(encoding='ascii', normalize=False)
            )
          | f.Optional(default=[])
        ),
      },

      allow_missing_keys = {
        'tips',
      },
    )
