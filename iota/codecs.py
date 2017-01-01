# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from codecs import Codec, CodecInfo, register as lookup_function

from iota.exceptions import with_context
from six import PY3, binary_type

__all__ = [
  'TrytesCodec',
  'TrytesDecodeError',
]


class TrytesDecodeError(ValueError):
  """
  Indicates that a tryte string could not be decoded to bytes.
  """
  pass


class TrytesCodec(Codec):
  """
  Codec for converting byte strings into trytes, and vice versa.
  """
  name = 'trytes'

  # :bc: Without the bytearray cast, Python 2 will populate the dict
  # with characters instead of integers.
  # noinspection SpellCheckingInspection
  alphabet = dict(enumerate(bytearray(b'9ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
  """
  Used to encode bytes into trytes.
  """

  index = dict(zip(alphabet.values(), alphabet.keys()))
  """
  Used to decode trytes into bytes.
  """

  @classmethod
  def get_codec_info(cls):
    """
    Returns information used by the codecs library to configure the
    codec for use.
    """
    codec = cls()

    codec_info = {
      'encode': codec.encode,
      'decode': codec.decode,
    }

    # In Python 2, all codecs are made equal.
    # In Python 3, some codecs are more equal than others.
    if PY3:
      codec_info['_is_text_encoding'] = False

    return CodecInfo(**codec_info)

  # noinspection PyShadowingBuiltins
  def encode(self, input, errors='strict'):
    """
    Encodes a byte string into trytes.
    """
    if isinstance(input, memoryview):
      input = input.tobytes()

    if not isinstance(input, (binary_type, bytearray)):
      raise with_context(
        exc = TypeError("Can't encode {type}; byte string expected.".format(
          type = type(input).__name__,
        )),

        context = {
          'input': input,
        },
      )

    # :bc: In Python 2, iterating over a byte string yields characters
    # instead of integers.
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
    """
    Decodes a tryte string into bytes.
    """
    if isinstance(input, memoryview):
      input = input.tobytes()

    if not isinstance(input, (binary_type, bytearray)):
      raise with_context(
        exc = TypeError("Can't decode {type}; byte string expected.".format(
          type = type(input).__name__,
        )),

        context = {
          'input': input,
        },
      )

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
          raise with_context(
            exc = TrytesDecodeError(
              "'{name}' codec can't decode value; "
              "tryte sequence has odd length.".format(
                name = self.name,
              ),
            ),

            context = {
              'input': input,
            },
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
        # decoded.  Naturally, we can't represent this using ASCII.
        if errors == 'strict':
          raise with_context(
            exc = TrytesDecodeError(
              "'{name}' codec can't decode trytes {pair} at position {i}-{j}: "
              "ordinal not in range(255)".format(
                name  = self.name,
                pair  = chr(first) + chr(second),
                i     = i,
                j     = i+1,
              ),
            ),

            context = {
              'input': input,
            }
          )
        elif errors == 'replace':
          bytes_ += b'?'

    return binary_type(bytes_), len(input)


@lookup_function
def check_trytes_codec(encoding):
  if encoding == TrytesCodec.name:
    return TrytesCodec.get_codec_info()

  return None
