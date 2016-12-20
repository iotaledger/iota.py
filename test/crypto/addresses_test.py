# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address
from iota.crypto.addresses import AddressGenerator


# noinspection SpellCheckingInspection
class AddressGeneratorTestCase(TestCase):
  def test_get_addresses_single(self):
    """
    Generating a single address.
    """
    ag = AddressGenerator(
      seed = b'ITJVZTRFNBTRBSDIHWKOWCFBOQYQTENWLRUVHIBCBRTXYGDCCLLMM9DI9OQO',
    )

    self.assertListEqual(
      ag.get_addresses(start=0),

      [
        Address(
          b'QIMWUZUX9RBGQZQDMAVBHLMUP9SHRUDYACNRRRBX'
          b'QWRLTYFHDLQKYVHLLGBLSSKACNRIQJVX99OUFNUFE'
        ),
      ],
    )

    self.assertListEqual(
      ag.get_addresses(start=1),

      [
        Address(
          b'IGNEVQHYMVIMZB9XZAFQT9EMDGQJZQUKIVWGOESQ'
          b'DFDOEG9YQUPPD9MSKGDLP9QIHKGOSQZ9PTPEAZGNK'
        ),
      ],
    )

    # You can request an address at any arbitrary index, and the result
    # will always be consistent (assuming the seed doesn't change).
    # Note: this can be a slow process, so we'll keep the numbers small
    # so that tests don't take too long.
    self.assertListEqual(
      ag.get_addresses(start=13),

      [
        Address(
          b'VYJG9FMDTLHJXWXSEMIXJGMNCXWVNKQVBXUCWYLF'
          b'FYBBWUXNTECCHZQRA9WWHOKTYVRZTQAVFAKBQRXPJ'
        ),
      ],
    )

  def test_get_addresses_multiple(self):
    """
    Generating multiple addresses in one go.
    """
    ag = AddressGenerator(
      seed = b'TESTSEED9DONTUSEINPRODUCTION99999TPXGCGPRTMI9QQNCW9PKWTAAOPYHU',
    )

    self.assertListEqual(
      ag.get_addresses(start=1, count=2),

      [
        Address(
          b'AZNEMINAIYSTVTTLPJOXSECRCYJUNUSHDPKKHLJA'
          b'SHU9DAYROZP99ZHMCERMKHGALVUJQPGGK9TDMBHMB'
        ),

        Address(
          b'LOBJATMDBWOZWXZESPPCGFPCHKGAVWRYREQLCKAC'
          b'DOUDVDFVFJMIAOZZQHYCCQUOXWZOGEIL9HYFHDQ9S'
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
    ag = AddressGenerator(
      seed = b'TESTSEED9DONTUSEINPRODUCTION99999GIDXIZGHXKLOMIQVQRFSRUGYDWZA9',
    )

    self.assertListEqual(
      ag.get_addresses(start=1, count=2, step=-1),

      # This is the same as ``ag.get_addresses(start=0, count=2)``, but
      # the order is reversed.
      [
        Address(
          b'OEEOXMWT99FDFSXJYCKXZ9YKHDVJYWLMYFGWKWTB'
          b'LELJPTRZULNTCMIUY9GEGJF9OVIAYJOVKXVPCQGLZ'
        ),

        Address(
          b'TZIXDQENXNLLVIRAQFZOEZKKZDWJIVJCUH9APDTF'
          b'9BNXQUBJAUXZANSBPISZUCBSYQ9UKVAZNEMOKFKOA'
        ),
      ],
    )

  def test_generator(self):
    """
    Creating a generator.
    """
    ag = AddressGenerator(
      seed = b'TESTSEED9DONTUSEINPRODUCTION99999IPKZWMLYYOLWBJGINLSO9EEYQMCUJ',
    )

    generator = ag.create_generator()

    self.assertEqual(
      next(generator),

      Address(
        b'EFJQQFBNRDDEB9PFSOJTXZGXPVPEZUGWAUWGFEXV'
        b'NQEQE9PTXHGIWKDXAHBQGRHSFQQAJORUBGRKVXVNC'
      ),
    )

    self.assertEqual(
      next(generator),

      Address(
        b'UIFOSKQQMEFFCHOCDRZPXGTDXUJLBTVYELZQXOQ9'
        b'DOOHIUFMIXJZFWMQXGNHJNZ9XHTNNSQCGLQBMNDPJ'
      ),
    )

  def test_generator_with_offset(self):
    """
    Creating a generator that starts at an offset greater than 0.
    """
    ag = AddressGenerator(
      seed = b'TESTSEED9DONTUSEINPRODUCTION99999FFRFYAMRNWLGSGZNYUJNEBNWJQNYF',
    )

    generator = ag.create_generator(start=3, step=2)

    self.assertEqual(
      next(generator),

      Address(
        b'HTSDTNXY9MTVRUAGKTDFIMD9ZOYYELHDCHHWUZYF'
        b'GCNOJVJVPLPPTONWYQDIPELEHYX9HHKXWWUSOIJUE'
      ),
    )

    self.assertEqual(
      next(generator),

      Address(
        b'EGNGQFXNJQDUQJGIUMPBGGHFJTH9EXROLGQINOCW'
        b'GIDXIZGHXKLOMIQVQRFSRUGYDWZA9EQCEZCJGEBHX'
      ),
    )
