# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from collections import Iterable

from iota.api import BaseCommand
from iota.types import TransactionId, TryteString


class AttachToTangleCommand(BaseCommand):
  """
  Executes `attachToTangle` command.

  :see: iota.IotaApi.attach_to_tangle
  """
  command = 'attachToTangle'

  def _prepare_request(self, params):
    trunk_transaction     = params.get('trunk_transaction')
    branch_transaction    = params.get('branch_transaction')
    min_weight_magnitude  = params.get('min_weight_magnitude', 18)
    trytes                = params.get('trytes')

    if not isinstance(trunk_transaction, TransactionId):
      raise TypeError(
        'trunk_transaction has wrong type '
        '(expected TransactionID, actual {type}).'.format(
          type = type(trunk_transaction).__name__,
        ),
      )

    if not isinstance(branch_transaction, TransactionId):
      raise TypeError(
        'branch_transaction has wrong type '
        '(expected TransactionID, actual {type}).'.format(
          type = type(branch_transaction).__name__,
        ),
      )

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

    if not isinstance(trytes, Iterable):
      raise TypeError(
        'trytes has wrong type (expected Iterable, actual {type}).'.format(
          type = type(trytes).__name__,
        ),
      )

    if not trytes:
      raise ValueError('trytes must not be empty.')

    for i, t in enumerate(trytes):
      if not isinstance(t, TryteString):
        raise TypeError(
          'trytes[{i}] has wrong type '
          '(expected TryteString, actual {type}).'.format(
            i     = i,
            type  = type(t).__name__,
          ),
        )

    return {
      'trunkTransaction':   trunk_transaction.trytes,
      'branchTransaction':  branch_transaction.trytes,
      'minWeightMagnitude': min_weight_magnitude,
      'trytes':             [t.trytes for t in trytes],
    }

  def _prepare_response(self, response):
    trytes = response.get('trytes')
    if trytes:
      response['trytes'] = [TryteString(t.encode('ascii')) for t in trytes]
