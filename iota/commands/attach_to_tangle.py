# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from typing import Generator, Sequence

from six import binary_type

from iota.api import BaseCommand
from iota.types import TransactionId, TryteString

__all__ = [
  'AttachToTangleCommand',
]


class AttachToTangleCommand(BaseCommand):
  """
  Executes `attachToTangle` command.

  :see: iota.IotaApi.attach_to_tangle
  """
  command = 'attachToTangle'

  def _prepare_request(self, params):
    # Required parameters.
    trunk_transaction     = params['trunk_transaction']
    branch_transaction    = params['branch_transaction']
    trytes                = params['trytes']

    # Optional parameters.
    min_weight_magnitude  = params.get('min_weight_magnitude', 18)

    if type(min_weight_magnitude) is not int:
      raise TypeError(
        'min_weight_magnitude has wrong type '
        '(expected int, actual {type}).'.format(
          type = type(min_weight_magnitude).__name__,
        ),
      )

    if min_weight_magnitude < 18:
      raise ValueError(
        'min_weight_magnitude is too small '
        '(expected >= 18, actual {value}).'.format(
          value = min_weight_magnitude,
        ),
      )

    # Technically, we only need `trytes` to be an Iterable, but some
    #   types (such as TryteString) are Iterable yet not acceptable
    #   here.
    if not isinstance(trytes, (Sequence, Generator)):
      raise TypeError(
        'trytes has wrong type (expected Iterable, actual {type}).'.format(
          type = type(trytes).__name__,
        ),
      )

    if not trytes:
      raise ValueError('trytes must not be empty.')

    return {
      'trunkTransaction':   binary_type(TransactionId(trunk_transaction)),
      'branchTransaction':  binary_type(TransactionId(branch_transaction)),
      'minWeightMagnitude': min_weight_magnitude,
      'trytes':             [binary_type(TryteString(t)) for t in trytes],
    }

  def _prepare_response(self, response):
    self._convert_to_tryte_strings(response, ('trytes',))
