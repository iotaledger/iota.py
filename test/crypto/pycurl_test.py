# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import TryteString
from iota.crypto import Curl


class TestCurl(TestCase):
    def test_correct_first(self):
        inp = (
          'EMIDYNHBWMBCXVDEFOFWINXTERALUKYYPPHKP9JJ'
          'FGJEIUY9MUDVNFZHMMWZUYUSWAIOWEVTHNWMHANBH'
        )

        trits = TryteString(inp).as_trits()

        curl = Curl()
        curl.absorb(trits)
        trits_out = []
        curl.squeeze(trits_out)

        trits_out = TryteString.from_trits(trits_out)

        self.assertEqual(
            trits_out,
            'AQBOPUMJMGVHFOXSMUAGZNACKUTISDPBSILMRAGIG'
            'RXXS9JJTLIKZUW9BCJWKSTFBDSBLNVEEGVGAMSSM')

    def test_input_length_greater_then_243(self):
        inp = (
          'G9JYBOMPUXHYHKSNRNMMSSZCSHOFYOYNZRSZMAAYWDYEIMVVOGKPJB'
          'VBM9TDPULSFUNMTVXRKFIDOHUXXVYDLFSZYZTWQYTE9SPYYWYTXJYQ'
          '9IFGYOLZXWZBKWZN9QOOTBQMWMUBLEWUEEASRHRTNIQWJQNDWRYLCA'
        )

        trits = TryteString(inp).as_trits()

        curl = Curl()
        curl.absorb(trits, length=486)
        trits_out = []
        curl.squeeze(trits_out)

        trits_out = TryteString.from_trits(trits_out)

        self.assertEqual(
            trits_out,
            'RWCBOLRFANOAYQWXXTFQJYQFAUTEEBSZWTIRSSDR'
            'EYGCNFRLHQVDZXYXSJKCQFQLJMMRHYAZKRRLQZDKR')

    def test_input_with_offset(self):
        inp = (
          'G9JYBOMPUXHYHKSNRNMMSSZCSHOFYOYNZRSZMAAYWDYEIMVVOGKPJB'
          'VBM9TDPULSFUNMTVXRKFIDOHUXXVYDLFSZYZTWQYTE9SPYYWYTXJYQ'
          '9IFGYOLZXWZBKWZN9QOOTBQMWMUBLEWUEEASRHRTNIQWJQNDWRYLCA'
        )

        trits = TryteString(inp).as_trits()

        curl = Curl()
        curl.absorb(trits, 243, length=486)
        curl.absorb(trits, 0, length=243)
        trits_out = []
        curl.squeeze(trits_out)

        trits_out = TryteString.from_trits(trits_out)

        self.assertEqual(
            trits_out,
            'ZWNF9YOCAKC9CXQFYZDKXSSAZOCAZLEVEB9OZDJQG'
            'WEULHUDY9RAWAT9GIUXTTUSYJEGNGQDVJCGTQLN9')

    def test_squeeze_with_offset(self):
        inp = (
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


        d = [0] * 243
        trits = TryteString(inp).as_trits()
        curl = Curl()

        for i in range(6):
            curl.reset()
            curl.absorb(trits, i * 243, (i + 1) * 243)
            curl.squeeze(trits, i * 243)

        curl.reset()
        curl.absorb(trits)
        curl.squeeze(d)

        trits_out = TryteString.from_trits(d)

        self.assertEqual(
            trits_out,
            'TAWDGNSEAD9ZRGBBVRVEKQYYVDOKHYQ9KEIYJKFT'
            'BQEYZDWZVMRFJQQGTMPHBZOGPIJCCVWLZVDKLAQVI')
