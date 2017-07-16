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
          b'NWQBMJEBSYFCRKGLNUQZJIOQOMNMYPCIRVSVJLP9'
          b'OFV9CZ99LFGZHDKOUDGRVJXUDPUPCVOQBKSZLPU9K',
        ),
      ],
    )

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=10),

      [
        Address(
          b'AQNURLEH9IRPVDWNRLO9JHSY9OWTKHKIJOWSPKPW'
          b'RQLMUI9KOGSXMONCXPEJMRK9MPYQXKZLNYJXNDUUZ',
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
          b'SZWZMYQYWGXWAAVQSDTIOFGTZP9PWIDDUHHNGRDP'
          b'RCGNSXRNYWBEZIORKNNLNZHJ9QYMFYZIJJ9RFPBJT'
        ),

        Address(
          b'N9KY9HCT9VTI99FFRIIBHQZIJOVSLFVWPOIFSHWL'
          b'CCIVYLIDBKJLVQFYJNPIUNATUUCIRHUHNLFBCAXIY'
        ),

        Address(
          b'BH9BWJWHIHLJSHBYBENHLQQBOCQOOMAEJJFFBCSE'
          b'IMDVPDULGD9HBPNQKWBPM9SIDIMGUOGTPWMQSVVHZ'
        ),
      ],
    )

    # noinspection SpellCheckingInspection
    self.assertListEqual(
      ag.get_addresses(start=10, count=3),

      [
        Address(
          b'CCKZUWMILLQLLLIFNXBFGGPXFHNROQQOYYBMLIEOLB'
          b'PVIVFJMQAVCCGKVGNRTKAZQLKYWMTBUEVBPGZMN',
        ),

        Address(
          b'XWXALLEBVQXVRYLGPPJUL9RAIUKUXERBEMVTZJOMRB'
          b'CGXNYA99PN9DKOPAWDSIPIRUBKFQUBQFUOKZMQW',
        ),

        Address(
          b'CLYKQDU9WRHEJZSLMZKVDIWLHZKEIITWXDAHFFSQCP'
          b'LADQKLUQLSECZMIOUDSLXRWEDAEHKRVWQRGZMLI',
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
          b'DUOVVF9WCNAEOHHWUYUFSYOOWZPDVVD9JKFLQN9Z'
          b'DPAKKHSBKLTRFHD9UHIWGKSGAWCOMDG9GBPYISPWR',
        ),

        Address(
          b'NWQBMJEBSYFCRKGLNUQZJIOQOMNMYPCIRVSVJLP9'
          b'OFV9CZ99LFGZHDKOUDGRVJXUDPUPCVOQBKSZLPU9K',
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
        b'SZWZMYQYWGXWAAVQSDTIOFGTZP9PWIDDUHHNGRDP'
        b'RCGNSXRNYWBEZIORKNNLNZHJ9QYMFYZIJJ9RFPBJT',
      ),
    )

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'N9KY9HCT9VTI99FFRIIBHQZIJOVSLFVWPOIFSHWL'
        b'CCIVYLIDBKJLVQFYJNPIUNATUUCIRHUHNLFBCAXIY',
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
        b'DUOVVF9WCNAEOHHWUYUFSYOOWZPDVVD9JKFLQN9Z'
        b'DPAKKHSBKLTRFHD9UHIWGKSGAWCOMDG9GBPYISPWR',
      ),
    )

    # noinspection SpellCheckingInspection
    self.assertEqual(
      next(generator),

      Address(
        b'ZFIRBTDSLFAEDRAFORR9LETRUNRHTACYQPBV9VHR'
        b'EGVIGSKFQABGVLQPLFTAD9OHLPMAVKWBBDIKZSAOG',
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
          b'QTGZZPTYYFMFG9UCTOREALIZZJ9VEASMBFLMZARF'
          b'LENFSNPSITZZVXH9IGPVIRAVRYMXYVXQBUORWVILF',
        ),

        Address(
          b'FHOFBSATJIGMLKGGPWEBIBWIPELKTEAMAQTEDNUN'
          b'HOJBVBAIGTPLMKSGBHWZGNXTLRMFZXASV9FNZGBNY',
        ),

        Address(
          b'VRYXJWWGQIKDLI9R9KFECQXCLYNBHUMCWEYDTOTZ'
          b'GITLQIRDZCOBWXAOTVPGKBQBXKZAZAFRLZTDBRBXW',
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
          b'ZWJEPOOWHOZYEMGJCJAWDETMBUEHOYFHAGOFINQA'
          b'CSGFNHXTMDHVHVAWQHQEBLDXKOQVKHEIU9QWLWPSV',
        ),

        Address(
          b'TNCURBUSWSCMWKJMZFW9SDUTVMQRAHTWVPYQFDRZ'
          b'ALTMDEMCVWEVWYIJZMKOCEPSJKRV9EGDDDCLMCJBL',
        ),

        Address(
          b'HHZUZEKUTMBBIFZDUBVSEXEPEDWATWOBBGVCHBMI'
          b'MBVRLDDLBBWWMECJGNSXFJOCPOFSEZOHDGPVADYCK',
        ),
      ],
    )
