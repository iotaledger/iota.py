# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import filters as f

from iota.commands import FilterCommand, ResponseFilter
from iota.filters import Trytes
from iota.types import Address


class GetTipsCommand(FilterCommand):
  """
  Executes ``getTips`` command.

  See :py:method:`iota.api.IotaApi.get_tips`.
  """
  command = 'getTips'

  def get_request_filter(self):
    pass

  def get_response_filter(self):
    return GetTipsResponseFilter()


class GetTipsResponseFilter(ResponseFilter):
  def __init__(self):
    super(GetTipsResponseFilter, self).__init__({
      'hashes': (
          f.Array
        | f.FilterRepeater(
              f.ByteString(encoding='ascii')
            | Trytes(result_type=Address)
          )
      ),
    })
