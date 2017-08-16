# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from sha3 import keccak_384

from iota.exceptions import with_context

__all__ = [
  'Kerl',
]

TRIT_HASH_LENGTH = 243
BYTE_HASH_LENGTH = 48

class Kerl(object):
  def __init__(self):
    self._reset()

  def absorb(self, trits, offset=0, length=None):
    if length is None:
      length = len(trits)

    if length % 243:
      raise with_context(
        exc = ValueError('Illegal length (s/b divisible by 243).'),

        context = {
          'length': length,
        },
      )

    trits_state = []

    while offset < length:
      stop  = min(offset + TRIT_HASH_LENGTH, length)
      trits_state[0:stop - offset] = trits[offset:stop]

      # Byte encoding
      trits_state[TRIT_HASH_LENGTH-1] = 0
      un_bytes =\
        self.convertBigintToBytes(self.convertTritsToBigint(trits_state))
      _bytes = map(lambda x: x % 256, un_bytes)

      self.k.update(bytearray(_bytes))

      # Move on to the next hash.
      offset += TRIT_HASH_LENGTH


  def squeeze(self, trits, offset=0, length=TRIT_HASH_LENGTH):
    if length % 243:
      raise with_context(
        exc = ValueError('Illegal length (s/b divisible by 243).'),

        context = {
          'length': length,
        },
      )

    while offset < length:
      bytes_state = bytearray.fromhex(self.k.hexdigest())
      _bytes = map(lambda x: x if x<=127 else x-256, bytes_state)

      # Trits Encoding
      trits.extend([0] * max(0, TRIT_HASH_LENGTH - len(trits)))
      trits_state =\
        self.convertBigintToTrits(self.convertBytesToBigInt(_bytes))
      trits_state[TRIT_HASH_LENGTH - 1] = 0

      # Copy exactly one hash.
      stop = min(TRIT_HASH_LENGTH, length)
      trits[offset:stop] = trits_state[0:stop]

      # One hash worth of trits copied; now transform.
      bytes_state = map(lambda x: x ^ 0xFF, bytes_state)
      self._reset()
      self.k.update(bytearray(bytes_state))

      offset += TRIT_HASH_LENGTH

  def _reset(self):
    self.k = keccak_384()

  @staticmethod
  def convertTritsToBigint(trits):
    return sum(base * (3 ** power) for power, base in enumerate(trits))

  def convertBigintToTrits(self, n):
    return self.convertBigintToBase(n, 3, TRIT_HASH_LENGTH)

  @staticmethod
  def convertBigintToBytes(big):
    bytesArrayTemp = [((abs(big) >> pos * 8) % (1 << 8)) for pos in range(48)]
    # Big endian and balanced
    bytesArray =\
      list(map(
        lambda x: x if x <= 0x7F else (x - 0x100),
        reversed(bytesArrayTemp)
      ))

    if big < 0:
      # 1-compliment
      bytesArray = list(map(lambda x: ~x, bytesArray))
      # Add 1
      for pos in reversed(range(len(bytesArray))):
        add = ((bytesArray[pos] & 0xFF) + 1)
        bytesArray[pos] = add if add <= 0x7F else (add - 0x100)
        if bytesArray[pos] != 0:
          break

    return bytesArray

  @staticmethod
  def convertBytesToBigInt(ba):
    # Copy of array
    bytesArray = list(map(lambda x: x, ba))
    # Number sign in MSB
    signum = 1 if bytesArray[0] >= 0 else -1

    if signum == -1:
      # Subtract 1
      for pos in reversed(range(len(bytesArray))):
        sub = ((bytesArray[pos] & 0xFF) - 1)
        bytesArray[pos] = sub if sub <= 0x7F else (sub - 0x100)
        if bytesArray[pos] != -1:
          break
      # 1-compliment
      bytesArray = map(lambda x: ~x, bytesArray)

    # Sum magnitudes and set sign.
    return (
      sum((x & 0xFF) << pos * 8
          for pos, x in enumerate(reversed(bytesArray))) * signum
    )

  @staticmethod
  def convertBigintToBase(n, radix, pad):
    base = [0] * pad
    negative = n<0
    n = -n if negative else n
    max_ = int(radix / 2) if negative else int((radix - 1) / 2)

    for i in range(pad):
      n, remainder = divmod(n, radix)

      if remainder > max_:
        # Lend 1 to the next place so we can make this trit negative.
        n += 1
        remainder -= radix

      base[i] = -remainder if negative else remainder

    return base
