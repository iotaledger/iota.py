# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address
from iota.crypto.addresses import AddressGenerator
from iota.crypto.types import Seed


class AddressGeneratorTestCase(TestCase):
  maxDiff = None

  # noinspection SpellCheckingInspection
  def setUp(self):
    super(AddressGeneratorTestCase, self).setUp()

    self.seed_1 =\
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION999999GFDDC'
        b'PFIIEHBCWFN9KHRBEIHHREFCKBVGUGEDXCFHDFPAL',
      )

    self.seed_2 =\
      Seed(
        b'TESTVALUE9DONTUSEINPRODUCTION99999DCZGVE'
        b'JIZEKEGEEHYE9DOHCHLHMGAFDGEEQFUDVGGDGHRDR',
      )

  def test_get_addresses_single(self):
    """
    Generating a single address.
    """
    ag = AddressGenerator(self.seed_1)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0),

      [
        Address(
          b'DLEIS9XU9V9T9OURAKDUSQWBQEYFGJLRPRVEWKN9'
          b'SSUGIHBEIPBPEWISSAURGTQKWKWNHXGCBQTWNOGIY',
        ),
      ],
    )

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=10),

      [
        Address(
          b'XLXFTFBXUOOHRJDVBDBFEBDQDUKSLSOCLUYWGLAP'
          b'R9FUROUHPFINIUFKYSRTFMNWKNEPDZATWXIVWJMDD',
        ),
      ],
    )

  def test_get_addresses_multiple(self):
    """
    Generating multiple addresses in one go.
    """
    ag = AddressGenerator(self.seed_2)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0, count=3),

      [
        Address(
          b'FNKCVJPUANHNWNBAHFBTCONMCUBC9KCZ9EKREBCJ'
          b'AFMABCTEPLGGXDJXVGPXDCFOUCRBWFJFLEAVOEUPY',
        ),

        Address(
          b'MSYILYYZLSJ99TDMGQHDOBWGHTBARCBGJZE9PIMQ'
          b'LTEXJXKTDREGVTPA9NDGGLQHTMGISGRAKSLYPGWMB',
        ),

        Address(
          b'IIREHGHXUHARKVZDMHGUUCHZLUEQQULLEUSJHIIB'
          b'WFYZIZDUFTOVHAWCKRJXUZ9CSUVLTRYSUGBVRMTOW',
        ),
      ],
    )

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=10, count=3),

      [
        Address(
          b'BPXMVV9UPKBTVPJXPBHHOJYAFLALOYCGTSEDLZBH'
          b'NFMGEHREBQTRIPZAPREANPMZJNZZNCDIUFOYYGGFY',
        ),

        Address(
          b'RUCZQJWKXVDIXTLHHOKGMHOV9AKVDBG9HUQHPWNZ'
          b'UNKJNFVMULUSLKFJGSTBSNJMRYSJOBVBQSKVXISZB',
        ),

        Address(
          b'FQAKF9XVCLTBESJKWCHFOCTVABYEEJP9RXUVAEUW'
          b'ENFUUQK9VCHFEORHCYDUJQHNUDWNRDUDZTUGKHSPD',
        ),
      ],
    )

  def test_get_addresses_error_start_too_small(self):
    """
    Providing a negative ``start`` value to ``get_addresses``.

    :py:class:`AddressGenerator` can potentially generate an infinite
    number of addresses, so there is no "end" to offset against.
    """
    ag = AddressGenerator(seed=b'')

    with self.assertRaises(ValueError):
      ag.get_addresses(start=-1)

  def test_get_addresses_error_count_too_small(self):
    """
    Providing a ``count`` value less than 1 to ``get_addresses``.

    :py:class:`AddressGenerator` can potentially generate an infinite
    number of addresses, so there is no "end" to offset against.
    """
    ag = AddressGenerator(seed=b'')

    with self.assertRaises(ValueError):
      ag.get_addresses(start=0, count=0)

  def test_get_addresses_error_step_zero(self):
    """
    Providing a ``step`` value of 0 to ``get_addresses``.
    """
    ag = AddressGenerator(seed=b'')

    with self.assertRaises(ValueError):
      ag.get_addresses(start=0, step=0)

  def test_get_addresses_step_negative(self):
    """
    Providing a negative ``step`` value to ``get_addresses``.

    This is probably a weird use case, but what the heck.
    """
    ag = AddressGenerator(self.seed_1)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=1, count=2, step=-1),

      [
        Address(
          b'PNLOTLFSALMICK9PSW9ZWLE9KJAKPKGJZQJDAFMO'
          b'VLHXMJCJXFPVHOTTOYDIAUAYELXKZWZUITCQBIQKY',
        ),

        Address(
          b'DLEIS9XU9V9T9OURAKDUSQWBQEYFGJLRPRVEWKN9'
          b'SSUGIHBEIPBPEWISSAURGTQKWKWNHXGCBQTWNOGIY',
        ),
      ],
    )

  def test_generator(self):
    """
    Creating a generator.
    """
    ag = AddressGenerator(self.seed_2)

    generator = ag.create_iterator()

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'FNKCVJPUANHNWNBAHFBTCONMCUBC9KCZ9EKREBCJ'
        b'AFMABCTEPLGGXDJXVGPXDCFOUCRBWFJFLEAVOEUPY',
      ),
    )

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'MSYILYYZLSJ99TDMGQHDOBWGHTBARCBGJZE9PIMQ'
        b'LTEXJXKTDREGVTPA9NDGGLQHTMGISGRAKSLYPGWMB',
      ),
    )

    # ... ad infinitum ...

  def test_generator_with_offset(self):
    """
    Creating a generator that starts at an offset greater than 0.
    """
    ag = AddressGenerator(self.seed_1)

    generator = ag.create_iterator(start=1, step=2)

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'PNLOTLFSALMICK9PSW9ZWLE9KJAKPKGJZQJDAFMO'
        b'VLHXMJCJXFPVHOTTOYDIAUAYELXKZWZUITCQBIQKY',
      ),
    )

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'IWWMMHBFWCWOZQLBNXDJ9OOTIGXXU9WNUHFGUZWR'
        b'9FWGIUUUQUECHPKXJLIEKZBOVSEA9BCT9DLOCNCEC',
      ),
    )

  def test_security_level_lowered(self):
    """
    Generating addresses with a lower security level.
    """
    ag = AddressGenerator(self.seed_1, security_level=1)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0, count=3),

      [
        Address(
          b'KNDWDEEWWFVZLISLYRABGVWZCHZNZLNSEJXFKVGA'
          b'UFLL9UMZYEZMEJB9BDLAASWTHEKFREUDIUPY9ICKW',
        ),

        Address(
          b'CHOBTRTQWTMH9GWFWGWUODRSGPOJOIVJUNIQIBZL'
          b'HSWNYPHOD9APWJBMJMGLHFZENWFKDYWHX9JDFXTAB',
        ),

        Address(
          b'YHTOYQUCLDHAIDILFNPITVPYSTOCFAZIUNDYTRDZ'
          b'CVMVGZPONPINNVPJTOAOKHHZWLOKIZPVASTOGAKPA',
        ),
      ],
    )

  def test_security_level_elevated(self):
    """
    Generating addresses with a higher security level.
    """
    ag = AddressGenerator(self.seed_1, security_level=3)

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=0, count=3),

      [
        Address(
          b'BGHTGOUKKNTYFHYUAAPSRUEVN9QQXFOGVCH9Y9BO'
          b'NWXUBDLSKAWEOFZIVMHXBAYVPGDZEYCKNTUJCLPAX',
        ),

        Address(
          b'EGMRJEUIYFUGWAIXXZCHCZUVUUYITICVHDSHCQXG'
          b'FHJIVDCLTI9ZVRIKRLZQWW9CPOIXVDCBAHVGLUHI9',
        ),

        Address(
          b'ENPSARVJZGMMPWZTAIRHADEOZCEVIFNJWSZQHNEI'
          b'RVEVI9GYMFNEOGNUYCPGPSEFCSDHUHOQKDPVGDKYC',
        ),
      ],
    )
