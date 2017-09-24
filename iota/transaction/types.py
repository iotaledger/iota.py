# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from iota.crypto import FRAGMENT_LENGTH
from iota.exceptions import with_context
from iota.types import Hash, TryteString, TrytesCompatible

__all__ = [
  'BundleHash',
  'Fragment',
  'TransactionHash',
  'TransactionTrytes',
  'Nonce'
]


class BundleHash(Hash):
  """
  A TryteString that acts as a bundle hash.
  """
  pass


class TransactionHash(Hash):
  """
  A TryteString that acts as a transaction hash.
  """
  pass


class Fragment(TryteString):
  """
  A signature/message fragment in a transaction.
  """
  LEN = FRAGMENT_LENGTH

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Fragment, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise with_context(
        exc = ValueError('{cls} values must be {len} trytes long.'.format(
          cls = type(self).__name__,
          len = self.LEN
        )),

        context = {
          'trytes': trytes,
        },
      )


class TransactionTrytes(TryteString):
  """
  A TryteString representation of a Transaction.
  """
  LEN = 2673

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(TransactionTrytes, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise with_context(
        exc = ValueError('{cls} values must be {len} trytes long.'.format(
          cls = type(self).__name__,
          len = self.LEN
        )),

        context = {
          'trytes': trytes,
        },
      )

class Nonce(TryteString):
  """
  A TryteString that acts as a transaction nonce.
  """
  LEN = 27

  def __init__(self, trytes):
    # type: (TrytesCompatible) -> None
    super(Nonce, self).__init__(trytes, pad=self.LEN)

    if len(self._trytes) > self.LEN:
      raise with_context(
        exc = ValueError('{cls} values must be {len} trytes long.'.format(
          cls = type(self).__name__,
          len = self.LEN
        )),

        context = {
          'trytes': trytes,
        },
      )