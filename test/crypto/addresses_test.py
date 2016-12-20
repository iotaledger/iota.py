# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from iota import Address
from iota.crypto.addresses import AddressGenerator


# noinspection SpellCheckingInspection
class AddressGeneratorTestCase(TestCase):
  def test_generate_single_address(self):
    """
    Generating a single address.
    """
    ag = AddressGenerator(
      seed = b'ITJVZTRFNBTRBSDIHWKOWCFBOQYQTENWLRUVHIBCBRTXYGDCCLLMM9DI9OQO',
    )

    self.assertListEqual(
      ag.get_addresses(0),

      [
        Address(
          b'QIMWUZUX9RBGQZQDMAVBHLMUP9SHRUDYACNRRRBX'
          b'QWRLTYFHDLQKYVHLLGBLSSKACNRIQJVX99OUFNUFE'
        ),
      ],
    )

    self.assertListEqual(
      ag.get_addresses(1),

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
      ag.get_addresses(13),

      [
        Address(
          b'VYJG9FMDTLHJXWXSEMIXJGMNCXWVNKQVBXUCWYLF'
          b'FYBBWUXNTECCHZQRA9WWHOKTYVRZTQAVFAKBQRXPJ'
        ),
      ],
    )
