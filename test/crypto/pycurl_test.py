from unittest import TestCase

from iota import TryteString
from iota.crypto import Curl


class CurlTestCase(TestCase):
  """
  This is the test case for CURL-P hash function used in IOTA.

  Note that this test case covers :py:data:`iota.crypto.Curl`, **not**
  :py:class:`iota.crypto.pycurl.Curl`.

  This is intentional; it enables us to run unit tests for the C
  extension with the same code.

  See https://github.com/todofixthis/pyota-ccurl/ for more information.
  """

  def test_happy_path(self):
    """
    Typical use case.
    """
    input_ = (
      'EMIDYNHBWMBCXVDEFOFWINXTERALUKYYPPHKP9JJ'
      'FGJEIUY9MUDVNFZHMMWZUYUSWAIOWEVTHNWMHANBH'
    )

    trits = TryteString(input_).as_trits()

    curl = Curl()
    curl.absorb(trits)
    trits_out = []
    curl.squeeze(trits_out)

    trits_out = TryteString.from_trits(trits_out)

    self.assertEqual(
      trits_out,

      'AQBOPUMJMGVHFOXSMUAGZNACKUTISDPBSILMRAGI'
      'GRXXS9JJTLIKZUW9BCJWKSTFBDSBLNVEEGVGAMSSM',
    )

  def test_length_greater_than_243(self):
    """
    The input is longer than 1 hash.
    """
    input_ = (
      'G9JYBOMPUXHYHKSNRNMMSSZCSHOFYOYNZRSZMAAYWDYEIMVVOGKPJB'
      'VBM9TDPULSFUNMTVXRKFIDOHUXXVYDLFSZYZTWQYTE9SPYYWYTXJYQ'
      '9IFGYOLZXWZBKWZN9QOOTBQMWMUBLEWUEEASRHRTNIQWJQNDWRYLCA'
    )

    trits = TryteString(input_).as_trits()

    curl = Curl()
    curl.absorb(trits)
    trits_out = []
    curl.squeeze(trits_out)

    trits_out = TryteString.from_trits(trits_out)

    self.assertEqual(
      trits_out,

      'RWCBOLRFANOAYQWXXTFQJYQFAUTEEBSZWTIRSSDR'
      'EYGCNFRLHQVDZXYXSJKCQFQLJMMRHYAZKRRLQZDKR',
    )

  def test_length(self):
    """
    Specifying different values for the ``length`` argument.
    """
    input_ = (
      'G9JYBOMPUXHYHKSNRNMMSSZCSHOFYOYNZRSZMAAYWDYEIMVVOGKPJB'
      'VBM9TDPULSFUNMTVXRKFIDOHUXXVYDLFSZYZTWQYTE9SPYYWYTXJYQ'
      '9IFGYOLZXWZBKWZN9QOOTBQMWMUBLEWUEEASRHRTNIQWJQNDWRYLCA'
    )

    trits = TryteString(input_).as_trits()

    curl = Curl()
    curl.absorb(trits, offset=0, length=486)
    curl.absorb(trits, offset=0, length=243)
    trits_out = []
    curl.squeeze(trits_out)

    trits_out = TryteString.from_trits(trits_out)

    self.assertEqual(
      trits_out,

      'OTYHXEXJLCSMEY9LYCC9ASJXMORTLAYQEHRS9DAH'
      '9NR9DXLXYDGOVOBEL9LWRITLWPHPYPZDKXVPAPKUA',
    )

  def test_absorb_offset(self):
    """
    Passing an ``offset`` argument to :py:meth:`Curl.absorb`.
    """
    input_ = (
      'G9JYBOMPUXHYHKSNRNMMSSZCSHOFYOYNZRSZMAAYWDYEIMVVOGKPJB'
      'VBM9TDPULSFUNMTVXRKFIDOHUXXVYDLFSZYZTWQYTE9SPYYWYTXJYQ'
      '9IFGYOLZXWZBKWZN9QOOTBQMWMUBLEWUEEASRHRTNIQWJQNDWRYLCA'
    )

    trits = TryteString(input_).as_trits()

    curl = Curl()
    curl.absorb(trits, offset=243, length=486)
    curl.absorb(trits, offset=0, length=243)
    trits_out = []
    curl.squeeze(trits_out)

    trits_out = TryteString.from_trits(trits_out)

    self.assertEqual(
      trits_out,

      'ZWNF9YOCAKC9CXQFYZDKXSSAZOCAZLEVEB9OZDJQ'
      'GWEULHUDY9RAWAT9GIUXTTUSYJEGNGQDVJCGTQLN9',
    )

  def test_squeeze_offset(self):
    """
    Passing an ``offset`` argument to :py:meth:`Curl.squeeze`.

    Example use case:
    https://github.com/iotaledger/iri/blob/v1.4.1.6/src/main/java/com/iota/iri/hash/ISS.java#L83
    """
    input_ = (
      'CDLFODMOGMQAWXDURDXTUAOO9BFESHYGZLBUWIIHPTLNZCUNHZAAXSUPUIBW'
      'IRLOVKCVWJSWEKRJQZUVRDZGZRNANUNCSGANCJWVHMZMVNJVUAZNFZKDAIVV'
      'LSMIM9SVGUHYECTGGIXTAMXXO9FIXUMQFZCGRQWAOWJPBTXNNQIRSTZEEAJV'
      'FSXWTHWBQJCWQNYYMHSPCYRA99ITVILYJPMFGOGOUOZUVABK9HMGABSORCVD'
      'FNGLMPJ9NFKBWCZMFPIWEAGRWPRNLLG9VYUUVLCTEWKGWQIRIJKERZWC9LVR'
      'XJEXNHBNUGEGGLMWGERKYFB9YEZCLXLKKMCGLRKQOGASDOUDYEDJLMV9BHPG'
      'GCXQIUVUOFFXKEIIINLVWLRYHHLKXPLSTWKIKNEJWEDFQQFXQVEHGRCIJC9T'
      'GVQNPPKGCFGPJNWSCPQZDDSIGAVZEIVYJDVPUOCTEMKTZFGXNGPQCOIBD9MX'
      'YTHJTX'
    )

    trits = TryteString(input_).as_trits()
    curl = Curl()

    trits_out = [0] * 243
    for i in range(6):
      curl.reset()
      curl.absorb(trits, i * 243, (i + 1) * 243)
      curl.squeeze(trits, i * 243)

    curl.reset()
    curl.absorb(trits)
    curl.squeeze(trits_out)

    trits_out = TryteString.from_trits(trits_out)

    self.assertEqual(
      trits_out,

      'TAWDGNSEAD9ZRGBBVRVEKQYYVDOKHYQ9KEIYJKFT'
      'BQEYZDWZVMRFJQQGTMPHBZOGPIJCCVWLZVDKLAQVI',
    )

  def test_squeeze_multiple_hashes(self):
    """
    Squeezing more than 1 hash from the sponge.
    """
    input_ = (
      'EMIDYNHBWMBCXVDEFOFWINXTERALUKYYPPHKP9JJ'
      'FGJEIUY9MUDVNFZHMMWZUYUSWAIOWEVTHNWMHANBH'
    )

    trits = TryteString(input_).as_trits()

    curl = Curl()
    curl.absorb(trits)
    trits_out = []
    curl.squeeze(trits_out, length=486)

    trits_out = TryteString.from_trits(trits_out)

    self.assertEqual(
      trits_out,

      'AQBOPUMJMGVHFOXSMUAGZNACKUTISDPBSILMRAGIG'
      'RXXS9JJTLIKZUW9BCJWKSTFBDSBLNVEEGVGAMSSMQ'
      'GSJWCCFQRHWKTSMVPWWCEGOMCNWFYWDZBEDBLXIFB'
      'HOTCKUMCANLSXXTNKSYNBMOSDDEYFTDOYIKDRJM',
    )
