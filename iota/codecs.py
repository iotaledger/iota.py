# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import Codec, CodecInfo, register as lookup_function

from six import binary_type

__all__ = [
  'TrytesCodec',
  'TrytesDecodeError',
]


class TrytesDecodeError(ValueError):
  """Indicates that a tryte string could not be decoded to bytes."""
  pass


class TrytesCodec(Codec):
  """Codec for converting byte strings into trytes and vice versa."""
  name = 'trytes'

  # :bc: Without the bytearray cast, Python 2 will populate the dict
  #   with characters instead of integers.
  # noinspection SpellCheckingInspection
  alphabet  = dict(enumerate(bytearray(b'9ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
  index     = dict(zip(alphabet.values(), alphabet.keys()))

  @classmethod
  def get_codec_info(cls):
    """
    Returns information used by the codecs library to configure the
      codec for use.
    """
    codec = cls()

    return CodecInfo(
      encode            = codec.encode,
      decode            = codec.decode,
      _is_text_encoding = False,
    )

  # noinspection PyShadowingBuiltins
  def encode(self, input, errors='strict'):
    """Encodes a byte string into trytes."""
    if isinstance(input, memoryview):
      input = input.tobytes()

    if not isinstance(input, (binary_type, bytearray)):
      raise TypeError("Can't encode {type}; byte string expected.".format(
        type = type(input).__name__,
      ))

    # :bc: In Python 2, iterating over a byte string yields characters
    #   instead of integers.
    if not isinstance(input, bytearray):
      input = bytearray(input)

    trytes = bytearray()

    for c in input:
      second, first = divmod(c, len(self.alphabet))

      trytes.append(self.alphabet[first])
      trytes.append(self.alphabet[second])

    return binary_type(trytes), len(input)

  # noinspection PyShadowingBuiltins
  def decode(self, input, errors='strict'):
    """Decodes a tryte string into bytes."""
    if isinstance(input, memoryview):
      input = input.tobytes()

    if not isinstance(input, (binary_type, bytearray)):
      raise TypeError("Can't decode {type}; byte string expected.".format(
        type = type(input).__name__,
      ))

    # :bc: In Python 2, iterating over a byte string yields characters
    #   instead of integers.
    if not isinstance(input, bytearray):
      input = bytearray(input)

    bytes_ = bytearray()

    for i in range(0, len(input), 2):
      try:
        first, second = input[i:i+2]
      except ValueError:
        if errors == 'strict':
          raise TrytesDecodeError(
            "'{name}' codec can't decode value; "
            "tryte sequence has odd length.".format(
              name = self.name,
            ),
          )
        elif errors == 'replace':
          bytes_ += b'?'

        continue

      try:
        bytes_.append(
            self.index[first]
          + (self.index[second] * len(self.index))
        )
      except ValueError:
        # This combination of trytes yields a value > 255 when
        #   decoded.  Naturally, we can't represent this using ASCII.
        if errors == 'strict':
          raise TrytesDecodeError(
            "'{name}' codec can't decode trytes {pair} at position {i}-{j}: "
            "ordinal not in range(255)".format(
              name  = self.name,
              pair  = chr(first) + chr(second),
              i     = i,
              j     = i+1,
            ),
          )
        elif errors == 'replace':
          bytes_ += b'?'

    return binary_type(bytes_), len(input)


@lookup_function
def check_trytes_codec(encoding):
  if encoding == TrytesCodec.name:
    return TrytesCodec.get_codec_info()

  return None