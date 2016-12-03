# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, Sequence

from six import binary_type, string_types

from iota.commands import BaseCommand
from iota.types import TryteString


class BroadcastTransactionsCommand(BaseCommand):
  """
  Executes `broadcastTransactions` command.

  :see: iota.IotaApi.broadcast_transactions
  """
  command = 'broadcastTransactions'

  def _prepare_request(self, request):
    # Required parameters.
    trytes = request['trytes']

    if isinstance(trytes, Generator):
      # :see: https://youtrack.jetbrains.com/issue/PY-20709
      # noinspection PyTypeChecker
      trytes = list(trytes)

    if isinstance(trytes, string_types) or not isinstance(trytes, Sequence):
      raise TypeError(
        'trytes has wrong type (expected Sequence, actual {type}).'.format(
          type = type(trytes).__name__,
        ),
      )

    if not trytes:
      raise ValueError('trytes must not be empty.')

    return {
      'trytes': [binary_type(TryteString(t)) for t in trytes],
    }

  def _prepare_response(self, response):
    pass
