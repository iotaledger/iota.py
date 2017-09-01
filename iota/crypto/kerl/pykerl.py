# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from sha3 import keccak_384
from six import PY2

from iota.crypto.kerl import conv
from iota.exceptions import with_context

__all__ = [
  'Kerl',
]

BYTE_HASH_LENGTH = 48
TRIT_HASH_LENGTH = 243

class Kerl(object):
  def __init__(self):
    self.reset()

  def absorb(self, trits, offset=0, length=None):
    # Pad input if necessary, so that it can be divided evenly into
    # hashes.
    pad = ((len(trits) % TRIT_HASH_LENGTH) or TRIT_HASH_LENGTH)
    trits += [0] * (TRIT_HASH_LENGTH - pad)

    if length is None:
      length = len(trits)

    if length < 1:
      raise with_context(
        exc = ValueError('Invalid length passed to ``absorb``.'),

        context = {
          'trits': trits,
          'offset': offset,
          'length': length,
        },
      )

    while offset < length:
      stop = min(offset + TRIT_HASH_LENGTH, length)

      # If we're copying over a full chunk, zero last trit
      if stop - offset == TRIT_HASH_LENGTH:
        trits[stop - 1] = 0

      signed_nums = conv.convertToBytes(trits[offset:stop])

      # Convert signed bytes into their equivalent unsigned representation
      # In order to use Python's built-in bytes type
      unsigned_bytes = bytearray(conv.convert_sign(b) for b in signed_nums)

      self.k.update(unsigned_bytes)

      offset += TRIT_HASH_LENGTH

  def squeeze(self, trits, offset=0, length=None):
    # Pad input if necessary, so that it can be divided evenly into
    # hashes.
    pad = ((len(trits) % TRIT_HASH_LENGTH) or TRIT_HASH_LENGTH)
    trits += [0] * (TRIT_HASH_LENGTH - pad)

    if length is None:
      # By default, we will try to squeeze one hash.
      # Note that this is different than ``absorb``.
      length = len(trits) or TRIT_HASH_LENGTH

    if length < 1:
      raise with_context(
        exc = ValueError('Invalid length passed to ``squeeze``.'),

        context = {
          'trits': trits,
          'offset': offset,
          'length': length,
        },
      )

    while offset < length:
      unsigned_hash = self.k.digest()

      if PY2:
        unsigned_hash = map(ord, unsigned_hash) # type: ignore

      signed_hash = [conv.convert_sign(b) for b in unsigned_hash]

      trits_from_hash = conv.convertToTrits(signed_hash)
      trits_from_hash[TRIT_HASH_LENGTH - 1] = 0

      stop = min(TRIT_HASH_LENGTH, length)
      trits[offset:stop] = trits_from_hash[0:stop]

      flipped_bytes = bytearray(conv.convert_sign(~b) for b in unsigned_hash)

      # Reset internal state before feeding back in
      self.reset()
      self.k.update(flipped_bytes)

      offset += TRIT_HASH_LENGTH

  def reset(self):
    self.k = keccak_384()
